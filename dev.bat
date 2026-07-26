@echo off
REM Gardenify local dev — starts backend + Supabase
echo Starting Gardenify local dev environment...

REM Start Supabase (Docker)
echo [1/3] Starting Supabase...
docker compose up -d

REM Install Python deps
echo [2/3] Installing Python deps...
cd api && pip install -r requirements.txt -q && cd ..

REM Start backend
echo [3/3] Starting backend on http://localhost:8000
cd api && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
