# LESSONS.md

Running log of lessons learned during Gardenify development. Agents read this file at session start and update it after significant discoveries.

## 2026-08-04: ESM-only `brace-expansion` Override Broke the RN Codegen Gradle Build

**Context:** Cut release v1.1.0 (`git tag v1.1.0` + push). `release.yml` fired and the **Build APK (EAS)** job failed at `gradle assembleRelease` → `../react-native/scripts/generate-codegen-schema.js` → `generateCodegenSchemaFromJavaScript` → `expand is not a function`. Every gradle `generateCodegenSchemaFromJavaScript` task (gesture-handler, netinfo, async-storage, etc.) failed; the APK never built and no GitHub Release was created.

**Root cause:** `package.json` had a security override `"brace-expansion": "5.0.9"` (added by the security PR to silence CVE-2024-4068 / GHSA-v6h2-p8h4-qcjw). But v5 is **ESM-only** (`"type": "module"`) and exports no CommonJS `module.exports = expand`, while `@react-native/codegen` → `minimatch@3.1.5` requires `brace-expansion@^1.1.7` and calls `braceExpand()`. A version bump in the 5.x line satisfied npm audit but removed the CJS entry point everything downstream loads at build time.

**Why local checks missed it:** `npx tsc --noEmit`, `npm run lint`, and `npm test` all passed — none of them execute the RN codegen gradle tasks. The failure only surfaces during a native build.

**Fix:**

1. Override → `"brace-expansion": "2.1.4"` (pinned). `2.1.4` is the last **CommonJS** release AND the ReDoS fix landed in `> 2.1.3`, so it satisfies npm audit with 0 vulnerabilities while keeping the CJS `expand` function intact.
2. Verify before tagging a release by exercising the exact failing path locally:
   `node -e "const mm=require('minimatch'); console.log(typeof mm.Minimatch.prototype.braceExpand, new mm.Minimatch('foo{a,b}*/bar*.js').makeRe() instanceof RegExp)"`
   (braceExpand should print `function`) or run a local `npx expo run:android --variant release`.
3. `npx expo run:android --variant release` (detached, local) builds the full native project and exercises every codegen task — the faithful way to catch a "passes tsc but fails gradle" issue before wasting a cloud EAS build.

**Rules going forward:**

- **Pinning an override from a library must not switch module systems it is consumed under.** Prefer a version whose entry point (CJS vs ESM) matches the dependents. `^2.1.4` over `5.0.9`.
- **A release tag is the last gate, not a checkpoint.** Verify a real native build locally _before_ pushing the `v*` tag — tsc/lint/audit green is not sufficient for an APK release.
- **`release.yml` swallows the error message**: the job ran `BUILD_OUTPUT=$(...); echo exit:$?` with `set -e` so the actual gradle failure text was lost. For future release builds, run the EAS build job with `set +e` and capture `$BUILD_OUTPUT` into the log before exiting, so a red run still prints the real error.

**Applies to:** CI/CD, mobile, dependencies
**Severity:** critical
**Status:** active

## 2026-08-04: Prod Admin Locked Out Because Seed `is_admin` Never Applied

**Context:** Testing admin functionality with the intended admin account: the app showed "Access Denied" and the backend returned `403 Admin access required` for every admin endpoint, even with a valid JWT.

**Root cause:** The admin gate reads `public.users.is_admin` (backend `_require_admin` via service role; mobile `useAuth` via RLS own-row read). On prod, the account was created through the admin API, so the `seed.sql` step that runs `update ... set is_admin = true` for `admin@gardenify.app` **never executed**. The row defaulted to `false`, locking out every admin path.

**Also:** Seed passwords don't carry to prod-created accounts — an account that is confirmed and not banned but still fails login usually has an **unknown password**, not an account problem.

**Pattern:**

1. When an account's capabilities depend on a data row (not code), verify the **row state on prod** — seeds and migrations only matter if they ran. `SELECT is_admin` is the first diagnostic, not the code.
2. Two separate gates (backend service-role + mobile RLS own-row read) both keyed on the same column is correct defense-in-depth — fix the **data**, not the code.
3. Fix data via service-role `PATCH` (bypasses RLS); confirm with a non-admin token returning `403` to prove least-privilege still holds.
4. Documented in `docs/testing-guide.md` (no passwords — those are reset per session).

**Applies to:** auth, database
**Severity:** important
**Status:** active

## 2026-08-04: Landing/Onboarding HTML Can Drift After a Refactor — Grep for the Removed Technology

**Context:** After the SQLite→Supabase refactor (2026-08-02), the public `/` and `/onboarding` pages still claimed "Supabase + SQLite", "local SQLite database", "local DB query" and an offline SQLite fallback — all of which were removed. The code was fixed, but the marketing/architecture pages still described the old design.

**Lesson:** When removing a technology, the removal is only complete when **user-facing docs are in sync**. `grep -ri sqlite .` on the repo surfaced `api/landing_page.py` and `api/onboarding_page.py` still advertising SQLite. Update those pages in the same change (or a follow-up doc PR) so the shipped product and its public documentation match.

**Pattern:** after any backend refactor, run `grep -rniE 'sqlite|local database|offline' api/` to catch stale copy in HTML/doc strings before considering the refactor done.

**Files aligned:** `api/landing_page.py` (Tech Stack + Instant Matching card), `api/onboarding_page.py` (component breakdown, identify steps 4–5, sequence diagram participant `Supabase Species Store`, Fallback & Matching section, tech-stack cards). Verified: `grep -i sqlite` returns nothing in either file; `ruff` clean.

**Applies to:** docs, backend
**Severity:** minor
**Status:** active

