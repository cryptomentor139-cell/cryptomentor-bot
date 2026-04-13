import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.join(os.getcwd(), "Bismillah"))

# Load env before importing other modules that use os.getenv
load_dotenv(os.path.join(os.getcwd(), "Bismillah", ".env"))

from app.supabase_repo import _client

def check_active():
    try:
        c = _client()
        
        # 1. Check active sessions
        res = c.table("autotrade_sessions").select("*").eq("engine_active", True).execute()
        sessions = res.data or []
        print(f"--- Active Sessions: {len(sessions)} ---")
        for s in sessions:
            print(f"User {s.get('telegram_id')} | Status: {s.get('status')} | Mode: {s.get('trading_mode')}")

        # 2. Check today's trades
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        res_trades = c.table("autotrade_trades").select("*").gte("opened_at", today).execute()
        trades = res_trades.data or []
        print(f"\n--- Trades Today ({today}): {len(trades)} ---")
        for t in trades:
            print(f"User {t.get('telegram_id')} | Sym: {t.get('symbol')} | Side: {t.get('side')} | Status: {t.get('status')} | Profit: {t.get('profit_usdt')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_active()
