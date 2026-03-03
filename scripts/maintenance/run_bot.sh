#!/bin/bash
# ========================================
# CryptoMentor Bot - Run Script
# Linux/Mac Shell Script
# ========================================

echo ""
echo "========================================"
echo "  CryptoMentor Bot - Starting..."
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 tidak ditemukan!"
    echo "Pastikan Python3 sudah terinstall"
    exit 1
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "[ERROR] main.py tidak ditemukan!"
    echo "Pastikan Anda berada di folder Bismillah"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file tidak ditemukan!"
    echo "Bot mungkin tidak berfungsi tanpa konfigurasi"
    echo ""
    read -p "Press Enter to continue anyway..."
fi

echo "[INFO] Starting CryptoMentor Bot..."
echo "[INFO] Press Ctrl+C to stop"
echo ""
echo "========================================"
echo ""

# Start bot
python3 main.py

# If bot exits with error
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "  Bot stopped with error!"
    echo "========================================"
    read -p "Press Enter to continue..."
fi