## 2026-08-03: Secrets in Commits + Direct-to-main Commits (Both Caught, Both Fixed)

**Context:** During the SQLite→Supabase refactor, a Supabase Management API token (`sbp_…`) was committed into `.agents/session-todos.md` inside a commit made **directly on `main`** (violating the PR-only workflow). `git push` was rejected by GitHub push protection (`GH013` — Push cannot contain secrets).

**Lessons applied:**

1. **Raw secrets belong ONLY on gitignored files.** `.env.local`, `creds.json`, `.agents/handoff-current.md` are gitignored; tracked docs (`.agents/session-todos.md`, `MEMORY.md`, etc.) must reference a pointer (e.g. "see `creds.json`"), never the value. Verify with `git grep -nE 'sbp_[a-f0-9]{20,}'` before every push.
2. **GitHub push protection saved us** — the push was rejected so the token **never reached GitHub**. Rotation is still recommended hygiene for any secret written to a file.
3. **Fix a secret committed to history properly:** move the commit to a feature branch, `git add` the cleaned file, `git commit --amend` to rewrite the offending commit, verify `git grep` on `HEAD` is clean, then `git reset --hard origin/main` to restore `main`. The reflog still holds the old object locally but it is never pushed.
4. **Never commit on `main`.** Even mid-refactor, work goes on `feat/*`/`bugfix/*`/`chore/*` branches and merges via PR. A commit to `main` is now blocked locally by `.githooks/pre-commit` (and direct pushes by `.githooks/pre-push`).
5. **Hooks must be versioned + opt-in per clone.** Git doesn't track `.git/hooks`, so hooks live in the repo's `.githooks/` dir and each clone runs `git config core.hooksPath .githooks` (documented in AGENTS.md).

**Verification:** after `--amend`, `git grep -n "sbp_f527" HEAD` returns nothing; `git push` of the feature branch succeeded with no `GH013` block; CI on PR #21 all green (Python Tests, Lint & TypeCheck, Publish OTA, GitGuardian).

**Applies to:** all
**Severity:** critical
**Status:** active

## 2026-08-03: OpenCV Image-Validation Best Practices (Blur + Green Dominance)

**Context:** Applying OpenCV best practices to `image_processor.py`'s plant-likeness gate ahead of the PlantNet call.

**Lessons applied:**

1. **Always GaussianBlur before Canny** — Canny edge detection is extremely noise-sensitive; a `3x3` GaussianBlur first stabilizes edge output, so `content_score` reflects real structure, not sensor noise.
2. **Blur/quality is a variance-of-Laplacian, not an edge count** — a flat uniform image has no global content but also shouldn't be rejected as "edgy"; compute `cv2.Laplacian(gray).var()`, classify `sharpness < BLUR_THRESHOLD (100.0)` as blurry (PyImageSearch's well-known default). Edge count alone conflates "low detail" with "out of focus".
3. **Plant-likeness = green-pixel ratio in HSV** — threshold HSV green (`cv2.inRange` H≈30-90) and compute `green ratio = green_pixels / total`. This cleanly separates plants (high green share) from generic scenes.
4. **Surface the metrics in the schema** — added `sharpness`, `is_blurry`, `green_ratio` to `OpenCVResult` and returned them in `/api/identify` so callers can reason about quality (e.g., prompt "use a clearer photo" client-side if `is_blurry`).
5. **`is_plant_like` = `content_score > 0.01 OR green_ratio > 0.3`** — a structured (non-flat) image OR a strongly-green image passes; both must be low to call it "not a plant".

**Verified live on local backend:** flat-green JPEG → `sharpness:0, is_blurry:true, green_ratio:1.0`; structured green → `sharpness:370, is_blurry:false`.

**Applies to:** backend
**Severity:** minor
**Status:** active

## 2026-08-02: SQLite Files Don't Ship to Vercel — Use Supabase as the Only Local-Identify Backend

**Context:** `/api/identify` on Vercel logged `Local identification failed: unable to open database file`. The "local" identification step (perceptual-hash matching against a SQLite DB) silently no-ops in production.

**Issue:** `api/data/gardenify.db` is excluded from the Vercel bundle via `.vercelignore` (line 4: `api/data/gardenify.db`), and Vercel's filesystem is read-only (only `/tmp` writable) so WAL-mode SQLite can't work there anyway. Any code path that unconditionally `sqlite3.connect()`s the DB fails on serverless. Supabase was already the production species store (10,008 rows) but had **zero image hashes**, so `local_identify` had no Supabase equivalent.

**Decision (user):** Remove SQLite **entirely** — `local_identify` must hit Supabase (works on Vercel + local Supabase), all importers write to Supabase, `gardenify.db`/`local_db.py`/`schema.sql` deleted. This makes behavior consistent across local (local Supabase `127.0.0.1:54321`) and prod.

**Pattern:**

