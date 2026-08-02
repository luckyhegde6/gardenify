-- Store base64-encoded thumbnails for history images
-- The serverless filesystem is ephemeral, so thumbnail files vanish between
-- cold starts. Persisting the (already compressed, ~10-20KB) thumbnails as
-- base64 text in the DB makes history images survive and keeps rows tiny.

alter table if exists public.identifications
  add column if not exists image_thumbnails text[] default '{}';

-- Existing RLS policies (select/insert/update by auth.uid()) cover the new column.
