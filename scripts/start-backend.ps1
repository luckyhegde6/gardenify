# Start Gardenify backend in a detached window
Start-Process -FilePath 'cmd' -ArgumentList '/c cd /d F:\Local_git\gardenify && python -m uvicorn api.main:app --reload --port 8000' -WindowStyle Normal
Write-Host "Backend starting on http://localhost:8000"
