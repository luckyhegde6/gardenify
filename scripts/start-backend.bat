@echo off
title Gardenify Backend Launcher
cd /d "F:\Local_git\gardenify\api"
echo Starting FastAPI backend on port 8000...
start "Gardenify-Backend" python -m uvicorn api.main:app --reload --port 8000
echo Backend starting in separate window.
echo PID: %ERRORLEVEL%
