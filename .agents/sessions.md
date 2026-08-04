# Session Log

Track all agent sessions for continuity. Update before each commit.

## Session Format

```markdown
### YYYY-MM-DD: Session Title

- **Duration**: [time]
- **Goal**: [what was accomplished]
- **Files modified**: [list]
- **Tests status**: [pass/fail]
- **Next session**: [what to do next]
```

---

### 2026-08-04: v1.0.0 Release Testing + Prod Admin Log-in Fix

- **Duration**: ~4 hours (incl. EAS build queue wait)
- **Goal**: Wait for fixed v1.0.0 APK, verify History/Save on emulator, diagnose login + admin access on prod
- **Files modified**: `docs/testing-guide.md` (new), `LESSONS.md` (admin gotcha lesson). Prodt data (no commit): promoted `admin@gardenify.app`→`is_admin`, reset passwords.
- **Tests status**: History + Save verified on emulator (release APK, prod); admin endpoints 200 with admin token / 403 with non-admin; sign-in OK for both accounts
- **Next session**: seed Supabase `image_hashes` to prod; re-check PlantNet identify; decide on PR #3

---

### 2026-08-04: Landing Page Architecture Aligned to SQLite→Supabase Refactor

- **Duration**: ~1 hour
- **Goal**: Remove stale SQLite references from public pages after the SQLite→Supabase refactor; document the drift lesson
- **Files modified**:
  - `api/onboarding_page.py` — component breakdown, identify steps 4–5, sequence participant `Supabase Species Store`, "Fallback & Matching" section, tech-stack cards, nav link
  - `api/landing_page.py` — "Instant Matching" card + Database value `Supabase (PostgreSQL)`
  - `LESSONS.md` — added doc-drift lesson (2026-08-04)
- **Tests status**: `ruff` clean on both pages; `grep -i sqlite` returns nothing in either
- **Next session**: release v1.0.0 build still IN_QUEUE; open PR for this branch (ask user before merge)

---

### 2026-07-27: Initial Project Setup + Bug Fixes

- **Duration**: ~2 hours
- **Goal**: Fix CI failures (TypeScript + Python ruff), clean up stale template code, document mistakes
- **Files modified**:
  - `tsconfig.json` — removed stale example/ exclusion (no longer needed)
  - `api/ruff.toml` — created project-specific ruff config
  - `LESSONS.md` — added 8 documented mistakes with solutions
  - `example/` — deleted 20 stale template files (1172 lines)
- **Tests status**: Not verified locally (CI will tell)
- **Next session**: Fix remaining CI issues, add ENVIRONMENT/USE_REMOTE env vars, seed scripts, testing framework

---

### 2026-07-27: Pre-Commit Workflow Established

- **Duration**: ~30 min
- **Goal**: Create pre-commit workflow: sessions, memory, handoffs, lessons, primer, PRD check
- **Files modified**:
  - `.agents/sessions.md` — created session log
  - `.agents/handoff-current.md` — updated with current state
  - `.agents/primer.md` — created quick context for agents
  - `PRD.md` — created product requirements checklist
  - `MEMORY.md` — updated with current state
- **Tests status**: Pending
- **Next session**: ENVIRONMENT/USE_REMOTE, seed scripts, testing framework, PRD items

---

### 2026-07-29: Session 4 — Gallery Flow Fix + Agent/Plugin Overhaul

- **Duration**: ~2 hours
- **Goal**: Fix gallery crop step, test identification flow on emulator, add LSP/formatter/superpower plugins
- **Files modified**:
  - `src/app/(tabs)/index.tsx` — removed `allowsEditing` from gallery picker
  - `.opencode/plugins/gardenify-hooks.ts` — fixed tsc error parsing, removed redundant prettier formatting
  - `.opencode/plugins/superpower-hooks.ts` — created superpower plugin (service tracking, blocking cmd detection, compaction context)
  - `.opencode/instructions/INSTRUCTIONS.md` — added non-blocking service management section
  - `opencode.json` — added LSP (ts + pyright), formatters (prettier + ruff), testing/supabase/debug agents, new commands
  - `api/pyproject.toml` — created ruff config for Python formatting
  - `package.json` — added `pyright` + `prettier` as devDependencies
- **Tests status**: 73 Python passed, 21 Playwright API tests pass, lint clean
- **Gallery → identify flow verified on emulator**: gallery picker, crop removed, image preview, identify button all working
- **Next session**: Create PR, get Supabase credentials, deploy backend to Vercel

---

- **Duration**: ~15 min
- **Goal**: Fix all 9 ruff errors from GitHub Actions CI
- **Files modified**:
  - `api/routes/health.py` — UP017: `timezone.utc` → `UTC` alias
  - `api/routes/identify.py` — I001: sorted imports, B904: `raise ... from e`
  - `api/services/plant_care.py` — E501: wrapped long lines
  - `api/tests/test_api.py` — I001: sorted imports
  - `api/tests/test_services.py` — I001: sorted imports
- **Tests status**: Not verified locally
- **Next session**: Verify CI passes, continue with ENVIRONMENT/USE_REMOTE, seed scripts, testing framework

---

### 2026-07-27: Add ENVIRONMENT/USE_REMOTE env vars + seed scripts

- **Duration**: ~30 min
- **Goal**: Add environment mode switching and database seed scripts
- **Files modified**:
  - `api/config.py` — Added `environment`, `use_remote`, `is_production`, `supabase_effective_url`
  - `.env.example` — Added ENVIRONMENT, USE_REMOTE vars with docs
  - `.env.test` — Added ENVIRONMENT, USE_REMOTE vars
  - `docker-compose.yml` — Updated comments with env var docs
  - `supabase/seed.sql` — Full seed data (5 identifications, 3 favorites, test user)
  - `scripts/seed.sh` — Bash seed script (local/production modes)
  - `scripts/seed.ps1` — PowerShell seed script
  - `Makefile` — Added seed, seed-local, seed-prod commands
  - `api/routes/health.py` — Debug endpoint shows environment info
