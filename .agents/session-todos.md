# Session Todos

> Maintained during a session. Completed sessions are archived to `.agents/sessions/YYYY-MM-DD-<commit-hash>.md` and removed from this file.
> Rules:
>
> 1. Keep this file short — only the current session's todos.
> 2. Before a commit: mark done/cancelled, carry forward unfulfilled ones as new todos.
> 3. If an unfulfilled todo is a confirmed bug, log it in `BUGS.md`.
> 4. Never delete history — archive it to `.agents/sessions/` (date + commit hash in the filename) for future reference.

## Current Session (2026-08-06) — Auth Guard Release + Doc Restructure

- [x] Fix auth navigation (root guard in `_layout.tsx`) — sign-out → Login; login → Home in-app
- [x] Single version source (`app_version = "1.1.0"`; Profile footer from `app.json`)
- [x] Verify on emulator (build `e4cd16d5`): logout, login transition, session persistence, footer v1.1.0
- [x] PR #36 created + merged; CI green on main
- [x] Re-cut `v1.1.0` tag → release.yml running (EAS APK build `2d8eeb92` in progress)
- [x] Archive past sessions → `.agents/sessions/YYYY-MM-DD-<hash>.md`
- [x] Split LESSONS.md + MEMORY.md into category files
- [x] Update doc references (AGENTS.md, pre-commit-workflow, documentation-standards, primer)
- [ ] After release.yml finishes: verify GitHub Release has APK + `/api/health` reports 1.1.0
- [ ] Commit doc restructure (PR)

## Carried Forward

- [ ] Supabase: allowlist redirect `gardenify://reset-password` (config, not code)
- [ ] Seed prod `image_hashes` (apply migration 008 + run hash seed, ~20-30 min)
- [ ] Recheck PlantNet 404/401 identify failure
- [ ] Fix Supabase prod auth config (Site URL / redirects → prod app, not localhost)
- [ ] Expand hash index to remaining ~8K species
- [ ] Push notifications (Phase 3)
