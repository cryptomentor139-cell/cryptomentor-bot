#!/usr/bin/env python3
"""
Test AutoSignal with SMC Integration
"""
import os
import sys

# Set test environment
os.environ['CMC_API_KEY'] = os.getenv('CMC_API_KEY', 'test_key')
os.environ['AUTOSIGNAL_INTERVAL_SEC'] = '1800'
os.environ['FUTURES_TF'] = '15m'

print("🧪 Testing AutoSignal with SMC Integration")
print("=" * 60)

# Test 1: Import modules
print("\n1️⃣ Testing imports...")
try:
    from app.autosignal_fast import (
        compute_signal_fast,
        format_signal_text,
        autosignal_enabled,
        set_autosignal_enabled
    )
    from smc_analyzer import smc_analyzer
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check SMC Analyzer
print("\n2️⃣ Testing SMC Analyzer...")
try:
    # Test with BTC
    result = smc_analyzer.analyze('BTCUSDT', '15m', limit=200)
    
    if 'error' in result:
        print(f"   ⚠️  SMC analysis returned error: {result['error']}")
    else:
        print(f"   ✅ SMC analysis successful")
        print(f"      Order Blocks: {len(result.get('order_blocks', []))}")
        print(f"      FVGs: {len(result.get('fvgs', []))}")
        print(f"      Structure: {result.get('structure', {}).get('trend', 'unknown')}")
        print(f"      EMA 21: {result.get('ema_21', 0):.2f}")
        print(f"      Week High: {result.get('week_high', 0):.2f}")
        print(f"      Week Low: {result.get('week_low', 0):.2f}")
except Exception as e:
    print(f"   ❌ SMC analysis failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test signal generation with SMC
print("\n3️⃣ Testing signal generation with SMC...")
try:
    # Test with BTC
    signal = compute_signal_fast('BTC')
    
    if signal:
        print(f"   ✅ Signal generated for BTC")
        print(f"      Symbol: {signal.get('symbol')}")
        print(f"      Side: {signal.get('side')}")
        print(f"      Confidence: {signal.get('confidence')}%")
        print(f"      Reasons: {', '.join(signal.get('reasons', []))}")
        
        smc_data = signal.get('smc_data', {})
        if smc_data:
            print(f"      SMC Data:")
            print(f"         Order Blocks: {smc_data.get('order_blocks', 0)}")
            print(f"         FVGs: {smc_data.get('fvgs', 0)}")
            print(f"         Structure: {smc_data.get('structure', 'unknown')}")
            print(f"         EMA 21: {smc_data.get('ema_21', 0):.2f}")
        
        # Test formatting
        formatted = format_signal_text(signal)
        print(f"\n   📝 Formatted signal:")
        print("   " + "\n   ".join(formatted.split('\n')))
    else:
        print(f"   ℹ️  No signal generated for BTC (normal - waiting for setup)")
except Exception as e:
    print(f"   ❌ Signal generation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test autosignal state
print("\n4️⃣ Testing autosignal state...")
try:
    # Check if enabled
    is_enabled = autosignal_enabled()
    print(f"   Current state: {'✅ ENABLED' if is_enabled else '❌ DISABLED'}")
    
    # Toggle state
    set_autosignal_enabled(True)
    print(f"   Set to: ✅ ENABLED")
    
    # Verify
    is_enabled = autosignal_enabled()
    if is_enabled:
        print(f"   ✅ State verified: ENABLED")
    else:
        print(f"   ❌ State verification failed")
except Exception as e:
    print(f"   ❌ State test failed: {e}")

# Test 5: Check bot integration
print("\n5️⃣ Checking bot integration...")
try:
    with open('bot.py', 'r', encoding='utf-8') as f:
        bot_content = f.read()
    
    if 'start_background_scheduler' in bot_content and 'autosignal_fast' in bot_content:
        print("   ✅ AutoSignal scheduler integrated in bot.py")
    else:
        print("   ⚠️  AutoSignal scheduler not found in bot.py")
    
    if 'cmd_signal_on' in bot_content:
        print("   ✅ Admin commands registered")
    else:
        print("   ⚠️  Admin commands not found")
except Exception as e:
    print(f"   ❌ Bot integration check failed: {e}")

# Summary
print("\n" + "=" * 60)
print("✅ AutoSignal with SMC Integration Test Complete!")
print("\n📊 Features:")
print("   • Order Blocks detection")
print("   • Fair Value Gaps (FVG)")
print("   • Market Structure analysis")
print("   • Week High/Low tracking")
print("   • EMA 21 confirmation")
print("   • SnD zones (fallback)")
print("\n🎯 Admin Commands:")
print("   /signal_on  - Enable autosignal")
print("   /signal_off - Disable autosignal")
print("   /signal_status - Check status")
print("   /signal_tick - Manual scan")
print("\n⚙️  Configuration:")
print(f"   Interval: {os.getenv('AUTOSIGNAL_INTERVAL_SEC', '1800')}s (30 min)")
print(f"   Timeframe: {os.getenv('FUTURES_TF', '15m')}")
print(f"   Top coins: 25 (CMC)")
print(f"   Min confidence: 75%")
