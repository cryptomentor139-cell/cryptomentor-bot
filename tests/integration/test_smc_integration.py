#!/usr/bin/env python3
"""
Test SMC Integration
Validates that SMC analyzer works and formats correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_smc_analyzer():
    """Test SMC analyzer basic functionality"""
    print("=" * 60)
    print("TEST 1: SMC Analyzer Basic Functionality")
    print("=" * 60)
    
    try:
        from smc_analyzer import smc_analyzer
        
        # Test with BTC
        print("\n📊 Testing SMC analysis for BTCUSDT...")
        result = smc_analyzer.analyze('BTCUSDT', '1h', limit=200)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"✅ Analysis successful!")
        print(f"   Current Price: ${result.get('current_price', 0):,.2f}")
        print(f"   Order Blocks: {len(result.get('order_blocks', []))}")
        print(f"   FVGs: {len(result.get('fvgs', []))}")
        
        structure = result.get('structure', {})
        if structure:
            trend = structure.trend if hasattr(structure, 'trend') else 'unknown'
            print(f"   Market Structure: {trend}")
        
        print(f"   Week High: ${result.get('week_high', 0):,.2f}")
        print(f"   Week Low: ${result.get('week_low', 0):,.2f}")
        print(f"   EMA 21: ${result.get('ema_21', 0):,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smc_formatter():
    """Test SMC formatter"""
    print("\n" + "=" * 60)
    print("TEST 2: SMC Formatter")
    print("=" * 60)
    
    try:
        from smc_analyzer import smc_analyzer
        from smc_formatter import format_smc_analysis
        
        # Get analysis
        result = smc_analyzer.analyze('ETHUSDT', '1h', limit=200)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        # Test full format
        print("\n📊 Full Format:")
        print("-" * 60)
        full_text = format_smc_analysis(result, compact=False)
        print(full_text)
        
        # Test compact format
        print("\n📊 Compact Format:")
        print("-" * 60)
        compact_text = format_smc_analysis(result, compact=True)
        print(compact_text)
        
        print("\n✅ Formatter test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_coins():
    """Test SMC analysis on multiple coins"""
    print("\n" + "=" * 60)
    print("TEST 3: Multiple Coins Analysis")
    print("=" * 60)
    
    coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT']
    
    try:
        from smc_analyzer import smc_analyzer
        from smc_formatter import format_smc_analysis
        
        for coin in coins:
            print(f"\n📊 {coin}:")
            result = smc_analyzer.analyze(coin, '1h', limit=100)
            
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
                continue
            
            compact = format_smc_analysis(result, compact=True)
            print(f"   {compact}")
        
        print("\n✅ Multiple coins test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_order_blocks():
    """Test Order Block detection"""
    print("\n" + "=" * 60)
    print("TEST 4: Order Block Detection")
    print("=" * 60)
    
    try:
        from smc_analyzer import smc_analyzer
        
        result = smc_analyzer.analyze('BTCUSDT', '1h', limit=200)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        order_blocks = result.get('order_blocks', [])
        print(f"\n📊 Found {len(order_blocks)} Order Blocks:")
        
        for i, ob in enumerate(order_blocks, 1):
            print(f"\n   {i}. {ob.type.upper()} Order Block")
            print(f"      Range: ${ob.low:,.2f} - ${ob.high:,.2f}")
            print(f"      Strength: {ob.strength:.1f}%")
            print(f"      Time: {ob.time}")
        
        print("\n✅ Order Block test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fvg_detection():
    """Test Fair Value Gap detection"""
    print("\n" + "=" * 60)
    print("TEST 5: Fair Value Gap Detection")
    print("=" * 60)
    
    try:
        from smc_analyzer import smc_analyzer
        
        result = smc_analyzer.analyze('ETHUSDT', '1h', limit=200)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        fvgs = result.get('fvgs', [])
        print(f"\n📊 Found {len(fvgs)} Fair Value Gaps:")
        
        for i, fvg in enumerate(fvgs, 1):
            print(f"\n   {i}. {fvg.type.upper()} FVG")
            print(f"      Range: ${fvg.bottom:,.2f} - ${fvg.top:,.2f}")
            print(f"      Time: {fvg.time}")
            print(f"      Filled: {fvg.filled}")
        
        print("\n✅ FVG test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n🚀 SMC INTEGRATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("SMC Analyzer", test_smc_analyzer),
        ("SMC Formatter", test_smc_formatter),
        ("Multiple Coins", test_multiple_coins),
        ("Order Blocks", test_order_blocks),
        ("Fair Value Gaps", test_fvg_detection),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! SMC integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
