@echo off
echo ================================================
echo   TextNow Anti-Bot Detection Setup
echo ================================================
echo.
echo This script will install required dependencies
echo for enhanced anti-detection features.
echo.
pause

echo.
echo [1/3] Installing selenium-stealth...
pip install selenium-stealth

echo.
echo [2/3] Verifying other dependencies...
pip install -r requirements.txt

echo.
echo [3/3] Testing installation...
python -c "from selenium_stealth import stealth; print('[OK] selenium-stealth installed successfully')"

echo.
echo ================================================
echo   Installation Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Run: run_chrome_stealth.bat
echo 2. Log in to TextNow manually in the opened Chrome window
echo 3. Run: python textnow_automation.py
echo.
echo For more information, see: ANTI_BOT_SOLUTION.md
echo.
pause
