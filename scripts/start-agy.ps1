<#
.SYNOPSIS
    UXOps AI — Antigravity CLI Launcher (PowerShell)
.DESCRIPTION
    Launches the Antigravity CLI (`agy`) from the root of the UXOps AI repository.
    Automatically resolves the project root directory regardless of invocation location.
.EXAMPLE
    .\scripts\start-agy.ps1
#>

$ErrorActionPreference = "Stop"

# Determine script path and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")

# Change location to project root
Set-Location $ProjectRoot

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "🚀 Launching Antigravity CLI for UXOps AI" -ForegroundColor Green
Write-Host "📂 Project Root: $ProjectRoot" -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Cyan

# Verify if agy command exists
$AgyCmd = Get-Command agy -ErrorAction SilentlyContinue

if (-not $AgyCmd) {
    Write-Host "❌ Error: 'agy' command (Antigravity CLI) was not found in your PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "To install Antigravity CLI:" -ForegroundColor Yellow
    Write-Host "  Follow instructions at https://antigravity.google/docs/cli"
    Write-Host "  Or ensure the binary is installed and present in your system PATH."
    Write-Host ""
    exit 1
}

Write-Host "Starting Antigravity CLI..." -ForegroundColor Gray
& agy @args
