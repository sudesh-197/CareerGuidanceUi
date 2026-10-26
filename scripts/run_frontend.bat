@echo off
title CareerAI Frontend [port 3000]
color 0E
cd /d "%~dp0..\frontend"
echo.
echo  Frontend -^> http://localhost:3000
echo  Close this window to stop the frontend.
echo.
set BROWSER=none
npm start
pause
