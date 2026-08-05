# Cross-Session Handoff Protocol

This document ensures continuity between agent sessions and when handing off work.

## Handoff Template

When ending a session or passing work to another agent, include:

```markdown
## Current State

- **Last action**: [What was just done]
- **Files modified**: [List of changed files]
- **Tests status**: [Passing/Failing]
- **Known issues**: [Any problems encountered]

## Next Steps

1. [Immediate next task]
2. [Following task]
3. [Blocked items requiring human input]

## Context

- [Any important decisions made]
- [Workarounds applied]
- [References to relevant docs]

## Environment

- [Supabase project status]
- [Vercel deployment status]
- [Any pending credentials needed]
```

## Handoff Checklist

Before ending a session:

```
□ Current work is committed (if applicable)
□ .agents/lessons/<category>.md updated with any discoveries
□ No uncommitted secrets or temp files
□ Next steps clearly documented
□ Any TODO items are tracked
```

## Resuming Work

When starting a new session:

1. Read `LESSONS.md` index + `.agents/lessons/<category>.md` for context
2. Check `.agents/handoff-current.md` for latest state
3. Review recent git log (`git log --oneline -10`)
4. Run test suite to verify current state
5. Pick up from "Next Steps" in handoff doc

## File State Tracking

For each major component, track:

| Component       | Last Modified | Status  | Notes |
| --------------- | ------------- | ------- | ----- |
| Expo App        | —             | Pending | —     |
| FastAPI Backend | —             | Pending | —     |
| Supabase Schema | —             | Pending | —     |
| CI/CD           | —             | Pending | —     |
| Documentation   | —             | Pending | —     |
