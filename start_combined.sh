#!/bin/bash
# Script untuk menjalankan Bot Telegram + Automaton bersamaan

echo "=========================================="
echo "  CryptoMentor + Automaton Launcher"
echo "=========================================="
echo ""

# Fungsi untuk cleanup saat script dihentikan
cleanup() {
    echo ""
    echo "Stopping all processes..."
    kill $BOT_PID $AUTOMATON_PID 2>/dev/null
    wait $BOT_PID $AUTOMATON_PID 2>/dev/null
    echo "All processes stopped."
    exit 0
}

# Trap SIGINT dan SIGTERM untuk cleanup
trap cleanup SIGINT SIGTERM

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

echo "[1/4] Installing Python dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt --quiet

echo "[2/4] Installing Node.js dependencies for Automaton..."
cd automaton
npm install --silent
cd ..

echo "[3/4] Starting Telegram Bot..."
$PYTHON_CMD main.py &
BOT_PID=$!
echo "✓ Bot started (PID: $BOT_PID)"

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
