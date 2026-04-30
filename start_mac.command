#!/bin/bash
# ═══════════════════════════════════════════
#  📅 Schedule Butler — Mac One-Click Start
# ═══════════════════════════════════════════
# Double-click this file to launch the bot.

# cd to the script's own directory (handles Finder double-click)
cd "$(dirname "$0")"

echo "==============================================="
echo " 📅 Schedule Butler"
echo "==============================================="

# 1. Check .env
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  .env not found!"
    echo "👉 Copy .env.example → .env and fill in your tokens."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# 2. Auto-detect python3
PYTHON=""
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo ""
    echo "⚠️  Python not found!"
    echo "👉 Install via: brew install python3"
    echo "   or download from https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "🐍 Using: $($PYTHON --version)"

# 3. Create venv if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON -m venv venv
fi

# 4. Install deps
echo "🚀 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt -q

# 5. Launch
echo ""
echo "✨ Starting bot..."
echo "   Press Ctrl+C to stop."
echo ""
python main.py

# Keep terminal open on error
echo ""
read -p "Bot stopped. Press Enter to close..."
