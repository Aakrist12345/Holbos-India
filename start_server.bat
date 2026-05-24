@echo off
title Holbos India - Development Server
echo.
echo ========================================
echo   HOLBOS INDIA - Starting Server...
echo ========================================
echo.

cd /d "C:\Users\AAKRIST SHARMA\Downloads\holbos_attendance_erp\holbos_attendance"

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo ----------------------------------------
echo  Server starting at:
echo  http://127.0.0.1:8000
echo ----------------------------------------
echo.

REM Open browser to correct HTTP (not HTTPS) URL after 2 seconds
start /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"

python manage.py runserver 127.0.0.1:8000

pause
