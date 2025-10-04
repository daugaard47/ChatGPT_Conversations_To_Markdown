@echo off
REM ChatGPT Conversations to Markdown - One-Command Installer (Windows)

echo ======================================================================
echo 🚀 ChatGPT Conversations to Markdown - Installer
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo    Please install Python 3.7+ first:
    echo    Download from: https://www.python.org/downloads/
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if running from cloned repo or need to clone
if not exist "chatgpt_json_to_markdown.py" (
    echo.
    echo 📦 Cloning repository...
    git clone https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown.git
    cd ChatGPT_Conversations_To_Markdown
)

REM Install Python dependencies
echo.
echo 📥 Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ======================================================================
echo ✅ Installation Complete!
echo ======================================================================
echo.
echo 📋 Next steps:
echo    1. Run setup wizard: python setup.py
echo    2. Convert conversations: python chatgpt_json_to_markdown.py
echo.
echo 💡 Need help? Visit: https://github.com/daugaard47/ChatGPT_Conversations_To_Markdown
echo.
pause
