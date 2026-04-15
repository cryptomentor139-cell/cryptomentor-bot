from app.config.thresholds import thresholds

from .models import TradeDecision, TradeContext


def evaluate_trade_decision(ctx: TradeContext) -> TradeDecision:
    if ctx.confidence_score < thresholds.min_confidence_score:
        return TradeDecision(
            symbol=ctx.symbol,
            action="HOLD",
            confidence_score=ctx.confidence_score,
            reason="Confidence below threshold",
        )

    if ctx.market_state == "trending_up":
        action = "OPEN_LONG"
    elif ctx.market_state == "trending_down":
        action = "OPEN_SHORT"
    else:
        action = "HOLD"

    return TradeDecision(
        symbol=ctx.symbol,
        action=action,
        confidence_score=ctx.confidence_score,
        reason=f"Decision based on market_state={ctx.market_state}",
    )
