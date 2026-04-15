from typing import Any, Dict, List

import httpx

from app.config.settings import settings


class BitunixClient:
    """
    Exchange-specific adapter.
    TODO: finalize exact endpoint paths/signing with live Bitunix spec.
    """

    def __init__(self):
        self.base_url = settings.bitunix_base_url.rstrip("/")

    async def _get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{self.base_url}{path}", params=params or {})
            resp.raise_for_status()
            return resp.json()

    async def get_candles(self, symbol: str, timeframe: str, limit: int) -> List[Dict[str, Any]]:
        return (await self._get("/api/v1/market/candles", {"symbol": symbol, "interval": timeframe, "limit": limit})).get("data", [])

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        return (await self._get("/api/v1/market/ticker", {"symbol": symbol})).get("data", {})

    async def get_open_position(self, symbol: str) -> Dict[str, Any] | None:
        positions = (await self._get("/api/v1/account/positions", {"symbol": symbol})).get("data", [])
        return positions[0] if positions else None

    async def get_account_info(self) -> Dict[str, Any]:
        return (await self._get("/api/v1/account/info")).get("data", {})
