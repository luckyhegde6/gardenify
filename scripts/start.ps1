#Requires -Version 5.1
<#
.SYNOPSIS
    Start Gardenify local dev (Supabase + backend)
.EXAMPLE
    .\scripts\start.ps1              # Start all
    .\scripts\start.ps1 supabase     # Supabase only
    .\scripts\start.ps1 backend      # Backend only
#>
param(
    [ValidateSet("all","supabase","backend")]
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path $PSScriptRoot -Parent
$EnvFile = Join-Path $RootDir ".env"

function Write-Info { Write-Host "[START] $args" -ForegroundColor Cyan }
function Write-Ok   { Write-Host "[OK]   $args" -ForegroundColor Green }

# Load .env
function Import-EnvFile {
    if (Test-Path $EnvFile) {
        Get-Content $EnvFile | ForEach-Object {
            if ($_ -match "^(.+?)=(.*)$") {
                [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], "Process")
            }
        }
        Write-Ok "Loaded .env"
    } else {
        Write-Host "No .env found — run: .\scripts\setup.ps1 local" -ForegroundColor Red
        exit 1
    }
}

function Start-Supabase {
    Write-Info "Starting Supabase..."
    Push-Location $RootDir
    docker compose up -d
    Pop-Location
    Write-Ok "Supabase running"
    Write-Host ""
    Write-Info "Studio:    http://localhost:54323"
    Write-Info "API:       http://localhost:54321"
    Write-Info "DB:        postgresql://postgres:postgres@localhost:54322/postgres"
    Write-Info "Auth:      http://localhost:9999"
    Write-Info "REST:      http://localhost:3000"
    Write-Info "Storage:   http://localhost:5000"
}

function Start-Backend {
    Write-Info "Starting FastAPI backend..."
    Push-Location "$RootDir\api"
    pip install -r requirements.txt -q 2>$null
    Write-Ok "Backend starting on http://localhost:8000"
    Write-Info "Swagger: http://localhost:8000/docs"
    Write-Info "Debug:   http://localhost:8000/api/debug"
    python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
    Pop-Location
}

Import-EnvFile

switch ($Mode) {
    "supabase" { Start-Supabase }
    "backend"  { Start-Backend }
    "all"      { Start-Supabase; Start-Backend }
}
