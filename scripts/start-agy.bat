@echo off
rem ==============================================================================
rem UXOps AI — Antigravity CLI Launcher (Windows Batch)
rem ==============================================================================
rem This script launches the Antigravity CLI (`agy`) from the root of the UXOps AI
rem repository. It automatically navigates to the project root directory.
rem ==============================================================================

setlocal enabledelayedexpansion

rem Resolve project root relative to script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%.."
set "PROJECT_ROOT=%CD%"

echo ======================================================
echo 🚀 Launching Antigravity CLI for UXOps AI
echo 📂 Project Root: %PROJECT_ROOT%
echo ======================================================

rem Check if agy exists in PATH
where agy >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: 'agy' command ^(Antigravity CLI^) was not found in your PATH.
    echo.
    echo To install Antigravity CLI:
    echo   Follow instructions at https://antigravity.google/docs/cli
    echo   Or ensure the binary is installed and present in your system PATH.
    echo.
    exit /b 1
)

echo Starting Antigravity CLI...
agy %*
