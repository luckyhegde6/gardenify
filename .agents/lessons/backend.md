# Lessons — Backend (FastAPI, PlantNet, Image Processing, Serverless)

## 2026-08-02: Vercel Serverless Filesystem Is Read-Only (Only /tmp Writable)

**Context:** Production `/api/identify` returned HTTP 500. Traceback showed `ImageProcessor()` → `_ensure_upload_dir()` → `mkdir` at `/var/task/api/data/uploads/<upload_id>` failing with `OSError: [Errno 30] Read-only file system`.

**Issue:** Vercel serverless functions run from a read-only `/var/task`. Any write outside `/tmp` crashes at runtime — even a directory `mkdir`. The upload dir was hardcoded to `api/data/uploads`, which works locally but is read-only in production.

**Fix:**

1. Resolve the upload dir at import time: probe the default dir with a write test; on `OSError`, fall back to `<tempdir>/gardenify-uploads` (Vercel maps `/tmp`).
2. Make disk writes best-effort: wrap storage file writes in `try/except OSError`; on failure return `storage: {}` while still returning the in-memory `compressed_data` (the PlantNet pipeline only needs in-memory bytes).
3. Import `UPLOAD_DIR` from `image_processor` in `history.py` rather than re-deriving the path (single source of truth).

**Pattern:** On serverless platforms, never assume a project-relative path is writable. Resolve writable storage at startup with a fallback to `tempfile.gettempdir()`, and treat secondary disk writes (metadata/storage) as non-fatal so the primary in-memory path always succeeds.

## 2026-07-30: PlantNet API v2 Rejects `lang` Parameter

**Context:** Debugging "no match found" for rose image — PlantNet returned 400 with `{"message":"\"lang\" is not allowed"}`.

**Issue:** The `lang=en` parameter was included in the multipart form data sent to PlantNet, but the v2 API does NOT accept it. The old httpx-based code handled it silently — `raw` was set but had no results.

**Fix:** Remove the `lang` parameter entirely from multipart body and curl command.

**Key insight:** API docs mention `lang` for v1 endpoints but v2 endpoints reject it outright. Always test with `curl -v` to see the exact request/response when debugging API client issues.

## 2026-08-03: OpenCV Image-Validation Best Practices (Blur + Green Dominance)

**Lessons applied to `image_processor.py`'s plant-likeness gate:**

1. **Always GaussianBlur before Canny** — Canny edge detection is extremely noise-sensitive; a `3x3` GaussianBlur first stabilizes edge output, so `content_score` reflects real structure, not sensor noise.
2. **Blur/quality is a variance-of-Laplacian, not an edge count** — a flat uniform image has no global content but also shouldn't be rejected as "edgy"; compute `cv2.Laplacian(gray).var()`, classify `sharpness < BLUR_THRESHOLD (100.0)` as blurry (PyImageSearch default). Edge count alone conflates "low detail" with "out of focus".
3. **Plant-likeness = green-pixel ratio in HSV** — threshold HSV green (`cv2.inRange` H≈30-90) and compute `green ratio = green_pixels / total`.
4. **Surface the metrics in the schema** — added `sharpness`, `is_blurry`, `green_ratio` to `OpenCVResult` and returned them in `/api/identify`.
5. **`is_plant_like` = `content_score > 0.01 OR green_ratio > 0.3`** — structured image OR strongly-green image passes; both must be low to call it "not a plant".

**Verified live:** flat-green JPEG → `sharpness:0, is_blurry:true, green_ratio:1.0`; structured green → `sharpness:370, is_blurry:false`.

## 2026-07-29: Pydantic + `.env.local` Extra Fields Crash

1. **Extra fields not permitted** — `.env.local` has vars not defined in `Settings` model. Pydantic v2 `BaseSettings` rejects extra env vars by default. Fixed with `model_config["extra"] = "ignore"`.
2. **Field name mismatch** — env var is `SUPABASE_SERVICE_ROLE_KEY`, field was named `supabase_service_key`. Pydantic canonicalizes field names to uppercase. Renamed field to match.

**Pattern:** When adding a `.env` file to Pydantic's `env_file`, check all fields match their env var names (case-insensitive) and add `extra="ignore"` if the file has vars beyond the model. Pydantic reads `os.environ` first, then `.env` files.

## 2026-07-29: Admin Route Must Use Settings, Not os.environ

**Issue:** `_get_service_client()` used `os.environ.get()` which doesn't get values from Pydantic's `.env` file loading. Pydantic reads env files into its `Settings` object but doesn't write to `os.environ`.

**Fix:** Use `settings.supabase_url` / `settings.supabase_service_role_key` (from `api.config`).

