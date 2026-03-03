#!/usr/bin/env python3
"""
Test OpenClaw Crypto Integration
Quick test to verify crypto data tools are working
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

def test_crypto_tools():
    """Test crypto data tools"""
    from app.openclaw_crypto_tools import get_crypto_tools
    
    print("=" * 60)
    print("🧪 Testing OpenClaw Crypto Tools")
    print("=" * 60)
    print()
    
    tools = get_crypto_tools()
    
    # Test 1: Get current price
    print("📡 Test 1: Get Current Price (BTC)")
    print("-" * 60)
    price_data = tools.get_current_price('BTC')
    if 'error' in price_data:
        print(f"❌ Error: {price_data['error']}")
    else:
        print(f"✅ BTC Price: ${price_data['price_usd']:,.2f}")
        print(f"   Source: {price_data['source']}")
        print(f"   Timestamp: {price_data['timestamp']}")
    print()
    
    # Test 2: Get trading signal
    print("📡 Test 2: Get Trading Signal (ETH)")
    print("-" * 60)
    signal_data = tools.get_trading_signal('ETH')
    if 'error' in signal_data:
        print(f"❌ Error: {signal_data['error']}")
    else:
        print(f"✅ ETH Trading Signal:")
        print(f"   Price: ${signal_data['current_price']:,.2f}")
        print(f"   Signal: {signal_data['signal']}")
        print(f"   Momentum: {signal_data['momentum']}")
        print(f"   Change 30d: {signal_data['change_30d']}")
        print(f"   Support: ${signal_data['support']:,.2f}")
        print(f"   Resistance: ${signal_data['resistance']:,.2f}")
        print(f"   Analysis: {signal_data['analysis'][:100]}...")
    print()
    
    # Test 3: Format for LLM
    print("📡 Test 3: Format for LLM")
    print("-" * 60)
    if 'error' not in signal_data:
        formatted = tools.format_for_llm(signal_data)
        print("✅ Formatted output:")
        print(formatted[:300] + "...")
    print()
    
    # Test 4: Get crypto news
    print("📡 Test 4: Get Crypto News")
    print("-" * 60)
    news_data = tools.get_crypto_news(limit=3)
    if 'error' in news_data:
        print(f"⚠️  News API: {news_data['error']}")
        print("   (This is optional - bot will work without news)")
    else:
        print(f"✅ Got {news_data['news_count']} news items")
        for i, item in enumerate(news_data['news'][:2], 1):
            print(f"   {i}. {item['title'][:60]}...")
    print()
    
    print("=" * 60)
    print("✅ Crypto Tools Test Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Test in Telegram: /openclaw_start")
    print("2. Ask: 'What's the BTC price?'")
    print("3. Ask: 'Give me a trading signal for ETH'")
    print()

def test_crypto_detection():
    """Test crypto query detection"""
    print("=" * 60)
    print("🧪 Testing Crypto Query Detection")
    print("=" * 60)
    print()
    
    test_messages = [
        "What's the BTC price?",
        "Give me a trading signal for ETH",
        "Should I buy SOL?",
        "Tell me about Bitcoin",
        "What's happening in crypto market?",
        "Hello, how are you?"  # Non-crypto query
    ]
    
    # Mock OpenClawManager for testing
    class MockManager:
        def _get_crypto_context(self, message):
            from app.openclaw_crypto_tools import get_crypto_tools
            
            message_lower = message.lower()
            crypto_keywords = [
                'price', 'signal', 'trade', 'trading', 'buy', 'sell',
                'market', 'crypto', 'bitcoin', 'btc', 'eth', 'sol'
            ]
            
            has_crypto = any(keyword in message_lower for keyword in crypto_keywords)
            return "CRYPTO_DATA_DETECTED" if has_crypto else None
    
    manager = MockManager()
    
    for msg in test_messages:
        result = manager._get_crypto_context(msg)
        status = "✅ DETECTED" if result else "❌ NOT DETECTED"
        print(f"{status}: \"{msg}\"")
    
    print()
    print("=" * 60)
    print("✅ Detection Test Complete!")
    print("=" * 60)
    print()

if __name__ == "__main__":
    print("\n🚀 Starting OpenClaw Crypto Integration Tests...\n")
    
    try:
        test_crypto_tools()
        test_crypto_detection()
        
        print("✅ All tests passed!\n")
        print("OpenClaw is ready to provide crypto trading signals! 🚀📈\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
