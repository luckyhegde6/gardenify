# Phase 1: MVP

> Goal: User can capture a plant image, identify it via PlantNet, see results, and save to history.

## Sprint 1 — Foundation (Days 1-5)

### Backend (Python/FastAPI)

- [ ] Initialize FastAPI project structure in `api/`
- [ ] Create `api/requirements.txt` with fastapi, python-multipart, supabase, requests, pydantic
- [ ] Create `api/config.py` with Pydantic BaseSettings for env vars
- [ ] Create `api/models/schemas.py` with Pydantic request/response models
- [ ] Create `api/main.py` with FastAPI app, CORS, error handlers
- [ ] Implement `api/services/plantnet.py` — PlantNet API client
  - [ ] POST to `https://my-api.plantnet.org/v2/identify/all`
  - [ ] Handle multipart form data (images + organs)
  - [ ] Parse response into structured format
  - [ ] Handle PlantNet errors (429 quota, 400 bad image, etc.)
- [ ] Implement `api/routes/identify.py` — POST /api/identify
  - [ ] Accept multipart image upload (1-5 images)
  - [ ] Validate: JPEG/PNG only, <10MB each, total <50MB
  - [ ] Forward to PlantNet API
  - [ ] Return formatted results
- [ ] Implement `api/routes/health.py` — GET /api/health
- [ ] Create `api/vercel.json` for Vercel deployment
- [ ] Test locally with `vercel dev`

### Database (Supabase)

- [ ] Create Supabase project (or use local via `supabase start`)
- [ ] Create `supabase/migrations/001_initial_schema.sql`
  - [ ] `profiles` table (id, email, full_name, avatar_url, role, created_at)
  - [ ] `identifications` table (id, user_id, image_urls, organs, best_match, scientific_name, common_names, family, genus, confidence_score, all_results, created_at)
  - [ ] `favorites` table (id, user_id, scientific_name, created_at)
  - [ ] RLS policies for all tables (users see own data only)
  - [ ] Indexes for query performance
- [ ] Create `supabase/seed.sql` with admin user
- [ ] Create `plant-images` storage bucket (private)
- [ ] Create storage RLS policies (owner read/write)

### Mobile App (Expo)

- [ ] Install dependencies:
  - [ ] `npx expo install expo-image-picker expo-camera`
  - [ ] `npx expo install @supabase/supabase-js`
  - [ ] `npx expo install @react-native-async-storage/async-storage`
  - [ ] `npx expo install expo-secure-store`
  - [ ] `npx expo install expo-image-manipulator`
  - [ ] `npx expo install expo-crypto`
- [ ] Create `src/lib/supabase.ts` — Supabase client with SecureStore adapter
- [ ] Create `src/lib/api.ts` — Backend API client
- [ ] Create `src/lib/types.ts` — TypeScript interfaces
- [ ] Create auth flow:
  - [ ] `src/app/(auth)/login.tsx` — Login screen
  - [ ] `src/app/(auth)/register.tsx` — Register screen
  - [ ] `src/components/auth-guard.tsx` — Redirect if not authenticated
  - [ ] `src/hooks/use-auth.ts` — Session management hook
- [ ] Build scan screen:
  - [ ] `src/app/(tabs)/index.tsx` — Camera capture + gallery picker
  - [ ] `src/components/camera-capture.tsx` — Image picker component
  - [ ] Image compression (1024px, JPEG 0.8)
  - [ ] Image hashing (SHA-256)
  - [ ] Organ selection UI (auto/leaf/flower/fruit/bark)
- [ ] Build result screen:
  - [ ] `src/app/identification/[id].tsx` — Species result detail
  - [ ] `src/components/result-card.tsx` — Species display with confidence
- [ ] Build history screen:
  - [ ] `src/app/(tabs)/history.tsx` — Past identifications list
  - [ ] `src/components/identification-item.tsx` — List item
- [ ] Build profile screen:
  - [ ] `src/app/(tabs)/profile.tsx` — User info + logout
- [ ] Update `src/app/_layout.tsx` — Root layout with auth provider
- [ ] Update `src/components/app-tabs.tsx` — Tab navigator with Scan/History/Profile

## Sprint 2 — Polish & Ship MVP (Days 6-10)

- [ ] Error handling across all screens
  - [ ] Network error states
  - [ ] PlantNet failure states
  - [ ] Empty states for history
- [ ] Loading states and skeleton loaders
- [ ] Multi-image support (up to 5 images per identification)
- [ ] Pull-to-refresh on history screen
- [ ] Configure `app.json`:
  - [ ] App name: "Gardenify"
  - [ ] Permissions: camera, photos
  - [ ] Deep linking scheme
- [ ] Create `.env.example` with all required env vars
- [ ] Android build test: `npx expo run:android`
- [ ] End-to-end testing:
  - [ ] Register → login → scan → identify → view result → view history → logout
- [ ] Write backend tests:
  - [ ] `api/tests/test_identify.py`
  - [ ] `api/tests/test_health.py`
  - [ ] `api/tests/conftest.py`

## Acceptance Criteria

1. User can register with email/password and log in
2. User can capture photo or pick from gallery
3. Image is compressed and uploaded to Supabase Storage
4. Backend forwards to PlantNet and returns species identification
5. Results display with species name, confidence score, common names
6. Identification is saved to user's history
7. User can browse past identifications
8. Android build runs without crashes
9. All backend tests pass
10. RLS policies enforce user-scoped data access
