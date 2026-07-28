# Gardenify

[![CI](https://github.com/luckyhegde6/gardenify/actions/workflows/ci.yml/badge.svg)](https://github.com/luckyhegde6/gardenify/actions/workflows/ci.yml)
[![Backend](https://img.shields.io/badge/Backend-Vercel-black)](https://sasyakashi.vercel.app)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Expo](https://img.shields.io/badge/Expo-SDK%2055-blue)](https://expo.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Identify any plant, flower, leaf, or fruit with your camera. Powered by PlantNet AI.

**Live API:** [sasyakashi.vercel.app](https://sasyakashi.vercel.app)

Gardenify is a plant identification mobile app built with Expo (React Native) for Android. Users capture photos and receive species identification with confidence scores, common names, and taxonomy details.

## Architecture

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────┐
│  Expo App    │────▶│  Python Backend   │────▶│ PlantNet API │
│  (Android)   │     │  FastAPI/Vercel   │     │ (500/day)    │
│              │     └────────┬──────────┘     └──────────────┘
│  supabase-js │             │
│  (direct)    │     ┌───────▼───────────┐
└──────────────┘     │  Supabase         │
                     │  Auth + DB + Store │
                     └───────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Mobile | Expo SDK 55 (React Native) |
| Language | TypeScript 5.9 / Python 3.12 |
| Backend | FastAPI on [Vercel](https://sasyakashi.vercel.app) |
| Database | [Supabase](https://supabase.com) (PostgreSQL) |
| Auth | Supabase Auth |
| Plant AI | PlantNet API v2 |
| Build | EAS Build |
| CI/CD | GitHub Actions |

## API Endpoints

**Swagger UI (interactive docs):** [sasyakashi.vercel.app/docs](https://sasyakashi.vercel.app/docs)
**OpenAPI schema:** [sasyakashi.vercel.app/openapi.json](https://sasyakashi.vercel.app/openapi.json)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/identify` | Identify plant from images (multipart/form-data) |
| `GET` | `/api/species?q={query}&limit={n}` | Search species database |
| `GET` | `/api/species/{id}` | Species details by ID |
| `GET` | `/api/species/by-name/{name}` | Species by scientific name |

**Base URL:** `https://sasyakashi.vercel.app`

### Authentication

The API is currently **open** — no authentication is required to call any endpoint. Auth via Supabase JWT is planned for a future phase (see [phase-1-mvp.md](.agents/phase-1-mvp.md)). When implemented, authenticated requests will include:

```
Authorization: Bearer <supabase_jwt_token>
```

### Using the API

**Health check:**
```bash
curl https://sasyakashi.vercel.app/api/health
```

**Identify a plant** (send an image):
```bash
curl -X POST https://sasyakashi.vercel.app/api/identify \
  -F "images=@plant_photo.jpg"
```

**Search species:**
```bash
curl "https://sasyakashi.vercel.app/api/species?q=rose&limit=5"
```

**Get species by ID:**
```bash
curl https://sasyakashi.vercel.app/api/species/1
```

## Local Development

### Prerequisites

- Node.js 20+
- Python 3.12+
- Vercel CLI (`npm install -g vercel`)

### 1. Clone and install

```bash
git clone https://github.com/luckyhegde6/gardenify.git
cd gardenify
npm install
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your Supabase URL, anon key, and PlantNet API key
```

### 3. Start the backend

```bash
# Install Python dependencies
pip install -r api/requirements.txt

# Start local server
vercel dev
# → http://127.0.0.1:8000
```

### 4. Start the Expo app

```bash
npx expo start
# → Press 'a' for Android emulator
```

## Development Commands

| Command | Description |
|---|---|
| `npx expo start` | Start Expo dev server |
| `npm run lint` | Lint TypeScript |
| `npx tsc --noEmit` | Type check |
| `vercel dev` | Start Python backend |
| `python -m pytest api/tests/ -v` | Run backend tests |
| `python -m api.data.importers.run_all --seed-only` | Seed local DB |

## Project Structure

```
src/                    # Expo app
  app/                  # File-based routes (expo-router)
    (auth)/             # Auth screens
    (tabs)/             # Tab screens (Scan, History, Profile)
    identification/     # Result detail screens
  components/           # Reusable UI components
  hooks/                # Custom React hooks
  lib/                  # Utilities (supabase, api, types)

api/                    # Python backend
  main.py               # FastAPI entrypoint
  routes/               # API routes (health, identify, species)
  services/             # Business logic (PlantNet, local DB, hashing)
  models/               # Pydantic schemas
  data/                 # Local plant database (SQLite)
    importers/          # GBIF + seed data importers
  tests/                # Backend tests (73+ tests)

supabase/               # Database
  migrations/           # SQL migrations

.agents/                # Agent configuration
docs/                   # HTML documentation
```

## Deployment

### Backend (Vercel)

Already deployed at [sasyakashi.vercel.app](https://sasyakashi.vercel.app). Push to `main` to trigger automatic deployment.

```bash
vercel deploy --prod
```

### Mobile (EAS Build)

```bash
npx eas-cli build -p android --profile production
```

## Documentation

- [Architecture](.agents/architecture.md) — Full system design
- [Phase 1 MVP](.agents/phase-1-mvp.md) — MVP checklist
- [Security](.agents/security-harness.md) — Security practices

## License

MIT
