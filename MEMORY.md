# MEMORY.md — Quick Context for Agents

> **Read this FIRST.** This file gives you a fast recap of the project without burning context reading everything.

## Project Identity

**Gardenify** — Plant identification mobile app. Users photograph plants → get species, confidence, taxonomy, disease check, and care instructions.

| Key | Value |
|---|---|
| Repo | `https://github.com/luckyhegde6/gardenify` |
| EAS Project ID | `b17c6958-f3e7-4ec1-afcf-3b241fcbcda0` |
| EAS Owner | `luckyhegdedev` |
| Platform | Android-first, iOS later (Phase 3) |
| Backend | Python FastAPI on Vercel |
| Database | Supabase (PostgreSQL + Auth + Storage) |
| Plant AI | PlantNet API v2 (free 500/day) |

## Architecture in 10 Seconds

```
Expo App → FastAPI Backend → PlantNet API
    ↓              ↓
 Supabase      Supabase
 (auth/db)     (storage)
```

- **Auth**: Supabase Auth (email/password), JWT stored in expo-secure-store
- **API Key**: PlantNet key stays server-side only (backend proxy)
- **RLS**: Every table has Row Level Security — users see only their own data

## Current State (as of last session)

### Done
- [x] AGENTS.md, CLAUDE.md, LESSONS.md, MEMORY.md
- [x] `.agents/` — architecture.md, phase TODOs, guidelines, security, handoff
- [x] Python backend: FastAPI with `/api/identify`, `/api/health`
- [x] PlantNet service integration (async httpx)
- [x] Disease detection endpoint via PlantNet diseases API
- [x] Plant care analysis service (watering, sunlight, soil, growth)
- [x] Image caching (SHA-256 hash → cached result)
- [x] Metadata capture (EXIF, GPS, timestamp, device)
- [x] Pydantic schemas for all request/response models
- [x] Supabase migrations (users, identifications, favorites, user_settings)
- [x] OpenAPI 3.1 specification
- [x] Python tests (pytest)
- [x] HTML docs with Mermaid diagrams (3 pages)
- [x] CI/CD: GitHub Actions (lint, eas-build, deploy, migrate, release)
- [x] EAS config, MCP config, OpenCode config, Makefile
- [x] OpenCode rules

### Not Done
- [ ] Expo mobile UI screens (Scan, History, Profile, Result)
- [ ] Supabase project credentials (need from user)
- [ ] PlantNet API key (need from user)
- [ ] Vercel deployment (need credentials)
- [ ] `supabase db push` (need project linked)
- [ ] `vercel deploy --prod` (need project linked)
- [ ] `npm install` (need to add supabase-js, image-picker deps)

## Key Files Reference

| File | Purpose | Lines |
|---|---|---|
| `AGENTS.md` | Master agent instructions | 138 |
| `CLAUDE.md` | Behavioral guidelines | — |
| `MEMORY.md` | This file — quick context | — |
| `LESSONS.md` | Running lessons log | — |
| `.agents/architecture.md` | Full system architecture | 191 |
| `.agents/phase-1-mvp.md` | MVP TODO checklist | — |
| `api/main.py` | FastAPI entrypoint | 35 |
| `api/config.py` | Settings from env | 17 |
| `api/routes/identify.py` | POST /api/identify | 91 |
| `api/routes/health.py` | GET /api/health | 14 |
| `api/services/plantnet.py` | PlantNet API wrapper | 103 |
| `api/services/plant_care.py` | Care analysis engine | — |
| `api/services/cache.py` | Image hash + validation | — |
| `api/models/schemas.py` | Pydantic models | — |
| `supabase/migrations/001_initial_schema.sql` | DB schema + RLS | — |

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/health` | No | Health check |
| `POST` | `/api/identify` | No* | Identify plant + disease + care |
| `GET` | `/api/species/{name}` | No | Species details (Phase 2) |

*Auth not required for MVP identify (PlantNet quota is the limit). Add auth later.

## Database Tables

| Table | Purpose | RLS |
|---|---|---|
| `users` | User profiles (auto-created on signup) | Users see own |
| `identifications` | Plant scan results + metadata | Users see own |
| `favorites` | Saved species bookmarks | Users see own |
| `user_settings` | Per-user preferences | Users see own |

## Environment Variables Needed

```bash
# Backend (Vercel) — SUPPLY THESE
PLANTNET_API_KEY=your_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# Frontend (Expo .env) — SUPPLY THESE
EXPO_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
EXPO_PUBLIC_API_URL=http://localhost:3000/api
```

## Local Testing Quick Reference

### 1. Start Backend
```bash
cd api
pip install -r requirements.txt
vercel dev
# Opens at http://localhost:3000
```

### 2. Swagger UI
```
http://localhost:3000/docs
```

### 3. Test Identify via Swagger
1. Open `http://localhost:3000/docs`
2. Click `POST /api/identify`
3. Click "Try it out"
4. Upload 1-5 images (JPEG/PNG)
5. Set organs: `["leaf"]` or `["auto"]`
6. Set lang: `"en"`
7. Click "Execute"

