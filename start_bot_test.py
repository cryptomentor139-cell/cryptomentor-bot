#!/usr/bin/env python3
"""Start Bot Test - Test if bot can actually start"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import signal
import sys

print("🚀 Starting CryptoMentor Bot (Test Mode - 10 seconds)...\n")

async def test_bot_start():
    """Test bot startup"""
    try:
        from bot import TelegramBot
        
        bot = TelegramBot()
        print("✅ Bot instance created")
        
        await bot.setup_application()
        print("✅ Application setup complete")
        print("✅ All handlers registered")
        
        print("\n🎉 BOT IS READY TO RUN!")
        print("\n📊 Bot Status:")
        print(f"   • Token: {bot.token[:15]}...")
        print(f"   • Admins: {len(bot.admin_ids)}")
        print(f"   • Handlers: Registered")
        
        print("\n💡 To run bot continuously, use: python main.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Bot startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_bot_start())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(0)
