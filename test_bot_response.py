#!/usr/bin/env python3
"""
Test script to check if bot is receiving and responding to updates
"""
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

async def test_bot():
    """Test bot connectivity and recent updates"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return
    
    bot = Bot(token=token)
    
    try:
        # Get bot info
        print("🔍 Testing bot connection...")
        me = await bot.get_me()
        print(f"✅ Bot connected: @{me.username}")
        print(f"   ID: {me.id}")
        print(f"   Name: {me.first_name}")
        
        # Check webhook status
        print("\n🔍 Checking webhook status...")
        webhook_info = await bot.get_webhook_info()
        print(f"   URL: {webhook_info.url or 'None (polling mode)'}")
        print(f"   Pending updates: {webhook_info.pending_update_count}")
        print(f"   Last error: {webhook_info.last_error_message or 'None'}")
        
        if webhook_info.url:
            print("\n⚠️  PROBLEM FOUND: Webhook is set!")
            print("   This prevents polling from working.")
            print("   The bot needs to delete the webhook to use polling.")
            print("\n💡 Solution: The bot should call deleteWebhook on startup")
        else:
            print("\n✅ Webhook is not set - polling should work")
        
        # Try to get recent updates (this won't work if bot is already polling)
        print("\n🔍 Checking for recent updates...")
        try:
            updates = await bot.get_updates(limit=5, timeout=5)
            if updates:
                print(f"✅ Found {len(updates)} recent updates:")
                for update in updates:
                    if update.message:
                        print(f"   - Message from {update.message.from_user.first_name}: {update.message.text}")
                    elif update.callback_query:
                        print(f"   - Callback from {update.callback_query.from_user.first_name}")
            else:
                print("   No pending updates (this is normal if bot is already polling)")
        except Exception as e:
            print(f"   ⚠️  Cannot get updates: {e}")
            print("   (This is normal if bot is already running and polling)")
        
        print("\n" + "="*60)
        print("📊 DIAGNOSIS:")
        print("="*60)
        
        if webhook_info.url:
            print("❌ ISSUE: Webhook is active - this blocks polling!")
            print("   The bot cannot receive updates via polling while webhook is set.")
            print("\n🔧 FIX: Restart the bot - it should delete webhook on startup")
        else:
            print("✅ Bot configuration looks correct")
            print("   - Webhook is disabled ✓")
            print("   - Bot is connected ✓")
            print("   - Polling should be working ✓")
            print("\n💡 If bot still doesn't respond:")
            print("   1. Check if there are any errors in bot logs")
            print("   2. Try sending /start command to the bot")
            print("   3. Make sure you're messaging the correct bot: @" + me.username)
            print("   4. Check if bot has any privacy mode restrictions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Close the bot session
        await bot.close()

if __name__ == "__main__":
    asyncio.run(test_bot())
