#!/bin/bash
# ========================================
# CryptoMentor Bot - Status Check
# Linux/Mac Shell Script
# ========================================

echo ""
echo "========================================"
echo "  CryptoMentor Bot - Status Check"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 tidak ditemukan!"
    echo "Pastikan Python3 sudah terinstall"
    exit 1
fi

echo "[INFO] Checking bot status..."
echo ""

# Check for running bot processes
BOT_PIDS=$(pgrep -f "python.*main.py" || true)

if [ -n "$BOT_PIDS" ]; then
    echo "[RUNNING] Bot process found (PIDs: $BOT_PIDS)"
    echo ""
    echo "[STATUS] Bot is RUNNING ✓"
else
    echo "[STATUS] Bot is NOT running ✗"
fi

echo ""
echo "========================================"
echo ""

# Check configuration
if [ -f ".env" ]; then
    echo "[CONFIG] .env file: EXISTS ✓"
else
    echo "[CONFIG] .env file: MISSING ✗"
fi

if [ -f "main.py" ]; then
    echo "[CONFIG] main.py: EXISTS ✓"
else
    echo "[CONFIG] main.py: MISSING ✗"
fi

if [ -f "bot.py" ]; then
    echo "[CONFIG] bot.py: EXISTS ✓"
else
    echo "[CONFIG] bot.py: MISSING ✗"
fi

echo ""
echo "========================================"
