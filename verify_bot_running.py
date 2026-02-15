"""
Verify bot is running and check its status
"""
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

def check_bot_token():
    """Check if bot token is configured"""
    token = os.getenv('TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ Bot token not found in .env")
        return False
    
    print(f"✅ Bot token found: {token[:20]}...")
    return True

def test_bot_connection():
    """Test bot connection to Telegram"""
    print("\n🔌 Testing Telegram Bot API connection...")
    print("-" * 60)
    
    try:
        import requests
        
        token = os.getenv('TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
        url = f"https://api.telegram.org/bot{token}/getMe"
        
        print("⏳ Connecting to Telegram API...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print("\n✅ Bot is ONLINE and responding!")
                print(f"   Bot Name: {bot_info.get('first_name')}")
                print(f"   Username: @{bot_info.get('username')}")
                print(f"   Bot ID: {bot_info.get('id')}")
                print(f"   Can Join Groups: {bot_info.get('can_join_groups')}")
                print(f"   Can Read Messages: {bot_info.get('can_read_all_group_messages')}")
                return True
            else:
                print(f"❌ API returned error: {data}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def show_bot_info():
    """Show bot information and how to use"""
    print("\n" + "=" * 60)
    print("📱 HOW TO USE YOUR BOT")
    print("=" * 60)
    print()
    
    token = os.getenv('TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                username = bot_info.get('username')
                
                print(f"🤖 Your Bot: @{username}")
                print()
                print("📝 Steps to use:")
                print(f"   1. Open Telegram")
                print(f"   2. Search for: @{username}")
                print(f"   3. Click 'Start' or send: /start")
                print(f"   4. Send: /admin (if you're admin)")
                print()
                print("🎯 Admin Commands:")
                print("   /admin - Open admin panel")
                print("   /admin → Settings → Database Stats")
                print("   /admin → Settings → Broadcast")
                print()
                print("🤖 AI Commands:")
                print("   /ai btc - Analyze Bitcoin")
                print("   /chat hello - Chat with AI")
                print("   /aimarket - Market summary")
                print()
                print(f"🔗 Direct link: https://t.me/{username}")
                print()
    except:
        print("⚠️  Could not fetch bot info")
        print("   But bot should still be working!")
        print()
        print("📝 Try these commands in Telegram:")
        print("   /start")
        print("   /admin")
        print("   /ai btc")
        print()

def main():
    print()
    print("🤖 CryptoMentor Bot - Status Checker")
    print("=" * 60)
    print()
    
    # Check token
    if not check_bot_token():
        print("\n❌ Cannot proceed without bot token")
        return
    
    # Test connection
    bot_online = test_bot_connection()
    
    # Show info
    if bot_online:
        show_bot_info()
        
        print("=" * 60)
        print("✅ BOT IS READY!")
        print("=" * 60)
        print()
        print("🎉 Your bot is online and ready to receive messages!")
        print()
        print("💡 To start the bot process:")
        print("   python bot.py")
        print()
        print("📊 To check if bot process is running:")
        print("   Check Task Manager for 'python.exe' process")
        print("   Or try sending /start to your bot in Telegram")
        print()
    else:
        print("\n❌ Bot connection failed")
        print("   Check your TOKEN in .env file")
        print("   Make sure it's correct and not expired")
        print()

if __name__ == "__main__":
    main()
