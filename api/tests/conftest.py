"""Shared test fixtures for Gardenify API tests."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest


@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary SQLite database for testing."""
    import api.services.local_db as db_module

    # Override DB_PATH to use temp directory
    original_path = db_module.DB_PATH
    db_module.DB_PATH = tmp_path / "test.db"

    # Initialize the database
    db_module.init_db()

    yield db_module

    # Restore original path
    db_module.DB_PATH = original_path


@pytest.fixture
def sample_species():
    """Sample species data for testing."""
    return {
        "scientific_name": "Test plantus",
        "common_names": '["Test Plant", "Testing Flower"]',
        "family": "Testaceae",
        "genus": "Testus",
        "category": "herbaceous_flowering_plant",
        "native_regions": '["Testland"]',
        "observation_count": 42,
        "source": "test",
    }


@pytest.fixture
def sample_image_bytes():
    """Create a minimal valid JPEG image for testing."""
    # Minimal JPEG: SOI marker + APP0 + image data
    from PIL import Image
    from io import BytesIO

    img = Image.new("RGB", (64, 64), color=(128, 200, 128))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()
