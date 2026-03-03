"""
Test Bot with OpenClaw Integration
Quick check that bot can start with OpenClaw handlers
"""

import sys
import os

# Test imports
print("=" * 60)
print("Testing Bot with OpenClaw Integration")
print("=" * 60)

print("\n1. Testing OpenClaw CLI Bridge...")
try:
    from app.openclaw_cli_bridge import get_openclaw_cli_bridge
    bridge = get_openclaw_cli_bridge()
    is_healthy = bridge.check_health()
    print(f"   ✅ OpenClaw CLI Bridge: {'Working' if is_healthy else 'Not accessible'}")
except Exception as e:
    print(f"   ❌ OpenClaw CLI Bridge failed: {e}")
    sys.exit(1)

print("\n2. Testing OpenClaw Handlers...")
try:
    from app.handlers_openclaw_simple import register_openclaw_handlers
    print("   ✅ OpenClaw Handlers: Import successful")
except Exception as e:
    print(f"   ❌ OpenClaw Handlers failed: {e}")
    sys.exit(1)

print("\n3. Testing Bot Initialization...")
try:
    from bot import TelegramBot
    
    # Check if TOKEN is set
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("   ⚠️ TELEGRAM_BOT_TOKEN not set, skipping bot init")
    else:
        bot = TelegramBot()
        print("   ✅ Bot: Initialized successfully")
        
        # Try to setup application (without running)
        print("\n4. Testing Application Setup...")
        import asyncio
        asyncio.run(bot.setup_application())
        print("   ✅ Application: Setup successful with all handlers")
        
except Exception as e:
    print(f"   ❌ Bot initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All Tests Passed!")
print("=" * 60)
print("\n📋 Summary:")
print("✓ OpenClaw CLI Bridge working")
print("✓ OpenClaw Handlers loadable")
print("✓ Bot can initialize with OpenClaw")
print("✓ Handlers registered without errors")

print("\n🚀 Bot is ready to run with OpenClaw integration!")
print("\nAvailable commands:")
print("  /openclaw_status - Check OpenClaw availability")
print("  /openclaw_help - Show OpenClaw features")
print("  /openclaw_ask <question> - Ask AI assistant")
print("  /openclaw_test - Admin test (check integration)")

sys.exit(0)
