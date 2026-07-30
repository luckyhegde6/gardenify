# Gardenify

[![CI](https://github.com/luckyhegde6/gardenify/actions/workflows/ci.yml/badge.svg)](https://github.com/luckyhegde6/gardenify/actions/workflows/ci.yml)
[![Backend](https://img.shields.io/badge/Backend-Vercel-black)](https://sasyakashi.vercel.app)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Expo](https://img.shields.io/badge/Expo-SDK%2055-blue)](https://expo.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Identify any plant, flower, leaf, or fruit with your camera. Powered by PlantNet AI.

**Live API:** [sasyakashi.vercel.app](https://sasyakashi.vercel.app)

Gardenify is a plant identification mobile app built with Expo (React Native) for Android. Users capture photos and receive species identification with confidence scores, common names, taxonomy, disease detection, and plant care instructions.

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

| Layer    | Technology                                         |
| -------- | -------------------------------------------------- |
| Mobile   | Expo SDK 55 (React Native)                         |
| Language | TypeScript 5.9 / Python 3.12                       |
| Backend  | FastAPI on [Vercel](https://sasyakashi.vercel.app) |
| Database | [Supabase](https://supabase.com) (PostgreSQL)      |
| Auth     | Supabase Auth                                      |
| Plant AI | PlantNet API v2                                    |
| Build    | EAS Build                                          |
| CI/CD    | GitHub Actions                                     |

## API Endpoints

**Swagger UI (interactive docs):** [sasyakashi.vercel.app/docs](https://sasyakashi.vercel.app/docs)
**OpenAPI schema:** [sasyakashi.vercel.app/openapi.json](https://sasyakashi.vercel.app/openapi.json)

| Method   | Endpoint                           | Description                                       |
| -------- | ---------------------------------- | ------------------------------------------------- |
| `GET`    | `/api/health`                      | Health check + debug info                         |
| `POST`   | `/api/identify`                    | Identify plant from images (multipart/form-data)  |
| `GET`    | `/api/species?q={query}&limit={n}` | Search species database (10,008 species)          |
| `GET`    | `/api/species/{id}`                | Species details by ID                             |
| `GET`    | `/api/species/by-name/{name}`      | Species by scientific name                        |
| `GET`    | `/api/history`                     | Past identifications (list + detail + thumbnails) |
| `GET`    | `/api/admin/users`                 | List users (admin only, JWT required)             |
| `PATCH`  | `/api/admin/users/{id}`            | Update user role/tier (admin only)                |
| `DELETE` | `/api/admin/users/{id}`            | Soft-delete user (admin only)                     |

**Base URL:** `https://sasyakashi.vercel.app`

### Authentication

Most endpoints are **open** (no auth required). Admin endpoints (`/api/admin/*`) require a Supabase JWT with `is_admin=true`.

```
Authorization: Bearer <supabase_jwt_token>
```

### Local Dev Test Accounts

For local development against the Supabase seed data, use these accounts:

| Email               | Role  | Tier    |
| ------------------- | ----- | ------- |
| admin@gardenify.app | Admin | premium |
| test@gardenify.app  | User  | free    |
| user2@gardenify.app | User  | free    |

> Passwords are set in `supabase/seed.sql` (local dev only — never commit to production).

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

| Command                                                                  | Description                  |
| ------------------------------------------------------------------------ | ---------------------------- |
| `npx expo start`                                                         | Start Expo dev server        |
| `npm run lint`                                                           | Lint TypeScript              |
| `npx tsc --noEmit`                                                       | Type check                   |
| `cd api && uvicorn api.main:app --reload --port 8000 --no-server-header` | Start Python backend         |
| `cd api && pytest -v`                                                    | Run backend tests (73)       |
| `npx jest --no-cache`                                                    | Run frontend tests (41)      |
| `npx playwright test e2e/api-tests/ --reporter=list`                     | Run E2E tests (21)           |
| `make seed`                                                              | Seed local Supabase database |

## Project Structure

```
src/                    # Expo app (TypeScript)
  app/                  # expo-router file-based routes
    (auth)/             # Auth screens (login, register)
    (tabs)/             # Tab screens (Scan, Favorites, History, Profile)
    identification/     # Result detail screens
    species/            # Species detail screens
  components/           # Reusable UI components
  hooks/                # Custom React hooks (auth, camera, identification, theme, notifications)
  lib/                  # Utilities (supabase, api-client, types, cache, share, offline-queue)
  constants/            # Theme, fonts, spacing

api/                    # Python backend (FastAPI)
  main.py               # Vercel entrypoint + app factory
  routes/               # API route handlers (health, identify, species, history, admin)
  services/             # Business logic (PlantNet, plant care, OpenCV, hashing, local DB, Supabase)
  models/               # Pydantic schemas
  data/                 # Local plant database (SQLite, 10,008 species)
    importers/          # GBIF + seed data importers
  tests/                # Backend tests (73+ tests)

supabase/               # Database migrations
  migrations/           # SQL migration files (001-005)

.agents/                # Agent configuration and guidelines
```

## Releases

### Latest APK

Download the latest production APK from [Expo EAS Builds](https://expo.dev/accounts/luckyhegdedev/projects/gardenify/builds).

Or build it yourself:

```bash
npx eas build -p android --profile production
```

### Release Workflow

1. **Merge PR** into `main` (squash merge)
2. **CI runs automatically**: lint + typecheck + Python tests
3. **Vercel auto-deploys** backend from `main` (if `api/` changed)
4. **Tag the release**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
5. **GitHub Release is created** automatically (via CI)
6. **Build APK manually** (or via CI):
   ```bash
   npx eas build -p android --profile production
   ```

### APK Distribution

- **No Play Store** — direct APK installation only
- **Download from** [expo.dev](https://expo.dev/accounts/luckyhegdedev/projects/gardenify/builds)
- **Install on device**: enable "Install from unknown sources" in Android settings
- **OTA updates**: published to preview channels on `feat/*`/`bugfix/*` pushes

### Environment Variables for Release Builds

Required env vars for production APK builds. Set these via [EAS Secrets](https://docs.expo.dev/build-reference/variables/) (never commit secrets to git):

| Variable                        | Description                 |
| ------------------------------- | --------------------------- |
| `EXPO_PUBLIC_API_URL`           | Backend URL (in `eas.json`) |
| `EXPO_PUBLIC_SUPABASE_URL`      | Supabase project URL        |
| `EXPO_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key      |

## Documentation

- [Architecture](.agents/architecture.md) — Full system design
- [Phase 1 MVP](.agents/phase-1-mvp.md) — MVP checklist
- [Security](.agents/security-harness.md) — Security practices

## License

MIT
