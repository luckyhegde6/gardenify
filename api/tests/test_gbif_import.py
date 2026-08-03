"""Tests for GBIF importer."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestGBIFDownload:
    """Test GBIF archive download."""

    @patch("api.data.importers.import_gbif.requests.get")
    def test_download_creates_file(self, mock_get, tmp_path):
        """Test download saves zip file."""

        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"content-length": "1000"}
        mock_response.iter_content.return_value = [b"data"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Temp override cache dir
        with patch("api.data.importers.import_gbif.GBIF_CACHE_DIR", tmp_path):
            from api.data.importers.import_gbif import download_gbif_archive
            result = download_gbif_archive(force=True)

            assert result.exists()
            mock_get.assert_called_once()


class TestGBIFExtraction:
    """Test species extraction from archive."""

    def test_extract_species_from_txt(self, tmp_path):
        """Test extraction from tab-separated occurrence.txt."""
        import zipfile

        # Create a minimal test archive
        zip_path = tmp_path / "test.zip"
        occurrence = (
            "id\tlicense\tscientificName\tkingdom\ttaxonRank\n"
            "1\tcc\tMonstera deliciosa\tPlantae\tspecies\n"
            "2\tcc\tFicus benjamina\tPlantae\tspecies\n"
            "3\tcc\tMonstera deliciosa\tPlantae\tspecies\n"
        )

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("occurrence.txt", occurrence)

        from api.data.importers.import_gbif import extract_unique_species
        species = extract_unique_species(zip_path, max_species=100)

        assert len(species) == 2
        names = {s["scientific_name"] for s in species}
        assert "Monstera deliciosa" in names
        assert "Ficus benjamina" in names

        # Monstera should have count 2 (appeared twice)
        monstera = next(s for s in species if s["scientific_name"] == "Monstera deliciosa")
        assert monstera["observation_count"] == 2
        assert monstera["genus"] == "Monstera"

    def test_extract_species_limit(self, tmp_path):
        """Test max_species limit is respected."""
        import zipfile

        zip_path = tmp_path / "test.zip"
        lines = ["id\tlicense\tscientificName\n"]
        for i in range(50):
            lines.append(f"{i}\tcc\tSpecies{i} plant\n")

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("occurrence.txt", "\n".join(lines))

        from api.data.importers.import_gbif import extract_unique_species
        species = extract_unique_species(zip_path, max_species=10)

        assert len(species) == 10

    def test_extract_species_strips_author(self, tmp_path):
        """Test author names are stripped from scientific names."""
        import zipfile

        zip_path = tmp_path / "test.zip"
        occurrence = (
            "id\tscientificName\n"
            "1\tQuercus robur L.\n"
            "2\tRosa damascena Mill.\n"
        )

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("occurrence.txt", occurrence)

        from api.data.importers.import_gbif import extract_unique_species
        species = extract_unique_species(zip_path, max_species=100)

        names = {s["scientific_name"] for s in species}
        assert "Quercus robur" in names
        assert "Rosa damascena" in names
        # Authors should be removed
        assert "Quercus robur L." not in names

    def test_extract_empty_archive(self, tmp_path):
        """Test extraction from archive with no occurrence file."""
        import zipfile

        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("eml.xml", "<eml/>")

        from api.data.importers.import_gbif import extract_unique_species
        species = extract_unique_species(zip_path, max_species=100)

        assert species == []


class TestSupabaseSeedMapping:
    """Test mapping importer species dicts to Supabase columns."""

    def test_species_rows_json_encoded(self):
        from api.data.importers.seed_supabase_gbif import _species_rows

        rows = _species_rows([{
            "scientific_name": "Rosa damascena",
            "common_names": ["Damask Rose"],
            "family": "Rosaceae",
            "genus": "Rosa",
            "category": "woody_plant",
            "native_regions": ["Middle East"],
            "observation_count": 5,
            "source": "gbif",
        }])

        assert rows[0]["scientific_name"] == "Rosa damascena"
        # jsonb columns must be real lists, not JSON strings
        assert rows[0]["common_names"] == ["Damask Rose"]
        assert rows[0]["native_regions"] == ["Middle East"]
        assert rows[0]["observation_count"] == 5
        assert rows[0]["source"] == "gbif"

    def test_species_rows_missing_optional_fields(self):
        from api.data.importers.seed_supabase_gbif import _species_rows

        rows = _species_rows([{"scientific_name": "Monstera deliciosa", "observation_count": 3}])
        assert rows[0]["family"] == ""
        assert rows[0]["genus"] == ""
        assert rows[0]["common_names"] == []
        assert rows[0]["native_regions"] == []

    def test_requires_supabase_env(self):
        import os

        from api.data.importers.seed_supabase_gbif import _get_client

        old_url = os.environ.get("SUPABASE_URL")
        old_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        os.environ.pop("SUPABASE_URL", None)
        os.environ.pop("SUPABASE_SERVICE_ROLE_KEY", None)
        try:
            import pytest
            with pytest.raises(RuntimeError):
                _get_client()
        finally:
            if old_url is not None:
                os.environ["SUPABASE_URL"] = old_url
            if old_key is not None:
                os.environ["SUPABASE_SERVICE_ROLE_KEY"] = old_key


class TestGBIFImport:
    """Test import to Supabase."""

    def test_import_to_database(self, patched_supabase):
        """Test species are inserted via the shared seed helper."""

        species_list = [
            {
                "scientific_name": "Test species",
                "common_names": [],
                "family": "Testaceae",
                "genus": "Testus",
                "category": "",
                "native_regions": [],
                "observation_count": 42,
                "source": "gbif",
            }
        ]

        from api.data.importers.import_gbif import import_to_database
        result = import_to_database(species_list)

        assert result["inserted"] == 1
        assert result["errors"] == 0

        # Verify in fake Supabase
        rows = patched_supabase.tables["species"]
        assert len(rows) == 1
        assert rows[0]["genus"] == "Testus"
        assert rows[0]["observation_count"] == 42
