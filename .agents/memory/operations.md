# Memory — Auth, Security & Release Operations

## Auth Security

- Login is backend-mediated (`/api/auth/login`) with 3-failure lockout (15 min); forgot-password is one-shot per email until completed
- Admin can force-reset to default (`GARDENIFY_DEFAULT_PASSWORD`, default 12345678) via admin screen/API
- Recovery deep link must be allowlisted in Supabase: `gardenify://reset-password`
- Supabase prod: project `amyriuhwqyalodsfkwzf`; Auth users appear in `auth.users` (Auth Admin API), but `public.users` may return `[]` — suspected missing `handle_new_user` trigger in prod

## Release v1.1.0 (2026-08-06, in progress)

- App + API at 1.1.0; PR #36 (`fix/auth-navigation-and-version`) **merged** (commit `97554e2`)
- Tag `v1.1.0` moved to HEAD `97554e2`; `release.yml` run `31041652851` triggered; EAS build `2d8eeb92-4052-4dfd-950e-90e7955ec0dd` (in progress — EAS builder queue; previous run took ~1h13m)
- Flow: Build APK (EAS) → download artifact → upload asset → Create Release → Deploy Backend (Vercel)
- Old `v1.1.0` tag pointed at `fb2a5fc` (stale) → release deleted + re-cut
- CodeQL `Analyze` job failure on PR #36 was GitHub infra (model `claude-opus-4.6` unsupported) — unrelated to release build, not fixable in-repo

## Release Verification Checklist

- [ ] `/api/health` + `/api/debug` report `app_version: 1.1.0`
- [ ] GitHub Release `v1.1.0` has new APK asset (not the stale one)
- [ ] Emulator: install APK → login → identify flow works against prod
- [ ] Physical device spot-check
