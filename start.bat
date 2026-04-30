@echo off
chcp 65001 > nul
echo ===============================================
echo  📅 欢迎启动日程管家 (Schedule Butler)
echo ===============================================

if not exist ".env" (
    echo ⚠️ 错误: 找不到 .env 配置文件！
    echo 💡 请先将 .env.example 复制为 .env，并填入你的 Token 配置。
    pause
    exit /b 1
)

if not exist "venv" (
    echo 📦 正在为你创建虚拟环境...
    python -m venv venv
)

echo 🚀 正在安装/更新依赖...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q

echo ✨ 启动机器人...
python main.py
pause
