@echo off
echo ========================================================
echo   TextNow 便携版启动 (Chrome v121)
echo ========================================================
echo.

set CHROME_BIN=%~dp0chrome_portable\bin\chrome.exe

if not exist %CHROME_BIN% (
    echo ❌ 错误：未找到 Chrome v121
    echo 请先运行: python download_chrome.py
    pause
    exit /b
)

echo 正在启动 Chrome v121...
echo 请在打开的窗口中登录 TextNow
echo.

%CHROME_BIN% --remote-debugging-port=9222 --user-data-dir="%~dp0chrome_profile_v121" --no-first-run --no-default-browser-check https://www.textnow.com/login

pause
