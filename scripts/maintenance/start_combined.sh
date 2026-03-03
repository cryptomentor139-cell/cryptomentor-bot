#!/bin/bash
# Script untuk menjalankan Bot Telegram + Automaton bersamaan

set -e  # Exit on error

echo "=========================================="
echo "  CryptoMentor + Automaton Launcher"
echo "=========================================="
echo ""

# Fungsi untuk cleanup saat script dihentikan
cleanup() {
    echo ""
    echo "Stopping all processes..."
    kill $BOT_PID $AUTOMATON_PID 2>/dev/null || true
    wait $BOT_PID $AUTOMATON_PID 2>/dev/null || true
    echo "All processes stopped."
    exit 0
}

# Trap SIGINT dan SIGTERM untuk cleanup
trap cleanup SIGINT SIGTERM EXIT

# Cek Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python tidak ditemukan!"
    exit 1
fi

# Cek Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js tidak ditemukan!"
    exit 1
fi

echo "[1/4] Checking Python..."
$PYTHON_CMD --version

echo "[2/4] Checking Automaton build..."
if [ ! -d "automaton/dist" ] || [ ! -f "automaton/dist/index.js" ]; then
    echo "Building Automaton..."
    cd automaton
    if [ ! -d "node_modules" ]; then
        echo "Installing Node.js dependencies..."
        npm ci --silent || npm install --silent
    fi
    npm run build || {
        echo "ERROR: Automaton build failed!"
        exit 1
    }
    cd ..
    echo "✓ Automaton built successfully"
else
    echo "✓ Automaton already built"
fi

echo "[3/4] Starting Telegram Bot..."
$PYTHON_CMD main.py &
BOT_PID=$!
echo "✓ Bot started (PID: $BOT_PID)"

# Wait a bit to ensure bot starts
sleep 2

echo "[4/4] Starting Automaton..."
cd automaton
node dist/index.js --run &
AUTOMATON_PID=$!
cd ..
echo "✓ Automaton started (PID: $AUTOMATON_PID)"

echo ""
echo "=========================================="
echo "  Both services are running!"
echo "  Bot PID: $BOT_PID"
echo "  Automaton PID: $AUTOMATON_PID"
echo "  Press Ctrl+C to stop both"
echo "=========================================="
echo ""

# Wait untuk kedua proses
wait $BOT_PID $AUTOMATON_PID
