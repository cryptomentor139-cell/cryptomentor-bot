"""
Script untuk register Whitelabel #1 untuk testing.
"""
import asyncio
import os
import sys

# Add license_server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'license_server'))

from dotenv import load_dotenv
load_dotenv('license_server/.env')

from license_manager import LicenseManager


async def main():
    # WL#1 credentials
    ADMIN_TELEGRAM_ID = 801937545  # Admin1
    MONTHLY_FEE = 10.0  # $10 per bulan (TEST MODE)

    print(f"Registering Whitelabel #1:")
    print(f"  Admin Telegram ID: {ADMIN_TELEGRAM_ID}")
    print(f"  Monthly Fee: ${MONTHLY_FEE}")
    print()

    manager = LicenseManager()
    
    try:
        result = await manager.register_wl(
            admin_telegram_id=ADMIN_TELEGRAM_ID,
            monthly_fee=MONTHLY_FEE,
        )

        print("=" * 70)
        print("✅ WHITELABEL #1 REGISTERED SUCCESSFULLY")
        print("=" * 70)
        print(f"WL_ID:           {result['wl_id']}")
        print(f"SECRET_KEY:      {result['secret_key']}")
        print(f"DEPOSIT_ADDRESS: {result['deposit_address']}")
        print()
        print("Copy ke Whitelabel #1/.env:")
        print(f"  WL_ID={result['wl_id']}")
        print(f"  WL_SECRET_KEY={result['secret_key']}")
        print(f"  LICENSE_API_URL=http://localhost:8080")
        print()
        print(f"Deposit address untuk top-up (BSC USDT BEP-20):")
        print(f"  {result['deposit_address']}")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
