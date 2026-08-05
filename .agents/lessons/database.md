# Lessons — Database (Supabase, SQLite, Migrations, RLS, Seeds)

## 2026-08-02: SQLite Files Don't Ship to Vercel — Use Supabase as the Only Local-Identify Backend

**Context:** `/api/identify` on Vercel logged `Local identification failed: unable to open database file`. The "local" identification step (perceptual-hash matching against SQLite) silently no-ops in production.

**Issue:** `api/data/gardenify.db` is excluded from the Vercel bundle via `.vercelignore`, and Vercel's filesystem is read-only (only `/tmp` writable) so WAL-mode SQLite can't work there anyway. Any code path that unconditionally `sqlite3.connect()`s the DB fails on serverless. Supabase was already the production species store (10,008 rows) but had **zero image hashes**, so `local_identify` had no Supabase equivalent.

**Decision (user):** Remove SQLite **entirely** — `local_identify` must hit Supabase, all importers write to Supabase, `gardenify.db`/`local_db.py`/`schema.sql` deleted.

**Pattern:**

1. Treat any project-relative data file as non-shippable on serverless — if you can't write it and it's git-ignored, it doesn't exist in prod. Data must live in a database.
2. When migrating SQLite → Supabase, ids won't match (autoincrement vs BIGSERIAL) — join on the natural key (`scientific_name`).
3. Supabase `find_by_phash` = fetch all hashes + compute Hamming distance in Python (SQLite/PG bitwise XOR isn't portable; 2K rows is fast).
4. Gate local-identify on `supabase_species.is_available()`, not `local_db.is_available()`.

## 2026-08-02: jsonb Columns Reject json.dumps Strings — and Bulk Upsert Can Wipe Enriched Data

**Issue:** Two compounding bugs:

1. `species` stores `common_names`/`native_regions` as **jsonb**, but the seed sent `json.dumps([...])` — a JSON _string_ (`"[]"`). `_row_to_dict` returned `'[]'` (string), failing `isinstance(..., list)` checks.
2. The seed used `upsert(on_conflict="scientific_name")`, which **overwrites every column** — the GBIF archive has no common names, so all 10,008 enriched prod rows were clobbered to empty arrays.

**Fix:**

1. Send jsonb fields as real Python lists (`_to_list()`), never `json.dumps` strings.
2. During upsert, fetch existing `common_names`/`native_regions` and preserve non-empty values.
3. Beware `list("[]")` — it splits into `['[', ']']` (truthy), defeating the "empty" guard. Use a `json.loads`-based normalizer.

**Pattern:** For jsonb columns, treat JSON strings as data loss. When a bulk upsert can overwrite richer rows with sparse seed data, merge-on-conflict (preserve non-empty fields) instead of blind upsert. After any destructive seed run, verify `jsonb_typeof(col)='array'` and sample enriched rows.

## 2026-08-04: Prod Admin Locked Out Because Seed `is_admin` Never Applied

**Context:** Admin account showed "Access Denied" and backend returned `403 Admin access required` even with a valid JWT.

**Root cause:** The admin gate reads `public.users.is_admin`. On prod, the account was created through the admin API, so the `seed.sql` step that sets `is_admin = true` **never executed** — the row defaulted to `false`.

**Also:** Seed passwords don't carry to prod-created accounts — an account that is confirmed and not banned but still fails login usually has an **unknown password**, not an account problem.

**Pattern:**

1. When an account's capabilities depend on a data row (not code), verify the **row state on prod** — seeds/migrations only matter if they ran. `SELECT is_admin` is the first diagnostic, not the code.
2. Two separate gates (backend service-role + mobile RLS own-row read) both keyed on the same column is correct defense-in-depth — fix the **data**, not the code.
3. Fix data via service-role `PATCH` (bypasses RLS); confirm with a non-admin token returning `403` to prove least-privilege still holds.

## 2026-07-31: `supabase db push` Fails on Multi-Statement SQL — Apply Migrations Manually

**Issue:** `supabase db push` fails on SQL with multiple statements.

**Fix:** Apply manually per statement: `supabase db query "<sql>"` for single-line statements; for full migration files use a Python script with `psycopg2` to execute the entire file.

**Pattern:** Always have a manual apply strategy. Verify each migration via `_migrations` table or a query.

## SQLite Doesn't Support XOR — Use Python for Bitwise Operations

**Issue:** `find_by_phash()` used SQL `XOR` — `sqlite3.OperationalError: near "XOR": syntax error`.

**Fix:** Fetch all hashes from DB, compute Hamming distance in Python, filter/sort in Python.

**Pattern:** SQLite is minimal — no bitwise XOR, no CONV(). For complex comparisons, fetch and compute in Python. Fast enough for <100K rows.

## Test Expectations Must Match Business Logic

**Issue:** Test expected `observation_count == 100` after inserting with count 100; actual behavior is `42 + 100 = 142` (additive upsert).

**Pattern:** Write tests that verify actual behavior, not desired behavior. If behavior is additive, test that it adds.

## Darwin Core Archives Use Tab-Separated Text, Not CSV

**Issue:** Importer assumed `.csv` with `csv.DictReader`. Archive contains `.txt` files with tab-separated values; `scientificName` column contains author names (`"Quercus robur L."`).

**Fix:**

1. Read `.txt` with `split("\t")` instead of CSV reader.
2. Strip author names from scientific names (keep first 2 words).
3. Use `scientificName` column at index 15.

**Pattern:** Darwin Core Archives vary by dataset. Always inspect archive contents before writing importers.

## RLS: Missing Policies on Database Tables (anti-pattern)

**Context:** Created migrations without RLS policies.

**Fix:**

1. Always add RLS in the same migration as table creation: `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` + `CREATE POLICY`.
2. Use pattern: `CREATE POLICY "Users see own X" ON X FOR SELECT USING (auth.uid() = user_id)`.
3. Review checklist: "Does every table have RLS?"
4. Use `supabase db reset` to test locally.

**Pattern:** Security is not optional. Every table needs RLS. Every policy needs testing.
