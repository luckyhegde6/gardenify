# PRD Checklist — Gardenify MVP

> Product Requirements Document. Check items as they're completed.

## Core Features

### Authentication
- [ ] User can register with email/password
- [ ] User can log in
- [ ] User can log out
- [ ] Session persists across app restarts
- [ ] Password validation (min 8 chars)
- [ ] Error messages for invalid credentials

### Plant Identification
- [ ] User can capture photo with camera
- [ ] User can pick photo from gallery
- [ ] Image is compressed (1024px, JPEG 0.8)
- [ ] Image is validated (JPEG/PNG only, <10MB)
- [ ] User can select organ type (auto/leaf/flower/fruit/bark)
- [ ] User can upload up to 5 images per identification
- [ ] Loading state while identifying
- [ ] Results show species name + confidence score
- [ ] Results show common names
- [ ] Results show taxonomy (family, genus)
- [ ] Identification is saved to history

### Disease Detection
- [ ] Disease detection runs alongside species ID
- [ ] Results show disease name + confidence
- [ ] Results show description + treatment
- [ ] Graceful degradation if disease API fails

### Plant Care
- [ ] Results include care instructions
- [ ] Watering info (frequency, amount, method)
- [ ] Sunlight info (preference, hours)
- [ ] Soil info (type, pH, drainage)
- [ ] Temperature info (min/max, frost tender)
- [ ] Growth info (height, spread, rate)
- [ ] Propagation info (methods, difficulty)
- [ ] Humidity, toxicity, common pests

### History
- [ ] User can view past identifications
- [ ] List shows species name + date
- [ ] User can tap to view full result
- [ ] Pull-to-refresh
- [ ] Empty state when no history

### Profile
- [ ] User can view profile info
- [ ] User can log out from profile
- [ ] Display user email

## Technical Requirements

### Backend
- [ ] FastAPI server runs locally
- [ ] `/api/health` returns status
- [ ] `/api/identify` processes images
- [ ] `/api/debug` shows config (dev only)
- [ ] PlantNet API integration works
- [ ] Caching reduces duplicate API calls
- [ ] EXIF metadata extraction works
- [ ] Structured logging with correlation IDs
- [ ] CORS configured for Expo dev

### Database
- [ ] Supabase project created
- [ ] `users` table exists
- [ ] `identifications` table exists
- [ ] `favorites` table exists
- [ ] `user_settings` table exists
- [ ] RLS policies on all tables
- [ ] Indexes for query performance
- [ ] Storage bucket for plant images

### Mobile
- [ ] Expo project builds for Android
- [ ] Camera permission requested
- [ ] Gallery permission requested
- [ ] SecureStore used for tokens
- [ ] API URL from environment variable
- [ ] Error handling on all screens
- [ ] Loading states on all screens

### CI/CD
- [ ] GitHub Actions lint passes
- [ ] GitHub Actions typecheck passes
- [ ] GitHub Actions Python tests pass
- [ ] EAS build succeeds
- [ ] Vercel deployment works
- [ ] Supabase migrations run

## Security

- [ ] No hardcoded secrets in code
- [ ] PlantNet API key server-side only
- [ ] Supabase service key never exposed
- [ ] RLS enforces user-scoped access
- [ ] Input validation on all endpoints
- [ ] Rate limiting considered

## Code Quality

- [ ] TypeScript strict mode
- [ ] Python type hints
- [ ] No `any` types in TypeScript
- [ ] No bare `except` in Python
- [ ] Pre-commit hooks installed
- [ ] All tests pass
- [ ] Lint passes

## Documentation

- [ ] README.md exists
- [ ] .env.example with all vars
- [ ] API docs (Swagger/OpenAPI)
- [ ] Architecture diagram
- [ ] Agent instructions (AGENTS.md)
- [ ] Lessons learned (LESSONS.md)

## Nice to Have (Phase 2)

- [ ] Favorites/bookmarks
- [ ] Share results
- [ ] Offline mode
- [ ] Push notifications
- [ ] Dark mode
- [ ] Localization

---

**Last updated**: 2026-07-27
**Current progress**: Backend complete, mobile UI not started
