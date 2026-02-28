#!/usr/bin/env python3
"""
Force process pending updates to clear the queue
"""
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Application

load_dotenv()

async def process_pending_updates():
    """Manually fetch and process pending updates"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return
    
    bot = Bot(token=token)
    
    try:
        print("🔍 Fetching pending updates...")
        updates = await bot.get_updates(limit=100, timeout=10)
        
        if not updates:
            print("✅ No pending updates")
            return
        
        print(f"📥 Found {len(updates)} pending updates")
        
        for i, update in enumerate(updates, 1):
            print(f"\n📨 Update {i}/{len(updates)}:")
            print(f"   Update ID: {update.update_id}")
            
            if update.message:
                msg = update.message
                print(f"   Type: Message")
                print(f"   From: {msg.from_user.first_name} (@{msg.from_user.username})")
                print(f"   Text: {msg.text}")
                print(f"   Chat ID: {msg.chat_id}")
            elif update.callback_query:
                cb = update.callback_query
                print(f"   Type: Callback Query")
                print(f"   From: {cb.from_user.first_name}")
                print(f"   Data: {cb.data}")
            else:
                print(f"   Type: Other")
        
        # Get the last update ID to mark as processed
        last_update_id = updates[-1].update_id
        
        print(f"\n🔄 Marking updates as processed (offset={last_update_id + 1})...")
        await bot.get_updates(offset=last_update_id + 1, timeout=1)
        
        print("✅ All pending updates cleared!")
        print("\n💡 The running bot should now receive new messages.")
        print("   Try sending a new message to the bot.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(process_pending_updates())
