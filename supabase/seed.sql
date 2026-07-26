-- Seed data for Gardenify
-- Run after migrations

-- Note: Admin user should be created via Supabase Auth signup
-- This seed is for reference and sample data only

-- Sample identifications (will be created via the app)
-- The actual user and identification data is created at runtime
-- via Supabase Auth and the PlantNet API

-- Verify migrations ran correctly
do $$
begin
    -- Check tables exist
    assert (select count(*) from information_schema.tables
            where table_schema = 'public' and table_name = 'users') > 0,
           'users table not found';
    assert (select count(*) from information_schema.tables
            where table_schema = 'public' and table_name = 'identifications') > 0,
           'identifications table not found';
    assert (select count(*) from information_schema.tables
            where table_schema = 'public' and table_name = 'favorites') > 0,
           'favorites table not found';
    assert (select count(*) from information_schema.tables
            where table_schema = 'public' and table_name = 'user_settings') > 0,
           'user_settings table not found';

    raise notice 'All tables created successfully';
end $$;
