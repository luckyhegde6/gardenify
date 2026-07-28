# Release Guidelines

> How to version, build, and distribute Gardenify.

## Overview

Gardenify is distributed as a direct APK download — no Play Store. The release pipeline:

1. Code merges to `main` via PR
2. EAS builds a new APK automatically
3. A git tag triggers a GitHub Release
4. APK is available on Expo for download
5. Users install the APK directly on Android devices

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

| Change Type | Version Bump | Example |
|---|---|---|
| Bug fix | `patch` | 1.0.0 → 1.0.1 |
| New feature | `minor` | 1.0.0 → 1.1.0 |
| Breaking change | `major` | 1.0.0 → 2.0.0 |
| Pre-release | suffix | 1.1.0-alpha.1, 1.1.0-beta.2 |

## Release Steps

### Patch Release (bug fix)
```bash
git checkout main && git pull origin main
npm version patch
git push origin main --follow-tags
```

### Minor Release (new feature)
```bash
git checkout main && git pull origin main
npm version minor
git push origin main --follow-tags
```

### Major Release (breaking change)
```bash
git checkout main && git pull origin main
npm version major
git push origin main --follow-tags
```

### Pre-release
```bash
git checkout main && git pull origin main
npm version prerelease --preid=alpha   # 1.1.0-alpha.0
# or
npm version prerelease --preid=beta    # 1.1.0-beta.0
git push origin main --follow-tags
```

## What Happens on Release

When you push a `v*` tag:

1. **GitHub Release** is created automatically with release notes
2. **EAS Build** builds a production APK (runs on every push to main)
3. **Vercel** deploys the backend if `api/` changed
4. **Supabase** runs migrations if `supabase/` changed

## APK Distribution

### For Users
1. Go to [GitHub Releases](https://github.com/luckyhegde6/gardenify/releases)
2. Download the latest APK
3. On Android: Enable "Install from unknown sources" if prompted
4. Open the APK to install

### For Testing
1. Go to [EAS Builds](https://expo.dev/accounts/luckyhegdedev/projects/gardenify/builds)
2. Download the preview APK
3. Install on device

## OTA Updates (Expo)

Preview updates are published automatically when code is pushed to `feat/*`, `bugfix/*`, or `chore/*` branches.

To push an OTA update manually:
```bash
eas update --branch preview --auto
```

**Note:** Production OTA updates are NOT used. All production changes go through the full release cycle.

## Release Checklist

Before tagging a release:

```
Development:
  [ ] All features complete
  [ ] All bugs fixed
  [ ] Code reviewed and approved via PR
  [ ] CI passing (lint + typecheck + tests)

Quality:
  [ ] Manual testing on Android device
  [ ] No crashes or ANRs
  [ ] API endpoints working on production
  [ ] Supabase migrations applied

Release:
  [ ] Version bumped in package.json
  [ ] Changelog updated (if maintained)
  [ ] Tag pushed to main
  [ ] GitHub Release created
  [ ] APK build successful on EAS
  [ ] Download link verified
```

## Rollback

If a release has critical issues:

1. **Immediate:** Tag a hotfix from main
   ```bash
   git checkout main
   git checkout -b hotfix/critical-fix
   # fix, commit, PR, merge
   npm version patch
   git push origin main --follow-tags
   ```

2. **Notify users:** Update GitHub Release notes or create new release

3. **No OTA rollback** — since production doesn't use OTA, users must reinstall the APK

## Environment Variables

### Required GitHub Secrets
| Secret | Purpose |
|---|---|
| `EXPO_TOKEN` | EAS build and update |
| `VERCEL_TOKEN` | Backend deployment |
| `SUPABASE_ACCESS_TOKEN` | Database migrations |
| `SUPABASE_PROJECT_REF` | Supabase project ID |
| `SUPABASE_DB_PASSWORD` | Database password |

### Mobile App Config
| Variable | Value |
|---|---|
| `EXPO_PUBLIC_API_URL` | `https://sasyakashi.vercel.app` (production) |
| `EXPO_PUBLIC_SUPABASE_URL` | From Supabase dashboard |
| `EXPO_PUBLIC_SUPABASE_ANON_KEY` | From Supabase dashboard |
