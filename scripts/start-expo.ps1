# Start Gardenify Expo dev server in a detached window
Start-Process -FilePath 'cmd' -ArgumentList '/c cd /d F:\Local_git\gardenify && npx expo start --port 8083' -WindowStyle Normal
Write-Host "Expo dev server starting on http://localhost:8083"
