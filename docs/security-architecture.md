# Security Architecture

> Why Gardenify talks to Supabase directly from the app, where the real security
> boundary lives, and the plan to harden it.

## The Problem We're Solving

The app authenticates users **directly against Supabase** (via `@supabase/supabase-js` +
the public anon key), not through a backend-proxied auth endpoint. This is a deliberate
decision, but it's easy to mistake for a risk. This document explains:

1. What the actual security boundary is (RLS, not the client).
2. Why direct auth is the recommended pattern for Expo + Supabase.
3. What we must never ship to the client (`service_role`).
4. The staged hardening plan (device fingerprint, audit logs, optional auth proxy).

## Trust Boundary (One Diagram)

```
┌─────────────────────── PUBLIC / UNTRUSTED ───────────────────────┐
│                                                                  │
│   ┌──────────────┐   anon key + JWT    ┌────────────────────┐   │
│   │  Expo App    │────────────────────▶│  Supabase Auth     │   │
│   │  (Android)   │   direct            │  (email/password)  │   │
│   │              │◀────────────────────│                    │   │
│   │  supabase-js │   user JWT          └─────────┬──────────┘   │
│   └──────┬───────┘                              │              │
│          │                                       ▼              │
│          │  unauthenticated upload               ┌───────────┐  │
│          └──────────────────────────────────────▶│ FastAPI   │  │
│             images + organs                      │ (Vercel)  │  │
│                                                  └─────┬─────┘  │
│                                                        │        │
│                            service_role (server-only)  ▼        │
│                                                 ┌───────────┐   │
│                                                 │  Supabase │   │
│                                                 │ PostgreSQL│   │
│                                                 │  + RLS    │   │
│                                                 └───────────┘   │
└──────────────────────────────────────────────────────────────────┘

  Legend
  ──────  anon / user-context paths (safe to expose)
  ──────  service_role path (NEVER in the client bundle)
```

### What this diagram says

- **Auth** happens app → Supabase directly. The app holds only the **anon key**, which
  is a public identifier that can be read from any shipped APK.
- **Queries the app makes** (history, favorites, profile) go through RLS: every policy is
  scoped with `auth.uid() = user_id`, so a caller can only ever read/write their own rows —
  even if they hold a valid anon key and JWT.
- **The backend** (FastAPI on Vercel) does two independent jobs:
  - `/api/identify` — accepts uploads and calls PlantNet (PlantNet key lives **only** here).
  - Admin/history routes — talk to Supabase with either the user's JWT (verified via
    `auth.get_user`) or the **service_role** key, which lives **only** in the backend env.

## The Core Principle

> **The anon key is not a secret. RLS is the security boundary.**

Anyone can extract the anon key from the APK. That is expected and safe: the anon key is
just the Supabase project identifier, and every request is still subject to:

1. **RLS policies** — `auth.uid()`-scoped reads/writes per table.
2. **Auth** — a real user JWT is required to do anything as a user.
3. **Backend-held secrets** — PlantNet key and `service_role` key never reach the client.

The moment we treated the anon key as a secret (e.g. proxying auth through the backend to
"hide" it), we would gain zero security and add latency + a single point of failure.

## What We Keep Server-Side Only

| Secret                          | Exposed to app? | Why                                      |
| ------------------------------- | --------------- | ---------------------------------------- |
| `EXPO_PUBLIC_SUPABASE_ANON_KEY` | ✅ Yes (public) | Required for direct auth; safe under RLS |
| `EXPO_PUBLIC_SUPABASE_URL`      | ✅ Yes (public) | Public project URL                       |
| `SUPABASE_SERVICE_ROLE_KEY`     | ❌ No           | Bypasses RLS entirely; admin powers      |
| `PLANTNET_API_KEY`              | ❌ No           | Paid quota; would be abused if leaked    |
| `JWT_SECRET` / signing keys     | ❌ No           | Forges user sessions                     |

## Decisions & Rationale

| Decision                                                 | Why we did it                                                                                                       | Risk if we didn't                                                             |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Direct Supabase auth** instead of backend-proxied auth | Supabase's documented, first-party pattern for Expo; zero custom auth code; RLS already enforces per-user isolation | Custom auth proxy = more attack surface, more latency, no security gain       |
| **Backend owns PlantNet calls**                          | PlantNet API key must never ship in the APK; backend rate-limits and caches per our quota                           | Quota abuse, API key theft                                                    |
| **`service_role` confined to backend env**               | It bypasses RLS — shipping it in the client would let anyone read/delete all data                                   | Total data compromise                                                         |
| **Identify endpoint is unauthenticated**                 | Plant identification is a public feature; uploads are validated (type/size/count) at the boundary                   | (none security-wise for the identify call itself)                             |
| **History route validates the JWT server-side**          | Proves the caller is a real user before serving their history                                                       | Anyone with the anon key could query arbitrary rows if RLS were misconfigured |

## Hardening Plan (Staged)

These are future improvements, not blockers — the current setup is already safe.

### Stage 1 — Device fingerprint (recommended next)

Record which device a session came from, so a stolen session is detectable/revocable.

- Add `expo-device` and generate a persistent random device ID, stored in `expo-secure-storage`.
- Create a `user_devices` table (RLS: `auth.uid() = user_id`):

```sql
create table public.user_devices (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  device_fingerprint text not null,
  device_name text,
  last_seen_at timestamptz default now(),
  created_at timestamptz default now(),
  unique (user_id, device_fingerprint)
);

alter table public.user_devices enable row level security;

create policy "users manage own devices"
  on public.user_devices for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);
```

- On login, `upsert` the fingerprint; on app start, `touch last_seen_at`.

### Stage 2 — Backend-owned audit log

- A server-side `auth_audit` table (written with `service_role` only) recording every
  login/identify event: `user_id`, `device_fingerprint`, `ip`, `timestamp`.
- Add an authenticated `/api/audit` or extend `/api/history` to expose recent device
  activity so the user can see "This session came from Device X at 14:03".

### Stage 3 — Auth proxy only if needed

Move `signInWithPassword` behind the backend **only if** we need:

- Rate limiting / brute-force protection (Supabase has built-in rate limits today).
- Multi-device session revocation with custom rules.
- Funneling all auth events into one audit source.

Until then, keep direct auth — it's the simpler, first-party-recommended path.

## Enforced Rules (Codebase)

- `EXPO_PUBLIC_` prefixed env vars are the **only** client-visible config.
- `api/` env vars (`SUPABASE_SERVICE_ROLE_KEY`, `PLANTNET_API_KEY`) are never imported from
  `src/`.
- Every Supabase table has RLS enabled and `auth.uid()`-scoped policies (see
  `supabase/migrations/`).
- File uploads validated at the FastAPI boundary: JPEG/PNG/WebP, ≤10MB each, ≤5 files.
- No PII or secrets in logs; generic error messages returned to callers.

## Related Docs

- `docs/supabase-integration.md` — setup, migrations, and RLS examples
- `.agents/security-checklist.md` — pre-commit security gate
- `.agents/architecture.md` — overall system diagram
