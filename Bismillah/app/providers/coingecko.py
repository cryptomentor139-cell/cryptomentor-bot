
from typing import Dict, Any, List
from app.providers.http import fetch_json

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

async def get_global_metrics() -> Dict[str, Any]:
    """Get global metrics from CoinGecko as fallback"""
    url = f"{COINGECKO_BASE_URL}/global"
    data = await fetch_json(url, cache_key="cg:global", cache_ttl=300)
    
    if 'data' not in data:
        raise Exception("Invalid CoinGecko response")
    
    global_data = data['data']
    
    return {
        'market_cap': global_data.get('total_market_cap', {}).get('usd', 0),
        'market_cap_change_pct_24h': global_data.get('market_cap_change_percentage_24h_usd', 0),
        'total_volume_24h': global_data.get('total_volume', {}).get('usd', 0),
        'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
        'btc_dominance': global_data.get('market_cap_percentage', {}).get('btc', 0),
        'eth_dominance': global_data.get('market_cap_percentage', {}).get('eth', 0)
    }
