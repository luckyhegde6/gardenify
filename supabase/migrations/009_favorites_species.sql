-- Favorites are species-based: the app writes species_* columns and lists
-- saved plants per species (see src/app/(tabs)/favorites.tsx and the Save
-- button in src/app/identification/[id].tsx). The original schema (001)
-- modeled favorites as identification-based (identification_id NOT NULL),
-- which never matched the app, so every "Save" insert failed.
alter table public.favorites
    drop column if exists identification_id,
    drop column if exists notes,
    add column if not exists species_scientific_name text not null default '',
    add column if not exists species_common_name text default '',
    add column if not exists species_family text default '',
    add column if not exists species_genus text default '';

-- The original unique(user_id, identification_id) is dropped automatically
--when identification_id column is removed. Enforce uniqueness per species.
create unique index if not exists favorites_user_species_uniq
    on public.favorites (user_id, species_scientific_name);