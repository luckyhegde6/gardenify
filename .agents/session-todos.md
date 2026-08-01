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

- [ ] Cut next tag (e.g., v0.1.5) → verify new release flow end-to-end: APK build → GitHub Release → `deploy-backend` reaches production
- [ ] Verify `https://sasyakashi.vercel.app/health` returns `use_remote=true` + db ok after first release
- [ ] Confirm species detail endpoint returns `images` key (pending `supabase_species.py` fix reaching prod)
- [ ] Real-device re-test of `gardenify-v0.1.4.apk`
- [ ] Expand hash index to remaining ~8K species
- [ ] Push notifications (Phase 3)
