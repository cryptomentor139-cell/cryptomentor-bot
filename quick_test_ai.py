"""
Quick test untuk verify AI method exists dan bisa dipanggil
Tests speed optimization dengan different models
"""
import asyncio
import time
from deepseek_ai import DeepSeekAI

async def test():
    print("Testing CryptoMentor AI Speed Optimization...")
    print("=" * 60)
    
    ai = DeepSeekAI()
    print(f"AI Available: {ai.available}")
    print(f"Model: {ai.model}")
    print("=" * 60)
    
    # Check if method exists
    if hasattr(ai, 'analyze_market_simple'):
        print("✅ analyze_market_simple() method EXISTS")
    else:
        print("❌ analyze_market_simple() method NOT FOUND")
        return
    
    # Test with mock data
    mock_data = {
        'price': 95000.50,
        'change_24h': 3.5,
        'volume_24h': 45000000000,
        'high_24h': 96000,
        'low_24h': 92000
    }
    
    print("\nTesting with mock BTC data...")
    print(f"Price: ${mock_data['price']:,.2f}")
    print(f"Change: {mock_data['change_24h']:+.2f}%")
    print("=" * 60)
    
    if ai.available:
        print("\n⏱️  Measuring response time...")
        print("Calling AI (please wait)...\n")
        
        start_time = time.time()
        result = await ai.analyze_market_simple('BTC', mock_data, 'id')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print("=" * 60)
        print(f"⏱️  RESPONSE TIME: {response_time:.2f} seconds")
        print("=" * 60)
        
        # Evaluate speed
        if response_time < 5:
            print("✅ EXCELLENT - Very fast response!")
        elif response_time < 8:
            print("✅ GOOD - Acceptable response time")
        elif response_time < 12:
            print("⚠️  SLOW - Consider using faster model")
        else:
            print("❌ TOO SLOW - Switch to gpt-3.5-turbo")
        
        print("\n📊 Speed Recommendations:")
        if response_time > 8:
            print("   Consider adding to .env:")
            print("   AI_MODEL=openai/gpt-3.5-turbo")
        
        if "CRYPTOMENTOR AI" in result:
            print("\n✅ AI Response received with correct branding!")
            print(f"\nFirst 200 chars:\n{result[:200]}...")
        else:
            print("\n⚠️ AI Response received but check branding:")
            print(f"\nFirst 200 chars:\n{result[:200]}...")
    else:
        print("⚠️ AI not available (no API key)")
        print("But method exists, so code structure is correct!")
        print("\nTo test with real API:")
        print("1. Add DEEPSEEK_API_KEY to .env")
        print("2. Optionally add AI_MODEL=openai/gpt-3.5-turbo for speed")

if __name__ == "__main__":
    asyncio.run(test())
