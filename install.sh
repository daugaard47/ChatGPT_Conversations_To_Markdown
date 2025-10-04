#!/bin/bash

# ChatGPT Conversations to Markdown - One-Command Installer (Mac/Linux)

set -e  # Exit on error

echo "======================================================================"
echo "🚀 ChatGPT Conversations to Markdown - Installer"
echo "======================================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "   Please install Python 3.7+ first:"
    echo "   - Mac: brew install python3"
    echo "   - Ubuntu/Debian: sudo apt install python3 python3-pip"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if running from cloned repo or need to clone
if [ ! -f "chatgpt_json_to_markdown.py" ]; then
    echo ""
    echo "📦 Cloning repository..."
    git clone https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown.git
    cd ChatGPT_Conversations_To_Markdown
fi

# Install Python dependencies
echo ""
echo "📥 Installing dependencies..."
pip3 install -r requirements.txt --quiet

echo ""
echo "======================================================================"
echo "✅ Installation Complete!"
echo "======================================================================"
echo ""
echo "📋 Next steps:"
echo "   1. Run setup wizard: python3 setup.py"
echo "   2. Convert conversations: python3 chatgpt_json_to_markdown.py"
echo ""
echo "💡 Need help? Visit: https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown"
echo ""
