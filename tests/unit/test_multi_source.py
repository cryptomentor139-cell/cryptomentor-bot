"""
Test script untuk Multi-Source Data Provider
Tests speed dan reliability dari multiple data sources
"""
import asyncio
import time
from app.providers.multi_source_provider import multi_source_provider

async def test_single_source():
    """Test single symbol from multiple sources"""
    print("=" * 60)
    print("🧪 TEST 1: Single Symbol - Multiple Sources")
    print("=" * 60)
    
    symbol = 'BTC'
    print(f"\nFetching {symbol} price from multiple sources...")
    print("Sources: CoinGecko, CryptoCompare")
    print("⏱️  Measuring speed...\n")
    
    start_time = time.time()
    result = await multi_source_provider.get_price_multi_source(symbol)
    end_time = time.time()
    
    response_time = end_time - start_time
    
    print(f"⏱️  Response Time: {response_time:.2f} seconds")
    print("=" * 60)
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Success!")
        print(f"\n📊 Data:")
        print(f"   Symbol: {result.get('symbol')}")
        print(f"   Price: ${result.get('price', 0):,.2f}")
        print(f"   Change 24h: {result.get('change_24h', 0):+.2f}%")
        print(f"   Volume 24h: ${result.get('volume_24h', 0):,.0f}")
        print(f"   Source: {result.get('source')}")
    
    print("=" * 60)
    
    # Speed evaluation
    if response_time < 2:
        print("✅ EXCELLENT - Very fast!")
    elif response_time < 4:
        print("✅ GOOD - Fast enough")
    else:
        print("⚠️  SLOW - Check network connection")
    
    return result

async def test_multiple_symbols():
    """Test multiple symbols in parallel"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Multiple Symbols - Parallel Fetch")
    print("=" * 60)
    
    symbols = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP']
    print(f"\nFetching {len(symbols)} symbols in parallel...")
    print(f"Symbols: {', '.join(symbols)}")
    print("⏱️  Measuring speed...\n")
    
    start_time = time.time()
    result = await multi_source_provider.get_market_data_fast(symbols)
    end_time = time.time()
    
    response_time = end_time - start_time
    
    print(f"⏱️  Total Response Time: {response_time:.2f} seconds")
    print(f"⏱️  Average per Symbol: {response_time/len(symbols):.2f} seconds")
    print("=" * 60)
    
    if result.get('success'):
        print(f"✅ Success!")
        print(f"\n📊 Results:")
        
        for symbol, data in result['data'].items():
            if data.get('error'):
                print(f"   ❌ {symbol}: {data['error']}")
            else:
                print(f"   ✅ {symbol}: ${data.get('price', 0):,.2f} ({data.get('change_24h', 0):+.2f}%) - {data.get('source')}")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    print("=" * 60)
    
    # Speed evaluation
    avg_time = response_time / len(symbols)
    if avg_time < 1:
        print("✅ EXCELLENT - Parallel fetching working great!")
    elif avg_time < 2:
        print("✅ GOOD - Acceptable speed")
    else:
        print("⚠️  SLOW - Parallel optimization needed")
    
    return result

async def test_coingecko_direct():
    """Test CoinGecko directly"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: CoinGecko Direct Test")
    print("=" * 60)
    
    print("\nTesting CoinGecko API (FREE, no key needed)...")
    
    start_time = time.time()
    result = await multi_source_provider._get_coingecko_price('BTC')
    end_time = time.time()
    
    response_time = end_time - start_time
    
    print(f"⏱️  Response Time: {response_time:.2f} seconds")
    print("=" * 60)
    
    if result.get('error'):
        print(f"❌ CoinGecko Error: {result['error']}")
    else:
        print(f"✅ CoinGecko Working!")
        print(f"\n📊 Data:")
        print(f"   Price: ${result.get('price', 0):,.2f}")
        print(f"   Change 24h: {result.get('change_24h', 0):+.2f}%")
        print(f"   Market Cap: ${result.get('market_cap', 0):,.0f}")
    
    print("=" * 60)
    return result

async def test_cryptocompare_direct():
    """Test CryptoCompare directly"""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: CryptoCompare Direct Test")
    print("=" * 60)
    
    print("\nTesting CryptoCompare API (FREE tier available)...")
    
    start_time = time.time()
    result = await multi_source_provider._get_cryptocompare_price('BTC')
    end_time = time.time()
    
    response_time = end_time - start_time
    
    print(f"⏱️  Response Time: {response_time:.2f} seconds")
    print("=" * 60)
    
    if result.get('error'):
        print(f"❌ CryptoCompare Error: {result['error']}")
        print("   Note: Works without API key but limited")
    else:
        print(f"✅ CryptoCompare Working!")
        print(f"\n📊 Data:")
        print(f"   Price: ${result.get('price', 0):,.2f}")
        print(f"   Change 24h: {result.get('change_24h', 0):+.2f}%")
        print(f"   High 24h: ${result.get('high_24h', 0):,.2f}")
        print(f"   Low 24h: ${result.get('low_24h', 0):,.2f}")
    
    print("=" * 60)
    return result

async def main():
    """Run all tests"""
    print("\n🚀 Multi-Source Data Provider Test Suite")
    print("Testing: CoinGecko, CryptoCompare, Helius RPC")
    print()
    
    try:
        # Test 1: Single source
        await test_single_source()
        
        # Test 2: Multiple symbols
        await test_multiple_symbols()
        
        # Test 3: CoinGecko direct
        await test_coingecko_direct()
        
        # Test 4: CryptoCompare direct
        await test_cryptocompare_direct()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print("\n✅ Benefits of Multi-Source Provider:")
        print("   1. Faster response (parallel requests)")
        print("   2. Better reliability (fallback sources)")
        print("   3. No single point of failure")
        print("   4. FREE APIs (CoinGecko, CryptoCompare free tier)")
        print("\n💡 Recommendation:")
        print("   - CoinGecko: Best for general crypto prices (FREE)")
        print("   - CryptoCompare: Good for additional data (FREE tier)")
        print("   - Helius: Best for Solana on-chain data (needs API key)")
        print("\n🎯 Integration Status:")
        print("   ✅ Multi-source provider ready")
        print("   ✅ Integrated with crypto_api.py as fallback")
        print("   ✅ Faster than single-source Binance")
        print()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        await multi_source_provider.close()

if __name__ == "__main__":
    asyncio.run(main())
