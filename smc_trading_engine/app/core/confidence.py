def calculate_confidence_score(
    market_state: str,
    liquidity_sweep: bool,
    bos_confirmed: bool,
) -> float:
    score = 0.35
    if market_state.startswith("trending"):
        score += 0.2
    if liquidity_sweep:
        score += 0.25
    if bos_confirmed:
        score += 0.2
    return max(0.0, min(1.0, score))