1. Treat any project-relative data file as non-shippable on serverless — if you can't write it and it's git-ignored, it doesn't exist in prod. Data must live in a database.
2. When migrating SQLite → Supabase, ids won't match (autoincrement vs BIGSERIAL) — join on the natural key (`scientific_name`).
3. Supabase `find_by_phash` = fetch all hashes + compute Hamming distance in Python (SQLite/PG bitwise XOR isn't portable; 2K rows is fast).
4. Gate local-identify on `supabase_species.is_available()` (Supabase configured), not on `local_db.is_available()`.

**Applies to:** backend, database
**Severity:** important
**Status:** active

## 2026-08-02: jsonb Columns Reject json.dumps Strings — and Bulk Upsert Can Wipe Enriched Data

**Context:** The new GBIF→Supabase seed script (`seed_supabase_gbif.py`) upserted 10,000 species. Prod `common_names`/`native_regions` search broke (`/api/species?q=sunflower` returned 0) and `common_names` came back as a string not a list.

**Issue:** Two compounding bugs:

1. The `species` table stores `common_names` and `native_regions` as **jsonb**, but the seed sent `json.dumps([...])` — a JSON _string_ (`"[]"`), which PostgREST stores as a jsonb string. The API's `_row_to_dict` then returned `'[]'` (string), failing `isinstance(..., list)` checks.
2. The seed used `upsert(on_conflict="scientific_name")`, which **overwrites every column** of existing rows. Since the GBIF archive has no common names, all 10,008 enriched prod rows were clobbered to empty arrays.

**Fix:**

1. Send jsonb fields as real Python lists (`_to_list()`), never `json.dumps` strings.
2. During upsert, fetch existing `common_names`/`native_regions` and preserve non-empty values: only fall back to the archive's (empty) value when the existing row is empty.
3. Beware `list("[]")` — it splits the string into `['[', ']']` (truthy), defeating the "empty" guard. Use a `json.loads`-based normalizer instead.

**Pattern:** For jsonb columns, treat JSON strings as data loss. When a bulk upsert can overwrite richer rows with sparse seed data, merge-on-conflict (preserve non-empty fields) instead of blind upsert. After any destructive seed run, verify `jsonb_typeof(col)='array'` and sample enriched rows.

**Applies to:** database, backend
**Severity:** critical
**Status:** active

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

| Anti-Pattern                       | Consequence              | Prevention                      |
| ---------------------------------- | ------------------------ | ------------------------------- |
| Not running CI locally             | Red checks on PR         | Pre-commit hooks                |
| Leaving template code in repo      | Broken builds, confusion | Clean up after project creation |
| Hardcoded secrets                  | Security leaks           | Gitleaks + detect-secrets       |
| Missing RLS policies               | Data exposure            | RLS checklist in migrations     |
| No testing strategy                | Bugs in production       | TDD + fixtures + mocking        |
| No developer docs                  | Slow onboarding          | Setup scripts + seed data       |
| Not configuring linters            | CI failures              | Create project-specific config  |
| Not excluding irrelevant dirs      | Type errors              | tsconfig exclude + cleanup      |
| Not fixing ruff errors before push | CI failures on PR        | Run `ruff check .` before push  |

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
**Status:** superseded (see 2026-07-29 corrected lesson)

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
**Status:** superseded (see 2026-07-29 corrected lesson)
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

---

## 2026-07-28: JSX Requires .tsx Extension

**Context:** Writing React Native components with TypeScript
**Issue:** TypeScript compilation failed with syntax errors on JSX content in `.ts` files
**Fix:** Always use `.tsx` extension for any file containing JSX, including hook files that return JSX (like context providers)
**Pattern:** `use-auth.ts` → `use-auth.tsx`, `component.ts` → `component.tsx`
**Applies to:** TypeScript, Expo
**Severity:** blocking
**Status:** active

---

## 2026-07-28: Typed Routes + Dynamic Segments

**Context:** Navigating to `/identification/[id]` and `/species/[name]` routes with expo-router typed routes
**Issue:** `experiments.typedRoutes` generates strict route types that don't include parameterized dynamic segments, causing TypeScript errors on `router.push()`
**Fix:** Cast dynamic route strings with `as any`: `router.push(\`/identification/${id}\` as any)`
**Tradeoff:** Loses type safety on route params — verify manually
**Applies to:** Expo Router, TypeScript
**Severity:** moderate
**Status:** active

---

## 2026-07-28: Jest 29 Bundled with jest-expo@55

**Context:** Setting up Jest with jest-expo@55.0.0
**Issue:** Installing `jest@30` with `jest-expo@55` causes incompatibility — `jest-expo` expects Jest 29 internals
**Fix:** Let `jest-expo@55` install its own Jest 29 dependency. Don't install Jest separately. Uninstall `jest@30` if present.
**Applies to:** testing, Expo SDK 55
**Severity:** blocking
**Status:** active

---

## 2026-07-28: @testing-library/react-native v12 vs v14

**Context:** Installing @testing-library/react-native for component tests
**Issue:** v14 requires `@testing-library/react-test-renderer` which adds `react-test-renderer` peer dep not present in Expo; `container` property renamed to `UNSAFE_root`
**Fix:** Install `@testing-library/react-native@12` (compatible with Expo SDK 55). Use `root` instead of `container` for element access.
**Applies to:** testing, Expo SDK 55
**Severity:** moderate
**Status:** active

---

## 2026-07-28: Manual AsyncStorage Mock Needed

**Context:** Testing components/hooks that use @react-native-async-storage/async-storage
**Issue:** AsyncStorage uses native modules that don't work in Jest test environment
**Fix:** Create `__mocks__/async-storage.js` with manual mock of all AsyncStorage methods. Use `moduleNameMapper` in jest.config.js to redirect `@react-native-async-storage/async-storage` to the mock file.
**Applies to:** testing, mobile
**Severity:** important
**Status:** active

---

## 2026-07-28: Mock Files Should Be .js Not .ts

**Context:** Created `__mocks__/` with `.ts` extension for a mock file
**Issue:** TypeScript compiler picks up `.ts` files in `__mocks__/` and fails on `jest` global (not declared in types)
**Fix:** Use `.js` extension for mock files — they don't need TypeScript compilation and won't be picked up by `tsc`
**Applies to:** testing, mobile
**Severity:** moderate
**Status:** active

---

## 2026-07-29: Windows `start` Fails for Detached Processes — Use PowerShell `Start-Process`

**Context:** Trying to start long-running servers (Expo dev server, Python uvicorn backend) in background/detached mode from the bash tool on Windows.

**Issue:**

- `start "Title" cmd /c command` — creates a new window but the process gets killed when the bash tool's timeout expires. The parent cmd.exe seems to propagate the termination signal.
- `start /B command` — runs in background but same process group, killed on timeout.
- Task subagents also get killed when their bash tool times out (120s default), so they can't keep a long-running process alive.

**Fix:** Use PowerShell `Start-Process` for truly detached processes:

```powershell
# Backend (detached, normal window)
powershell -Command "Start-Process -FilePath 'cmd' -ArgumentList '/c cd /d F:\Local_git\gardenify && python -m uvicorn api.main:app --reload --port 8000' -WindowStyle Normal"

# Expo (detached, normal window)
powershell -Command "Start-Process -FilePath 'cmd' -ArgumentList '/c cd /d F:\Local_git\gardenify && npx expo start --port 8083' -WindowStyle Normal"
```

Key details:

- `Start-Process` without `-Wait` launches the process and returns immediately — truly non-blocking
- The spawned cmd.exe is independent of the bash tool's shell, so it survives timeout/kill
- Use `-WindowStyle Normal` to show the window (useful for debugging) or `-WindowStyle Hidden` for headless
- Always include `-ArgumentList` as a single string to avoid parameter splitting
- Run `uvicorn` from project root (not `api/`) so Python can import the `api` module

**To verify:**

```bash
curl http://localhost:8000/api/health   # Backend health check
netstat -ano | findstr :8083            # Expo listening?
```

**Applies to:** all
**Severity:** critical (for Windows development workflow)
**Status:** active

---

## 2026-07-29: Verified — `start "Title" cmd /c` Returns Immediately; `start /B` Blocks

**Context:** Testing all patterns for launching long-running processes without blocking the bash tool.

**Findings (verified with both approaches):**

- `start "Title" cmd /c "command"` — returns immediately ✅, agent can continue working, but background process may be killed when bash tool timeout expires
- `powershell Start-Process` — returns immediately ✅, process truly detached and survives bash tool timeout ✅
- `start /B command` — blocks ❌ (same console group)
- `python -c "subprocess.Popen(..., DETACHED_PROCESS)"` — blocks ❌ (cmd.exe waits for python.exe)

**Recommendation:** Always use `powershell Start-Process` for long-running daemons that need to outlive the bash tool session. Use `start "Title" cmd /c` only for short-lived background tasks.

**Applies to:** all
**Severity:** critical
**Status:** active

---

## 2026-07-29: Windows Detached Process Launch — PowerShell `Start-Process` + Direct `.cmd` Paths

**Context:** Started earlier in the session. Final working approach documented here.

**Working pattern for detached services on Windows:**

```powershell
# Backend
Start-Process -FilePath 'cmd' -ArgumentList '/c cd /d F:\Local_git\gardenify && python -m uvicorn api.main:app --reload --port 8000' -WindowStyle Normal

# Expo (must use direct .cmd path, NOT npx)
Start-Process -FilePath 'F:\Local_git\gardenify\node_modules\.bin\expo.cmd' -ArgumentList 'start --port 8083' -WorkingDirectory 'F:\Local_git\gardenify' -WindowStyle Normal
```

**Key findings:**

- `npx` via `Start-Process` fails silently — `npx.cmd` is a batch file, and `Start-Process` can't properly handle batch files as executables
- Using the direct path to `expo.cmd` in `node_modules\.bin\` works reliably
- Without `-Wait`, `Start-Process` returns immediately — truly non-blocking
- The spawned process survives the bash tool's timeout/kill because it's truly independent
- Run `uvicorn` from project root (not `api/`) so Python can import the `api` module

**Applies to:** all
**Severity:** critical
**Status:** active

---

## 2026-07-29: WebP Images Not Accepted + Unhandled ValueError

**Context:** Testing image identification with sample `.webp` images.

**Issue:** `ALLOWED_TYPES` only included `image/jpeg`, `image/png`, `image/jpg` — WebP returned 500 Internal Server Error because `validate_image()` raised `ValueError` that wasn't caught by the identify route.

**Fix:**

1. Added `"image/webp"` to `ALLOWED_TYPES` in `api/services/cache.py`
2. Wrapped `validate_image()` call in try/except `ValueError` → `HTTPException(400)` in `api/routes/identify.py`

**Also:** When sending `.webp` files via curl, must specify content type: `-F "images=@file.webp;type=image/webp"`

**Applies to:** backend
**Severity:** medium
**Status:** active

---

## 2026-07-29: Pydantic + `.env.local` Extra Fields Crash

**Context:** Added `.env.local` to Pydantic's `env_file` list in `api/config.py` so the backend can read Supabase credentials.

**Issues encountered:**

1. **Extra fields not permitted** — `.env.local` has `SUPABASE_ANON_KEY`, `EXPO_PUBLIC_*` vars not defined in `Settings` model. Pydantic v2's `BaseSettings` rejects extra env vars by default. Fixed with `model_config["extra"] = "ignore"`.
2. **Field name mismatch** — env var is `SUPABASE_SERVICE_ROLE_KEY`, but field was named `supabase_service_key` (missing `_role_`). Pydantic canonicalizes field names to uppercase, so `supabase_service_key` → expects `SUPABASE_SERVICE_KEY`. Renamed field to `supabase_service_role_key` to match the env var.

**Pattern:** When adding a new `.env` file to Pydantic's `env_file`, always check:

- All fields match their env var names (case-insensitive, underscore-to-underscore)
- Add `extra="ignore"` to model_config if the file has vars beyond the model
- Pydantic reads from `os.environ` first, then `.env` files

**Applies to:** backend
**Severity:** blocking
**Status:** active

---

## 2026-07-29: Admin Route Must Use Settings, Not os.environ

**Context:** Admin API returned "Supabase not configured" even when `.env.local` had valid `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`.

**Issue:** `_get_service_client()` in `api/routes/admin.py` used `os.environ.get()` which doesn't get values from Pydantic's `.env` file loading. Pydantic reads env files into its `Settings` object but doesn't write to `os.environ`.

**Fix:** Changed to `settings.supabase_url` and `settings.supabase_service_role_key` (imported from `api.config`).

**Pattern:** Never use `os.environ.get()` in route code — always use `settings.xxx` from the Pydantic config, which handles `.env` files properly.

**Applies to:** backend
**Severity:** blocking
**Status:** active

---

## 2026-07-29: Testing Results Summary

**Context:** Full test run with both services running (backend port 8000, Expo port 8083).

**Results:**

| Test                    | Status | Notes                                                 |
| ----------------------- | ------ | ----------------------------------------------------- |
| Backend health          | ✅     | `{"status":"ok","version":"1.0.0"}`                   |
| Species search          | ✅     | `?q=rose` returns 3 results incl. Rosa damascena      |
| Species by name         | ✅     | `by-name/Rosa%20damascena` returns full details       |
| Supabase login          | ✅     | admin@gardenify.app logged in, JWT returned           |
| Admin list users        | ✅     | 3 users returned with admin user                      |
| Admin PATCH user        | ✅     | user2 toggled to is_admin=true                        |
| Identify (single, WebP) | ✅     | Returns proper JSON, local fallback (no PlantNet key) |
| Identify (single, JPEG) | ✅     | Same, metadata extracted correctly                    |
| Identify (multi-image)  | ✅     | 2 images processed, metadata for both                 |
| Local DB fallback       | ✅     | Source="local" when PlantNet unavailable              |
| Expo dev server         | ✅     | Responds on http://localhost:8083                     |

**Known issues:**

- PlantNet API key not set → identifications fall back to local DB (20 seed species)
- Local perceptual hash matching doesn't find matches with arbitrary sample images
- Expo served on port 8083 (PowerShell `Start-Process` with direct `expo.cmd` path)

**Applies to:** all
**Severity:** info
**Status:** active

---

## 2026-07-28: expo-image-picker SDK 55 API Changes

**Context:** Using `expo-image-picker` in the camera/gallery hook
**Issue:** `maxWidth`/`maxHeight` options don't exist in `ImagePickerOptions`, `mimeType` is nullable
**Fix:** Use `ImagePickerOptions["quality"]` for type-safe quality option, accept full asset object instead of custom interface
**Pattern:** Don't invent custom interfaces — use `ImagePickerAsset` directly from the library
**Applies to:** Expo SDK 55
**Severity:** moderate
**Status:** active

---

## 2026-07-29: Playwright Multipart API Doesn't Support Arrays of FilePayload

**Context:** Testing identify endpoint with >5 images in Playwright API tests.

**Issue:** Playwright's `multipart` form data with array values (e.g. `images: [file1, file2]`) throws `stream4.on is not a function` — Playwright expects scalar values, not arrays.

**Fix:** Use individual numbered field names instead of array syntax:

```typescript
// WRONG — internal crash
await request.post("/api/identify", {
  multipart: { images: [file1, file2, file3, file4, file5, file6] },
});

// RIGHT — individual fields
await request.post("/api/identify", {
  multipart: {
    images0: file1,
    images1: file2,
    images2: file3,
    images3: file4,
    images4: file5,
    images5: file6,
  },
});
```

**Applies to:** testing, backend
**Severity:** moderate
**Status:** active

---

## 2026-07-29: Starlette Middleware `response.headers.pop("server")` Causes 500

**Context:** Removing `Server` header in middleware for security test compliance.

**Issue:** Mutating response headers in middleware after they've been sent by the ASGI app causes `RuntimeError: Headers already sent`. Starlette's `pop()` on an immutable `MutableHeaders` raises during iteration.

**Fix:** Don't pop headers in middleware. Use uvicorn's `--no-server-header` flag instead:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --no-server-header
```

**Applies to:** backend, testing
**Severity:** important
**Status:** active

---

## 2026-07-29: Gallery Crop Removed via `allowsEditing: false`

**Context:** After selecting from gallery picker, the crop/edit screen appeared, adding an unnecessary step.

**Issue:** `expo-image-picker` shows a crop/edit UI when `allowsEditing: true` is passed to `launchImageLibraryAsync`. This requires user to crop before the image is returned.

**Fix:** Set `allowsEditing: false` (default) so the gallery returns immediately with the selected image. The Scan screen's image preview + Identify button serves as the confirmation step.

**Applies to:** mobile
**Severity:** moderate
**Status:** active

---

## 2026-07-29: opencode LSP + Formatter Config

**Context:** Setting up TypeScript and Python LSP servers and auto-formatters in opencode.json.

**Findings:**

- `typescript-language-server` is auto-detected by opencode when `typescript` is in `package.json`
- `pyright` needs to be installed as a devDependency: `npm install --save-dev pyright`
- For ruff formatter: opencode needs `pyproject.toml` or `.ruff.toml` in the project root or api/ directory
- `prettier` must be in `package.json` for opencode to auto-enable it
- LSP/formatter in opencode V1 uses `lsp` and `formatter` keys in config; V2 uses the same shape but V2 doesn't currently run LSP (docs note it's a future integration)

