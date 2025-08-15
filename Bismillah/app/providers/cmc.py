
import os
from typing import Dict, Any, Optional, List
from app.providers.http import fetch_json

CMC_API_KEY = os.getenv('CMC_API_KEY')
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"

async def get_global_metrics() -> Dict[str, Any]:
    """Get global market metrics from CMC"""
    if not CMC_API_KEY:
        raise Exception("CMC_API_KEY not configured")
    
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    url = f"{CMC_BASE_URL}/global-metrics/quotes/latest"
    data = await fetch_json(url, headers=headers, cache_key="cmc:global", cache_ttl=300)
    
    if 'data' not in data:
        raise Exception("Invalid CMC response")
    
    metrics = data['data']
    quote = metrics.get('quote', {}).get('USD', {})
    
    return {
        'market_cap': quote.get('total_market_cap', 0),
        'market_cap_change_pct_24h': quote.get('total_market_cap_yesterday_percentage_change', 0),
        'total_volume_24h': quote.get('total_volume_24h', 0),
        'active_cryptocurrencies': metrics.get('active_cryptocurrencies', 0),
        'btc_dominance': metrics.get('btc_dominance', 0),
        'eth_dominance': metrics.get('eth_dominance', 0)
    }

async def get_coin_quotes(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """Get coin quotes from CMC"""
    if not CMC_API_KEY:
        raise Exception("CMC_API_KEY not configured")
    
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    symbol_list = ','.join(symbols)
    url = f"{CMC_BASE_URL}/cryptocurrency/quotes/latest"
    params = {'symbol': symbol_list}
    
    data = await fetch_json(url, params=params, headers=headers, 
                          cache_key=f"cmc:quotes:{symbol_list}", cache_ttl=60)
    
    if 'data' not in data:
        raise Exception("Invalid CMC response")
    
    return data['data']
