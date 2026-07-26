# Code Generation Guidelines for Gardenify

## Overview

These rules ensure consistent, high-quality code generation across all agents working on the project.

## 1. TypeScript/React Native Rules

### Component Structure
```tsx
// Always use functional components
export function PlantCard({ plant, onPress }: PlantCardProps) {
  return (/* ... */);
}

// Props interface defined above component
interface PlantCardProps {
  plant: Plant;
  onPress: (id: string) => void;
}
```

### File Organization
```
src/components/plant-card/
  index.tsx          # Main component
  styles.ts          # StyleSheet (platform-specific if needed)
  types.ts           # TypeScript interfaces
```

### Naming Conventions
- Components: `PascalCase` (PlantCard, IdentificationResult)
- Hooks: `use` prefix (useIdentification, useAuth)
- Utilities: `camelCase` (formatDate, computeHash)
- Constants: `UPPER_SNAKE_CASE` (API_BASE_URL, MAX_IMAGES)
- Files: `kebab-case.tsx` (plant-card.tsx, identification-result.tsx)

## 2. Python/FastAPI Rules

### Route Structure
```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()

class ResponseModel(BaseModel):
    field: str

@router.get("/endpoint", response_model=ResponseModel)
async def endpoint_name():
    """Docstring explaining the endpoint."""
    pass
```

### File Organization
```
api/
  main.py            # FastAPI app initialization
  config.py          # Settings and environment
  routes/            # API endpoint handlers
  services/          # Business logic
  models/            # Pydantic schemas
  middleware/         # Custom middleware
```

### Naming Conventions
- Functions: `snake_case` (identify_plant, compute_hash)
- Classes: `PascalCase` (IdentificationResponse, PlantNetClient)
- Constants: `UPPER_SNAKE_CASE` (API_BASE_URL, MAX_RETRIES)
- Files: `snake_case.py` (plantnet.py, cache.py)

## 3. Database Rules

### Migration Naming
```
001_initial_schema.sql
002_add_user_settings.sql
003_create_analytics_table.sql
```

### RLS Policy Naming
```sql
-- Pattern: [table]_[action]_[scope]
create policy "users_select_own"
    on public.users for select
    using (auth.uid() = id);
```

## 4. Documentation Rules

### Inline Comments
```typescript
// WHY: We use SHA-256 here because PlantNet deduplicates by hash
// and we need consistent hashing across client/server
const hash = computeImageHash(imageBytes);
```

### API Documentation
Every endpoint must have:
- Summary (1 line)
- Description (1-2 sentences)
- Request schema with examples
- Response schema with examples
- Error cases documented

## 5. Testing Rules

### Test File Naming
```
component-name.test.tsx    # Unit tests
api-endpoint.test.py       # API tests
feature-flow.test.ts       # Integration tests
```

### Test Structure
```typescript
describe('FeatureGroup', () => {
  describe('specificFeature', () => {
    it('should handle expected case', () => {
      // Arrange
      // Act
      // Assert
    });

    it('should handle edge case', () => {
      // ...
    });
  });
});
```

## 6. Git Commit Messages

### Format
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

## 7. Performance Guidelines

### React Native
- Use `React.memo` for expensive renders
- Lazy load images and screens
- Minimize re-renders with proper dependency arrays
- Use `useCallback` and `useMemo` judiciously

### API
- Pagination for list endpoints
- Caching with appropriate TTL
- Async I/O for all external calls
- Connection pooling for database

### Database
- Index frequently queried columns
- Use `explain analyze` to verify query plans
- Avoid N+1 queries
- Use transactions for multi-table operations