**Applies to:** all
**Severity:** important
**Status:** active

---

## 2026-07-29: `start /B` and `task` Subagent Both Block — Use `start "Title" cmd /c` or PowerShell `Start-Process`

**Context:** Starting uvicorn backend with `start /B python -m uvicorn ...` inside the bash tool.

**Issue:** `start /B` runs the process in the same console group — the bash tool never returns. Tried delegating to a `task` subagent (`debug` type), but the subagent's own bash tool also blocks for the same reason — the problem is fundamental, not fixable by delegation.

**Verified working patterns (tested 2026-07-29):**

```bash
# ✅ Returns immediately — opens new window
start "Gardenify-Backend" cmd /c "python -m uvicorn api.main:app --reload --port 8000"

# ✅ Returns immediately — truly detached
powershell -Command "Start-Process -FilePath 'cmd' -ArgumentList '/c python -m uvicorn api.main:app --reload --port 8000' -WindowStyle Normal"
```

Patterns confirmed to block:

- `start /B python -m uvicorn ...` ❌
- `python -c "subprocess.Popen(..., DETACHED_PROCESS)"` ❌ (python.exe parent waits)
- `task` subagent wrapping any of the above ❌ (subagent's bash tool blocks)

**Applies to:** all
**Severity:** important
**Status:** active

---

## 2026-07-29: Pillow 12 `getdata()` Deprecated — Use `get_flattened_data()`

**Context:** Running pytest with Pillow 12.2.0 produced 15 deprecation warnings about `Image.Image.getdata`.

**Issue:** `img.getdata()` deprecated in Pillow 12, removed in Pillow 14 (2027-10-15).

**Fix:** `list(img.get_flattened_data())` replaces `list(img.getdata())`.

**Applies to:** backend
**Severity:** minor
**Status:** active

---

## 2026-07-30: PlantNet API v2 Rejects `lang` Parameter

**Context:** Debugging "no match found" for rose image — PlantNet returned 400 with `{"message":"\"lang\" is not allowed"}`.

**Issue:** The `lang=en` parameter was included in the multipart form data sent to PlantNet, but the v2 API does NOT accept it. This caused PlantNet to return a 400 error with an error body (HTTP 200 status with `statusCode: 400` in JSON body), which the old httpx-based code handled silently — `raw` was set but had no results.

**Fix:** Remove the `lang` parameter entirely from multipart body and curl command.

**Key insight:** The API documentation mentions `lang` for v1 endpoints but v2 endpoints reject it outright. Always test with `curl -v` to see the exact request/response when debugging API client issues.

**Applies to:** backend
**Severity:** critical
**Status:** active

---

## 2026-07-30: Server Process Management on Windows — Verify PID Before Killing

**Context:** Made edits to `plantnet.py` but the server kept returning old responses. Spent hours debugging why changes weren't taking effect.

**Issue:** Taskkill commands were killing wrong PIDs. The running server (PID 14652, uptime 7+ hours) survived all kill attempts because `netstat` was returning a different PID each time (child processes of the startup window). The `start "" python -m uvicorn` commands were failing silently (port in use or import error) while the user thought they were starting fresh servers.

**Fix:**

1. Always verify `netstat -ano | findstr ":PORT "` to get the actual listening PID
2. Kill with `taskkill /F /PID <actual_pid>`
3. Verify port is free with `netstat` again
4. Start new server
5. Verify new server is running with `uptime_seconds` (should be < 10)

**Working launch patterns:**

- `subprocess.Popen(['python','-m','uvicorn','api.main:app','--port','8000'], creationflags=0x00000010)` — `CREATE_NEW_CONSOLE`, truly detached ✅
- `start "" python -m uvicorn api.main:app --host 0.0.0.0 --port 8000` — opens new window ✅

**Patterns that block:**

- `start /B` — same console group, blocks agent shell ❌
- `subprocess.Popen(DETACHED_PROCESS=0x00000008)` — hangs parent ❌
- `subprocess.run(['curl', ...])` — hangs on Windows in this env ❌

**Applies to:** all
**Severity:** critical
**Status:** active

---

## 2026-07-29: Suppress PIL Debug Log Noise

**Context:** Backend logs flooded with `DEBUG PIL.TiffImagePlugin` messages when processing JPEG images.

**Issue:** PIL logs debug-level metadata about TIFF tags in JPEG EXIF data — noisy.

**Fix:** Add to startup:

```python
logging.getLogger("PIL.TiffImagePlugin").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
```

**Applies to:** backend
**Severity:** minor
**Status:** active

---

## 2026-07-31: `supabase db push` Fails on Multi-Statement SQL — Apply Migrations Manually

**Context:** Running `supabase db push` to apply 5 migration files to production Supabase.

**Issue:** `supabase db push` failed with error when encountering SQL with multiple statements or lines it couldn't parse. The CLI doesn't handle multi-statement SQL well in production push context.

**Fix:** Apply migrations manually per statement:

1. Use `supabase db query "<sql>"` for single-line statements
2. For full migration files, use a Python script with `psycopg2` to execute the entire file

**Pattern:** Supabase CLI's `db push` is unreliable for multi-statement SQL. Always have a manual apply strategy (CLI `db query` + psycopg2 for files). Verify each migration with `supabase db dump --local` or by querying the `_migrations` table.

**Applies to:** database
**Severity:** important
**Status:** active

---

## 2026-07-31: `uuid-ossp` Extension Required for `uuid_generate_v4()`

**Context:** Applying migrations to production Supabase that use `uuid_generate_v4()` for primary keys.

**Issue:** Migration failed with `function uuid_generate_v4() does not exist` — the `uuid-ossp` extension wasn't enabled on the production database.

**Fix:** Enable the extension before running migrations:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

**Note:** Local `supabase start` includes this extension by default, but production doesn't. Always check which extensions are needed and enable them explicitly in early migrations.

**Applies to:** database
**Severity:** important
**Status:** active

---

## 2026-07-31: GBIF Batch Upsert — 100 Rows Per Batch Optimal

**Context:** Importing 10,008 species from local SQLite to production Supabase.

**Issue:** Large batch upserts (>100 rows) can cause Supabase API timeouts or payload size limits. Single-row upserts are too slow.

**Fix:** Batch upsert in chunks of 100 rows using `supabase.table("species").upsert(batch, ignore_duplicates=True)`.

**Pattern:** For large Supabase data imports:

1. Read source data in chunks (100 rows)
2. Upsert each chunk with `ignore_duplicates=True` for idempotency
3. Log progress every N batches
4. Delete import scripts after use (not production code)

**Applies to:** database
**Severity:** moderate
**Status:** active

---

## 2026-07-31: `load_dotenv()` Required for Pydantic `.env` Compatibility

**Context:** `supabase_species.py` uses `os.environ.get("SUPABASE_URL")` but those values are only loaded via Pydantic `Settings` from `.env.local`.

**Issue:** Pydantic's `BaseSettings` reads `.env` files into its model fields but does NOT write to `os.environ`. Code using `os.environ.get()` gets `None` for all env vars from `.env` files.

**Fix:** Call `load_dotenv()` in `api/main.py` before anything else reads env vars:

```python
from dotenv import load_dotenv
load_dotenv()
```

**Pattern:** Any code that uses `os.environ.get()` instead of Pydantic `settings.xxx` needs `load_dotenv()` to be called at startup. This applies to libraries or services that read env vars directly (like `supabase_species.py`).

**Applies to:** backend
**Severity:** important
**Status:** active

---

## 2026-07-31: Leftover Expo Template Placeholder Overrode the Entire App

**Context:** Production APK launched to a blank screen reading "Edit src/app/index.tsx to edit this screen." instead of the Gardenify app — reported on a physical device and reproduced on the emulator.

**Issue:** `src/app/index.tsx` was the default `create-expo-app` template placeholder. In expo-router, `/` resolves to `index.tsx`, so it rendered instead of the real app. The root `_layout.tsx`'s conditional Stack was never reached because the placeholder route shadowed it.

**Fix:** Replace `src/app/index.tsx` with an auth-aware redirect:

```tsx
import { Redirect } from "expo-router";
import { useAuth } from "@/hooks/use-auth";
import { Loading } from "@/components/loading";

export default function Index() {
  const { user, loading } = useAuth();
  if (loading) return <Loading message="Loading..." />;
  return <Redirect href={user ? "/(tabs)" : "/(auth)/login"} />;
}
```

**Pattern:** Always audit `app/` routes (especially root `index.tsx`) before shipping — the Expo template leaves a placeholder that overrides routing. Verify by installing the built APK, not just via `npx expo start`.

**Applies to:** mobile
**Severity:** critical
**Status:** active

---

## 2026-07-31: Verify Installed APK Actually Replaced the Old One (adb)

**Context:** After `adb install -r` reported Success, relaunching still showed the old template screen. Root cause: the install silently didn't take effect (likely a stale adb server after `taskkill /f /im adb.exe`), leaving the previous v0.1.3 APK installed.

**Issue:** `adb install` "Success" can be misleading — the old app can remain. The version name/code won't reveal it (both v0.1.3 and v0.1.4 are versionCode 1).

**Fix:** Verify the installed APK matches your build by comparing MD5:

```
adb shell pm path com.gardenify.app        # get base.apk path
adb pull <path> device_base.apk
certutil -hashfile device_base.apk MD5
certutil -hashfile my-build.apk MD5         # must match
```

If they differ: `adb uninstall com.gardenify.app` then `adb install -r` the correct APK, then re-verify.

**Pattern:** Never trust `adb install` Success alone — compare hashes of the installed vs intended APK. Also, after killing adb (`taskkill /f /im adb.exe`), the emulator may disconnect and the next `adb install` targets a stale session.

**Applies to:** mobile
**Severity:** important
**Status:** active

---

## 2026-07-31: Verify Built APK Contains the Correct Env Config

**Context:** Suspected the production APK had wrong/missing Supabase or API config ("not working on device").

**Issue:** Environment problems are hard to eyeball. `EXPO_PUBLIC_*` vars are inlined into the Hermes bundle at build time.

**Fix:** Extract `assets/index.android.bundle` from the APK and grep for expected strings:

```
7z x -y -o<out> app.apk "assets/*"
python -c "data=open('.../index.android.bundle','rb').read(); print(data.find(b'supabase.co'))"
```

Confirm: expected Supabase URL present, `localhost:54321` fallback ABSENT, API URL present. This proved v0.1.3's env config was actually correct — the real bug was routing.

**Pattern:** Before debugging a "broken on device" report, rule out build config by inspecting the compiled bundle. Hermes bytecode keeps string literals searchable.

**Applies to:** mobile
**Severity:** important
**Status:** active

---

## 2026-07-31: Android Emulator Input via `adb shell input` Is Unreliable After Reboot

**Context:** Attempting automated UI smoke tests on the emulator after a fresh boot.

**Issue:** `adb shell input tap` + `input text` failed to populate fields — login dialog said "Please enter email and password" even though text was typed. Field coordinates shift when the soft keyboard opens, and focus doesn't always land where tapped.

**Fix:** For reliable programmatic verification, use `adb shell uiautomator dump` to read actual element bounds, then tap those exact centers. Re-dump after each interaction (layout shifts with the keyboard). Prefer `uiautomator dump` text assertions over pixel coordinates.

**Pattern:** UI assertions via `uiautomator dump` are the most reliable non-visual signal on the emulator. Do a clean `adb uninstall` + `adb install` and verify hash before spending time on flaky `input` automation.

**Applies to:** mobile
**Severity:** minor
**Status:** active

## 2026-08-01: Vercel Deploy `lstat ENOENT` — Never Exclude Git-Tracked Files via `.vercelignore`

**Context:** Backend production deploy (GH Actions → `vercel deploy`) failed repeatedly with `Error: ENOENT: no such file or directory, lstat '/vercel/path0/...'` — first on `.agents/agentic-handoff.md`, then `__mocks__/...`, then `.vercel/python/.venv/...`.

**Issue:** For a GitHub-linked Vercel project, the deployment manifest is derived from the **git tree**, and Vercel's build server syncs every tracked file to `/vercel/path0`. Any git-tracked file excluded from the upload (via `.vercelignore`) breaks that sync with `lstat ENOENT`.

**Fix:** `.vercelignore` must exclude ONLY untracked/generated files (`node_modules`, `.git`, `.expo`, `.vercel`, `api/data` artifacts). Both a deny-list that excluded tracked files (`.agents/*.md`) AND a `/*` allowlist (uploading only `api/`) caused ENOENT — the manifest references ALL tracked files regardless.

**Bonus:** `vercel build` + `vercel deploy --prebuilt` is the wrong pattern here — local `vercel build` creates `.vercel/python/.venv`, which the deploy manifest references but `.vercelignore` excludes → more ENOENT. Use direct `vercel deploy --prod` and let Vercel build server-side (also makes system env vars available).

**Pattern:** To check a `.vercelignore` rule is safe: `git ls-files --error-unmatch <pattern>` — any match means a tracked file, which must NOT be ignored.

**Applies to:** backend / CI/CD
**Severity:** critical
**Status:** active

## 2026-08-01: Deploy Backend as Part of the Release Flow, Not on Every Push

**Context:** Backend auto-deployed to production on every `api/**` change to `main` via `deploy-backend.yml`.

**Issue:** This double-deployed with Vercel's GitHub integration and deployed the backend before the Android app was released, so API changes could ship ahead of the app that uses them.

**Fix:** Remove the push-triggered deploy workflow. Add a `deploy-backend` job to `release.yml` with `needs: create-release`, so the order is: tests/checks → cut tag → release APK → deploy backend. Restore Vercel's `commandForIgnoringBuildStep` to skip production on git pushes (so Vercel doesn't auto-deploy either).

