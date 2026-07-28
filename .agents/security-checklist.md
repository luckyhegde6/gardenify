# Security Checklist

> Run this checklist before EVERY commit. Security is not optional.

## Pre-Commit Security Gate

```
□ SECRETS: No hardcoded API keys, tokens, passwords, or secrets
□ ENV: All secrets in .env (gitignored) or environment variables
□ KEYS: No private keys, JWT secrets, or signing keys in code
□ RLS: All database tables have Row Level Security enabled
□ AUTH: User can only access their own data (auth.uid() checks)
□ INPUT: All user inputs validated (Pydantic/Zod)
□ SQL: Parameterized queries only (no string concatenation)
□ UPLOAD: File uploads validated (type, size, count)
□ LOGS: No PII or secrets in log output
□ ERRORS: Error messages don't leak internal details
□ CORS: Only known origins allowed
□ HTTPS: Enforced in production
□ DEPS: No known vulnerable dependencies
```

## Detailed Security Checks

### 1. Secrets Management
```bash
# Check for hardcoded secrets
grep -rn "api_key\|password\|secret\|token" --include="*.py" --include="*.ts" api/ src/
grep -rn "AKIA\|sk_live\|pk_live" --include="*.py" --include="*.ts" api/ src/

# Verify .env is gitignored
git check-ignore .env

# Run gitleaks
gitleaks protect --staged
```

### 2. Authentication & Authorization
```sql
-- Every table must have RLS enabled
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;

-- Every table must have at least one policy
CREATE POLICY "users_select_own" ON table_name
    FOR SELECT USING (auth.uid() = user_id);

-- Test: Can user A access user B's data?
-- Should return 0 rows
SELECT * FROM table_name WHERE user_id = 'other-user-id';
```

### 3. Input Validation
```python
# Backend: Always use Pydantic models
class IdentifyRequest(BaseModel):
    organs: list[str] = Field(default=["auto"])
    lang: str = Field(default="en", max_length=5)

# Frontend: Always use Zod schemas
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});
```

### 4. File Upload Security
```python
# Validate file type
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg"}
if content_type not in ALLOWED_TYPES:
    raise HTTPException(400, "Invalid file type")

# Validate file size
if size > 10 * 1024 * 1024:  # 10MB
    raise HTTPException(400, "File too large")

# Validate file count
if len(files) > 5:
    raise HTTPException(400, "Too many files")
```

### 5. Error Handling
```python
# Never expose internal details
try:
    result = call_external_api()
except Exception as e:
    logger.error("API call failed: %s", e)  # Log full error
    raise HTTPException(502, "Service unavailable")  # Generic message
```

### 6. Dependency Security
```bash
# Check for known vulnerabilities
npm audit
pip-audit

# Update vulnerable dependencies
npm audit fix
pip install --upgrade vulnerable-package
```

## Security Incident Response

If a security issue is found:

1. **IMMEDIATE**: Rotate compromised credentials
2. **ASSESS**: Determine scope of impact
3. **FIX**: Patch the vulnerability
4. **NOTIFY**: Inform affected users if needed
5. **DOCUMENT**: Add to LESSONS.md with prevention steps
6. **PREVENT**: Add test/rule to prevent recurrence

## Security Audit Schedule

| Check | Frequency | Tool |
|---|---|---|
| Dependency scan | Every commit | npm audit, pip-audit |
| Secret scan | Every commit | gitleaks, detect-secrets |
| RLS policy review | Every schema change | Manual + automated test |
| API key rotation | Quarterly | Manual |
| Penetration test | Before launch | External |
