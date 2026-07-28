# OpenCode Rules for Gardenify

These rules guide OpenCode agents when working on this project.

## Project Context

- **Stack**: Expo SDK 55 + FastAPI + Supabase + PlantNet
- **Target**: Android-first, iOS later
- **Database**: Supabase PostgreSQL with RLS on every table
- **Backend**: Python FastAPI on Vercel serverless
- **Plant AI**: PlantNet API v2 (500/day free tier)

## Code Rules

1. **TypeScript**: No `any`, explicit return types, strict mode
2. **Python**: Type hints on all functions, Pydantic for models
3. **React Native**: Functional components only, hooks for state
4. **SQL**: Always use RLS, parameterized queries
5. **File naming**: Components = kebab-case.tsx, Python = snake_case.py

## Security Rules

1. Never commit secrets, API keys, or tokens
2. Use expo-secure-store for sensitive data
3. PlantNet API key stays server-side only
4. RLS policies on every database table
5. Validate all user inputs with Pydantic/Zod

## Testing Rules

1. Write tests for all new features
2. Run `npm run lint` and `npx tsc --noEmit` before commits
3. Run `pytest` for Python changes
4. Test edge cases, not just happy path

## Documentation Rules

1. Update LESSONS.md when learning something new
2. Comment WHY, not WHAT
3. Keep AGENTS.md current with architecture changes
4. Document API endpoints with request/response examples

## Environment Rules

1. Use `.env.example` as template
2. Never commit `.env` files
3. Use `EXPO_PUBLIC_` prefix for client-side env vars
4. Keep PlantNet API key in server-side env only
