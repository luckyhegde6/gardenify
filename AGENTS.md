# Gardenify — Agent Instructions

> **Read this before writing any code.** This file is the primary context for all AI agents working on Gardenify.

## Project Overview

Gardenify is a plant identification mobile app. Users capture photos of plants, flowers, leaves, or fruits and receive species identification with confidence scores, common names, and taxonomy details. Built with Expo (React Native) for Android-first deployment, a Python FastAPI backend on Vercel, and Supabase for auth/database/storage. Plant identification powered by the PlantNet API (50,000+ species, free tier 500/day).

## Tech Stack

| Layer                | Technology            | Version                  |
| -------------------- | --------------------- | ------------------------ |
| Mobile               | Expo (React Native)   | SDK 55                   |
| Language (Mobile)    | TypeScript            | 5.9                      |
| Language (Backend)   | Python                | 3.12                     |
| Backend Framework    | FastAPI               | 0.117+                   |
| Database             | Supabase (PostgreSQL) | —                        |
| Auth                 | Supabase Auth         | —                        |
| Storage              | Supabase Storage      | —                        |
| Plant AI             | PlantNet API v2       | REST                     |
| Deployment (Mobile)  | EAS Build             | APK only (no Play Store) |
| Deployment (Backend) | Vercel Serverless     | —                        |
| CI/CD                | GitHub Actions        | —                        |

## Architecture (One Diagram)

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

## Git Workflow (PR-Only)

**All changes to `main` go through pull requests.** No direct commits allowed.

### Branch Naming

```
feat/short-description      # New features
bugfix/short-description    # Bug fixes
chore/short-description     # Maintenance, deps, config
hotfix/short-description    # Critical production fixes
```

### Flow

```bash
# Start work
git checkout main && git pull origin main
git checkout -b feat/my-feature

# Work, commit, push
git add -A && git commit -m "feat(api): add new endpoint"
git push origin feat/my-feature

# Create PR: main ← feat/my-feature
# Wait for CI green + approval
# Squash merge
```

### What Happens on Merge

| Event                                 | Action                                    |
| ------------------------------------- | ----------------------------------------- |
| PR merged to `main`                   | CI runs (lint + typecheck + Python tests) |
| `api/` changed on `main`              | Vercel deploys backend to production      |
| `supabase/` changed on `main`         | Supabase migrations run                   |
| Push to `feat/*`/`bugfix/*`/`chore/*` | OTA preview update published              |
| `v*` tag pushed                       | GitHub Release created, APK built         |

### Distribution

