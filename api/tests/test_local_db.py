"""Tests for Supabase-backed species data layer (successor to local_db tests)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from api.services import supabase_species


class TestSupabaseSpecies:
    def test_insert_species(self, patched_supabase, sample_species):
        """Insert a species and retrieve it."""
        species_id = supabase_species.insert_species(sample_species)
        assert species_id is not None
        assert species_id > 0

        result = supabase_species.get_species_by_id(species_id)
        assert result is not None
        assert result["scientific_name"] == "Test plantus"
        assert result["family"] == "Testaceae"
        assert result["genus"] == "Testus"

    def test_insert_species_upsert(self, patched_supabase, sample_species):
        """Inserting same species twice updates rather than duplicates."""
        id1 = supabase_species.insert_species(sample_species)
        sample_species["observation_count"] = 100
        id2 = supabase_species.insert_species(sample_species)
        assert id1 == id2

        result = supabase_species.get_species_by_id(id1)
        assert result["observation_count"] == 142  # 42 + 100

    def test_search_species(self, patched_supabase, sample_species):
        """Search finds species by scientific name."""
        supabase_species.insert_species(sample_species)
        results = supabase_species.search_species("test")
        assert len(results) >= 1
        assert any(r["scientific_name"] == "Test plantus" for r in results)

    def test_search_species_by_genus(self, patched_supabase, sample_species):
        """Search finds species by genus."""
        supabase_species.insert_species(sample_species)
        results = supabase_species.search_species("testus")
        assert len(results) >= 1

    def test_search_species_by_family(self, patched_supabase, sample_species):
        """Search finds species by family."""
        supabase_species.insert_species(sample_species)
        results = supabase_species.search_species("testaceae")
        assert len(results) >= 1

    def test_search_species_limit(self, patched_supabase):
        """Search respects limit parameter."""
        for i in range(10):
            supabase_species.insert_species({
                "scientific_name": f"Species testus {i}",
                "observation_count": i,
            })
        results = supabase_species.search_species("testus", limit=5)
        assert len(results) <= 5

    def test_get_species_not_found(self, patched_supabase):
        """Getting non-existent species returns None."""
        assert supabase_species.get_species_by_id(99999) is None

    def test_get_species_by_name(self, patched_supabase, sample_species):
        """Get species by exact scientific name."""
        supabase_species.insert_species(sample_species)
        result = supabase_species.get_species_by_name("Test plantus")
        assert result is not None
        assert result["scientific_name"] == "Test plantus"

    def test_get_species_by_name_not_found(self, patched_supabase):
        """Getting non-existent species by name returns None."""
        assert supabase_species.get_species_by_name("Nonexistent plantus") is None

    def test_insert_image_hash(self, patched_supabase, sample_species):
        """Insert an image hash record."""
        species_id = supabase_species.insert_species(sample_species)
        hash_id = supabase_species.insert_image_hash(
            species_id=species_id,
            image_path="test/image.jpg",
            phash="abc123def456",
            dhash="abc123def456",
            category="herb",
        )
        assert hash_id is not None
        assert hash_id > 0

    def test_get_species_images(self, patched_supabase, sample_species):
        """Species detail includes images."""
        species_id = supabase_species.insert_species(sample_species)
        supabase_species.insert_image_hash(
            species_id=species_id,
            image_path="test.jpg",
            phash="abc123",
        )
        result = supabase_species.get_species_by_id(species_id)
        assert len(result["images"]) == 1
        assert result["images"][0]["image_path"] == "test.jpg"

    def test_species_count(self, patched_supabase, sample_species):
        """Species count returns correct number."""
        assert supabase_species.get_species_count() == 0
        supabase_species.insert_species(sample_species)
        assert supabase_species.get_species_count() == 1

    def test_hash_count(self, patched_supabase, sample_species):
        """Hash count returns correct number."""
        assert supabase_species.get_hash_count() == 0
        species_id = supabase_species.insert_species(sample_species)
        supabase_species.insert_image_hash(species_id=species_id, image_path="a.jpg", phash="aaa")
        assert supabase_species.get_hash_count() == 1

    def test_json_fields_parsed(self, patched_supabase, sample_species):
        """JSON fields (common_names, native_regions) are parsed correctly."""
        supabase_species.insert_species(sample_species)
        result = supabase_species.get_species_by_id(supabase_species.get_species_count())
        assert isinstance(result["common_names"], list)
        assert "Test Plant" in result["common_names"]
        assert isinstance(result["native_regions"], list)
        assert "Testland" in result["native_regions"]

    def test_find_by_phash_exact(self, patched_supabase, sample_species):
        """find_by_phash returns exact match with hamming distance 0."""
        species_id = supabase_species.insert_species(sample_species)
        supabase_species.insert_image_hash(
            species_id=species_id,
            image_path="ref.jpg",
            phash="abc123def456",
        )
        matches = supabase_species.find_by_phash("abc123def456", max_distance=12)
        assert len(matches) == 1
        assert matches[0]["hamming_dist"] == 0
        assert matches[0]["scientific_name"] == "Test plantus"

    def test_find_by_phash_no_match(self, patched_supabase, sample_species):
        """find_by_phash returns empty when nothing is close."""
        species_id = supabase_species.insert_species(sample_species)
        supabase_species.insert_image_hash(
            species_id=species_id,
            image_path="ref.jpg",
            phash="0000000000000000",
        )
        matches = supabase_species.find_by_phash("ffffffffffffffff", max_distance=5)
        assert matches == []