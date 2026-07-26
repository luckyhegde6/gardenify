#!/bin/bash
# Gardenify local dev — starts backend + Supabase
set -e

echo "Starting Gardenify local dev environment..."

echo "[1/3] Starting Supabase..."
docker compose up -d

echo "[2/3] Installing Python deps..."
cd api && pip install -r requirements.txt -q && cd ..

echo "[3/3] Starting backend on http://localhost:8000"
cd api && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
