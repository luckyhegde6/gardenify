# Lessons — CI/CD, Dependencies, EAS Build, Vercel Deploy

## 2026-08-05: Global `brace-expansion` Override Broke EAS Fingerprint — Use Scoped Overrides

**Context:** After pinning `"brace-expansion": "2.1.4"` globally, the re-cut release failed in 5 seconds at EAS Build's "compute project fingerprint" step: `Failed to compute project fingerprint: (0, brace_expansion_1.expand) is not a function`.

**Root cause:** A **global** override forces one brace-expansion version on the entire tree, but two consumers need incompatible entry points:

| Consumer           | Used by                 | Import style                               | Needs      |
| ------------------ | ----------------------- | ------------------------------------------ | ---------- |
| `minimatch@3.1.5`  | `@react-native/codegen` | `require('brace-expansion')()` callable    | CJS v2.1.4 |
| `minimatch@10.2.5` | `@expo/fingerprint`     | `(0, brace_expansion.expand)` named export | v5.x       |

`brace-expansion` v2 exports a callable but **no named `.expand`**; v5 has named `expand` but is ESM-only. No single version satisfies both.

**Fix:** scope the override to the CJS consumer:

```json
"overrides": {
  "minimatch@3.1.5": { "brace-expansion": "2.1.4" },
  "js-yaml": "5.2.3",
  "uuid": "14.0.1"
}
```

**Verification (before wasting a cloud build):**

```bash
node -e "require('@expo/fingerprint').createFingerprintAsync(process.cwd()).then(function(f){console.log('OK',f.hash)}).catch(function(e){console.error('FAIL',e.message);process.exit(1)})"
node -e "var be=require('node_modules/minimatch/node_modules/brace-expansion'); console.log(typeof be.expand)"  # function
```

**Rules going forward:**

- **Overrides are global — scope them by parent package when dependents disagree.** `"pkg@version": { "dep": "x" }`.
- **A fix that resolves one consumer can break a sibling.** After any override change, grep which versions exist in the tree and check each consumer's import style.
- **`release.yml` swallowing `set -e` output hides every class of EAS failure** — patched the job to `set +e` capture + echo before exit so a red run always prints the real error.

## 2026-08-04: ESM-only `brace-expansion` Override Broke the RN Codegen Gradle Build

**Context:** Cut release v1.1.0. `release.yml` Build APK (EAS) job failed at `gradle assembleRelease` → `generate-codegen-schema.js` → `expand is not a function`. Every gradle `generateCodegenSchemaFromJavaScript` task failed; no APK or GitHub Release.

**Root cause:** `package.json` had a security override `"brace-expansion": "5.0.9"` (to silence CVE-2024-4068). But v5 is **ESM-only** and exports no CommonJS `module.exports = expand`, while `@react-native/codegen` → `minimatch@3.1.5` requires `brace-expansion@^1.1.7` and calls `braceExpand()`.

**Why local checks missed it:** `npx tsc --noEmit`, `npm run lint`, `npm test` all passed — none execute the RN codegen gradle tasks.

**Fix:**

1. Override → `"brace-expansion": "2.1.4"` (last CommonJS release AND ReDoS fix in `> 2.1.3`, so 0 vulnerabilities).
2. Verify before tagging a release: `node -e "const mm=require('minimatch'); console.log(typeof mm.Minimatch.prototype.braceExpand, new mm.Minimatch('foo{a,b}*/bar*.js').makeRe() instanceof RegExp)"` or `npx expo run:android --variant release`.
3. `npx expo run:android --variant release` builds the full native project and exercises every codegen task — the faithful way to catch a "passes tsc but fails gradle" issue.

**Rules going forward:**

- **Pinning an override from a library must not switch module systems it is consumed under.** Prefer a version whose entry point (CJS vs ESM) matches the dependents.
- **A release tag is the last gate, not a checkpoint.** Verify a real native build locally _before_ pushing the `v*` tag.
- **`release.yml` swallows the error message** — run the EAS build job with `set +e` and capture `$BUILD_OUTPUT`.

## 2026-08-01: Vercel Deploy `lstat ENOENT` — Never Exclude Git-Tracked Files via `.vercelignore`

**Context:** Backend production deploy failed repeatedly with `Error: ENOENT: no such file or directory, lstat '/vercel/path0/...'`.

