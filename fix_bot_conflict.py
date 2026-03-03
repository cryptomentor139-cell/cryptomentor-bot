#!/usr/bin/env python3
"""
Fix Bot Conflict - Delete Webhook and Check Status
"""

import requests
import os
from dotenv import load_dotenv

def main():
    print("🔧 Bot Conflict Fixer")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env")
        return
    
    print(f"✅ Bot token loaded: {token[:10]}...")
    
    # Check webhook status
    print("\n🔍 Checking webhook status...")
    try:
        info_response = requests.get(
            f'https://api.telegram.org/bot{token}/getWebhookInfo',
            timeout=10
        )
        webhook_info = info_response.json()
        
        if webhook_info.get('ok'):
            result = webhook_info.get('result', {})
            webhook_url = result.get('url', '')
            pending_updates = result.get('pending_update_count', 0)
            
            print(f"   Webhook URL: {webhook_url if webhook_url else '(none)'}")
            print(f"   Pending updates: {pending_updates}")
            
            if webhook_url:
                print("\n❌ Webhook is ACTIVE! This causes conflict with polling.")
                print("   Deleting webhook...")
                
                delete_response = requests.get(
                    f'https://api.telegram.org/bot{token}/deleteWebhook',
                    timeout=10
                )
                delete_result = delete_response.json()
                
                if delete_result.get('ok'):
                    print("✅ Webhook deleted successfully!")
                else:
                    print(f"❌ Failed to delete webhook: {delete_result}")
            else:
                print("✅ No webhook active (good for polling)")
        else:
            print(f"❌ API error: {webhook_info}")
    
    except Exception as e:
        print(f"❌ Error checking webhook: {e}")
    
    # Get bot info
    print("\n🔍 Checking bot info...")
    try:
        me_response = requests.get(
            f'https://api.telegram.org/bot{token}/getMe',
            timeout=10
        )
        me_info = me_response.json()
        
        if me_info.get('ok'):
            bot = me_info.get('result', {})
            print(f"   Bot username: @{bot.get('username')}")
            print(f"   Bot name: {bot.get('first_name')}")
            print(f"   Bot ID: {bot.get('id')}")
        else:
            print(f"❌ API error: {me_info}")
    
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
    
    # Check for pending updates
    print("\n🔍 Checking for pending updates...")
    try:
        updates_response = requests.get(
            f'https://api.telegram.org/bot{token}/getUpdates?limit=1',
            timeout=10
        )
        updates_info = updates_response.json()
        
        if updates_info.get('ok'):
            updates = updates_info.get('result', [])
            print(f"   Pending updates: {len(updates)}")
            
            if updates:
                print("   (These will be processed when bot starts)")
        else:
            print(f"❌ API error: {updates_info}")
    
    except Exception as e:
        print(f"❌ Error checking updates: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Conflict check complete!")
    print("\n🎯 Next steps:")
    print("   1. Make sure NO local bot is running")
    print("   2. Check Task Manager for python.exe")
    print("   3. Restart Railway: railway restart")
    print("   4. Check logs: railway logs")
    print("\n💡 If still conflicts:")
    print("   - Kill all Python processes: taskkill /F /IM python.exe")
    print("   - Wait 30 seconds")
    print("   - Restart Railway again")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
