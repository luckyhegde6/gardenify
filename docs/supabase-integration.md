# Supabase Integration Guide

> Connect Gardenify to Supabase for auth, database, and storage.

## Prerequisites

1. **Supabase Account**: https://supabase.com/signup
2. **Supabase CLI**: `npm i -g supabase`

## Step 1: Create Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Fill in:
   - Organization: Your org
   - Project name: `gardenify`
   - Database password: (save this!)
   - Region: Closest to your users
4. Click "Create new project"

## Step 2: Get Credentials

1. Go to **Settings** → **API**
2. Copy these values:

| Key | Location |
|---|---|
| Project URL | `https://xxx.supabase.co` |
| Anon Key | `eyJhbGciOiJIUzI1NiIs...` |
| Service Role Key | `eyJhbGciOiJIUzI1NiIs...` |

## Step 3: Run Migrations

```bash
# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push

# Seed database
supabase db seed
# Or: make seed-prod
```

## Step 4: Configure Environment Variables

### Backend (.env)

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Mobile (app.json or .env)

```json
{
  "expo": {
    "extra": {
      "supabaseUrl": "https://your-project.supabase.co",
      "supabaseAnonKey": "your-anon-key"
    }
  }
}
```

## Step 5: Verify Tables

1. Go to **Table Editor** in Supabase dashboard
2. Verify these tables exist:

| Table | Purpose |
|---|---|
| `users` | User profiles |
| `identifications` | Plant scan results |
| `favorites` | Saved species |
| `user_settings` | User preferences |

3. Verify RLS is enabled (lock icon on each table)

## Step 6: Configure Auth

### Email/Password Auth

1. Go to **Authentication** → **Providers**
2. Enable **Email** provider
3. Configure:
   - Confirm email: Off (for dev)
   - Double confirmation: Off

### Social Login (Optional)

1. Enable Google, GitHub, etc.
2. Add OAuth credentials
3. Configure redirect URLs

## Step 7: Configure Storage

1. Go to **Storage**
2. Create bucket: `plant-images`
3. Set bucket policy:

```sql
-- Allow authenticated users to upload
CREATE POLICY "Users can upload plant images"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'plant-images');

-- Allow owners to read their images
CREATE POLICY "Users can read own images"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'plant-images' AND auth.uid()::text = (storage.foldername(name))[1]);
```

## Step 8: Row Level Security (RLS)

Every table must have RLS enabled. Verify:

```sql
-- Check RLS status
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';

-- All should show rowsecurity = true
```

### RLS Policy Examples

```sql
-- Users can only see their own profile
CREATE POLICY "Users can view own profile"
ON public.users FOR SELECT
USING (auth.uid() = id);

-- Users can only insert their own identifications
CREATE POLICY "Users can create own identifications"
ON public.identifications FOR INSERT
WITH CHECK (auth.uid() = user_id);
```

## Step 9: Test Connection

### From Backend

```bash
# Test API endpoint
curl -X POST https://your-project.supabase.co/rest/v1/rpc/get_user_stats \
  -H "apikey: your-anon-key" \
  -H "Authorization: Bearer your-anon-key"

# Should return user stats or error
```

### From Mobile

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://your-project.supabase.co',
  'your-anon-key'
);

// Test connection
const { data, error } = await supabase
  .from('users')
  .select('*')
  .limit(1);

console.log({ data, error });
```

## Step 10: Monitoring

### Dashboard Metrics

1. Go to **Reports** in Supabase dashboard
2. Monitor:
   - Database size
   - API requests
   - Auth signups
   - Storage usage

### Logs

1. Go to **Logs** → **Postgres**
2. View SQL queries
3. Check for slow queries

## Common Tasks

### Add New Column

```bash
# Create migration
supabase migration new add_care_column

# Edit migration file
# supabase/migrations/xxxx_add_care_column.sql

# Apply
supabase db push
```

### Reset Database

```bash
# ⚠️ WARNING: This deletes all data
supabase db reset

# Or with seed
supabase db reset --seed
```

### Backup Database

```bash
# Export to SQL
pg_dump "postgresql://postgres:password@db.xxx.supabase.co:5432/postgres" > backup.sql

# Or use Supabase dashboard
# Settings → Database → Backups
```

## Security Checklist

```
□ RLS enabled on all tables
□ Service role key never exposed to client
□ API keys in environment variables
□ No hardcoded secrets in code
□ Storage buckets have proper policies
□ Auth providers configured correctly
□ Email confirmation enabled in production
□ Rate limiting enabled
```

## Troubleshooting

### "relation does not exist"

```bash
# Run migrations
supabase db push

# Verify tables exist
supabase db inspect tables
```

### "permission denied for table"

```bash
# Check RLS policies
SELECT * FROM pg_policies WHERE tablename = 'your_table';

# Test with service role key (bypasses RLS)
curl -H "Authorization: Bearer your-service-role-key" ...
```

### "new row violates row-level security policy"

```bash
# Check policy conditions
SELECT * FROM pg_policies WHERE tablename = 'identifications';

# Ensure auth.uid() matches user_id
SELECT auth.uid(), user_id FROM identifications;
```

## Cost Estimation

| Tier | Price | Includes |
|---|---|---|
| Free | $0 | 500MB DB, 1GB storage, 50K MAU |
| Pro | $25/month | 8GB DB, 100GB storage, unlimited MAU |
| Team | $599/month | 8GB DB, 100GB storage, priority support |

For Gardenify MVP (1000 users):
- **Free tier is sufficient**
- ~100MB database usage
- ~500MB storage usage
