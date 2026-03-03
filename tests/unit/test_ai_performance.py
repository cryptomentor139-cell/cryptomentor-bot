"""
Test AI Performance - Measure actual response times
"""
import asyncio
import time
from deepseek_ai import DeepSeekAI

async def test_ai_speed():
    """Test AI response time with real API call"""
    print("=" * 60)
    print("🧪 AI PERFORMANCE TEST")
    print("=" * 60)
    
    ai = DeepSeekAI()
    
    if not ai.available:
        print("❌ AI not available (no API key)")
        return
    
    print(f"\n✅ AI Model: {ai.model}")
    print(f"✅ API Key: {ai.api_key[:20]}...")
    print(f"✅ Base URL: {ai.base_url}")
    
    # Test data
    mock_data = {
        'price': 70000,
        'change_24h': 2.5,
        'volume_24h': 45000000000,
        'high_24h': 71000,
        'low_24h': 69000
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST 1: Simple Market Analysis")
    print("=" * 60)
    
    print("\n⏱️  Starting timer...")
    start_time = time.time()
    
    try:
        result = await ai.analyze_market_simple('BTC', mock_data, 'id')
        end_time = time.time()
        
        elapsed = end_time - start_time
        
        print(f"\n⏱️  Response Time: {elapsed:.2f} seconds")
        print("=" * 60)
        
        # Evaluate performance
        if elapsed < 5:
            print("✅ EXCELLENT - Very fast!")
            status = "EXCELLENT"
        elif elapsed < 10:
            print("✅ GOOD - Acceptable speed")
            status = "GOOD"
        elif elapsed < 20:
            print("⚠️  SLOW - Could be better")
            status = "SLOW"
        elif elapsed < 60:
            print("❌ VERY SLOW - Check network/API")
            status = "VERY SLOW"
        else:
            print("❌ TIMEOUT - API problem!")
            status = "TIMEOUT"
        
        # Check response
        if "timeout" in result.lower():
            print("\n❌ API Timeout detected!")
            print("   OpenRouter API is slow or down")
        elif "CRYPTOMENTOR AI" in result:
            print("\n✅ Response received with correct branding")
            print(f"\nFirst 200 chars:\n{result[:200]}...")
        else:
            print("\n⚠️  Response received but check content")
        
        # Performance summary
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"\nModel: {ai.model}")
        print(f"Response Time: {elapsed:.2f}s")
        print(f"Status: {status}")
        
        if status in ["SLOW", "VERY SLOW", "TIMEOUT"]:
            print("\n⚠️  PERFORMANCE ISSUES DETECTED!")
            print("\n🔧 Recommended Actions:")
            print("   1. Check OpenRouter API status")
            print("   2. Test network latency: ping openrouter.ai")
            print("   3. Try different model in .env:")
            print("      AI_MODEL=anthropic/claude-instant-v1")
            print("   4. Consider switching to direct OpenAI API")
            print("   5. Check server location (closer to US = faster)")
        else:
            print("\n✅ Performance is acceptable!")
        
        return elapsed
        
    except asyncio.TimeoutError:
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"\n❌ TIMEOUT after {elapsed:.2f} seconds")
        print("\n🔧 This means:")
        print("   - OpenRouter API is very slow")
        print("   - Network issues")
        print("   - API endpoint down")
        print("\n💡 Solutions:")
        print("   1. Wait and try again later")
        print("   2. Switch to different model")
        print("   3. Use direct OpenAI API")
        return None
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_multiple_requests():
    """Test multiple requests to check consistency"""
    print("\n" + "=" * 60)
    print("📊 TEST 2: Multiple Requests (Consistency Check)")
    print("=" * 60)
    
    ai = DeepSeekAI()
    
    if not ai.available:
        print("❌ AI not available")
        return
    
    mock_data = {
        'price': 70000,
        'change_24h': 2.5,
        'volume_24h': 45000000000,
        'high_24h': 71000,
        'low_24h': 69000
    }
    
    times = []
    
    for i in range(3):
        print(f"\n🔄 Request {i+1}/3...")
        start = time.time()
        
        try:
            result = await ai.analyze_market_simple('BTC', mock_data, 'id')
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"   ⏱️  {elapsed:.2f}s")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print("\n" + "=" * 60)
        print("📊 CONSISTENCY RESULTS")
        print("=" * 60)
        print(f"\nAverage: {avg_time:.2f}s")
        print(f"Fastest: {min_time:.2f}s")
        print(f"Slowest: {max_time:.2f}s")
        print(f"Variance: {max_time - min_time:.2f}s")
        
        if max_time - min_time > 5:
            print("\n⚠️  HIGH VARIANCE - Inconsistent performance")
            print("   API response times are unpredictable")
        else:
            print("\n✅ CONSISTENT - Stable performance")

async def main():
    """Run all tests"""
    print("\n🚀 AI Performance Testing Suite")
    print("Testing OpenRouter API with configured model")
    print()
    
    # Test 1: Single request
    elapsed = await test_ai_speed()
    
    # Test 2: Multiple requests (only if first test succeeded)
    if elapsed and elapsed < 30:
        await test_multiple_requests()
    else:
        print("\n⚠️  Skipping consistency test due to slow/failed first test")
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RECOMMENDATIONS")
    print("=" * 60)
    
    if elapsed and elapsed < 10:
        print("\n✅ AI performance is GOOD!")
        print("   No action needed.")
    elif elapsed and elapsed < 20:
        print("\n⚠️  AI performance is ACCEPTABLE but could be better")
        print("\n💡 Optional improvements:")
        print("   - Try different model")
        print("   - Add response caching")
        print("   - Use CDN/edge computing")
    else:
        print("\n❌ AI performance is POOR!")
        print("\n🔧 Required actions:")
        print("   1. Check OpenRouter API status: https://status.openrouter.ai")
        print("   2. Test network: ping openrouter.ai")
        print("   3. Try different model:")
        print("      AI_MODEL=anthropic/claude-instant-v1")
        print("   4. Consider direct OpenAI API:")
        print("      - Faster")
        print("      - More reliable")
        print("      - Better support")
        print("   5. Check server location")
        print("      - Closer to US = faster")
        print("      - Use VPN if needed")
    
    print()

if __name__ == "__main__":
    asyncio.run(main())
