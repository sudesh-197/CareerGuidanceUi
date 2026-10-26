@echo off
title CareerAI - Stopping...
color 0C

echo.
echo  +----------------------------------------------+
echo  ^|        CareerAI - Stopping Servers           ^|
echo  +----------------------------------------------+
echo.

echo  Stopping backend  (port 5000)...
set "FOUND5000=0"
for /f "tokens=5" %%p in ('netstat -aon 2^>nul ^| findstr ":5000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%p /F >nul 2>&1
    set "FOUND5000=1"
)
if "%FOUND5000%"=="1" (
    echo  OK: Backend stopped.
) else (
    echo  -- Backend was not running.
)

echo.
echo  Stopping frontend (port 3000)...
set "FOUND3000=0"
for /f "tokens=5" %%p in ('netstat -aon 2^>nul ^| findstr ":3000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%p /F >nul 2>&1
    set "FOUND3000=1"
)
if "%FOUND3000%"=="1" (
    echo  OK: Frontend stopped.
) else (
    echo  -- Frontend was not running.
)

echo.
echo  Closing server windows...
taskkill /FI "WINDOWTITLE eq CareerAI Backend [port 5000]"  /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq CareerAI Frontend [port 3000]" /F >nul 2>&1
echo  OK: Done.

echo.
echo  +----------------------------------------------+
echo  ^|  All CareerAI servers stopped.               ^|
echo  +----------------------------------------------+
echo.
pause
exit
