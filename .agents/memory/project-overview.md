# Memory — Project Overview

**Gardenify** — Plant identification mobile app. Photo → species + disease + care instructions.

## Key Facts

| Key              | Value                                                                                       |
| ---------------- | ------------------------------------------------------------------------------------------- |
| Repo             | `https://github.com/luckyhegde6/gardenify`                                                  |
| EAS Project ID   | `b17c6958-f3e7-4ec1-afcf-3b241fcbcda0`                                                      |
| Platform         | Android-first, iOS later                                                                    |
| Backend          | Python FastAPI on Vercel                                                                    |
| Database         | Supabase (PostgreSQL + Auth + Storage)                                                      |
| Plant AI         | PlantNet API v2 (free 500/day)                                                              |
| Backend (prod)   | `https://sasyakashi.vercel.app`                                                             |
| Vercel env       | `USE_REMOTE=true`, PlantNet API key, Supabase URL/anon key                                  |
| Vercel bundle    | 268MB (fixed from 611MB — 412MB GBIF zip + dev data excluded via `.vercelignore`)           |
| EAS Builds       | https://expo.dev/accounts/luckyhegdedev/projects/gardenify/builds                           |
| Local DB size    | 10,008 species, 1,960 with perceptual hashes (19.6%)                                        |
| Backend Pipeline | OpenCV gate → local DB pHash → PlantNet (quota saver)                                       |
| Tests            | 86 Python + 21 Playwright + 41 Jest = 148 total                                             |
| PlantNet status  | Fixed: no `lang` param, urllib-based, verified working                                      |
| Server restart   | Use `Popen(CREATE_NEW_CONSOLE=0x00000010)` on Windows                                       |
| Supabase prod    | Project `amyriuhwqyalodsfkwzf` linked, 6 migrations applied (006 thumbnail live)            |
| Prod species     | 10,008 GBIF species, jsonb common_names/native_regions; seed is idempotent + merge-preserve |
| History images   | Persisted as base64 thumbnails in `identifications.image_thumbnails` (migration 006)        |
| Vercel FS        | `/var/task` read-only; only `/tmp` writable — upload dir falls back to temp                 |

## Architecture (10 seconds)

```
Expo App → FastAPI Backend → PlantNet API
    ↓              ↓
 Supabase      Supabase
(auth/db)     (storage)
```

## Key Decisions

- **PlantNet** over Google Vision: free 500/day, plant-specialized
- **FastAPI** over Express: Python ecosystem, async, type safety
- **Supabase** over Firebase: RLS, PostgreSQL, open source
- **4-tab navigation**: Scan → Saved → History → Profile
- **expo-secure-store** for tokens, AsyncStorage for cache
- **Server-side API key**: never expose PlantNet key to client
