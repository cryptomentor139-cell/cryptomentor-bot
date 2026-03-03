#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test bot startup locally with .env file
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Checking environment variables...")
print(f"✅ TELEGRAM_BOT_TOKEN: {'SET' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ MISSING'}")
print(f"✅ ADMIN1: {os.getenv('ADMIN1', 'NOT SET')}")
print(f"✅ ADMIN2: {os.getenv('ADMIN2', 'NOT SET')}")

if not os.getenv('TELEGRAM_BOT_TOKEN'):
    print("\n❌ TELEGRAM_BOT_TOKEN is missing!")
    print("Please check your .env file")
    exit(1)

print("\n🚀 Starting bot...")

import bot
import asyncio

# Create bot instance
telegram_bot = bot.TelegramBot()

# Run bot for 5 seconds to test startup
async def test_run():
    try:
        await telegram_bot.setup_application()
        await telegram_bot.application.initialize()
        print("\n✅ Bot initialized successfully!")
        print("✅ All handlers registered")
        print("\n🎉 Bot startup test PASSED!")
        return True
    except Exception as e:
        print(f"\n❌ Bot startup test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

result = asyncio.run(test_run())
exit(0 if result else 1)
