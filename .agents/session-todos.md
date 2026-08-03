# Session Todos

> Maintained throughout a session. Checked/updated before every commit.
> Rules:
>
> 1. Open a new session by copying the checklist below.
> 2. Before every commit: mark done/cancelled items, carry forward unfulfilled ones as new todos.
> 3. If an unfulfilled todo is identified as a bug, log it in BUGS.md.
> 4. Never delete history — carry items forward instead of dropping them.

## Checklist (copy at session start)

- [ ] Todos tracked in this file for the whole session
- [ ] `.agents/sessions.md` updated
- [ ] `.agents/handoff-current.md` updated
- [ ] `MEMORY.md` updated
- [ ] `LESSONS.md` updated (if new discovery)
- [ ] `BUGS.md` updated (if bug found/fixed)
- [ ] `PRD.md` updated (if feature completed)
- [ ] Unfulfilled todos carried forward to next session
- [ ] Any unfulfilled todo identified as a bug added to BUGS.md

---

## 2026-08-01 Session — Backend Deploy Fix + Release Flow

- [x] Fix expired `VERCEL_TOKEN` env secret (#10 PR)
- [x] Add `uv` install for `vercel build` (#10)
- [x] Root-cause `lstat ENOENT` deploy failures
- [x] Correct `.vercelignore` to exclude only untracked files (#13)
- [x] Move backend deploy into release flow after `create-release` (#14)
- [x] Restore Vercel `commandForIgnoringBuildStep` for production
- [x] Update docs (sessions, handoff, MEMORY, LESSONS, BUGS)
- [x] Set up session-todo workflow + rules
- [x] Commit docs update

### Carried Forward (next session)

- [x] Cut v0.1.5 tag → release flow end-to-end verified (APK → Release → deploy-backend to prod)
- [x] Verify `https://sasyakashi.vercel.app/api/health` returns ok after first release
- [x] Confirm species detail endpoint returns `images` key (fix live on prod)
- [ ] Real-device re-test of `gardenify-v0.1.5.apk`
- [ ] Fix Supabase prod auth config (Site URL / redirect URLs → production app, not localhost)
- [ ] Investigate "verified but cannot login" (missing `public.users` profile rows for Auth users)
- [ ] Re-test v0.1.5 APK on emulator against prod (login + identify flow)
- [ ] Expand hash index to remaining ~8K species
- [ ] Push notifications (Phase 3)

## 2026-08-02 Session — Identify 500 Fix + Release Notes

- [x] Fix `/api/identify` read-only FS 500 (PR #16) — temp-dir fallback + best-effort writes
- [x] Add 4 tests (`api/tests/test_image_processor.py`); 77 passed, ruff/tsc clean
- [x] PR #17: release-notes body template placeholders
- [x] Merge both PRs; verified prod auto-deploy (build `gardenify-7h7o4wo4x` Ready, aliased)
- [x] Verify prod `/api/identify` returns 400 (plant validation) not read-only FS 500
- [x] File & close issue #18 (read-only FS bug)
- [x] Update docs (handoff, sessions)

## 2026-08-02 Session — Deploy Size Fix + Thumbnail Persistence + GBIF Seed

- [x] Root-cause 611MB Vercel bundle: `api/data/gbif/plantnet_observations.zip` (412MB) shipped despite `.vercelignore`
- [x] Move zip out of repo → `C:\Users\lucky\AppData\Local\Temp\opencode\plantnet_observations.zip`
- [x] `.vercelignore`: exclude `api/data/gardenify.db-journal`, `api/data/uploads/`, `api/data/plantnet-300k/`, `api/data/hashes/`, `api/data/geoplant/`, `**/__pycache__/`
- [x] Preview deploy verified: upload 344MB → 82.1KB, bundle 611MB → 268MB
- [x] GBIF → Supabase seed: `api/data/importers/seed_supabase_gbif.py` + `.github/workflows/seed-gbif.yml`
- [x] History images persisted in DB: `image_thumbnails text[]` column (migration `006_thumbnail_data.sql`)
- [x] `image_processor.py` emits `thumbnail_data_url`; identify/history wired end-to-end
- [x] Tests: 86 passed, ruff clean, tsc clean, lint clean
- [x] Push migration `006_thumbnail_data.sql` to prod Supabase (image_thumbnails column live)
- [x] Run `seed_supabase_gbif` against prod — completed (0 inserted, 10,000 updated)
- [x] **BUG found & fixed**: seed sent jsonb fields as `json.dumps` strings + blind upsert wiped 10,008 enriched `common_names` rows → restored from local SQLite, seed now `_to_list()` + merge-preserve; LESSONS.md logged; 86 tests pass
- [ ] Deploy fixed bundle to production + verify `/api/health`
- [ ] Recheck PlantNet 404/401 identify failure (stale from prior session)

### Carried Forward (from 2026-08-01)

- [ ] Real-device re-test of `gardenify-v0.1.5.apk`
- [ ] Fix Supabase prod auth config (Site URL / redirect URLs → production app, not localhost)
- [ ] Investigate "verified but cannot login" (missing `public.users` profile rows for Auth users)
- [ ] Re-test v0.1.5 APK on emulator against prod (login + identify flow)
- [ ] Expand hash index to remaining ~8K species
- [ ] Push notifications (Phase 3)

---

## 2026-08-02 Session — Remove SQLite Entirely → Supabase-Only Backend + OpenCV Best Practices

> **User decisions (clarified before starting):**
>
> 1. Remove SQLite **entirely** (delete `local_db.py`, `schema.sql`, `gardenify.db`; rewrite all importers to write to Supabase).
> 2. Research OpenCV image-identification best practices → **apply improvements to `image_processor.py` + document** in LESSONS.md.
> 3. `local_identify` must hit **Supabase** (works on Vercel + local Supabase), not SQLite.
> 4. Local dev uses **local Supabase** (`http://127.0.0.1:54321`) per `.env.local` — no SQLite fallback anywhere.

### Root cause recap (why this refactor)

- Vercel: `api/data/gardenify.db` is in `.vercelignore` so it never ships; `local_db.py` `sqlite3.connect()` fails → "Local identification failed: unable to open database file" (harmless log noise, but local identify never works on Vercel).
- Supabase `species` table has 10,008 rows but **no image hashes** (`get_hash_count()` returns 0 in `supabase_species.py`).
- Local SQLite `gardenify.db` holds 10,008 species + **1,960 `image_hashes`** (phash+dhash, `{species_id}\img.jpg` paths, 1 hash per species id). Species ids are `BIGSERIAL` in Supabase vs autoincrement in SQLite → **must map by `scientific_name`, not id**.

### Refactor checklist

- [x] **Step 1 — Migration `008_image_hashes_table.sql`**: create `image_hashes` table (species_id FK → species.id, image_path, phash, dhash, category, created_at) + indexes + RLS (public SELECT, service-role INSERT/UPDATE). Follow `002_species_table.sql` pattern.
- [x] **Step 2 — Hash seed to Supabase (REGENERATE, not migrate)**: rewritten `scripts/build_hash_index.py` → Supabase (`get_species_id_map()` + `insert_image_hash`). Not yet run against prod (~20-30 min, `total_hashes` currently 0).
- [x] **Step 3 — `supabase_species.py`**: added `find_by_phash()`, `insert_image_hash()`, `get_species_images()`, real `get_hash_count()`, `get_species_id_map()`; kept `search_species`/`get_species_by_id`/`get_species_by_name`.
- [x] **Step 4 — `local_identify.py`**: rewritten to call Supabase `find_by_phash` only (no `local_db` imports).
- [x] **Step 5 — `identify.py`**: gate on `supabase_species.is_available()` instead of `local_db.is_available()`.
- [x] **Step 6 — `species.py`**: dropped `_get_backend()` SQLite fallback → Supabase only.
- [x] **Step 7 — `main.py`**: removed `local_db.init_db()` + `seed_database()` startup block.
- [x] **Step 8 — Delete SQLite**: deleted `api/services/local_db.py`, `api/data/schema.sql`, `api/data/gardenify.db`; removed sqlite refs from `.vercelignore`.
- [x] **Step 9 — Rewrite importers to Supabase**: `seed_species.py`, `import_gbif.py`, `import_plantnet300k.py`, `build_hash_index.py` (importers + scripts/), `run_all.py`. Shared pattern: `seed_supabase_gbif.seed_supabase_gbif_from_list()` (batch upsert, `_to_list()` jsonb, merge-preserve).
- [x] **Step 10 — Rewrite tests**: `conftest.py` `FakeSupabaseClient` + `patched_supabase` fixture (no live Supabase needed); `test_species_routes.py`, `test_identify_offline.py`, `test_gbif_import.py`, `test_local_db.py` (→ Supabase data-layer tests, 21 tests) rewritten.
- [x] **Step 11 — OpenCV research + apply**: `image_processor.py` now GaussianBlur→Canny, variance-of-Laplacian blur detection (`BLUR_THRESHOLD=100.0`), HSV green-pixel ratio; `OpenCVResult` gained `sharpness`/`is_blurry`/`green_ratio`; 4 new tests in `test_image_processor.py`.
- [x] **Step 12 — Docs**: LESSONS.md (SQLite→Supabase + OpenCV), AGENTS.md/MEMORY.md/BUGS.md/handoff updated.
- [x] **Step 13 — Verify**: `npx tsc --noEmit` clean + `cd api && ruff check .` clean + `cd api && pytest` **91 passed**. Backend live-verified + emulator E2E (Monstera 81.7%).
- [ ] **Step 14 — Migrate prod hashes**: apply migration 008 + run hash seed against prod Supabase (deferred — requires 20-30 min run).
- [ ] **Step 15 — Verify on Vercel**: POST valid image → 200 with `source: "local"` when phash matches; no "Local identification failed" warning.

### Current progress (as of writing)

- [x] Investigated all files referencing `local_db`/`local_identify` (routes, importers, tests, main, scripts).
- [x] Confirmed SQLite data: 10,008 species, 1,960 image_hashes (phash hex strings like `c54949e4b6f389d0`).
- [x] Confirmed Supabase `species` schema (migration 002) + RLS pattern + jsonb fields.
- [x] **Implementation COMPLETE** — refactor done, tests green (91), backend + emulator verified.
- [ ] Migration 008 + hash seed to prod (deferred, ~20-30 min).

### Environment facts

- Local Supabase: `http://127.0.0.1:54321` (currently DOWN — run `npx supabase start` to use local, or `USE_REMOTE=true` for prod).
- Prod Supabase: project `amyriuhwqyalodsfkwzf`, URL `https://amyriuhwqyalodsfkwzf.supabase.co`. Management API token lives in the gitignored `C:\Users\lucky\AppData\Local\Temp\opencode\creds.json` — never commit tokens to tracked files.
- `.env.local`: has both local keys (top) AND prod keys (bottom, remote block) — `SUPABASE_SERVICE_ROLE_KEY` at line 8 is the LOCAL one, line 37 is PROD. Careful when seeding prod.
