# MEMORY.md — Quick Context for Agents

> **Read this FIRST.** Saves ~60% context vs reading AGENTS.md + architecture.md.

## Project Identity

**Gardenify** — Plant identification mobile app. Photo → species + disease + care instructions.

| Key              | Value                                                                                       |
| ---------------- | ------------------------------------------------------------------------------------------- |
| Repo             | `https://github.com/luckyhegde6/gardenify`                                                  |
| EAS Project ID   | `b17c6958-f3e7-4ec1-afcf-3b241fcbcda0`                                                      |
| Platform         | Android-first, iOS later                                                                    |
| Backend          | Python FastAPI on Vercel                                                                    |
| Database         | Supabase (PostgreSQL + Auth + Storage)                                                      |
| Plant AI         | PlantNet API v2 (free 500/day)                                                              |
| Current Branch   | `feat/branded-404-favicon-sitemap` (PR #20)                                                 |
| Backend (prod)   | `https://sasyakashi.vercel.app`                                                             |
| Vercel env       | `USE_REMOTE=true`, PlantNet API key, Supabase URL/anon key                                  |
| Vercel bundle    | 268MB (fixed from 611MB — 412MB GBIF zip + dev data excluded via `.vercelignore`)           |
| EAS Build        | Production APK built, env vars from `eas secret:create` (not in git)                        |
| APK Distribution | [GitHub Releases](https://github.com/luckyhegde6/gardenify/releases) (latest v0.1.5)        |
| EAS Builds       | https://expo.dev/accounts/luckyhegdedev/projects/gardenify/builds                           |
| Local DB size    | 10,008 species, 1,960 with perceptual hashes (19.6%)                                        |
| Backend Pipeline | OpenCV gate → local DB pHash → PlantNet (quota saver)                                       |
| Tests            | 86 Python + 21 Playwright + 41 Jest = 148 total                                             |
| PlantNet status  | Fixed: no `lang` param, urllib-based, verified working                                      |
| Server restart   | Use `Popen(CREATE_NEW_CONSOLE=0x00000010)` on Windows                                       |
| Supabase prod    | Project `amyriuhwqyalodsfkwzf` linked, 6 migrations applied (006 thumbnail live)            |
| Prod species     | 10,008 GBIF species, jsonb common_names/native_regions; seed is idempotent + merge-preserve |
| History images   | Persisted as base64 thumbnails in `identifications.image_thumbnails` (migration 006)        |
| Vercel FS        | `/var/task` read-only; only `/tmp` writable — upload dir falls back to temp                 |

## Architecture (10 seconds)

```
Expo App → FastAPI Backend → PlantNet API
    ↓              ↓
 Supabase      Supabase
(auth/db)     (storage)
```

## Current State

### ✅ DONE — Remove SQLite Entirely → Supabase-Only Backend (2026-08-03)

**Refactor complete and verified end-to-end.** No SQLite anywhere in runtime paths; all importers write to Supabase; `local_identify` hits Supabase; OpenCV best practices applied.

- **Why (root cause)**: `api/data/gardenify.db` was in `.vercelignore` so SQLite never shipped on Vercel → `local_identify` always failed there. Supabase `species` had 10,008 rows but 0 image hashes.
- **What changed**: deleted `api/services/local_db.py`, `api/data/schema.sql`, `api/data/gardenify.db`; rewrote all importers (`seed_species.py`, `import_gbif.py`, `import_plantnet300k.py`, `build_hash_index.py`, `run_all.py`) to write to Supabase via shared `seed_supabase_gbif.seed_supabase_gbif_from_list()`; added `supabase_species.find_by_phash()`/`insert_image_hash()`/`get_species_images()`/real `get_hash_count()`/`get_species_id_map()`; `local_identify.py` → Supabase only; identify/species/main gates on `supabase_species.is_available()`.
- **Tests**: rewritten with `FakeSupabaseClient` (in-memory, monkeypatched `_get_client`) — **91 Python tests pass**, ruff clean, tsc clean.
- **OpenCV**: `image_processor.py` now GaussianBlurs before Canny, detects blur via variance-of-Laplacian (`BLUR_THRESHOLD=100.0`), adds HSV green-pixel ratio; `OpenCVResult` schema gained `sharpness`/`is_blurry`/`green_ratio`. Verified live: flat green → `is_blurry:true`, structured → `sharpness:370`.
- **Migration `008_image_hashes_table.sql`**: `image_hashes` table (FK→species, phash/dhash/category, RLS) written but **NOT yet applied to prod** — prod identify currently logs a graceful PostgREST 404 for `/rest/v1/image_hashes` (handled).
- **Hashes**: 1,960 old SQLite hashes were regenerable (archive at `C:\Users\lucky\AppData\Local\Temp\opencode\plantnet_observations.zip`) via `scripts/build_hash_index.py` → Supabase; `total_hashes` currently 0.
- **Emulator verification**: local backend on `:8000` (prod Supabase) + installed `com.gardenify.app` APK on emulator-5554 → login via prod auth (new `devtest@gardenify.app` auto-confirmed user created via service-role admin API) → gallery pick → identify → **Monstera deliciosa 81.7%** rendered with taxonomy + care.
- **Known limitations**: local Supabase still won't start (Docker Desktop Linux engine missing); backend verified against prod Supabase instead. Migration 008 + hash seed pending for prod.
- **Resume point**: `.agents/handoff-current.md` → "Active Task" (apply migration 008 + seed hashes to prod).

### Done — Phase 1 (Foundation)

- [x] All agent docs
- [x] Backend: FastAPI `/api/identify`, `/api/health`, `/api/debug`, `/api/species`
- [x] PlantNet: species + disease detection
- [x] Plant care: watering, sunlight, soil, temperature, growth, propagation
- [x] Caching: SHA-256 hash → 1hr in-memory cache
- [x] Local plant database (SQLite, 20 seed species)
- [x] Offline fallback: perceptual hash matching (dHash + pHash)
- [x] Supabase migrations with RLS on all tables
- [x] CI/CD: GitHub Actions (lint, test, build, deploy)
- [x] All docs, seed scripts, dev environment, OpenCode + ECC integration
- [x] **Mobile UI**: Auth (login/register), 4-tab nav (Scan/Saved/History/Profile), camera/gallery scan, results detail, history list, profile

### Done — Phase 2 (Enhanced Experience)

- [x] Disease detection UI on results screen
- [x] Favorites system (save/unfavorite, favorites list, remove)
- [x] Species detail screen (taxonomy + Wikipedia/GBIF links)
- [x] Share results (text share via react-native Share, image via expo-sharing)
- [x] Multi-language settings hook (en/fr/es)
- [x] Image cropping (allowsEditing: true)
- [x] Result caching (AsyncStorage with 24h TTL)

### Done — Testing Infrastructure

- [x] Jest config (jest-expo preset, moduleNameMapper for @/ + AsyncStorage)
- [x] 6 test files: theme (8), cache (8), api-client (7), button (6), loading (4), plant-card (6)
- [x] 41 frontend tests passing
- [x] 73 Python tests passing
- [x] TypeScript clean (0 errors)
- [x] Lint clean (0 errors, 1 pre-existing warning)

### Done — Backend API Enhancements

- [x] OpenCV image validation (edge detection + color analysis + content score)
- [x] Image compression, thumbnail generation, server-side storage
- [x] Identify flow: OpenCV gate → local DB pHash → PlantNet as fallback
- [x] Source flag in response: `source: "local" | "plantnet"`
- [x] History endpoints (GET list + detail + thumbnail)
- [x] Synthetic test fixtures for E2E tests
- [x] Perceptual hash index: 1,960 species from GBIF (19.6% coverage)
- [x] GBIF image downloader + hash index builder script
- [x] LSP (TypeScript + Python), formatter (Prettier + Ruff), superpower plugin
- [x] 21 Playwright API tests passing
- [x] **PlantNet integration verified** — rose → _Rosa lucieae_ (10 results, quota 491)
- [x] **Skip-gate fixed** — PlantNet called when local DB has no matches
- [x] **Server restart workflow** — `Popen(CREATE_NEW_CONSOLE)` for detached process

### Production Deployment (Done)

- [x] Vercel production deployment — bundle 527MB → 267MB, `use_remote=true` live
- [x] Dev deps stripped from requirements.txt
- [x] EAS Secrets configured (Supabase creds not in git)
- [x] Android APK built (production profile)
- [x] PR #7 merged into main
- [x] Release automation — tag push → EAS build → APK auto-attached to GitHub Release
- [x] **BUG-007 fixed** — `src/app/index.tsx` template placeholder overrode the real app; replaced with auth redirect (released v0.1.4)
- [x] **Branded app icon** — leaf/sprout on blue→green gradient
- [x] **Deploy flow redesigned** — removed `deploy-backend.yml`; backend deploys via `deploy-backend` job in `release.yml` after `create-release` (tests → tag → release APK → deploy backend)
- [x] **Vercel ENOENT deploy bug fixed** — `vercel build` + `--prebuilt` created local `.vercel/python/.venv` artifacts referenced by the deploy manifest but excluded by `.vercelignore` → `lstat ENOENT`. Switched to direct `vercel deploy --prod` (server-side build)
- [x] **`.vercelignore` corrected** — only excludes untracked/generated files; previously excluded git-tracked files that Vercel's git-tree manifest syncs (deny-list and allowlist both caused ENOENT)
- [x] **Vercel CLI pinned** — `vercel@58.4.4`; project `commandForIgnoringBuildStep` skips production on git pushes (prod deploys only via release workflow)
- [x] **v0.1.5 released & verified** — APK → GitHub Release → `deploy-backend` to prod; release notes categorized
- [x] **Read-only FS 500 fixed** — `ImageProcessor` resolves writable upload dir (temp fallback on Vercel), storage writes best-effort; prod `/api/identify` returns 400 not 500 (PR #16, deployed)
- [x] **Prod seed users synced** — `admin@`, `test@`, `user2@` created via Auth Admin API (email-confirmed)
- [x] **Deploy size fixed (611MB → 268MB)** — removed 412MB GBIF zip from repo; `.vercelignore` excludes dev data dirs + `__pycache__`; preview verified (upload 82KB)
- [x] **GBIF → Supabase seed** — `api/data/importers/seed_supabase_gbif.py` + `.github/workflows/seed-gbif.yml` (dispatch + weekly cron); idempotent, preserves enriched jsonb data; ran against prod (10,000 updated)
- [x] **History thumbnails in DB** — migration `006_thumbnail_data.sql` (`image_thumbnails text[]`) APPLIED to prod; `thumbnail_data_url` flows identify → history → app
- [x] **Seed data-loss bug fixed** — jsonb fields now sent as lists + merge-preserve on upsert (was `json.dumps` strings wiping common_names); prod restored from local SQLite; LESSONS.md logged

### Not Done

- [ ] 🔴 Deploy fixed bundle to production + verify `/api/health` (after user merges PR #20)
- [ ] 🟡 Recheck PlantNet 404/401 identify failure (stale from prior session)
- [ ] 🟡 Fix Supabase prod auth config — email confirmation links point to `localhost:3000` (Site URL/redirects on `amyriuhwqyalodsfkwzf`); must point at production app
- [ ] 🟡 Investigate "verified but cannot login" — `public.users` returns `[]` for Auth users; suspected missing `handle_new_user` trigger in prod
- [ ] 🟡 Re-test v0.1.5 APK on emulator against prod (login + identify flow)
- [ ] v0.1.5 APK re-test on physical device
- [ ] Expand hash index to remaining ~8K species (need alternative image sources)
- [ ] Push notifications (Phase 3)
- [ ] Community features (Phase 3)

## Mobile App Structure

```
src/
  app/
    _layout.tsx              # Root: AuthProvider + Stack (auth/tabs conditional)
    index.tsx                # Auth-aware redirect → /(auth)/login or /(tabs)
    (auth)/
      _layout.tsx            # Auth stack
      login.tsx              # Login with email/password
      register.tsx           # Register with password validation
    (tabs)/
      _layout.tsx            # 4-tab bottom navigator
      index.tsx              # Scan: camera + gallery + organ selector
      favorites.tsx          # Favorites list
      history.tsx            # Past identifications
      profile.tsx            # User info + sign out
    identification/
      [id].tsx               # Results detail (species, disease, care, share)
    species/
      [name].tsx             # Species detail (taxonomy + external links)
  components/
    button.tsx               # 5 variants, 3 sizes
    plant-card.tsx           # Card with confidence bar
    loading.tsx              # Loading spinner + overlay
  hooks/
    use-auth.tsx             # Auth context + provider
    use-identification.ts    # Identify plant via API
    use-camera.ts            # Camera/gallery picker
    use-settings.ts          # Language/theme settings
  lib/
    supabase.ts              # Supabase client (SecureStore adapter)
    api-client.ts            # Backend API client
    types.ts                 # TypeScript types matching backend schemas
    cache.ts                 # AsyncStorage result cache (24h TTL)
    share.ts                 # Share module
  constants/
    theme.ts                 # Colors, spacing, typography, shadows
```

## Local Development

```bash
# Quick start
npm install
npx expo start

# Backend (separate terminal)
cd api
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Verify (all 4 must pass)
npx tsc --noEmit          # TypeScript (0 errors)
cd api && pytest          # Python tests (86 passing)
npx expo lint             # Lint (0 errors)
npx jest --no-cache       # Frontend tests (41 passing)
npx playwright test e2e/api-tests/ --reporter=list   # E2E (21 passing)
```

## Key Decisions

- **PlantNet** over Google Vision: free 500/day, plant-specialized
- **FastAPI** over Express: Python ecosystem, async, type safety
- **Supabase** over Firebase: RLS, PostgreSQL, open source
- **4-tab navigation**: Scan → Saved → History → Profile
- **expo-secure-store** for tokens, AsyncStorage for cache
- **Server-side API key**: never expose PlantNet key to client

## Auth Security (recent)
- Login is backend-mediated (/api/auth/login) with 3-failure lockout (15 min) ; forgot-password is one-shot per email until completed
- Admin can force-reset to default (GARDENIFY_DEFAULT_PASSWORD, default 12345678) via admin screen/API
- Recovery deep link must be allowlisted in Supabase: gardenify://reset-password

## Release v1.1.0
- App + API at 1.1.0; release/v1.1.0 PR pending merge; tag v1.1.0 triggers automated release.yml
- Backend already deployed to prod manually; auth endpoints verified live
