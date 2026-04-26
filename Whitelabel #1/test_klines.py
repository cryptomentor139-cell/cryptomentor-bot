"""Test klines provider WL#1 — pastikan pakai CryptoCompare bukan Bitunix"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.providers.data_provider import inject_provider_env
inject_provider_env()

from app.providers.alternative_klines_provider import alternative_klines_provider

for symbol in ["BTC", "ETH", "BNB"]:
    klines = alternative_klines_provider.get_klines(symbol, interval='1h', limit=5)
    if klines:
        last = klines[-1]
        print(f"✅ {symbol}USDT — {len(klines)} candles | close: {last[4]}")
    else:
        print(f"❌ {symbol}USDT — failed to get klines")
