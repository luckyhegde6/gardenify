-- Gardenify Local Plant Database Schema
-- SQLite3 — for local development and offline fallback

CREATE TABLE IF NOT EXISTS species (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scientific_name TEXT UNIQUE NOT NULL,
    common_names TEXT DEFAULT '[]',
    family TEXT DEFAULT '',
    genus TEXT DEFAULT '',
    category TEXT DEFAULT '',
    native_regions TEXT DEFAULT '[]',
    observation_count INTEGER DEFAULT 0,
    source TEXT DEFAULT 'plantnet300k',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_species_scientific ON species(scientific_name);
CREATE INDEX IF NOT EXISTS idx_species_genus ON species(genus);
CREATE INDEX IF NOT EXISTS idx_species_family ON species(family);
CREATE INDEX IF NOT EXISTS idx_species_category ON species(category);

CREATE TABLE IF NOT EXISTS image_hashes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id INTEGER REFERENCES species(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    phash TEXT NOT NULL,
    dhash TEXT DEFAULT '',
    category TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_phash ON image_hashes(phash);
CREATE INDEX IF NOT EXISTS idx_dhash ON image_hashes(dhash);
CREATE INDEX IF NOT EXISTS idx_image_species ON image_hashes(species_id);

CREATE TABLE IF NOT EXISTS import_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    status TEXT DEFAULT 'started',
    records_imported INTEGER DEFAULT 0,
    error_message TEXT DEFAULT '',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
