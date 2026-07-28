# Vercel Deployment Guide

> Deploy Gardenify backend to Vercel in 5 minutes.

## Prerequisites

1. **Vercel Account**: https://vercel.com/signup
2. **Vercel CLI**: `npm i -g vercel`
3. **GitHub Repo**: https://github.com/luckyhegde6/gardenify

## Step 1: Login to Vercel

```bash
vercel login
# Opens browser for authentication
```

## Step 2: Link Project

```bash
# From project root
vercel link

# Follow prompts:
# - Set up "luckyhegde6/gardenify"? Yes
# - Which scope? Select your account
# - Link to existing project? No (create new)
# - Project name: gardenify-api
```

## Step 3: Configure Environment Variables

```bash
# Add environment variables
vercel env add PLANTNET_API_KEY production
# Paste your PlantNet API key

vercel env add SUPABASE_URL production
# Paste: https://your-project.supabase.co

vercel env add SUPABASE_SERVICE_KEY production
# Paste your Supabase service role key

vercel env add DEBUG production
# Set to: false

# For preview deployments (branch-specific)
vercel env add PLANTNET_API_KEY preview
vercel env add SUPABASE_URL preview
vercel env add SUPABASE_SERVICE_KEY preview
vercel env add DEBUG preview
```

## Step 4: Deploy

```bash
# Deploy to preview (branch)
vercel

# Deploy to production
vercel --prod

# Or use the deploy script
./scripts/deploy.sh backend
```

## Step 5: Configure Custom Domain (Optional)

```bash
# Add domain
vercel domains add api.gardenify.app

# Or use Vercel dashboard:
# 1. Go to project settings
# 2. Domains tab
# 3. Add: api.gardenify.app
```

## Step 6: Verify Deployment

```bash
# Check deployment status
vercel ls

# Test endpoints
curl https://gardenify-api.vercel.app/api/health
curl https://gardenify-api.vercel.app/api/debug

# View logs
vercel logs
```

## Vercel Configuration

### vercel.json (Auto-generated)

The project uses Vercel's auto-detection. For custom config:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/main.py"
    }
  ]
}
```

### Project Structure

```
gardenify/
├── api/
│   ├── main.py          # Vercel entrypoint
│   ├── config.py        # Settings
│   ├── routes/          # API routes
│   ├── services/        # Business logic
│   ├── models/          # Pydantic schemas
│   └── requirements.txt # Python deps
├── vercel.json          # Vercel config (auto)
└── package.json         # For Vercel CLI
```

## Environment Variables Reference

| Variable | Production | Preview | Local |
|---|---|---|---|
| `PLANTNET_API_KEY` | Real key | Real key | Real key |
| `SUPABASE_URL` | `https://xxx.supabase.co` | Same | `http://localhost:54321` |
| `SUPABASE_SERVICE_KEY` | Real key | Same | Local key |
| `DEBUG` | `false` | `true` | `true` |
| `ENVIRONMENT` | `production` | `production` | `local` |

## Troubleshooting

### Build Fails
```bash
# Check Python version
cat api/requirements.txt | head -5

# Verify dependencies
cd api && pip install -r requirements.txt

# Test locally
vercel dev
```

### Cold Start Issues
```bash
# Vercel serverless has cold starts (~1-2s)
# Solutions:
# 1. Use Vercel Edge Functions for faster cold starts
# 2. Add keep-warm pings
# 3. Optimize imports (lazy loading)
```

### Environment Variables Not Working
```bash
# Verify vars are set
vercel env ls

# Pull vars to local
vercel env pull .env.local

# Check var is accessible
vercel exec -- node -e "console.log(process.env.PLANTNET_API_KEY)"
```

## GitHub Actions Integration

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Vercel CLI
        run: npm install -g vercel
      
      - name: Pull Vercel Environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
      
      - name: Build
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
      
      - name: Deploy
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## Cost Estimation

| Tier | Price | Includes |
|---|---|---|
| Hobby | Free | 100GB bandwidth, 100K serverless executions |
| Pro | $20/user/month | 1TB bandwidth, unlimited executions |
| Enterprise | Custom | SLA, support, custom limits |

For Gardenify MVP (500 identifications/day):
- **Hobby tier is sufficient**
- ~15K executions/month
- ~500MB bandwidth/month
