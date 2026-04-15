#!/usr/bin/env python3
"""Inspect actual DB data via API to understand what's wrong with the display."""
import paramiko
import json

HOST = "147.93.156.165"
USER = "root"
PASS = "<REDACTED_VPS_PASSWORD>"

def run(ssh, cmd):
    _, stdout, _ = ssh.exec_command(cmd, timeout=20)
    return stdout.read().decode("utf-8", errors="replace")

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=<REDACTED_PASSWORD> timeout=15)

    script = '''
import sys, os, json
sys.path.insert(0, '/root/cryptomentor-bot')
sys.path.insert(0, '/root/cryptomentor-bot/Bismillah')
os.chdir('/root/cryptomentor-bot')
from dotenv import load_dotenv
load_dotenv('/root/cryptomentor-bot/.env')

# Use venv
sys.path.insert(0, '/root/cryptomentor-bot/venv/lib/python3.12/site-packages')
sys.path.insert(0, '/root/cryptomentor-bot/venv/lib/python3.11/site-packages')

from supabase import create_client
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
db = create_client(url, key)

# Sample 10 closed trades - look at ALL fields
result = db.table("autotrade_trades").select("*").neq("status", "open").limit(10).order("opened_at", desc=True).execute()
trades = result.data or []
print("=== SAMPLE CLOSED TRADES (most recent 10) ===")
for t in trades:
    print(json.dumps({
        "user": t.get("telegram_id"),
        "symbol": t.get("symbol"),
        "status": t.get("status"),
        "side": t.get("side"),
        "entry": t.get("entry_price"),
        "exit": t.get("exit_price"),
        "qty": t.get("qty"),
        "pnl_usdt": t.get("pnl_usdt"),
        "pnl_pct": t.get("pnl_pct"),
        "opened_at": (t.get("opened_at") or "")[:16],
        "closed_at": (t.get("closed_at") or "")[:16],
    }))

# Get ALL fields of autotrade_trades
result_all = db.table("autotrade_trades").select("*").limit(1).execute()
if result_all.data:
    print("\\n=== ALL TRADE TABLE COLUMNS ===")
    print(list(result_all.data[0].keys()))

# Count trades by status (last 30 days)
from datetime import datetime, timedelta
start = (datetime.utcnow() - timedelta(days=30)).isoformat()
result2 = db.table("autotrade_trades").select("status, pnl_usdt").gte("opened_at", start).execute()
from collections import Counter
statuses = Counter(t["status"] for t in (result2.data or []))
print("\\n=== TRADE STATUS COUNTS (last 30d) ===")
for s, c in sorted(statuses.items(), key=lambda x: -x[1]):
    print(f"  {s}: {c}")

# pnl_usdt null/zero analysis
closed_trades = [t for t in (result2.data or []) if t.get("status") not in ("open", None)]
null_pnl = sum(1 for t in closed_trades if t.get("pnl_usdt") is None)
zero_pnl = sum(1 for t in closed_trades if t.get("pnl_usdt") == 0)
pos_pnl = sum(1 for t in closed_trades if (t.get("pnl_usdt") or 0) > 0)
neg_pnl = sum(1 for t in closed_trades if (t.get("pnl_usdt") or 0) < 0)
print(f"\\n=== PNL_USDT ANALYSIS (closed trades, last 30d) ===")
print(f"  Total closed: {len(closed_trades)}")
print(f"  NULL pnl: {null_pnl}")
print(f"  Zero pnl: {zero_pnl}")
print(f"  Positive pnl: {pos_pnl}")
print(f"  Negative pnl: {neg_pnl}")

# Check session fields
result3 = db.table("autotrade_sessions").select("*").limit(1).execute()
if result3.data:
    print("\\n=== SESSION TABLE COLUMNS ===")
    print(list(result3.data[0].keys()))
    print("Sample:", json.dumps({k: v for k, v in result3.data[0].items() if k not in ("api_key", "api_secret", "password")}))
'''

    sftp = ssh.open_sftp()
    with sftp.file('/tmp/inspect_db.py', 'w') as f:
        f.write(script)
    sftp.close()

    out = run(ssh, "/root/cryptomentor-bot/venv/bin/python3 /tmp/inspect_db.py 2>&1")
    print(out)
    ssh.close()

if __name__ == "__main__":
    main()
