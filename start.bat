@echo off
REM Smart Traffic System - Windows Startup Script

echo ========================================
echo   Smart Traffic System
echo   Version 2.0
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [!] Virtual environment not found
    echo [*] Creating virtual environment...
    python -m venv venv
    echo [+] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo [*] Checking dependencies...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [!] Dependencies not installed
    echo [*] Installing dependencies...
    pip install -r requirements.txt
    echo [+] Dependencies installed
    echo.
)

REM Start the application
echo [*] Starting Smart Traffic System...
echo.
echo [+] Application will open in your browser
echo [+] Press Ctrl+C to stop the server
echo.
streamlit run app_new.py

pause
