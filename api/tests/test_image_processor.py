import io
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from api.services import image_processor
from PIL import Image


def _jpeg_bytes(size: tuple[int, int] = (64, 64)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, (34, 139, 34)).save(buf, format="JPEG")
    return buf.getvalue()


class TestUploadDirResolution:
    def test_default_dir_is_writable(self):
        """api/data/uploads should be writable in local dev."""
        probe = image_processor.UPLOAD_DIR / ".write_test"
        probe.write_text("ok")
        assert probe.read_text() == "ok"
        probe.unlink()

    def test_falls_back_to_temp_when_default_not_writable(self, monkeypatch):
        """When the default dir cannot be written, UPLOAD_DIR uses a temp dir."""
        import tempfile

        class _ReadOnlyDefault:
            def mkdir(self, *args, **kwargs):
                raise OSError("Read-only file system")

        monkeypatch.setattr(
            image_processor, "DEFAULT_UPLOAD_DIR", _ReadOnlyDefault()
        )

        tmp_root = Path(tempfile.gettempdir())
        resolved = image_processor._resolve_upload_dir()
        assert tmp_root in resolved.parents or str(resolved).startswith(str(tmp_root))
        assert resolved.exists()
        probe = resolved / ".write_test"
        probe.write_text("ok")
        assert probe.read_text() == "ok"
        probe.unlink()


class TestProcessorResilientStorage:
    def test_process_returns_compressed_data_without_disk_write(self, monkeypatch):
        """process() should not crash when storage writes fail; data stays in memory."""
        import builtins

        real_open = builtins.open
        processor = image_processor.ImageProcessor()

        def _blocking_open(file, mode="r", *args, **kwargs):
            upload_dir = str(image_processor.UPLOAD_DIR)
            if mode.startswith("w") and str(file).startswith(upload_dir):
                raise OSError("Read-only file system")
            return real_open(file, mode, *args, **kwargs)

        monkeypatch.setattr(builtins, "open", _blocking_open)

        data = _jpeg_bytes()
        result = processor.process(data, "rose.jpg", "image/jpeg")

        assert result["valid"] is True
        assert result["compressed_data"]  # in-memory data preserved
        assert result["storage"] == {}  # no storage paths when write failed

    def test_process_writes_storage_normally(self, tmp_path, monkeypatch):
        """When writes succeed, storage paths point at real files."""
        monkeypatch.setattr(
            image_processor, "UPLOAD_DIR", tmp_path, raising=False
        )
        processor = image_processor.ImageProcessor()

        data = _jpeg_bytes()
        result = processor.process(data, "rose.jpg", "image/jpeg")

        assert result["valid"] is True
        storage = result["storage"]
        assert storage  # paths present
        for path in (storage["original"], storage["compressed"], storage["thumbnail"]):
            assert os.path.isfile(path)


class TestProcessorThumbnailDataUrl:
    def test_process_returns_base64_thumbnail_data_url(self, monkeypatch):
        """process() should expose a base64 data URL for the thumbnail."""
        processor = image_processor.ImageProcessor()
        data = _jpeg_bytes()
        result = processor.process(data, "rose.jpg", "image/jpeg")

        assert result["valid"] is True
        url = result["thumbnail_data_url"]
        assert url.startswith("data:image/jpeg;base64,")

        import base64
        b64 = url.split(",", 1)[1]
        decoded = base64.b64decode(b64)
        assert len(decoded) > 0
        # Decodable back into a valid JPEG (SOI marker).
        assert decoded[:2] == b"\xff\xd8"

    def test_thumbnail_data_url_present_even_when_disk_write_fails(self, monkeypatch):
        """Thumbnail data URL must survive read-only filesystems (serverless)."""
        import builtins

        real_open = builtins.open

        def _blocking_open(file, mode="r", *args, **kwargs):
            upload_dir = str(image_processor.UPLOAD_DIR)
            if mode.startswith("w") and str(file).startswith(upload_dir):
                raise OSError("Read-only file system")
            return real_open(file, mode, *args, **kwargs)

        monkeypatch.setattr(builtins, "open", _blocking_open)
        processor = image_processor.ImageProcessor()
        data = _jpeg_bytes()
        result = processor.process(data, "rose.jpg", "image/jpeg")

        assert result["valid"] is True
        assert result["storage"] == {}
        assert result["thumbnail_data_url"].startswith("data:image/jpeg;base64,")
