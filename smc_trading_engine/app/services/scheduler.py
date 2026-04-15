import asyncio

from app.config.pairs import DEFAULT_PAIRS
from app.config.settings import settings
from app.services.scan_service import scan_symbol


async def scan_loop():
    while True:
        for symbol in DEFAULT_PAIRS:
            await scan_symbol(symbol=symbol)
        await asyncio.sleep(settings.scan_interval_seconds)
