import os

def fix():
    path = r'd:\cryptomentorAI\Bismillah\app\bitunix_autotrade_client.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. place_order
    old1 = """        result = self._request('POST', '/api/v1/futures/trade/place_order',
                               body=body, signed=True)"""
    new1 = """        result = self._request('POST', '/api/v1/futures/trade/place_order',
                               body=body, signed=True, priority=True)"""
    content = content.replace(old1, new1)

    # 2. place_order_with_tpsl
    old2 = """        result = self._request('POST', '/api/v1/futures/trade/place_order',
                               body=body, signed=True)"""
    # Note: replace(old1, new1) might have already hit this if they are identical!
    
    # 3. modify_order
    old3 = """        result = self._request('POST', '/api/v1/futures/tpsl/position/modify_order',
                               body=body, signed=True)"""
    new3 = """        result = self._request('POST', '/api/v1/futures/tpsl/position/modify_order',
                               body=body, signed=True, priority=True)"""
    content = content.replace(old3, new3)

    # 4. Global Priority increase
    content = content.replace("_bitunix_rate_limiter = RateLimiter(10, 1.0)", "_bitunix_rate_limiter = RateLimiter(30, 1.0)")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed bitunix client")

fix()
