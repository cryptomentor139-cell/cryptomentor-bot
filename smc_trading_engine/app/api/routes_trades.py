from fastapi import APIRouter

from app.services.scan_service import scan_symbol

router = APIRouter(tags=["trades"])


@router.post("/trades/scan/{symbol}")
async def scan(symbol: str):
    return await scan_symbol(symbol=symbol.upper())
