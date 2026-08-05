# Lessons — Git Workflow (Branching, PRs, Secrets)

## 2026-08-03: Secrets in Commits + Direct-to-main Commits (Both Caught, Both Fixed)

**Context:** During the SQLite→Supabase refactor, a Supabase Management API token (`sbp_…`) was committed into `.agents/session-todos.md` inside a commit made **directly on `main`**. `git push` was rejected by GitHub push protection (`GH013` — Push cannot contain secrets).

**Lessons applied:**

1. **Raw secrets belong ONLY on gitignored files.** `.env.local`, `creds.json`, `.agents/handoff-current.md` are gitignored; tracked docs must reference a pointer (e.g. "see `creds.json`"), never the value. Verify with `git grep -nE 'sbp_[a-f0-9]{20,}'` before every push.
2. **GitHub push protection saved us** — the push was rejected so the token **never reached GitHub**. Rotation is still recommended hygiene for any secret written to a file.
3. **Fix a secret committed to history properly:** move the commit to a feature branch, `git add` the cleaned file, `git commit --amend` to rewrite the offending commit, verify `git grep` on `HEAD` is clean, then `git reset --hard origin/main` to restore `main`.
4. **Never commit on `main`.** Even mid-refactor, work goes on branches and merges via PR. Blocked locally by `.githooks/pre-commit` + `.githooks/pre-push`.
5. **Hooks must be versioned + opt-in per clone.** Hooks live in `.githooks/` and each clone runs `git config core.hooksPath .githooks`.

**Verification:** after `--amend`, `git grep -n "sbp_f527" HEAD` returns nothing; `git push` succeeded with no `GH013` block; CI on PR #21 all green.

## Branch Divergence Causes Massive Merge Conflicts

**Context:** Merging stashed changes from `develop` (diverged significantly from `main`) into a new branch from `main`. 15+ merge conflicts; had to manually resolve by accepting "ours".

**Fix:** Use `git stash` then `git checkout main && git checkout -b feat/... && git stash pop`. For large divergences use squash-merge or cherry-pick instead of merge.

## Always Check Open PRs Before Starting New Work

**Issue:** Two open PRs (#1, #2) modified the same core files → 15+ merge conflicts.

**Fix:** Before creating any new branch, run `gh pr list`. If an existing PR touches overlapping files, either branch from that PR's branch or coordinate to avoid overlap.

**Pattern:** `gh pr list` → check file overlap → branch from the right base. Never start from `main` blindly when other PRs are in flight.

## Don't Branch From Main When Other PRs Target Main

**Issue:** Two PRs both branching from `main` with the same merge base and overlapping files → conflicts on every overlapping file; had to use `git merge --ours`, losing content.

**Fix:** When multiple PRs are in flight, identify the "base" PR (larger scope, foundational) and branch new work from that PR's branch, making the second PR a clean superset.

## Clean Up Analysis Repos After Research

**Context:** Cloned `plantnet-ai-taxonomist` and `plantnet-300k` for analysis. Both were cloned to temp dir AND project root; the TS files broke `npx tsc --noEmit`.

**Pattern:** After analyzing external repos: delete clones from project root immediately, add cloned dirs to `.gitignore`, extract only the data/code you actually need.
