import asyncio
from dotenv import load_dotenv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('D:/cryptomentorAI/Bismillah')
load_dotenv('D:/cryptomentorAI/Bismillah/.env')

from app.supabase_repo import _client
from app.bitunix_autotrade_client import BitunixAutoTradeClient

async def investigate():
    s = _client()
    tg_id = 7972497694
    
    # 1. Fetch autotrade session
    res = s.table('autotrade_sessions').select('*').eq('telegram_id', tg_id).execute()
    if not res.data:
        print("No session found.")
        return
    session = res.data[0]
    print(f"Session info: Initial Deposit: {session.get('initial_deposit')} | Current Balance: {session.get('current_balance')}")

    # 2. Fetch API keys from user_api_keys
    keys_res = s.table('user_api_keys').select('*').eq('telegram_id', tg_id).execute()
    if not keys_res.data:
        print("No API keys found in user_api_keys.")
        return
        
    keys = keys_res.data[0]
    # Check if api_secret is encrypted. If so, decrypt.
    import base64
    from cryptography.fernet import Fernet
    
    # Need to check how encryption is handled in codebase. Let's look at stackmentor/users_repo.
    # Actually wait, maybe I can just fetch via standard route since I'm on host.
    
    from app.users_repo import get_user_api_key
    decrypted_keys = get_user_api_key(tg_id)
    if not decrypted_keys:
        print("Could not decrypt keys.")
        return
        
    exchange = decrypted_keys.get('exchange')
    print(f"Exchange from Keys: {exchange}")
    
    api_key = decrypted_keys.get('api_key')
    api_secret = decrypted_keys.get('api_secret')
    
    if exchange == 'bitunix':
        client = BitunixAutoTradeClient(api_key, api_secret)
        acct = client.fetch_account()
        if acct.get('success'):
            print(f"Bitunix Live Balance: {acct.get('balance')} | Equity: {acct.get('equity')}")
        else:
            print("Failed to fetch Bitunix account:", acct)
            
        trades = client._request('GET', '/api/v1/futures/order/history', params={'limit': 10}, signed=True)
        print("\nBitunix Trades:")
        for t in trades.get('data', [])[:5]:
            print(t)
    elif exchange == 'bingx':
        from app.bingx_autotrade_client import BingXAutoTradeClient
        client = BingXAutoTradeClient(api_key, api_secret)
        acct = client.get_account_info()
        print(f"BingX Live Account: {acct}")
        
    # Check autotrade_trades table
    trades_res = s.table('autotrade_trades').select('*').eq('telegram_id', tg_id).order('id', desc=True).limit(5).execute()
    print(f"\nDB Trades Count: {len(trades_res.data)}")
    for t in trades_res.data:
        print(f"Trade: {t.get('symbol')} | PnL: {t.get('realized_pnl')}")


if __name__ == '__main__':
    asyncio.run(investigate())
