-- Add results_json column to identifications for the app detail screen
-- The app stores full IdentificationResponse JSON here for history + detail views

alter table if exists public.identifications
  add column if not exists results_json text;

-- Update RLS to include the new column
-- (existing policies cover all columns via "select" and "insert")
