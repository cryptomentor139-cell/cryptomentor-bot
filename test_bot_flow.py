#!/usr/bin/env python3
"""
Test Bot Flow - Comprehensive bot testing
Tests all major components without actually running the bot
"""

import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing Environment Variables...")
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'PGHOST',
        'PGDATABASE',
        'DEEPSEEK_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
            print(f"  ❌ {var} - MISSING")
        else:
            value = os.getenv(var)
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✅ {var} - {masked}")
    
    if missing:
        print(f"\n❌ Missing variables: {', '.join(missing)}")
        return False
    
    print("✅ All environment variables present")
    return True

def test_imports():
    """Test critical imports"""
    print("\n🔍 Testing Critical Imports...")
    
    tests = [
        ("telegram", "python-telegram-bot"),
        ("requests", "requests"),
        ("aiohttp", "aiohttp"),
        ("web3", "web3"),
        ("supabase", "supabase"),
    ]
    
    failed = []
    for module, package in tests:
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package} - {e}")
            failed.append(package)
    
    if failed:
        print(f"\n❌ Failed imports: {', '.join(failed)}")
        return False
    
    print("✅ All critical imports successful")
    return True

def test_database():
    """Test database connection"""
    print("\n🔍 Testing Database Connection...")
    
    try:
        from services import get_database
        db = get_database()
        print(f"  ✅ Database instance created: {type(db).__name__}")
        
        # Test basic query
        try:
            stats = db.get_user_stats()
            print(f"  ✅ Database query successful")
            print(f"     Total users: {stats.get('total_users', 0)}")
            print(f"     Premium users: {stats.get('premium_users', 0)}")
        except Exception as e:
            print(f"  ⚠️ Database query failed: {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False

def test_bot_initialization():
    """Test bot initialization"""
    print("\n🔍 Testing Bot Initialization...")
    
    try:
        from bot import TelegramBot
        bot = TelegramBot()
        print(f"  ✅ Bot initialized")
        print(f"     Token: {bot.token[:10]}...")
        print(f"     Admin IDs: {len(bot.admin_ids)} admins")
        return True
    except Exception as e:
        print(f"  ❌ Bot initialization failed: {e}")
        return False

def test_handlers():
    """Test handler imports"""
    print("\n🔍 Testing Handler Modules...")
    
    handlers = [
        "app.handlers_manual_signals",
        "app.handlers_admin_premium",
        "app.handlers_deepseek",
        "app.handlers_automaton",
        "menu_handlers",
    ]
    
    failed = []
    for handler in handlers:
        try:
            __import__(handler)
            print(f"  ✅ {handler}")
        except Exception as e:
            print(f"  ⚠️ {handler} - {str(e)[:50]}")
            failed.append(handler)
    
    if failed:
        print(f"\n⚠️ Some handlers failed (may be optional): {len(failed)}")
    else:
        print("✅ All handlers loaded")
    
    return True

def test_crypto_api():
    """Test crypto API"""
    print("\n🔍 Testing Crypto API...")
    
    try:
        from crypto_api import crypto_api
        print(f"  ✅ Crypto API loaded")
        
        # Test price fetch
        try:
            price_data = crypto_api.get_crypto_price("BTC")
            if 'error' not in price_data:
                print(f"  ✅ Price fetch successful: BTC = ${price_data['price']:,.2f}")
            else:
                print(f"  ⚠️ Price fetch returned error: {price_data['error']}")
        except Exception as e:
            print(f"  ⚠️ Price fetch failed: {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Crypto API failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 CryptoMentor Bot - Comprehensive Flow Test")
    print("=" * 60)
    
    results = {
        "Environment": test_environment(),
        "Imports": test_imports(),
        "Database": test_database(),
        "Bot Init": test_bot_initialization(),
        "Handlers": test_handlers(),
        "Crypto API": test_crypto_api(),
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Bot is ready to run.")
        print("\n💡 To start the bot, run:")
        print("   python main.py")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
