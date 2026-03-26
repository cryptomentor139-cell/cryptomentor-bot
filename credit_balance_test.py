"""
Script untuk simulasi deposit USDT ke WL#1 (untuk testing).
Dalam production, ini dilakukan otomatis oleh deposit_monitor.py
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
    wl_id = "36741b13-c92d-46d8-aa2f-1acdaefee634"
    amount = 50.0  # $50 USDT untuk test (cukup untuk 5 bulan @ $10/bulan)
    tx_hash = "0xTEST_TRANSACTION_HASH_12345"  # Fake tx hash untuk testing
    block_number = 12345678
    
    print(f"Simulating deposit to WL#1:")
    print(f"  WL_ID: {wl_id}")
    print(f"  Amount: ${amount} USDT")
    print(f"  TX Hash: {tx_hash}")
    print()
    
    manager = LicenseManager()
    
    try:
        # Credit balance
        credited = await manager.credit_balance(
            wl_id=wl_id,
            amount=amount,
            tx_hash=tx_hash,
            block_number=block_number
        )
        
        if credited:
            print("✅ Balance credited successfully!")
            print()
            
            # Get updated license info
            license_row = await manager.get_license(wl_id)
            print("Updated license info:")
            print(f"  Balance: ${license_row.get('balance_usdt', 0):.2f} USDT")
            print(f"  Status: {license_row.get('status')}")
            print(f"  Expires At: {license_row.get('expires_at')}")
        else:
            print("⚠️ Transaction already processed (idempotent)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
