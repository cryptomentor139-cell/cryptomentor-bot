import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), "Bismillah"))
load_dotenv(os.path.join(os.getcwd(), "Bismillah", ".env"))

from app.supabase_repo import _client

def check_global_trades():
    try:
        c = _client()
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        res = c.table("autotrade_trades").select("*").gte("opened_at", today).execute()
        trades = res.data or []
        print(f"Total trades today (Global): {len(trades)}")
        for t in trades[:10]:
             print(f"User {t.get('telegram_id')} | Sym: {t.get('symbol')} | Status: {t.get('status')} | Opened: {t.get('opened_at')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_global_trades()
