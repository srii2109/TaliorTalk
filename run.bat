@echo off
title TailorTalk Launcher
echo ========================================================
echo        🏮 TAILORTALK: LUXURY SAREE SEARCH AGENT 🏮
echo ========================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python 3.9+ and make sure "Add Python to PATH" is checked.
    echo.
    pause
    exit /b
)

:: Install/Verify packages
echo [1/3] Verifying and installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies failed to install. Attempting to start anyway...
)
echo.

:: Configure Gemini API Key
echo [2/3] Configuring secure Gemini API connection...
if "%GEMINI_API_KEY%"=="" (
    echo Gemini API Key not found in system variables.
    set /p GEMINI_API_KEY="Please paste your Gemini API Key and press Enter: "
) else (
    echo [SUCCESS] Existing GEMINI_API_KEY environment variable detected.
)
echo.

:: Launch Streamlit Server
echo [3/3] Starting Streamlit visual dashboard...
echo.
python -m streamlit run app.py --server.port 8501

pause
