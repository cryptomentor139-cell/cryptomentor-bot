from app.core.models import OrderRequest
from app.exchange.execution import close_position, place_order


async def execute_decision(symbol: str, action: str, size: float, leverage: int):
    if action == "OPEN_LONG":
        req = OrderRequest(symbol=symbol, side="BUY", size=size, leverage=leverage)
        return await place_order(req)
    if action == "OPEN_SHORT":
        req = OrderRequest(symbol=symbol, side="SELL", size=size, leverage=leverage)
        return await place_order(req)
    if action == "CLOSE":
        return await close_position(symbol)
    return None
