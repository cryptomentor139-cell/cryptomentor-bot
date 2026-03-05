"""
Test Real-Time Crypto Data Tools
Verify that tools are working correctly
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_crypto_price_tool():
    """Test get_crypto_price tool"""
    print("=" * 60)
    print("TEST 1: get_crypto_price Tool")
    print("=" * 60)
    
    try:
        from app.openclaw_langchain_agent_simple import get_crypto_price
        
        # Test Bitcoin
        print("\n📊 Testing BTC price fetch...")
        result = get_crypto_price.invoke({"symbol": "BTC"})
        print(f"Result:\n{result}")
        
        if "Price:" in result and "$" in result:
            print("✅ BTC price fetched successfully")
        else:
            print("❌ BTC price fetch failed")
            return False
        
        # Test Ethereum
        print("\n📊 Testing ETH price fetch...")
        result = get_crypto_price.invoke({"symbol": "ETH"})
        print(f"Result:\n{result}")
        
        if "Price:" in result and "$" in result:
            print("✅ ETH price fetched successfully")
        else:
            print("❌ ETH price fetch failed")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_binance_price_tool():
    """Test get_binance_price tool"""
    print("\n" + "=" * 60)
    print("TEST 2: get_binance_price Tool")
    print("=" * 60)
    
    try:
        from app.openclaw_langchain_agent_simple import get_binance_price
        
        # Test BTCUSDT
        print("\n📊 Testing BTCUSDT price fetch...")
        result = get_binance_price.invoke({"symbol": "BTCUSDT"})
        print(f"Result:\n{result}")
        
        if "Price:" in result and "$" in result:
            print("✅ BTCUSDT price fetched successfully")
        else:
            print("❌ BTCUSDT price fetch failed")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_prices_tool():
    """Test get_multiple_crypto_prices tool"""
    print("\n" + "=" * 60)
    print("TEST 3: get_multiple_crypto_prices Tool")
    print("=" * 60)
    
    try:
        from app.openclaw_langchain_agent_simple import get_multiple_crypto_prices
        
        # Test multiple coins
        print("\n📊 Testing multiple crypto prices fetch...")
        result = get_multiple_crypto_prices.invoke({"symbols": ["BTC", "ETH", "SOL"]})
        print(f"Result:\n{result}")
        
        if "BTC:" in result and "ETH:" in result and "SOL:" in result:
            print("✅ Multiple prices fetched successfully")
        else:
            print("❌ Multiple prices fetch failed")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_tool_calling():
    """Test agent's ability to call tools"""
    print("\n" + "=" * 60)
    print("TEST 4: Agent Tool Calling")
    print("=" * 60)
    
    try:
        from app.openclaw_langchain_agent_simple import get_openclaw_agent
        
        agent = get_openclaw_agent()
        print("✅ Agent initialized")
        
        # Test with a price query
        test_user_id = 1187119989  # Admin ID from .env
        test_message = "What's the current Bitcoin price?"
        
        print(f"\n📝 Testing message: '{test_message}'")
        print("🔄 Processing...")
        
        result = await agent.chat(
            user_id=test_user_id,
            message=test_message,
            deduct_credits=False,  # Don't deduct for test
            is_admin=True  # Test as admin
        )
        
        if result['success']:
            response = result['response']
            print(f"\n✅ Agent response received:")
            print(f"Response: {response[:200]}...")
            
            # Check if response contains real-time data
            if "$" in response and any(word in response.lower() for word in ['price', 'btc', 'bitcoin']):
                print("\n✅ Response contains price data")
                
                # Check if it looks like real-time data
                if "24h" in response or "change" in response.lower():
                    print("✅ Response includes market data (likely real-time)")
                    return True
                else:
                    print("⚠️ Response might not be using real-time data")
                    return False
            else:
                print("❌ Response doesn't contain expected price data")
                return False
        else:
            print(f"❌ Agent chat failed: {result.get('error')}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_descriptions():
    """Test that tools have proper descriptions"""
    print("\n" + "=" * 60)
    print("TEST 5: Tool Descriptions")
    print("=" * 60)
    
    try:
        from app.openclaw_langchain_agent_simple import OpenClawSimpleAgent
        
        agent = OpenClawSimpleAgent()
        
        print("\n📋 Base Tools:")
        for tool in agent.base_tools:
            print(f"\n  • {tool.name}")
            print(f"    Description: {tool.description[:100]}...")
        
        print("\n🔑 Admin Tools:")
        for tool in agent.admin_tools:
            print(f"\n  • {tool.name}")
            print(f"    Description: {tool.description[:100]}...")
        
        # Check if descriptions are informative
        for tool in agent.base_tools:
            if len(tool.description) < 20:
                print(f"⚠️ Tool {tool.name} has short description")
                return False
        
        print("\n✅ All tools have proper descriptions")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 REAL-TIME CRYPTO DATA TOOLS - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run synchronous tests
    results.append(("Crypto Price Tool", test_crypto_price_tool()))
    results.append(("Binance Price Tool", test_binance_price_tool()))
    results.append(("Multiple Prices Tool", test_multiple_prices_tool()))
    results.append(("Tool Descriptions", test_tool_descriptions()))
    
    # Run async test
    results.append(("Agent Tool Calling", await test_agent_tool_calling()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        print("\n🎉 Real-time crypto data tools are working correctly!")
    else:
        print(f"⚠️ {total - passed} test(s) failed")
        print("\n🔧 Please check the errors above")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
