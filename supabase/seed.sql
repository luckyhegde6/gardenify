-- Gardenify Seed Data
-- Run after migrations

do $$
declare
    v_admin uuid;
    v_user1 uuid;
    v_user2 uuid;
    id1 uuid;
    id2 uuid;
    id3 uuid;
    id4 uuid;
    id5 uuid;
begin
    -- Create admin user
    v_admin := uuid_generate_v4();
    insert into auth.users (id, instance_id, aud, role, email, encrypted_password, email_confirmed_at, last_sign_in_at, raw_app_meta_data, raw_user_meta_data, created_at, updated_at, confirmation_token, email_change, email_change_token_new, recovery_token, is_sso_user, is_anonymous)
    values (v_admin, '00000000-0000-0000-0000-000000000000', 'authenticated', 'authenticated', 'admin@gardenify.app', crypt('admin12345678', gen_salt('bf')), now(), now(), '{"provider":"email","providers":["email"]}', '{"full_name":"Admin User"}', now(), now(), '', '', '', '', false, false);
    insert into auth.identities (user_id, identity_data, provider, provider_id, last_sign_in_at, created_at, updated_at)
    values (v_admin, jsonb_build_object('sub', v_admin, 'email', 'admin@gardenify.app', 'email_verified', true, 'phone_verified', false), 'email', 'admin@gardenify.app', now(), now(), now());

    -- Create test user 1
    v_user1 := uuid_generate_v4();
    insert into auth.users (id, instance_id, aud, role, email, encrypted_password, email_confirmed_at, last_sign_in_at, raw_app_meta_data, raw_user_meta_data, created_at, updated_at, confirmation_token, email_change, email_change_token_new, recovery_token, is_sso_user, is_anonymous)
    values (v_user1, '00000000-0000-0000-0000-000000000000', 'authenticated', 'authenticated', 'test@gardenify.app', crypt('test12345678', gen_salt('bf')), now(), now(), '{"provider":"email","providers":["email"]}', '{"full_name":"Test User"}', now(), now(), '', '', '', '', false, false);
    insert into auth.identities (user_id, identity_data, provider, provider_id, last_sign_in_at, created_at, updated_at)
    values (v_user1, jsonb_build_object('sub', v_user1, 'email', 'test@gardenify.app', 'email_verified', true, 'phone_verified', false), 'email', 'test@gardenify.app', now(), now(), now());

    -- Create test user 2
    v_user2 := uuid_generate_v4();
    insert into auth.users (id, instance_id, aud, role, email, encrypted_password, email_confirmed_at, last_sign_in_at, raw_app_meta_data, raw_user_meta_data, created_at, updated_at, confirmation_token, email_change, email_change_token_new, recovery_token, is_sso_user, is_anonymous)
    values (v_user2, '00000000-0000-0000-0000-000000000000', 'authenticated', 'authenticated', 'user2@gardenify.app', crypt('test12345678', gen_salt('bf')), now(), now(), '{"provider":"email","providers":["email"]}', '{"full_name":"Jane Botanist"}', now(), now(), '', '', '', '', false, false);
    insert into auth.identities (user_id, identity_data, provider, provider_id, last_sign_in_at, created_at, updated_at)
    values (v_user2, jsonb_build_object('sub', v_user2, 'email', 'user2@gardenify.app', 'email_verified', true, 'phone_verified', false), 'email', 'user2@gardenify.app', now(), now(), now());

    -- Mark admin (the handle_new_user trigger auto-creates profiles)
    update public.users set full_name = 'Admin User', subscription_tier = 'premium', is_admin = true
    where id = v_admin;

    update public.users set full_name = 'Test User', subscription_tier = 'free'
    where id = v_user1;

    update public.users set full_name = 'Jane Botanist', subscription_tier = 'pro'
    where id = v_user2;

    -- Update user settings
    update public.user_settings set language = 'en', preferred_organ = 'auto'
    where user_id = v_user1;

    update public.user_settings set language = 'fr', preferred_organ = 'flower'
    where user_id = v_user2;

    -- Identifications (v_user1's data)
    insert into public.identifications (user_id, image_urls, image_hashes, best_match, score, species_scientific_name, species_common_names, species_family, species_genus, organs, raw_plantnet_response)
    values (v_user1, array['https://example.com/rose1.jpg'], array['abc123hash1'], 'Rosa gallica', 0.95, 'Rosa gallica', array['Gallic Rose','French Rose','Common Rose'], 'Rosaceae', 'Rosa', array['flower'], '{"results":[{"score":0.95,"species":{"scientificNameWithoutAuthor":"Rosa gallica","commonNames":["Gallic Rose"],"family":{"scientificNameWithoutAuthor":"Rosaceae"},"genus":{"scientificNameWithoutAuthor":"Rosa"}}}]}'::jsonb)
    returning id into id1;

    insert into public.identifications (user_id, image_urls, image_hashes, best_match, score, species_scientific_name, species_common_names, species_family, species_genus, organs, raw_plantnet_response)
    values (v_user1, array['https://example.com/monstera1.jpg'], array['def456hash2'], 'Monstera deliciosa', 0.88, 'Monstera deliciosa', array['Swiss Cheese Plant','Split-leaf Philodendron'], 'Araceae', 'Monstera', array['leaf'], '{"results":[{"score":0.88,"species":{"scientificNameWithoutAuthor":"Monstera deliciosa","commonNames":["Swiss Cheese Plant"],"family":{"scientificNameWithoutAuthor":"Araceae"},"genus":{"scientificNameWithoutAuthor":"Monstera"}}}]}'::jsonb)
    returning id into id2;

    insert into public.identifications (user_id, image_urls, image_hashes, best_match, score, species_scientific_name, species_common_names, species_family, species_genus, organs, raw_plantnet_response)
    values (v_user1, array['https://example.com/lavender1.jpg'], array['ghi789hash3'], 'Lavandula angustifolia', 0.92, 'Lavandula angustifolia', array['English Lavender','True Lavender'], 'Lamiaceae', 'Lavandula', array['flower'], '{"results":[{"score":0.92,"species":{"scientificNameWithoutAuthor":"Lavandula angustifolia","commonNames":["English Lavender"],"family":{"scientificNameWithoutAuthor":"Lamiaceae"},"genus":{"scientificNameWithoutAuthor":"Lavandula"}}}]}'::jsonb)
    returning id into id3;

    -- Identifications (v_user2's data)
    insert into public.identifications (user_id, image_urls, image_hashes, best_match, score, species_scientific_name, species_common_names, species_family, species_genus, organs, raw_plantnet_response)
    values (v_user2, array['https://example.com/oak1.jpg'], array['jkl012hash4'], 'Quercus robur', 0.85, 'Quercus robur', array['English Oak','Pedunculate Oak'], 'Fagaceae', 'Quercus', array['leaf','bark'], '{"results":[{"score":0.85,"species":{"scientificNameWithoutAuthor":"Quercus robur","commonNames":["English Oak"],"family":{"scientificNameWithoutAuthor":"Fagaceae"},"genus":{"scientificNameWithoutAuthor":"Quercus"}}}]}'::jsonb)
    returning id into id4;

    insert into public.identifications (user_id, image_urls, image_hashes, best_match, score, species_scientific_name, species_common_names, species_family, species_genus, organs, raw_plantnet_response)
    values (v_user1, array['https://example.com/tomato1.jpg'], array['mno345hash5'], 'Solanum lycopersicum', 0.91, 'Solanum lycopersicum', array['Tomato','Garden Tomato'], 'Solanaceae', 'Solanum', array['fruit'], '{"results":[{"score":0.91,"species":{"scientificNameWithoutAuthor":"Solanum lycopersicum","commonNames":["Tomato"],"family":{"scientificNameWithoutAuthor":"Solanaceae"},"genus":{"scientificNameWithoutAuthor":"Solanum"}}}]}'::jsonb)
    returning id into id5;

    -- Favorites
    insert into public.favorites (user_id, identification_id, notes)
    values (v_user1, id1, 'Beautiful rose in the garden'), (v_user1, id3, 'Lavender from the farmers market'), (v_user1, id5, 'My tomato plant')
    on conflict do nothing;

    raise notice 'Seed inserted: admin=admin@gardenify.app/admin12345678, user1=test@gardenify.app/test12345678, user2=user2@gardenify.app/test12345678';
end $$;
