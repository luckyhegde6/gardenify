#!/usr/bin/env bash
# deploy.sh — Deploy Gardenify to production
# Usage: ./scripts/deploy.sh [backend|mobile|all]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
info() { echo -e "${CYAN}[DEPLOY]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC}    $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }

# Load .env
if [ -f "$ROOT_DIR/.env" ]; then
    set -a; source "$ROOT_DIR/.env"; set +a
fi

deploy_backend() {
    info "Deploying Python backend to Vercel..."
    cd "$ROOT_DIR"

    if ! command -v vercel &>/dev/null; then
        warn "Installing Vercel CLI..."
        npm i -g vercel
    fi

    if [ -z "${VERCEL_TOKEN:-}" ]; then
        vercel deploy --prod
    else
        vercel deploy --prod --token "$VERCEL_TOKEN"
    fi
    ok "Backend deployed"
}

deploy_mobile() {
    info "Building Android APK..."
    cd "$ROOT_DIR"

    if ! npx eas-cli whoami &>/dev/null; then
        warn "Not logged in to EAS. Run: npx eas-cli login"
        return 1
    fi

    npx eas-cli build -p android --profile production --non-interactive
    ok "Build submitted"
}

deploy_migrate() {
    info "Pushing Supabase migrations..."
    cd "$ROOT_DIR"

    if ! command -v supabase &>/dev/null; then
        warn "Installing Supabase CLI..."
        npm i -g supabase
    fi

    supabase link --project-ref "${SUPABASE_PROJECT_REF:-}"
    supabase db push
    ok "Migrations applied"
}

MODE="${1:-all}"
case "$MODE" in
    backend)  deploy_backend ;;
    mobile)   deploy_mobile ;;
    migrate)  deploy_migrate ;;
    all|"")
        deploy_migrate
        deploy_backend
        deploy_mobile
        ;;
    -h|--help)
        echo "Usage: $0 [all|backend|mobile|migrate]"
        ;;
esac
