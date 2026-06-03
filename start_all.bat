@echo off
setlocal enabledelayedexpansion
title Power User Profiling System V2.0

echo ============================================
echo   Power User Profile System V2.0
echo ============================================
echo.

set ROOT=%~dp0

echo [1/2] Starting Django backend on port 8000...
cd /d "%ROOT%"
start "" "cmd.exe" /k "python manage.py runserver 0.0.0.0:8000"
timeout /t 5 /nobreak >nul

echo [2/2] Starting Vue frontend on port 5186...
cd /d "%ROOT%frontend"
start "" "cmd.exe" /k "npm run dev"
timeout /t 6 /nobreak >nul

echo.
echo ============================================
echo   System started successfully!
echo   Frontend : http://localhost:5186
echo   Backend  : http://localhost:8000
echo.
echo   Admin   : admin / admin123
echo   User    : user001 / pass123456
echo ============================================
echo.

start "" http://localhost:5186
pause
