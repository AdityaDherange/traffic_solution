#!/bin/bash
# Smart Traffic System - Linux/Mac Startup Script

echo "========================================"
echo "  Smart Traffic System"
echo "  Version 2.0"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[!] Virtual environment not found"
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
    echo "[+] Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "[*] Checking dependencies..."
if ! pip show streamlit > /dev/null 2>&1; then
    echo "[!] Dependencies not installed"
    echo "[*] Installing dependencies..."
    pip install -r requirements.txt
    echo "[+] Dependencies installed"
    echo ""
fi

# Start the application
echo "[*] Starting Smart Traffic System..."
echo ""
echo "[+] Application will open in your browser"
echo "[+] Press Ctrl+C to stop the server"
echo ""
streamlit run app_new.py
