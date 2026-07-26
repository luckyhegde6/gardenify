.PHONY: install dev lint typecheck test backend clean

# Install all dependencies
install:
	npm install
	cd api && pip install -r requirements.txt

# Start Expo dev server
dev:
	npx expo start

# Start with Android
dev-android:
	npx expo start --android

# Start Python backend
backend:
	cd api && vercel dev

# Lint TypeScript
lint:
	npm run lint

# Type check TypeScript
typecheck:
	npx tsc --noEmit

# Run Python tests
test-python:
	cd api && pytest

# Lint Python
lint-python:
	cd api && ruff check .
	cd api && ruff format --check .

# Build Android APK
build-android:
	npx eas-cli build -p android --profile preview

# Build Android production
build-android-prod:
	npx eas-cli build -p android --profile production

# Deploy backend to Vercel
deploy-backend:
	cd api && vercel deploy --prod

# Run Supabase migrations
migrate:
	supabase db push

# Clean generated files
clean:
	rm -rf node_modules
	rm -rf .expo
	rm -rf api/__pycache__
	rm -rf api/.pytest_cache

# Help
help:
	@echo "Gardenify Development Commands:"
	@echo ""
	@echo "  make install       - Install all dependencies"
	@echo "  make dev           - Start Expo dev server"
	@echo "  make dev-android   - Start with Android"
	@echo "  make backend       - Start Python backend"
	@echo "  make lint          - Lint TypeScript"
	@echo "  make typecheck     - Type check TypeScript"
	@echo "  make test-python   - Run Python tests"
	@echo "  make lint-python   - Lint Python"
	@echo "  make build-android - Build Android APK"
	@echo "  make deploy-backend - Deploy backend to Vercel"
	@echo "  make migrate       - Run Supabase migrations"
	@echo "  make clean         - Clean generated files"
