import os
import re

def optimize_signals():
    file_path = r'd:\cryptomentorAI\website-backend\app\routes\signals.py'
    if not os.path.exists(file_path): return
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add Cache Header
    if '_CONFLUENCE_CACHE = {}' not in content:
        content = content.replace(
            "import logging",
            "import logging\nimport time as _v_time"
        )
        content = content.replace(
            "_signal_cache: Dict[str, Dict[str, Any]] = {}",
            "_signal_cache: Dict[str, Dict[str, Any]] = {}\n_CONFLUENCE_CACHE = {} # (sym, risk): (expiry, sig)"
        )

    # 2. Apply cache in generate_confluence_signals
    old_generate = """async def generate_confluence_signals(
    symbol: str,
    user_risk_pct: float = 0.5
) -> Optional[Dict[str, Any]]:
    \"\"\"
    Generate a confluence-validated trading signal for symbol if 2+ factors align.
...
    Returns: signal dict if confluent, or None if weak setup
    \"\"\"
    symbol_upper = symbol.upper()

    # Get config for user's risk level (clamped to [0.5, 100.0])
    user_risk_pct = _normalize_risk_pct(user_risk_pct, default=1.0)
    config = _risk_profile(user_risk_pct)
    min_confidence = config["min_confidence"]"""

    # We need a more robust match
    pattern = r"async def generate_confluence_signals.*?symbol_upper = symbol\.upper\(\).*?min_confidence = config\[\"min_confidence\"\]"
    
    new_logic = """    symbol_upper = symbol.upper()
    user_risk_pct = _normalize_risk_pct(user_risk_pct, default=1.0)
    
    # Check cache
    now = _v_time.time()
    risk_bucket = round(user_risk_pct, 2)
    cache_key = (symbol_upper, risk_bucket)
    exp, cached_sig = _CONFLUENCE_CACHE.get(cache_key, (0, None))
    if cached_sig is not None and now < exp:
        return cached_sig

    # Get config for user's risk level (clamped to [0.5, 100.0])
    config = _risk_profile(user_risk_pct)
    min_confidence = config["min_confidence"]"""

    if "symbol_upper = symbol.upper()" in content:
        # Simple string replace for safety
        content = content.replace(
            "    symbol_upper = symbol.upper()\n\n    # Get config for user's risk level (clamped to [0.5, 100.0])\n    user_risk_pct = _normalize_risk_pct(user_risk_pct, default=1.0)\n    config = _risk_profile(user_risk_pct)\n    min_confidence = config[\"min_confidence\"]",
            new_logic
        )

    # 3. Store in cache at the end of generate_confluence_signals
    store_logic = """    if signal:
        _CONFLUENCE_CACHE[cache_key] = (now + 60, signal)
    
    return signal"""
    
    # Find the end of generate_confluence_signals
    if "return signal" in content and "_CONFLUENCE_CACHE[cache_key]" not in content:
        content = content.replace("    return signal", store_logic)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Optimized signals confluence logic")

optimize_signals()
