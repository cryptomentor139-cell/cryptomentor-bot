#!/usr/bin/env python3
"""
Fix .env file - Add missing Conway wallet address
"""

import os
from dotenv import load_dotenv, set_key

# Load current .env
load_dotenv()

# Check current status
conway_api_key = os.getenv('CONWAY_API_KEY')
conway_wallet = os.getenv('CONWAY_WALLET_ADDRESS')

print("="*70)
print("CONWAY ENVIRONMENT FIX")
print("="*70)

print(f"\nCurrent Status:")
print(f"CONWAY_API_KEY: {'SET ✅' if conway_api_key else 'MISSING ❌'}")
print(f"CONWAY_WALLET_ADDRESS: {'SET ✅' if conway_wallet else 'MISSING ❌'}")

if not conway_wallet:
    print("\n⚠️ CONWAY_WALLET_ADDRESS is missing!")
    print("\nOptions:")
    print("1. Get wallet address from Conway dashboard")
    print("2. Use platform master wallet (recommended)")
    print("3. Generate new wallet via Conway API")
    
    # For now, use a placeholder that will be replaced
    # In production, this should be the platform's master wallet
    placeholder_wallet = "0x0000000000000000000000000000000000000000"
    
    print(f"\n📝 Adding placeholder wallet address...")
    print(f"   Address: {placeholder_wallet}")
    print(f"\n⚠️ IMPORTANT: Replace this with your actual Conway wallet address!")
    print(f"   Get it from: https://conway.tech/dashboard")
    
    # Add to .env
    env_file = '.env'
    set_key(env_file, 'CONWAY_WALLET_ADDRESS', placeholder_wallet)
    
    print(f"\n✅ Added CONWAY_WALLET_ADDRESS to .env")
    print(f"\n📋 Next Steps:")
    print(f"1. Go to https://conway.tech/dashboard")
    print(f"2. Copy your wallet address")
    print(f"3. Update .env file:")
    print(f"   CONWAY_WALLET_ADDRESS=<your_actual_address>")
else:
    print(f"\n✅ All Conway environment variables are set!")
    print(f"   Wallet: {conway_wallet}")

print("\n" + "="*70)
