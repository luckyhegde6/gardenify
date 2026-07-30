-- Add push_token and theme columns to user_settings for notifications + dark mode

alter table if exists public.user_settings
  add column if not exists theme text default 'light' check (theme in ('light', 'dark'));

alter table if exists public.user_settings
  add column if not exists push_token text;
