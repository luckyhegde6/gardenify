-- Image hashes table for local (Supabase-backed) identification.
-- Replaces the SQLite `image_hashes` table so perceptual-hash matching works
-- on Vercel (where SQLite never ships) and against local Supabase in dev.

CREATE TABLE IF NOT EXISTS public.image_hashes (
    id BIGSERIAL PRIMARY KEY,
    species_id BIGINT REFERENCES public.species(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    phash TEXT NOT NULL,
    dhash TEXT DEFAULT '',
    category TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_image_hashes_phash ON public.image_hashes(phash);
CREATE INDEX IF NOT EXISTS idx_image_hashes_dhash ON public.image_hashes(dhash);
CREATE INDEX IF NOT EXISTS idx_image_hashes_species ON public.image_hashes(species_id);

-- Enable RLS
ALTER TABLE public.image_hashes ENABLE ROW LEVEL SECURITY;

-- Public read access (same as species)
CREATE POLICY "Allow public read image hashes" ON public.image_hashes
    FOR SELECT USING (true);

-- Service role can insert/update
CREATE POLICY "Allow service role write image hashes" ON public.image_hashes
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow service role update image hashes" ON public.image_hashes
    FOR UPDATE USING (true);
