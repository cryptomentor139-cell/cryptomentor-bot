#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test bot startup without actually running it
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    print("=" * 60)
    print("🧪 Testing Bot Startup Components")
    print("=" * 60)
    print()
    
    tests = []
    
    # Test 1: Import bot module
    print("1️⃣ Testing bot.py import...")
    try:
        import bot
        print("   ✅ bot.py imported successfully")
        tests.append(True)
    except Exception as e:
        print(f"   ❌ Failed to import bot.py: {e}")
        tests.append(False)
    
    # Test 2: Import menu handlers
    print("\n2️⃣ Testing menu_handlers.py import...")
    try:
        import menu_handlers
        print("   ✅ menu_handlers.py imported successfully")
        tests.append(True)
    except Exception as e:
        print(f"   ❌ Failed to import menu_handlers.py: {e}")
        tests.append(False)
    
    # Test 3: Import menu system
    print("\n3️⃣ Testing menu_system.py import...")
    try:
        import menu_system
        print("   ✅ menu_system.py imported successfully")
        tests.append(True)
    except Exception as e:
        print(f"   ❌ Failed to import menu_system.py: {e}")
        tests.append(False)
    
    # Test 4: Import database
    print("\n4️⃣ Testing database.py import...")
    try:
        import database
        print("   ✅ database.py imported successfully")
        tests.append(True)
    except Exception as e:
        print(f"   ❌ Failed to import database.py: {e}")
        tests.append(False)
    
    # Test 5: Check .env file
    print("\n5️⃣ Checking .env file...")
    if os.path.exists('.env'):
        print("   ✅ .env file exists")
        
        # Check for critical variables
        from dotenv import load_dotenv
        load_dotenv()
        
        critical_vars = [
            'TELEGRAM_BOT_TOKEN',
            'SUPABASE_URL',
            'SUPABASE_KEY',
        ]
        
        missing = []
        for var in critical_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print(f"   ⚠️  Missing variables: {', '.join(missing)}")
            tests.append(False)
        else:
            print("   ✅ All critical variables present")
            tests.append(True)
    else:
        print("   ❌ .env file not found")
        tests.append(False)
    
    # Test 6: Check bot instance creation
    print("\n6️⃣ Testing bot instance creation...")
    try:
        from bot import CryptoMentorBot
        print("   ✅ CryptoMentorBot class accessible")
        tests.append(True)
    except Exception as e:
        print(f"   ❌ Failed to access CryptoMentorBot: {e}")
        tests.append(False)
    
    # Summary
    print()
    print("=" * 60)
    passed = sum(tests)
    total = len(tests)
    print(f"📊 Test Results: {passed}/{total} passed")
    print("=" * 60)
    
    if passed == total:
        print()
        print("✅ All tests passed! Bot is ready to run.")
        print("🚀 Start bot with: python bot.py")
        return True
    else:
        print()
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
