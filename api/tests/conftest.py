"""Shared test fixtures for Gardenify API tests."""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest


class _FakeResp:
    """Minimal stand-in for supabase PostgRESTResponse."""

    def __init__(self, data, count=None):
        self.data = data
        self.count = count


class _FakeQuery:
    """Chainable query builder backed by in-memory tables.

    Supports the subset of the Supabase client query API used by
    ``supabase_species`` and ``seed_supabase_gbif``.
    """

    def __init__(self, client, table):
        self._client = client
        self._table = table
        self._cols = "*"
        self._filters = []  # (op, key, value)
        self._order = None
        self._limit = None
        self._count = False
        self._insert_payload = None
        self._update_payload = None
        self._upsert_payload = None
        self._on_conflict = None

    def select(self, cols="*", count=None):
        if count:
            self._count = True
        self._cols = cols
        return self

    def eq(self, key, value):
        self._filters.append(("eq", key, value))
        return self

    def in_(self, key, values):
        self._filters.append(("in", key, values))
        return self

    def or_(self, expr):
        self._filters.append(("or", None, expr))
        return self

    def order(self, col, desc=False):
        self._order = (col, bool(desc))
        return self

    def limit(self, n):
        self._limit = n
        return self

    def insert(self, payload):
        self._insert_payload = payload
        return self

    def update(self, payload):
        self._update_payload = payload
        return self

    def upsert(self, rows, on_conflict=None, ignore_duplicates=False):
        self._upsert_payload = rows
        self._on_conflict = on_conflict
        return self

    def execute(self):
        return self._client._execute(self)


class FakeSupabaseClient:
    """In-memory fake of the Supabase client for offline tests."""

    def __init__(self):
        self.tables = {}

    def table(self, table_name):
        if table_name not in self.tables:
            self.tables[table_name] = []
        return _FakeQuery(self, table_name)

    def _execute(self, q: _FakeQuery):
        table = q._table
        if q._insert_payload is not None:
            return self._insert(table, q._insert_payload)
        if q._update_payload is not None:
            return self._update(table, q._update_payload)
        if q._upsert_payload is not None:
            return self._upsert(table, q._upsert_payload, q._on_conflict)
        return self._select(
            table,
            cols=q._cols,
            filters=q._filters,
            order=q._order,
            limit=q._limit,
            count=q._count,
        )

    def _insert(self, table, payload):
        rows = payload if isinstance(payload, list) else [payload]
        inserted = []
        for row in rows:
            new_row = dict(row)
            new_row["id"] = self._next_id(table)
            self.tables[table].append(new_row)
            inserted.append(new_row)
        return _FakeResp(inserted)

    def _update(self, table, payload):
        rows = self.tables[table]
        updated = []
        for row in rows:
            row.update(payload)
            updated.append(row)
        return _FakeResp(updated)

    def _upsert(self, table, rows, conflict_col):
        conflict_col = conflict_col or "id"
        updated = []
        inserted = []
        for row in rows:
            existing = next(
                (r for r in self.tables[table] if r.get(conflict_col) == row.get(conflict_col)),
                None,
            )
            if existing is not None:
                existing.update(dict(row))
                updated.append(existing)
            else:
                new_row = dict(row)
                new_row["id"] = self._next_id(table)
                self.tables[table].append(new_row)
                inserted.append(new_row)
        return _FakeResp(inserted + updated)

    def _select(self, table, cols, filters, order, limit, count):
        rows = self.tables[table]
        for op, key, value in filters:
            if op == "eq":
                rows = [r for r in rows if r.get(key) == value]
            elif op == "in":
                rows = [r for r in rows if r.get(key) in value]
            elif op == "or":
                rows = [r for r in rows if _matches_ilike_or(r, value)]

        # Resolve embedded species join (e.g. select(... species(id, name) ...))
        if isinstance(cols, str) and "species(" in cols:
            species_table = self.tables.get("species", [])
            for row in rows:
                row["species"] = next(
                    (s for s in species_table if s.get("id") == row.get("species_id")),
                    {},
                )

        if order:
            col, desc = order
            rows = sorted(
                rows,
                key=lambda r: (r.get(col) is None, r.get(col)),
                reverse=desc,
            )
        if limit is not None:
            rows = rows[:limit]

        if count:
            return _FakeResp(list(rows), len(rows))
        return _FakeResp(list(rows))

    def _next_id(self, table):
        return max((r.get("id", 0) for r in self.tables[table]), default=0) + 1


def _matches_ilike_or(row, expr):
    """Match a PostgREST OR expression like 'a.ilike.%q%,b.ilike.%q%'."""
    for clause in expr.split(","):
        clause = clause.strip()
        match = re.match(r"([\w]+)\.ilike\.%(.*)%", clause)
        if match:
            col, needle = match.group(1), match.group(2).lower()
            if needle in str(row.get(col, "")).lower():
                return True
    return False


@pytest.fixture
def patched_supabase(monkeypatch):
    """Patch every Supabase client entry point with a shared fake DB."""
    client = FakeSupabaseClient()

    import api.services.supabase_species  # noqa: F401  (module import for patch)
    from api import services
    from api.data.importers import seed_supabase_gbif

    monkeypatch.setattr(services.supabase_species, "_get_client", lambda: client)
    monkeypatch.setattr(seed_supabase_gbif, "_get_client", lambda: client)
    return client


@pytest.fixture
def sample_species():
    """Sample species data for testing."""
    return {
        "scientific_name": "Test plantus",
        "common_names": ["Test Plant", "Testing Flower"],
        "family": "Testaceae",
        "genus": "Testus",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["Testland"],
        "observation_count": 42,
        "source": "test",
    }


@pytest.fixture
def sample_image_bytes():
    """Create a minimal valid JPEG image for testing."""
    from io import BytesIO

    from PIL import Image

    img = Image.new("RGB", (64, 64), color=(128, 200, 128))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()