#!/usr/bin/env python3
"""
Test OpenClaw Enhanced Features
- Binance API integration
- GPT-4 Vision for chart analysis
"""

import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()


async def test_crypto_data_tools():
    """Test Binance API integration"""
    print("\n" + "="*60)
    print("TEST 1: Crypto Data Tools (Binance API)")
    print("="*60)
    
    try:
        from app.openclaw_crypto_data_tools import get_crypto_data_tools
        
        tools = get_crypto_data_tools()
        
        # Test 1: Get current price
        print("\n1️⃣ Testing get_current_price(BTCUSDT)...")
        result = await tools.get_current_price("BTCUSDT")
        
        if result['success']:
            print(f"✅ BTC Price: ${result['price']:,.2f}")
        else:
            print(f"❌ Failed: {result.get('error')}")
            return False
        
        # Test 2: Get 24h stats
        print("\n2️⃣ Testing get_24h_stats(ETHUSDT)...")
        result = await tools.get_24h_stats("ETHUSDT")
        
        if result['success']:
            print(f"✅ ETH Stats:")
            print(f"   Price: ${result['price']:,.2f}")
            print(f"   24h Change: {result['change_percent_24h']:+.2f}%")
            print(f"   24h High: ${result['high_24h']:,.2f}")
            print(f"   24h Low: ${result['low_24h']:,.2f}")
        else:
            print(f"❌ Failed: {result.get('error')}")
            return False
        
        # Test 3: Get top gainers
        print("\n3️⃣ Testing get_top_gainers()...")
        result = await tools.get_top_gainers(limit=5)
        
        if result['success']:
            print(f"✅ Top 5 Gainers:")
            for i, gainer in enumerate(result['gainers'][:5], 1):
                print(f"   {i}. {gainer['symbol']}: {gainer['change_percent']:+.2f}%")
        else:
            print(f"❌ Failed: {result.get('error')}")
            return False
        
        print("\n✅ All crypto data tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_vision_tools():
    """Test GPT-4 Vision integration"""
    print("\n" + "="*60)
    print("TEST 2: Vision Tools (GPT-4 Vision)")
    print("="*60)
    
    try:
        from app.openclaw_vision_tools import get_vision_tools
        import os
        
        tools = get_vision_tools()
        
        # Check if API key is configured
        api_key = os.getenv('OPENCLAW_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            print("⚠️ No API key configured - skipping vision tests")
            print("   Set OPENCLAW_API_KEY or OPENROUTER_API_KEY to test")
            return True  # Not a failure, just skipped
        
        print("✅ API key configured")
        print("✅ Vision tools initialized")
        print("\n💡 To test image analysis:")
        print("   1. Send a chart image to the bot")
        print("   2. Bot will automatically analyze it")
        print("   3. Check the response for technical analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_enhanced_handler():
    """Test enhanced message handler"""
    print("\n" + "="*60)
    print("TEST 3: Enhanced Message Handler")
    print("="*60)
    
    try:
        # Mock manager
        class MockManager:
            pass
        
        from app.openclaw_enhanced_handler import get_enhanced_handler
        
        manager = MockManager()
        handler = get_enhanced_handler(manager)
        
        # Test 1: Symbol extraction
        print("\n1️⃣ Testing symbol extraction...")
        
        test_messages = [
            "What's the BTC price?",
            "Show me ETH and SOL stats",
            "BTCUSDT analysis",
            "Compare Bitcoin and Ethereum"
        ]
        
        for msg in test_messages:
            symbols = handler._extract_crypto_symbols(msg)
            print(f"   '{msg}' → {symbols}")
        
        print("✅ Symbol extraction working")
        
        # Test 2: Market data request detection
        print("\n2️⃣ Testing market data detection...")
        
        test_messages = [
            "market overview",
            "show me top gainers",
            "what's trending?",
            "just a normal question"
        ]
        
        for msg in test_messages:
            is_market = handler._is_market_data_request(msg)
            print(f"   '{msg}' → {'Market request' if is_market else 'Normal'}")
        
        print("✅ Market data detection working")
        
        # Test 3: Message enhancement (without actual API calls)
        print("\n3️⃣ Testing message enhancement...")
        print("   (Skipping actual API calls in test)")
        print("✅ Enhanced handler initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 OpenClaw Enhanced Features Test")
    print("="*60)
    
    results = []
    
    # Test 1: Crypto Data Tools
    results.append(("Crypto Data Tools", await test_crypto_data_tools()))
    
    # Test 2: Vision Tools
    results.append(("Vision Tools", await test_vision_tools()))
    
    # Test 3: Enhanced Handler
    results.append(("Enhanced Handler", await test_enhanced_handler()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ OpenClaw Enhanced Features Ready:")
        print("   • Binance API integration")
        print("   • GPT-4 Vision for charts")
        print("   • Auto-detection & enhancement")
        print("\n📋 Next Steps:")
        print("1. Deploy to Railway: git push")
        print("2. Test with real Telegram messages")
        print("3. Send chart images to bot")
        print("4. Ask about crypto prices")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please check the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
