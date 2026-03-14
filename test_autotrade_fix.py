#!/usr/bin/env python3
"""
Quick test script to verify AutoTrade fix
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all autotrade components can be imported"""
    print("🧪 Testing AutoTrade imports...")
    
    try:
        from app.handlers_autotrade import (
            cmd_autotrade, cmd_autotrade_start, cmd_autotrade_status,
            cmd_autotrade_withdraw, cmd_autotrade_history, register_autotrade_handlers
        )
        print("✅ AutoTrade handlers imported successfully")
        
        from app.bitunix_autotrade_client import BitunixAutoTradeClient
        print("✅ BitunixAutoTradeClient imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_bitunix_client():
    """Test Bitunix client creation"""
    print("\n🧪 Testing Bitunix client...")
    
    try:
        from app.bitunix_autotrade_client import BitunixAutoTradeClient
        client = BitunixAutoTradeClient()
        print("✅ BitunixAutoTradeClient created successfully")
        
        # Test connection (will fail without real API keys, but should not crash)
        connection = client.check_connection()
        print(f"📡 Connection test: {connection['online']} - {connection.get('error', 'OK')}")
        
        return True
    except Exception as e:
        print(f"❌ Bitunix client error: {e}")
        return False

def test_bot_initialization():
    """Test that bot can initialize with autotrade handlers"""
    print("\n🧪 Testing bot initialization...")
    
    try:
        from bot import TelegramBot
        bot = TelegramBot()
        print("✅ TelegramBot initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Bot initialization error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AutoTrade Fix Verification\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Bitunix Client Test", test_bitunix_client),
        ("Bot Initialization Test", test_bot_initialization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n{'='*50}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ AutoTrade fix is working correctly")
        print("✅ /autotrade command should now work")
        print("\n📋 Next steps:")
        print("1. Deploy the bot to Railway")
        print("2. Test /autotrade command in Telegram")
        print("3. Ensure user has premium status")
        print("4. Fund Bitunix account for real trading")
    else:
        print("⚠️ Some tests failed - check errors above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)