**Pattern:** Never use `os.environ.get()` in route code — always use `settings.xxx` from the Pydantic config.

## 2026-07-31: `load_dotenv()` Required for Pydantic `.env` Compatibility

**Issue:** `supabase_species.py` uses `os.environ.get("SUPABASE_URL")` but values are only loaded via Pydantic `Settings` from `.env.local`. Pydantic does NOT write to `os.environ`.

**Fix:** Call `load_dotenv()` in `api/main.py` before anything else reads env vars.

**Pattern:** Any code using `os.environ.get()` instead of Pydantic `settings.xxx` needs `load_dotenv()` at startup.

## 2026-07-29: WebP Images Not Accepted + Unhandled ValueError

**Issue:** `ALLOWED_TYPES` only included `image/jpeg`, `image/png`, `image/jpg` — WebP returned 500 because `validate_image()` raised `ValueError` that wasn't caught.

**Fix:**

1. Added `"image/webp"` to `ALLOWED_TYPES`.
2. Wrapped `validate_image()` in try/except `ValueError` → `HTTPException(400)`.

**Also:** When sending `.webp` via curl, must specify content type: `-F "images=@file.webp;type=image/webp"`.

## 2026-07-29: Pillow 12 `getdata()` Deprecated — Use `get_flattened_data()`

**Issue:** `img.getdata()` deprecated in Pillow 12, removed in Pillow 14 (2027-10-15).

**Fix:** `list(img.get_flattened_data())` replaces `list(img.getdata())`.

## 2026-07-29: Suppress PIL Debug Log Noise

**Issue:** Backend logs flooded with `DEBUG PIL.TiffImagePlugin` messages when processing JPEG images.

**Fix:**

```python
logging.getLogger("PIL.TiffImagePlugin").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
```

## 2026-07-29: Starlette Middleware `response.headers.pop("server")` Causes 500

**Issue:** Mutating response headers in middleware after they've been sent raises `RuntimeError: Headers already sent`.

**Fix:** Don't pop headers in middleware. Use uvicorn's `--no-server-header` flag:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --no-server-header
```

## 2026-08-01: `uuid-ossp` Extension Required for `uuid_generate_v4()`

**Issue:** Migration failed with `function uuid_generate_v4() does not exist` — the `uuid-ossp` extension wasn't enabled on production.

**Fix:** `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";` before migrations that use it.

**Note:** Local `supabase start` includes this extension by default, but production doesn't.

## 2026-07-31: GBIF Batch Upsert — 100 Rows Per Batch Optimal

**Pattern:** For large Supabase data imports: batch upsert in chunks of 100 rows with `ignore_duplicates=True` for idempotency, log progress every N batches, delete import scripts after use.

## 2026-07-28: Missing Modules Cause Chain Import Failures

**Issue:** `main.py` imports `identify_router` which imports services that don't exist yet. Import failure cascaded: main.py → identify.py → cache.py (not found). All tests failed because they import `app` from `main.py`.

**Fix:** Use `try/except ImportError` for optional route imports. Only include routers when their dependencies exist.

## Using Python Reserved Word as Directory Name

**Context:** Created `api/data/import/` directory for import scripts. `from api.data.import.seed_species import seed_database` → `SyntaxError: invalid syntax`.

**Fix:** Rename `api/data/import/` → `api/data/importers/`; update all references.

**Pattern:** Never name directories or files with Python reserved words (`import`, `class`, `def`, `return`, `from`, `as`, etc.).

## Perceptual Hash Algorithms Need Structured Images

**Context:** Testing dHash and pHash with uniform-color images.

**Issue:** Uniform images (all black/white) produce identical dHash (`0000000000000000`); pHash on synthetic images has high Hamming distance even for similar images.

**Fix:** Use gradient/checkerboard images for hash testing; test hash consistency (same image = same hash) rather than distance; use structurally similar images for distance tests.

**Pattern:** Perceptual hashes work on spatial structure, not color. Test with images that have gradients, edges, and patterns.

## supabase-py Auth Flow Lessons (2026-08-04)

- `supabase-py` (2.31) exposes server-side password flows: `auth.reset_password_for_email(email, {redirect_to})`, `auth.verify_otp({type: recovery, email, token})`, and `auth.admin.update_user_by_id(id, {password})`. Client-side recovery-link handling on Expo uses the app scheme (`gardenify://reset-password`) with PKCE code param.
- When routing app login through a backend that returns Supabase tokens, call `supabase.auth.setSession({access_token, refresh_token})` to restore the session.
- In-memory rate-limiter on serverless is per-instance/approximate; a 3-strike lockout must not prune a mid-burst entry (prune only idle or expired-lock entries).
