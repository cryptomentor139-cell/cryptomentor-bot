import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
repo_root = Path(__file__).resolve().parent
sys.path.append(str(repo_root / "Bismillah"))

from dotenv import load_dotenv
load_dotenv(repo_root / ".env")
load_dotenv(repo_root / "Bismillah" / ".env")

from app.scalping_engine import ScalpingEngine
from app.trading_mode import ScalpingConfig, ScalpingSignal
from app.bitunix_autotrade_client import BitunixAutoTradeClient
from app.supabase_repo import _client

# Pairs from ENGINE_CONFIG
PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", 
         "DOTUSDT", "MATICUSDT", "LINKUSDT", "UNIUSDT", "ATOMUSDT", "XAUUSDT", "CLUSDT", "QQQUSDT"]

async def global_rerun():
    print("🔄 STARTING GLOBAL RERUN SYSTEM...")
    s = _client()
    
    # 1. FORCE 3% RISK FOR ALL USERS (as requested)
    print("Updating all users to 3% risk per trade...")
    s.table("autotrade_sessions").update({
        "risk_per_trade": 3.0,
        "one_click_risk_per_trade": 3.0
    }).neq("telegram_id", 0).execute()
    print("✅ All sessions updated to 3.0%.")

    # 2. Get active users
    res = s.table("autotrade_sessions").select("telegram_id, current_balance").eq("engine_active", True).execute()
    users = [r["telegram_id"] for r in res.data]
    print(f"Found {len(users)} active users to process.")
    
    if not users:
        print("No active users. Exiting.")
        return

    # 3. SCAN SYMBOLS (Global Cache)
    # We use a sample user to run the scanner logic
    sample_uid = users[0]
    sample_client = BitunixAutoTradeClient(sample_uid)
    scanner = ScalpingEngine(sample_uid, sample_client, None, 0, ScalpingConfig())
    
    signals_found = {}
    print(f"Scanning {len(PAIRS)} pairs for valid signals...")
    
    for symbol in PAIRS:
        try:
            # We bypass cooldown for the global rerun to catch missed opportunities
            signal = await scanner.generate_scalping_signal(symbol)
            if signal:
                print(f"🔥 VALID SIGNAL: {symbol} {signal.side} (Confidence: {signal.confidence}%)")
                signals_found[symbol] = signal
            else:
                # print(f"--- {symbol}: No current signal")
                pass
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")

    if not signals_found:
        print("\n❌ No valid signals found in the market right now.")
        print("Market may be ranging or signals haven't refreshed. All users are primed for next auto-scan.")
        return

    # 4. EXECUTE FOR ALL USERS
    for symbol, signal in signals_found.items():
        print(f"\n🚀 Executing {symbol} {signal.side} for all eligible users...")
        for uid in users:
            try:
                u_client = BitunixAutoTradeClient(uid)
                # Check position (using the sync get_positions wrapped in thread)
                pos_resp = await asyncio.to_thread(u_client.get_positions)
                
                if pos_resp.get("success"):
                    # result has 'positions' list
                    positions = pos_resp.get("positions", [])
                    if any(p.get("symbol") == symbol for p in positions):
                        print(f"  [User:{uid}] Already in {symbol}. Skipping.")
                        continue

                # Place order
                u_engine = ScalpingEngine(uid, u_client, None, 0, ScalpingConfig())
                u_engine.config.risk_per_trade = 3.0
                
                # place_scalping_order is async
                success = await u_engine.place_scalping_order(signal)
                if success:
                    print(f"  [User:{uid}] ✅ ORDER PLACED at 3% risk.")
                else:
                    print(f"  [User:{uid}] ❌ FAILED (Qty or Margin).")
            except Exception as ue:
                import traceback
                traceback.print_exc()
                print(f"  [User:{uid}] ⚠️ ERROR: {ue}")

    print("\n✅ Global rerun complete.")

if __name__ == "__main__":
    asyncio.run(global_rerun())
