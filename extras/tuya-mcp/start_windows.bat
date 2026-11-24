@echo off
chcp 65001 >nul
title tuya-mcp 哄睡玩偶
cd /d "%~dp0"
:loop
venv\Scripts\python server.py
echo 服务退出了，5 秒后自动重启...
timeout /t 5 >nul
goto loop
