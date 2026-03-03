#!/usr/bin/env python3
"""
Send a test message to the bot to trigger a response
"""
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

async def send_test():
    """Send test message"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    admin_id = int(os.getenv('ADMIN1', '1187119989'))
    
    bot = Bot(token=token)
    
    try:
        print(f"📤 Sending test message to admin {admin_id}...")
        
        # Send a message that should trigger the bot
        await bot.send_message(
            chat_id=admin_id,
            text="/start"
        )
        
        print("✅ Test message sent!")
        print("💡 Check if the bot responds in Telegram")
        print("   Also check the bot process output for any errors")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_test())
