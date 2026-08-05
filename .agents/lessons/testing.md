# Lessons — Testing (Jest, Playwright, Pytest)

## 2026-07-28: Jest 29 Bundled with jest-expo@55

**Issue:** Installing `jest@30` with `jest-expo@55` causes incompatibility — `jest-expo` expects Jest 29 internals.

**Fix:** Let `jest-expo@55` install its own Jest 29 dependency. Don't install Jest separately. Uninstall `jest@30` if present.

## 2026-07-28: @testing-library/react-native v12 vs v14

**Issue:** v14 requires `@testing-library/react-test-renderer` which adds a `react-test-renderer` peer dep not present in Expo; `container` property renamed to `UNSAFE_root`.

**Fix:** Install `@testing-library/react-native@12` (compatible with Expo SDK 55). Use `root` instead of `container` for element access.

## 2026-07-28: Manual AsyncStorage Mock Needed

**Issue:** AsyncStorage uses native modules that don't work in the Jest test environment.

**Fix:** Create `__mocks__/async-storage.js` with a manual mock of all AsyncStorage methods. Use `moduleNameMapper` in `jest.config.js` to redirect `@react-native-async-storage/async-storage` to the mock file.

## 2026-07-28: Mock Files Should Be .js Not .ts

**Issue:** `.ts` mock files get picked up by TypeScript and fail on the `jest` global (not declared in types).

**Fix:** Use `.js` extension for mock files — they don't need TypeScript compilation and won't be picked up by `tsc`.

## 2026-07-29: Playwright Multipart API Doesn't Support Arrays of FilePayload

**Issue:** Playwright's `multipart` form data with array values throws `stream4.on is not a function`.

**Fix:** Use individual numbered field names instead of array syntax:

```typescript
// WRONG — internal crash
await request.post("/api/identify", {
  multipart: { images: [f1, f2, f3, f4, f5, f6] },
});

// RIGHT — individual fields
await request.post("/api/identify", {
  multipart: {
    images0: f1,
    images1: f2,
    images2: f3,
    images3: f4,
    images4: f5,
    images5: f6,
  },
});
```

## No Testing Framework (anti-pattern)

**Issue:** Tests only covered happy path; no mocking of PlantNet, no integration tests with Supabase, no fixtures.

**Fix:**

1. Create `api/tests/conftest.py` with shared fixtures + `api/tests/fixtures/` with test images and API responses.
2. Use `pytest-httpx` to mock PlantNet API calls.
3. Add integration tests with Supabase (test database) + e2e tests for the full flow.
4. Use an in-memory `FakeSupabaseClient` + `patched_supabase` fixture so backend tests need no live Supabase.

**Pattern:** TDD: write test first, then code. Tests are documentation, not afterthought.

## Not Running Type Checks on All Code

**Issue:** `tsconfig.json` checked all `**/*.ts` including `example/` → TS errors in CI.

**Fix:** Add `exclude: ["example/**", "node_modules/**"]` or remove irrelevant dirs; run `npx tsc --noEmit` in CI.

## Not Running Ruff Locally Before Push

**Fix:** Run `ruff check api/` before every push; run `ruff format api/`; add to pre-commit hook. Use `ruff check api/ --fix` for import sorting.

**Pattern:** "If it's not in CI, it's not tested. If it's not in pre-commit, it's not caught."
