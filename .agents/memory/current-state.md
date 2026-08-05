# Memory — Current State

> **Branch:** `main` (auth-guard + version-source already merged via PR #36; v1.1.0 release in progress)

## ✅ DONE — Remove SQLite Entirely → Supabase-Only Backend (2026-08-03)

**Refactor complete and verified end-to-end.** No SQLite anywhere in runtime paths; all importers write to Supabase; `local_identify` hits Supabase; OpenCV best practices applied.

- **Why (root cause)**: `api/data/gardenify.db` was in `.vercelignore` so SQLite never shipped on Vercel → `local_identify` always failed there. Supabase `species` had 10,008 rows but 0 image hashes.
- **What changed**: deleted `api/services/local_db.py`, `api/data/schema.sql`, `api/data/gardenify.db`; rewrote all importers to Supabase via shared `seed_supabase_gbif.seed_supabase_gbif_from_list()`; added `supabase_species.find_by_phash()`/`insert_image_hash()`/`get_species_images()`/real `get_hash_count()`/`get_species_id_map()`; `local_identify.py` → Supabase only; identify/species/main gate on `supabase_species.is_available()`.
- **Tests**: rewritten with `FakeSupabaseClient` (in-memory, monkeypatched `_get_client`) — **91 Python tests pass**, ruff clean, tsc clean.
- **OpenCV**: `image_processor.py` now GaussianBlurs before Canny, detects blur via variance-of-Laplacian (`BLUR_THRESHOLD=100.0`), adds HSV green-pixel ratio; `OpenCVResult` schema gained `sharpness`/`is_blurry`/`green_ratio`.
- **Migration `008_image_hashes_table.sql`**: written but **NOT yet applied to prod** — prod identify currently logs a graceful PostgREST 404 for `/rest/v1/image_hashes` (handled).
- **Hashes**: 1,960 old SQLite hashes were regenerable via `scripts/build_hash_index.py` → Supabase; `total_hashes` currently 0.
- **Known limitations**: local Supabase still won't start (Docker Desktop Linux engine missing); backend verified against prod Supabase instead. Migration 008 + hash seed pending for prod.

## ✅ DONE — Phase 1 (Foundation)

- [x] All agent docs
- [x] Backend: FastAPI `/api/identify`, `/api/health`, `/api/debug`, `/api/species`
- [x] PlantNet: species + disease detection
- [x] Plant care: watering, sunlight, soil, temperature, growth, propagation
- [x] Caching: SHA-256 hash → 1hr in-memory cache
- [x] Local plant database (SQLite, 20 seed species) → **replaced by Supabase**
- [x] Offline fallback: perceptual hash matching (dHash + pHash)
- [x] Supabase migrations with RLS on all tables
- [x] CI/CD: GitHub Actions (lint, test, build, deploy)
- [x] **Mobile UI**: Auth (login/register), 4-tab nav, camera/gallery scan, results detail, history list, profile

## ✅ DONE — Phase 2 (Enhanced Experience)

- [x] Disease detection UI on results screen
- [x] Favorites system (save/unfavorite, favorites list, remove)
- [x] Species detail screen (taxonomy + Wikipedia/GBIF links)
- [x] Share results (text via react-native Share, image via expo-sharing)
- [x] Multi-language settings hook (en/fr/es)
- [x] Image cropping (allowsEditing: true)
- [x] Result caching (AsyncStorage with 24h TTL)

## ✅ DONE — Testing Infrastructure

- [x] Jest config (jest-expo preset, moduleNameMapper for @/ + AsyncStorage)
- [x] 6 test files: theme (8), cache (8), api-client (7), button (6), loading (4), plant-card (6)
- [x] 41 frontend tests passing
- [x] 95 Python tests passing
- [x] TypeScript clean (0 errors)
- [x] Lint clean (0 errors)

## ✅ DONE — Backend API Enhancements

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
- [x] **PlantNet integration verified** — rose → _Rosa lucieae_ (10 results)
- [x] **Skip-gate fixed** — PlantNet called when local DB has no matches
- [x] **Server restart workflow** — `Popen(CREATE_NEW_CONSOLE)` for detached process

## ✅ DONE — Production Deployment

- [x] Vercel production deployment — bundle 268MB, `use_remote=true` live
- [x] Dev deps stripped from requirements.txt
- [x] EAS Secrets configured (Supabase creds not in git)
- [x] Android APK built (production profile)
- [x] Release automation — tag push → EAS build → APK auto-attached to GitHub Release
- [x] **BUG-007 fixed** — `src/app/index.tsx` template placeholder overrode the real app
- [x] **Branded app icon** — leaf/sprout on blue→green gradient
- [x] **Deploy flow redesigned** — backend deploys via `deploy-backend` job in `release.yml` after `create-release`
- [x] **Vercel ENOENT deploy bug fixed** — direct `vercel deploy --prod` (server-side build)
- [x] **`.vercelignore` corrected** — only excludes untracked/generated files
- [x] **Vercel CLI pinned** — `vercel@58.4.4`
- [x] **v0.1.5 released & verified** — APK → GitHub Release → `deploy-backend` to prod
- [x] **Read-only FS 500 fixed** — `ImageProcessor` resolves writable upload dir (temp fallback)
- [x] **Prod seed users synced** — `admin@`, `test@`, `user2@` created via Auth Admin API
- [x] **Deploy size fixed (611MB → 268MB)** — 412MB GBIF zip removed from repo
- [x] **GBIF → Supabase seed** — idempotent, merge-preserve; ran against prod (10,000 updated)
- [x] **History thumbnails in DB** — migration `006_thumbnail_data.sql` APPLIED to prod
- [x] **Seed data-loss bug fixed** — jsonb fields as lists + merge-preserve on upsert

## ✅ DONE — Auth Navigation + Version Source (2026-08-06)

- [x] **Auth navigation guard** in `src/app/_layout.tsx` — sign-out → Login; login → Home in-app (verified on emulator, build `e4cd16d5`); PR #36 merged
- [x] **Single version source** — `settings.app_version = "1.1.0"`; Profile footer reads `app.json`
- [x] **v1.1.0 re-cut** — tag moved to main HEAD, release.yml running (EAS build `2d8eeb92`)

## Not Done

- [ ] 🔴 Finish v1.1.0 release (EAS build → GitHub Release → Vercel deploy) + verify `/api/health` reports 1.1.0
- [ ] 🟡 Supabase redirect allowlist `gardenify://reset-password` (config, not code)
- [ ] 🟡 Seed prod `image_hashes` (apply migration 008 + run hash seed, ~20-30 min)
- [ ] 🟡 Recheck PlantNet 404/401 identify failure (stale from prior session)
- [ ] 🟡 Fix Supabase prod auth config — email confirmation links point to `localhost:3000`
- [ ] 🟡 Re-test v0.1.5 APK on emulator against prod
- [ ] v0.1.5 APK re-test on physical device
- [ ] Expand hash index to remaining ~8K species (need alternative image sources)
- [ ] Push notifications (Phase 3)
- [ ] Community features (Phase 3)
