import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
repo_root = Path(__file__).resolve().parent
# Critical: Add Bismillah to path so 'from app...' works
sys.path.append(str(repo_root / "Bismillah"))

from dotenv import load_dotenv
# Load from root or Bismillah
load_dotenv(repo_root / ".env")
load_dotenv(repo_root / "Bismillah" / ".env")

# Pre-import relative to repo root
from app.scalping_engine import ScalpingEngine
from app.trading_mode import ScalpingConfig
from app.bitunix_autotrade_client import BitunixAutoTradeClient
from app.supabase_repo import _client

async def repair_eth():
    print("Starting ETHUSDT Signal Repair (Fixed Path)...")
    s = _client()
    res = s.table("autotrade_sessions").select("telegram_id, current_balance").eq("engine_active", True).execute()
    users = [r["telegram_id"] for r in res.data if (r.get("current_balance") or 0) < 100]
    
    print(f"Checking {len(users)} potentially affected users...")
    
    if not users:
        print("No active users found.")
        return

    # Check signal using the first user
    client = BitunixAutoTradeClient(users[0])
    engine = ScalpingEngine(users[0], client, None, 0, ScalpingConfig())
    
    print("Scanning for current ETHUSDT signal...")
    signal = await engine._scan_single_symbol("ETHUSDT")
    if not signal:
        print("ETHUSDT is currently not signaling a valid entry in the scanner.")
        print("The market might have moved or the signal is no longer optimal. No action taken.")
        return

    print(f"Found active ETHUSDT {signal.side} signal (Confidence: {signal.confidence}%).")
    print(f"Entry: {signal.entry_price} | SL: {signal.sl_price}")

    for uid in users:
        print(f"\n[User:{uid}] Processing...")
        try:
            u_client = BitunixAutoTradeClient(uid)
            # Check positions via direct API to avoid engine overhead
            pos_resp = await u_client._bitunix_request("POST", "/api/v1/futures/position", {"symbol": "ETHUSDT"})
            if pos_resp.get("success") and pos_resp.get("data"):
                # If data is a list and not empty
                if isinstance(pos_resp["data"], list) and len(pos_resp["data"]) > 0:
                    print(f"Skipping: User already has ETH position.")
                    continue
                # If data is single object with quantity
                if isinstance(pos_resp["data"], dict) and float(pos_resp["data"].get("size", 0)) != 0:
                    print(f"Skipping: User already has ETH position.")
                    continue

            # Place order
            u_engine = ScalpingEngine(uid, u_client, None, 0, ScalpingConfig())
            success = await u_engine.place_scalping_order(signal)
            if success:
                print(f"SUCCESS: Order placed.")
            else:
                print(f"FAILED: Still insufficient qty or risk limit.")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(repair_eth())
