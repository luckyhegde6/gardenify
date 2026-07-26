#!/usr/bin/env bash
# start.sh — Start Gardenify local dev (Supabase + backend)
# Usage: ./scripts/start.sh [backend|all]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
info() { echo -e "${CYAN}[START]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC}   $*"; }

# Load .env if present
load_env() {
    local env_file="$ROOT_DIR/.env"
    if [ -f "$env_file" ]; then
        set -a
        # shellcheck disable=SC1090
        source "$env_file"
        set +a
        ok "Loaded .env"
    else
        echo "No .env found — run: ./scripts/setup.sh local"
        exit 1
    fi
}

start_supabase() {
    info "Starting Supabase..."
    cd "$ROOT_DIR"
    docker compose up -d
    ok "Supabase running"
    echo ""
    info "Services:"
    info "  Studio:    http://localhost:54323"
    info "  API:       http://localhost:54321"
    info "  DB:        postgresql://postgres:postgres@localhost:54322/postgres"
    info "  Auth:      http://localhost:9999"
    info "  REST:      http://localhost:3000"
    info "  Storage:   http://localhost:5000"
}

start_backend() {
    info "Starting FastAPI backend..."
    cd "$ROOT_DIR/api"
    pip install -r requirements.txt -q 2>/dev/null
    ok "Backend starting on http://localhost:8000"
    info "Swagger: http://localhost:8000/docs (DEBUG=true)"
    info "Debug:   http://localhost:8000/api/debug"
    exec uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
}

MODE="${1:-all}"
load_env

case "$MODE" in
    supabase|db)
        start_supabase
        ;;
    backend|api)
        start_backend
        ;;
    all|"")
        start_supabase
        echo ""
        start_backend
        ;;
    *)
        echo "Usage: $0 [all|supabase|backend]"
        exit 1
        ;;
esac
