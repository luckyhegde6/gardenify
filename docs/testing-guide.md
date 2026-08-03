# Gardenify Testing Guide

Operational playbook for testing the shipped app (APK + backend + auth) on an
Android emulator against **prod**. Read before any testing session.

**Security note:** this file intentionally contains **no passwords or tokens**.
Credentials are (re)generated/reset per session and kept only in gitignored
files (`creds.json`, `.env.local`). Any account listed below must have its
password reset at the start of the session that uses it (see
[Making accounts usable](#making-accounts-usable)).

---

## 1. Golden rule: prod vs local

- The **release APK** (EAS `build:release`/`production`) connects to **prod
  Supabase** (`EXPO_PUBLIC_SUPABASE_URL = https://amyriuhwqyalodsfkwzf.supabase.co`)
  and **prod backend** (`https://sasyakashi.vercel.app`).
- The **dev build** (`npx expo start` / Expo Go) reads `.env.local`, which has a
  **local** Supabase block **and** a **prod/remote** block. The **last** key wins.
  `.env.local` contains **both** `SUPABASE_URL`, `SUPABASE_ANON_KEY` /
  `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`.
- Symptom "can't log in" is often a **build/environment mismatch**: a user that
  exists on prod does not exist on a local Supabase (and vice-versa). Always
  confirm **which Supabase the running app points to** before diagnosing auth.

## 2. Confirming which project the APK talks to

Deterministic check on prod:

```js
// Node (reads .env.local, uses LAST block = prod)
const url = kv["SUPABASE_URL"]; // prod, quoted in env
const anon = kv["SUPABASE_PUBLISHABLE_KEY"]; // prod anon key
const skey = kv["SUPABASE_SERVICE_ROLE_KEY"]; // prod service role (never ship to client)
```

Strip surrounding `"` from `.env.local` values before use. Endpoint smoke:

```bash
curl https://sasyakashi.vercel.app/api/health
```

## 3. Release build (EAS) testing

- The **signed release APK** is built via `eas build --profile production`.
- **Only download the artifact whose `gitCommitHash` matches the current
  `main`/tag.** Old builds linger in `eas build:list` and **predate bug fixes**.
  Confirm: `get hash === main HEAD` before installing.
- Builds sit **IN_QUEUE for a long time on EAS's free tier**; do not assume a
  stall = error. Poll with `eas build:view <id>`; watch `updatedAt` advancing.
  `status.expo.dev` shows service-wide incidents (rarely the cause).
- Install/repair history-safe flows:
  - Reset sample data, create a deterministic **admin account with a known role**
    (see Admin section) so panel tests are repeatable.

## 4. Mobile flows to test on every release build

### History tab

- **Regressed (v1.0.0):** the tab never fetched on mount (`useFocusEffect` was
  missing — only pull-to-refresh loaded). Symptom: stuck on "Loading history…".
- Test: open **History** → must render list immediately with past
  identifications; pull-to-refresh still works.

### Save / Favorites

- **Regressed (v1.0.0):** the `favorites` schema was `identification_id`-based,
  but the app saves **species**-based → migration `009_favorites_species.sql`
  (dropped `identification_id`, added species columns + unique
  `(user_id, species_scientific_name)`).
- Test: open an identification result → tap **Save** → label flips to "Saved";
  open **Saved** tab → count increments; no crash on empty state.

### Driving the UI without visual

If the model can't read screenshots, use the accessibility tree:

```bash
adb shell uiautomator dump /sdcard/ui.xml && adb shell cat /sdcard/ui.xml
```

Then tap tab centers (bottom tab bar) via `adb shell input tap <x> <y>`.

## 6. Auth / login on prod

- Seed accounts are **not** present on prod by default — prod accounts were
  created via the admin API, so **passwords differ from `supabase/seed.sql`**.
  A "confirmed + not banned" user that still fails login = **wrong/unknown
  password**, not an account problem.
- A missing `public.users` row causes profile/RLS failures but **not** a hard
  login failure (auth is in `auth.users`).

## 7. Admin functionality (the biggest gotcha)

- The admin gate is the **`is_admin` column on `public.users`**, checked in two
  places:
  - backend: `api/routes/admin.py` `_require_admin` → service-role read of
    `users.is_admin` (bypasses RLS).
  - mobile: `src/hooks/use-auth.tsx` reads `users.is_admin` via the anon client
    (RLS policy "Admins can view all profiles" uses `public.is_admin(auth.uid())
OR auth.uid() = id` — own-row select passes).
- **Observed bug:** the intended admin (`admin@gardenify.app`) had
  `is_admin = false` on prod (seed `update ... set is_admin=true` was **never
  run**). Result: both gates blocked ALL admin actions. Fix was a row-level
  `UPDATE` via service role.
- **Test matrix to re-run after promotion** (each endpoint should be 2xx with
  the admin token, **403 with a non-admin token**):
  1. `GET  /api/admin/users` — list all
  2. `GET  /api/admin/users/{id}` — detail
  3. `PATCH /api/admin/users/{id}` — change tier + toggle `is_admin`
  4. `DELETE /api/admin/users/{id}` — soft-delete/ban (destructive — use a
     throwaway account)
- Backend schema treats `subscription_tier` as a free string (no enum), so the
  mobile tier cycle free→pro→premium→free is accepted. RLS must stay enabled on
  `public.users`; only the service role and the owning user may read/write rows.

## 8. Security best practices (non-negotiable)

- **No secrets in this doc or any tracked file.** Passwords, `sbp_…`,
  `SUPABASE_SERVICE_ROLE_KEY`, `sk-…` must live only in gitignored
  `creds.json` / `.env.local`. Scan before every push:
  `git grep -nE 'sbp_[a-f0-9]{20,}'`.
- **Service-role key is server-only.** It is safe to use from a one-off Node
  bootstrap script that reads `.env.local`, but never from the mobile client.
- **Reset test passwords each session** and rotate if they ever reach a file
  that could be pushed. Do not document the values.
- Frontend decides "is admin" via RLS-gated own-row read; backend re-validates
  via service role. Keep **both** (defense in depth).
- Push protection + `.githooks` block direct `main` Pushes; do not bypass with
  `--no-verify`/`-f` unless intentionally overriding.
- Destructive admin actions (DELETE/ban) must be tested on a **throwaway**
  account, never the real admin.

## 9. Emulator environment

```bash
adb devices                # expect emulator-5554
adb -s emulator-5554 install -r <apk>      # -r = replace, keeps data
adb -s emulator-5554 shell monkey -p com.gardenify.app -c android.intent.category.LAUNCHER 1
adb -s emulator-5554 exec-out screencap -p > screen.png   # visual only
```

Tag `adb shell input keyevent 4` = back. Keep local Supabase availability in
mind; if local is down, point tests at prod.

## 10. Admin/seat sanity list before a release

- [ ] History tab renders without "Loading…"
- [ ] Save toggles + Saved tab updates
- [ ] admin account has `is_admin=true` (promote via service role)
- [ ] admin endpoints return 2xx; non-admin returns 403
- [ ] password for test/admin set (credential store) — **not** in docs
- [ ] `git grep` secret scan clean; no `console.log` in release paths
