# Session Todos

> Maintained throughout a session. Checked/updated before every commit.
> Rules:
>
> 1. Open a new session by copying the checklist below.
> 2. Before every commit: mark done/cancelled items, carry forward unfulfilled ones as new todos.
> 3. If an unfulfilled todo is identified as a bug, log it in BUGS.md.
> 4. Never delete history — carry items forward instead of dropping them.

## Checklist (copy at session start)

- [ ] Todos tracked in this file for the whole session
- [ ] `.agents/sessions.md` updated
- [ ] `.agents/handoff-current.md` updated
- [ ] `MEMORY.md` updated
- [ ] `LESSONS.md` updated (if new discovery)
- [ ] `BUGS.md` updated (if bug found/fixed)
- [ ] `PRD.md` updated (if feature completed)
- [ ] Unfulfilled todos carried forward to next session
- [ ] Any unfulfilled todo identified as a bug added to BUGS.md

---

## 2026-08-01 Session — Backend Deploy Fix + Release Flow

- [x] Fix expired `VERCEL_TOKEN` env secret (#10 PR)
- [x] Add `uv` install for `vercel build` (#10)
- [x] Root-cause `lstat ENOENT` deploy failures
- [x] Correct `.vercelignore` to exclude only untracked files (#13)
- [x] Move backend deploy into release flow after `create-release` (#14)
- [x] Restore Vercel `commandForIgnoringBuildStep` for production
- [x] Update docs (sessions, handoff, MEMORY, LESSONS, BUGS)
- [x] Set up session-todo workflow + rules
- [x] Commit docs update

### Carried Forward (next session)

- [x] Cut v0.1.5 tag → release flow end-to-end verified (APK → Release → deploy-backend to prod)
- [x] Verify `https://sasyakashi.vercel.app/api/health` returns ok after first release
- [x] Confirm species detail endpoint returns `images` key (fix live on prod)
- [ ] Real-device re-test of `gardenify-v0.1.5.apk`
- [ ] Fix Supabase prod auth config (Site URL / redirect URLs → production app, not localhost)
- [ ] Investigate "verified but cannot login" (missing `public.users` profile rows for Auth users)
- [ ] Re-test v0.1.5 APK on emulator against prod (login + identify flow)
- [ ] Expand hash index to remaining ~8K species
- [ ] Push notifications (Phase 3)

## 2026-08-02 Session — Identify 500 Fix + Release Notes

- [x] Fix `/api/identify` read-only FS 500 (PR #16) — temp-dir fallback + best-effort writes
- [x] Add 4 tests (`api/tests/test_image_processor.py`); 77 passed, ruff/tsc clean
- [x] PR #17: release-notes body template placeholders
- [x] Merge both PRs; verified prod auto-deploy (build `gardenify-7h7o4wo4x` Ready, aliased)
- [x] Verify prod `/api/identify` returns 400 (plant validation) not read-only FS 500
- [x] File & close issue #18 (read-only FS bug)
- [x] Update docs (handoff, sessions)
