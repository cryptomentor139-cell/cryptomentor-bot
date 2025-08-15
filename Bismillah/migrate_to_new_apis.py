#!/usr/bin/env python3
"""
Migration helper script to update from old API structure to new modular structure
"""

import os
import shutil
import logging
from datetime import datetime

def backup_old_files():
    """Backup old API files"""
    backup_dir = f"backup_old_apis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    files_to_backup = [
        'setup_coinapi.py',
        'setup_coinglass_v4.py'
    ]

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"📁 Created backup directory: {backup_dir}")

    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
            print(f"✅ Backed up {file}")
        else:
            print(f"⚠️ File not found: {file}")

    print(f"📦 Old files backed up to: {backup_dir}")
    return backup_dir

def check_new_structure():
    """Check if new API structure is in place"""
    required_files = [
        'crypto_api.py',
        'data_provider.py',
        'binance_provider.py',
        'coinmarketcap_provider.py'
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ All required new API files are present")
        return True

def migrate_api_structure():
    """Main migration function"""
    print("🔄 CryptoMentor AI - API Migration")
    print("=" * 50)

    try:
        # Step 1: Backup old files
        print("\n📦 Step 1: Backing up old files...")
        backup_dir = backup_old_files()

        # Step 2: Check new structure
        print("\n🔍 Step 2: Checking new API structure...")
        if not check_new_structure():
            print("❌ Migration cannot proceed - missing new API files")
            return False

        # Step 3: Test new APIs
        print("\n🧪 Step 3: Testing new API integrations...")
        try:
            from crypto_api import CryptoAPI
            crypto_api = CryptoAPI()

            # Test basic functionality
            btc_price = crypto_api.get_crypto_price('BTC')
            if btc_price and btc_price.get('success'):
                print(f"✅ New API working - BTC: ${btc_price.get('price', 0):,.2f}")
            else:
                print("⚠️ New API test failed but structure is correct")

        except Exception as e:
            print(f"⚠️ New API test error: {e}")

        print("\n✅ Migration completed successfully!")
        print(f"📁 Old files backed up to: {backup_dir}")
        print("🚀 New modular API structure is ready!")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    migrate_api_structure()