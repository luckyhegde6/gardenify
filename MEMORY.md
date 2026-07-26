# MEMORY.md — Quick Context for Agents

> **Read this FIRST.** Saves ~60% context vs reading AGENTS.md + architecture.md.

## Project Identity

**Gardenify** — Plant identification mobile app. Photo → species + disease + care instructions.

| Key | Value |
|---|---|
| Repo | `https://github.com/luckyhegde6/gardenify` |
| EAS Project ID | `b17c6958-f3e7-4ec1-afcf-3b241fcbcda0` |
| Platform | Android-first, iOS later |
| Backend | Python FastAPI on Vercel |
| Database | Supabase (PostgreSQL + Auth + Storage) |
| Plant AI | PlantNet API v2 (free 500/day) |

## Architecture (10 seconds)

```
Expo App → FastAPI Backend → PlantNet API
    ↓              ↓
 Supabase      Supabase
 (auth/db)     (storage)
```

## Current State

### Done
- [x] All agent docs (AGENTS.md, CLAUDE.md, LESSONS.md, MEMORY.md)
- [x] `.agents/` — architecture, phase TODOs, security, handoff, self-improvement
- [x] Backend: FastAPI `/api/identify`, `/api/health`, `/api/debug`
- [x] PlantNet: species + disease detection
- [x] Plant care: watering, sunlight, soil, temperature, growth, propagation
- [x] Caching: SHA-256 hash → 1hr in-memory cache
- [x] Metadata: EXIF, GPS, dimensions, camera info
- [x] Structured logging with correlation IDs + request timing
- [x] Supabase migrations with RLS on all tables
- [x] CI/CD: GitHub Actions (lint, test, build, deploy)
- [x] HTML docs with Mermaid (3 pages)
- [x] Local dev: docker-compose.yml, dev.sh/dev.bat scripts
- [x] MCP config (Expo remote + Supabase utils)

### Not Done
- [ ] Expo mobile UI screens
- [ ] Supabase/PlantNet credentials (need from user)
- [ ] Vercel deployment
- [ ] ENVIRONMENT/USE_REMOTE env vars
- [ ] Seed data scripts
- [ ] Testing framework (TDD, e2e, integration)
- [ ] PRD.md (product requirements)
- [ ] BUGS.md (issue tracker)
- [ ] LSP/MCP rules
- [ ] AI guardrails

## Local Development

### Quick Start (recommended)
```bash
# One command — starts Supabase + backend
./dev.sh        # macOS/Linux
dev.bat         # Windows
```

### Manual Start
```bash
# 1. Start local Supabase (requires Docker)
docker compose up -d
# Dashboard: http://localhost:54323

# 2. Start backend
cd api
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

### Test via Swagger
1. Open `http://localhost:8000/docs` (debug mode only)
2. Click `POST /api/identify` → Try it out
3. Upload images, set organs `["leaf"]`, click Execute

### Test via curl
```bash
curl -X POST http://localhost:8000/api/identify \
  -F "images=@plant.jpg" -F 'organs=["leaf"]' -F "lang=en"
```

### Debug Endpoint
```bash
curl http://localhost:8000/api/debug
# Returns: config status, cache stats, uptime, Python version
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/identify` | Identify + disease + care |
| `GET` | `/api/debug` | Debug info (dev only) |

## Key Files

| File | Purpose |
|---|---|
| `api/main.py` | FastAPI app + logging middleware |
| `api/config.py` | Settings from env vars |
| `api/routes/identify.py` | POST /api/identify |
| `api/routes/health.py` | Health + debug endpoints |
| `api/services/plantnet.py` | PlantNet API client |
| `api/services/plant_care.py` | Care profile lookup |
| `api/services/cache.py` | Hashing, validation, caching, metadata |
| `api/models/schemas.py` | Pydantic models |
| `docker-compose.yml` | Local Supabase stack |
| `.env.example` | All env vars with defaults |

## Environment Variables

```bash
# Local dev (defaults work out of the box)
cp .env.example .env

# Production — supply these
PLANTNET_API_KEY=your_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
```

## Logging & Observability

- Every request gets a **correlation ID** (X-Correlation-ID header)
- Response time logged: `GET /api/identify → 200 (1234ms) [a1b2c3d4]`
- Debug mode: `DEBUG=true` enables verbose logs + /api/debug + Swagger
- Unhandled errors return correlation ID for tracing

## Database Tables

| Table | Purpose | RLS |
|---|---|---|
| `users` | Profiles (auto-created on signup) | Users see own |
| `identifications` | Scan results + metadata | Users see own |
| `favorites` | Saved species | Users see own |
| `user_settings` | Preferences | Users see own |

## Agent Workflow

1. Read MEMORY.md (this file) — 30 seconds
2. Check LESSONS.md — before decisions
3. Run lint/typecheck — before commits
4. Update LESSONS.md — after discoveries

## Don't Waste Context On

- `.agents/` files unless doing architecture work
- HTML docs unless debugging rendering
- CI/CD workflows unless modifying them
- plant_care.py profiles unless changing care data

## Key Decisions

- **PlantNet** over Google Vision: free 500/day, plant-specialized
- **FastAPI** over Express: Python ecosystem, async, type safety
- **Supabase** over Firebase: RLS, PostgreSQL, open source
- **expo-secure-store** over AsyncStorage: security
- **Server-side API key**: never expose PlantNet key to client
