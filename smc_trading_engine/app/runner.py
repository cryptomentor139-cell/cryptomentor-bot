import asyncio

from app.services.scheduler import scan_loop


def run() -> None:
    asyncio.run(scan_loop())