### 4. Test via curl
```bash
curl -X POST http://localhost:3000/api/identify \
  -F "images=@plant_photo.jpg" \
  -F 'organs=["leaf"]' \
  -F "lang=en"
```

### 5. Test Health Check
```bash
curl http://localhost:3000/api/health
```

## What Each Service Does

### Image Processing Pipeline
```
User photo → Validate (type/size) → SHA-256 hash → Check cache
  Cache HIT  → Return cached result (skip PlantNet call)
  Cache MISS → Upload to Supabase Storage → Forward to PlantNet → Cache result → Return
```

### Metadata Captured Per Identification
- Image SHA-256 hash (deduplication)
- File size, dimensions, format
- EXIF data if available (camera, date taken)
- GPS coordinates (if user grants permission)
- Device info (platform, app version)
- Timestamp of identification
- User organ selection (leaf/flower/fruit/bark)

### Disease Detection
- Uses PlantNet diseases API: `POST /v2/diseases/identify`
- Same image upload format
- Returns disease name, confidence, description
- Runs in parallel with species identification

### Plant Care Analysis
Based on identified species, returns:
- **Watering**: Frequency, method, seasonal adjustments
- **Sunlight**: Direct/indirect/shade, hours per day
- **Soil**: Type, pH, drainage requirements
- **Temperature**: Min/max range, frost sensitivity
- **Humidity**: Preferred level, misting needs
- **Growth**: Mature height, spread, growth rate
- **Bloom**: Flowering season, color, fragrance
- **Propagation**: Seeds, cuttings, division
- **Common Pests**: Aphids, spider mites, etc.
- **Toxicity**: Safe for pets/children?

## Agent Workflow

1. **Read MEMORY.md** (this file) — 30 seconds
2. **Read relevant .agents/ file** — if doing architecture work
3. **Read AGENTS.md** — if writing new code
4. **Check LESSONS.md** — before making decisions
5. **Run lint/typecheck** — before committing
6. **Update LESSONS.md** — after learning something new

## Don't Waste Context On

- Reading all `.agents/` files unless specifically needed
- Re-reading architecture.md if you already know the system
- Looking at HTML docs unless debugging rendering
- Reading CI/CD workflows unless modifying them

## Key Decisions Already Made

- **PlantNet over Google Vision**: Free 500/day, specialized for plants
- **FastAPI over Express**: Python ecosystem, type safety, async
- **Supabase over Firebase**: RLS, PostgreSQL, open source
- **expo-secure-store over AsyncStorage**: Security for tokens
- **Server-side API key**: Never expose PlantNet key to client
- **hybrid local+cloud**: react-native-fast-tflite for Phase 3+

## External Docs

- Expo SDK 55: https://docs.expo.dev/versions/v55.0.0/
- Supabase + Expo: https://docs.expo.dev/guides/using-supabase/
- PlantNet API: https://my.plantnet.org/doc/getting-started/introduction
- FastAPI: https://fastapi.tiangolo.com/
- Vercel Python: https://vercel.com/docs/functions/python
