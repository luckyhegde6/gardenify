# Self-Improvement Loop for Gardenify Agents

This document defines how agents continuously improve code quality, performance, and reliability.

## 1. Pre-Commit Self-Check

Before every commit, run this self-checklist:

```
□ Linting passes (npm run lint / ruff check)
□ Type checking passes (npx tsc --noEmit)
□ Tests pass (npm test / pytest)
□ No hardcoded secrets or API keys
□ RLS policies reviewed for new tables
□ Error handling covers edge cases
□ No unnecessary dependencies added
□ Comments explain WHY, not WHAT
□ Code matches existing patterns in codebase
```

## 2. Post-Merge Validation

After merging to main:

```
□ EAS build succeeds
□ Backend deploys to Vercel
□ Lighthouse score > 90
□ No console.error in production logs
□ Database migrations ran cleanly
```

## 3. Weekly Review

Every Friday, review:

- [ ] Bug reports and fix patterns
- [ ] Performance metrics (API latency, app startup time)
- [ ] Test coverage gaps
- [ ] Dependency updates available
- [ ] Security advisories

## 4. Learning Capture

When you learn something new:

1. Update `.agents/lessons/<category>.md` with the finding
2. Add a rule to `CLAUDE.md` if it's a general principle
3. Update `AGENTS.md` if it affects the architecture
4. Add a test case to prevent regression

## 5. Failure Analysis

When something breaks:

1. **Root cause**: What actually happened?
2. **Why wasn't it caught?**: What test/rule was missing?
3. **Fix**: Apply the code change
4. **Prevent**: Add test, rule, or check to prevent recurrence
5. **Document**: Update `.agents/lessons/<category>.md` with the pattern

## 6. Performance Benchmarks

Track these metrics over time:

| Metric                  | Target  | Current | Trend |
| ----------------------- | ------- | ------- | ----- |
| App startup time        | < 2s    | —       | —     |
| API response time       | < 500ms | —       | —     |
| Identification accuracy | > 90%   | —       | —     |
| Test coverage           | > 80%   | —       | —     |
| Bundle size             | < 50MB  | —       | —     |

## 7. Code Quality Metrics

Monitor:

- Lines of code per function (< 50 ideal)
- Cyclomatic complexity (< 10)
- Test coverage per module
- Dependency count
- Bundle size impact per feature
