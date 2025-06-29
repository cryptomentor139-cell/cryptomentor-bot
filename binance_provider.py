
import requests
import logging
from typing import List, Dict, Any

class BinanceFuturesProvider:
    def __init__(self):
        self.futures_base_url = "https://fapi.binance.com/fapi/v1"

    def get_tickers(self) -> List[str]:
        """Get list of all available USDT-margined futures symbols"""
        url = f"{self.futures_base_url}/exchangeInfo"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return [
                symbol['symbol']
                for symbol in data['symbols']
                if symbol['contractType'] == 'PERPETUAL' and symbol['quoteAsset'] == 'USDT'
            ]
        except Exception as e:
            logging.error(f"Error fetching Binance tickers: {e}")
            return []
