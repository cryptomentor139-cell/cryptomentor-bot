
import httpx
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

# Simple in-memory cache
_cache: Dict[str, Dict[str, Any]] = {}

async def fetch_json(url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, 
                    timeout: int = 10, cache_key: Optional[str] = None, 
                    cache_ttl: int = 60) -> Dict[str, Any]:
    """Fetch JSON with caching and retry"""
    
    # Check cache
    if cache_key and cache_key in _cache:
        cached = _cache[cache_key]
        if datetime.now() < cached['expires']:
            return cached['data']
    
    # Prepare request
    headers = headers or {}
    params = params or {}
    
    # Retry logic
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Cache result
                if cache_key:
                    _cache[cache_key] = {
                        'data': data,
                        'expires': datetime.now() + timedelta(seconds=cache_ttl)
                    }
                
                return data
                
        except Exception as e:
            if attempt == 2:  # Last attempt
                raise e
            await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
    
    raise Exception("Max retries exceeded")