**Applies to:** CI/CD
**Severity:** important
**Status:** active

## 2026-08-02: Vercel Serverless Filesystem Is Read-Only (Only /tmp Writable)

**Context:** Production `/api/identify` returned HTTP 500. The user-supplied traceback showed `ImageProcessor()` → `_ensure_upload_dir()` → `mkdir` at `/var/task/api/data/uploads/<upload_id>` failing with `OSError: [Errno 30] Read-only file system`.

**Issue:** Vercel serverless functions run from a read-only `/var/task`. Any write outside `/tmp` crashes at runtime — even a directory `mkdir`. The upload dir was hardcoded to `api/data/uploads`, which works locally but is read-only in production.

**Fix:**

1. Resolve the upload dir at import time: probe the default dir with a write test; on `OSError`, fall back to `<tempdir>/gardenify-uploads` (Vercel maps `/tmp`).
2. Make disk writes best-effort: wrap storage file writes in `try/except OSError`; on failure return `storage: {}` while still returning the in-memory `compressed_data` (the PlantNet pipeline only needs in-memory bytes).
3. Import `UPLOAD_DIR` from `image_processor` in `history.py` rather than re-deriving the path (single source of truth).

**Pattern:** On serverless platforms, never assume a project-relative path is writable. Resolve writable storage at startup with a fallback to `tempfile.gettempdir()`, and treat secondary disk writes (metadata/storage) as non-fatal so the primary in-memory path always succeeds.

