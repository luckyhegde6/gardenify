# Gardenify — OpenCode Instructions

Consolidated rules and guidelines for OpenCode agents working on Gardenify.

---

## Security Guidelines (CRITICAL)

### Mandatory Security Checks

Before ANY commit:

- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] All user inputs validated (Pydantic on backend, Zod on mobile)
- [ ] SQL injection prevention (parameterized queries only)
- [ ] RLS enabled on every new Supabase table
- [ ] `service_role` key never exposed to client
- [ ] PlantNet API key stays server-side only
- [ ] Error messages don't leak sensitive data

### Secret Management

```python
# NEVER: Hardcoded secrets
API_KEY = "sk-proj-xxxxx"

# ALWAYS: Environment variables
import os
API_KEY = os.environ.get("PLANTNET_API_KEY")
if not API_KEY:
    raise ValueError("PLANTNET_API_KEY not configured")
```

### Security Response Protocol

If security issue found:

1. STOP immediately
2. Use **security-reviewer** agent
3. Fix CRITICAL issues before continuing
4. Rotate any exposed secrets
5. Review entire codebase for similar issues

---

## Coding Style

### TypeScript Rules

- Strict mode enabled — no `any` types
- Explicit return types on exported functions
- Use `const` by default, `let` when reassignment is needed, never `var`
- Prefer `interface` over `type` for object shapes
- Use optional chaining `?.` and nullish coalescing `??`

### Python Rules

- Type hints on ALL functions — no exceptions
- Pydantic models for every request and response
- Use `logging` module — never `print()`
- No bare `except` — always specify exception type
- f-strings for string formatting

### React Native Rules

- Functional components only — no class components
- Hooks for state management
- Use `expo-secure-store` — never `AsyncStorage` for sensitive data
- Platform-specific files: `.ios.tsx`, `.android.tsx`, `.web.tsx`

### Immutability Pattern

```typescript
// WRONG: Mutation
function updateUser(user, name) {
  user.name = name; // MUTATION!
  return user;
}

// CORRECT: Immutability
function updateUser(user, name) {
  return { ...user, name };
}
```

### File Organization

- Many small files > few large files
- 200-400 lines typical, 800 max
- Organize by feature/domain, not by type
- Components = kebab-case.tsx, Python = snake_case.py

---

## Testing Requirements

### Minimum Test Coverage: 80%

### Test-Driven Development (MANDATORY)

1. Write test first (RED)
2. Run test — it should FAIL
3. Write minimal implementation (GREEN)
4. Run test — it should PASS
5. Refactor (IMPROVE)
6. Verify coverage (80%+)

### Test Commands

```bash
# TypeScript lint
npm run lint

# TypeScript type check
npx tsc --noEmit

# Python tests
cd api && pytest

# Python lint
cd api && python -m ruff check .
```

### Test Types Required

1. **Unit Tests** — Individual functions, utilities, components
2. **Integration Tests** — API endpoints, database operations
3. **E2E Tests** — Critical user flows (Playwright)

---

## Git Workflow

### Commit Message Format

```
<type>: <description>

<optional body>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`

### Pre-Commit Checklist

Before EVERY commit:

```
□ .agents/session-todos.md maintained — start of session, checked before commit;
  unfulfilled todos carried forward; confirmed-bug todos logged in BUGS.md
□ npm run lint passes
□ npx tsc --noEmit passes
□ cd api && pytest passes
□ No console.log in production code
□ No hardcoded secrets
□ RLS enabled on new tables
□ .agents/sessions.md updated
□ .agents/handoff-current.md updated
□ MEMORY.md index + .agents/memory/current-state.md updated
□ LESSONS.md index + .agents/lessons/<category>.md updated (if new discovery)
□ BUGS.md updated (if bug found/fixed)
```

---

## Agent Orchestration

### Available Agents

| Agent                | Purpose                 | When to Use                    |
| -------------------- | ----------------------- | ------------------------------ |
| planner              | Implementation planning | Complex features, refactoring  |
| code-reviewer        | Code review             | After writing code             |
| security-reviewer    | Security analysis       | Auth, API, RLS, sensitive data |
| tdd-guide            | Test-driven development | New features, bug fixes        |
| build-error-resolver | Fix build errors        | When build fails               |
| database-reviewer    | Database optimization   | SQL, schema, RLS               |
| doc-updater          | Documentation           | Updating docs                  |
| refactor-cleaner     | Dead code cleanup       | Code maintenance               |

