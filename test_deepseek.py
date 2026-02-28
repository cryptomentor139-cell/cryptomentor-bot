"""
Test script untuk DeepSeek AI integration
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_deepseek_basic():
    """Test basic DeepSeek AI functionality"""
    print("🧪 Testing DeepSeek AI Integration...\n")
    
    # Import DeepSeek AI
    from deepseek_ai import DeepSeekAI
    
    # Initialize
    deepseek = DeepSeekAI()
    
    if not deepseek.available:
        print("❌ DeepSeek AI not available. Check your API key in .env file.")
        return False
    
    print("✅ DeepSeek AI initialized successfully\n")
    
    # Test 1: Market Analysis
    print("📊 Test 1: Market Analysis")
    print("-" * 50)
    
    market_data = {
        'price': 45234.56,
        'change_24h': 2.34,
        'volume_24h': 28500000000
    }
    
    try:
        analysis = await deepseek.analyze_market_with_reasoning(
            symbol='BTC',
            market_data=market_data,
            language='id'
        )
        
        print(f"Response length: {len(analysis)} characters")
        print(f"Preview: {analysis[:200]}...\n")
        print("✅ Market analysis test passed\n")
    except Exception as e:
        print(f"❌ Market analysis test failed: {e}\n")
        return False
    
    # Test 2: Chat
    print("💬 Test 2: Chat Feature")
    print("-" * 50)
    
    try:
        response = await deepseek.chat_about_market(
            user_message="Gimana cara baca candlestick?",
            language='id'
        )
        
        print(f"Response length: {len(response)} characters")
        print(f"Preview: {response[:200]}...\n")
        print("✅ Chat test passed\n")
    except Exception as e:
        print(f"❌ Chat test failed: {e}\n")
        return False
    
    # Test 3: API Call
    print("🔌 Test 3: Direct API Call")
    print("-" * 50)
    
    try:
        response = await deepseek._call_deepseek_api(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say hello in Indonesian.",
            max_tokens=100
        )
        
        if response:
            print(f"Response: {response}\n")
            print("✅ API call test passed\n")
        else:
            print("❌ API call returned None\n")
            return False
    except Exception as e:
        print(f"❌ API call test failed: {e}\n")
        return False
    
    print("=" * 50)
    print("🎉 All tests passed successfully!")
    print("=" * 50)
    
    return True


async def test_with_crypto_api():
    """Test DeepSeek with real CryptoAPI data"""
    print("\n🧪 Testing DeepSeek with Real Market Data...\n")
    
    try:
        from deepseek_ai import DeepSeekAI
        from crypto_api import CryptoAPI
        
        deepseek = DeepSeekAI()
        crypto_api = CryptoAPI()
        
        if not deepseek.available:
            print("❌ DeepSeek AI not available")
            return False
        
        # Get real BTC data
        print("📡 Fetching real BTC data from Binance...")
        btc_data = crypto_api.get_crypto_price('BTC', force_refresh=True)
        
        if 'error' in btc_data:
            print(f"❌ Failed to get BTC data: {btc_data['error']}")
            return False
        
        print(f"✅ Got BTC data: ${btc_data['price']:,.2f} ({btc_data['change_24h']:+.2f}%)\n")
        
        # Analyze with DeepSeek
        print("🤖 Analyzing with DeepSeek AI...")
        analysis = await deepseek.analyze_market_with_reasoning(
            symbol='BTC',
            market_data=btc_data,
            language='id'
        )
        
        print("\n" + "=" * 50)
        print("DEEPSEEK AI ANALYSIS:")
        print("=" * 50)
        print(analysis)
        print("=" * 50)
        
        print("\n✅ Real data test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Real data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("=" * 50)
    print("DEEPSEEK AI INTEGRATION TEST SUITE")
    print("=" * 50)
    print()
    
    # Check environment
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        print("Please add it to your .env file")
        return
    
    print(f"✅ API Key found: {api_key[:20]}...{api_key[-10:]}\n")
    
    # Run basic tests
    basic_passed = await test_deepseek_basic()
    
    if basic_passed:
        # Run real data test
        print("\n" + "=" * 50)
        real_passed = await test_with_crypto_api()
        
        if real_passed:
            print("\n🎊 ALL TESTS COMPLETED SUCCESSFULLY! 🎊")
        else:
            print("\n⚠️ Some tests failed. Check the output above.")
    else:
        print("\n❌ Basic tests failed. Fix issues before proceeding.")


if __name__ == "__main__":
    asyncio.run(main())
