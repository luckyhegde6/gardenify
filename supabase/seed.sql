-- Gardenify Seed Data
-- Run after migrations: psql $DATABASE_URL -f supabase/seed.sql
-- Or use: make seed

-- ============================================================
-- TEST USERS (create via Supabase Auth, then insert profile)
-- ============================================================
-- Note: Users are auto-created via the on_auth_user_created trigger.
-- These are fallback inserts if trigger hasn't run yet.

-- ============================================================
-- SAMPLE IDENTIFICATIONS (for testing UI)
-- ============================================================
-- These use a fake user_id. Replace with your actual user UUID.

do $$
declare
    test_user_id uuid := '00000000-0000-0000-0000-000000000001';
    id1 uuid;
    id2 uuid;
    id3 uuid;
    id4 uuid;
    id5 uuid;
begin
    -- Insert test user (skip if exists)
    insert into public.users (id, email, full_name, subscription_tier)
    values (test_user_id, 'test@gardenify.app', 'Test User', 'free')
    on conflict (id) do nothing;

    insert into public.user_settings (user_id, language, preferred_organ)
    values (test_user_id, 'en', 'auto')
    on conflict (user_id) do nothing;

    -- Identification 1: Rose
    insert into public.identifications (
        id, user_id, image_urls, image_hashes, best_match, score,
        species_scientific_name, species_common_names, species_family,
        species_genus, organs, raw_plantnet_response
    ) values (
        uuid_generate_v4(), test_user_id,
        array['https://example.com/rose1.jpg'],
        array['abc123hash1'],
        'Rosa gallica', 0.95,
        'Rosa gallica', array['Gallic Rose', 'French Rose', 'Common Rose'],
        'Rosaceae', 'Rosa',
        array['flower'],
        '{"results": [{"score": 0.95, "species": {"scientificNameWithoutAuthor": "Rosa gallica", "commonNames": ["Gallic Rose"], "family": {"scientificNameWithoutAuthor": "Rosaceae"}, "genus": {"scientificNameWithoutAuthor": "Rosa"}}}]}'::jsonb
    ) returning id into id1;

    -- Identification 2: Monstera
    insert into public.identifications (
        id, user_id, image_urls, image_hashes, best_match, score,
        species_scientific_name, species_common_names, species_family,
        species_genus, organs, raw_plantnet_response
    ) values (
        uuid_generate_v4(), test_user_id,
        array['https://example.com/monstera1.jpg'],
        array['def456hash2'],
        'Monstera deliciosa', 0.88,
        'Monstera deliciosa', array['Swiss Cheese Plant', 'Split-leaf Philodendron'],
        'Araceae', 'Monstera',
        array['leaf'],
        '{"results": [{"score": 0.88, "species": {"scientificNameWithoutAuthor": "Monstera deliciosa", "commonNames": ["Swiss Cheese Plant"], "family": {"scientificNameWithoutAuthor": "Araceae"}, "genus": {"scientificNameWithoutAuthor": "Monstera"}}}]}'::jsonb
    ) returning id into id2;

    -- Identification 3: Lavender
    insert into public.identifications (
        id, user_id, image_urls, image_hashes, best_match, score,
        species_scientific_name, species_common_names, species_family,
        species_genus, organs, raw_plantnet_response
    ) values (
        uuid_generate_v4(), test_user_id,
        array['https://example.com/lavender1.jpg'],
        array['ghi789hash3'],
        'Lavandula angustifolia', 0.92,
        'Lavandula angustifolia', array['English Lavender', 'True Lavender'],
        'Lamiaceae', 'Lavandula',
        array['flower'],
        '{"results": [{"score": 0.92, "species": {"scientificNameWithoutAuthor": "Lavandula angustifolia", "commonNames": ["English Lavender"], "family": {"scientificNameWithoutAuthor": "Lamiaceae"}, "genus": {"scientificNameWithoutAuthor": "Lavandula"}}}]}'::jsonb
    ) returning id into id3;

    -- Identification 4: Oak Tree
    insert into public.identifications (
        id, user_id, image_urls, image_hashes, best_match, score,
        species_scientific_name, species_common_names, species_family,
        species_genus, organs, raw_plantnet_response
    ) values (
        uuid_generate_v4(), test_user_id,
        array['https://example.com/oak1.jpg'],
        array['jkl012hash4'],
        'Quercus robur', 0.85,
        'Quercus robur', array['English Oak', 'Pedunculate Oak'],
        'Fagaceae', 'Quercus',
        array['leaf', 'bark'],
        '{"results": [{"score": 0.85, "species": {"scientificNameWithoutAuthor": "Quercus robur", "commonNames": ["English Oak"], "family": {"scientificNameWithoutAuthor": "Fagaceae"}, "genus": {"scientificNameWithoutAuthor": "Quercus"}}}]}'::jsonb
    ) returning id into id4;

    -- Identification 5: Tomato
    insert into public.identifications (
        id, user_id, image_urls, image_hashes, best_match, score,
        species_scientific_name, species_common_names, species_family,
        species_genus, organs, raw_plantnet_response
    ) values (
        uuid_generate_v4(), test_user_id,
        array['https://example.com/tomato1.jpg'],
        array['mno345hash5'],
        'Solanum lycopersicum', 0.91,
        'Solanum lycopersicum', array['Tomato', 'Garden Tomato'],
        'Solanaceae', 'Solanum',
        array['fruit'],
        '{"results": [{"score": 0.91, "species": {"scientificNameWithoutAuthor": "Solanum lycopersicum", "commonNames": ["Tomato"], "family": {"scientificNameWithoutAuthor": "Solanaceae"}, "genus": {"scientificNameWithoutAuthor": "Solanum"}}}]}'::jsonb
    ) returning id into id5;

    -- Add some favorites
    insert into public.favorites (user_id, identification_id, notes)
    values
        (test_user_id, id1, 'Beautiful rose in the garden'),
        (test_user_id, id3, 'Lavender from the farmers market'),
        (test_user_id, id5, 'My tomato plant')
    on conflict do nothing;

    raise notice 'Seed data inserted successfully';
    raise notice 'Test user ID: %', test_user_id;
    raise notice 'Created 5 identifications and 3 favorites';
end $$;

-- ============================================================
-- CARE PROFILES REFERENCE (for documentation)
-- ============================================================
-- The app uses Python care profiles, not database.
-- See api/services/plant_care.py for care data.
--
-- Profile types: default, succulent, tropical, herb, tree
-- Maps: genus → profile, family → profile, fallback → default
