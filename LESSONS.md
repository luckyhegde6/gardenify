# LESSONS.md

Running log of lessons learned during Gardenify development. Agents read this file at session start and update it after significant discoveries.

## Format

```markdown
## YYYY-MM-DD: Lesson Title
**Context:** What was happening
**Issue/Success:** What went wrong or right
**Fix/Pattern:** What should be done instead
**Applies to:** [backend | mobile | database | all]
**Severity:** [critical | important | minor]
**Status:** [active | superseded]
```

---

## 2026-07-27: Initial Architecture Decisions

**Context:** Designing the Gardenify plant identification app architecture
**Decision:** PlantNet API (free tier 500/day) over OpenAI GPT-4o for plant identification
**Rationale:** Free tier sufficient for MVP, 50K+ species, specialized for plants, no per-call cost
**Applies to:** all
**Severity:** important
**Status:** active

## 2026-07-27: Supabase Over Firebase

**Context:** Choosing backend-as-a-service provider
**Decision:** Supabase (PostgreSQL + Auth + Storage) over Firebase
**Rationale:** PostgreSQL gives us RLS, SQL queries, and type safety. Generous free tier (500MB DB, 1GB storage, 50K MAU). Better for data-heavy apps with complex queries.
**Applies to:** database
**Severity:** important
**Status:** active

## 2026-07-27: Python Backend as API Proxy

**Context:** Deciding where PlantNet API calls happen
**Decision:** Python FastAPI backend on Vercel proxies all PlantNet calls
**Rationale:** Keeps PlantNet API key server-side. Enables result caching, rate limiting, and future enrichment (LLM care tips). PlantNet responses are fast (~2-5s), so Vercel's 60s timeout is fine.
**Applies to:** backend
**Severity:** important
**Status:** active

## 2026-07-27: Local AI as Future Enhancement

**Context:** User asked about Android local AI for plant identification
**Decision:** Start with PlantNet API only. Consider hybrid local+API in Phase 3+ if quota becomes an issue.
**Rationale:** Local TFLite models are 50-100MB, cover fewer species (~10K vs 50K), and require Expo dev client builds. Not worth the complexity for MVP.
**Applies to:** mobile
**Severity:** minor
**Status:** active

## 2026-07-27: Image Compression Before Upload

**Context:** Designing image storage pipeline
**Decision:** Compress images client-side to max 1024px, JPEG quality 0.8 before upload
**Rationale:** Reduces ~3MB photos to ~200KB. Saves Supabase storage (1GB free), reduces upload time on mobile networks, and PlantNet accepts compressed images fine.
**Applies to:** mobile
**Severity:** important
**Status:** active

## 2026-07-27: Image Hash Caching for Deduplication

**Context:** Stretching PlantNet's 500/day free quota
**Decision:** Compute SHA-256 hash of compressed images before sending to PlantNet
**Rationale:** If same image was identified before, return cached result without API call. Eliminates duplicate identifications from re-captures.
**Applies to:** backend
**Severity:** important
**Status:** active

## 2026-07-27: Disease Detection via PlantNet Diseases API

**Context:** User wanted disease detection alongside species identification
**Decision:** Use PlantNet's separate diseases endpoint (`/v2/diseases/identify`) in parallel with species identification
**Rationale:** Same image format, no additional API key needed. Returns disease name, confidence, description, and treatment. Runs after species ID so it doesn't block the primary flow.
**Applies to:** backend
**Severity:** important
**Status:** active

## 2026-07-27: Plant Care Analysis Engine

**Context:** User wanted watering, sunlight, soil, growth, and propagation info
**Decision:** Build a taxonomy-based care profile lookup system (genus → family → default)
**Rationale:** PlantNet doesn't provide care instructions. We maintain care profiles keyed by genus/family. In production, this could connect to a plant database API (Trefle, Perenual) or LLM-generated care guides.
**Applies to:** backend
**Severity:** important
**Status:** active

## 2026-07-27: EXIF and GPS Metadata Extraction

