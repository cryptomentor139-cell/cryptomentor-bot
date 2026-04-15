from .confidence import calculate_confidence_score
from .entry_zone import detect_entry_zone
from .liquidity import detect_liquidity_sweep
from .market_state import classify_market_state
from .models import TradeContext
from .structure import confirm_break_of_structure


def build_trade_context(symbol: str, candles):
    market_state = classify_market_state(candles)
    liquidity_sweep = detect_liquidity_sweep(candles)
    bos_confirmed = confirm_break_of_structure(candles)
    zone_low, zone_high = detect_entry_zone(candles)
    confidence_score = calculate_confidence_score(
        market_state=market_state,
        liquidity_sweep=liquidity_sweep,
        bos_confirmed=bos_confirmed,
    )
    return TradeContext(
        symbol=symbol,
        market_state=market_state,
        liquidity_sweep=liquidity_sweep,
        bos_confirmed=bos_confirmed,
        confidence_score=confidence_score,
        entry_zone_low=zone_low,
        entry_zone_high=zone_high,
    )
