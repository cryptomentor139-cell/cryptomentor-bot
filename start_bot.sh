#!/bin/bash
# Script untuk menjalankan CryptoMentor AI Bot di Linux/Mac

echo "========================================"
echo "  CryptoMentor AI Bot - Starter"
echo "========================================"
echo ""

# Cek apakah di folder yang benar
if [ ! -f "main.py" ]; then
    echo "ERROR: File main.py tidak ditemukan!"
    echo "Pastikan Anda menjalankan script ini dari folder Bismillah"
    exit 1
fi

# Cek apakah .env ada
if [ ! -f ".env" ]; then
    echo "WARNING: File .env tidak ditemukan!"
    echo "Bot mungkin tidak bisa jalan tanpa konfigurasi."
    echo ""
fi

echo "[1/3] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    python3 --version
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    python --version
else
    echo "ERROR: Python tidak ditemukan!"
    echo "Install Python terlebih dahulu"
    exit 1
fi

echo ""
echo "[2/3] Installing dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "WARNING: Ada masalah saat install dependencies"
    echo "Bot mungkin tidak berfungsi dengan baik"
    echo ""
fi

echo ""
echo "[3/3] Starting bot..."
echo ""
echo "========================================"
echo "  Bot is starting..."
echo "  Press Ctrl+C to stop"
echo "========================================"
echo ""

$PYTHON_CMD main.py

echo ""
echo "========================================"
echo "  Bot stopped"
echo "========================================"