- **APK:** Built via EAS, distributed via [GitHub Releases](https://github.com/luckyhegde6/gardenify/releases)
- **GitHub Release:** Created automatically on `v*` tag push
- **No Play Store** — direct APK installation only

## File Structure

```
src/                    # Expo app (TypeScript)
  app/                  # expo-router file-based routes
    (auth)/             # Auth screens (login, register)
    (tabs)/             # Main tab screens
    identification/     # Result detail screens
  components/           # Reusable UI components
  hooks/                # Custom React hooks
  lib/                  # Utilities (supabase client, API client, types)
  constants/            # Theme, fonts, spacing

api/                    # Python backend (FastAPI)
  main.py               # Vercel entrypoint + landing page
  routes/               # API route handlers
  services/             # Business logic (PlantNet, Supabase, cache)
  models/               # Pydantic schemas
  data/                 # Local plant database + importers
  tests/                # Backend tests (73+ tests)

supabase/               # Database migrations and seeds
  migrations/           # SQL migration files

.agents/                # Agent configuration and guidelines
  orchestration.md      # Monitoring and coordination agents
  release-guidelines.md # Release process documentation
  linear-history.md     # Git flow and branching strategy
```

## How to Run Locally

```bash
# 1. Install dependencies
npm install

# 2. Start Expo dev server
npx expo start

# 3. Start Python backend (separate terminal)
cd api && pip install -r requirements.txt && vercel dev
```

## How to Test

```bash
# Lint
npm run lint

# Type check
npx tsc --noEmit

# Python tests
cd api && pytest

# Full CI locally
npx tsc --noEmit && cd api && ruff check . && cd api && pytest --tb=short
```

## Code Conventions

- **TypeScript**: Strict mode, no `any`, explicit return types on exported functions
- **Python**: Type hints on all functions, Pydantic for all request/response models, no bare `except`
- **React Native**: Functional components only, hooks for state management
- **Supabase**: Always use Row Level Security (RLS), parameterized queries, never expose service_role key
- **File naming**: Components = `kebab-case.tsx`, Routes = `kebab-case.tsx`, Python = `snake_case.py`
- **Imports**: React/React Native → Expo → Third-party → Internal (`@/`)

## What NOT to Do

- Do NOT commit directly to `main` — always use PRs
- Do NOT use `expo-cli` directly — use `npx expo` commands
- Do NOT install Expo packages with `npm install` — always use `npx expo install`
- Do NOT store tokens in AsyncStorage — use `expo-secure-storage`
- Do NOT hardcode API URLs — use environment variables with `EXPO_PUBLIC_` prefix
- Do NOT skip RLS policies on new database tables
- Do NOT add dependencies without checking if an existing dep covers the need
- Do NOT use `console.log` in production code — use structured logging
- Do NOT commit secrets, API keys, or tokens to git
- Do NOT publish OTA updates to production — only preview branch

## Expo v55 Notes

Read the exact versioned docs at https://docs.expo.dev/versions/v55.0.0/ before writing any code.

- Typed routes are enabled (`experiments.typedRoutes` in app.json)
- React Compiler is enabled (`experiments.reactCompiler` in app.json)
- Use `expo-router` for navigation (file-based routing in `src/app/`)
- Platform-specific files use `.ios.tsx`, `.android.tsx`, `.web.tsx` extensions

## Detailed Documentation

For comprehensive architecture, phase TODOs, security guidelines, and agentic workflows, see the `.agents/` directory:

- `.agents/architecture.md` — Full system architecture
- `.agents/phase-1-mvp.md` — MVP phase checklist
- `.agents/code-generation-guidelines.md` — Code generation rules
- `.agents/security-harness.md` — Security checklist
- `.agents/self-improvement-loop.md` — Agent learning protocol
- `.agents/agentic-handoff.md` — Cross-session handoff protocol
- `.agents/sessions.md` — Session log (update before each commit)
- `.agents/handoff-current.md` — Current state for next agent
- `.agents/primer.md` — Quick context for new agents
- `.agents/pre-commit-workflow.md` — Pre-commit checklist
- `.agents/security-checklist.md` — Detailed security checks
- `.agents/code-hygiene.md` — Code quality rules
- `.agents/linear-history.md` — Git flow and branching strategy
- `.agents/documentation-standards.md` — Documentation rules
- `.agents/product-development.md` — Product thinking and UX
- `.agents/release-guidelines.md` — Release process documentation
- `.agents/orchestration.md` — Monitoring and coordination agents

## Pre-Commit Workflow

Maintain `.agents/session-todos.md` from session start until the final commit: mark done/cancelled items before each commit, carry unfulfilled ones forward as new todos, and log any unfulfilled todo that is a confirmed bug into `BUGS.md`. Before EVERY commit, update these files:

```
□ .agents/session-todos.md — todos checked, unfulfilled carried forward, bugs logged
□ .agents/sessions.md — log what was done
□ .agents/handoff-current.md — next steps for next agent
□ MEMORY.md — current state + what's not done
□ LESSONS.md — any new discoveries
□ PRD.md — check off completed items
□ .agents/primer.md — quick context for new agents
□ BUGS.md — log any bugs found or fixed
```

## External References

- Expo SDK 55 Docs: https://docs.expo.dev/versions/v55.0.0/
- Supabase + Expo: https://docs.expo.dev/guides/using-supabase/
- PlantNet API: https://my.plantnet.org/doc/getting-started/introduction
- Expo MCP Server: https://docs.expo.dev/mcp/
- agent-device (testing): https://oss.callstack.com/agent-device/
