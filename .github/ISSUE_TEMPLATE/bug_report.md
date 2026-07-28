# Gardenify

> 🌿 Identify any plant, flower, leaf, or fruit with your camera

[![Build Status](https://github.com/luckyhegde6/gardenify/actions/workflows/lint.yml/badge.svg)](https://github.com/luckyhegde6/gardenify/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Gardenify is a plant identification mobile app built with Expo (React Native) for Android. Users capture photos and receive species identification with confidence scores, common names, and taxonomy details.

**Powered by PlantNet API** — 50,000+ species, 500 free identifications/day.

## Quick Start

```bash
# Clone
git clone https://github.com/luckyhegde6/gardenify.git
cd gardenify

# Install
npm install

# Configure
cp .env.example .env
# Edit .env with your keys

# Run
npx expo start
```

## Tech Stack

| Layer | Technology |
|---|---|
| Mobile | Expo SDK 55 (React Native) |
| Language | TypeScript 5.9 / Python 3.12 |
| Backend | FastAPI on Vercel |
| Database | Supabase (PostgreSQL) |
| Plant AI | PlantNet API v2 |
| Build | EAS Build |
| CI/CD | GitHub Actions |

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

## Development

```bash
npm run lint          # Lint TypeScript
npx tsc --noEmit      # Type check
cd api && pytest      # Python tests
npx expo start        # Start dev server
```

## Project Structure

```
src/                    # Expo app (TypeScript)
  app/                  # File-based routes
  components/           # UI components
  hooks/                # Custom hooks
  lib/                  # Utilities

api/                    # Python backend
  main.py               # FastAPI server
  routes/               # API routes
  services/             # Business logic

supabase/               # Database
  migrations/           # SQL migrations

.agents/                # Agent docs
docs/                   # HTML docs with Mermaid
```

## Deployment

- **Backend**: `vercel deploy --prod`
- **Mobile**: `eas build -p android --profile production`
- **Database**: `supabase db push`

## Documentation

- [Architecture](.agents/architecture.md)
- [Phase 1 MVP](.agents/phase-1-mvp.md)
- [Security](.agents/security-harness.md)
- [HTML Docs](docs/index.html)
- [API Flows](docs/api-flows.html)
- [Auth Flow](docs/auth-flow.html)

## License

MIT
