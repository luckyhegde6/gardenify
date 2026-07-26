# Linear History & Changelog Rules

> Maintain clean git history and automatic changelogs.

## 1. Linear History Rules

### Why Linear History?
- Easy to bisect bugs
- Clear feature progression
- Simple rollbacks
- Readable `git log`

### Rules
```
□ NEVER use merge commits on main/develop
□ ALWAYS rebase feature branches before merge
□ ALWAYS squash when merging to main
□ One logical change per commit
□ Commit messages follow conventional format
```

### Git Workflow
```bash
# Feature branch
git checkout -b feature/xyz-123-plant-care

# Make changes
git add -A
git commit -m "feat(plant-care): add watering schedule UI"

# Rebase before push
git rebase main

# Push
git push origin feature/xyz-123-plant-care

# Merge (squash)
git checkout main
git merge --squash feature/xyz-123-plant-care
git commit -m "feat(plant-care): add watering schedule UI"

# Delete branch
git branch -d feature/xyz-123-plant-care
```

## 2. Changelog Format

### CHANGELOG.md Structure
```markdown
# Changelog

## [Unreleased]

### Added
- New features

### Changed
- Changes to existing features

### Fixed
- Bug fixes

### Removed
- Removed features

### Security
- Security fixes

---

## [1.2.0] - 2026-07-27

### Added
- Plant disease detection endpoint
- Care instructions for identified plants
- EXIF metadata extraction

### Fixed
- Image upload validation error handling
- Cache key collision issue

---

## [1.1.0] - 2026-07-20

### Added
- Basic plant identification
- User authentication
- History screen
```

### Version Numbers
- **Major (X.0.0)**: Breaking changes
- **Minor (0.X.0)**: New features (backward compatible)
- **Patch (0.0.X)**: Bug fixes

## 3. Commit Message Convention

### Format
```
type(scope): brief description

[optional body]

[optional footer]
```

### Types
| Type | Description | Example |
|---|---|---|
| feat | New feature | feat(api): add disease detection |
| fix | Bug fix | fix(cache): handle expired entries |
| docs | Documentation | docs(readme): add API examples |
| style | Formatting | style(api): fix import order |
| refactor | Restructure | refactor(plantnet): extract parser |
| test | Tests | test(api): add identify endpoint tests |
| chore | Build/deps | chore(deps): update fastapi |
| perf | Performance | perf(cache): add TTL cleanup |
| ci | CI/CD | ci: add Python test job |
| revert | Revert | revert: undo cache change |

### Scopes
| Scope | Description |
|---|---|
| api | Backend API |
| mobile | Expo app |
| db | Database/schema |
| ci | CI/CD |
| docs | Documentation |
| deps | Dependencies |
| security | Security |

### Examples
```
feat(api): add plant care endpoint

- Returns watering, sunlight, soil info
- Maps genus/family to care profiles

Closes #42

fix(mobile): handle camera permission denied

- Show helpful error message
- Redirect to settings

Fixes #38

chore(deps): update expo to SDK 55

- Update all expo packages
- Fix breaking changes
```

## 4. Automated Changelog Generation

### Using git-cliff
```bash
# Install
brew install git-cliff  # macOS
cargo install git-cliff  # Rust

# Generate changelog
git cliff -o CHANGELOG.md

# Add to pre-commit hook
git cliff -o CHANGELOG.md && git add CHANGELOG.md
```

### git-cliff Config (cliff.toml)
```toml
[changelog]
header = "# Changelog\n\n"
body = """
{% if version %}\
    ## [{{ version | trim_start_matches(pat="v") }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
    ## [Unreleased]
{% endif %}\
{% for commit in commits %}
    - {{ commit.message | upper_first }}{% if commit.scope %} ({{ commit.scope }}){% endif %}\
{% endfor %}
"""
```

## 5. Pre-Commit Checks

```
□ Commit message follows convention
□ One logical change per commit
□ No merge conflicts
□ All tests pass
□ Lint passes
□ Type check passes
□ No secrets in commit
□ Changelog updated (if applicable)
```

## 6. Release Process

### Before Release
```bash
# 1. Update version in package.json
npm version minor  # or major/patch

# 2. Generate changelog
git cliff -o CHANGELOG.md

# 3. Commit
git add -A
git commit -m "chore(release): v1.2.0"

# 4. Tag
git tag -a v1.2.0 -m "Release v1.2.0"

# 5. Push
git push origin main --tags
```

### Release Checklist
```
□ Version bumped
□ Changelog generated
□ All tests pass
□ Build succeeds
□ Documentation updated
□ Breaking changes documented
□ Migration guide (if needed)
□ GitHub release created
```

## 7. Hotfix Process

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-bug main

# 2. Fix the bug
git add -A
git commit -m "fix(security): patch XSS vulnerability"

# 3. Rebase
git rebase main

# 4. Merge (squash)
git checkout main
git merge --squash hotfix/critical-bug
git commit -m "fix(security): patch XSS vulnerability"

# 5. Tag
git tag -a v1.2.1 -m "Hotfix v1.2.1"

# 6. Push
git push origin main --tags
```

## 8. Branch Protection Rules

### Main Branch
```
□ Require pull request reviews
□ Require status checks (CI)
□ Require up-to-date branches
□ Restrict force pushes
□ Require signed commits (optional)
```

### Develop Branch
```
□ Require pull request reviews
□ Require status checks (CI)
□ Allow force pushes (for rebasing)
```
