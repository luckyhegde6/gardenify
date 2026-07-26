#!/usr/bin/env bash
# seed.sh — Seed database with test data
# Usage: ./scripts/seed.sh [local|production]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SEED_FILE="$PROJECT_ROOT/supabase/seed.sql"
ENV_MODE="${1:-local}"

echo "=== Gardenify Seed Script ==="
echo "Mode: $ENV_MODE"

# Load environment
if [ "$ENV_MODE" = "local" ]; then
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        echo "ERROR: .env file not found. Run: cp .env.example .env"
        exit 1
    fi
    source "$PROJECT_ROOT/.env"
    DATABASE_URL="${SUPABASE_URL:-http://localhost:54321}"
    echo "Using local Supabase: $DATABASE_URL"
else
    echo "Using production Supabase"
    if [ -z "${SUPABASE_URL:-}" ]; then
        echo "ERROR: SUPABASE_URL not set for production"
        exit 1
    fi
    DATABASE_URL="$SUPABASE_URL"
fi

# Check if seed file exists
if [ ! -f "$SEED_FILE" ]; then
    echo "ERROR: Seed file not found: $SEED_FILE"
    exit 1
fi

echo ""
echo "Seed file: $SEED_FILE"
echo ""

# Run seed
if command -v supabase &> /dev/null; then
    echo "Running via Supabase CLI..."
    supabase db reset --linked 2>/dev/null || {
        echo "Fallback: running seed directly..."
        psql "$DATABASE_URL" -f "$SEED_FILE"
    }
elif command -v psql &> /dev/null; then
    echo "Running via psql..."
    psql "$DATABASE_URL" -f "$SEED_FILE"
else
    echo "ERROR: Neither 'supabase' nor 'psql' found in PATH"
    echo "Install: brew install supabase/tap/supabase"
    exit 1
fi

echo ""
echo "=== Seed Complete ==="
echo "Test user ID: 00000000-0000-0000-0000-000000000001"
echo "Created: 5 identifications, 3 favorites"
