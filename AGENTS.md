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

### Git Hooks (enforced gate)

Repository ships versioned hooks in `.githooks/` that block **direct commits on `main`/`master`** and **direct pushes to `main`/`master`**. Every fresh clone must enable them once:

```bash
git config core.hooksPath .githooks
```

- `.githooks/pre-commit` — refuses to commit when `HEAD` is on `main`/`master`.
- `.githooks/pre-push` — refuses to push refs targeting `main`/`master` on any remote.

Never bypass with `git commit --no-verify` (or `-f` on push) unless you intentionally override **both** the gate and GitHub push protection. Secrets stay only on gitignored files (`.env.local`, `creds.json`, `.agents/handoff-current.md`). Before pushing, verify no tokens are staged: `git grep -nE 'sbp_[a-f0-9]{20,}'`.

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

Also see the `docs/` directory for developer-facing guides:

- `docs/security-architecture.md` — Trust boundary, RLS, and auth decisions
- `docs/supabase-integration.md` — Supabase setup and migrations
- `docs/vercel-deployment.md` — Backend deployment

## Agent Memory, Handoff & Self-Improvement

This is the **operating model** for agents: how state is persisted across sessions, how a new agent reconstructs context cheaply, how mistakes become lessons, and how the system prevents hallucinated history and keeps token usage low.

### 1. Memory Layout (what lives where)

| File                                    | Tracked in git? | Contents                                                                                                 | Purpose                                                   |
| --------------------------------------- | --------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `AGENTS.md`                             | ✅              | Rules, workflow, this model                                                                              | Permanent conventions. Read once, follow always.          |
| `MEMORY.md`                             | ✅              | **Index only** → `.agents/memory/*.md`                                                                   | Entry point for project state.                            |
| `.agents/memory/project-overview.md`    | ✅              | Identity, key facts, architecture                                                                        | 10-second context.                                        |
| `.agents/memory/current-state.md`       | ✅              | ✅ done / ❌ not-done, last major refactor                                                               | What changed and what's left.                             |
| `.agents/memory/app-structure.md`       | ✅              | File tree, auth guard, run commands                                                                      | Where code lives + how to run.                            |
| `.agents/memory/operations.md`          | ✅              | Auth security, release status, verification checklists                                                   | Ops-specific state.                                       |
| `LESSONS.md`                            | ✅              | **Index only** → `.agents/lessons/*.md`                                                                  | Entry point for learned lessons.                          |
| `.agents/lessons/*.md`                  | ✅              | Category files (backend, mobile, database, ci-cd, git, windows-dev, testing, architecture, docs-process) | `YYYY-MM-DD`-stamped mistakes → fix → prevention pattern. |
| `.agents/session-todos.md`              | ✅              | Current session todos + carried-forward                                                                  | Live task tracking.                                       |
| `.agents/sessions.md`                   | ✅              | Running chronological session log                                                                        | Audit trail of every session.                             |
| `.agents/sessions/YYYY-MM-DD-<hash>.md` | ✅              | **Archives** of completed sessions                                                                       | Historical detail, removed from session-todos.            |
| `.agents/handoff-current.md`            | ❌ (gitignored) | Live state, env, creds refs, emulator coords                                                             | Volatile "resume here" note. Never committed.             |
| `.agents/primer.md`                     | ✅              | Quick-start table for new agents                                                                         | Fast onboarding.                                          |

**Read order on session start:** `.agents/primer.md` → `MEMORY.md` index → `.agents/memory/current-state.md` → `.agents/handoff-current.md` → recent `git log --oneline -10` → `.agents/session-todos.md`. That is ~10 files of small, targeted reads instead of one giant blob — do NOT dump whole archives or the full `sessions.md`.

### 2. Session Handoff & Continuity

- **Handoff = files, not prose.** Do not trust your own summary of the session; before finishing, update `.agents/sessions.md` (log entry) and `.agents/handoff-current.md` (state + next steps) and mark/carry `.agents/session-todos.md`. The next agent resumes from these, never from conversation memory.
- **`.agents/handoff-current.md` is the live resume point.** It is gitignored on purpose: it holds mutable state, environment references and ephemeral details (e.g. emulator tap coordinates, test credentials location) that should never be committed. Treat it as scratchpad state, not permanent doc.
- **Session archives.** When a session completes, its todos move to `.agents/sessions/YYYY-MM-DD-<commit-hash>.md` and are removed from `.agents/session-todos.md`, keeping the todos file short. The filename encodes the date + the commit the work landed in, so the archive is traceable back to code.
- **Todos are either done, carried forward, or bug-logged.** Before each commit: mark `[x]`/`[~]` on every item, carry unfulfilled ones into the next session's list verbatim, and if an unfulfilled todo is a _confirmed bug_, also log it in `BUGS.md`. Never silently drop a todo.

