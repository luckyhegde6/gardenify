# Orchestration Agents

> Automated monitoring and coordination for Gardenify development.

## 1. CI Monitor Agent

**Trigger:** Every push to any branch.

### Responsibilities
- Run lint, typecheck, and Python tests
- Report failures immediately
- Block PR merge if CI is red

### CI Commands
```bash
# TypeScript
npx tsc --noEmit

# Python lint
cd api && ruff check .

# Python tests
cd api && pytest --tb=short

# Full CI locally
npx tsc --noEmit && cd api && ruff check . && cd api && pytest --tb=short
```

### Failure Protocol
1. CI fails → agent reads error output
2. Agent identifies the failing check (lint, typecheck, or test)
3. Agent reads the relevant source file
4. Agent fixes the issue
5. Agent re-runs the failing check
6. If still failing, agent surfaces the issue to the user

## 2. PR Review Agent

**Trigger:** PR opened or updated targeting `main`.

### Pre-Merge Checklist
```
[ ] All CI checks pass
[ ] No merge conflicts with main
[ ] Branch is up to date with main
[ ] Code follows project conventions
[ ] No secrets or API keys committed
[ ] New routes have proper error handling
[ ] Database changes have RLS policies
[ ] API changes have Pydantic models
[ ] TypeScript has no 'any' types
[ ] Commit messages follow convention
```

### Review Commands
```bash
# Check for conflicts
git fetch origin
git merge-base --is-ancestor origin/main HEAD

# Check for secrets
git diff origin/main -- '*.py' '*.ts' '*.tsx' '*.json' | grep -i "password\|secret\|token\|key" | grep -v "SUPABASE\|PLANTNET\|VERCEL\|EXPO"

# Check Python conventions
cd api && ruff check .

# Check TypeScript
npx tsc --noEmit
```

## 3. Release Agent

**Trigger:** User runs `npm version` and pushes tags.

### Release Protocol
1. Verify you're on `main` and up to date
2. Verify all CI checks pass
3. Run `npm version patch/minor/major`
4. Push with `git push origin main --follow-tags`
5. Verify GitHub Release was created
6. Verify EAS build was triggered
7. Report the release URL and APK download link

### Post-Release Verification
```bash
# Check release exists
curl -s https://api.github.com/repos/luckyhegde6/gardenify/releases/latest | jq '.tag_name'

# Check API health
curl -s https://sasyakashi.vercel.app/api/health

# Check species endpoint
curl -s "https://sasyakashi.vercel.app/api/species?limit=1"
```

## 4. Deployment Agent

**Trigger:** Push to `main` with changes in `api/` or `supabase/`.

### Backend Deploy Protocol
1. Detect changes in `api/` directory
2. Verify Python lint and tests pass
3. Verify Vercel deployment succeeds
4. Check health endpoint after deploy
5. Verify API endpoints work

### Database Migration Protocol
1. Detect changes in `supabase/` directory
2. Verify migration SQL is valid
3. Check that Supabase migration ran successfully
4. Verify the schema is correct post-migration

### Deploy Monitoring Commands
```bash
# Check Vercel deployment
curl -s https://sasyakashi.vercel.app/api/health

# Check species API
curl -s "https://sasyakashi.vercel.app/api/species?limit=1"

# Check landing page
curl -s -o /dev/null -w "%{http_code}" https://sasyakashi.vercel.app
```

## 5. Development Workflow Agent

**Trigger:** User starts new work.

### New Feature Flow
```
1. git checkout main && git pull origin main
2. git checkout -b feat/feature-name
3. [implement feature]
4. git add -A && git commit -m "feat(scope): description"
5. git push origin feat/feature-name
6. [create PR: main ← feat/feature-name]
7. [CI runs automatically]
8. [get approval]
9. [squash merge]
10. git checkout main && git pull origin main
11. git branch -d feat/feature-name
```

### Bug Fix Flow
```
1. git checkout main && git pull origin main
2. git checkout -b bugfix/bug-description
3. [write test that reproduces bug]
4. [fix the bug]
5. [verify test passes]
6. git add -A && git commit -m "fix(scope): description"
7. git push origin bugfix/bug-description
8. [create PR: main ← bugfix/bug-description]
9. [CI runs automatically]
10. [get approval + merge]
```

### Chore/Maintenance Flow
```
1. git checkout main && git pull origin main
2. git checkout -b chore/maintenance-task
3. [perform maintenance]
4. git add -A && git commit -m "chore(scope): description"
5. git push origin chore/maintenance-task
6. [create PR: main ← chore/maintenance-task]
7. [CI runs automatically]
8. [merge]
```

## 6. Monitoring Dashboard

### Health Checks (run periodically)
```bash
# API Health
curl -s https://sasyakashi.vercel.app/api/health | jq .

# Landing Page
curl -s -o /dev/null -w "Landing: %{http_code}\n" https://sasyakashi.vercel.app

# Swagger Docs
curl -s -o /dev/null -w "Docs: %{http_code}\n" https://sasyakashi.vercel.app/docs

# Species API
curl -s "https://sasyakashi.vercel.app/api/species?q=rose&limit=1" | jq .count

# Identify endpoint
curl -s -o /dev/null -w "Identify: %{http_code}\n" https://sasyakashi.vercel.app/api/identify
```

### Status Summary
```
Component       Status    URL
─────────────   ──────    ───
Landing Page    ✅        https://sasyakashi.vercel.app
Swagger Docs    ✅        https://sasyakashi.vercel.app/docs
API Health      ✅        https://sasyakashi.vercel.app/api/health
Species API     ✅        https://sasyakashi.vercel.app/api/species
GitHub Repo     ✅        https://github.com/luckyhegde6/gardenify
```
