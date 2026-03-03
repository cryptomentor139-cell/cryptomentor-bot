"""
Test script untuk memverifikasi CryptoMentor AI berfungsi dengan baik
Menguji analyze_market_simple() yang tidak memerlukan OHLCV data
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_ai_analysis():
    """Test AI analysis dengan data BTC"""
    print("=" * 60)
    print("🧪 TEST CRYPTOMENTOR AI - MARKET ANALYSIS")
    print("=" * 60)
    
    # Import modules
    from deepseek_ai import DeepSeekAI
    from crypto_api import CryptoAPI
    
    # Initialize
    deepseek = DeepSeekAI()
    crypto_api = CryptoAPI()
    
    # Check if AI is available
    if not deepseek.available:
        print("❌ CryptoMentor AI tidak tersedia!")
        print("   Pastikan DEEPSEEK_API_KEY sudah diset di .env")
        return False
    
    print("✅ CryptoMentor AI tersedia\n")
    
    # Test 1: Get BTC market data
    print("📊 Test 1: Mengambil data market BTC...")
    market_data = crypto_api.get_crypto_price('BTC', force_refresh=True)
    
    if 'error' in market_data:
        print(f"❌ Error getting market data: {market_data['error']}")
        return False
    
    print(f"✅ Data BTC berhasil diambil:")
    print(f"   - Price: ${market_data.get('price', 0):,.2f}")
    print(f"   - Change 24h: {market_data.get('change_24h', 0):+.2f}%")
    print(f"   - Volume 24h: ${market_data.get('volume_24h', 0):,.0f}")
    print()
    
    # Test 2: AI Analysis (Simple - no OHLCV needed)
    print("🤖 Test 2: Meminta analisis dari CryptoMentor AI...")
    print("   (Mohon tunggu 5-10 detik...)\n")
    
    analysis = await deepseek.analyze_market_simple(
        symbol='BTC',
        market_data=market_data,
        language='id'
    )
    
    if "❌" in analysis or "Error" in analysis:
        print(f"❌ AI Analysis gagal:")
        print(analysis)
        return False
    
    print("✅ AI Analysis berhasil!")
    print("\n" + "=" * 60)
    print("📝 HASIL ANALISIS:")
    print("=" * 60)
    print(analysis)
    print("=" * 60)
    
    # Test 3: Chat with AI
    print("\n🤖 Test 3: Chat dengan CryptoMentor AI...")
    print("   (Mohon tunggu 5-10 detik...)\n")
    
    chat_response = await deepseek.chat_about_market(
        user_message="Gimana kondisi market crypto hari ini?",
        language='id'
    )
    
    if "❌" in chat_response or "Error" in chat_response:
        print(f"❌ Chat gagal:")
        print(chat_response)
        return False
    
    print("✅ Chat berhasil!")
    print("\n" + "=" * 60)
    print("💬 HASIL CHAT:")
    print("=" * 60)
    print(chat_response)
    print("=" * 60)
    
    return True

async def main():
    """Main test function"""
    print("\n🚀 Memulai test CryptoMentor AI...\n")
    
    success = await test_ai_analysis()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ SEMUA TEST BERHASIL!")
        print("=" * 60)
        print("\n📌 CryptoMentor AI siap digunakan!")
        print("\nCara menggunakan di bot:")
        print("1. /ai BTC - Analisis market Bitcoin")
        print("2. /chat gimana market hari ini? - Chat dengan AI")
        print("3. /aimarket - Summary market global")
    else:
        print("❌ TEST GAGAL!")
        print("=" * 60)
        print("\n🔧 Troubleshooting:")
        print("1. Pastikan DEEPSEEK_API_KEY ada di .env")
        print("2. Pastikan koneksi internet stabil")
        print("3. Cek log error di atas untuk detail")
    print()

if __name__ == "__main__":
    asyncio.run(main())