**Issue:** For a GitHub-linked Vercel project, the deployment manifest is derived from the **git tree**, and Vercel's build server syncs every tracked file. Any git-tracked file excluded from the upload (via `.vercelignore`) breaks that sync with `lstat ENOENT`.

**Fix:** `.vercelignore` must exclude ONLY untracked/generated files (`node_modules`, `.git`, `.expo`, `.vercel`, `api/data` artifacts). Both a deny-list that excluded tracked files AND a `/*` allowlist caused ENOENT — the manifest references ALL tracked files regardless.

**Bonus:** `vercel build` + `vercel deploy --prebuilt` is the wrong pattern — local `vercel build` creates `.vercel/python/.venv`, which the manifest references but `.vercelignore` excludes → more ENOENT. Use direct `vercel deploy --prod` and let Vercel build server-side.

**Pattern:** To check a `.vercelignore` rule is safe: `git ls-files --error-unmatch <pattern>` — any match means a tracked file, which must NOT be ignored.

## 2026-08-01: Deploy Backend as Part of the Release Flow, Not on Every Push

**Issue:** Backend auto-deployed on every `api/**` change to `main` via `deploy-backend.yml`, double-deploying with Vercel's GitHub integration and shipping API changes before the app that uses them.

**Fix:** Remove the push-triggered deploy workflow. Add a `deploy-backend` job to `release.yml` with `needs: create-release`, so the order is: tests/checks → cut tag → release APK → deploy backend. Restore Vercel's `commandForIgnoringBuildStep` to skip production on git pushes.

## 2026-08-04: Vercel Auto-Deploy Does Not Reliably Fire on GitHub Merges (release 1.1.0)

**Lesson:** Auth endpoints were absent on prod until a manual `vercel --prod` from main. When a release changes the backend, deploy the backend manually BEFORE tagging so the new APK never points at a stale API. Full release is automated by `.github/workflows/release.yml` on a `v*` tag push (EAS production build → GitHub Release with APK → Vercel deploy). The git pre-push hook only blocks main/master branches, so tag pushes are allowed.

## 2026-07-31: `package-lock.json` Must Be Committed for `npm ci` to Work

**Issue:** After a merge, `package-lock.json` was out of sync with `package.json`; CI failed with "Missing: eslint@9.39.5 from lock file" and 200+ more.

**Fix:** Run `npm install` to regenerate `package-lock.json` and commit it.

**Pattern:** After any merge/rebase that changes `package.json`, run `npm install` to sync the lock file. Never edit `package-lock.json` manually.

## 2026-07-31: `requirements.txt` Must Exist for Python CI

**Issue:** CI ran `pip install -r requirements.txt` but no `requirements.txt` existed.

**Fix:** Create `api/requirements.txt` with all Python dependencies (runtime + dev: fastapi, uvicorn, pydantic, supabase, pillow, pytest, ruff).

## 2026-07-28: Stale Template Files Breaking CI

**Issue:** Expo template's `example/` directory (1172 lines) was left in repo. It imported `@/components/*` etc., `tsconfig.json` mapped `@/*` → `./src/*` and `include: ["**/*.ts","**/*.tsx"]` picked it up → `Cannot find module '@/components/animated-icon'`. CI failed on every push.

**Fix:** Run `npx tsc --noEmit` after project creation; remove `example/` (or add `exclude: ["example/**"]`); add a pre-commit hook running `tsc --noEmit`.

**Pattern:** Always verify CI passes after initial setup. Don't assume template code is compatible with your customizations.

## 2026-07-28: Python Linter Errors (ruff B008 + BLE001)

**Issue:** `File(...) = File(...)` and `Form(default=["auto"])` → ruff B008; `except Exception` → BLE001.

**Fix:** Create `api/ruff.toml` with project-specific ignores (`B008`, `BLE001`), `known-first-party = ["api"]`, and per-file ignores for tests (`S101`).

**Pattern:** Linter rules are guidelines, not absolute. Document why you ignore specific rules.

## 2026-07-28: Not Running CI Locally Before Push

**Pattern:** "If it's not in CI, it's not tested. If it's not in pre-commit, it's not caught." Run `npx tsc --noEmit` and `ruff check .` before pushing; add pre-commit hooks.

## 2026-08-01: Release Flow Verification (v0.1.5)

Cut v0.1.5 tag → release flow ran end-to-end: APK → GitHub Release → `deploy-backend` to prod. Verified `https://sasyakashi.vercel.app/api/health` returns ok after first release; species detail endpoint returns `images` key live on prod.
