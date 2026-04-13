import sys
import os
import time

def apply_client_optimizations():
    file_path = r'd:\cryptomentorAI\Bismillah\app\bitunix_autotrade_client.py'
    if not os.path.exists(file_path): return
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Bypass for orders in _request
    if 'priority: bool = False' not in content:
        content = content.replace(
            'def _request(self, method: str, endpoint: str, params: Dict = None, body: Dict = None, signed: bool = False, _retry: int = 0) -> Dict:',
            'def _request(self, method: str, endpoint: str, params: Dict = None, body: Dict = None, signed: bool = False, _retry: int = 0, priority: bool = False) -> Dict:'
        )
        
    old_rate_limit = """        # Smart Proxy rotation
        proxy_url = self._get_healthy_proxy()
        
        # Apply 10req/sec per IP rate limits BEFORE calling
        proxy_key = proxy_url if proxy_url else "LOCAL_IP"
        _bitunix_rate_limiter.wait(proxy_key)"""
        
    new_rate_limit = """        # High-priority requests (orders) skip the rate limiter wait
        # to ensure the fastest possible execution.
        if not priority:
            # Smart Proxy rotation
            proxy_url = self._get_healthy_proxy()
            
            # Apply rate limits BEFORE calling
            proxy_key = proxy_url if proxy_url else "LOCAL_IP"
            _bitunix_rate_limiter.wait(proxy_key)
        else:
            # Orders always use LOCAL_IP for maximum speed unless a gateway is active
            proxy_url = None
            # print(f"[Bitunix:Priority] {method} {endpoint} bypassing rate limiter")"""

    if old_rate_limit in content:
        content = content.replace(old_rate_limit, new_rate_limit)

    # Priority flags for placement
    content = content.replace(
        "return self._request('POST', '/api/v1/futures/trade/place_order', body=body, signed=True)",
        "return self._request('POST', '/api/v1/futures/trade/place_order', body=body, signed=True, priority=True)"
    )
    content = content.replace(
        "return self._request('POST', '/api/v1/futures/tpsl/position/modify_order', body=body, signed=True)",
        "return self._request('POST', '/api/v1/futures/tpsl/position/modify_order', body=body, signed=True, priority=True)"
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Optimized BitunixAutoTradeClient")

def apply_service_cache():
    file_path = r'd:\cryptomentorAI\website-backend\app\services\bitunix.py'
    if not os.path.exists(file_path): return
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '_ACCOUNT_CACHE' not in content:
        header = """_CLIENT_CACHE: Dict[int, BitunixAutoTradeClient] = {}"""
        new_header = """_CLIENT_CACHE: Dict[int, BitunixAutoTradeClient] = {}
_ACCOUNT_CACHE = {} # tg_id: (expiry, data)
_POSITIONS_CACHE = {}
import time as _time"""
        content = content.replace(header, new_header)

    old_account = """async def fetch_account(telegram_id: int) -> Dict[str, Any]:
    client = _client_for(telegram_id)
    return await asyncio.to_thread(client.get_account_info)"""
    
    new_account = """async def fetch_account(telegram_id: int) -> Dict[str, Any]:
    now = _time.time()
    exp, data = _ACCOUNT_CACHE.get(telegram_id, (0, {}))
    if now < exp: return data
    
    client = _client_for(telegram_id)
    res = await asyncio.to_thread(client.get_account_info)
    if res.get("success"):
        _ACCOUNT_CACHE[telegram_id] = (now + 3, res)
    return res"""

    if old_account in content:
        content = content.replace(old_account, new_account)

    old_positions = """async def fetch_positions(telegram_id: int) -> Dict[str, Any]:
    client = _client_for(telegram_id)
    return await asyncio.to_thread(client.get_positions)"""
    
    new_positions = """async def fetch_positions(telegram_id: int) -> Dict[str, Any]:
    now = _time.time()
    exp, data = _POSITIONS_CACHE.get(telegram_id, (0, {}))
    if now < exp: return data
    
    client = _client_for(telegram_id)
    res = await asyncio.to_thread(client.get_positions)
    if res.get("success"):
        _POSITIONS_CACHE[telegram_id] = (now + 3, res)
    return res"""

    if old_positions in content:
        content = content.replace(old_positions, new_positions)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Optimized bitunix service cache")

apply_client_optimizations()
apply_service_cache()
