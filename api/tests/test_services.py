import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from api.services.cache import compute_hash, validate_image


class TestImageHash:
    def test_deterministic(self):
        data = b"test image data"
        assert compute_hash(data) == compute_hash(data)

    def test_different_inputs(self):
        assert compute_hash(b"data1") != compute_hash(b"data2")

    def test_returns_hex(self):
        result = compute_hash(b"test")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)


class TestImageValidation:
    def test_valid_jpeg(self):
        validate_image("photo.jpg", 1024, "image/jpeg")

    def test_valid_png(self):
        validate_image("photo.png", 2048, "image/png")

    def test_invalid_type(self):
        with pytest.raises(ValueError, match="Bad type"):
            validate_image("file.gif", 1024, "image/gif")

    def test_empty_file(self):
        with pytest.raises(ValueError, match="empty"):
            validate_image("empty.jpg", 0, "image/jpeg")

    def test_oversized(self):
        with pytest.raises(ValueError, match="exceeds"):
            validate_image("big.jpg", 20 * 1024 * 1024, "image/jpeg")
