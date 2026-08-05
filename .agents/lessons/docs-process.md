# Lessons — Documentation & Agent Process

## 2026-08-04: Landing/Onboarding HTML Can Drift After a Refactor — Grep for the Removed Technology

**Context:** After the SQLite→Supabase refactor (2026-08-02), the public `/` and `/onboarding` pages still claimed "Supabase + SQLite", "local SQLite database", and an offline SQLite fallback — all removed. Code was fixed, but the marketing/architecture pages still described the old design.

**Lesson:** When removing a technology, the removal is only complete when **user-facing docs are in sync**. `grep -ri sqlite .` surfaced `api/landing_page.py` and `api/onboarding_page.py` still advertising SQLite.

**Pattern:** After any backend refactor, run `grep -rniE 'sqlite|local database|offline' api/` to catch stale copy in HTML/doc strings.

**Files aligned:** `api/landing_page.py` (Tech Stack + Instant Matching card), `api/onboarding_page.py` (component breakdown, identify steps 4–5, sequence participant `Supabase Species Store`, Fallback & Matching, tech-stack cards). Verified: `grep -i sqlite` returns nothing; `ruff` clean.

## Not Updating Session Files Before Commit (anti-pattern)

**Issue:** Made changes but didn't update session tracking, memory, handoffs, or PRD before committing.

**Fix:** Pre-commit workflow:

1. Update `.agents/sessions.md` with what was done
2. Update `.agents/handoff-current.md` with next steps
3. Update `MEMORY.md` index + `.agents/memory/current-state.md` with current state
4. Update `LESSONS.md` index + `.agents/lessons/<category>.md` with discoveries
5. Update `PRD.md` with completed items

**Pattern:** "If it's not documented, it didn't happen. If it's not tracked, it won't be done." Treat docs as first-class citizens, not afterthoughts.

## Session Archive Convention (2026-08-06)

- Completed sessions are archived to `.agents/sessions/YYYY-MM-DD-<commit-hash>.md` and removed from `.agents/session-todos.md`, keeping the todos file short and crisp.
- LESSONS are split by category under `.agents/lessons/` (architecture, backend, database, mobile, ci-cd, git, windows-dev, testing) instead of one giant `LESSONS.md`.
- MEMORY is split by section under `.agents/memory/` instead of one large file.

## Hardcoded Secrets in Config Files (anti-pattern)

**Issue:** `.env.example` and `docker-compose.yml` had placeholder values that could be mistaken for real secrets.

**Fix:**

1. Use obvious placeholders: `PLANTNET_API_KEY=your_key_here`
2. Add `.gitleaks.toml` to exclude `.env.example` and `.env.test`
3. Add pre-commit hooks: `gitleaks protect --staged`, `detect-private-key`
4. Never put real keys in any file except `.env` (gitignored)

**Pattern:** Treat every file as if it will be committed. Use `git diff --cached` to review before committing.

## Not Documenting Environment Configuration (anti-pattern)

**Fix:**

1. Create `scripts/setup.sh` and `scripts/setup.ps1` with interactive menus
2. Add `ENVIRONMENT=local|production` to `config.py`
3. Add `USE_REMOTE=true` flag
4. Create `scripts/seed.sh` with test data

**Pattern:** Developer experience is a feature. If it's hard to start, it's hard to contribute.