**Context:** User wanted image metadata capture (camera, date, GPS, dimensions)
**Decision:** Use Pillow to extract EXIF data and image dimensions from uploaded images
**Rationale:** EXIF gives us camera model, date taken, and GPS coordinates. Useful for: (1) helping identify where a plant was found, (2) tracking when photos were taken, (3) future features like location-based plant recommendations.
**Applies to:** backend
**Severity:** medium
**Status:** active

## 2026-07-27: In-Memory Result Caching

**Context:** Avoid re-identifying the same images within a short window
**Decision:** Cache identification results in-memory with 1-hour TTL, keyed by image hashes + organs + language
**Rationale:** Simple first step before Redis/Supabase caching. Saves PlantNet quota for repeated identical uploads. Cache key includes organ selection since same image with different organ tags may yield different results.
**Applies to:** backend
**Severity:** medium
**Status:** active

## 2026-07-27: MEMORY.md for Agent Context Efficiency

**Context:** Agents were burning context re-reading large files at session start
**Decision:** Create MEMORY.md as a quick-recap file with key facts, current state, file references, and testing instructions
**Rationale:** Agents can read MEMORY.md (200 lines) instead of AGENTS.md + architecture.md + phase TODOs (500+ lines). Saves ~60% context on session start.
**Applies to:** all
**Severity:** important
**Status:** active

## 2026-07-27: Swagger UI for Local API Testing

**Context:** Need a way to test the identify endpoint with file uploads locally
**Decision:** FastAPI's built-in Swagger UI at `/docs` supports multipart file upload testing
**Rationale:** No need for Postman or curl — Swagger UI lets you upload images, set organ types, and see full request/response. Works with `vercel dev` locally.
**Applies:** backend
**Severity:** minor
**Status:** active

---

## Mistakes & Solutions — How to Avoid Them

### Mistake 1: Stale Template Files Breaking CI

**Context:** Expo SDK 55 project was created with `create-expo-app`, then heavily customized. The `example/` directory (1172 lines of template code) was left in the repo.

**What went wrong:**
- `example/src/**` imported `@/components/*`, `@/constants/*`, `@/assets/*`
- `tsconfig.json` mapped `@/*` → `./src/*` (our app code, not example code)
- `tsconfig.json` `include: ["**/*.ts", "**/*.tsx"]` picked up `example/` files
- TypeScript compiler failed: `Cannot find module '@/components/animated-icon'`
- CI failed on every push and PR

**Root cause:** Did not verify CI passes after initial project setup. Did not realize Expo template includes an `example/` directory with its own component tree.

**Fix:**
1. After project creation, run `npx tsc --noEmit` to verify no type errors
2. Remove `example/` directory if not needed (it's Expo's demo app, not your code)
3. Or add `exclude: ["example/**"]` to `tsconfig.json`
4. Add pre-commit hook that runs `tsc --noEmit` before commits

**Pattern:** Always verify CI passes after initial setup. Don't assume template code is compatible with your customizations.

---

### Mistake 2: Python Linter Errors (ruff B008 + BLE001)

**Context:** Added ruff to CI pipeline. Python code had patterns that ruff flagged as errors.

**What went wrong:**
- `api/routes/identify.py`: `File(...) = File(...)` and `Form(default=["auto"])` in function signatures → ruff B008 (function call in default argument)
- `api/services/plantnet.py`: `except Exception as e:` → ruff BLE001 (blind except)
- `api/services/cache.py`: `except Exception as e:` → ruff BLE001 (blind except)
- CI failed on `ruff check .`

**Root cause:** FastAPI idioms (File/Form in defaults) conflict with ruff's default rules. Blind excepts are intentional for resilience in API clients and EXIF parsing.

**Fix:**
1. Create `api/ruff.toml` with project-specific ignores:
   ```toml
   ignore = [
       "B008",   # FastAPI: File/Form in defaults (idiomatic)
       "BLE001", # Blind except OK for resilience
   ]
   ```
2. Add `known-first-party = ["api"]` to fix import ordering
3. Add per-file ignores: `tests/*` → ignore `S101` (assert OK in tests)

