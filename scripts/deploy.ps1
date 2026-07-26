#Requires -Version 5.1
<#
.SYNOPSIS
    Deploy Gardenify to production
.EXAMPLE
    .\scripts\deploy.ps1              # Deploy all
    .\scripts\deploy.ps1 backend      # Backend only
    .\scripts\deploy.ps1 mobile       # EAS build only
    .\scripts\deploy.ps1 migrate      # Supabase migrations only
#>
param(
    [ValidateSet("all","backend","mobile","migrate")]
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path $PSScriptRoot -Parent
$EnvFile = Join-Path $RootDir ".env"

function Write-Info { Write-Host "[DEPLOY] $args" -ForegroundColor Cyan }
function Write-Ok   { Write-Host "[OK]     $args" -ForegroundColor Green }
function Write-Warn { Write-Host "[WARN]   $args" -ForegroundColor Yellow }

# Load .env
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "^(.+?)=(.*)$") {
            [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], "Process")
        }
    }
}

function Deploy-Backend {
    Write-Info "Deploying Python backend to Vercel..."
    Push-Location $RootDir

    if (-not (Get-Command vercel -ErrorAction SilentlyContinue)) {
        Write-Warn "Installing Vercel CLI..."
        npm i -g vercel
    }

    if ($env:VERCEL_TOKEN) {
        vercel deploy --prod --token $env:VERCEL_TOKEN
    } else {
        vercel deploy --prod
    }

    Write-Ok "Backend deployed"
    Pop-Location
}

function Deploy-Mobile {
    Write-Info "Building Android APK..."
    Push-Location $RootDir
    npx eas-cli build -p android --profile production --non-interactive
    Write-Ok "Build submitted"
    Pop-Location
}

function Deploy-Migrate {
    Write-Info "Pushing Supabase migrations..."
    Push-Location $RootDir

    if (-not (Get-Command supabase -ErrorAction SilentlyContinue)) {
        Write-Warn "Installing Supabase CLI..."
        npm i -g supabase
    }

    if ($env:SUPABASE_PROJECT_REF) {
        supabase link --project-ref $env:SUPABASE_PROJECT_REF
    }
    supabase db push
    Write-Ok "Migrations applied"
    Pop-Location
}

switch ($Mode) {
    "backend" { Deploy-Backend }
    "mobile"  { Deploy-Mobile }
    "migrate" { Deploy-Migrate }
    "all"     { Deploy-Migrate; Deploy-Backend; Deploy-Mobile }
}
