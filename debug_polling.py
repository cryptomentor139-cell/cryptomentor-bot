#!/usr/bin/env python3
"""
Debug script to check if bot is actually receiving updates
"""
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

load_dotenv()

# Simple handler that logs everything
async def debug_handler(update, context):
    print(f"🎯 RECEIVED UPDATE!")
    print(f"   Update ID: {update.update_id}")
    if update.message:
        print(f"   Message: {update.message.text}")
        print(f"   From: {update.message.from_user.first_name}")
        await update.message.reply_text("✅ Bot is working! Received your message.")
    print("="*60)

async def test_polling():
    """Test if polling actually works"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    print("🔍 Starting minimal test bot...")
    print("   This will test if polling works at all")
    print("="*60)
    
    # Create minimal application
    app = Application.builder().token(token).build()
    
    # Add simple handlers
    app.add_handler(MessageHandler(filters.ALL, debug_handler))
    
    # Initialize
    await app.initialize()
    await app.start()
    
    print("✅ Test bot started")
    print("🔄 Starting polling...")
    
    # Start polling
    await app.updater.start_polling(
        poll_interval=1.0,
        timeout=10,
        drop_pending_updates=False
    )
    
    print("✅ Polling active")
    print("📱 Send a message to the bot now!")
    print("   Bot: @Subridujdirdsjbot")
    print("   Waiting for updates...")
    print("="*60)
    
    # Wait for 60 seconds
    try:
        await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    
    # Cleanup
    await app.updater.stop()
    await app.stop()
    await app.shutdown()
    
    print("👋 Test complete")

if __name__ == "__main__":
    asyncio.run(test_polling())
