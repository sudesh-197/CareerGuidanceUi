@echo off
setlocal EnableDelayedExpansion
title CareerAI - Starting...
color 0A

echo.
echo  +----------------------------------------------+
echo  ^|      CareerAI - Intelligent Career           ^|
echo  ^|           Guidance System                    ^|
echo  +----------------------------------------------+
echo.

:: ── Project root = folder this .bat lives in ──────────────────────────────────
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
echo  Project root : %ROOT%
echo.

:: ══════════════════════════════════════════════════════════════════════════════
:: STEP 1 - Python
:: ══════════════════════════════════════════════════════════════════════════════
echo  [1/5] Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 goto :NO_PYTHON
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo  OK: %PY_VER%
echo.
goto :CHECK_NODE

:NO_PYTHON
echo  ERROR: Python not found.
echo  Download from: https://www.python.org/downloads/
echo  Tick "Add Python to PATH" during install.
pause
exit /b 1

:: ══════════════════════════════════════════════════════════════════════════════
:: STEP 2 - Node.js
:: ══════════════════════════════════════════════════════════════════════════════
:CHECK_NODE
echo  [2/5] Checking Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 goto :NO_NODE
for /f "tokens=*" %%v in ('node --version 2^>^&1') do set "NODE_VER=%%v"
echo  OK: Node.js %NODE_VER%
echo.
goto :SETUP_VENV

:NO_NODE
echo  ERROR: Node.js not found.
echo  Download from: https://nodejs.org/
pause
exit /b 1

:: ══════════════════════════════════════════════════════════════════════════════
:: STEP 3 - Virtual environment
:: ══════════════════════════════════════════════════════════════════════════════
:SETUP_VENV
echo  [3/5] Setting up Python environment...

set "VENV=%ROOT%\backend\venv"
set "VENV_PY=%VENV%\Scripts\python.exe"

:: Check if venv python actually works (guards against stale/wrong-user venv)
if exist "%VENV_PY%" (
    "%VENV_PY%" --version >nul 2>&1
    if %errorlevel% neq 0 goto :RECREATE_VENV
    echo  OK: Virtual environment found.
    goto :CHECK_PACKAGES
)

:RECREATE_VENV
echo  Creating virtual environment...
if exist "%VENV%" rmdir /s /q "%VENV%"
python -m venv "%VENV%"
if %errorlevel% neq 0 goto :VENV_FAIL
echo  OK: Virtual environment created.
goto :CHECK_PACKAGES

:VENV_FAIL
echo  WARNING: Could not create venv. Using system Python.
set "VENV_PY=python"

:CHECK_PACKAGES
echo  Checking Python packages...
"%VENV_PY%" -c "import flask" >nul 2>&1
if %errorlevel% neq 0 goto :INSTALL_PACKAGES
echo  OK: Packages ready.
echo.
goto :CHECK_NODE_MODULES

:INSTALL_PACKAGES
echo  Installing backend packages (may take a minute)...
"%VENV_PY%" -m pip install --quiet -r "%ROOT%\backend\requirements.txt"
if %errorlevel% neq 0 goto :PIP_FAIL
echo  OK: Packages installed.
echo.
goto :CHECK_NODE_MODULES

:PIP_FAIL
echo  ERROR: pip install failed. Check internet connection.
pause
exit /b 1

:: ══════════════════════════════════════════════════════════════════════════════
:: STEP 4 - Node modules
:: ══════════════════════════════════════════════════════════════════════════════
:CHECK_NODE_MODULES
echo  [4/5] Checking Node modules...
if exist "%ROOT%\frontend\node_modules\react" goto :NODE_MODULES_OK
echo  Running npm install (first time, a few minutes)...
cd /d "%ROOT%\frontend"
call npm install --silent
if %errorlevel% neq 0 goto :NPM_FAIL
echo  OK: Node modules installed.
echo.
goto :CLEAR_PORTS

:NODE_MODULES_OK
echo  OK: Node modules ready.
echo.
goto :CLEAR_PORTS

:NPM_FAIL
echo  ERROR: npm install failed.
pause
exit /b 1

:: ══════════════════════════════════════════════════════════════════════════════
:: STEP 5 - Clear ports
:: ══════════════════════════════════════════════════════════════════════════════
:CLEAR_PORTS
echo  [5/5] Clearing ports 3000 and 5000...
for /f "tokens=5" %%p in ('netstat -aon 2^>nul ^| findstr ":5000 " ^| findstr "LISTENING"') do taskkill /PID %%p /F >nul 2>&1
for /f "tokens=5" %%p in ('netstat -aon 2^>nul ^| findstr ":3000 " ^| findstr "LISTENING"') do taskkill /PID %%p /F >nul 2>&1
echo  OK: Ports clear.
echo.

set "BACKEND_RUNNER=%ROOT%\scripts\run_backend.bat"
set "FRONTEND_RUNNER=%ROOT%\scripts\run_frontend.bat"

:: ══════════════════════════════════════════════════════════════════════════════
:: LAUNCH
:: ══════════════════════════════════════════════════════════════════════════════
echo  Starting Flask backend  ->  http://localhost:5000
start "CareerAI Backend [port 5000]" cmd /k "%BACKEND_RUNNER%"

timeout /t 3 /nobreak >nul

echo  Starting React frontend ->  http://localhost:3000
start "CareerAI Frontend [port 3000]" cmd /k "%FRONTEND_RUNNER%"

echo.
echo  Waiting for React to compile (~20 seconds)...
timeout /t 20 /nobreak >nul

echo  Opening browser...
start "" http://localhost:3000

echo.
echo  +----------------------------------------------+
echo  ^|  CareerAI is running!                        ^|
echo  ^|                                              ^|
echo  ^|  Frontend  ->  http://localhost:3000         ^|
echo  ^|  Backend   ->  http://localhost:5000         ^|
echo  ^|                                              ^|
echo  ^|  Run STOP_PROJECT.bat to stop all servers.   ^|
echo  +----------------------------------------------+
echo.
pause
endlocal