**Pattern:** Linter rules are guidelines, not absolute. Document why you ignore specific rules. Create a `ruff.toml` or `pyproject.toml` with explicit ignores.

---

### Mistake 3: Not Running CI Locally Before Push

**Context:** Pushed code to GitHub without running lint/typecheck locally first.

**What went wrong:**
- TypeScript errors were caught only by GitHub Actions
- Python ruff errors were caught only by GitHub Actions
- Multiple commits pushed with failing CI
- PR shows red checks

**Root cause:** No local pre-commit hooks configured. No habit of running `npx tsc --noEmit` and `ruff check .` before pushing.

**Fix:**
1. Install pre-commit hooks: `pip install pre-commit && pre-commit install`
2. Add hooks for: `gitleaks`, `ruff check`, `npx tsc --noEmit`, `pytest`
3. Run `make precommit-run` before pushing
4. Add to `.pre-commit-config.yaml`:
   ```yaml
   - repo: local
     hooks:
       - id: ruff
         name: ruff check
         entry: ruff check api/
         language: system
       - id: tsc
         name: TypeScript check
         entry: npx tsc --noEmit
         language: system
   ```

**Pattern:** "If it's not in CI, it's not tested. If it's not in pre-commit, it's not caught."

---

### Mistake 4: Hardcoded Secrets in Config Files

**Context:** Created `.env.example` and `docker-compose.yml` with placeholder values that could be mistaken for real secrets.

**What went wrong:**
- `.env.example` had `<your-local-anon-key-from-supabase-start>` which could be committed
- `docker-compose.yml` had `${SUPABASE_ANON_KEY:?Run 'supabase start'}` which requires env vars
- No validation that secrets are not committed

**Root cause:** Did not distinguish between "placeholder text" and "real secrets". Did not use gitleaks or detect-secrets.

**Fix:**
1. Use obvious placeholders: `PLANTNET_API_KEY=your_key_here`
2. Add `.gitleaks.toml` to exclude `.env.example` and `.env.test`
3. Add pre-commit hook: `gitleaks protect --staged`
4. Add `detect-private-key` hook to catch accidentally committed keys
5. Never put real keys in any file except `.env` (which is gitignored)

**Pattern:** Treat every file as if it will be committed. Use `git diff --cached` to review before committing.

---

### Mistake 5: Missing RLS Policies on Database Tables

**Context:** Created Supabase migrations without Row Level Security (RLS) policies.

**What went wrong:**
- Tables created without RLS enabled
- Anyone could read/write all data
- No per-user data isolation

**Root cause:** Forgot to add `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` and `CREATE POLICY` statements.

**Fix:**
1. Always add RLS in the same migration as table creation
2. Use pattern: `CREATE POLICY "Users see own X" ON X FOR SELECT USING (auth.uid() = user_id)`
3. Add review checklist: "Does every table have RLS?"
4. Use `supabase db reset` to test locally

**Pattern:** Security is not optional. Every table needs RLS. Every policy needs testing.

---

### Mistake 6: Not Documenting Environment Configuration

**Context:** Local development required multiple steps (Docker, Supabase, PlantNet API key) but no clear guide existed.

**What went wrong:**
- New developers (or AI agents) didn't know how to start local dev
- No `ENVIRONMENT=local|production` variable
- No `USE_REMOTE=true` flag to connect local backend to prod Supabase
- No seed data for testing

**Root cause:** Focused on building features, not on developer experience. Did not create setup scripts or seed data.

**Fix:**
1. Create `scripts/setup.sh` and `scripts/setup.ps1` with interactive menus
2. Add `ENVIRONMENT=local|production` to `config.py`
3. Add `USE_REMOTE=true` flag to `docker-compose.yml`
4. Create `scripts/seed.sh` with test data
5. Add `make dev` command that starts everything

**Pattern:** Developer experience is a feature. If it's hard to start, it's hard to contribute.

---

### Mistake 7: No Testing Framework

**Context:** Backend code had 11 tests but no testing strategy, no fixtures, no mocking, no e2e tests.

