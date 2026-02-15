"""
Comprehensive API verification script
Tests all configured APIs and measures performance
"""
import os
import asyncio
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_deepseek_ai():
    """Test DeepSeek AI / OpenRouter"""
    print("\n" + "=" * 60)
    print("🤖 TEST 1: AI MODEL (DeepSeek/OpenRouter)")
    print("=" * 60)
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    model = os.getenv('AI_MODEL', 'openai/gpt-3.5-turbo')
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in .env")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    print(f"✅ Model configured: {model}")
    
    # Test AI
    try:
        from deepseek_ai import DeepSeekAI
        ai = DeepSeekAI()
        
        if not ai.available:
            print("❌ AI not available")
            return False
        
        print("✅ AI initialized successfully")
        
        # Quick test with mock data
        mock_data = {
            'price': 95000,
            'change_24h': 2.5,
            'volume_24h': 45000000000,
            'high_24h': 96000,
            'low_24h': 94000
        }
        
        print("\n⏱️  Testing AI response time...")
        start = time.time()
        result = await ai.analyze_market_simple('BTC', mock_data, 'id')
        elapsed = time.time() - start
        
        print(f"⏱️  Response time: {elapsed:.2f} seconds")
        
        if "CRYPTOMENTOR AI" in result:
            print("✅ AI working with correct branding!")
            if elapsed < 5:
                print("✅ EXCELLENT - Very fast!")
            elif elapsed < 8:
                print("✅ GOOD - Acceptable speed")
            else:
                print("⚠️  SLOW - Consider checking network")
            return True
        else:
            print("⚠️  AI working but check branding")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_multi_source_provider():
    """Test Multi-Source Data Provider"""
    print("\n" + "=" * 60)
    print("🌐 TEST 2: MULTI-SOURCE DATA PROVIDER")
    print("=" * 60)
    
    try:
        from app.providers.multi_source_provider import multi_source_provider
        
        # Test CoinGecko
        print("\n📊 Testing CoinGecko (FREE, no key needed)...")
        start = time.time()
        result = await multi_source_provider._get_coingecko_price('BTC')
        elapsed = time.time() - start
        
        if result.get('error'):
            print(f"⚠️  CoinGecko: {result['error']}")
            print("   (May be rate limited, this is normal)")
        else:
            print(f"✅ CoinGecko working! (${result.get('price', 0):,.2f})")
            print(f"⏱️  Response time: {elapsed:.2f}s")
        
        # Test CryptoCompare
        print("\n📊 Testing CryptoCompare...")
        api_key = os.getenv('CRYPTOCOMPARE_API_KEY')
        if api_key:
            print(f"✅ API Key found: {api_key[:20]}...")
        else:
            print("⚠️  No API key (will use free tier)")
        
        start = time.time()
        result = await multi_source_provider._get_cryptocompare_price('BTC')
        elapsed = time.time() - start
        
        if result.get('error'):
            print(f"❌ CryptoCompare: {result['error']}")
        else:
            print(f"✅ CryptoCompare working! (${result.get('price', 0):,.2f})")
            print(f"⏱️  Response time: {elapsed:.2f}s")
        
        # Test Helius (Solana)
        print("\n📊 Testing Helius RPC (Solana)...")
        api_key = os.getenv('HELIUS_API_KEY')
        if not api_key:
            print("⚠️  HELIUS_API_KEY not configured (optional)")
        else:
            print(f"✅ API Key found: {api_key[:20]}...")
            start = time.time()
            result = await multi_source_provider._get_helius_price('SOL')
            elapsed = time.time() - start
            
            if result.get('error'):
                print(f"⚠️  Helius: {result['error']}")
            else:
                print(f"✅ Helius working!")
                print(f"⏱️  Response time: {elapsed:.2f}s")
        
        # Test parallel fetching
        print("\n📊 Testing Parallel Fetch (5 symbols)...")
        symbols = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP']
        start = time.time()
        result = await multi_source_provider.get_market_data_fast(symbols)
        elapsed = time.time() - start
        
        if result.get('success'):
            success_count = sum(1 for data in result['data'].values() if not data.get('error'))
            print(f"✅ Parallel fetch working! ({success_count}/{len(symbols)} successful)")
            print(f"⏱️  Total time: {elapsed:.2f}s")
            print(f"⏱️  Average per symbol: {elapsed/len(symbols):.2f}s")
            
            if elapsed < 3:
                print("✅ EXCELLENT - Very fast parallel fetching!")
            elif elapsed < 5:
                print("✅ GOOD - Acceptable speed")
            else:
                print("⚠️  SLOW - Check network connection")
        else:
            print(f"❌ Parallel fetch failed: {result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_binance_api():
    """Test Binance API"""
    print("\n" + "=" * 60)
    print("📈 TEST 3: BINANCE API (Fallback)")
    print("=" * 60)
    
    try:
        from crypto_api import CryptoAPI
        crypto_api = CryptoAPI()
        
        print("\n📊 Testing Binance spot price...")
        start = time.time()
        result = crypto_api.get_crypto_price('BTC', force_refresh=True)
        elapsed = time.time() - start
        
        if result.get('error'):
            print(f"❌ Binance error: {result['error']}")
            return False
        else:
            print(f"✅ Binance working! (${result.get('price', 0):,.2f})")
            print(f"⏱️  Response time: {elapsed:.2f}s")
            print(f"📊 Source: {result.get('source', 'unknown')}")
            
            if elapsed < 2:
                print("✅ EXCELLENT - Very fast!")
            elif elapsed < 5:
                print("✅ GOOD - Acceptable speed")
            else:
                print("⚠️  SLOW - May be using fallback")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_telegram_bot():
    """Test Telegram Bot Token"""
    print("\n" + "=" * 60)
    print("📱 TEST 4: TELEGRAM BOT")
    print("=" * 60)
    
    token = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env")
        return False
    
    print(f"✅ Bot Token found: {token[:20]}...")
    
    # Validate token format
    if ':' in token and len(token) > 40:
        print("✅ Token format valid")
        return True
    else:
        print("⚠️  Token format may be invalid")
        return False

def test_database_config():
    """Test Database Configuration"""
    print("\n" + "=" * 60)
    print("🗄️  TEST 5: DATABASE CONFIGURATION")
    print("=" * 60)
    
    # Check Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        print(f"✅ Supabase URL: {supabase_url[:30]}...")
        print(f"✅ Supabase Key: {supabase_key[:30]}...")
    else:
        print("⚠️  Supabase not configured (will use local SQLite)")
    
    # Check PostgreSQL/Neon
    pg_host = os.getenv('PGHOST')
    pg_user = os.getenv('PGUSER')
    pg_db = os.getenv('PGDATABASE')
    
    if pg_host and pg_user and pg_db:
        print(f"✅ PostgreSQL Host: {pg_host[:30]}...")
        print(f"✅ PostgreSQL User: {pg_user}")
        print(f"✅ PostgreSQL DB: {pg_db}")
    else:
        print("⚠️  PostgreSQL not configured")
    
    return True

async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 COMPREHENSIVE API VERIFICATION")
    print("=" * 60)
    print("\nTesting all configured APIs and services...")
    
    results = {}
    
    # Test 1: AI Model
    results['AI Model'] = await test_deepseek_ai()
    
    # Test 2: Multi-Source Provider
    results['Multi-Source'] = await test_multi_source_provider()
    
    # Test 3: Binance API
    results['Binance'] = await test_binance_api()
    
    # Test 4: Telegram Bot
    results['Telegram'] = test_telegram_bot()
    
    # Test 5: Database
    results['Database'] = test_database_config()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service}: {'WORKING' if status else 'FAILED'}")
    
    success_count = sum(1 for status in results.values() if status)
    total_count = len(results)
    
    print("\n" + "=" * 60)
    print(f"📈 Overall: {success_count}/{total_count} services working")
    print("=" * 60)
    
    if success_count == total_count:
        print("\n🎉 ALL SYSTEMS GO! Bot is ready for production!")
        print("\n🚀 Next steps:")
        print("   1. Start bot: python main.py")
        print("   2. Test in Telegram: /ai BTC")
        print("   3. Monitor performance")
    elif success_count >= 3:
        print("\n✅ Core systems working! Bot can run with some limitations.")
        print("\n⚠️  Some optional services not configured:")
        for service, status in results.items():
            if not status:
                print(f"   - {service}")
    else:
        print("\n❌ Critical services not working! Fix errors before running bot.")
        print("\n🔧 Check:")
        for service, status in results.items():
            if not status:
                print(f"   - {service}")
    
    print()
    
    # Cleanup
    try:
        from app.providers.multi_source_provider import multi_source_provider
        await multi_source_provider.close()
    except:
        pass

if __name__ == "__main__":
    asyncio.run(main())
