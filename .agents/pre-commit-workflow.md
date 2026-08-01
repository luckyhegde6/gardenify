# Pre-Commit Workflow

> Run this checklist BEFORE every commit.

## Session Todo File (MANDATORY)

Always maintain `.agents/session-todos.md` from session start until the final commit:

1. **At session start**: copy the checklist + any carried-forward todos into the file.
2. **Before every commit**: review all todos — mark completed/cancelled; carry unfulfilled ones forward as "next session" todos.
3. **During commit check**: if an unfulfilled todo is a confirmed bug, add it to BUGS.md.
4. **Never drop a todo silently** — carry it forward or log it.

## Pre-Commit Checklist

```
□ SECURITY
  □ No hardcoded secrets (grep for api_key, password, secret, token)
  □ .env is gitignored
  □ gitleaks passes
  □ detect-private-key passes

□ CODE QUALITY
  □ TypeScript: npx tsc --noEmit
  □ Python: ruff check api/
  □ Python: ruff format --check api/
  □ No console.log in production code
  □ No bare except in Python
  □ No any types in TypeScript

□ TESTING
  □ pytest passes (make test-python)
  □ No test files modified (unless adding tests)
  □ New code has tests

□ DOCUMENTATION
  □ MEMORY.md updated
  □ LESSONS.md updated (if new discovery)
  □ .agents/sessions.md updated
  □ .agents/handoff-current.md updated
  □ .agents/session-todos.md checked — all done/carried-forward; unfulfilled bugs → BUGS.md
  □ PRD.md updated (if feature completed)
  □ BUGS.md updated (if bug fixed)
  □ Comments explain WHY, not WHAT

□ GIT
  □ Commit message follows convention
  □ One logical change per commit
  □ No merge conflicts
  □ Branch is up to date with main

□ PRODUCT
  □ Feature solves a real user problem
  □ UI is intuitive
  □ Error states are handled
  □ Loading states are shown
  □ Accessibility considered
```

## Commit Message Format

```
type(scope): brief description

- Detail 1
- Detail 2

Refs: #issue-number (if applicable)
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Build process, dependencies
- `perf`: Performance improvement
- `ci`: CI/CD changes
- `security`: Security fix

### Scopes

- `api`: Backend API
- `mobile`: Expo app
- `db`: Database/schema
- `ci`: CI/CD
- `docs`: Documentation
- `deps`: Dependencies

## Linear History Rules

```
□ NEVER use merge commits on main/develop
□ ALWAYS rebase feature branches before merge
□ ALWAYS squash when merging to main
□ One logical change per commit
□ Commit messages follow conventional format
```

## Automated Checks

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: gitleaks
        name: gitleaks
        entry: gitleaks protect --staged
        language: system
      - id: detect-private-key
        name: detect-private-key
        entry: detect-private-key
        language: system
      - id: ruff
        name: ruff check
        entry: ruff check api/
        language: system
      - id: tsc
        name: TypeScript check
        entry: npx tsc --noEmit
        language: system
      - id: pytest
        name: Python tests
        entry: cd api && pytest
        language: system
```

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx tsc --noEmit

  python:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: api
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest
```

## Quick Commands

```bash
# Run all checks
make precommit-run

# Run specific checks
make lint          # TypeScript lint
make typecheck     # TypeScript type check
make test-python   # Python tests
make lint-python   # Python lint

# Fix auto-fixable issues
npx expo lint --fix
ruff check api/ --fix
ruff format api/
```
