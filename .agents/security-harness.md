# Security Harness for Gardenify

## Mandatory Security Checks

Before any code is committed or deployed, verify:

### Authentication & Authorization
```
□ No hardcoded API keys, tokens, or secrets
□ All database tables have RLS enabled
□ User can only access their own data
□ Service role key never exposed to client
□ JWT tokens validated on every request
```

### Input Validation
```
□ All user inputs validated with Pydantic (backend)
□ All form inputs validated with Zod (frontend)
□ File uploads validated (type, size, count)
□ SQL queries parameterized (never string concatenation)
□ No eval() or exec() on user input
```

### Data Protection
```
□ HTTPS enforced in production
□ Sensitive data not logged
□ API keys stored in environment variables
□ Image URLs not publicly accessible without auth
□ No PII in error messages
```

### Rate Limiting
```
□ PlantNet API quota tracked and enforced
□ Per-user identification limits enforced
□ File upload size limits enforced
□ CORS configured for known origins only
```

## Security Audit Schedule

| Check | Frequency | Owner |
|---|---|---|
| Dependency scan | Weekly | CI/CD |
| RLS policy review | Monthly | Manual |
| API key rotation | Quarterly | Manual |
| Penetration test | Before launch | External |

## Incident Response

If a security issue is discovered:

1. **Immediate**: Rotate the compromised credential
2. **Assess**: Determine scope of impact
3. **Fix**: Patch the vulnerability
4. **Notify**: Inform affected users if needed
5. **Document**: Add to LESSONS.md with prevention steps

## Environment Variables

All secrets must be in `.env` (local) or Vercel/Supabase environment (production):

```bash
# Backend (Vercel)
PLANTNET_API_KEY=...
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...

# Frontend (Expo)
EXPO_PUBLIC_SUPABASE_URL=...
EXPO_PUBLIC_SUPABASE_ANON_KEY=...
```

Never commit `.env` files. Use `.env.example` as template.
