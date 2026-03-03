#!/usr/bin/env python3
"""
Quick Setup Script untuk Signal Tracking System
"""
import os
from pathlib import Path

def main():
    print("🚀 Signal Tracking System Setup\n")
    
    # 1. Create directories
    print("📁 Creating directories...")
    log_dir = Path("signal_logs")
    log_dir.mkdir(exist_ok=True)
    print("   ✅ signal_logs/")
    
    # 2. Check dependencies
    print("\n📦 Checking dependencies...")
    try:
        import pydrive2
        print("   ✅ PyDrive2 installed")
    except ImportError:
        print("   ❌ PyDrive2 not installed")
        print("   Run: pip install PyDrive2")
        return
    
    # 3. Check credentials
    print("\n🔐 Checking Google Drive credentials...")
    creds_file = Path("gdrive_credentials.json")
    if creds_file.exists():
        print("   ✅ gdrive_credentials.json found")
    else:
        print("   ❌ gdrive_credentials.json not found")
        print("   Follow SIGNAL_TRACKING_SETUP.md to setup")
        return
    
    # 4. Test authentication
    print("\n🔑 Testing Google Drive authentication...")
    try:
        from app.gdrive_uploader import gdrive_uploader
        if gdrive_uploader.enabled:
            print("   ✅ Google Drive connected")
        else:
            print("   ⚠️ Google Drive not enabled")
            print("   Check credentials and try again")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 5. Test tracking
    print("\n📊 Testing signal tracking...")
    try:
        from app.signal_tracker_integration import track_user_command
        track_user_command(123456, "test_user", "/test", "BTC", "1h")
        print("   ✅ Tracking working")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 6. Test winrate calculation
    print("\n📈 Testing winrate calculation...")
    try:
        from app.signal_tracker_integration import get_current_winrate
        stats = get_current_winrate(7)
        print(f"   ✅ Winrate: {stats['winrate']}%")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print("\n" + "="*50)
    print("✅ Setup Complete!")
    print("="*50)
    print("\n📋 Next Steps:")
    print("1. Integrate tracking calls in bot commands")
    print("2. Register admin commands in bot.py")
    print("3. Start scheduler in bot main()")
    print("4. Test with: /winrate, /signal_stats")
    print("\n📖 See: TRACKING_INTEGRATION_EXAMPLE.md")

if __name__ == "__main__":
    main()
