#!/bin/bash
# Run OpenClaw credits migration on Railway

echo "🔧 Running OpenClaw Credits Migration on Railway"
echo "=================================================="

# Run both migration scripts
echo ""
echo "1️⃣ Creating tables..."
python fix_openclaw_credits_sqlite.py

echo ""
echo "2️⃣ Adding columns..."
python fix_credits_column.py

echo ""
echo "=================================================="
echo "✅ Migration completed!"
echo "=================================================="
