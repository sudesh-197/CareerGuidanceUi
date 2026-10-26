@echo off
setlocal
title CareerAI - Install Dependencies
color 0B

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║     CareerAI - First-Time Setup              ║
echo  ╚══════════════════════════════════════════════╝
echo.
echo  This will install all Python and Node.js dependencies.
echo  Run this ONCE before using START_PROJECT.bat.
echo.
pause

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

:: ── Python check ──────────────────────────────────────────────────────────────
echo.
echo  [1/4] Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  ✗ Python not found. Install from https://python.org
    pause & exit /b 1
)
python --version
echo  ✓ Python OK.

:: ── Node check ────────────────────────────────────────────────────────────────
echo.
echo  [2/4] Checking Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo  ✗ Node.js not found. Install from https://nodejs.org
    pause & exit /b 1
)
node --version
echo  ✓ Node.js OK.

:: ── Python venv + packages ────────────────────────────────────────────────────
echo.
echo  [3/4] Setting up Python virtual environment...
set "VENV=%ROOT%\backend\venv"

if not exist "%VENV%\Scripts\python.exe" (
    echo  Creating venv...
    python -m venv "%VENV%"
)

echo  Installing Python packages (this may take a minute)...
"%VENV%\Scripts\pip.exe" install --upgrade pip --quiet
"%VENV%\Scripts\pip.exe" install -r "%ROOT%\backend\requirements.txt" --quiet
if %errorlevel% neq 0 (
    echo  ✗ pip install failed. Check your internet connection.
    pause & exit /b 1
)
echo  ✓ Python packages installed.

:: ── Node modules ──────────────────────────────────────────────────────────────
echo.
echo  [4/4] Installing Node.js packages (this may take a few minutes)...
cd /d "%ROOT%\frontend"
call npm install
if %errorlevel% neq 0 (
    echo  ✗ npm install failed.
    pause & exit /b 1
)
echo  ✓ Node packages installed.

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║  Setup complete!                             ║
echo  ║  You can now run START_PROJECT.bat           ║
echo  ╚══════════════════════════════════════════════╝
echo.
pause
endlocal
