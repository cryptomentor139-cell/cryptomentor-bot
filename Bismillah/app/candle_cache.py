"""
Candle Cache System
Prevents redundant API calls by caching candle data
"""

import asyncio
import time
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# Global cache: {(symbol, timeframe, limit): (data, timestamp)}
_candle_cache: Dict[Tuple[str, str, int], Tuple[list, float]] = {}
_inflight_fetches: Dict[Tuple[str, str, int], asyncio.Future] = {}

# Cache TTL in seconds
CACHE_TTL = 10  # 10 seconds cache

# Semaphore to limit concurrent API calls (max 10 concurrent)
_api_semaphore = asyncio.Semaphore(10)


async def get_candles_cached(fetch_func, symbol: str, timeframe: str, limit: int = 100):
    """
    Get candles with caching to reduce API load.
    
    Args:
        fetch_func: Async function to fetch candles (e.g., client.get_klines)
        symbol: Trading pair symbol
        timeframe: Candle timeframe
        limit: Number of candles
        
    Returns:
        List of candles or None if failed
    """
    cache_key = (symbol, timeframe, limit)
    now = time.time()
    
    # Check cache first
    if cache_key in _candle_cache:
        data, timestamp = _candle_cache[cache_key]
        age = now - timestamp
        
        if age < CACHE_TTL:
            logger.debug(f"[Cache HIT] {symbol} {timeframe} (age: {age:.1f}s)")
            return data

    inflight = _inflight_fetches.get(cache_key)
    if inflight is not None:
        logger.debug(f"[Cache WAIT] {symbol} {timeframe} - awaiting in-flight fetch")
        try:
            return await asyncio.shield(inflight)
        except Exception as e:
            logger.error(f"[Cache] In-flight fetch failed for {symbol} {timeframe}: {e}")
            if cache_key in _candle_cache:
                stale_data, _ = _candle_cache[cache_key]
                logger.warning(f"[Cache STALE] {symbol} {timeframe} - using stale cache after in-flight failure")
                return stale_data
            return None

    loop = asyncio.get_running_loop()
    inflight = loop.create_future()
    _inflight_fetches[cache_key] = inflight
    
    # Cache miss or expired - fetch with semaphore
    try:
        async with _api_semaphore:
            # Another request may have refreshed the cache while we were waiting.
            now = time.time()
            if cache_key in _candle_cache:
                data, timestamp = _candle_cache[cache_key]
                age = now - timestamp
                if age < CACHE_TTL:
                    logger.debug(f"[Cache HIT-AFTER-WAIT] {symbol} {timeframe} (age: {age:.1f}s)")
                    inflight.set_result(data)
                    return data

            data = await fetch_func(symbol, timeframe, limit)

            # Update cache even for empty list so callers share the same short-lived result.
            _candle_cache[cache_key] = (data, time.time())
            logger.debug(f"[Cache MISS] {symbol} {timeframe} - fetched and cached")
            inflight.set_result(data)
            return data

    except Exception as e:
        logger.error(f"[Cache] Failed to fetch {symbol} {timeframe}: {e}")
        if cache_key in _candle_cache:
            stale_data, _ = _candle_cache[cache_key]
            logger.warning(f"[Cache STALE] {symbol} {timeframe} - using stale cache after fetch failure")
            inflight.set_result(stale_data)
            return stale_data
        inflight.set_result(None)
        return None
    finally:
        _inflight_fetches.pop(cache_key, None)


def clear_cache():
    """Clear all cached candles (useful for testing)"""
    global _candle_cache
    _candle_cache.clear()
    logger.info("[Cache] Cleared all cached candles")


def get_cache_stats() -> dict:
    """Get cache statistics"""
    now = time.time()
    total = len(_candle_cache)
    fresh = sum(1 for _, (_, ts) in _candle_cache.items() if (now - ts) < CACHE_TTL)
    stale = total - fresh
    
    return {
        "total_entries": total,
        "fresh_entries": fresh,
        "stale_entries": stale,
        "cache_ttl": CACHE_TTL,
        "max_concurrent": _api_semaphore._value,
    }