### Immediate Agent Usage (No user prompt needed)

1. Complex feature requests → Use **planner** agent
2. Code just written/modified → Use **code-reviewer** agent
3. Bug fix or new feature → Use **tdd-guide** agent
4. Auth/API/RLS changes → Use **security-reviewer** agent
5. Schema/migration changes → Use **database-reviewer** agent

---

## Expo-Specific Rules

- Always use `npx expo install` for Expo packages — never `npm install`
- Use typed routes (enabled in app.json `experiments.typedRoutes`)
- Platform-specific files: `.ios.tsx`, `.android.tsx`, `.web.tsx`
- Don't use `expo-cli` directly — use `npx expo` commands
- Test on physical device before marking camera/image features complete
- Use environment variables with `EXPO_PUBLIC_` prefix for client-side

---

## Python Backend Rules

- Type hints on ALL functions — no exceptions
- Pydantic models for every request and response
- Use `logging` module — never `print()`
- Write tests for every API route
- Validate input at the boundary (FastAPI dependency injection)
- No bare `except` — always specify exception type

---

## Supabase Rules

- Enable RLS on every new table — no exceptions
- Never expose `service_role` key to the client
- Use `auth.uid()` in RLS policies for user-scoped data
- Create database indexes for frequently queried columns
- Use Supabase migrations for schema changes — never manual SQL in production

---

## Performance Tips

### Context Window Management

- Avoid last 20% of context window for large refactoring
- Use subagents for complex multi-file tasks
- Keep instructions concise — load skills on-demand

### Model Selection

- Use primary model for most coding tasks
- Use subagents for specialized review and planning
- Delegate to domain experts (database-reviewer, security-reviewer) early

---

## Success Metrics

You are successful when:

- All tests pass (80%+ coverage)
- No security vulnerabilities
- Code is readable and maintainable
- Performance is acceptable
- User requirements are met
- CI/CD pipeline passes

---

## Non-Blocking Service Management

### Problem

Long-running commands like `uvicorn`, `npx expo start`, or `adb logcat` block the bash tool. They must be launched as detached processes so the agent can continue working.

### Critical Constraint

**The bash tool blocks until the command exits.** Any approach that doesn't cause the _parent cmd.exe_ to exit quickly will block the agent. This rules out:

- `npx expo start` — never exits ❌
- `python -c "subprocess.Popen(...)"` — parent python.exe blocks waiting for Popen'd children on Windows ❌
- `start /B cmd /c "..."` — same process group, tool waits ❌
- Subagent `task` wrapping any of the above — subagent's own bash tool blocks ❌

### Working Patterns (Windows)

```bash
# ✅ start "Title" cmd /c "..." — opens new window, returns immediately
start "Gardenify-Backend" cmd /c "cd /d F:\Local_git\gardenify && python -m uvicorn api.main:app --reload --port 8000"

# ✅ powershell Start-Process — truly detached, returns immediately
powershell -Command "Start-Process -FilePath 'cmd' -ArgumentList '/c cd /d F:\Local_git\gardenify && python -m uvicorn api.main:app --reload --port 8000' -WindowStyle Normal"
```

### Non-Working Patterns (Windows)

```bash
# ❌ Blocks — /B keeps process in same console group
start /B python -m uvicorn api.main:app --reload --port 8000

# ❌ Blocks — Python parent waits for child
python -c "import subprocess; subprocess.Popen(['uvicorn', 'api.main:app'], creationflags=subprocess.DETACHED_PROCESS)"

# ❌ Blocks — subagent's bash tool inherits same issue
# (task with debug subagent → bash → blocked)
```

### Service State Tracking

The `superpower-hooks.ts` plugin tracks running services across session compactions. Use the `debug` agent to manage service lifecycle.

### Important Caveats

- Detached processes inherit current working directory — always use `cd /d` in `cmd /c`
- No stdout/stderr captured from detached processes — redirect to file if logs needed
- Use `taskkill /f /im uvicorn.exe` or `taskkill /F /PID <pid>` to stop services
- Verify with `curl http://localhost:8000/api/health` before using
