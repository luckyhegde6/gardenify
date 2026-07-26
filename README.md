# Gardenify

> Identify any plant, flower, leaf, or fruit with your camera. Powered by PlantNet AI.

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
| Backend | FastAPI on Vercel |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth |
| Plant AI | PlantNet API v2 |
| Build | EAS Build |
| CI/CD | GitHub Actions |

## Prerequisites

- Node.js 20+
- Python 3.12+
- Vercel CLI (`npm install -g vercel`)
- Supabase CLI (`npm install -g supabase`)
- Expo CLI (`npm install -g expo-cli`)

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/luckyhegde6/gardenify.git
cd gardenify
npm install
```

### 2. Set up Supabase

```bash
# Start local Supabase (requires Docker)
supabase start

# Or create a project at https://supabase.com
# Then run migrations:
supabase db push
```

### 3. Configure environment

```bash
cp .env.example .env
# Fill in your Supabase URL, anon key, and PlantNet API key
```

### 4. Start the app

```bash
# Terminal 1: Expo dev server
npx expo start

# Terminal 2: Python backend
cd api
pip install -r requirements.txt
vercel dev
```

## Development Commands

| Command | Description |
|---|---|
| `npx expo start` | Start Expo dev server |
| `npx expo start --android` | Start on Android |
| `npm run lint` | Lint TypeScript |
| `npx tsc --noEmit` | Type check |
| `vercel dev` | Start Python backend locally |
| `pytest` | Run Python tests |
| `npx eas-cli build -p android` | Build Android APK |

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
  routes/               # API routes
  services/             # Business logic
  models/               # Pydantic schemas

supabase/               # Database
  migrations/           # SQL migrations
  seed.sql              # Seed data

.agents/                # Agent configuration
docs/                   # HTML documentation
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check + quota info |
| `POST` | `/api/identify` | Identify plant from images |
| `GET` | `/api/species/{name}` | Species details |

## Deployment

### Backend (Vercel)

```bash
vercel deploy --prod
```

### Mobile (EAS Build)

```bash
# Build Android APK
npx eas-cli build -p android --profile production

# Build and submit to Play Store
npx eas-cli build -p android --profile production --submit
```

## Documentation

- [Architecture](.agents/architecture.md) — Full system design
- [Phase 1 MVP](.agents/phase-1-mvp.md) — MVP checklist
- [Security](.agents/security-harness.md) — Security practices
- [API Docs](docs/api-flows.html) — API flow diagrams
- [HTML Docs](docs/index.html) — Visual documentation

## Contributing

1. Create a feature branch from `main`
2. Make your changes following the code conventions in `AGENTS.md`
3. Run `npm run lint` and `npx tsc --noEmit`
4. Create a pull request with a clear description

## License

MIT
