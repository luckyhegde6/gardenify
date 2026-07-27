"""Tests for species API routes."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.services import local_db


@pytest.fixture
def client():
    """Test client with seeded database."""
    # Initialize and seed the database
    local_db.init_db()
    from api.data.importers.seed_species import seed_database
    seed_database()
    return TestClient(app)


class TestListSpecies:
    def test_list_all_species(self, client):
        """GET /api/species returns species list."""
        response = client.get("/api/species")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "total_species" in data
        assert "results" in data
        assert data["total_species"] >= 20

    def test_list_species_with_limit(self, client):
        """Limit parameter controls result count."""
        response = client.get("/api/species?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 5


class TestSearchSpecies:
    def test_search_by_scientific_name(self, client):
        """Search by scientific name finds matches."""
        response = client.get("/api/species?q=monstera")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        assert any("Monstera" in r["scientific_name"] for r in data["results"])

    def test_search_by_common_name(self, client):
        """Search by common name finds matches."""
        response = client.get("/api/species?q=sunflower")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1

    def test_search_by_genus(self, client):
        """Search by genus finds matches."""
        response = client.get("/api/species?q=ficus")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        assert any(r["genus"] == "Ficus" for r in data["results"])

    def test_search_by_family(self, client):
        """Search by family finds matches."""
        response = client.get("/api/species?q=araceae")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1

    def test_search_no_results(self, client):
        """Search with no matches returns empty list."""
        response = client.get("/api/species?q=zzzznonexistent")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0

    def test_search_empty_query(self, client):
        """Empty query returns all species."""
        response = client.get("/api/species?q=")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 20


class TestGetSpecies:
    def test_get_species_by_id(self, client):
        """GET /api/species/{id} returns species detail."""
        response = client.get("/api/species/1")
        assert response.status_code == 200
        data = response.json()
        assert "scientific_name" in data
        assert "common_names" in data
        assert "family" in data
        assert "genus" in data
        assert "images" in data

    def test_get_species_not_found(self, client):
        """GET /api/species/{id} with invalid ID returns 404."""
        response = client.get("/api/species/99999")
        assert response.status_code == 404

    def test_get_species_by_name(self, client):
        """GET /api/species/by-name/{name} returns species."""
        response = client.get("/api/species/by-name/Monstera%20deliciosa")
        assert response.status_code == 200
        data = response.json()
        assert data["scientific_name"] == "Monstera deliciosa"

    def test_get_species_by_name_not_found(self, client):
        """GET /api/species/by-name/{name} with invalid name returns 404."""
        response = client.get("/api/species/by-name/Nonexistent%20plantus")
        assert response.status_code == 404


class TestSpeciesData:
    def test_species_has_correct_fields(self, client):
        """Species response has all expected fields."""
        response = client.get("/api/species/1")
        data = response.json()
        required = ["id", "scientific_name", "common_names", "family",
                     "genus", "category", "native_regions", "observation_count"]
        for field in required:
            assert field in data, f"Missing field: {field}"

    def test_common_names_is_list(self, client):
        """common_names is a JSON-parsed list."""
        response = client.get("/api/species/1")
        data = response.json()
        assert isinstance(data["common_names"], list)

    def test_native_regions_is_list(self, client):
        """native_regions is a JSON-parsed list."""
        response = client.get("/api/species/1")
        data = response.json()
        assert isinstance(data["native_regions"], list)
