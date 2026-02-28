#!/usr/bin/env python3
"""
Test script untuk memverifikasi signal tracking integration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("🧪 Testing Signal Tracking Integration\n")
print("=" * 50)

# Test 1: Import handlers
print("\n1️⃣ Testing handler imports...")
try:
    from app.handlers_signal_tracking import (
        cmd_winrate, cmd_weekly_report, cmd_upload_logs, cmd_signal_stats
    )
    print("   ✅ All handlers imported successfully")
except Exception as e:
    print(f"   ❌ Handler import failed: {e}")
    sys.exit(1)

# Test 2: Import integration helpers
print("\n2️⃣ Testing integration helpers...")
try:
    from app.signal_tracker_integration import (
        track_user_command, track_signal_given, 
        update_signal_outcome, get_current_winrate
    )
    print("   ✅ All integration helpers imported")
except Exception as e:
    print(f"   ❌ Integration helper import failed: {e}")
    sys.exit(1)

# Test 3: Import scheduler
print("\n3️⃣ Testing scheduler...")
try:
    from app.scheduler import task_scheduler
    print("   ✅ Scheduler imported successfully")
except Exception as e:
    print(f"   ❌ Scheduler import failed: {e}")
    sys.exit(1)

# Test 4: Check signal logger
print("\n4️⃣ Testing signal logger...")
try:
    from app.signal_logger import signal_logger
    print(f"   ✅ Signal logger initialized")
    print(f"   📁 Log directory: {signal_logger.log_dir}")
except Exception as e:
    print(f"   ❌ Signal logger failed: {e}")
    sys.exit(1)

# Test 5: Check G: drive sync
print("\n5️⃣ Testing G: drive sync...")
try:
    from app.local_gdrive_sync import local_gdrive_sync
    if local_gdrive_sync.enabled:
        print(f"   ✅ G: drive sync enabled")
        print(f"   📁 G: drive path: {local_gdrive_sync.gdrive_path}")
    else:
        print(f"   ⚠️ G: drive sync disabled (G: drive not available)")
except Exception as e:
    print(f"   ❌ G: drive sync check failed: {e}")

# Test 6: Check Supabase storage
print("\n6️⃣ Testing Supabase storage...")
try:
    from app.supabase_storage import supabase_storage
    if supabase_storage.enabled:
        print(f"   ✅ Supabase storage enabled")
        print(f"   🪣 Bucket: {supabase_storage.bucket_name}")
    else:
        print(f"   ⚠️ Supabase storage disabled")
except Exception as e:
    print(f"   ❌ Supabase storage check failed: {e}")

# Test 7: Test tracking functionality
print("\n7️⃣ Testing tracking functionality...")
try:
    # Track a test command
    track_user_command(999999, "test_user", "/test", "BTC", "1h")
    print("   ✅ Command tracking works")
    
    # Track a test signal
    signal_id = track_signal_given(
        999999, "BTCUSDT", "1h", 50000, 51000, 52000, 49500, "LONG"
    )
    print(f"   ✅ Signal tracking works (ID: {signal_id})")
    
    # Update signal outcome
    update_signal_outcome(signal_id, hit_tp=True, pnl_percent=2.0)
    print("   ✅ Signal update works")
    
    # Get winrate
    stats = get_current_winrate(7)
    if stats:
        print(f"   ✅ Winrate calculation works")
        print(f"      📊 Total signals: {stats['total_signals']}")
        print(f"      📈 Winrate: {stats['winrate']}%")
    else:
        print("   ⚠️ No winrate data available")
        
except Exception as e:
    print(f"   ❌ Tracking functionality failed: {e}")
    import traceback
    traceback.print_exc()

# Test 8: Check bot.py integration
print("\n8️⃣ Checking bot.py integration...")
try:
    with open("bot.py", "r", encoding="utf-8") as f:
        bot_content = f.read()
        
    if "handlers_signal_tracking" in bot_content:
        print("   ✅ Signal tracking handlers registered in bot.py")
    else:
        print("   ❌ Signal tracking handlers NOT found in bot.py")
        
    if "cmd_signal_stats" in bot_content:
        print("   ✅ /signal_stats command registered")
    else:
        print("   ❌ /signal_stats command NOT registered")
        
except Exception as e:
    print(f"   ❌ Bot.py check failed: {e}")

# Test 9: Check main.py integration
print("\n9️⃣ Checking main.py integration...")
try:
    with open("main.py", "r", encoding="utf-8") as f:
        main_content = f.read()
        
    if "task_scheduler" in main_content:
        print("   ✅ Scheduler startup added to main.py")
    else:
        print("   ❌ Scheduler startup NOT found in main.py")
        
except Exception as e:
    print(f"   ❌ Main.py check failed: {e}")

print("\n" + "=" * 50)
print("✅ Integration test complete!")
print("\n💡 Next steps:")
print("   1. Restart bot: python main.py")
print("   2. Test commands: /signal_stats, /winrate")
print("   3. Check logs in signal_logs/ directory")
print("   4. Verify G: drive sync (if enabled)")
