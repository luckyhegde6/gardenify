# Rules — Gardenify

## Must Always
- Use `npx expo install` for Expo packages — never `npm install`
- Enable RLS on every new Supabase table — no exceptions
- Use `auth.uid()` in RLS policies for user-scoped data
- Type hints on all Python functions — no exceptions
- Pydantic models for every API request and response
- Run `npm run lint` and `npx tsc --noEmit` before commits
- Run `cd api && pytest` for Python changes
- Validate user inputs at boundaries (Pydantic/Zod)
- Use environment variables — never hardcode secrets
- Follow existing file naming: components = kebab-case.tsx, Python = snake_case.py

## Must Never
- Commit secrets, API keys, or tokens to git
- Store tokens in AsyncStorage — use expo-secure-storage
- Expose `service_role` key to the client
- Skip RLS policies on new database tables
- Use `console.log` in production code — use structured logging
- Add dependencies without checking if an existing dep covers the need
- Use `expo-cli` directly — use `npx expo` commands
- Bypass security checks or validation hooks
- Submit untested changes
- Ship code without checking the relevant test suite

## Agent Format
- Agents are defined in `opencode.json` under the `agent` key.
- Each agent has `description`, `mode`, and optional `prompt` and `tools`.
- File names are lowercase with hyphens and must match the agent name.

## Skill Format
- Skills live in `.opencode/skills/<name>/SKILL.md`.
- Each skill includes YAML frontmatter with `name` and `description`.
- Skill bodies should include practical guidance and clear "When to Use" sections.

## Commit Style
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Keep changes modular and well-described
- Before committing: update sessions.md, handoff-current.md, MEMORY.md, LESSONS.md
