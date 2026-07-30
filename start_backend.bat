@echo off
cd /d "%~dp0"
echo Starting Gardenify backend...
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
pause
