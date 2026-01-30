@echo off
echo ========================================
echo TextNow 手动发送工具
echo ========================================
echo.
echo 功能:
echo 1. 向当前选中的对话发送自定义SMS
echo 2. 提供3个预设模板
echo 3. 支持自定义消息编辑
echo.
echo 使用前请确保:
echo - 已运行 run_chrome_debug.bat
echo - 已在Chrome中登录TextNow
echo ========================================
echo.
pause

python textnow_manual_send.py

pause
