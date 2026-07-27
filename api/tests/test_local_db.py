"""Tests for local database operations."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))



class TestLocalDB:
    def test_init_db(self, tmp_db):
        """Database initialization creates tables."""
        import sqlite3
        conn = sqlite3.connect(str(tmp_db.DB_PATH))
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        assert "species" in table_names
        assert "image_hashes" in table_names
        conn.close()

    def test_insert_species(self, tmp_db, sample_species):
        """Insert a species and retrieve it."""
        species_id = tmp_db.insert_species(sample_species)
        assert species_id is not None
        assert species_id > 0

        result = tmp_db.get_species_by_id(species_id)
        assert result is not None
        assert result["scientific_name"] == "Test plantus"
        assert result["family"] == "Testaceae"
        assert result["genus"] == "Testus"

    def test_insert_species_upsert(self, tmp_db, sample_species):
        """Inserting same species twice updates rather than duplicates."""
        id1 = tmp_db.insert_species(sample_species)
        # Insert again with higher observation count — adds to existing
        sample_species["observation_count"] = 100
        id2 = tmp_db.insert_species(sample_species)
        assert id1 == id2  # Same ID = update, not insert

        result = tmp_db.get_species_by_id(id1)
        assert result["observation_count"] == 142  # 42 + 100

    def test_search_species(self, tmp_db, sample_species):
        """Search finds species by scientific name."""
        tmp_db.insert_species(sample_species)
        results = tmp_db.search_species("test")
        assert len(results) >= 1
        assert any(r["scientific_name"] == "Test plantus" for r in results)

    def test_search_species_by_genus(self, tmp_db, sample_species):
        """Search finds species by genus."""
        tmp_db.insert_species(sample_species)
        results = tmp_db.search_species("testus")
        assert len(results) >= 1

    def test_search_species_by_family(self, tmp_db, sample_species):
        """Search finds species by family."""
        tmp_db.insert_species(sample_species)
        results = tmp_db.search_species("testaceae")
        assert len(results) >= 1

    def test_search_species_limit(self, tmp_db):
        """Search respects limit parameter."""
        for i in range(10):
            tmp_db.insert_species({
                "scientific_name": f"Species testus {i}",
                "observation_count": i,
            })
        results = tmp_db.search_species("testus", limit=5)
        assert len(results) <= 5

    def test_get_species_not_found(self, tmp_db):
        """Getting non-existent species returns None."""
        result = tmp_db.get_species_by_id(99999)
        assert result is None

    def test_get_species_by_name(self, tmp_db, sample_species):
        """Get species by exact scientific name."""
        tmp_db.insert_species(sample_species)
        result = tmp_db.get_species_by_name("Test plantus")
        assert result is not None
        assert result["scientific_name"] == "Test plantus"

    def test_get_species_by_name_not_found(self, tmp_db):
        """Getting non-existent species by name returns None."""
        result = tmp_db.get_species_by_name("Nonexistent plantus")
        assert result is None

    def test_insert_image_hash(self, tmp_db, sample_species):
        """Insert an image hash record."""
        species_id = tmp_db.insert_species(sample_species)
        hash_id = tmp_db.insert_image_hash(
            species_id=species_id,
            image_path="test/image.jpg",
            phash="abc123def456",
            dhash="abc123def456",
            category="herb",
        )
        assert hash_id is not None
        assert hash_id > 0

    def test_get_species_images(self, tmp_db, sample_species):
        """Species detail includes images."""
        species_id = tmp_db.insert_species(sample_species)
        tmp_db.insert_image_hash(
            species_id=species_id,
            image_path="test.jpg",
            phash="abc123",
        )
        result = tmp_db.get_species_by_id(species_id)
        assert len(result["images"]) == 1
        assert result["images"][0]["image_path"] == "test.jpg"

    def test_species_count(self, tmp_db, sample_species):
        """Species count returns correct number."""
        assert tmp_db.get_species_count() == 0
        tmp_db.insert_species(sample_species)
        assert tmp_db.get_species_count() == 1

    def test_hash_count(self, tmp_db, sample_species):
        """Hash count returns correct number."""
        assert tmp_db.get_hash_count() == 0
        species_id = tmp_db.insert_species(sample_species)
        tmp_db.insert_image_hash(species_id=species_id, image_path="a.jpg", phash="aaa")
        assert tmp_db.get_hash_count() == 1

    def test_json_fields_parsed(self, tmp_db, sample_species):
        """JSON fields (common_names, native_regions) are parsed correctly."""
        tmp_db.insert_species(sample_species)
        result = tmp_db.get_species_by_id(tmp_db.get_species_count())
        assert isinstance(result["common_names"], list)
        assert "Test Plant" in result["common_names"]
        assert isinstance(result["native_regions"], list)
        assert "Testland" in result["native_regions"]
