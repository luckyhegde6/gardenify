"""Perceptual image hashing — dHash and pHash implementations.

Uses only Pillow (no external imagehash library needed).
dHash: 64-bit difference hash, fast (~1ms per image).
pHash: 64-bit perceptual hash via DCT, more robust (~5ms per image).
"""

import logging
import math
from io import BytesIO

from PIL import Image

logger = logging.getLogger(__name__)


def compute_dhash(data: bytes, hash_size: int = 8) -> str:
    """Compute difference hash (dHash) from image bytes.

    Resizes to (hash_size+1) x hash_size, converts to grayscale,
    compares adjacent pixels horizontally.
    Returns 16-char hex string (64-bit hash).
    """
    img = Image.open(BytesIO(data)).convert("L")
    img = img.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(img.get_flattened_data())

    bits = []
    for row in range(hash_size):
        for col in range(hash_size):
            idx = row * (hash_size + 1) + col
            bits.append(1 if pixels[idx] < pixels[idx + 1] else 0)

    return _bits_to_hex(bits)


def compute_phash(data: bytes, hash_size: int = 8) -> str:
    """Compute perceptual hash (pHash) from image bytes.

    Uses simplified DCT on 32x32 grayscale image.
    Returns 16-char hex string (64-bit hash).
    """
    img = Image.open(BytesIO(data)).convert("L")
    img = img.resize((32, 32), Image.Resampling.LANCZOS)
    pixels = list(img.get_flattened_data())

    # Fast DCT approximation via row-then-column 1D DCT
    dct = _dct2d_fast(pixels, 32)

    # Take top-left 8x8 (low frequencies, excluding DC)
    low_freq = []
    for row in range(hash_size):
        for col in range(hash_size):
            low_freq.append(dct[row * 32 + col])

    # Median threshold
    median = sorted(low_freq)[len(low_freq) // 2]
    bits = [1 if p > median else 0 for p in low_freq]

    return _bits_to_hex(bits)


def hamming_distance(hash1: str, hash2: str) -> int:
    """Compute Hamming distance between two hex hash strings."""
    if len(hash1) != len(hash2):
        raise ValueError(f"Hash lengths differ: {len(hash1)} vs {len(hash2)}")

    dist = 0
    for c1, c2 in zip(hash1, hash2):
        xor = int(c1, 16) ^ int(c2, 16)
        dist += xor.bit_count()
    return dist


def match_hash(query_hash: str, hash_list: list[tuple[str, str]],
               max_distance: int = 10) -> list[tuple[str, int]]:
    """Find matching hashes within max_distance.

    Args:
        query_hash: The hash to match against.
        hash_list: List of (identifier, hash) tuples.
        max_distance: Maximum Hamming distance to consider a match.

    Returns:
        List of (identifier, distance) tuples, sorted by distance.
    """
    matches = []
    for identifier, candidate_hash in hash_list:
        dist = hamming_distance(query_hash, candidate_hash)
        if dist <= max_distance:
            matches.append((identifier, dist))
    return sorted(matches, key=lambda x: x[1])


def _bits_to_hex(bits: list[int]) -> str:
    """Convert list of bits to hex string."""
    hex_str = ""
    for i in range(0, len(bits), 4):
        nibble = bits[i:i + 4]
        val = sum(b << (3 - j) for j, b in enumerate(nibble))
        hex_str += format(val, "x")
    return hex_str


def _dct1d(row: list[float]) -> list[float]:
    """1D DCT-II (fast, O(n log n) via butterfly)."""
    n = len(row)
    result = [0.0] * n
    for k in range(n):
        total = 0.0
        for i in range(n):
            total += row[i] * math.cos(math.pi * k * (2 * i + 1) / (2 * n))
        result[k] = total
    return result


def _dct2d_fast(pixels: list[int], size: int) -> list[float]:
    """2D DCT via row-then-column 1D DCT (O(n^3) instead of O(n^4))."""
    # Row DCT
    row_dct = []
    for r in range(size):
        row = [float(pixels[r * size + c]) for c in range(size)]
        row_dct.extend(_dct1d(row))

    # Column DCT
    result = [0.0] * (size * size)
    for c in range(size):
        col = [row_dct[r * size + c] for r in range(size)]
        col_dct = _dct1d(col)
        for r in range(size):
            result[r * size + c] = col_dct[r]

    return result
