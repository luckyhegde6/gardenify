"""Generate test fixture images with plant-like features for E2E tests.

Creates JPEGs with green shapes (leaf-like) on brown/soil backgrounds
so OpenCV edge detection finds enough content to pass is_plant_like gate.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FIXTURES = Path("e2e/api-tests/fixtures")

try:
    import numpy as np
    from PIL import Image, ImageDraw
except ImportError:
    print("PIL/Pillow not installed. Install: pip install Pillow")
    sys.exit(1)


def make_leaf_image(width=300, height=300, seed=42):
    """Green leaf shape on brown background."""
    rng = np.random.RandomState(seed)
    arr = rng.randint(60, 90, (height, width, 3), dtype=np.uint8)
    arr[:, :] = [101, 67, 33]
    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img)

    cx, cy = width // 2, height // 2
    for i in range(6):
        ox = int(rng.randn() * 20)
        oy = int(rng.randn() * 20)
        rx = 30 + int(rng.rand() * 40)
        ry = 60 + int(rng.rand() * 40)
        left = cx + ox - rx
        top = cy + oy - ry
        right = cx + ox + rx
        bottom = cy + oy + ry
        g = 80 + int(rng.rand() * 100)
        draw.ellipse([left, top, right, bottom], fill=(34, g, 34))

    return img


def make_flower_image(width=300, height=300, seed=43):
    """Flower shape with petals on green background."""
    rng = np.random.RandomState(seed)
    arr = rng.randint(30, 60, (height, width, 3), dtype=np.uint8)
    arr[:, :] = [40, 90, 40]
    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img)

    cx, cy = width // 2, height // 2
    for angle in range(0, 360, 30):
        rad = np.deg2rad(angle)
        px = int(cx + 50 * np.cos(rad))
        py = int(cy + 50 * np.sin(rad))
        r = int(15 + rng.rand() * 15)
        draw.ellipse(
            [px - r, py - r, px + r, py + r],
            fill=(200, 50, 50),
        )

    draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(255, 200, 50))
    return img


def make_bark_image(width=300, height=300, seed=44):
    """Bark-like texture (brown/gray) with vertical lines."""
    rng = np.random.RandomState(seed)
    arr = rng.randint(70, 120, (height, width, 3), dtype=np.uint8)
    arr[:, :] = [70, 55, 45]
    for x in range(0, width, 6):
        shade = int(40 + rng.rand() * 30)
        thickness = rng.randint(2, 4)
        arr[:, x : x + thickness] = [shade, shade - 10, shade - 15]
    img = Image.fromarray(arr, "RGB")
    return img


def main():
    FIXTURES.mkdir(parents=True, exist_ok=True)

    leaf = make_leaf_image(seed=42)
    leaf.save(str(FIXTURES / "leaf.jpg"), "JPEG", quality=90)
    print(f"leaf.jpg: {os.path.getsize(FIXTURES / 'leaf.jpg')} bytes")

    flower = make_flower_image(seed=43)
    flower.save(str(FIXTURES / "flower.jpg"), "JPEG", quality=90)
    print(f"flower.jpg: {os.path.getsize(FIXTURES / 'flower.jpg')} bytes")

    bark = make_bark_image(seed=44)
    bark.save(str(FIXTURES / "bark.jpg"), "JPEG", quality=90)
    print(f"bark.jpg: {os.path.getsize(FIXTURES / 'bark.jpg')} bytes")

    print(f"Fixtures in {FIXTURES.resolve()}")


if __name__ == "__main__":
    main()
