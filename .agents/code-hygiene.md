# Code Hygiene Rules

> Follow these rules for clean, maintainable code.

## 1. File Size Limits

| Type | Max Lines | Action if Exceeded |
|---|---|---|
| Component | 200 | Split into sub-components |
| Hook | 100 | Extract logic to utility |
| Utility | 150 | Split by responsibility |
| API route | 100 | Extract to service layer |
| Test file | 300 | Split by test group |
| Config file | 50 | Use external config |

## 2. Function Complexity

| Metric | Limit | Action |
|---|---|---|
| Lines per function | 50 | Extract helper functions |
| Parameters per function | 5 | Use options object |
| Nesting depth | 3 | Use early returns |
| Cyclomatic complexity | 10 | Simplify logic |

## 3. Import Rules

```typescript
// 1. React/React Native
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';

// 2. Expo
import { Image } from 'expo-image';
import * as FileSystem from 'expo-file-system';

// 3. Third-party
import {supabase} from '@supabase/supabase-js';

// 4. Internal (relative)
import { Button } from '../components/Button';
import { colors } from '../constants/colors';

// 5. Path aliases
import { helper } from '@/utils/helper';
```

## 4. Naming Conventions

| Type | Convention | Example |
|---|---|---|
| Component | PascalCase | `PlantCard.tsx` |
| Hook | camelCase + use | `useIdentification.ts` |
| Utility | camelCase | `formatDate.ts` |
| Constant | UPPER_SNAKE | `API_BASE_URL` |
| Type/Interface | PascalCase | `PlantSpecies` |
| CSS Module | camelCase | `plantCard.module.css` |
| Python file | snake_case | `plantnet.py` |
| Python class | PascalCase | `PlantNetClient` |
| Python function | snake_case | `identify_plant` |
| SQL table | snake_case | `user_settings` |
| SQL policy | snake_case | `users_select_own` |

## 5. Comment Rules

```typescript
// ✅ GOOD: Explain WHY
// We use SHA-256 because PlantNet deduplicates by hash
const hash = computeHash(image);

// ✅ GOOD: Explain non-obvious behavior
// PlantNet returns 429 when quota exceeded, not 403
if (response.status === 429) {
  throw new QuotaExceededError();
}

// ❌ BAD: Explain WHAT (redundant)
// Compute hash
const hash = computeHash(image);

// ❌ BAD: Obvious comments
// Return the result
return result;
```

## 6. Error Handling Patterns

```typescript
// ✅ GOOD: Specific error types
class PlantNetError extends Error {
  constructor(message: string, public statusCode: number) {
    super(message);
    this.name = 'PlantNetError';
  }
}

// ✅ GOOD: Graceful degradation
try {
  const disease = await identifyDisease(image);
} catch (error) {
  // Disease detection is non-critical
  logger.warn('Disease detection failed:', error);
  return null;
}

// ❌ BAD: Swallowing errors
try {
  const result = await riskyOperation();
} catch (e) {
  // ignore
}
```

## 7. Testing Standards

```typescript
// ✅ GOOD: Descriptive test names
describe('identifyPlant', () => {
  it('should return species when valid image provided', async () => {
    // Arrange
    const image = createTestImage();
    
    // Act
    const result = await identifyPlant(image);
    
    // Assert
    expect(result.species).toBeDefined();
    expect(result.confidence).toBeGreaterThan(0);
  });

  it('should throw when no images provided', async () => {
    await expect(identifyPlant([])).rejects.toThrow('At least one image');
  });
});
```

## 8. Git Hygiene

### Commit Messages
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
- `perf`: Performance improvement
- `ci`: CI/CD changes

### Branch Naming
```
feature/xyz-123-short-description
bugfix/xyz-123-short-description
hotfix/xyz-123-short-description
chore/short-description
```

## 9. Documentation Standards

### README.md
- Project overview (1 paragraph)
- Quick start (3-5 commands)
- Environment variables
- API endpoints
- Contributing guidelines

### Code Comments
- WHY, not WHAT
- TODO format: `// TODO(username): description`
- FIXME format: `// FIXME(username): description`
- NO generic comments like `// Initialize variable`

### API Documentation
Every endpoint must have:
- Summary (1 line)
- Description (1-2 sentences)
- Request schema with examples
- Response schema with examples
- Error cases documented

## 10. Performance Checklist

```
□ Images compressed before upload
□ Lazy loading for lists
□ Memoization for expensive computations
□ Debounced search/filter inputs
□ Pagination for large datasets
□ Caching with appropriate TTL
□ No unnecessary re-renders
□ Bundle size < 50MB
```

## 11. Accessibility Checklist

```
□ All images have alt text
□ Touch targets >= 44x44 points
□ Color contrast >= 4.5:1
□ Screen reader labels on all interactive elements
□ Keyboard navigation works
□ Loading states announced
□ Error states announced
```

## 12. Cross-Platform Checklist

```
□ Tested on Android
□ Tested on iOS (if applicable)
□ Tested on different screen sizes
□ Safe area handling
□ Platform-specific code in .ios.tsx/.android.tsx
□ No web-only APIs without platform check
```
