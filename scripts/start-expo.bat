@echo off
title Gardenify Expo Launcher
cd /d "F:\Local_git\gardenify"
echo Starting Expo dev server on port 8083...
start "Gardenify-Expo" npx expo start --port 8083
echo Expo starting in separate window.
echo PID: %ERRORLEVEL%