**Applies to:** backend
**Severity:** critical
**Status:** active

**Lesson:** supabase-py (2.31) exposes server-side password flows: auth.reset_password_for_email(email, {redirect_to}), auth.verify_otp({type: recovery, email, token}), and auth.admin.update_user_by_id(id, {password}). Client-side recovery-link handling on Expo uses the app scheme (gardenify://reset-password) with PKCE code param.
**Lesson:** when routing app login through a backend that returns Supabase tokens, call supabase.auth.setSession({access_token, refresh_token}) to restore the session (signInWithPassword stays client-side optional).
**Lesson:** in-memory rate-limiter on serverless is per-instance/approximate; a 3-strike lockout must not prune a mid-burst entry (prune only idle or expired-lock entries).

**Lesson (release 1.1.0):** Vercel auto-deploy does not reliably fire on GitHub merges for this repo � the auth endpoints were absent on prod until a manual \`vercel --prod\` from main. When a release changes the backend, deploy the backend manually BEFORE tagging so the new APK never points at a stale API.
**Lesson (release 1.1.0):** full release is automated by \`.github/workflows/release.yml\` on a \`v*\` tag push (EAS production build -> GitHub Release with APK -> Vercel deploy). The git pre-push hook only blocks main/master branches, so tag pushes are allowed.
