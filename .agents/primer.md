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

| Component | Status | Notes |
|---|---|---|
| Backend API | ✅ Done | FastAPI, `/api/identify`, `/api/health`, `/api/debug` |
| PlantNet Integration | ✅ Done | Species + disease detection |
| Plant Care | ✅ Done | Taxonomy-based care profiles |
| Caching | ✅ Done | SHA-256 hash, 1hr TTL |
| Metadata | ✅ Done | EXIF, GPS, dimensions |
| Logging | ✅ Done | Correlation IDs, request timing |
| Supabase Schema | ✅ Done | Users, identifications, favorites, settings + RLS |
| CI/CD | ✅ Done | GitHub Actions (lint, test, build, deploy) |
| Docs | ✅ Done | HTML + Mermaid (3 pages) |
| Local Dev | ✅ Done | docker-compose, setup scripts |
| Agent Docs | ✅ Done | AGENTS.md, CLAUDE.md, LESSONS.md, MEMORY.md |
| Pre-commit | ✅ Done | gitleaks, detect-secrets |
| Mobile UI | ❌ Not started | Expo screens |
| Credentials | ❌ Blocked | Need from user |
| Vercel Deploy | ❌ Not started | — |

## What's Next

1. Fix remaining CI (verify tsc + ruff pass)
2. Add `ENVIRONMENT=local|production` + `USE_REMOTE=true` to config
3. Create seed scripts for testing
4. Add testing framework (TDD, e2e, integration)
5. Create PRD.md and BUGS.md
6. Add LSP/MCP rules and AI guardrails

## Key Files

| File | Purpose |
|---|---|
| `api/main.py` | FastAPI app + logging |
| `api/config.py` | Settings from env vars |
| `api/routes/identify.py` | POST /api/identify |
| `api/routes/health.py` | Health + debug |
| `api/services/plantnet.py` | PlantNet client |
| `api/services/plant_care.py` | Care profiles |
| `api/services/cache.py` | Hashing, caching, metadata |
| `api/models/schemas.py` | Pydantic models |
| `api/ruff.toml` | Python linting config |
| `docker-compose.yml` | Local Supabase stack |
| `.env.example` | Env vars template |
| `MEMORY.md` | Quick context for agents |
| `LESSONS.md` | Mistakes and solutions |

## Environment Variables

```bash
# Local dev (defaults work)
cp .env.example .env

# Production — supply these
PLANTNET_API_KEY=your_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
```

## Run Commands

```bash
# Start everything
make dev

# Lint + typecheck
make lint && make typecheck

# Python tests
make test-python

# Python lint
make lint-python
```

## Common Mistakes to Avoid

1. **Don't leave example/ in repo** — breaks TypeScript CI
2. **Don't skip RLS** — every table needs row-level security
3. **Don't commit secrets** — use .env, gitleaks catches them
4. **Don't skip pre-commit** — run `make precommit-run` before push
5. **Don't use bare except** — use specific exceptions (ruff BLE001)

## If You're Stuck

1. Read `LESSONS.md` — most problems are documented
2. Check `git log --oneline -5` — see what changed recently
3. Run `make test-python` — verify backend works
4. Run `npx tsc --noEmit` — catch TypeScript errors
5. Check `.agents/handoff-current.md` — latest state
