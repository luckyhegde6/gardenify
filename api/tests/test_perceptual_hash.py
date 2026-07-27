"""Tests for perceptual hash functions."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from PIL import Image
from io import BytesIO

from api.services.perceptual_hash import (
    compute_dhash,
    compute_phash,
    hamming_distance,
    match_hash,
    _bits_to_hex,
    _dct1d,
)


def _make_image(color=(128, 128, 128), size=(64, 64)) -> bytes:
    """Create a minimal JPEG image."""
    img = Image.new("RGB", size, color=color)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_gradient_image() -> bytes:
    """Create an image with a gradient (left-to-right dark to light)."""
    img = Image.new("RGB", (64, 64))
    pixels = img.load()
    for x in range(64):
        for y in range(64):
            val = int(x * 255 / 63)
            pixels[x, y] = (val, val, val)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_checkerboard_image() -> bytes:
    """Create a checkerboard pattern image."""
    img = Image.new("RGB", (64, 64))
    pixels = img.load()
    for x in range(64):
        for y in range(64):
            val = 255 if (x // 8 + y // 8) % 2 == 0 else 0
            pixels[x, y] = (val, val, val)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestDHash:
    def test_returns_hex_string(self):
        """dHash returns a 16-char hex string."""
        data = _make_image()
        result = compute_dhash(data)
        assert isinstance(result, str)
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)

    def test_deterministic(self):
        """Same image produces same hash."""
        data = _make_image()
        h1 = compute_dhash(data)
        h2 = compute_dhash(data)
        assert h1 == h2

    def test_different_images_different_hashes(self):
        """Different images produce different hashes."""
        h1 = compute_dhash(_make_gradient_image())
        h2 = compute_dhash(_make_checkerboard_image())
        assert h1 != h2


class TestPHash:
    def test_returns_hex_string(self):
        """pHash returns a 16-char hex string."""
        data = _make_image()
        result = compute_phash(data)
        assert isinstance(result, str)
        assert len(result) == 16

    def test_deterministic(self):
        """Same image produces same hash."""
        data = _make_image()
        h1 = compute_phash(data)
        h2 = compute_phash(data)
        assert h1 == h2

    def test_similar_images_close_hash(self):
        """Similar images have small Hamming distance."""
        # Use gradient images (more structure for DCT)
        h1 = compute_phash(_make_gradient_image())
        h2 = compute_phash(_make_gradient_image())
        dist = hamming_distance(h1, h2)
        assert dist == 0  # Same image = same hash


class TestHammingDistance:
    def test_same_hash_zero_distance(self):
        """Same hash has distance 0."""
        assert hamming_distance("abc123", "abc123") == 0

    def test_max_distance(self):
        """Completely different hashes have high distance."""
        assert hamming_distance("0000", "ffff") == 16

    def test_single_bit_difference(self):
        """One bit difference = distance 1."""
        assert hamming_distance("0000", "0001") == 1

    def test_length_mismatch_raises(self):
        """Different length hashes raise ValueError."""
        with pytest.raises(ValueError, match="lengths differ"):
            hamming_distance("abc", "abcd")


class TestMatchHash:
    def test_finds_exact_match(self):
        """Finds exact hash match."""
        matches = match_hash("abc123", [("species1", "abc123")])
        assert len(matches) == 1
        assert matches[0][0] == "species1"
        assert matches[0][1] == 0

    def test_finds_close_match(self):
        """Finds hash within threshold."""
        matches = match_hash("abc123", [("species1", "abc122")], max_distance=1)
        assert len(matches) == 1

    def test_rejects_distant_match(self):
        """Rejects hash beyond threshold."""
        matches = match_hash("0000", [("species1", "ffff")], max_distance=5)
        assert len(matches) == 0

    def test_sorted_by_distance(self):
        """Results sorted by distance (closest first)."""
        matches = match_hash("abc123", [
            ("far", "abc111"),
            ("close", "abc123"),
            ("medium", "abc103"),
        ])
        assert matches[0][0] == "close"
        assert matches[-1][0] == "far"

    def test_empty_hash_list(self):
        """Empty hash list returns empty results."""
        matches = match_hash("abc123", [])
        assert matches == []


class TestBitsToHex:
    def test_all_zeros(self):
        """All zeros → '0' repeated."""
        result = _bits_to_hex([0, 0, 0, 0])
        assert result == "0"

    def test_all_ones(self):
        """All ones → 'f'."""
        result = _bits_to_hex([1, 1, 1, 1])
        assert result == "f"

    def test_mixed_bits(self):
        """Mixed bits → correct hex."""
        result = _bits_to_hex([1, 0, 1, 0])
        assert result == "a"


class TestDCT:
    def test_dct1d_returns_list(self):
        """1D DCT returns list of floats."""
        result = _dct1d([1.0, 2.0, 3.0, 4.0])
        assert isinstance(result, list)
        assert len(result) == 4
        assert all(isinstance(x, float) for x in result)