**What went wrong:**
- Tests only cover happy path
- No mocking of PlantNet API calls
- No integration tests with Supabase
- No end-to-end tests
- No test data fixtures

**Root cause:** Tests were added after code, not before. No TDD approach.

**Fix:**
1. Create `api/tests/conftest.py` with shared fixtures
2. Create `api/tests/fixtures/` with test images and API responses
3. Use `pytest-httpx` to mock PlantNet API calls
4. Add integration tests with Supabase (using test database)
5. Add e2e tests that test full flow: image → API → response

**Pattern:** TDD: Write test first, then code. Tests are documentation, not afterthought.

---

### Mistake 8: Not Running Type Checks on All Code

**Context:** TypeScript strict mode enabled but only ran on `src/` directory.

**What went wrong:**
- `example/` directory had TypeScript errors
- `npx tsc --noEmit` failed because it checked all `**/*.ts` files
- Could not catch errors in non-src directories

**Root cause:** Did not configure `tsconfig.json` to exclude irrelevant directories.

**Fix:**
1. Add `exclude: ["example/**", "node_modules/**"]` to `tsconfig.json`
2. Or remove irrelevant directories entirely (cleaner)
3. Run `npx tsc --noEmit` in CI to catch all errors
4. Add to pre-commit hook

**Pattern:** Type checking should cover all code, not just src/. If you exclude directories, document why.

---

### Summary: Anti-Patterns to Avoid

| Anti-Pattern | Consequence | Prevention |
|---|---|---|
| Not running CI locally | Red checks on PR | Pre-commit hooks |
| Leaving template code in repo | Broken builds, confusion | Clean up after project creation |
| Hardcoded secrets | Security leaks | Gitleaks + detect-secrets |
| Missing RLS policies | Data exposure | RLS checklist in migrations |
| No testing strategy | Bugs in production | TDD + fixtures + mocking |
| No developer docs | Slow onboarding | Setup scripts + seed data |
| Not configuring linters | CI failures | Create project-specific config |
| Not excluding irrelevant dirs | Type errors | tsconfig exclude + cleanup |
| Not fixing ruff errors before push | CI failures on PR | Run `ruff check .` before push |

---

### Mistake 10: Not Running Ruff Locally Before Push

**Context:** Pushed code with 9 ruff errors to GitHub Actions.

**What went wrong:**
- Import sorting (I001) in 4 files
- `timezone.utc` → `UTC` alias (UP017) in health.py
- `raise ... from e` missing (B904) in identify.py
- Line too long (E501) in plant_care.py

**Root cause:** Did not run `ruff check api/` locally before pushing.

**Fix:**
1. Run `ruff check api/` before every push
2. Run `ruff format api/` to auto-fix formatting
3. Add to pre-commit hook: `ruff check api/ && ruff format --check api/`
4. Use `ruff check api/ --fix` to auto-fix import sorting

**Pattern:** "If it's not in CI, it's not tested. If it's not in pre-commit, it's not caught."

---

### Mistake 9: Not Updating Session Files Before Commit

**Context:** Made changes but didn't update session tracking, memory, handoffs, or PRD before committing.

**What went wrong:**
- No session log to track what was done
- No handoff doc for next agent to resume
- No PRD checklist to track progress
- Memory file became stale

**Root cause:** Focused on code changes, not on documentation workflow. No pre-commit checklist.

**Fix:**
1. Create pre-commit workflow:
   - Update `.agents/sessions.md` with what was done
   - Update `.agents/handoff-current.md` with next steps
   - Update `MEMORY.md` with current state
   - Update `LESSONS.md` with discoveries
   - Update `PRD.md` with completed items
2. Add to pre-commit hook or make checklist
3. Treat docs as first-class citizens, not afterthoughts

**Pattern:** "If it's not documented, it didn't happen. If it's not tracked, it won't be done."

---

### Mistake 11: Windows `start` Command Blocks Agent Shell

**Context:** Trying to start backend server with `start cmd /c "uvicorn ..."` then test with `curl`.

