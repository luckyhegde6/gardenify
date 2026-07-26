---
name: security-review
description: Security review for Gardenify. Checks auth, API endpoints, RLS policies, and sensitive data handling.
---

## What I do
Comprehensive security review covering: authentication, authorization, input validation, data exposure, and dependency vulnerabilities.

## When to use me
Use this after writing code that handles: user authentication, API endpoints, database queries, file uploads, or sensitive data.

## Security Checklist

### Authentication & Authorization
- [ ] Supabase Auth properly configured
- [ ] JWT tokens validated on backend
- [ ] Session management uses SecureStore (not AsyncStorage)
- [ ] No hardcoded credentials

### API Security
- [ ] All inputs validated with Pydantic models
- [ ] Rate limiting configured
- [ ] CORS properly restricted
- [ ] Error messages don't leak internals
- [ ] PlantNet API key stays server-side only

### Database Security
- [ ] RLS enabled on every table
- [ ] `auth.uid()` used in RLS policies
- [ ] No SQL injection vectors (parameterized queries)
- [ ] Service role key never exposed to client

### Data Exposure
- [ ] No secrets in client-side code
- [ ] No API keys in git history
- [ ] Environment variables used for config
- [ ] `.env` files in `.gitignore`

### Dependencies
- [ ] No known vulnerabilities in dependencies
- [ ] Dependencies are pinned to specific versions
- [ ] No unnecessary dependencies added

## Gardenify-Specific Concerns
- PlantNet API key must NEVER be in mobile app code
- Supabase `service_role` key must NEVER be in mobile app code
- User plant images stored in Supabase Storage with RLS
- Identification results tied to user via `user_id` foreign key
- Cache keys use SHA-256 hashes (no user data in cache keys)

## Severity Levels
- **CRITICAL**: Immediate fix required, block commit
- **HIGH**: Fix before merge
- **MEDIUM**: Fix when possible
- **LOW**: Track for future improvement
