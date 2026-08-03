-- Gardenify Fix: Recreate missing RLS INSERT policies + profile trigger
-- Production was missing the objects from 001 (insert/delete policies, handle_new_user
-- trigger, updated_at triggers, reset_daily_quota). Idempotent so it is safe to re-run.

-- ============================================================
-- FUNCTIONS
-- ============================================================

-- Auto-create user profile on signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
    insert into public.users (id, email, full_name, avatar_url)
    values (
        new.id,
        new.email,
        coalesce(new.raw_user_meta_data->>'full_name', ''),
        coalesce(new.raw_user_meta_data->>'avatar_url', '')
    );

    insert into public.user_settings (user_id)
    values (new.id);

    return new;
end;
$$ language plpgsql security definer;

-- Trigger for auto-creating user profile
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user();

-- Update updated_at timestamp
create or replace function public.update_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists users_updated_at on public.users;
create trigger users_updated_at
    before update on public.users
    for each row execute function public.update_updated_at();

drop trigger if exists user_settings_updated_at on public.user_settings;
create trigger user_settings_updated_at
    before update on public.user_settings
    for each row execute function public.update_updated_at();

-- Daily quota reset function
create or replace function public.reset_daily_quota()
returns void as $$
begin
    update public.users
    set identifications_used_today = 0,
        last_identification_date = current_date
    where last_identification_date < current_date;
end;
$$ language plpgsql security definer;

-- ============================================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================================

-- Users: allow inserting own profile
drop policy if exists "Users can insert own profile" on public.users;
create policy "Users can insert own profile"
    on public.users for insert
    with check (auth.uid() = id);

-- Identifications: user-scoped select/insert/delete
drop policy if exists "Users can view own identifications" on public.identifications;
create policy "Users can view own identifications"
    on public.identifications for select
    using (auth.uid() = user_id);

drop policy if exists "Users can create own identifications" on public.identifications;
create policy "Users can create own identifications"
    on public.identifications for insert
    with check (auth.uid() = user_id);

drop policy if exists "Users can delete own identifications" on public.identifications;
create policy "Users can delete own identifications"
    on public.identifications for delete
    using (auth.uid() = user_id);

-- Favorites: user-scoped select/insert/delete
drop policy if exists "Users can view own favorites" on public.favorites;
create policy "Users can view own favorites"
    on public.favorites for select
    using (auth.uid() = user_id);

drop policy if exists "Users can create own favorites" on public.favorites;
create policy "Users can create own favorites"
    on public.favorites for insert
    with check (auth.uid() = user_id);

drop policy if exists "Users can delete own favorites" on public.favorites;
create policy "Users can delete own favorites"
    on public.favorites for delete
    using (auth.uid() = user_id);

-- User Settings: user-scoped select/update/insert
drop policy if exists "Users can view own settings" on public.user_settings;
create policy "Users can view own settings"
    on public.user_settings for select
    using (auth.uid() = user_id);

drop policy if exists "Users can update own settings" on public.user_settings;
create policy "Users can update own settings"
    on public.user_settings for update
    using (auth.uid() = user_id);

drop policy if exists "Users can insert own settings" on public.user_settings;
create policy "Users can insert own settings"
    on public.user_settings for insert
    with check (auth.uid() = user_id);
