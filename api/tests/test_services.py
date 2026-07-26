import sys
import os

# Add parent directory to path so 'api' package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from api.services.cache import compute_image_hash, validate_image


class TestImageHash:
    def test_deterministic(self):
        data = b"test image data"
        assert compute_image_hash(data) == compute_image_hash(data)

    def test_different_inputs_different_hashes(self):
        assert compute_image_hash(b"data1") != compute_image_hash(b"data2")

    def test_returns_hex_string(self):
        result = compute_image_hash(b"test")
        assert len(result) == 64  # SHA-256 hex length
        assert all(c in "0123456789abcdef" for c in result)


class TestImageValidation:
    def test_valid_jpeg(self):
        validate_image("photo.jpg", 1024, "image/jpeg")

    def test_valid_png(self):
        validate_image("photo.png", 2048, "image/png")

    def test_invalid_type(self):
        import pytest
        with pytest.raises(ValueError, match="Invalid image type"):
            validate_image("file.gif", 1024, "image/gif")

    def test_empty_file(self):
        import pytest
        with pytest.raises(ValueError, match="empty"):
            validate_image("empty.jpg", 0, "image/jpeg")

    def test_oversized_file(self):
        import pytest
        with pytest.raises(ValueError, match="exceeds maximum size"):
            validate_image("big.jpg", 20 * 1024 * 1024, "image/jpeg")
