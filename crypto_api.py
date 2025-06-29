
import requests
import os
from binance_provider import BinanceFuturesProvider

class CryptoAPI:
    def __init__(self):
        self.provider = BinanceFuturesProvider()
        self.cryptonews_key = os.getenv("CRYPTONEWS_API_KEY")

    def get_futures_tickers(self):
        return self.provider.get_tickers()

    def get_latest_crypto_news(self, limit=5):
        url = "https://cryptonews-api.com/api/v1/category"
        params = {
            "section": "general",
            "items": limit,
            "token": self.cryptonews_key
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            articles = data.get("data", [])
            return articles
        except Exception as e:
            return [{"title": "Error fetching news", "url": str(e)}]
