#!/bin/bash
echo "==============================================="
echo " 📅 欢迎启动日程管家 (Schedule Butler)"
echo "==============================================="

if [ ! -f .env ]; then
    echo "⚠️ 错误: 找不到 .env 配置文件！"
    echo "💡 请先将 .env.example 复制为 .env，并填入你的 Token 配置。"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "📦 正在为你创建虚拟环境..."
    python3 -m venv venv
fi

echo "🚀 正在安装/更新依赖..."
source venv/bin/activate
pip install -r requirements.txt -q

echo "✨ 启动机器人..."
python main.py
