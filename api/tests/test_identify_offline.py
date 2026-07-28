"""Tests for offline identification fallback."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from io import BytesIO

import pytest
from api.services.local_db import (
    insert_image_hash,
    insert_species,
)
from api.services.local_identify import local_identify, search_local_species
from api.services.perceptual_hash import compute_phash
from PIL import Image


def _make_image_bytes(color=(128, 200, 128)) -> bytes:
    """Create a minimal JPEG image."""
    img = Image.new("RGB", (64, 64), color=color)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    """Set up a test database for each test."""
    import api.services.local_db as db_module
    original_path = db_module.DB_PATH
    db_module.DB_PATH = tmp_path / "test.db"
    db_module.init_db()
    yield
    db_module.DB_PATH = original_path


class TestLocalIdentify:
    @pytest.mark.asyncio
    async def test_identify_returns_dict(self):
        """local_identify returns a dict with expected keys."""
        data = _make_image_bytes()
        images = [("test.jpg", BytesIO(data))]
        result = await local_identify(images)
        assert isinstance(result, dict)
        assert "best_match" in result
        assert "results" in result
        assert "source" in result
        assert result["source"] == "local"

    @pytest.mark.asyncio
    async def test_identify_empty_images(self):
        """local_identify with no images returns empty results."""
        result = await local_identify([])
        assert result["best_match"] == ""
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_identify_with_no_matching_species(self):
        """local_identify with no matching species returns empty results."""
        # Insert a species but no image hashes
        insert_species({
            "scientific_name": "Test plantus",
            "observation_count": 10,
        })
        data = _make_image_bytes()
        images = [("test.jpg", BytesIO(data))]
        result = await local_identify(images)
        # No hashes in DB, so no matches
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_identify_with_matching_hash(self):
        """local_identify finds species by perceptual hash."""
        # Insert species and image hash
        species_id = insert_species({
            "scientific_name": "Test plantus",
            "observation_count": 10,
        })

        # Create a reference image and compute its pHash
        # (local_identify uses pHash for matching)
        ref_data = _make_image_bytes()
        ref_phash = compute_phash(ref_data)

        insert_image_hash(
            species_id=species_id,
            image_path="ref.jpg",
            phash=ref_phash,
        )

        # Identify using same image (should match perfectly)
        images = [("test.jpg", BytesIO(ref_data))]
        result = await local_identify(images)
        assert len(result["results"]) >= 1
        assert result["results"][0]["species"]["scientific_name"] == "Test plantus"

    @pytest.mark.asyncio
    async def test_identify_source_field(self):
        """Response includes source='local'."""
        result = await local_identify([])
        assert result["source"] == "local"
        assert result["version"] == "local-1.0"


class TestSearchLocalSpecies:
    def test_search_returns_list(self):
        """search_local_species returns a list."""
        insert_species({"scientific_name": "Search testus", "observation_count": 5})
        results = search_local_species("search")
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_search_empty_returns_all(self):
        """Empty query returns species."""
        for i in range(5):
            insert_species({"scientific_name": f"Test {i}", "observation_count": i})
        results = search_local_species("")
        assert len(results) >= 5
