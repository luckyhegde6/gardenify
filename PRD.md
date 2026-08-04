# PRD Checklist — Gardenify MVP

> Product Requirements Document. Check items as they're completed.

## Core Features

### Authentication

- [x] User can register with email/password
- [x] User can log in
- [x] User can log out
- [x] Session persists across app restarts (SecureStore)
- [x] Password validation (min 8 chars)
- [x] Error messages for invalid credentials
- [x] Forgot-password flow (recovery email + one-time reset link) — app parses `token`/`access_token` deep-link params; backend rate-limits one pending reset per email
- [x] Landing page documents register / login / reset steps

### Plant Identification

- [x] User can capture photo with camera
- [x] User can pick photo from gallery
- [x] Image is compressed (JPEG 0.8 quality)
- [x] Image is validated (backend-side)
- [x] User can select organ type (auto/leaf/flower/fruit/bark)
- [x] User can upload up to 5 images per identification
- [x] Loading state while identifying
- [x] Results show species name + confidence score
- [x] Results show common names
- [x] Results show taxonomy (family, genus)
- [ ] Identification is saved to history (Supabase storage integration pending)

### Disease Detection

- [x] Disease detection runs alongside species ID (backend)
- [x] Results show disease name + confidence
- [x] Results show description + treatment
- [x] Graceful degradation if disease API fails

### Plant Care

- [x] Results include care instructions
- [x] Watering info (frequency, amount, method)
- [x] Sunlight info (preference, hours)
- [x] Soil info (type, pH, drainage)
- [x] Temperature info (min/max, frost tender)
- [x] Growth info (height, spread, rate)
- [x] Propagation info (methods, difficulty)
- [x] Humidity, toxicity, common pests

### History

- [x] User can view past identifications
- [x] List shows species name + date
- [x] User can tap to view full result
- [x] Pull-to-refresh
- [x] Empty state when no history

### Profile

- [x] User can view profile info
- [x] User can log out from profile
- [x] Display user email

## Technical Requirements

### Backend

- [x] FastAPI server runs locally
- [x] `/api/health` returns status
- [x] `/api/identify` processes images (OpenCV gate + local DB + PlantNet)
- [x] `/api/debug` shows config (dev only)
- [x] `/api/history` returns past identifications
- [x] `/api/species` fuzzy search
- [x] PlantNet API integration works
- [x] Caching reduces duplicate API calls (SHA-256 + 1hr TTL)
- [x] EXIF metadata extraction works
- [x] Structured logging with correlation IDs
- [x] OpenCV image validation (edge detection, color analysis, content score)
- [x] Image compression + thumbnail generation + server-side storage
- [x] Perceptual hash index for offline matching (1,960 species)
- [x] CORS configured for Expo dev

### Database

- [x] Supabase project created
- [x] `users` table exists
- [x] `identifications` table exists
- [x] `favorites` table exists
- [x] `user_settings` table exists
- [x] RLS policies on all tables
- [x] Indexes for query performance
- [ ] Storage bucket for plant images
- [x] Seed data scripts (make seed)

### Mobile

- [x] Expo project builds for Android
- [x] Camera permission requested
- [x] Gallery permission requested
- [x] SecureStore used for tokens
- [x] API URL from environment variable (EXPO_PUBLIC_API_URL)
- [x] Error handling on all screens (Alert + error states)
- [x] Loading states on all screens

### CI/CD

- [x] GitHub Actions lint passes
- [x] GitHub Actions typecheck passes
- [x] GitHub Actions Python tests pass
- [x] EAS build succeeds
- [x] Vercel deployment works
- [x] Supabase migrations run

## Security

- [x] No hardcoded secrets in code (gitleaks + detect-secrets pre-commit)
- [x] PlantNet API key server-side only
- [x] Supabase service key never exposed
- [x] RLS enforces user-scoped access
- [x] Input validation on all endpoints (Pydantic + FastAPI)
- [x] Rate limiting considered (PlantNet 500/day via cache + local DB fallback)

## Code Quality

- [x] TypeScript strict mode
- [x] Python type hints
- [x] No `any` types in TypeScript
- [x] No bare `except` in Python
- [x] Pre-commit hooks installed
- [x] All tests pass
- [x] Lint passes

## Documentation

- [x] README.md exists
- [x] .env.example with all vars
- [x] API docs (Swagger/OpenAPI)
- [x] Architecture diagram
- [x] Agent instructions (AGENTS.md)
- [x] Lessons learned (LESSONS.md)
- [x] PRD checklist (this file)

## Nice to Have (Phase 2)

- [x] Favorites/bookmarks
- [x] Share results
- [ ] Offline mode (backend ready, mobile pending)
- [ ] Push notifications
- [ ] Dark mode
- [x] Localization (en/fr/es settings hook)
- [x] Disease detection UI
- [x] Species detail pages
- [x] Image cropping
- [x] Result caching

---

**Last updated**: 2026-07-31
**Current progress**: Species detail crash fixed, production Supabase linked + migrations applied + 10,008 GBIF species imported, backend configured for remote

### Admin User Management

- [x] Admin API endpoints (GET/PATCH/DELETE /api/admin/users)
- [x] Admin mobile screen (search, toggle admin, cycle tier, soft-delete)
- [x] JWT-protected admin routes
- [x] RLS recursion fix via security definer
- [x] Seed SQL includes is_admin users + identities
