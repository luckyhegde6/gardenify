# seed.ps1 — Seed database with test data (PowerShell)
# Usage: .\scripts\seed.ps1 [local|production]

param(
    [string]$Environment = "local"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$SeedFile = Join-Path $ProjectRoot "supabase\seed.sql"

Write-Host "=== Gardenify Seed Script ===" -ForegroundColor Cyan
Write-Host "Mode: $Environment"

# Load environment
if ($Environment -eq "local") {
    $EnvFile = Join-Path $ProjectRoot ".env"
    if (-not (Test-Path $EnvFile)) {
        Write-Host "ERROR: .env file not found. Run: Copy-Item .env.example .env" -ForegroundColor Red
        exit 1
    }
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "^([^#=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
    $DatabaseUrl = if ($env:SUPABASE_URL) { $env:SUPABASE_URL } else { "http://localhost:54321" }
    Write-Host "Using local Supabase: $DatabaseUrl"
} else {
    Write-Host "Using production Supabase"
    if (-not $env:SUPABASE_URL) {
        Write-Host "ERROR: SUPABASE_URL not set for production" -ForegroundColor Red
        exit 1
    }
    $DatabaseUrl = $env:SUPABASE_URL
}

# Check seed file
if (-not (Test-Path $SeedFile)) {
    Write-Host "ERROR: Seed file not found: $SeedFile" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Seed file: $SeedFile"
Write-Host ""

# Run seed
if (Get-Command supabase -ErrorAction SilentlyContinue) {
    Write-Host "Running via Supabase CLI..."
    supabase db reset --linked 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Fallback: running seed directly..."
        psql $DatabaseUrl -f $SeedFile
    }
} elseif (Get-Command psql -ErrorAction SilentlyContinue) {
    Write-Host "Running via psql..."
    psql $DatabaseUrl -f $SeedFile
} else {
    Write-Host "ERROR: Neither 'supabase' nor 'psql' found in PATH" -ForegroundColor Red
    Write-Host "Install: scoop install supabase"
    exit 1
}

Write-Host ""
Write-Host "=== Seed Complete ===" -ForegroundColor Green
Write-Host "Test user ID: 00000000-0000-0000-0000-000000000001"
Write-Host "Created: 5 identifications, 3 favorites"
