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


def _structured_jpeg_bytes(size: tuple[int, int] = (128, 128)) -> bytes:
    """A green image with sharp edges/bands, so Laplacian variance is non-zero."""
    import numpy as np

    arr = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    block = 8
    for y in range(0, size[1], block):
        for x in range(0, size[0], block):
            val = 60 if (x // block + y // block) % 2 == 0 else 200
            arr[y : y + block, x : x + block] = (val // 2, val, val // 2)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="JPEG")
    return buf.getvalue()


class TestOpenCVAnalysis:
    def test_sharp_image_is_not_blurry(self):
        """A sharp, structured green image has high Laplacian variance."""
        result = image_processor.validate_with_opencv(_structured_jpeg_bytes())
        assert result["valid"] is True
        assert result["sharpness"] > 0
        assert result["is_blurry"] is False

    def test_green_image_is_plant_like(self):
        """A foliage-green image is flagged plant-like via green ratio."""
        result = image_processor.validate_with_opencv(_jpeg_bytes())
        assert result["valid"] is True
        assert result["green_ratio"] > 0.3
        assert result["is_plant_like"] is True

    def test_blurry_image_detected(self):
        """A heavily blurred image is marked blurry (low Laplacian variance)."""
        import numpy as np

        img = Image.new("RGB", (128, 128), (40, 120, 40))
        arr = np.array(img)
        from PIL import ImageFilter

        blurred = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(radius=12))
        buf = io.BytesIO()
        blurred.save(buf, format="JPEG")
        result = image_processor.validate_with_opencv(buf.getvalue())
        assert result["valid"] is True
        assert result["is_blurry"] is True

    def test_opencv_metadata_in_process(self):
        """process() exposes the OpenCV analysis fields in metadata."""
        result = image_processor.ImageProcessor().process(
            _jpeg_bytes(), "leaf.jpg", "image/jpeg"
        )
        ocv = result["metadata"]["opencv"]
        assert ocv["valid"] is True
        assert "sharpness" in ocv
        assert "green_ratio" in ocv
        assert "is_blurry" in ocv
        assert ocv["is_plant_like"] is True


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