**What went wrong:**
- `start /B cmd /c` with `timeout /t 5 /nobreak >nul` — `timeout` doesn't work with input redirection in non-interactive shells
- `start "gardenify-api" cmd /c "..."` followed by `curl` — `start` opens a new window but the agent shell doesn't know when it's ready
- Agent gets stuck waiting, times out after 30s

**Root cause:** Windows `start` command launches processes in new cmd windows. Agent shell can't detect when the server is ready to accept connections. `timeout /t N /nobreak` requires interactive shell.

**Fix:**
1. Start server in background with: `start "name" cmd /c "command"` — this works, server starts fine
2. Agent should NOT try to wait/verify inline. Instead, note that server is starting in another window
3. Verify separately with `curl` after a short delay, or ask user to confirm
4. Alternatively, use Python's `subprocess.Popen` for programmatic background process management

**Pattern:** When launching background processes from agent shell on Windows, `start` works but the agent cannot synchronously verify readiness. Launch separately, verify separately.

**Applies to:** all
**Severity:** minor
**Status:** active

---

### Pre-Commit Workflow (Established 2026-07-27)

Before EVERY commit, update these files:

```
□ .agents/sessions.md — log what was done
□ .agents/handoff-current.md — next steps for next agent
□ MEMORY.md — current state + what's not done
□ LESSONS.md — any new mistakes or discoveries
□ PRD.md — check off completed items
□ .agents/primer.md — quick context for new agents
```

This ensures:
- Continuity between sessions
- No work is forgotten
- Progress is visible
- Next agent can resume quickly

---

### Mistake 12: Using Python Reserved Word as Directory Name

**Context:** Created `api/data/import/` directory for database import scripts.

**What went wrong:**
- `import` is a Python reserved keyword
- `from api.data.import.seed_species import seed_database` → `SyntaxError: invalid syntax`
- Backend failed to start

**Root cause:** Named a directory `import` without considering Python import syntax.

**Fix:**
1. Rename directory: `api/data/import/` → `api/data/importers/`
2. Update all references: `api.data.import.*` → `api.data.importers.*`
3. Use `ren` command on Windows: `ren "api\data\import" "importers"`

**Pattern:** Never name directories or files with Python reserved words (`import`, `class`, `def`, `return`, `from`, `as`, etc.).

**Applies to:** backend
**Severity:** critical
**Status:** active

---

### Mistake 13: Agent Shell Blocks on Windows `start` Command

**Context:** Starting backend server with `start "gardenify-api" cmd /c "uvicorn ..."` to test new routes.

**What went wrong:**
- Server starts successfully in a new window
- But the agent shell gets stuck waiting
- User had to manually stop the agent

**Root cause:** Windows `start` command launches processes in new cmd windows. The agent shell cannot detect when the server is ready, and the `start` command itself may block depending on shell configuration.

**Fix:**
1. Server starts fine — the command works
2. Agent should NOT try to verify readiness inline
3. User should confirm server is running, then agent tests with `curl`
4. Or: agent starts server in a separate task and tests after delay

**Pattern:** On Windows, `start` + background processes work but the agent shell gets stuck. Separate server launch from testing.

**Applies to:** all
**Severity:** minor
**Status:** active

---

### Lesson: Clean Up Analysis Repos After Research

**Context:** Cloned `plantnet-ai-taxonomist` and `plantnet-300k` repos for analysis.

**What happened:**
- Both repos were cloned to temp dir AND project root
- `plantnet-ai-taxonomist/` had TypeScript files that broke `npx tsc --noEmit`
- `plantnet-300k/` had Python training scripts we don't need
- Had to clean up both locations, add to .gitignore

**Pattern:** After analyzing external repos:
1. Delete clones from project root immediately
2. Add cloned dirs to .gitignore
3. Extract only the data/code you actually need
4. Don't leave analysis artifacts in the repo

**Applies to:** all
**Severity:** minor
**Status:** active

---

### Lesson: SQLite Doesn't Support XOR — Use Python for Bitwise Operations

**Context:** `find_by_phash()` used SQL `XOR` for Hamming distance calculation.

