@echo off
echo ===================================================
echo   Starting Chrome with Enhanced Anti-Detection
echo ===================================================
echo.
echo This will launch Chrome with maximum stealth settings.
echo 1. Please LOG IN to TextNow in this window.
echo 2. Keep this window OPEN while running the automation.
echo 3. You can minimize it, but do not close it.
echo.

REM Create a local profile directory so login persists
if not exist "chrome_profile_stealth" mkdir "chrome_profile_stealth"

REM Launch Chrome with enhanced anti-detection flags
start "" chrome.exe ^
--remote-debugging-port=9222 ^
--user-data-dir="%~dp0chrome_profile_stealth" ^
--disable-blink-features=AutomationControlled ^
--exclude-switches=enable-automation ^
--disable-infobars ^
--start-maximized ^
--disable-web-security ^
--disable-features=IsolateOrigins,site-per-process ^
--allow-running-insecure-content ^
--disable-popup-blocking ^
--disable-save-password-bubble ^
--disable-translate ^
--no-first-run ^
--no-service-autorun ^
--password-store=basic

echo.
echo Chrome launched with stealth profile: %~dp0chrome_profile_stealth
echo.
echo IMPORTANT: 
echo - Complete any CAPTCHA or verification in this window
echo - Stay logged in to TextNow
echo - Keep this window open
echo.
pause
