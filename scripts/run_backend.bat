@echo off
title CareerAI Backend [port 5000]
color 0B
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set FLASK_DEBUG=1
cd /d "%~dp0..\backend"
echo.
echo  Backend -^> http://localhost:5000
echo  Close this window to stop the backend.
echo.
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" run.py
) else (
    python run.py
)
pause