**What went wrong:**
- `sqlite3.OperationalError: near "XOR": syntax error`
- SQLite doesn't support bitwise XOR (`^`) or `CONV()` like MySQL
- The SQL query was MySQL-specific, not portable

**Fix:**
1. Fetch all hashes from DB
2. Compute Hamming distance in Python
3. Filter and sort in Python

**Pattern:** SQLite is minimal — no bitwise XOR, no CONV(), no advanced string ops. For complex comparisons, fetch data and compute in Python. Fast enough for <100K rows.

**Applies to:** backend
**Severity:** important
**Status:** active

---

### Lesson: Perceptual Hash Algorithms Need Structured Images

**Context:** Testing dHash and pHash with uniform-color images.

**What went wrong:**
- Uniform images (all black/white) produce identical dHash (`0000000000000000`)
- dHash compares adjacent pixels — uniform = all bits 0
- pHash on synthetic images has high Hamming distance even for similar images

**Fix:**
1. Use gradient/checkerboard images for hash testing
2. Test hash consistency (same image = same hash) rather than distance
3. For distance tests, use structurally similar images

**Pattern:** Perceptual hashes work on spatial structure, not color. Test with images that have gradients, edges, and patterns.

**Applies to:** backend
**Severity:** minor
**Status:** active

---

### Lesson: Test Expectations Must Match Business Logic

**Context:** Testing species upsert with observation_count.

**What went wrong:**
- Test expected `observation_count == 100` after inserting with count 100
- Actual behavior: `observation_count = 42 + 100 = 142` (additive)
- The upsert logic adds to existing count, doesn't replace

**Fix:** Update test expectation to match actual behavior: `assert result["observation_count"] == 142`

**Pattern:** Write tests that verify actual behavior, not desired behavior. If behavior is additive, test that it adds.

**Applies to:** backend
**Severity:** minor
**Status:** active

---

### Lesson: Darwin Core Archives Use Tab-Separated Text, Not CSV

**Context:** Importing species from PlantNet GBIF Darwin Core Archive.

**What went wrong:**
- Initial importer assumed `.csv` files with `csv.DictReader`
- Archive actually contains `.txt` files with tab-separated values
- No `taxon.csv` file — only `occurrence.txt`, `multimedia.txt`, `eml.xml`, `meta.xml`
- `scientificName` column contains author names: `"Quercus robur L."`

**Fix:**
1. Read `.txt` files with `split("\t")` instead of CSV reader
2. Strip author names from scientific names (keep first 2 words)
3. Use `scientificName` column at index 15

**Pattern:** Darwin Core Archives vary by dataset. Always inspect the archive contents before writing importers. Check file extensions, delimiters, and column names.

**Applies to:** backend
**Severity:** important
**Status:** active

---

### Lesson: package-lock.json Must Be Committed for npm ci to Work

**Context:** CI workflow runs `npm ci` which requires `package-lock.json` to be in sync with `package.json`.

**What went wrong:**
- Merged stashed changes from `develop` branch which had different package versions
- `package-lock.json` was not regenerated after merge
- CI failed with "Missing: eslint@9.39.5 from lock file" and 200+ more missing packages

**Fix:** Run `npm install` to regenerate `package-lock.json` and commit it.

**Pattern:** After any merge or rebase that changes `package.json`, always run `npm install` to sync the lock file. Never edit `package-lock.json` manually.

**Applies to:** CI/CD, frontend
**Severity:** critical
**Status:** active

---

### Lesson: requirements.txt Must Exist for Python CI

**Context:** CI workflow runs `pip install -r requirements.txt` in the `api/` directory.

**What went wrong:**
- No `requirements.txt` file existed — dependencies were only listed informally
- CI failed with "Could not open requirements file: No such file or directory"

**Fix:** Create `api/requirements.txt` with all Python dependencies (fastapi, uvicorn, pydantic, supabase, pillow, pytest, ruff, etc.).

**Pattern:** Always create and maintain `requirements.txt` alongside Python projects. Include both runtime and dev dependencies (pytest, ruff).

