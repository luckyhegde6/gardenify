# Git Flow & Branching Strategy

> Branch protection, PR-only merges, and release workflow.

## 1. Branch Naming Convention

All branches MUST follow this naming pattern:

```
feat/short-description      # New features
bugfix/short-description    # Bug fixes
chore/short-description     # Maintenance, deps, config
hotfix/short-description    # Critical production fixes
preview                    # OTA preview updates
```

### Examples
```
feat/plant-care-screen
feat/species-search-filter
bugfix/camera-permission-crash
bugfix/identify-timeout
chore/update-expo-sdk
chore/add-ruff-config
hotfix/auth-token-expiry
```

### Rules
```
NEVER commit directly to main
NEVER use feature/ prefix (use feat/)
NEVER use fix/ prefix (use bugfix/)
ALWAYS create a PR for all changes to main
ALWAYS get CI green before merging
ALWAYS squash-merge to main
```

## 2. Branch Protection Rules

### Main Branch (GitHub Settings)
Configure these in GitHub → Settings → Branches → Branch protection rules:

```
Branch name pattern: main

Required:
  [x] Require a pull request before merging
      [x] Require approvals (1 minimum)
      [x] Dismiss stale pull request approvals when new commits are pushed
  [x] Require status checks to pass before merging
      Required checks:
        - Lint & TypeCheck
        - Python Tests
  [x] Require branches to be up to date before merging
  [x] Require conversation resolution before merging

Restrictions:
  [x] Restrict force pushes
  [x] Restrict deletions
  [x] Do not allow bypassing the above settings
```

### How to Set Up
1. Go to `https://github.com/luckyhegde6/gardenify/settings/branches`
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Enable all options listed above
5. Save changes

## 3. Development Workflow

### Starting New Work
```bash
# Always start from latest main
git checkout main
git pull origin main

# Create your branch
git checkout -b feat/my-new-feature

# Make changes, commit with conventional messages
git add -A
git commit -m "feat(scope): add new feature"

# Push and create PR
git push origin feat/my-new-feature
# Open PR: main ← feat/my-new-feature
```

### PR Requirements
```
Before PR can be merged:
  [ ] All CI checks pass (TypeScript, Python, lint)
  [ ] At least 1 approval
  [ ] Branch is up to date with main
  [ ] All conversations resolved
  [ ] No merge conflicts
```

### Commit Message Convention
```
type(scope): brief description

[optional body]
[optional footer]
```

| Type | When | Example |
|---|---|---|
| `feat` | New feature | `feat(api): add species search` |
| `fix` | Bug fix | `fix(mobile): handle camera error` |
| `chore` | Maintenance | `chore(deps): update fastapi` |
| `docs` | Documentation | `docs(readme): add API examples` |
| `style` | Formatting | `style(api): fix imports` |
| `refactor` | Restructure | `refactor(db): extract queries` |
| `test` | Add tests | `test(api): add identify tests` |
| `perf` | Performance | `perf(cache): add cleanup` |
| `ci` | CI/CD | `ci: add release workflow` |
| `revert` | Revert | `revert: undo cache change` |

## 4. Release Process

### Version Bumping
```bash
# From main, after PR merge
npm version patch   # Bug fixes: 1.0.0 → 1.0.1
npm version minor   # New features: 1.0.0 → 1.1.0
npm version major   # Breaking: 1.0.0 → 2.0.0
```

### Creating a Release
```bash
# 1. Ensure you're on main and up to date
git checkout main
git pull origin main

# 2. Bump version (updates package.json)
npm version minor   # or patch/major

# 3. Push with tags
git push origin main --follow-tags

# This triggers:
#   → GitHub Action creates a Release with release notes
#   → EAS builds a new APK (production profile)
#   → Release appears at https://github.com/luckyhegde6/gardenify/releases
```

### APK Distribution
- APKs are built via EAS and available at [expo.dev](https://expo.dev/accounts/luckyhegdedev/projects/gardenify/builds)
- GitHub Release page includes download instructions
- No Play Store — direct APK distribution only

### Pre-release Tags
```bash
# Alpha/beta releases
git tag -a v1.1.0-alpha.1 -m "Alpha v1.1.0"
git tag -a v1.1.0-beta.1 -m "Beta v1.1.0"
git push origin main --tags
```

## 5. Hotfix Process

For critical production fixes:
```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# 2. Fix, commit, push
git add -A
git commit -m "fix(security): patch vulnerability"
git push origin hotfix/critical-fix

# 3. Create PR: main ← hotfix/critical-fix
# 4. After merge, tag release
git checkout main
git pull origin main
npm version patch
git push origin main --follow-tags
```

## 6. Pre-Push Checklist

```
Before pushing ANY branch:
  [ ] npm run lint (TypeScript)
  [ ] npx tsc --noEmit (type check)
  [ ] cd api && pytest (Python tests)
  [ ] ruff check . (Python lint)
  [ ] Commit messages follow convention
  [ ] No secrets or keys in code
  [ ] Branch is rebased on latest main (if behind)
```

## 7. CI/CD Pipeline Summary

```
Push to feat/bugfix/chore branch
  → CI runs (lint + typecheck + Python tests)
  → EAS Update published to preview branch

PR to main
  → CI runs (lint + typecheck + Python tests)
  → Requires approval + green CI

Merge to main (squash)
  → EAS builds APK (production profile)
  → Vercel deploys backend (if api/ changed)
  → Supabase runs migrations (if supabase/ changed)

Tag v*
  → GitHub Release created
  → APK available for download
```
