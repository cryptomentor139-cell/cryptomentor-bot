#!/bin/bash
# ========================================
# CryptoMentor Bot - Restart Script
# Linux/Mac Shell Script
# ========================================

echo ""
echo "========================================"
echo "  CryptoMentor Bot - Restart Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 tidak ditemukan!"
    echo "Pastikan Python3 sudah terinstall"
    exit 1
fi

echo "[1/4] Mencari proses bot yang sedang berjalan..."
echo ""

# Find and kill existing bot processes
BOT_PIDS=$(pgrep -f "python.*main.py" || true)

if [ -n "$BOT_PIDS" ]; then
    echo "Menghentikan proses bot (PIDs: $BOT_PIDS)..."
    kill -9 $BOT_PIDS 2>/dev/null || true
    echo "Proses bot dihentikan"
else
    echo "Tidak ada proses bot yang berjalan"
fi

echo ""
echo "[2/4] Menunggu proses selesai..."
sleep 2

echo "[3/4] Membersihkan cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "Cache dibersihkan"
echo ""

echo "[4/4] Memulai bot..."
echo ""
echo "========================================"
echo "  Bot Starting..."
echo "  Press Ctrl+C to stop"
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
