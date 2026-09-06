# Antigravity Link — Universal Windows 1-Liner Installer
# Usage: irm https://raw.githubusercontent.com/ImNotMrReaper/antigravity-link/main/install.ps1 | iex
$ErrorActionPreference = "SilentlyContinue"
$repoUrl = "https://github.com/ImNotMrReaper/antigravity-link.git"
$installDir = Join-Path $HOME "antigravity-link"

if (Test-Path ".\agy_link.py") {
    $installDir = (Get-Location).Path
} else {
    Write-Host "📦 Cloning Antigravity Link to $installDir..." -ForegroundColor Cyan
    if (Test-Path "$installDir\.git") {
        Push-Location $installDir
        git pull origin main
        Pop-Location
    } else {
        git clone $repoUrl $installDir
    }
}

Write-Host "🚀 Running Antigravity Link Windows Installer..." -ForegroundColor Cyan
Push-Location $installDir
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $installDir "install_windows_shortcuts.ps1")
Pop-Location
