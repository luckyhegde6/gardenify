# Soul — Gardenify Identity

## Core Identity
Gardenify is a plant identification mobile app. Users photograph plants and receive species identification with confidence scores, common names, and taxonomy details. Built with Expo SDK 55, Python FastAPI, Supabase, and PlantNet API.

## Core Principles
1. **Mobile-First** — Android deployment, iOS later. Every decision optimizes for mobile UX.
2. **Security-First** — RLS on every table, no secrets in client code, validate all inputs.
3. **Test-Driven** — Write tests before implementation. Verify before committing.
4. **Simplicity** — Minimum code that solves the problem. No speculative abstractions.
5. **Surgical Changes** — Touch only what you must. Match existing patterns.

## Architecture Philosophy
Gardenify uses a thin-client architecture: the Expo app handles UI and auth directly with Supabase, while the Python backend proxies PlantNet API calls (keeping the API key server-side) and manages caching/metadata extraction. This keeps the mobile app fast and the backend stateless.

## Agent Orchestration
Agents are invoked proactively: planners for multi-file features, reviewers after code changes, security reviewers for auth/API/RLS, TDD guides for new features, and build resolvers when the toolchain breaks.

## Cross-Harness Compatibility
This project uses both OpenCode and Claude Code. Files in `.opencode/` configure OpenCode agents, plugins, skills, and tools. Files in `.claude/` configure Claude Code rules and guardrails. `AGENTS.md` and `CLAUDE.md` serve as shared context for both harnesses.
