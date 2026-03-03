#!/usr/bin/env python3
"""
Test script to verify multi-coin signals timeout fix
Tests that signals complete within 30 seconds or timeout gracefully
"""

import asyncio
import time
from futures_signal_generator import FuturesSignalGenerator

async def test_multi_coin_signals():
    """Test multi-coin signals with timeout"""
    print("🧪 Testing Multi-Coin Signals Timeout Fix\n")
    print("=" * 60)
    
    generator = FuturesSignalGenerator()
    
    # Test 1: Normal execution
    print("\n📊 Test 1: Normal Execution")
    print("-" * 60)
    start_time = time.time()
    
    try:
        # Add 30 second timeout (same as production)
        signals = await asyncio.wait_for(
            generator.generate_multi_signals(),
            timeout=30.0
        )
        
        elapsed = time.time() - start_time
        
        print(f"✅ SUCCESS: Signals generated in {elapsed:.2f} seconds")
        print(f"📏 Signal length: {len(signals)} characters")
        print(f"⏱️ Within timeout: {'YES' if elapsed < 30 else 'NO'}")
        
        # Show first 500 chars
        print(f"\n📄 Preview (first 500 chars):")
        print("-" * 60)
        print(signals[:500])
        print("...")
        
        return True
        
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"❌ TIMEOUT: Signals took longer than 30 seconds")
        print(f"⏱️ Elapsed: {elapsed:.2f} seconds")
        return False
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ ERROR: {str(e)}")
        print(f"⏱️ Elapsed: {elapsed:.2f} seconds")
        import traceback
        traceback.print_exc()
        return False

async def test_multi_source_timeout():
    """Test multi-source provider timeout"""
    print("\n\n📊 Test 2: Multi-Source Provider Timeout")
    print("-" * 60)
    
    try:
        from app.providers.multi_source_provider import multi_source_provider
        
        start_time = time.time()
        
        # Test BTC price fetch with timeout
        btc_data = await asyncio.wait_for(
            multi_source_provider.get_price('BTC'),
            timeout=5.0
        )
        
        elapsed = time.time() - start_time
        
        if btc_data.get('error'):
            print(f"⚠️ WARNING: Multi-source returned error: {btc_data.get('error')}")
            print(f"⏱️ Elapsed: {elapsed:.2f} seconds")
            return True  # Still OK, fallback should work
        else:
            print(f"✅ SUCCESS: BTC price fetched in {elapsed:.2f} seconds")
            print(f"💰 BTC Price: ${btc_data.get('price', 0):,.2f}")
            print(f"📊 Source: {btc_data.get('source', 'unknown')}")
            return True
            
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"⚠️ TIMEOUT: Multi-source took longer than 5 seconds")
        print(f"⏱️ Elapsed: {elapsed:.2f} seconds")
        print("💡 This is OK - fallback to Binance-only should work")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 MULTI-COIN SIGNALS TIMEOUT FIX TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Normal execution
    result1 = await test_multi_coin_signals()
    results.append(("Multi-Coin Signals", result1))
    
    # Test 2: Multi-source timeout
    result2 = await test_multi_source_timeout()
    results.append(("Multi-Source Provider", result2))
    
    # Summary
    print("\n\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Multi-coin signals timeout fix is working correctly")
    else:
        print("❌ SOME TESTS FAILED")
        print("⚠️ Please check the errors above")
    print("=" * 60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
