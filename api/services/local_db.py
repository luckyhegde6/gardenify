"""SQLite connection and query helpers for local plant database."""

import json
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "gardenify.db"
SCHEMA_PATH = DB_DIR / "schema.sql"


def is_available() -> bool:
    """Check if local SQLite database exists."""
    return DB_PATH.exists()


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
        logger.info("Local database initialized at %s", DB_PATH)
    finally:
        conn.close()


def search_species(query: str, limit: int = 20) -> list[dict]:
    """Fuzzy search by scientific or common name."""
    conn = get_connection()
    try:
        q = f"%{query}%"
        rows = conn.execute(
            """SELECT id, scientific_name, common_names, family, genus,
                      category, native_regions, observation_count
               FROM species
               WHERE scientific_name LIKE ? OR common_names LIKE ?
                  OR genus LIKE ? OR family LIKE ?
               ORDER BY observation_count DESC
               LIMIT ?""",
            (q, q, q, q, limit),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_species_by_id(species_id: int) -> dict | None:
    """Get full species detail by ID."""
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT id, scientific_name, common_names, family, genus,
                      category, native_regions, observation_count, source
               FROM species WHERE id = ?""",
            (species_id,),
        ).fetchone()
        if not row:
            return None
        result = _row_to_dict(row)
        result["images"] = _get_species_images(conn, species_id)
        return result
    finally:
        conn.close()


def get_species_by_name(scientific_name: str) -> dict | None:
    """Get species by exact scientific name."""
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT id, scientific_name, common_names, family, genus,
                      category, native_regions, observation_count, source
               FROM species WHERE scientific_name = ?""",
            (scientific_name,),
        ).fetchone()
        if not row:
            return None
        result = _row_to_dict(row)
        result["images"] = _get_species_images(conn, row["id"])
        return result
    finally:
        conn.close()


def find_by_phash(phash: str, max_distance: int = 10) -> list[dict]:
    """Find species by perceptual hash using Hamming distance.

    SQLite doesn't support XOR, so we fetch all hashes and compute
    Hamming distance in Python. Fast enough for <100K hashes.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT s.id, s.scientific_name, s.common_names, s.family,
                      s.genus, s.category, ih.image_path, ih.phash
               FROM image_hashes ih
               JOIN species s ON s.id = ih.species_id"""
        ).fetchall()

        matches = []
        for row in rows:
            candidate = row["phash"]
            if not candidate:
                continue
            dist = _hamming_distance(phash, candidate)
            if dist <= max_distance:
                d = dict(row)
                d["hamming_dist"] = dist
                del d["phash"]  # Don't expose raw hash in response
                matches.append(d)

        matches.sort(key=lambda x: x["hamming_dist"])
        return matches
    finally:
        conn.close()


def _hamming_distance(h1: str, h2: str) -> int:
    """Compute Hamming distance between two hex hash strings."""
    dist = 0
    for c1, c2 in zip(h1, h2):
        xor = int(c1, 16) ^ int(c2, 16)
        dist += xor.bit_count()
    return dist


def insert_species(species_data: dict) -> int:
    """Insert or update a species. Returns the species ID."""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM species WHERE scientific_name = ?",
            (species_data["scientific_name"],),
        ).fetchone()

        if existing:
            conn.execute(
                """UPDATE species SET
                    common_names = COALESCE(?, common_names),
                    family = COALESCE(NULLIF(?, ''), family),
                    genus = COALESCE(NULLIF(?, ''), genus),
                    category = COALESCE(NULLIF(?, ''), category),
                    native_regions = COALESCE(?, native_regions),
                    observation_count = observation_count + ?
                   WHERE id = ?""",
                (
                    species_data.get("common_names"),
                    species_data.get("family", ""),
                    species_data.get("genus", ""),
                    species_data.get("category", ""),
                    species_data.get("native_regions"),
                    species_data.get("observation_count", 1),
                    existing["id"],
                ),
            )
            conn.commit()
            return existing["id"]

        cursor = conn.execute(
            """INSERT INTO species
                (scientific_name, common_names, family, genus, category,
                 native_regions, observation_count, source)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                species_data["scientific_name"],
                species_data.get("common_names", "[]"),
                species_data.get("family", ""),
                species_data.get("genus", ""),
                species_data.get("category", ""),
                species_data.get("native_regions", "[]"),
                species_data.get("observation_count", 1),
                species_data.get("source", "manual"),
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def insert_image_hash(species_id: int, image_path: str,
                      phash: str, dhash: str = "", category: str = "") -> int:
    """Insert an image hash record."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO image_hashes (species_id, image_path, phash, dhash, category)
               VALUES (?, ?, ?, ?, ?)""",
            (species_id, image_path, phash, dhash, category),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_species_count() -> int:
    """Get total species count."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) as cnt FROM species").fetchone()
        return row["cnt"]
    finally:
        conn.close()


def get_hash_count() -> int:
    """Get total image hash count."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) as cnt FROM image_hashes").fetchone()
        return row["cnt"]
    finally:
        conn.close()


def _get_species_images(conn: sqlite3.Connection, species_id: int) -> list[dict]:
    """Get image hashes for a species."""
    rows = conn.execute(
        """SELECT image_path, phash, dhash, category
           FROM image_hashes WHERE species_id = ?""",
        (species_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a SQLite Row to dict, parsing JSON fields."""
    d = dict(row)
    for key in ("common_names", "native_regions"):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                d[key] = []
    return d
