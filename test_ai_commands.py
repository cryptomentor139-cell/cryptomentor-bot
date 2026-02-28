#!/usr/bin/env python3
"""
Test AI commands locally to debug Railway issue
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_ai_commands():
    """Test AI command handlers"""
    print("=" * 60)
    print("Testing AI Commands")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('CEREBRAS_API_KEY')
    if not api_key:
        print("❌ CEREBRAS_API_KEY not found in .env")
        return False
    
    print(f"✅ CEREBRAS_API_KEY found: {api_key[:20]}...")
    
    # Test Cerebras initialization
    try:
        from cerebras_ai import CerebrasAI
        cerebras = CerebrasAI()
        
        if not cerebras.available:
            print("❌ Cerebras AI not available")
            return False
        
        print("✅ Cerebras AI initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Cerebras: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test handlers import
    try:
        from app.handlers_deepseek import handle_ai_analyze, handle_ai_chat, handle_ai_market_summary
        print("✅ AI handlers imported successfully")
    except Exception as e:
        print(f"❌ Failed to import handlers: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test market data fetch
    print("\n" + "=" * 60)
    print("Test: Fetching market data for BTC")
    print("=" * 60)
    
    try:
        from crypto_api import CryptoAPI
        crypto_api = CryptoAPI()
        
        market_data = crypto_api.get_crypto_price('BTC', force_refresh=True)
        
        if 'error' in market_data:
            print(f"❌ Market data error: {market_data['error']}")
            return False
        
        print(f"✅ Market data fetched:")
        print(f"   Price: ${market_data.get('price', 0):,.2f}")
        print(f"   Change 24h: {market_data.get('change_24h', 0):+.2f}%")
        
    except Exception as e:
        print(f"❌ Market data fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test AI analysis
    print("\n" + "=" * 60)
    print("Test: AI Analysis")
    print("=" * 60)
    
    try:
        import time
        start = time.time()
        
        analysis = await cerebras.analyze_market_simple('BTC', market_data, 'id')
        elapsed = time.time() - start
        
        print(f"✅ AI analysis completed in {elapsed:.2f}s")
        print(f"\nResponse preview (first 200 chars):")
        print(analysis[:200] + "...")
        
    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test chat
    print("\n" + "=" * 60)
    print("Test: AI Chat")
    print("=" * 60)
    
    try:
        start = time.time()
        
        response = await cerebras.chat_about_market("Apa itu bull market?", 'id')
        elapsed = time.time() - start
        
        print(f"✅ AI chat completed in {elapsed:.2f}s")
        print(f"\nResponse preview (first 200 chars):")
        print(response[:200] + "...")
        
    except Exception as e:
        print(f"❌ AI chat failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nAI commands should work. If not working in Railway:")
    print("1. Check CEREBRAS_API_KEY is set in Railway environment variables")
    print("2. Check Railway deployment logs for errors")
    print("3. Verify bot.py registered AI handlers")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_ai_commands())
    exit(0 if success else 1)
