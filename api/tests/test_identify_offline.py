"""Tests for offline identification fallback."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from io import BytesIO

import pytest
from api.services import supabase_species
from api.services.local_identify import local_identify, search_local_species
from api.services.perceptual_hash import compute_phash
from PIL import Image


def _make_image_bytes(color=(128, 200, 128)) -> bytes:
    """Create a minimal JPEG image."""
    img = Image.new("RGB", (64, 64), color=color)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestLocalIdentify:
    @pytest.mark.asyncio
    async def test_identify_returns_dict(self, patched_supabase):
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
    async def test_identify_empty_images(self, patched_supabase):
        """local_identify with no images returns empty results."""
        result = await local_identify([])
        assert result["best_match"] == ""
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_identify_with_no_matching_species(self, patched_supabase):
        """local_identify with no matching species returns empty results."""
        supabase_species.insert_species({
            "scientific_name": "Test plantus",
            "observation_count": 10,
        })
        data = _make_image_bytes()
        images = [("test.jpg", BytesIO(data))]
        result = await local_identify(images)
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_identify_with_matching_hash(self, patched_supabase):
        """local_identify finds species by perceptual hash."""
        species_id = supabase_species.insert_species({
            "scientific_name": "Test plantus",
            "observation_count": 10,
        })

        ref_data = _make_image_bytes()
        ref_phash = compute_phash(ref_data)

        supabase_species.insert_image_hash(
            species_id=species_id,
            image_path="ref.jpg",
            phash=ref_phash,
        )

        images = [("test.jpg", BytesIO(ref_data))]
        result = await local_identify(images)
        assert len(result["results"]) >= 1
        assert result["results"][0]["species"]["scientific_name"] == "Test plantus"

    @pytest.mark.asyncio
    async def test_identify_source_field(self, patched_supabase):
        """Response includes source='local'."""
        result = await local_identify([])
        assert result["source"] == "local"
        assert result["version"] == "local-1.0"


class TestSearchLocalSpecies:
    def test_search_returns_list(self, patched_supabase):
        """search_local_species returns a list."""
        supabase_species.insert_species({"scientific_name": "Search testus", "observation_count": 5})
        results = search_local_species("search")
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_search_empty_returns_all(self, patched_supabase):
        """Empty query returns species."""
        for i in range(5):
            supabase_species.insert_species({"scientific_name": f"Test {i}", "observation_count": i})
        results = search_local_species("")
        assert len(results) >= 5