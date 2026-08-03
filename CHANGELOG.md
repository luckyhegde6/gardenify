# Changelog

All notable changes to Gardenify are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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
