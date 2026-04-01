@echo off

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 未安装，请先安装 Python 3.7+
    pause
    exit /b 1
)

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败
    pause
    exit /b 1
)

REM 启动后台服务
echo 启动后台服务...
python backend/app.py

pause