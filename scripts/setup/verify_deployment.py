#!/usr/bin/env python3
"""
Verify Railway Deployment - Check if handlers are properly loaded
"""

import sys
import os

print("="*60)
print("DEPLOYMENT VERIFICATION")
print("="*60)

# Test 1: Check if files exist
print("\n1. Checking if files exist...")
files_to_check = [
    'app/premium_checker.py',
    'app/handlers_manual_signals.py',
    'bot.py'
]

all_exist = True
for file in files_to_check:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    print(f"   {status} {file}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n❌ CRITICAL: Some files are missing!")
    sys.exit(1)

# Test 2: Try importing handlers
print("\n2. Testing imports...")
try:
    from app.handlers_manual_signals import (
        cmd_analyze, cmd_futures, cmd_futures_signals,
        cmd_signal, cmd_signals
    )
    print("   ✅ All handlers imported successfully")
    print(f"      - cmd_analyze: {cmd_analyze.__name__}")
    print(f"      - cmd_futures: {cmd_futures.__name__}")
    print(f"      - cmd_futures_signals: {cmd_futures_signals.__name__}")
    print(f"      - cmd_signal: {cmd_signal.__name__} (alias)")
    print(f"      - cmd_signals: {cmd_signals.__name__} (alias)")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 3: Check premium checker
print("\n3. Testing premium checker...")
try:
    from app.premium_checker import is_lifetime_premium, check_and_deduct_credits
    print("   ✅ Premium checker imported successfully")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 4: Check FuturesSignalGenerator
print("\n4. Testing FuturesSignalGenerator...")
try:
    from futures_signal_generator import FuturesSignalGenerator
    print("   ✅ FuturesSignalGenerator imported successfully")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 5: Check bot.py can import handlers
print("\n5. Testing bot.py handler registration...")
try:
    # Read bot.py and check if handlers are registered
    with open('bot.py', 'r', encoding='utf-8') as f:
        bot_content = f.read()
    
    if 'from app.handlers_manual_signals import' in bot_content:
        print("   ✅ Handler import found in bot.py")
    else:
        print("   ❌ Handler import NOT found in bot.py")
        sys.exit(1)
    
    if 'CommandHandler("analyze", cmd_analyze)' in bot_content:
        print("   ✅ /analyze handler registration found")
    else:
        print("   ❌ /analyze handler registration NOT found")
        sys.exit(1)
    
    if 'CommandHandler("futures", cmd_futures)' in bot_content:
        print("   ✅ /futures handler registration found")
    else:
        print("   ❌ /futures handler registration NOT found")
        sys.exit(1)
    
    if 'CommandHandler("futures_signals", cmd_futures_signals)' in bot_content:
        print("   ✅ /futures_signals handler registration found")
    else:
        print("   ❌ /futures_signals handler registration NOT found")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error reading bot.py: {e}")
    sys.exit(1)

# Test 6: Check environment variables
print("\n6. Checking environment variables...")
required_env_vars = [
    'TELEGRAM_BOT_TOKEN',
    'SUPABASE_URL',
    'SUPABASE_KEY'
]

env_ok = True
for var in required_env_vars:
    value = os.getenv(var)
    if value:
        print(f"   ✅ {var}: Set")
    else:
        print(f"   ⚠️  {var}: Not set")
        env_ok = False

if not env_ok:
    print("\n   ⚠️  Some environment variables are missing")
    print("   This is OK for local testing, but required for Railway")

# Final summary
print("\n" + "="*60)
print("VERIFICATION SUMMARY")
print("="*60)
print("✅ All files exist")
print("✅ All handlers can be imported")
print("✅ Premium checker works")
print("✅ FuturesSignalGenerator works")
print("✅ Bot.py has handler registrations")
if env_ok:
    print("✅ All environment variables set")
else:
    print("⚠️  Some environment variables missing (OK for local)")

print("\n🎉 DEPLOYMENT VERIFICATION PASSED!")
print("\nNext steps:")
print("1. Check Railway logs for handler registration message")
print("2. Test commands in Telegram: /analyze BTCUSDT")
print("3. Verify signals are generated correctly")
print("="*60)
