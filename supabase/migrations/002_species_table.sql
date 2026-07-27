-- Species table for Gardenify
-- Stores plant species data for search and identification

CREATE TABLE IF NOT EXISTS species (
    id BIGSERIAL PRIMARY KEY,
    scientific_name TEXT UNIQUE NOT NULL,
    common_names JSONB DEFAULT '[]'::jsonb,
    family TEXT DEFAULT '',
    genus TEXT DEFAULT '',
    category TEXT DEFAULT '',
    native_regions JSONB DEFAULT '[]'::jsonb,
    observation_count INTEGER DEFAULT 0,
    source TEXT DEFAULT 'seed',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_species_scientific ON species(scientific_name);
CREATE INDEX IF NOT EXISTS idx_species_genus ON species(genus);
CREATE INDEX IF NOT EXISTS idx_species_family ON species(family);

-- Enable RLS
ALTER TABLE species ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Allow public read access" ON species
    FOR SELECT USING (true);

-- Service role can insert/update
CREATE POLICY "Allow service role write" ON species
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow service role update" ON species
    FOR UPDATE USING (true);
