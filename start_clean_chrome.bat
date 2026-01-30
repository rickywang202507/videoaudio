@echo off
echo ========================================================
echo   TextNow 纯净启动模式
echo ========================================================
echo.
echo 1. 将启动一个全新的 Chrome 窗口
echo 2. 这个窗口没有"受自动测试软件控制"的条幅
echo 3. 请在这个窗口中登录 TextNow，并完成验证码
echo.
echo ========================================================
pause

taskkill /f /im chrome.exe /t >nul 2>&1

:: 使用您的 Chrome 路径
set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist %CHROME_PATH% set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

:: 启动 Chrome，只开启调试端口，不添加任何反检测参数（越少越好）
%CHROME_PATH% --remote-debugging-port=9222 --user-data-dir="%~dp0chrome_profile_manual" https://www.textnow.com/login

echo.
echo 浏览器已启动！
echo.
echo 请在浏览器中：
echo 1. 输入账号密码
echo 2. 通过验证码（这时候应该很容易过）
echo 3. 登录成功进入页面后
echo.
echo 回到这里运行 python connect_textnow.py
echo.
pause
