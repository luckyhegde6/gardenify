-- Add admin role support
alter table public.users
add column if not exists is_admin boolean default false;

-- Grant role-level access to tables (RLS policies handle row-level filtering)
grant usage on schema public to anon, authenticated, service_role;
grant all on all tables in schema public to anon, authenticated, service_role;
grant all on all sequences in schema public to anon, authenticated, service_role;

-- Security definer function to check admin status (bypasses RLS)
create or replace function public.is_admin(uid uuid)
returns boolean
language sql
security definer
stable
as $$
    select coalesce(
        (select is_admin from public.users where id = uid),
        false
    );
$$;

-- Admin can view any user's profile (for admin panel)
create policy "Admins can view all profiles"
    on public.users for select
    using (
        public.is_admin(auth.uid())
        or auth.uid() = id
    );

-- Admin can update any user's profile
create policy "Admins can update all profiles"
    on public.users for update
    using (
        public.is_admin(auth.uid())
    );

-- Admin can view any identification
create policy "Admins can view all identifications"
    on public.identifications for select
    using (
        public.is_admin(auth.uid())
        or auth.uid() = user_id
    );

-- Admin can view any favorite
create policy "Admins can view all favorites"
    on public.favorites for select
    using (
        public.is_admin(auth.uid())
        or auth.uid() = user_id
    );
