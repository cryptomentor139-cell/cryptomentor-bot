from app.core.context_builder import build_trade_context
from app.core.decision_engine import evaluate_trade_decision
from app.exchange.market_data import fetch_candles


async def scan_symbol(symbol: str, timeframe: str = "15m") -> dict:
    candles = await fetch_candles(symbol=symbol, timeframe=timeframe, limit=120)
    ctx = build_trade_context(symbol=symbol, candles=candles)
    decision = evaluate_trade_decision(ctx)
    return {"context": ctx.model_dump(), "decision": decision.model_dump()}
