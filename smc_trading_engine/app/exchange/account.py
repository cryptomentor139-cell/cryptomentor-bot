from app.exchange.bitunix_client import BitunixClient


async def fetch_account_info():
    return await BitunixClient().get_account_info()
