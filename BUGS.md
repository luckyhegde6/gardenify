# BUGS.md — Issue Tracker

> Log all bugs, issues, and observations. Track resolution.

## Format

```markdown
### BUG-001: Title
- **Status**: Open | In Progress | Fixed | Won't Fix
- **Severity**: Critical | High | Medium | Low
- **Component**: Backend | Mobile | Database | CI/CD
- **Reported**: YYYY-MM-DD
- **Description**: What happened
- **Steps to reproduce**: How to trigger
- **Expected**: What should happen
- **Actual**: What actually happened
- **Fix**: How it was fixed (if applicable)
- **Root cause**: Why it happened (if known)
```

---

## Open Issues

### BUG-001: TypeScript CI failing on example/ imports
- **Status**: Fixed
- **Severity**: High
- **Component**: CI/CD
- **Reported**: 2026-07-27
- **Description**: `npx tsc --noEmit` fails because `example/` directory has old template files importing `@/components/*` that don't exist in `src/`.
- **Steps to reproduce**: Run `npx tsc --noEmit`
- **Expected**: Type check passes
- **Actual**: TypeScript errors in `example/src/` files
- **Fix**: Removed `example/` directory entirely
- **Root cause**: Expo template includes example app that wasn't cleaned up

### BUG-002: Python ruff B008 errors on FastAPI File/Form defaults
- **Status**: Fixed
- **Severity**: Medium
- **Component**: Backend
- **Reported**: 2026-07-27
- **Description**: `ruff check` flags `File(...)` and `Form(...)` in function signatures as B008 (function call in default argument).
- **Steps to reproduce**: Run `ruff check api/`
- **Expected**: No errors
- **Actual**: B008 errors on `identify.py`
- **Fix**: Added `api/ruff.toml` with `ignore = ["B008"]`
- **Root cause**: FastAPI idiomatic pattern conflicts with ruff's default rules

### BUG-003: Python ruff BLE001 errors on blind except
- **Status**: Fixed
- **Severity**: Medium
- **Component**: Backend
- **Reported**: 2026-07-27
- **Description**: `ruff check` flags `except Exception as e:` as BLE001 (blind except).
- **Steps to reproduce**: Run `ruff check api/`
- **Expected**: No errors
- **Actual**: BLE001 errors on `plantnet.py` and `cache.py`
- **Fix**: Added `api/ruff.toml` with `ignore = ["BLE001"]`
- **Root cause**: Intentional resilience pattern (catch all exceptions for API client + EXIF parser)

---

## Fixed Issues

(None yet — add fixed issues here)

---

## Won't Fix

(None yet — add won't-fix issues here with explanation)

---

## Observations

### OBS-001: PlantNet API returns 429 not 403 for quota exceeded
- **Component**: Backend
- **Date**: 2026-07-27
- **Description**: PlantNet API returns HTTP 429 (Too Many Requests) when quota is exceeded, not 403 (Forbidden) as might be expected.
- **Action**: Handle 429 specifically in `plantnet.py`

### OBS-002: EXIF extraction fails silently on some images
- **Component**: Backend
- **Date**: 2026-07-27
- **Description**: Some images (especially screenshots or edited photos) have corrupt or missing EXIF data. The code handles this gracefully with try/except.
- **Action**: None needed — degradation is by design

### OBS-003: In-memory cache is lost on serverless restart
- **Component**: Backend
- **Date**: 2026-07-27
- **Description**: Vercel serverless functions restart frequently, clearing the in-memory cache. This is expected behavior for serverless.
- **Action**: Consider Redis or Supabase caching for production

---

## Usage

### Adding a Bug
1. Copy the template above
2. Fill in all fields
3. Assign next BUG-XXX number
4. Add to "Open Issues" section

### Updating Status
- Change status to "In Progress" when starting work
- Change status to "Fixed" when resolved
- Add fix description and root cause
- Move to "Fixed Issues" section

### Closing Issues
- Move to "Fixed Issues" or "Won't Fix" section
- Add resolution notes
- Reference commit hash if applicable

---

**Last updated**: 2026-07-27
**Total open**: 0
**Total fixed**: 3
**Total observations**: 3
