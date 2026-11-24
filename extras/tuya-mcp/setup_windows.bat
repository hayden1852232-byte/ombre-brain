@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul || (echo 没找到 Python，请先到 python.org 安装，安装时勾选 Add python.exe to PATH & pause & exit /b 1)
if not exist venv py -3 -m venv venv
venv\Scripts\python -m pip install -q -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
if not exist .env copy .env.example .env >nul
echo.
echo 装好了。下一步：用记事本打开 .env 填凭证，然后双击 list_codes_windows.bat
pause
