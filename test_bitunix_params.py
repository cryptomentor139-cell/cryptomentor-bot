import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), "Bismillah"))
load_dotenv(os.path.join(os.getcwd(), "Bismillah", ".env"))

from app.bitunix_autotrade_client import BitunixAutoTradeClient

# Using a test account if possible, or just trying with one of the users
def test_margin_mode():
    api_key = os.getenv("BITUNIX_API_KEY")
    api_secret = os.getenv("BITUNIX_API_SECRET")
    
    if not api_key:
        print("No API key found in .env")
        return

    client = BitunixAutoTradeClient(api_key, api_secret)
    symbol = "BTCUSDT"
    
    modes_to_try = [
        {"marginMode": "crossed", "marginCoin": "USDT"},
        {"marginMode": "isolated", "marginCoin": "USDT"},
        {"marginMode": "CROSSED"},
        {"marginMode": "ISOLATION"},
        {"marginMode": "CROSS"},
        {"marginMode": "ISOLATED"},
        {"margin_mode": "crossed"},
        {"margin_mode": "isolated"},
    ]
    
    for body in modes_to_try:
        print(f"Testing with body: {body}")
        try:
            # Manually call _request to bypass set_margin_mode logic
            res = client._request('POST', '/api/v1/futures/account/change_margin_mode', 
                                  body={"symbol": symbol, **body}, signed=True)
            print(f"Result: {res}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_margin_mode()
