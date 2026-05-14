<#
.SYNOPSIS
Build Kshethra-Mithram Windows standalone executable

.DESCRIPTION
This script builds a self-contained Windows .exe for the Kshethra-Mithram
temple management application. It handles:
1. Building frontend assets (webpack)
2. Installing PyInstaller
3. Running PyInstaller to create the executable

.EXAMPLE
PS> .\build.ps1
#>

# Exit on first error
$ErrorActionPreference = "Stop"

# Get the project root (parent of windows-app)
$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Kshethra-Mithram Windows Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build webpack assets
Write-Host "Step 1: Building webpack frontend assets..." -ForegroundColor Yellow
Push-Location $projectRoot
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Webpack build failed" -ForegroundColor Red
    exit 1
}
Pop-Location

# Step 2: Ensure PyInstaller is installed
Write-Host ""
Write-Host "Step 2: Installing PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller installation failed" -ForegroundColor Red
    exit 1
}

# Step 3: Run PyInstaller
Write-Host ""
Write-Host "Step 3: Building executable with PyInstaller..." -ForegroundColor Yellow
Push-Location $projectRoot
pyinstaller windows-app/kshethra-mithram.spec --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller build failed" -ForegroundColor Red
    exit 1
}
Pop-Location

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Build complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your application is ready at:" -ForegroundColor Cyan
Write-Host "  windows-app\dist\kshethra-mithram\kshethra-mithram.exe" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Cyan
Write-Host "  .\windows-app\dist\kshethra-mithram\kshethra-mithram.exe" -ForegroundColor Yellow
Write-Host ""
