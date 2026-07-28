-- Gardenify Database Schema
-- Supabase PostgreSQL migrations

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- ============================================================
-- TABLES
-- ============================================================

-- Users table (extends Supabase Auth)
create table if not exists public.users (
    id uuid primary key references auth.users(id) on delete cascade,
    email text unique not null,
    full_name text,
    avatar_url text,
    subscription_tier text default 'free' check (subscription_tier in ('free', 'pro', 'premium')),
    identifications_used_today int default 0,
    last_identification_date date default current_date,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Plant identifications
create table if not exists public.identifications (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references public.users(id) on delete cascade not null,
    image_urls text[] not null default '{}',
    image_hashes text[] not null default '{}',
    best_match text not null,
    score float not null check (score >= 0.0 and score <= 1.0),
    species_scientific_name text not null,
    species_common_names text[] default '{}',
    species_family text,
    species_genus text,
    organs text[] default '{}',
    raw_plantnet_response jsonb,
    created_at timestamptz default now()
);

-- User favorites/bookmarks
create table if not exists public.favorites (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references public.users(id) on delete cascade not null,
    identification_id uuid references public.identifications(id) on delete cascade not null,
    notes text,
    created_at timestamptz default now(),
    unique(user_id, identification_id)
);

-- App settings per user
create table if not exists public.user_settings (
    user_id uuid primary key references public.users(id) on delete cascade,
    language text default 'en',
    notifications_enabled boolean default true,
    auto_save_to_history boolean default true,
    preferred_organ text default 'auto' check (preferred_organ in ('leaf', 'flower', 'fruit', 'bark', 'auto')),
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- ============================================================
-- INDEXES
-- ============================================================

create index if not exists idx_identifications_user_id on public.identifications(user_id);
create index if not exists idx_identifications_created_at on public.identifications(created_at desc);
create index if not exists idx_identifications_best_match on public.identifications(best_match);
create index if not exists idx_favorites_user_id on public.favorites(user_id);

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

alter table public.users enable row level security;
alter table public.identifications enable row level security;
alter table public.favorites enable row level security;
alter table public.user_settings enable row level security;

-- Users: Users can only read/update their own data
create policy "Users can view own profile"
    on public.users for select
    using (auth.uid() = id);

create policy "Users can update own profile"
    on public.users for update
    using (auth.uid() = id);

create policy "Users can insert own profile"
    on public.users for insert
    with check (auth.uid() = id);

-- Identifications: Users can only access their own
create policy "Users can view own identifications"
    on public.identifications for select
    using (auth.uid() = user_id);

create policy "Users can create own identifications"
    on public.identifications for insert
    with check (auth.uid() = user_id);

create policy "Users can delete own identifications"
    on public.identifications for delete
    using (auth.uid() = user_id);

-- Favorites: Users can only access their own
create policy "Users can view own favorites"
    on public.favorites for select
    using (auth.uid() = user_id);

create policy "Users can create own favorites"
    on public.favorites for insert
    with check (auth.uid() = user_id);

create policy "Users can delete own favorites"
    on public.favorites for delete
    using (auth.uid() = user_id);

-- User Settings: Users can only access their own
create policy "Users can view own settings"
    on public.user_settings for select
    using (auth.uid() = user_id);

create policy "Users can update own settings"
    on public.user_settings for update
    using (auth.uid() = user_id);

create policy "Users can insert own settings"
    on public.user_settings for insert
    with check (auth.uid() = user_id);

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
create or replace trigger on_auth_user_created
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

create or replace trigger users_updated_at
    before update on public.users
    for each row execute function public.update_updated_at();

create or replace trigger user_settings_updated_at
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
