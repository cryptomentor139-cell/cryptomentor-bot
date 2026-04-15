from app.core.models import OrderRequest, OrderResult


async def place_order(request: OrderRequest) -> OrderResult:
    # TODO: wire to signed Bitunix trading endpoints.
    return OrderResult(success=False, symbol=request.symbol, side=request.side, message="Execution adapter not wired yet")


async def close_position(symbol: str) -> OrderResult:
    # TODO: wire to signed Bitunix close endpoint.
    return OrderResult(success=False, symbol=symbol, side="", message="Close adapter not wired yet")