- **Tests status**: Not verified locally
- **Next session**: Verify CI passes, continue with testing framework

---

### 2026-07-27: Playwright + Deployment Guides + Dev Workflow

- **Duration**: ~45 min
- **Goal**: Complete testing framework, deployment guides, dev workflow docs
- **Files modified**:
  - `playwright.config.ts` — Playwright config for API + visual tests
  - `e2e/api-tests/health.spec.ts` — API health/debug/identify endpoint tests
  - `e2e/api-tests/integration.spec.ts` — Full flow, caching, error recovery, security tests
  - `e2e/visual/api-snapshots.spec.ts` — Response structure snapshots, timing tests
  - `e2e/android/README.md` — Android emulator testing guide
  - `docs/vercel-deployment.md` — Vercel backend deployment guide
  - `docs/supabase-integration.md` — Supabase auth/database/storage setup guide
  - `.gitignore` — Added Playwright artifacts, test results, blob reports
  - `opencode.json` — Added Playwright MCP server
  - `.agents/security-checklist.md` — 13-point security gate
  - `.agents/code-hygiene.md` — Code quality rules
  - `.agents/linear-history.md` — Git workflow + changelog
  - `.agents/pre-commit-workflow.md` — Pre-commit checklist
  - `.agents/documentation-standards.md` — Doc rules
  - `.agents/product-development.md` — UX, accessibility, analytics
  - `.agents/sessions.md` — Session log (this file)
  - `.agents/handoff-current.md` — Current handoff state
  - `.agents/primer.md` — Quick context for new agents
  - `PRD.md` — Product requirements checklist (60+ items)
  - `BUGS.md` — Issue tracker
- **Tests status**: Playwright installed, tests written but not run
- **Next session**: Run Playwright tests, verify CI passes, get Supabase credentials

---

### 2026-07-27: OpenCode + Claude ECC Integration

- **Duration**: ~45 min
- **Goal**: Integrate opencode best practices (rules, plugins, skills, tools) + ECC patterns from affaan-m/ECC
- **Files modified**:
  - `opencode.json` — Full rewrite: 9 agents, 10 commands, permissions, plugin/skills config
  - `SOUL.md` — Project identity and core principles
  - `RULES.md` — Must always/never rules, agent/skill format, commit style
  - `.opencode/plugins/gardenify-hooks.ts` — Auto-format, typecheck, security, session management hooks
  - `.opencode/instructions/INSTRUCTIONS.md` — Security, coding, testing, git, Expo, Python, Supabase rules
  - `.opencode/skills/tdd-workflow/SKILL.md` — TDD methodology for Gardenify
  - `.opencode/skills/security-review/SKILL.md` — Security review checklist
  - `.opencode/skills/expo-development/SKILL.md` — Expo SDK 55 patterns
  - `.opencode/skills/fastapi-backend/SKILL.md` — FastAPI route/service/model patterns
  - `.opencode/skills/supabase-rls/SKILL.md` — RLS policies and auth integration
  - `.claude/rules/gardenify-guardrails.md` — Prompt defense, commit, code style, security defaults
- **Tests status**: Not verified locally
- **Next session**: Verify CI passes, run Playwright tests, get Supabase credentials

---

### 2026-07-27: Local Plant Database + Offline Fallback

- **Duration**: ~1.5 hours
- **Goal**: Build local SQLite plant database for offline identification, perceptual hash matching, species search API
- **Files created**:
  - `api/data/schema.sql` — SQLite schema (species, image_hashes, import_log)
  - `api/services/local_db.py` — SQLite connection, CRUD operations
  - `api/services/perceptual_hash.py` — dHash + pHash implementation
  - `api/services/local_identify.py` — Local plant identification service
  - `api/routes/species.py` — GET /api/species endpoints
  - `api/data/importers/` — Import scripts (plantnet300k, seed, hash index, orchestrator)
  - `api/data/importers/seed_species.py` — 20 common species for testing
