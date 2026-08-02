# Agent Primer — Quick Start

> Read this FIRST when starting a new session. Saves ~60% context.

## 30-Second Context

**Gardenify** = Plant ID app. Photo → species + disease + care.

```
Expo App → FastAPI Backend → PlantNet API
    ↓              ↓
 Supabase      Supabase
(auth/db)     (storage)
```

## Current State (What's Done)

| Component            | Status   | Notes                                                                                                   |
| -------------------- | -------- | ------------------------------------------------------------------------------------------------------- |
| Backend API          | ✅ Done  | FastAPI, full pipeline: OpenCV gate → local DB → PlantNet                                               |
| PlantNet Integration | ✅ Done  | Species + disease detection                                                                             |
| Plant Care           | ✅ Done  | Taxonomy-based care profiles                                                                            |
| OpenCV Validation    | ✅ Done  | Edge detection, k-means colors, content scoring                                                         |
| Local DB + Offline   | ✅ Done  | 10,008 species, 1,960 with perceptual hashes (19.6%)                                                    |
| Image Processing     | ✅ Done  | OpenCV gate, compression, thumbnails, server-side storage                                               |
| History API          | ✅ Done  | GET list + detail + thumbnail endpoints                                                                 |
| Supabase Schema      | ✅ Done  | All 5 migrations applied to production Supabase                                                         |
| CI/CD                | ✅ Done  | GitHub Actions (lint, test, build, deploy)                                                              |
| Mobile UI            | ✅ Done  | Auth, 4-tabs (Scan/Saved/History/Profile), results, species detail                                      |
| Phase 2 Features     | ✅ Done  | Disease UI, favorites, share, caching, multi-lang                                                       |
| Admin Panel          | ✅ Done  | Backend API + mobile screen + RLS (security definer)                                                    |
| Frontend Tests       | ✅ Done  | 41 tests (Jest)                                                                                         |
| E2E Tests            | ✅ Done  | 21 Playwright API tests (OpenCV, caching, security, error recovery)                                     |
| Production Supabase  | ✅ Done  | Linked, 5 migrations applied, 10,008 GBIF species imported                                              |
| Deploy Bundle Size   | ✅ Fixed | 611MB → 268MB (412MB GBIF zip removed, `.vercelignore` widened)                                         |
| GBIF Seed Script     | ✅ Done  | `seed_supabase_gbif.py` + GH Action (dispatch + weekly cron)                                            |
| History Thumbnails   | ✅ Done  | Persisted as base64 in `identifications.image_thumbnails` (mig 006)                                     |
| Species Detail       | ✅ Fixed | `common_names` type string → string[]                                                                   |
| PlantNet Integration | ✅ Fixed | `lang` removed, skip-gate fixed, verified with rose image                                               |
| Vercel Deploy        | ✅ Done  | `https://sasyakashi.vercel.app` live, bundle 268MB                                                      |
| Android APK          | ✅ Done  | Production build on EAS, env vars via EAS Secrets                                                       |
| EAS Secrets          | ✅ Done  | Supabase URL + anon key (not in git)                                                                    |
| PR #20               | 🟡 Open  | `feat/branded-404-favicon-sitemap` → `main`, favicon/404 + deploy-size/thumbnail changes, merge by user |

## What's Next

1. Deploy fixed bundle to production + push migration 006 + run `seed_supabase_gbif` (user merges PR #20)
2. Recheck PlantNet 404/401 identify failure
3. Test APK on physical device (verify identify flow against production backend)
4. Expand hash index to remaining ~8K species (need alternative image sources)
5. Push notifications

## Key Files

| File                              | Purpose                    |
| --------------------------------- | -------------------------- |
| `src/app/_layout.tsx`             | Root layout + auth routing |
| `src/app/(auth)/login.tsx`        | Login screen               |
| `src/app/(tabs)/index.tsx`        | Scan screen                |
| `src/app/identification/[id].tsx` | Results (central screen)   |
| `src/app/species/[name].tsx`      | Species details            |
| `src/app/(tabs)/favorites.tsx`    | Favorites list             |
| `src/hooks/use-auth.tsx`          | Auth context               |
| `src/lib/api-client.ts`           | Backend API client         |

## Environment Variables

```bash
# Client-side (EXPO_PUBLIC_ prefix)
EXPO_PUBLIC_SUPABASE_URL=https://amyriuhwqyalodsfkwzf.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=<your-key>
EXPO_PUBLIC_API_URL=http://localhost:8000/api     # Dev: local backend
# EXPO_PUBLIC_API_URL=https://sasyakashi.vercel.app/api  # Prod: production backend

# Backend (.env.local)
USE_REMOTE=true
SUPABASE_URL=https://amyriuhwqyalodsfkwzf.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<key>
```

## Run Commands

```bash
# Start Expo
npx expo start

# Backend
cd api && uvicorn api.main:app --reload --port 8000 --no-server-header

# Python tests (73 passing)
cd api && pytest

# E2E tests (21 passing)
npx playwright test e2e/api-tests/ --reporter=list

# Frontend tests (41 passing)
npx jest --no-cache

# TypeScript + lint
npx tsc --noEmit && npx expo lint
```

## Common Mistakes to Avoid

1. **Don't use `.ts` for files with JSX** — must be `.tsx`
2. **Don't skip RLS** — every table needs row-level security
3. **Don't use `expo-cli` directly** — use `npx expo` commands
4. **Don't use `npm install` for Expo packages** — use `npx expo install`
5. **Don't store tokens in AsyncStorage** — use `expo-secure-store`