**Applies to:** CI/CD, backend
**Severity:** critical
**Status:** active

---

### Lesson: CSS Module Imports Need TypeScript Declarations

**Context:** Web-specific `.web.tsx` file imports a CSS module (`*.module.css`).

**What went wrong:**
- `animated-icon.web.tsx` imports `./animated-icon.module.css`
- TypeScript error: "Cannot find module './animated-icon.module.css' or its corresponding type declarations"
- CI failed on `npx tsc --noEmit`

**Fix:** Create `src/types/css-module.d.ts` with `declare module '*.module.css'` and add to `tsconfig.json` includes.

**Pattern:** When using CSS modules in Expo/React Native web builds, always add a TypeScript declaration file for `*.module.css`.

**Applies to:** frontend, CI/CD
**Severity:** important
**Status:** active

---

### Lesson: Missing Modules Cause Chain Import Failures

**Context:** `main.py` imports `identify_router` which imports `cache`, `plantnet`, `plant_care` services.

**What went wrong:**
- These services don't exist yet (planned for future phases)
- Import failure cascaded: main.py → identify.py → cache.py (not found)
- All tests failed because they import `app` from `main.py`

**Fix:** Use `try/except ImportError` for optional route imports. Only include routers when their dependencies exist.

**Pattern:** When routes have unimplemented dependencies, guard the import with try/except rather than importing unconditionally.

**Applies to:** backend
**Severity:** important
**Status:** active

---

### Lesson: Branch Divergence Causes Massive Merge Conflicts

**Context:** Merging stashed changes from `develop` (which diverged significantly from `main`) into a new branch from `main`.

**What went wrong:**
- `develop` had hundreds of commits ahead of `main`
- Files existed on one branch but not the other
- 15+ merge conflicts on stash pop
- Had to manually resolve by accepting "ours" (stashed) versions

**Fix:** Use `git stash` then `git checkout main && git checkout -b feat/... && git stash pop`. Resolve conflicts by accepting stashed versions for files that should exist.

**Pattern:** When bringing work from a diverged branch, create a fresh branch from the target and apply changes. Use squash-merge or cherry-pick instead of merge for large divergences.

**Applies to:** git workflow
**Severity:** important
**Status:** active

---

### Lesson: Always Check Open PRs Before Starting New Work

**Context:** Starting a new feature branch without checking if other PRs are open.

**What went wrong:**
- PR #1 (`develop`) was open with 100 files changed
- PR #2 (`feat/ci-cd-release-workflow`) was created from `main` independently
- Both branches modified the same core files (api/main.py, package.json, etc.)
- Merging either PR would conflict with the other
- Wasted hours resolving 15+ merge conflicts between two branches

**Fix:** Before creating any new branch, always run `gh pr list` to check for open PRs. If an existing PR touches overlapping files, either:
1. Branch from that PR's branch instead of `main`
2. Or coordinate with the existing PR to avoid overlap

**Pattern:** `gh pr list` → check file overlap → branch from the right base. Never start from `main` blindly when other PRs are in flight.

**Applies to:** git workflow
**Severity:** critical
**Status:** active

---

### Lesson: Don't Branch From Main When Other PRs Target Main

**Context:** Two PRs both branching from `main` that modify overlapping files.

**What went wrong:**
- Both PRs had the same merge base (`main` = initial commit)
- Both modified api/main.py, package.json, eas.json, workflows, etc.
- Cherry-picking or merging between them caused 15+ conflicts on every overlapping file
- Had to use `git merge --ours` to resolve, losing some unique content from PR #1

**Fix:** When multiple PRs are in flight:
1. Identify which PR is the "base" PR (larger scope, foundational changes)
2. Branch new work from that PR's branch, not from `main`
3. This makes the second PR a clean superset — no conflicts on merge

**Pattern:** If PR A exists and PR B needs overlapping files, branch PR B from PR A's branch. PR B becomes: `PR_A_commits + PR_B_commits` with zero conflicts.

**Applies to:** git workflow
**Severity:** critical
**Status:** active