- **Files modified**:
  - `api/main.py` — Added species router, local DB init on startup
  - `api/routes/identify.py` — Added offline fallback to local DB
  - `api/models/schemas.py` — Added `source` field to IdentificationResponse
  - `.gitignore` — Added data dirs, cloned repos
  - `tsconfig.json` — Reverted (no exclusions needed after cleanup)
  - `LESSONS.md` — Added 3 new lessons (#11, #12, #13)
- **Cleanup**:
  - Removed `plantnet-ai-taxonomist/` from project root
  - Removed `plantnet-300k/` from project root (code files)
  - Renamed `api/data/import/` → `api/data/importers/` (reserved keyword)
- **Tests status**: All endpoints verified working via curl
  - `GET /api/species?q=monstera` ✓
  - `GET /api/species/1` ✓
  - `GET /api/species/by-name/Rosa%20damascena` ✓
  - `npx tsc --noEmit` ✓
  - `python -m py_compile` ✓
- **Next session**: Download GBIF Darwin Core Archive, populate real species data, test with PlantNet-300K metadata

---

### 2026-07-27: Bug Fixes + Test Suite

- **Duration**: ~45 minutes
- **Goal**: Fix identify.py bugs, add comprehensive test suite, reconcile docs
- **Bugs fixed**:
  - `identify.py:99` — undefined `e` in except block (PlantNet error variable scope)
  - `identify.py:118` — undefined `parsed` when PlantNet fails (variable scope)
  - `local_db.py:find_by_phash` — SQLite doesn't support XOR (replaced with Python-side Hamming)
- **Tests created** (67 total, all passing):
  - `test_local_db.py` — 15 tests (init, insert, upsert, search, JSON parsing)
  - `test_perceptual_hash.py` — 16 tests (dHash, pHash, Hamming, match, DCT)
  - `test_species_routes.py` — 15 tests (list, search, detail, by-name, 404s)
  - `test_identify_offline.py` — 10 tests (local identify, hash matching, source field)
- **Files modified**:
  - `api/routes/identify.py` — fixed 2 bugs
  - `api/services/local_db.py` — replaced SQL XOR with Python Hamming
  - `api/tests/conftest.py` — shared fixtures
  - `api/tests/test_perceptual_hash.py` — fixed uniform image tests
  - `api/tests/test_local_db.py` — fixed upsert expectation
  - `api/tests/test_identify_offline.py` — fixed pHash vs dHash mismatch
  - `LESSONS.md` — 3 new lessons (SQLite XOR, hash testing, test expectations)
- **Tests status**: 67 passed, 0 failed, 18 warnings (Pillow deprecation)
- **Next session**: Download GBIF data, populate real species, reconcile docs

---

### 2026-07-28: Phase 1 Mobile UI + Phase 2 Features

- **Duration**: ~2 hours
- **Goal**: Build complete Phase 1 mobile app (auth, scan, history, profile, results) + Phase 2 features (disease UI, favorites, species details, caching, sharing, multi-language)
- **Branch**: `feat/mobile-ui-phase-1-2`
- **Files created**:
  - `src/lib/types.ts` — All TypeScript types matching backend schemas
  - `src/lib/supabase.ts` — Supabase client with SecureStore adapter
  - `src/lib/api-client.ts` — Backend API client (identify, species search, health)
  - `src/lib/cache.ts` — AsyncStorage result cache with 24h TTL
  - `src/lib/share.ts` — Share module (react-native Share + expo-sharing)
  - `src/constants/theme.ts` — Colors, spacing, typography, shadows
  - `src/hooks/use-auth.tsx` — Auth context/provider with signup, login, logout
  - `src/hooks/use-identification.ts` — Plant identification hook
  - `src/hooks/use-camera.ts` — Camera + gallery picker hook
  - `src/hooks/use-settings.ts` — Language/theme settings hook
  - `src/components/button.tsx` — Reusable button (5 variants, 3 sizes)
  - `src/components/plant-card.tsx` — Plant result card with confidence bar
  - `src/components/loading.tsx` — Loading spinner + overlay
  - `src/components/index.ts` — Barrel exports
  - `src/app/_layout.tsx` — Root layout with auth check (AuthProvider + Stack navigator)
  - `src/app/(auth)/_layout.tsx` — Auth group stack layout
  - `src/app/(auth)/login.tsx` — Login screen with email/password
  - `src/app/(auth)/register.tsx` — Register screen with validation
  - `src/app/(tabs)/_layout.tsx` — 4-tab bottom navigator (Scan, Saved, History, Profile)
  - `src/app/(tabs)/index.tsx` — Scan screen with camera/gallery + organ selector
  - `src/app/(tabs)/favorites.tsx` — Favorites list with remove + species detail link
  - `src/app/(tabs)/history.tsx` — Past identifications list with pull-to-refresh
  - `src/app/(tabs)/profile.tsx` — Profile screen with user info + sign out
  - `src/app/identification/[id].tsx` — Results detail with disease detection UI, favorites button, care info, species detail link
  - `src/app/species/[name].tsx` — Species detail screen with taxonomy + Wikipedia/GBIF links
- **Files modified**:
  - `app.json` — Added plugins: expo-secure-store, expo-sharing, expo-localization
  - `package.json` — Added deps: @supabase/supabase-js, expo-image-picker, expo-secure-store, expo-sharing, expo-localization, @react-native-async-storage/async-storage, react-native-view-shot
  - `src/app/_layout.tsx` — Rewrote with AuthProvider + conditional auth/tabs routing + species route
  - `.agents/sessions.md` — This entry
  - `.agents/handoff-current.md` — Updated
  - `MEMORY.md` — Updated
  - `PRD.md` — Checked off completed items
  - `.agents/primer.md` — Updated
- **Dependencies installed**: expo-secure-store, expo-image-picker, expo-sharing, expo-localization, @supabase/supabase-js, @react-native-async-storage/async-storage, react-native-view-shot
- **Tests status**: 73 passed, TypeScript clean, lint clean
- **Next session**: Run Expo dev server to verify screens render, then create PR to main

### 2026-07-28: Testing Infrastructure + Jest Setup

- **Duration**: ~15 min
- **Goal**: Set up Jest testing infrastructure, write 41 frontend tests, fix TypeScript/lint CI
- **Files created**:
  - `jest.config.js` — Jest config with jest-expo preset, moduleNameMapper for @/ alias + AsyncStorage mock
  - `__mocks__/async-storage.js` — Manual mock for @react-native-async-storage/async-storage
  - `src/__tests__/theme.test.ts` — 8 tests (colors, spacing, borderRadius, typography)
  - `src/__tests__/cache.test.ts` — 8 tests (set/get, getRecent, clear, expiry)
  - `src/__tests__/api-client.test.ts` — 7 tests (health, identify, searchSpecies, getSpeciesByName)
  - `src/__tests__/button.test.tsx` — 6 tests (render, onPress, loading, disabled, variants)
  - `src/__tests__/loading.test.tsx` — 4 tests (Loading + LoadingOverlay)
  - `src/__tests__/plant-card.test.tsx` — 6 tests (names, confidence, empty commonNames, onPress)
  - `src/__tests__/helpers.ts` — Shared test fixtures (mock result, species, identification)
- **Files modified**:
  - `src/app/_layout.tsx` — Fixed: async functions passed as direct children to `<Stack>` (React 19 warning)
  - `src/app/(tabs)/favorites.tsx` — Fixed: added missing `useCallback` import
  - `src/app/(tabs)/history.tsx` — Fixed: wrapped `onRefresh` in `useCallback`
  - `src/app/(tabs)/profile.tsx` — Fixed: wrapped `handleSignOut` in `useCallback`
  - `src/__tests__/loading.test.tsx` — Fixed: `container` → `root` (v12 API rename)
  - `package.json` — Added test scripts
  - `.gitignore` — Added `__mocks__/@react-native-async-storage/*.ts`
- **Dependencies installed**: jest-expo@55.0.0, @testing-library/react-native@12, @types/jest
- **Lessons learned**:
  1. Jest 30 is incompatible with jest-expo — must use Jest 29 (bundled with jest-expo)
  2. `@testing-library/react-native` v12 renamed `container` → `UNSAFE_root` / `root`
  3. Mock files in `__mocks__/` should be `.js` not `.ts` to avoid TypeScript compilation
- **Tests status**: 41 passed (frontend), 73 passed (Python), TypeScript clean, lint clean
- **Next session**: Create PR to main, then get Supabase/PlantNet credentials for production

---

### 2026-07-29: Admin User Management + Supabase RLS Fixes

- **Duration**: ~3 hours
- **Goal**: Build admin user management (backend API + mobile screen), fix Supabase seed SQL + RLS policies, verify auth/RLS flow
- **Files created**:
  - `api/routes/admin.py` — 4 admin API endpoints (GET/PATCH/DELETE /api/admin/users)
  - `src/app/admin.tsx` — Admin user management screen (search, toggle admin, cycle tier, soft-delete)
  - `supabase/migrations/003_admin_users.sql` — Admin role support, RLS recursion fix via security definer, table GRANTs
- **Files modified**:
  - `supabase/seed.sql` — Rewritten: added aud='authenticated', role='authenticated', auth.identities records, fixed null confirmed_at (generated column)
  - `api/models/schemas.py` — Added AdminUserResponse, AdminUserListResponse, AdminUserUpdate schemas
  - `api/main.py` — Registered admin router with "Admin" tag; added tags to all existing routers for Swagger
  - `src/app/_layout.tsx` — Registered admin screen route
  - `src/app/(tabs)/profile.tsx` — Added admin link (conditional on isAdmin)
  - `src/hooks/use-auth.tsx` — Added isAdmin field from public.users table
  - `src/lib/api-client.ts` — Added adminGetUsers, adminUpdateUser, adminDeleteUser methods
  - `src/lib/types.ts` — Added AdminUser, AdminUserListResponse, AdminUserUpdate types
- **Flow verified**:
  - All 3 seeded users log in via auth endpoint (admin@gardenify.app, test@gardenify.app, user2@gardenify.app)
  - Admin user lists 3 users via API; non-admin sees only their own profile (RLS enforced)
  - Admin can PATCH another user's is_admin field
  - DELETE returns 204 with correct RLS behavior (non-admin gets 403)
- **Tests status**: 73/73 Python tests pass, ruff clean, TypeScript clean (0 errors in app code), ESLint clean (0 warnings in app code)
- **Blocked**: Expo dev server couldn't start (port 8081 held by stale process; port 8082 timed out in non-interactive shell)
- **Next session**: Start Expo dev server and verify login on emulator; create PR

---

### 2026-07-29: UX Improvements + Playwright Fixes + Debug Endpoint

- **Duration**: ~45 min
- **Goal**: Fix Share button, add haptic feedback, add retry to no-match screen, fix backend server header, add debug endpoint, fix all Playwright tests
- **Files modified**:
  - `src/app/(tabs)/index.tsx` — Added `expo-haptics` import + haptic feedback on all buttons
  - `src/app/identification/[id].tsx` — Fixed Share button (uses `Share.share` with plant info), added retry+home buttons to no-match, added haptic to save/share
  - `api/main.py` — Removed `server` header `.pop()` that caused 500 errors; uvicorn uses `--no-server-header` flag
  - `api/routes/health.py` — Added `/api/debug` endpoint (version, python, uptime, config info)
  - `e2e/api-tests/health.spec.ts` — Rewrote >5 images test (Playwright multipart array bug → individual fields)
  - `e2e/api-tests/integration.spec.ts` — Added `uniqueJpeg()` to fix cache collision between tests
- **Dependencies installed**: expo-haptics
- **Key fix learned**: `response.headers.pop("server", None)` crashes in Starlette middleware — use `--no-server-header` uvicorn flag instead
- **Tests status**: 21/21 Playwright tests pass, backend healthy
- **Blocked**: Expo dev server started but port 8081 not reachable via tool; emulator started but UI testing deferred
- **Next session**: Test gallery picker → identification flow on emulator; create PR

---

### 2026-07-29: OpenCV Gate + Perceptual Hash Index + GBIF Download

- **Duration**: ~3 hours
- **Goal**: Add OpenCV image validation to backend, build perceptual hash index from GBIF images for offline matching
- **Files created**:
  - `api/services/image_processor.py` — OpenCV pipeline (edge detection, k-means color clustering, compression, thumbnail)
  - `api/routes/history.py` — History endpoints (GET /api/history, GET /api/history/{id}, GET /api/history/{id}/thumbnail/{index})
  - `api/services/local_identify.py` — Local identification matching using pHash from DB
  - `api/routes/admin.py` — (from previous session, now finalized)
  - `e2e/api-tests/fixtures/` — `leaf.jpg`, `flower.jpg` synthetic plant JPEGs
  - `scripts/build_hash_index.py` — GBIF image downloader + hash index builder
  - `scripts/generate-test-fixtures.py` — Synthetic plant JPEG generator
  - `.opencode/plugins/superpower-hooks.ts` — Service tracking, blocking detection
- **Files modified**:
  - `api/routes/identify.py` — Rewritten: OpenCV gate → local DB lookup → PlantNet only if local match
  - `api/services/perceptual_hash.py` — `getdata()` → `get_flattened_data()` (Pillow 12 compat)
  - `api/main.py` — Added PIL logging suppression
  - `api/models/schemas.py` — Added OpenCVResult, ImageStorage, History schemas
  - `e2e/api-tests/integration.spec.ts` — Uses fixture images, validates opencv/storage/exif/source fields
  - `e2e/api-tests/health.spec.ts` — Uses fixture images for JPEG test
  - `.gitignore` — Added uploads, logs, agent artifacts, samples
  - `opencode.json` — LSP/formatter/superpower plugin config
- **Key features**:
  - OpenCV `is_plant_like` gate rejects non-plant images (edge detection + color analysis)
  - `source: "local" | "plantnet"` in response — skips PlantNet when local DB has matches
  - Perceptual hash index: 1,960 species indexed (19.6% coverage), 0 download errors
  - Synthetic plant JPEGs pass OpenCV gate for E2E testing
  - `--no-server-header` uvicorn flag, PIL debug log suppression
- **Tests status**: 73/73 Python, 21/21 Playwright, 0 deprecation warnings

---

### 2026-07-30: PlantNet API Fix — Lang Param + Server Restart + Rose Identification Verified

- **Duration**: ~2 hours
- **Goal**: Fix "no match found" for rose image identification on emulator
- **Root causes** (3 bugs):
  1. **Reversed skip-gate** (`identify.py` L212): When local DB had no matches, PlantNet was skipped instead of being called as fallback
  2. **`lang` not allowed** (`plantnet.py`): PlantNet API v2 rejects `lang` field — removed from multipart body and curl command
  3. **Server never restarted**: All code edits were on disk but the original server (7h uptime) kept running with stale httpx code — had to kill PID 14652 and start fresh
- **Files modified**:
  - `api/services/plantnet.py` — Rewrote `_call_plantnet`: removed httpx (network issues in env), replaced with urllib + manual multipart with `_build_multipart()`; removed `lang` param
  - `api/routes/identify.py` — Fixed reversed PlantNet skip-gate logic; removed `lang` from `identify_plant`/`identify_disease` calls
  - `api/services/image_processor.py` — Added `compressed_data` to return dict; RGBA→RGB conversion in `compress_image` and `generate_thumbnail` (JPEG can't encode alpha)
  - `start_backend.bat` — Reverted to simple uvicorn launch
- **Key discovery**: PlantNet API v2 does NOT accept `lang` parameter — returns `{"statusCode":400,"message":"\"lang\" is not allowed"}`
- **Verification**: `/api/identify` with rose image returns `best_match: "Rosa lucieae"`, 10 results, `remaining_quota: 491`
- **Process management lesson**: `start /B` and `subprocess.Popen(DETACHED_PROCESS)` both block agent shell. Verified working: `start "" python -m uvicorn` (new window) and `subprocess.Popen(CREATE_NEW_CONSOLE)` from Python
- **Tests status**: 73/73 Python passed, TypeScript clean, ruff clean

### 2026-07-31: Species Detail Fix + Production Supabase Setup + GBIF Import

- **Duration**: ~3 hours
- **Goal**: Fix species detail crash, set up production Supabase, import GBIF species data
- **Bugs fixed**:
  - `species/[name].tsx:59` — `common_names.split(",")` crashed because API returns JSON array, not string. Fixed: `common_names ?? []` + `.join(", ")`
  - `src/lib/types.ts:105` — `SpeciesListItem.common_names` type changed `string` → `string[]`
- **Production Supabase setup**:
  - Linked project `amyriuhwqyalodsfkwzf` via `supabase link`
  - All 5 migrations applied manually via `supabase db query` + psycopg2 (multi-statement SQL not supported by CLI)
  - `uuid-ossp` extension enabled for `uuid_generate_v4()`
  - 10,008 GBIF species imported via batch upsert (100 per batch) from local SQLite
  - `load_dotenv()` added to `api/main.py` so `supabase_species.py` can read `.env.local`
  - `.env.local` updated with `USE_REMOTE=true` + production Supabase URL/keys
  - Backend now queries production Supabase for species
- **Files modified**:
  - `src/lib/types.ts` — `common_names` string → string[]
  - `src/app/species/[name].tsx` — `.split(",")` → `?? []` + `.join(", ")`
  - `src/__tests__/api-client.test.ts` — mock data updated (strings → arrays)
  - `api/main.py` — added `load_dotenv()` import + call
  - `api/config.py` — USE_REMOTE, supabase_effective_url, env_file loading
  - `api/routes/species.py` — `_get_backend()` checks `supabase_species.is_available()`
  - `api/services/supabase_species.py` — reads SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY from os.environ
  - `.env.local` — production Supabase config
- **Tests status**: TypeScript clean, 73/73 Python pass, ruff clean
- **Next session**: Create PR, deploy backend to Vercel

### 2026-07-31: Production Deployment — Vercel + EAS APK

- **Duration**: ~1.5 hours
- **Goal**: Deploy backend to Vercel production, build Android APK for distribution
- **Branch**: `feat/production-deployment`
- **Commits**:
  - `8974f07` — feat(deploy): production backend deployed, EAS secrets configured
- **What was done**:
  - ✅ **Vercel redeploy**: Moved 2,170 GBIF hash images (254MB) out of `api/` to fix bundle size (527MB → 267MB)
  - ✅ **Dev deps stripped**: Removed pytest, pytest-asyncio, ruff from production `requirements.txt`
  - ✅ **Backend verified**: `https://sasyakashi.vercel.app` — health OK, `use_remote=true`, species search works
  - ✅ **EAS.json updated**: Added `EXPO_PUBLIC_API_URL` to production profile (public URL only)
  - ✅ **EAS Secrets configured**: `EXPO_PUBLIC_SUPABASE_URL` + `EXPO_PUBLIC_SUPABASE_ANON_KEY` set via `eas secret:create` (not in git)
  - ✅ **APK built**: Production APK available on EAS
  - ✅ **PR created**: [#7 feat/production-deployment](https://github.com/luckyhegde6/gardenify/pull/7)
- **Files modified**:
  - `api/requirements.txt` — removed dev deps
  - `eas.json` — added EXPO_PUBLIC_API_URL env
- **Security fix**: Supabase credentials moved from `eas.json` to EAS Secrets (user review caught this)
- **Next session**: Merge PR, test APK on device, expand hash index, push notifications

### 2026-07-31: v0.1.0 Release — APK Built, Tested, Shipped

- **Duration**: ~30 min
- **Goal**: Build production APK, test on emulator against prod backend, ship v0.1.0
- **What was done**:
  - ✅ PR #7 merged to main
  - ✅ New production APK built (`eas build -p android --profile production`)
  - ✅ APK (85.6MB) installed + launched on Pixel_7_API_34 emulator (com.gardenify.app)
  - ✅ Production backend verified: health, debug, species search/detail, history all working
  - ✅ `git tag v0.1.0` pushed → GitHub Release created with APK attached
  - ✅ Release link: https://github.com/luckyhegde6/gardenify/releases/tag/v0.1.0
  - ✅ README/AGENTS/MEMORY links updated to point at GitHub Releases
- **Files modified**:
  - `README.md` — download links → GitHub Releases
  - `AGENTS.md` — APK distribution link → GitHub Releases
  - `MEMORY.md` — APK URL → release link
  - `.gitignore` — added `prodAPK/`, `gardenify-prod.apk`, `smoke-test.png`
- **Next session**: Expand hash index, push notifications, Play Store (later)

### 2026-07-31: Root-Cause Fix — APK Showed Expo Template Screen + New App Icon

- **Duration**: ~1 hour
- **Goal**: Diagnose why production APK "didn't work" on a real device, fix it, update the app icon
- **Branch**: `main`
- **What was done**:
  - ✅ **Root cause found**: `src/app/index.tsx` was the default Expo template placeholder ("Edit src/app/index.tsx..."). It's the `/` route, so it overrode the real app on every device (emulator + physical).
  - ✅ **Verified env was NOT the issue**: Extracted `assets/index.android.bundle` from v0.1.3 APK — contains `https://amyriuhwqyalodsfkwzf.supabase.co` and `https://sasyakashi.vercel.app/api`; no `localhost:54321` fallback.
  - ✅ **Fix**: Replaced `src/app/index.tsx` with auth-aware `Redirect` → `/(auth)/login` or `/(tabs)` via `useAuth()`.
  - ✅ **New app icon**: Generated leaf/sprout icon on brand blue→green gradient (`icon.png` 1024, adaptive foreground/background/monochrome, splash, favicon) via PIL script.
  - ✅ `app.json` — `ios.icon` now points at `./assets/images/icon.png` (was the default `expo.icon` composer).
  - ✅ Typecheck + lint pass.
  - 🔄 **In progress**: EAS production APK build (`1ecadb49`) running for verification.
- **Files modified**:
  - `src/app/index.tsx` — template placeholder → auth redirect
  - `assets/images/icon.png`, `android-icon-{foreground,background,monochrome}.png`, `splash-icon.png`, `favicon.png` — new branded icon
  - `app.json` — iOS icon path
  - `BUGS.md` — added BUG-007
- **Tests status**: TypeScript clean, lint clean (APK verification pending)
- **Next session**: Install rebuilt APK on emulator, confirm real screens load, then tag `v0.1.4` to release the fixed APK via CI

---

### 2026-08-01: Backend Deploy Fixed — Moved into Release Flow

- **Duration**: ~2 hours
- **Goal**: Fix the broken Vercel production deploy (token invalid → uv missing → `lstat ENOENT`), then align deploy with the intended release process
- **Branch**: `main` (via PRs #10–#14)
- **What was done**:
  - ✅ **Token fixed**: replaced expired `VERCEL_TOKEN` env secret with `vcp_1vJDJ...` (validated via `vercel whoami` → luckyhegde6); set via `gh secret set --env production`
  - ✅ **uv fix (#10)**: `vercel build` needs `uv` on the runner → added `pip install uv`
  - ✅ **Root-caused `lstat ENOENT`**: Vercel's deploy manifest syncs the git tree; any git-tracked file excluded by `.vercelignore` breaks the sync. Deny-list failed on `.agents/*.md` (#11 allowlist made it worse → `__mocks__/...`)
  - ✅ **`.vercelignore` corrected (#13)**: only excludes untracked/generated files — verified no remaining pattern matches a git-tracked path
  - ✅ **CLI pinned (#12)**: `vercel@58.4.4` + `--force` (did not fix alone — confirmed manifest issue)
  - ✅ **Deploy flow redesigned (#14)**: removed `deploy-backend.yml`; added `deploy-backend` job to `release.yml` running AFTER `create-release` via direct `vercel deploy --prod` (server-side build, no local `.vercel/python/.venv` artifacts)
  - ✅ **Vercel project setting**: restored `commandForIgnoringBuildStep` to skip production on git pushes (no premature auto-deploys; prod deploys only via release workflow)
- **Files modified**:
  - `.github/workflows/deploy-backend.yml` — deleted
  - `.github/workflows/release.yml` — added `deploy-backend` job
  - `.vercelignore` — only untracked files
  - `.github/workflows/deploy-backend.yml` (before deletion) — uv + CLI pin + direct deploy (reverted via deletion)
- **Tests status**: TypeScript clean, lint clean, 73/73 Python pass, all PRs #10–#14 CI checks green
- **Next session**: Cut next tag to run the new release flow end-to-end; verify `deploy-backend` job reaches production (species `images` key fix pending)

---

### 2026-08-02: Identify 500 Fix + Release Notes + v0.1.5 Verification

- **Duration**: ~1.5 hours
- **Goal**: Fix production `/api/identify` 500 (read-only FS on Vercel), publish release-notes template, verify v0.1.5 release + prod seed users
- **Branch**: `main` (via PRs #16, #17)
- **What was done**:
  - ✅ **Read-only FS 500 fixed (#16)**: `ImageProcessor` resolves a writable upload dir — probes `api/data/uploads`, falls back to `<tempdir>/gardenify-uploads` on Vercel (`/var/task` is read-only, only `/tmp` writable). Storage writes best-effort: on failure `storage` returns `{}`, in-memory `compressed_data` still flows to PlantNet. `history.py` imports `UPLOAD_DIR` from image_processor.
  - ✅ **4 new tests** (`api/tests/test_image_processor.py`): default writable, temp fallback, write-failure resilience, normal storage path. 77/77 Python pass, ruff clean, tsc clean.
  - ✅ **Release notes template (#17)**: `release.yml` body now has What's New / Bug Fixes / Enhancements / What's Changed (PRs) placeholders.
  - ✅ **Both PRs merged** (squash); Vercel auto-deployed prod build `gardenify-7h7o4wo4x` (Ready, aliased to `sasyakashi.vercel.app`).
  - ✅ **Prod verified**: `POST /api/identify` now returns HTTP 400 (plant-detection validation) instead of read-only FS 500.
  - ✅ **Issue #18 filed & closed** documenting the bug + fix.
  - ✅ **v0.1.5 release flow confirmed** — APK (89.5MB) installed on `emulator-5554`, launches; seed users `admin@`/`test@`/`user2@` synced to prod Supabase via Auth Admin API.
- **Files modified**:
  - `api/services/image_processor.py` — `_resolve_upload_dir()` (temp fallback), best-effort storage writes
  - `api/routes/history.py` — import `UPLOAD_DIR` from image_processor (dropped duplicate Path)
  - `api/tests/test_image_processor.py` — new test file (4 tests)
  - `.github/workflows/release.yml` — release-notes body placeholders
  - `.agents/handoff-current.md`, `.agents/session-todos.md`, `.agents/sessions.md`, `MEMORY.md` — updated
- **Tests status**: 77/77 Python, ruff clean, `npx tsc --noEmit` clean, all CI checks green
- **Next session**: Fix Supabase prod auth config (Site URL/redirects → app, not localhost); investigate `public.users` missing profile rows for Auth users ("verified but cannot login"); re-test v0.1.5 APK against prod

---

### 2026-08-02: Deploy Size Fix + Thumbnail Persistence + GBIF Seed

- **Duration**: ~2 hours
- **Goal**: Get Vercel bundle under 500MB, persist history images in Supabase, move GBIF processing server-side
- **Branch**: `feat/branded-404-favicon-sitemap` (PR #20), committing onto this branch per user choice
- **Root cause**: Vercel bundle hit 611MB because `api/data/gbif/plantnet_observations.zip` (412MB) shipped despite `.vercelignore` entries
- **What was done**:
  - ✅ Moved 412MB zip out of repo → `C:\Users\lucky\AppData\Local\Temp\opencode\plantnet_observations.zip`
  - ✅ `.vercelignore` now excludes `api/data/gardenify.db-journal`, `api/data/uploads/`, `api/data/plantnet-300k/`, `api/data/hashes/`, `api/data/geoplant/`, `**/__pycache__/`
  - ✅ Preview deploy verified: upload 344MB → **82.1KB**, bundle 611MB → **268MB**, build successful
  - ✅ GBIF → Supabase seed: `api/data/importers/seed_supabase_gbif.py` + `.github/workflows/seed-gbif.yml` (dispatch + weekly cron); prod species route already reads Supabase
  - ✅ History images persisted in DB: migration `supabase/migrations/006_thumbnail_data.sql` (`image_thumbnails text[]`); `image_processor.py` emits compressed `thumbnail_data_url`; identify route passes it through; history list maps to `thumbnail_urls`; `serve_thumbnail` reads DB base64 first with legacy fallback; app inserts/stores `image_thumbnails`
  - ✅ Migration 006 applied to prod Supabase (image_thumbnails live)
  - ✅ `seed_supabase_gbif` run against prod — completed (0 inserted, 10,000 updated)
  - ✅ **Seed data-loss bug found & fixed**: jsonb fields sent as `json.dumps` strings + blind `upsert` wiped 10,008 enriched `common_names`/`native_regions` rows. Restored from local SQLite (all rows back as proper JSON arrays), seed rewritten (`_to_list()` normalizer + merge-preserve non-empty existing fields), tests updated; LESSONS.md logged. Verified idempotent on re-run (enriched data preserved, 0 corrupted rows)
  - ✅ Tests: 86 passed, ruff clean, `npx tsc --noEmit` clean, `npm run lint` clean
- **Files modified**:
  - `.vercelignore`, `api/models/schemas.py`, `api/routes/history.py`, `api/routes/identify.py`, `api/services/image_processor.py`, `api/tests/test_gbif_import.py`, `api/tests/test_image_processor.py`, `src/app/(tabs)/history.tsx`, `src/app/(tabs)/index.tsx`, `src/lib/types.ts`, `api/data/importers/seed_supabase_gbif.py`
  - New: `.github/workflows/seed-gbif.yml`, `supabase/migrations/006_thumbnail_data.sql`
- **Tests status**: 86/86 Python, ruff clean, tsc clean, lint clean
- **Next session**: Deploy fixed bundle to prod + verify `/api/health`; recheck PlantNet 404/401 identify failure

---

### 2026-08-02: Remove SQLite Entirely → Supabase-Only Backend (planning + investigation)

- **Duration**: ~1 hour
- **Goal**: Plan and start the user-requested refactor to eliminate SQLite from the backend — `local_identify` must hit Supabase (Vercel + local), all importers write to Supabase, and OpenCV best practices applied to image identification
- **Branch**: `feat/branded-404-favicon-sitemap` (PR #20 open) — refactor not yet implemented
- **What was done (investigation only, no code changes yet)**:
  - ✅ Confirmed Vercel root cause: `api/data/gardenify.db` in `.vercelignore` never ships → `sqlite3.connect()` fails → "Local identification failed: unable to open database file"
  - ✅ Mapped every file referencing `local_db`/`local_identify`: routes (`identify.py`, `species.py`), `main.py` startup init, importers (`seed_species.py`, `import_gbif.py`, `import_plantnet300k.py`, `build_hash_index.py`, `run_all.py`), `scripts/build_hash_index.py`, tests (`conftest.py`, `test_species_routes.py`, `test_identify_offline.py`, `test_gbif_import.py`, `test_local_db.py`)
  - ✅ Verified local SQLite data: 10,008 species, **1,960 image_hashes** (phash/dhash, `{species_id}\img.jpg`, 16-char hex). Supabase species ids are BIGSERIAL → hash mapping must go via `scientific_name`
  - ✅ Confirmed Supabase `species` schema (migration 002), jsonb fields, RLS pattern; `supabase_species.py` `get_hash_count()` hardcoded to 0
  - ✅ Documented full 15-step refactor plan in `.agents/session-todos.md` + `.agents/handoff-current.md`
  - ✅ Clarified scope with user: **remove SQLite entirely** + **apply OpenCV improvements and document**
- **Files modified**: `.agents/session-todos.md`, `.agents/handoff-current.md` (refactor plan + state), this file
- **Tests status**: not run (no code changes); last known green 86/86 Python
- **Next session**: Implement refactor per plan — start with migration `008_image_hashes_table.sql` + `supabase_species.py` extension

---

### 2026-08-03: Remove SQLite Entirely → Supabase-Only Backend (IMPLEMENTATION + E2E verification)

- **Duration**: ~3 hours
- **Goal**: Execute the planned refactor — kill SQLite, all importers→Supabase, `local_identify`→Supabase, apply OpenCV best practices, verify locally + on emulator.
- **Branch**: `main`
- **What was done**:
  - ✅ Deleted `local_db.py`, `schema.sql`, `gardenify.db`; removed sqlite lines from `.vercelignore`; removed `main.py` local-DB init/seed.
  - ✅ Rewrote all importers to Supabase via shared `seed_supabase_gbif.seed_supabase_gbif_from_list()`: `seed_species.py`, `import_gbif.py`, `import_plantnet300k.py`, `build_hash_index.py`, `run_all.py`.
  - ✅ Extended `supabase_species.py`: `find_by_phash`, `insert_image_hash`, `get_species_images`, real `get_hash_count`, `get_species_id_map`.
  - ✅ Rewrote `local_identify.py` → Supabase only; `identify.py`/`species.py` gates on `supabase_species.is_available()`. `find_by_phash` graceful on PostgREST 404 (migration 008 not on prod yet).
  - ✅ Added migration `008_image_hashes_table.sql` (image_hashes FK, phash/dhash/category, RLS).
  - ✅ Rewrote tests with in-memory `FakeSupabaseClient` + `patched_supabase` fixture — 91 tests pass, ruff clean, tsc clean.
  - ✅ OpenCV best practices applied to `image_processor.py` (GaussianBlur→Canny, variance-of-Laplacian blur threshold 100.0, HSV green ratio); `OpenCVResult` gained `sharpness`/`is_blurry`/`green_ratio`; added 4 tests.
  - ✅ E2E on emulator: started local backend w/ prod Supabase; installed `com.gardenify.app` (standalone) logged in via prod auth (created `devtest@gardenify.app` via service-role admin API), picked gallery image, identified → **Monstera deliciosa 81.7%** rendered (taxonomy + care). `POST /api/identify` → 200.
  - ⏭ Deferred for next session: apply migration 008 + seed hashes to prod (needs 20-30 min run).
- **Tests status**: 91/91 Python, ruff clean, `npx tsc --noEmit` clean
- **Next session**: apply migration 008 + seed hashes to prod (~20-30 min), then commit this session.

---

## Session Rules

1. **Before commit**: Update this file with what was done
2. **After commit**: Note commit hash and what changed
3. **At session end**: Update handoff-current.md with next steps
4. **When blocked**: Document in LESSONS.md with workaround

## Session: Auth security (forgot pw + admin reset + rate limiting)

- Backend: new /api/auth/login (3-failure lockout), /api/auth/forgot-password (reset-once), /api/auth/reset-password (verify recovery code + set pw)
- Backend: admin POST /admin/users/{id}/reset-password (sets default) ; shared deps.py (get_service_client, require_user, require_admin)
- Mobile: login now routes through backend + setSession; Forgot Password button + forgot-password screen; reset-password deep-link screen; admin Reset Password button
- Tests: 95 Python (4 new auth_security), ruff clean, tsc clean, lint clean

## Session: Release v1.1.0 (auth/login)

- Deployed backend to prod manually (vercel --prod) � auth endpoints live (auto-deploy unreliable)
- Bumped 1.0.0 -> 1.1.0 (package.json, app.json, api/main.py, HealthResponse); CHANGELOG + LESSONS updated; release/v1.1.0 PR opened
- Next: tag v1.1.0 after merge -> release.yml (EAS APK + GitHub Release + backend deploy)

## Session: v1.1.0 Build Fix (brace-expansion) + Reset Feature Verification

- Tag v1.1.0 pushed; release.yml run 30889700141 FAILED at Build APK (EAS)
- Root cause: package.json override brace-expansion 5.0.9 (ESM-only) broke RN codegen (minimatch@3.1.5 needs CJS expand()); pinned to 2.1.4 (0 vulns)
- Verified: local release build (gradlew app:assembleRelease) SUCCEEDS after fix; app boots, auth UI renders, client validation works
- Tested forgot-password end-to-end on prod build: app shows "Reset Link Sent"; email delivered (luckyhegdedev@gmail.com)
- Diagnosed reset completion gaps: (1) Supabase redirect allowlist missing gardenify:// -> recovery email links to web localhost:3000 (CONFIRMED); (2) reset-password.tsx expects ?code=&email= but Supabase sends token= query / access_token fragment
- Created fix/brace-expansion-override branch; updated LESSONS.md + handoff + sessions
- Next: commit+PR the fix, then re-cut v1.1.0 (re-tag or bump)
