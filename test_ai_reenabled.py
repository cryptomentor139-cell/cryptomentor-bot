#!/usr/bin/env python3
"""
Test script to verify AI features are re-enabled and working
Tests Cerebras AI integration
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_cerebras_integration():
    """Test Cerebras AI integration"""
    print("=" * 60)
    print("Testing Cerebras AI Integration")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('CEREBRAS_API_KEY')
    if not api_key:
        print("❌ CEREBRAS_API_KEY not found in .env")
        return False
    
    print(f"✅ CEREBRAS_API_KEY found: {api_key[:20]}...")
    
    # Test import
    try:
        from cerebras_ai import CerebrasAI
        print("✅ cerebras_ai module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import cerebras_ai: {e}")
        return False
    
    # Test initialization
    try:
        cerebras = CerebrasAI()
        if not cerebras.available:
            print("❌ Cerebras AI not available")
            return False
        print("✅ Cerebras AI initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Cerebras: {e}")
        return False
    
    # Test market analysis
    print("\n" + "=" * 60)
    print("Test 1: Market Analysis (/ai btc)")
    print("=" * 60)
    
    try:
        import time
        start = time.time()
        
        # Mock market data
        market_data = {
            'price': 50000,
            'change_24h': 2.5,
            'volume_24h': 25000000000
        }
        
        analysis = await cerebras.analyze_market_simple('BTC', market_data, 'id')
        elapsed = time.time() - start
        
        print(f"✅ Analysis completed in {elapsed:.2f}s")
        print(f"\nResponse preview (first 200 chars):")
        print(analysis[:200] + "...")
        
        if elapsed > 2.0:
            print(f"⚠️ Warning: Response time {elapsed:.2f}s is slower than expected (target: <1s)")
        else:
            print(f"🚀 Excellent! Response time {elapsed:.2f}s is within target")
            
    except Exception as e:
        print(f"❌ Market analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test chat
    print("\n" + "=" * 60)
    print("Test 2: Chat (/chat)")
    print("=" * 60)
    
    try:
        start = time.time()
        
        response = await cerebras.chat_about_market(
            "Apa itu bull market?",
            'id'
        )
        elapsed = time.time() - start
        
        print(f"✅ Chat completed in {elapsed:.2f}s")
        print(f"\nResponse preview (first 200 chars):")
        print(response[:200] + "...")
        
        if elapsed > 2.0:
            print(f"⚠️ Warning: Response time {elapsed:.2f}s is slower than expected")
        else:
            print(f"🚀 Excellent! Response time {elapsed:.2f}s is within target")
            
    except Exception as e:
        print(f"❌ Chat failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test handlers import
    print("\n" + "=" * 60)
    print("Test 3: Handler Integration")
    print("=" * 60)
    
    try:
        from app.handlers_deepseek import handle_ai_analyze, handle_ai_chat, handle_ai_market_summary
        print("✅ All AI handlers imported successfully")
        print("   - handle_ai_analyze")
        print("   - handle_ai_chat")
        print("   - handle_ai_market_summary")
    except Exception as e:
        print(f"❌ Failed to import handlers: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nAI features are ready to use:")
    print("• /ai <symbol> - Market analysis")
    print("• /chat <message> - Chat with AI")
    print("• /aimarket - Global market summary")
    print("\nMenu button: 🤖 Ask AI")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_cerebras_integration())
    exit(0 if success else 1)
