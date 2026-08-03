# Gardenify 🌿

> **Identify any plant, flower, leaf, or fruit with your camera — powered by PlantNet AI.**

[![CI](https://github.com/luckyhegde6/gardenify/actions/workflows/lint.yml/badge.svg)](https://github.com/luckyhegde6/gardenify/actions/workflows/lint.yml)
[![Backend](https://img.shields.io/badge/Backend-Live-black)](https://sasyakashi.vercel.app)
[![Expo](https://img.shields.io/badge/Expo-SDK%2055-blue)](https://expo.dev/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Live API:** [sasyakashi.vercel.app](https://sasyakashi.vercel.app) · **Swagger:** [docs](https://sasyakashi.vercel.app/docs)

Gardenify is a plant identification mobile app for **Android**, built with **Expo (React Native)**. Point your camera at any plant, flower, leaf, fruit, or bark — Gardenify returns species identification with confidence scores, common names, taxonomy, disease detection, and tailored plant-care instructions.

---

## ✨ Features

- 📷 **Instant identification** — photo or gallery, PlantNet AI for 50,000+ species
- 🧠 **Smart pipeline** — OpenCV plant-likeness gate + SHA-256 cache save API quota; a **perceptual-hash species store** answers known plants instantly
- 🗂️ **History & Favorites** — revisit past identifications, save plants for quick reference
- 🛡️ **Secure by default** — Supabase Row Level Security, server-side API keys, tokens in `expo-secure-store`
- 🧑‍💼 **Admin dashboard** — role/tier management with least-privilege JWT gating
- 🚀 **OTA-ready** — expo-router navigation, EAS Build + Update, GitHub Actions CI/CD

---

## 🏗️ Architecture

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

The mobile app talks to both the FastAPI backend and Supabase (auth + storage + RLS-protected data) directly. The backend owns PlantNet proxying, image processing, species matching, and history/favorites APIs.

---

## 🧰 Tech Stack

| Layer    | Technology                                         |
| -------- | -------------------------------------------------- |
| Mobile   | Expo SDK 55 (React Native, TypeScript 5.9)         |
| Backend  | FastAPI on [Vercel](https://sasyakashi.vercel.app) |
| Database | [Supabase](https://supabase.com) (PostgreSQL, RLS) |
| Plant AI | PlantNet API v2 (records → local species matching) |
| Auth     | Supabase Auth (email/password, JWT)                |
| Storage  | Supabase Storage                                   |
| Build    | EAS Build (APK) + Update                           |
| CI/CD    | GitHub Actions (6 workflows)                       |

---

## 🔌 API

**Swagger (interactive):** [sasyakashi.vercel.app/docs](https://sasyakashi.vercel.app/docs) · **OpenAPI:** [sasyakashi.vercel.app/openapi.json](https://sasyakashi.vercel.app/openapi.json) · **Base URL:** `https://sasyakashi.vercel.app`

| Method   | Endpoint                           | Description                                       |
| -------- | ---------------------------------- | ------------------------------------------------- |
| `GET`    | `/api/health`                      | Health check + version                            |
| `POST`   | `/api/identify`                    | Identify plant from images (multipart/form-data)  |
| `GET`    | `/api/species?q={query}&limit={n}` | Fuzzy search 10,008 species                       |
| `GET`    | `/api/species/{id}`                | Species details by ID                             |
| `GET`    | `/api/species/by-name/{name}`      | Species by scientific name                        |
| `GET`    | `/api/history`                     | Past identifications (list + detail + thumbnails) |
| `GET`    | `/api/admin/users`                 | List users _(admin, JWT)_                         |
| `PATCH`  | `/api/admin/users/{id}`            | Update role / tier _(admin, JWT)_                 |
| `DELETE` | `/api/admin/users/{id}`            | Soft-delete user _(admin, JWT)_                   |

### Authentication

Public endpoints need **no auth**. Admin endpoints require a Supabase JWT whose user has `is_admin = true`:

```text
Authorization: Bearer <supabase_jwt_token>
```

### Example calls

```bash
# Health
curl https://sasyakashi.vercel.app/api/health

# Identify a plant
curl -X POST https://sasyakashi.vercel.app/api/identify -F "images=@plant_photo.jpg"

# Search species
curl "https://sasyakashi.vercel.app/api/species?q=rose&limit=5"

# Species by ID
curl https://sasyakashi.vercel.app/api/species/1
```

> 🔐 **No secrets or passwords are documented here.** Local-dev seed accounts and their credentials are defined only in `supabase/seed.sql` and must never be used against production. Passwords are reset per session during testing (see `docs/testing-guide.md`).

---

## 🧪 Testing

| Type      | Command                                              | Coverage          |
| --------- | ---------------------------------------------------- | ----------------- |
| Lint      | `npm run lint`                                       | TypeScript / Expo |
| Typecheck | `npx tsc --noEmit`                                   | TypeScript strict |
| Frontend  | `npx jest`                                           | 44 tests          |
| Backend   | `cd api && pytest`                                   | 91 tests          |
| E2E       | `npx playwright test e2e/api-tests/ --reporter=list` | 21 tests          |

Replayable end-to-end device testing (History/Save, auth, admin, release-build sanity) lives in **[`docs/testing-guide.md`](docs/testing-guide.md)**.

---

## 🛠️ Local Development

**Prerequisites:** Node.js 20+, Python 3.12+, Vercel CLI.

```bash
# 1. Clone & install
git clone https://github.com/luckyhegde6/gardenify.git
cd gardenify
npm install

# 2. Configure environment
cp .env.example .env
# → fill Supabase URL + anon key + PlantNet API key

# 3. Backend (separate terminal)
pip install -r api/requirements.txt
vercel dev                 # http://127.0.0.1:8000

# 4. Mobile
npx expo start             # press 'a' for Android
```

### Dev commands

| Command                                         | Description           |
| ----------------------------------------------- | --------------------- |
| `npx expo start`                                | Start Expo dev server |
| `npm run lint`                                  | Lint (Expo)           |
| `npx tsc --noEmit`                              | Typecheck             |
| `cd api && pytest`                              | Backend tests         |
| `npx eas build -p android --profile production` | Build release APK     |

---

## 📁 Project Structure

```
src/                    # Expo app (TypeScript)
  app/                  # expo-router file-based routes
    (auth)/             # login, register
    (tabs)/             # Scan, Favorites, History, Profile
    identification/     # result detail screens
  components/           # reusable UI
  hooks/                # auth, camera, identification, theme, notifications
  lib/                  # supabase, api-client, types, cache
  constants/            # theme, fonts, spacing

api/                    # Python backend (FastAPI)
  main.py               # Vercel entrypoint
  routes/               # health, identify, species, history, admin
  services/             # PlantNet, plant care, OpenCV, perceptual hashing, Supabase
  models/               # Pydantic schemas
  data/importers/       # GBIF + seed importers (writes to Supabase)
  tests/                # backend tests

supabase/
  migrations/           # SQL migrations (001–009)
  seed.sql              # local-dev seed (never run on prod)

docs/                   # guides (testing, security, supabase, vercel)
.agents/                # agent/automation guidelines
```

---

## 🎉 Releases

### Latest APK

Download the latest APK from [GitHub Releases](https://github.com/luckyhegde6/gardenify/releases) — no Play Store required.

```bash
npx eas build -p android --profile production
```

### Release flow

1. Merge feature PR into `main` (squash merge)
2. **CI** runs → lint + typecheck + Python tests
3. **Vercel** auto-deploys backend when `api/` changes
4. Tag a release → **GitHub Release** is created automatically
5. Attach the **EAS-built APK** from GitHub Releases

### Distribution

- **No Play Store** — direct APK install only (enable "Install from unknown sources")
- **OTA updates** — preview channel on `feat/*`/`bugfix/*` pushes
- **Build logs** — [expo.dev](https://expo.dev/accounts/luckyhegdeddev/projects/gardenify/builds)

### Release build env

Required vars for production APKs — set via [EAS Secrets](https://docs.expo.dev/build-reference/variables/) (never commit secrets):

| Variable                        | Purpose              |
| ------------------------------- | -------------------- |
| `EXPO_PUBLIC_API_URL`           | Backend URL          |
| `EXPO_PUBLIC_SUPABASE_URL`      | Supabase project URL |
| `EXPO_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key    |

---

## 📚 Documentation

- [Architecture](.agents/architecture.md)
- [Security Harness](.agents/security-harness.md)
- [Security Architecture](docs/security-architecture.md)
- [Testing Guide](docs/testing-guide.md)
- [Supabase Integration](docs/supabase-integration.md)
- [Vercel Deployment](docs/vercel-deployment.md)

## 🤝 Contributing

PR-only workflow. Commit on a branch (`feat/*`, `bugfix/*`, `chore/*`, `docs/*`) and open a PR against `main`. Direct commits/pushes to `main` are blocked by gated by repo hooks.

## License

MIT
