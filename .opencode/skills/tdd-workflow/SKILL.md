---
name: tdd-workflow
description: Test-Driven Development workflow for Gardenify. Write tests first, implement, verify 80%+ coverage.
---

## What I do
Enforce TDD methodology: RED (write failing test) → GREEN (minimal implementation) → REFACTOR (improve).

## When to use me
Use this when starting a new feature, fixing a bug, or refactoring code in Gardenify.

## Workflow

### 1. Write Test First (RED)
```bash
# For TypeScript/React Native
npx jest --testPathPattern=<feature-name>

# For Python/FastAPI
cd api && pytest tests/test_<feature>.py -v
```

### 2. Implement (GREEN)
Write the minimum code to make the test pass. No speculative features.

### 3. Refactor (IMPROVE)
- Remove duplication
- Improve naming
- Extract helpers
- Verify all tests still pass

### 4. Verify Coverage
```bash
# TypeScript
npx jest --coverage

# Python
cd api && pytest --cov=. --cov-report=term-missing
```

## Gardenify-Specific Rules
- Tests for API routes must mock PlantNet API calls
- Tests for Supabase must test RLS policies
- Tests for Expo components must use `@testing-library/react-native`
- Always test error cases, not just happy path
- Never test implementation details — test behavior

## Test File Locations
- TypeScript: `__tests__/` adjacent to source files
- Python: `api/tests/` mirroring `api/routes/` and `api/services/`
- E2E: `e2e/` directory with Playwright specs