### 3. Self-Learning (avoid repeating mistakes)

- Every non-obvious discovery, bug fix, or gotcha gets a `YYYY-MM-DD`-stamped entry in the matching `.agents/lessons/<category>.md`, plus a one-line pointer in the `LESSONS.md` index. Format: **Context → Issue → Fix/Pattern → Applies to → Severity → Status**.
- After the entry, ask "does this deserve a rule in `AGENTS.md` / `CLAUDE.md`, or a regression test?" — a lesson only sticks if it changes future behavior, not just the doc.
- **Failure analysis loop** (from `.agents/self-improvement-loop.md`): Root cause → Why wasn't it caught? → Fix → Prevent (test/rule/check) → Document. The last step is mandatory, not optional.

### 4. Self-Healing (detect + recover from broken state)

- **Verify before you claim.** After any change, run the real checks: `npx tsc --noEmit`, `npm run lint`, `cd api && pytest`, `npx jest`, and the e2e suite. A "works" claim without a passing check is a hallucination risk.
- **Trust the repo over memory.** If your memory of a file's contents disagrees with the file, the file wins — re-read it. Never reconstruct code or state from recollection.
- **Service-level self-healing:** backend/EAS/dev services run detached on Windows; use the debug agent to verify `curl http://localhost:8000/api/health` before relying on them. If a release/build is stuck, check the actual CI/EAS status (`gh run view`, `eas build:list`) rather than assuming.
- **Post-merge validation** (from `.agents/self-improvement-loop.md`): after merging, confirm EAS build, Vercel deploy, migrations and `/api/health` actually succeeded — do not infer success from the merge event alone.

### 5. Avoiding Hallucination

- **Never invent history.** Every claim about what was done must trace to: a git commit, a tracked doc, a passing test, or a verified live check (e.g. `curl /api/health`). If it isn't in git/docs/tests, phrase it as a hypothesis to verify, not a fact.
- **Never invent facts/URLs/versions.** Check the repo (commit hashes, `app.json`, `api/config.py`) or query the live system before stating a version, endpoint, or number.
- **Never invent file paths or API shapes.** Grep/read the actual code first; mirror existing patterns.
- **Secrets hygiene prevents false state:** `handoff-current.md` and `.env.local`/`creds.json` are gitignored; never commit them, never echo real keys into docs. Before pushing: `git grep -nE 'sbp_[a-f0-9]{20,}'`.

### 6. Token Efficiency

- **Small, targeted reads beat big dumps.** Index files (`MEMORY.md`, `LESSONS.md`) exist so you read only the category you need — load `.agents/lessons/backend.md`, not the whole history. Read file slices by offset/limit; grep before glob; glob before reading entire directories.
- **Keep docs short by construction.** `session-todos.md` = only current session + carried-forward. `sessions/` archives absorb history. Each lesson is one tight block. If a memory/lesson file grows past ~200 lines, split it.
- **Don't re-derive what's documented.** If `.agents/memory/app-structure.md` already lists the file tree, don't re-run directory scans to learn it.
- **State before you act.** Before a multi-file change, state your assumptions and plan in 2–3 lines so work (and token spend) doesn't go down a wrong path. For complex features, delegate planning/review to subagents (planner, code-reviewer, security-reviewer) which run in their own context.

## Pre-Commit Workflow

Maintain `.agents/session-todos.md` from session start until the final commit: mark done/cancelled items before each commit, carry unfulfilled ones forward as new todos, and log any unfulfilled todo that is a confirmed bug into `BUGS.md`. Before EVERY commit, update these files:

```
□ .agents/session-todos.md — todos checked, unfulfilled carried forward, bugs logged
□ .agents/sessions.md — log what was done
□ .agents/handoff-current.md — next steps for next agent
□ MEMORY.md — current state + what's not done (index; details in .agents/memory/)
□ LESSONS.md — any new discoveries (index; details in .agents/lessons/)
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
