# LESSONS.md — Index

> Lessons are split by category under `.agents/lessons/`. Add new lessons to the matching file. Each entry: **Context → Fix/Pattern → Applies to → Severity → Status**.

## Categories

| File                                                                 | Covers                                                                               |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [`.agents/lessons/architecture.md`](.agents/lessons/architecture.md) | Initial decisions (PlantNet, Supabase, FastAPI proxy, care engine, caching)          |
| [`.agents/lessons/backend.md`](.agents/lessons/backend.md)           | FastAPI, PlantNet API, OpenCV, image processing, serverless FS, Pydantic/env, Pillow |
| [`.agents/lessons/database.md`](.agents/lessons/database.md)         | Supabase, RLS, migrations, seeds, jsonb, SQLite→Supabase, hash matching              |
| [`.agents/lessons/mobile.md`](.agents/lessons/mobile.md)             | Expo Router, React Native, auth guard, APK verification, emulator                    |
| [`.agents/lessons/ci-cd.md`](.agents/lessons/ci-cd.md)               | EAS Build, brace-expansion overrides, Vercel deploy, release flow, npm/pip CI        |
| [`.agents/lessons/git.md`](.agents/lessons/git.md)                   | Branching, PRs, secrets-in-commits, merge conflicts                                  |
| [`.agents/lessons/windows-dev.md`](.agents/lessons/windows-dev.md)   | Detached processes, server PID management on Windows                                 |
| [`.agents/lessons/testing.md`](.agents/lessons/testing.md)           | Jest, Playwright, Pytest, TDD, ruff                                                  |
| [`.agents/lessons/docs-process.md`](.agents/lessons/docs-process.md) | Documentation drift, session files, pre-commit workflow                              |

## Format

```markdown
## YYYY-MM-DD: Lesson Title

**Context:** What was happening
**Issue/Success:** What went wrong or right
**Fix/Pattern:** What should be done instead
**Applies to:** [backend | mobile | database | all]
**Severity:** [critical | important | minor]
**Status:** [active | superseded]
```

## Recent highlights

- **2026-08-06** expo-router initial-route `<Redirect>` is not an auth guard — guard the root layout → `mobile.md`
- **2026-08-05** global `brace-expansion` override broke EAS fingerprint — scope overrides by parent → `ci-cd.md`
- **2026-08-04** ESM-only `brace-expansion` override broke RN codegen gradle build → `ci-cd.md`
- **2026-08-04** prod admin locked out because seed `is_admin` never applied → `database.md`
- **2026-08-02** Vercel serverless FS read-only; SQLite never ships; jsonb rejects `json.dumps` strings → `backend.md`, `database.md`
- **2026-08-01** Vercel `lstat ENOENT` — never exclude git-tracked files via `.vercelignore` → `ci-cd.md`
