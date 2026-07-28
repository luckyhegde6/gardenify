# Architecture — Gardenify

> Full system architecture for the Gardenify plant identification app.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GARDENIFY SYSTEM                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐                                               │
│  │   EXPO APP       │  Android-first mobile app                    │
│  │   (React Native) │  expo-router file-based navigation           │
│  │                  │  expo-image-picker for camera/gallery         │
│  │   supabase-js    │  Direct Supabase connection for auth/data    │
│  └────────┬─────────┘                                               │
│           │                                                         │
│           │ HTTP (JSON)          HTTPS (multipart)                  │
│           ▼                       ▼                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │  PYTHON BACKEND  │  │  PLANTNET API    │  │  SUPABASE        │ │
│  │  FastAPI/Vercel  │  │  REST v2         │  │                  │ │
│  │                  │  │  50K+ species    │  │  ┌────────────┐  │ │
│  │  /api/identify   │──│  /v2/identify    │  │  │ PostgreSQL │  │ │
│  │  /api/health     │  │  Free: 500/day   │  │  │ + RLS      │  │ │
│  │  /api/species    │  │                  │  │  ├────────────┤  │ │
│  └──────────────────┘  └──────────────────┘  │  │ Auth       │  │ │
│                                              │  │ (JWT)      │  │ │
│  ┌──────────────────┐                       │  ├────────────┤  │ │
│  │  EAS BUILD       │                       │  │ Storage    │  │ │
│  │  Android APK/AAB │                       │  │ (images)   │  │ │
│  │  iOS (Phase 3)   │                       │  └────────────┘  │ │
│  └──────────────────┘                       └──────────────────┘ │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐                      │
│  │  GITHUB ACTIONS  │  │  VERCEL          │                      │
│  │  CI/CD           │  │  Serverless host │                      │
│  │  lint + test     │  │  for Python API  │                      │
│  │  + EAS build     │  │                  │                      │
│  └──────────────────┘  └──────────────────┘                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow: Plant Identification

```
User captures photo
        │
        ▼
┌─────────────────┐
│ Client-side     │  expo-image-manipulator
│ Compression     │  Max 1024px, JPEG quality 0.8
│ + Hashing       │  SHA-256 for deduplication
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cache Check     │  AsyncStorage: hash → cached result?
│ (Local)         │  HIT → skip to display
└────────┬────────┘
         │ MISS
         ▼
┌─────────────────┐
│ Upload to       │  Supabase Storage
│ Supabase        │  Path: plant-images/{user_id}/{uuid}.jpg
│ Storage         │  Returns: signed URL
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Call Python     │  POST /api/identify
│ Backend         │  Body: images[] + organs[]
│ (FastAPI)       │  Header: Authorization: Bearer {jwt}
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Forward to      │  POST https://my-api.plantnet.org/v2/identify/all
│ PlantNet API    │  Multipart: images + organs
│                 │  Returns: species list + confidence scores
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Save to DB      │  INSERT INTO identifications
│ (Supabase)      │  image_urls, species_info, confidence, full_response
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Return to App   │  bestMatch, results[], remainingQuota
│ Display Result  │  Species name, confidence bar, common names
└─────────────────┘
```

## Auth Flow

```
┌─────────────────┐         ┌──────────────────┐
│  Mobile App     │         │  Supabase Auth   │
│                 │         │                  │
│  1. Register    │────────▶│  signUp()        │
│     email+pass  │         │  Creates user    │
│                 │◀────────│  Sends confirm   │
│                 │         │                  │
│  2. Login       │────────▶│  signIn()        │
│                 │◀────────│  Returns JWT     │
│                 │         │  + refresh token │
│                 │         │                  │
│  3. Session     │ Store in SecureStore      │
│     Persistence │ (iOS Keychain / Android   │
│                 │  Keystore)                │
│                 │         │                  │
│  4. Auto-refresh│◀───────│  Token expires   │
│                 │  1hr    │  → refresh       │
│                 │────────▶│  → new JWT       │
│                 │         │                  │
│  5. RLS         │ Every DB query includes   │
│     Enforcement │ Authorization: Bearer JWT │
│                 │ Supabase checks auth.uid()│
└─────────────────┘         └──────────────────┘
```

## Component Breakdown

### Mobile App (Expo)

| Component | File | Purpose |
|---|---|---|
| Root Layout | `src/app/_layout.tsx` | Theme provider, auth guard, splash |
| Auth Guard | `src/components/auth-guard.tsx` | Redirect unauthenticated users |
| Tab Navigator | `src/components/app-tabs.tsx` | Bottom tabs (Scan, History, Profile) |
| Scan Screen | `src/app/(tabs)/index.tsx` | Camera capture + organ selection |
| Result Screen | `src/app/identification/[id].tsx` | Species result detail |
| History Screen | `src/app/(tabs)/history.tsx` | Past identifications list |
| Profile Screen | `src/app/(tabs)/profile.tsx` | User info + settings |
| Supabase Client | `src/lib/supabase.ts` | Configured with SecureStore |
| API Client | `src/lib/api.ts` | Backend API calls |
| Types | `src/lib/types.ts` | TypeScript interfaces |

### Python Backend (FastAPI)

| Component | File | Purpose |
|---|---|---|
| Entrypoint | `api/main.py` | FastAPI app, CORS, error handlers |
| Config | `api/config.py` | Settings from env vars |
| Identify Route | `api/routes/identify.py` | POST /api/identify |
| Health Route | `api/routes/health.py` | GET /api/health |
| PlantNet Client | `api/services/plantnet.py` | PlantNet API wrapper |
| Cache Service | `api/services/cache.py` | Image hash caching |
| Schemas | `api/models/schemas.py` | Pydantic models |
| Auth Middleware | `api/middleware/auth.py` | JWT verification |
| Rate Limiter | `api/middleware/rate_limit.py` | Rate limiting |

### Database (Supabase PostgreSQL)

| Table | Purpose | RLS |
|---|---|---|
| `profiles` | User profiles (synced from auth) | Users see own only |
| `identifications` | Plant scan results | Users see own only |
| `favorites` | Saved species | Users see own only |
| Storage: `plant-images` | Raw compressed images | Owner read/write |
| Storage: `avatars` | User profile pictures | Public read, owner write |

## Technology Decisions

| Decision | Choice | Why |
|---|---|---|
| Plant ID | PlantNet API | Free 500/day, 50K+ species, specialized |
| Database | Supabase (PostgreSQL) | RLS, auth, storage in one service |
| Backend | FastAPI on Vercel | Python flexibility, serverless scale |
| Mobile | Expo SDK 55 | File-based routing, typed routes, React 19 |
| Auth | Supabase Auth | Email + Google, session persistence |
| Storage | Supabase Storage | Private buckets with RLS |

## Scaling Strategy

```
Phase 1 (MVP):     Vercel serverless + Supabase free tier
Phase 2 (Enhanced): Add caching, optimize queries
Phase 3 (Community): Consider Supabase Pro ($25/mo)
Phase 4 (Scale):    Evaluate dedicated backend if needed
```

**Key metrics to watch:**
- PlantNet API calls/day (free limit: 500)
- Supabase Storage usage (free limit: 1GB)
- Supabase DB size (free limit: 500MB)
- Vercel function invocations (free: 100K/mo)
