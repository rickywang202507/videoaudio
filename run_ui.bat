@echo off
title MU Call Processor AI - RUNNING
echo ==================================================
echo       MU CALL PROCESSOR AI ENHANCED (v2.1)
echo ==================================================
echo.

cd /d "%~dp0"

:: Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b
)

echo [1/2] Scheduling Browser Launch (in 4s)...
:: Start a background task to open the browser after 4 seconds
start /b cmd /c "timeout /t 4 /nobreak >nul && start http://127.0.0.1:8000"

echo [2/2] Starting Server...
echo.
echo ==================================================
echo    IMPORTANT INSTRUCTIONS:
echo    ----------------------------------------------
echo    1. The browser will open automatically.
echo    2. This window must STAY OPEN for the app to work.
echo    3. To STOP the app, simple CLOSE THIS WINDOW (Click X).
echo ==================================================
echo.

:: Run server directly (blocking mode). 
:: When this window is closed, the server dies.
python server.py
