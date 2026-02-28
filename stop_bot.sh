#!/bin/bash
# ========================================
# CryptoMentor Bot - Stop Script
# Linux/Mac Shell Script
# ========================================

echo ""
echo "========================================"
echo "  CryptoMentor Bot - Stop Script"
echo "========================================"
echo ""

echo "[INFO] Mencari proses bot yang sedang berjalan..."
echo ""

# Find bot processes
BOT_PIDS=$(pgrep -f "python.*main.py" || true)

if [ -n "$BOT_PIDS" ]; then
    echo "[INFO] Menghentikan proses bot (PIDs: $BOT_PIDS)..."
    kill -9 $BOT_PIDS 2>/dev/null || true
    echo ""
    echo "[SUCCESS] Bot berhasil dihentikan!"
else
    echo "[INFO] Tidak ada proses bot yang berjalan"
fi

echo ""
echo "========================================"
