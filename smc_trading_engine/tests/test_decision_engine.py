from app.core.decision_engine import evaluate_trade_decision
from app.core.models import TradeContext


def test_hold_when_low_confidence():
    ctx = TradeContext(
        symbol="BTCUSDT",
        market_state="trending_up",
        liquidity_sweep=False,
        bos_confirmed=False,
        confidence_score=0.2,
        entry_zone_low=1.0,
        entry_zone_high=2.0,
    )
    decision = evaluate_trade_decision(ctx)
    assert decision.action == "HOLD"
