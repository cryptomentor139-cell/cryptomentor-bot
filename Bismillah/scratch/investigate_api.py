import asyncio
from dotenv import load_dotenv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('D:/cryptomentorAI/Bismillah')
load_dotenv('D:/cryptomentorAI/Bismillah/.env')

from app.supabase_repo import _client

async def investigate():
    s = _client()
    res2 = s.table('autotrade_trades').select('*').eq('telegram_id', '7972497694').order('id', desc=True).limit(5).execute()
    print("\nTrades:")
    for t in res2.data:
        print(f"[ID: {t.get('id')}] [{t.get('opened_at') or t.get('created_at', '?')}] {t['symbol']} | Side: {t['side']} | Margin: {t.get('margin_used')} | Qty: {t.get('qty')} | Entry: {t.get('entry_price')} | SL: {t.get('sl_price')} | Leverage: {t.get('leverage')}")
        print(f"  Closed at: {t.get('closed_at')} | PnL: {t.get('realized_pnl')} | Status: {t.get('status')} | Close Reason: {t.get('close_reason')}")

if __name__ == '__main__':
    asyncio.run(investigate())
