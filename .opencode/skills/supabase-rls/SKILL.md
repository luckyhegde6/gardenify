---
name: supabase-rls
description: Supabase Row Level Security patterns for Gardenify. Covers RLS policies, migrations, and auth integration.
---

## What I do
Guide Supabase RLS setup, database migrations, and auth integration following security best practices.

## When to use me
Use this when creating new database tables, modifying RLS policies, or working with Supabase auth.

## Key Patterns

### Table with RLS
```sql
CREATE TABLE public.identifications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  species_name TEXT NOT NULL,
  scientific_name TEXT,
  confidence DECIMAL(5,4),
  image_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Enable RLS
ALTER TABLE public.identifications ENABLE ROW LEVEL SECURITY;

-- Users can only see their own identifications
CREATE POLICY "Users can view own identifications"
ON public.identifications FOR SELECT
USING (auth.uid() = user_id);

-- Users can insert their own identifications
CREATE POLICY "Users can create own identifications"
ON public.identifications FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Users can delete their own identifications
CREATE POLICY "Users can delete own identifications"
ON public.identifications FOR DELETE
USING (auth.uid() = user_id);
```

### Migration File
```
supabase/migrations/
  001_initial_schema.sql   # Users, identifications, favorites, settings
  002_add_care_profiles.sql # Plant care data
```

### Auth Integration (Mobile)
```typescript
import { createClient } from '@supabase/supabase-js'
import * as SecureStore from 'expo-secure-store'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    storage: {
      getItem: (key) => SecureStore.getItemAsync(key),
      setItem: (key, value) => SecureStore.setItemAsync(key, value),
      removeItem: (key) => SecureStore.deleteItemAsync(key),
    },
  },
})
```

## Rules
- Enable RLS on every new table — no exceptions
- Use `auth.uid()` in RLS policies for user-scoped data
- Never expose `service_role` key to the client
- Use Supabase migrations for schema changes — never manual SQL in production
- Create database indexes for frequently queried columns
- Always test RLS policies with different user contexts
