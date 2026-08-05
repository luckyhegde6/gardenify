# Memory — Mobile App Structure & Local Dev

## Structure

```
src/
  app/
    _layout.tsx              # Root: AuthProvider + Stack + ROOT AUTH GUARD (useSegments/router)
    index.tsx                # Initial redirect (entry)
    (auth)/
      _layout.tsx            # Auth stack
      login.tsx              # Login with email/password
      register.tsx           # Register with password validation
    (tabs)/
      _layout.tsx            # 4-tab bottom navigator
      index.tsx              # Scan: camera + gallery + organ selector
      favorites.tsx          # Favorites list
      history.tsx            # Past identifications
      profile.tsx            # User info + sign out (footer: Gardenify v{app.json version})
    identification/
      [id].tsx               # Results detail (species, disease, care, share)
    species/
      [name].tsx             # Species detail (taxonomy + external links)
  components/
    button.tsx               # 5 variants, 3 sizes
    plant-card.tsx           # Card with confidence bar
    loading.tsx              # Loading spinner + overlay
  hooks/
    use-auth.tsx             # Auth context + provider
    use-identification.ts    # Identify plant via API
    use-camera.ts            # Camera/gallery picker
    use-settings.ts          # Language/theme settings
  lib/
    supabase.ts              # Supabase client (SecureStore adapter)
    api-client.ts            # Backend API client
    types.ts                 # TypeScript types matching backend schemas
    cache.ts                 # AsyncStorage result cache (24h TTL)
    share.ts                 # Share module
  constants/
    theme.ts                 # Colors, spacing, typography, shadows
```

## Auth Navigation Guard (2026-08-06)

- `src/app/_layout.tsx` root guard (useSegments + router.replace): `!user` outside `(auth)` → `/(auth)/login`; `user` in `(auth)` except `reset-password` → `/(tabs)`. Fixes sign-out dead-end + login no-transition (initial-route `<Redirect>` only ran once).
- Version single-source: `api/config.py` `app_version = "1.1.0"`; health/debug/schemas/main read it; Profile footer reads `app.json` via `Constants.expoConfig?.version`.
- Verified on emulator (prod-baked build `e4cd16d5`): logout → Login + session cleared; login → Home in-app; session persists on restart; footer `Gardenify v1.1.0`.
- EAS submit gotcha: hang at "Computing project fingerprint" → use `EAS_SKIP_AUTO_FINGERPRINT=1`; cancel duplicate builds (`eas build:cancel <id>`).

## Local Development

```bash
# Quick start
npm install
npx expo start

# Backend (separate terminal)
cd api
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Verify (all 4 must pass)
npx tsc --noEmit          # TypeScript (0 errors)
cd api && pytest          # Python tests (86 passing)
npx expo lint             # Lint (0 errors)
npx jest --no-cache       # Frontend tests (41 passing)
npx playwright test e2e/api-tests/ --reporter=list   # E2E (21 passing)
```

## Windows Server Start (non-blocking)

```bash
# Detached backend (never blocks the shell)
powershell -Command "Start-Process -FilePath 'cmd' -ArgumentList '/c cd /d F:\Local_git\gardenify && python -m uvicorn api.main:app --reload --port 8000' -WindowStyle Normal"
```
