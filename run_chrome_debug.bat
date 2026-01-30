@echo off
echo ===================================================
echo   Starting Chrome for TextNow Automation
echo ===================================================
echo.
echo This will launch a persistent Chrome window for the bot to use.
echo 1. Please LOG IN to TextNow in this window.
echo 2. Keep this window OPEN while running the Sync tool.
echo 3. You can minimize it, but do not close it.
echo.

REM Create a local profile directory so login persists
if not exist "chrome_profile_debug" mkdir "chrome_profile_debug"

REM Launch Chrome with debugging port 9222
start "" chrome.exe --remote-debugging-port=9222 --user-data-dir="%~dp0chrome_profile_debug" --disable-blink-features=AutomationControlled --exclude-switches=enable-automation --disable-infobars --start-maximized

echo Chrome launched. User Data: %~dp0chrome_profile_debug
pause
