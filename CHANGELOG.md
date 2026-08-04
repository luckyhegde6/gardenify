# Changelog

All notable changes to Gardenify are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-08-04

Password recovery and hardened login. Login now routes through the backend
(3-attempt lockout), users can request a one-shot password reset via a Supabase
recovery email, and admins can force-reset any account to the default password.

### Added

- **Forgot Password flow** — a "Forgot Password?" button on the login screen
  sends a Supabase recovery email. Each email gets **one pending reset at a
  time**; further requests are rejected (429) until the reset is completed.
  (PR #32)
- **Recovery deep link** — reset links open the app via the
  `gardenify://reset-password` scheme (PKCE code), where the user sets a new
  password. (PR #32)
- **Admin "Reset Password" button** — admins can force-reset any user's
  password to the configured default (`GARDENIFY_DEFAULT_PASSWORD`). (PR #32)
- **Backend-mediated login** — `POST /api/auth/login` returns Supabase tokens;
  the app restores its session via `supabase.auth.setSession`. Login now
  rate-limits to **3 failed attempts** before a temporary lockout (429).
  (PR #32)
- **Shared auth dependencies** — `require_user` / `require_admin` centralize
  JWT verification so privileged calls are authenticated with proper
  permissions. (PR #32)

### Security

- **Brute-force protection** on login (3-strike, 15-minute lockout).
- **No user enumeration** on password recovery — the forgot-password endpoint
  always returns the same response for known and unknown emails.
- **Password recovery uses recovery codes** verified server-side via
  `verify_otp`; the new password is set through the admin API.

### Notes

- Requires the Supabase redirect URL `gardenify://reset-password` to be
  allowlisted in the Supabase Auth dashboard for the recovery email link to
  open the app.
- Default password and lockout windows are configurable via environment
  variables (`GARDENIFY_DEFAULT_PASSWORD`, `LOGIN_MAX_ATTEMPTS`,
  `LOGIN_LOCKOUT_SECONDS`).

## [1.0.0] - 2026-08-03

First 1.0.0 release. Removes the last legacy dependency (SQLite) from the
backend, makes image quality validation explicit, and ships the branded web
pages.

### Added

- **Image decodability validation** — photos are verified decodable before
  they are sent to the identification API, with a clear
  "Image could not be decoded. Choose another photo." error instead of a
  backend failure. (PR #21)
- **Thumbnail persistence** — identification thumbnails are saved to Supabase
  and used in the History list (falls back to the original image). (PR #20)
- **Branded 404 page, favicon, and sitemap.xml** for the web/API surface.
  (PR #20)

### Changed

- **Supabase-only backend** — SQLite was removed entirely. All local
  identification and seed/import paths now read and write through Supabase,
  matching production where SQLite files could never be written. (PR #21)
- **OpenCV image validation improvements**:
  - GaussianBlur applied before Canny edge detection (more stable `content_score`).
  - Variance-of-Laplacian blur detection (`BLUR_THRESHOLD = 100.0`).
  - HSV green-pixel ratio used to determine plant-likeness.
  - Identify responses now surface `sharpness`, `is_blurry`, and `green_ratio`.
- **Image hashes in Supabase** — new `image_hashes` table + migration for
  phash-based local identification (seed/backfill pending in production).

### Fixed

- **`/api/identify` 500 on Vercel (read-only filesystem)** — root cause was
  SQLite files not shipping to Vercel and being unwritable there. Local
  identification now uses Supabase instead of a bundled database file.
  (PR #16, PR #21)
- **History tab stuck on "Loading history..."** — the history list was never
  fetched on screen focus; now fetched via `useFocusEffect`.
- **Save (favorites) failing** — the `favorites` table schema was
  identification-based (`identification_id` NOT NULL) but the app saves
  species-based favorites; reshaped via migration `009` so "Save" persists
  and the Saved tab lists plants. (PR #24)
