#!/usr/bin/env python3
"""
Test DeepSeek AI secara langsung
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("🧪 Testing DeepSeek AI")
print("="*60)

# Test 1: Check API key
print("\n1️⃣ Checking API key...")
api_key = os.getenv('DEEPSEEK_API_KEY')
if api_key:
    print(f"   ✅ API key found: {api_key[:20]}...")
else:
    print("   ❌ API key NOT found!")
    print("   Check .env file for DEEPSEEK_API_KEY")
    exit(1)

# Test 2: Initialize DeepSeek
print("\n2️⃣ Initializing DeepSeek AI...")
try:
    from deepseek_ai import DeepSeekAI
    
    deepseek = DeepSeekAI()
    
    if deepseek.available:
        print("   ✅ DeepSeek AI initialized")
    else:
        print("   ❌ DeepSeek AI not available")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 3: Test chat function
print("\n3️⃣ Testing chat function...")
async def test_chat():
    try:
        response = await deepseek.chat_about_market(
            user_message="Apa itu Bitcoin?",
            language='id'
        )
        
        if response and len(response) > 50:
            print("   ✅ Chat function working!")
            print(f"   Response preview: {response[:200]}...")
            return True
        else:
            print(f"   ❌ Response too short or empty: {response}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test 4: Test analyze function
print("\n4️⃣ Testing analyze function...")
async def test_analyze():
    try:
        market_data = {
            'price': 43250.00,
            'change_24h': 2.5,
            'volume_24h': 28500000000
        }
        
        response = await deepseek.analyze_market_with_reasoning(
            symbol='BTC',
            market_data=market_data,
            language='id'
        )
        
        if response and len(response) > 50:
            print("   ✅ Analyze function working!")
            print(f"   Response preview: {response[:200]}...")
            return True
        else:
            print(f"   ❌ Response too short or empty: {response}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run tests
async def run_all_tests():
    chat_ok = await test_chat()
    analyze_ok = await test_analyze()
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    print(f"Chat function: {'✅ PASS' if chat_ok else '❌ FAIL'}")
    print(f"Analyze function: {'✅ PASS' if analyze_ok else '❌ FAIL'}")
    
    if chat_ok and analyze_ok:
        print("\n✅ All tests passed! DeepSeek AI is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        print("\n💡 Common issues:")
        print("   - Invalid API key")
        print("   - Network/firewall blocking OpenRouter")
        print("   - API rate limit exceeded")
        print("   - API service temporarily down")

asyncio.run(run_all_tests())
