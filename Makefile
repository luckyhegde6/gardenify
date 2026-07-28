.PHONY: install dev backend lint typecheck test-python lint-python migrate deploy-backend deploy-mobile help setup setup-local setup-cloud setup-validate seed seed-local seed-prod

# ── Setup ─────────────────────────────────────────────────────
setup:
	@./scripts/setup.sh all

setup-local:
	@./scripts/setup.sh local

setup-cloud:
	@./scripts/setup.sh cloud

setup-plantnet:
	@./scripts/setup.sh plantnet

setup-validate:
	@./scripts/setup.sh validate

setup-show:
	@./scripts/setup.sh show

# ── Install ───────────────────────────────────────────────────
install:
	npm install
	cd api && pip install -r requirements.txt

# ── Start ─────────────────────────────────────────────────────
dev:
	@./scripts/start.sh all

dev-backend:
	@./scripts/start.sh backend

dev-supabase:
	@./scripts/start.sh supabase

# ── Lint & Test ───────────────────────────────────────────────
lint:
	npm run lint

typecheck:
	npx tsc --noEmit

test-python:
	cd api && python -m pytest tests/ -v

lint-python:
	cd api && ruff check .
	cd api && ruff format --check .

# ── Build ─────────────────────────────────────────────────────
build-android:
	npx eas-cli build -p android --profile preview

build-android-prod:
	npx eas-cli build -p android --profile production

# ── Deploy ────────────────────────────────────────────────────
deploy-backend:
	@./scripts/deploy.sh backend

deploy-mobile:
	@./scripts/deploy.sh mobile

deploy-migrate:
	@./scripts/deploy.sh migrate

deploy-all:
	@./scripts/deploy.sh all

# ── Database ──────────────────────────────────────────────────
migrate:
	supabase db push

seed:
	@./scripts/seed.sh local

seed-local:
	@./scripts/seed.sh local

seed-prod:
	@./scripts/seed.sh production

# ── Pre-commit ────────────────────────────────────────────────
precommit-install:
	pip install pre-commit
	pre-commit install

precommit-run:
	pre-commit run --all-files

# ── Clean ─────────────────────────────────────────────────────
clean:
	rm -rf node_modules .expo api/__pycache__ api/.pytest_cache .pytest_cache
	rm -rf api/.ruff_cache

# ── Help ──────────────────────────────────────────────────────
help:
	@echo "Gardenify Commands:"
	@echo ""
	@echo "  Setup:"
	@echo "    make setup              — Full local setup (Supabase + PlantNet)"
	@echo "    make setup-local        — Local Supabase only"
	@echo "    make setup-cloud        — Supabase Cloud"
	@echo "    make setup-plantnet     — PlantNet API key"
	@echo "    make setup-validate     — Validate .env"
	@echo "    make setup-show         — Show .env (redacted)"
	@echo ""
	@echo "  Dev:"
	@echo "    make dev                — Start everything (Supabase + backend)"
	@echo "    make dev-backend        — Backend only"
	@echo "    make dev-supabase       — Supabase only"
	@echo ""
	@echo "  Lint & Test:"
	@echo "    make lint               — Lint TypeScript"
	@echo "    make typecheck          — Type check TypeScript"
	@echo "    make test-python        — Run Python tests"
	@echo "    make lint-python        — Lint Python"
	@echo ""
	@echo "  Build & Deploy:"
	@echo "    make build-android      — EAS preview build"
	@echo "    make deploy-backend     — Vercel production"
	@echo "    make deploy-migrate     — Supabase migrations"
	@echo "    make deploy-all         — Everything"
	@echo ""
	@echo "  Database:"
	@echo "    make migrate            — Run Supabase migrations"
	@echo "    make seed               — Seed local database"
	@echo "    make seed-prod          — Seed production database"
	@echo ""
	@echo "  Other:"
	@echo "    make precommit-install  — Install pre-commit hooks"
	@echo "    make precommit-run      — Run pre-commit on all files"
	@echo "    make clean              — Remove generated files"
