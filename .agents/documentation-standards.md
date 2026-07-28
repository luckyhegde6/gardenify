# Documentation Standards

> Clean, maintainable, and useful documentation.

## 1. Documentation Types

### User-Facing
- **README.md**: Project overview, quick start
- **CHANGELOG.md**: Version history
- **CONTRIBUTING.md**: How to contribute

### Developer-Facing
- **AGENTS.md**: Agent instructions
- **MEMORY.md**: Quick context for agents
- **LESSONS.md**: Mistakes and solutions
- **.agents/**: Architecture, phase TODOs, guidelines

### API Documentation
- **OpenAPI/Swagger**: Auto-generated from code
- **API Examples**: Request/response samples

## 2. Documentation Rules

### README.md Structure
```markdown
# Project Name

One-line description.

## Quick Start

```bash
# 3-5 commands to get started
```

## Features

- Feature 1
- Feature 2

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| API_KEY | Your API key | Yes |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/identify | Identify plant |

## Contributing

See CONTRIBUTING.md
```

### Code Comments
```typescript
// ✅ GOOD: Explain WHY
// We use SHA-256 because PlantNet deduplicates by hash
const hash = computeHash(image);

// ✅ GOOD: Explain non-obvious behavior
// PlantNet returns 429 when quota exceeded, not 403
if (response.status === 429) {
  throw new QuotaExceededError();
}

// ✅ GOOD: TODO format
// TODO(username): Add caching for this endpoint
const result = await identifyPlant(image);

// ❌ BAD: Explain WHAT (redundant)
// Compute hash
const hash = computeHash(image);

// ❌ BAD: Obvious comments
// Return the result
return result;
```

### API Documentation
Every endpoint must have:
- Summary (1 line)
- Description (1-2 sentences)
- Request schema with examples
- Response schema with examples
- Error cases documented

## 3. Documentation Updates

### When to Update
```
□ After adding a feature → Update README.md
□ After changing API → Update OpenAPI spec
□ After fixing a bug → Update LESSONS.md
□ After making a decision → Update AGENTS.md
□ After discovering something → Update LESSONS.md
□ Before commit → Update MEMORY.md
```

### Who Updates
- **README.md**: Developer who adds feature
- **CHANGELOG.md**: Automated or release manager
- **AGENTS.md**: Architecture owner
- **MEMORY.md**: Any agent
- **LESSONS.md**: Any agent who learns something

## 4. Documentation Quality

### Clear
- Simple language
- Short sentences
- Concrete examples

### Concise
- No unnecessary words
- Bullet points over paragraphs
- Tables over lists when appropriate

### Complete
- All features documented
- All API endpoints documented
- All environment variables documented

### Current
- Updated with code changes
- No stale information
- Version numbers match

## 5. Documentation Tools

### Auto-Generation
```bash
# OpenAPI spec from FastAPI
uvicorn api.main:app --openapi=openapi.json

# TypeDoc for TypeScript
npx typedoc src/**/*.ts

# Sphinx for Python
cd docs && make html
```

### Linting
```bash
# Markdown lint
npx markdownlint-cli2 "**/*.md"

# Spell check
npx cspell "src/**/*.{ts,tsx}" "*.md"
```

## 6. Documentation Checklist

```
□ README.md has quick start
□ README.md has environment variables
□ README.md has API endpoints
□ All API endpoints documented
□ All features documented
□ All env vars documented
□ No stale information
□ Examples are working
□ Links are valid
□ No typos
```

## 7. Common Documentation Mistakes

| Mistake | Solution |
|---|---|
| Outdated README | Update after every feature |
| Missing env vars | Document all required vars |
| No examples | Add request/response examples |
| Too verbose | Use bullet points, tables |
| No changelog | Generate on every release |
| Stale comments | Review comments quarterly |
