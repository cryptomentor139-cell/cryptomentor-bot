def validate_symbol(symbol: str) -> str:
    normalized = (symbol or "").strip().upper()
    if not normalized.endswith("USDT"):
        raise ValueError("Only USDT pairs are supported in v1")
    return normalized
