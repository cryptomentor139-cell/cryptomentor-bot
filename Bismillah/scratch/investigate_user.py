import sys
import asyncio
from dotenv import load_dotenv
from pprint import pprint

sys.path.append('D:/cryptomentorAI/Bismillah')
load_dotenv('D:/cryptomentorAI/Bismillah/.env')

from app.supabase_repo import _client

async def investigate():
    s = _client()
    
    res = s.table('autotrade_sessions').select('*').eq('telegram_id', '7972497694').execute()
    if not res.data:
        print("No session")
        return
    session = res.data[0]
    print(f"Session Mode: {session.get('risk_mode')} | Risk: {session.get('risk_per_trade')}% | Default Leverage: {session.get('leverage')}x")
    
    res2 = s.table('autotrade_trades').select('*').eq('telegram_id', '7972497694').order('id', desc=True).limit(5).execute()
    print("\nTrades:")
    for t in res2.data:
        print(f"[{t.get('opened_at') or t.get('created_at', '?')}] {t['symbol']} | Side: {t['side']} | Margin: {t.get('margin_used')} | PositionSize(Qty): {t.get('qty')} | Entry: {t.get('entry_price')} | SL: {t.get('sl_price')} | Leverage: {t.get('leverage')}")
        print(f"  Closed at: {t.get('closed_at')} | PnL: {t.get('realized_pnl')} | Status: {t.get('status')} | Close Reason: {t.get('close_reason')}")

if __name__ == '__main__':
    asyncio.run(investigate())
