@echo off
echo ================================================
echo   Installing Undetected ChromeDriver
echo ================================================
echo.
echo This will install the most powerful anti-detection library.
echo.
pause

echo.
echo [1/2] Installing undetected-chromedriver...
pip install undetected-chromedriver

echo.
echo [2/2] Verifying installation...
python -c "import undetected_chromedriver; print('[OK] undetected-chromedriver version:', undetected_chromedriver.__version__)"

echo.
echo ================================================
echo   Installation Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Run: python textnow_undetected.py
echo 2. Test if you can pass the verification
echo.
pause
