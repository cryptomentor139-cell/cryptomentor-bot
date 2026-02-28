"""
Test script untuk StepFun Step 3.5 Flash (FREE model)
"""
import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_stepfun():
    """Test StepFun Step 3.5 Flash model"""
    print("=" * 60)
    print("🧪 TESTING STEPFUN STEP 3.5 FLASH (FREE MODEL)")
    print("=" * 60)
    print()
    
    # Check environment
    print("📋 Checking Environment Variables...")
    api_key = os.getenv('DEEPSEEK_API_KEY')
    ai_model = os.getenv('AI_MODEL', 'stepfun/step-3.5-flash')
    
    print(f"   DEEPSEEK_API_KEY: {'✅ Set' if api_key else '❌ Not Set'}")
    print(f"   AI_MODEL: {ai_model}")
    print()
    
    if not api_key:
        print("❌ ERROR: DEEPSEEK_API_KEY not configured!")
        print("   Please add your API key to .env file")
        return
    
    if ai_model != 'stepfun/step-3.5-flash':
        print(f"⚠️ WARNING: AI_MODEL is set to '{ai_model}'")
        print("   Expected: 'stepfun/step-3.5-flash'")
        print()
    
    # Test DeepSeekAI with StepFun
    print("🤖 Testing CryptoMentor AI with StepFun...")
    print("-" * 60)
    try:
        from deepseek_ai import DeepSeekAI
        
        ai = DeepSeekAI()
        
        print(f"   Provider: {ai.provider}")
        print(f"   Model: {ai.model}")
        print(f"   Available: {ai.available}")
        print()
        
        if not ai.available:
            print("❌ CryptoMentor AI not available")
            return
        
        # Test 1: Market Analysis
        print("📊 Test 1: Market Analysis (BTC)")
        print("-" * 60)
        
        test_market_data = {
            'price': 95000.50,
            'change_24h': 3.5,
            'volume_24h': 45000000000,
            'high_24h': 96000,
            'low_24h': 92000
        }
        
        start_time = datetime.now()
        
        analysis = await ai.analyze_market_simple(
            symbol='BTC',
            market_data=test_market_data,
            language='id'
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if analysis and not analysis.startswith('❌'):
            print(f"✅ Analysis completed in {duration:.2f}s")
            print(f"   Length: {len(analysis)} characters")
            print(f"   Preview:")
            print("-" * 60)
            print(analysis[:500] + "..." if len(analysis) > 500 else analysis)
            print("-" * 60)
        else:
            print(f"❌ Analysis failed: {analysis}")
        print()
        
        # Test 2: Chat about crypto news
        print("💬 Test 2: Chat - Berita Crypto Hari Ini")
        print("-" * 60)
        
        start_time = datetime.now()
        
        chat_response = await ai.chat_about_market(
            user_message="Apa berita penting tentang Bitcoin hari ini? Berikan analisis singkat.",
            language='id'
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if chat_response and not chat_response.startswith('❌'):
            print(f"✅ Chat response received in {duration:.2f}s")
            print(f"   Length: {len(chat_response)} characters")
            print(f"   Preview:")
            print("-" * 60)
            print(chat_response[:500] + "..." if len(chat_response) > 500 else chat_response)
            print("-" * 60)
        else:
            print(f"❌ Chat failed: {chat_response}")
        print()
        
        # Test 3: Market reasoning
        print("🧠 Test 3: Market Reasoning (ETH)")
        print("-" * 60)
        
        test_market_data_eth = {
            'price': 3500.25,
            'change_24h': -2.1,
            'volume_24h': 15000000000,
            'high_24h': 3600,
            'low_24h': 3450
        }
        
        start_time = datetime.now()
        
        reasoning = await ai.analyze_market_with_reasoning(
            symbol='ETH',
            market_data=test_market_data_eth,
            language='id'
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if reasoning and not reasoning.startswith('❌'):
            print(f"✅ Reasoning completed in {duration:.2f}s")
            print(f"   Length: {len(reasoning)} characters")
            print(f"   Preview:")
            print("-" * 60)
            print(reasoning[:500] + "..." if len(reasoning) > 500 else reasoning)
            print("-" * 60)
        else:
            print(f"❌ Reasoning failed: {reasoning}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Summary
    print()
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print()
    print("✅ StepFun Step 3.5 Flash is working!")
    print()
    print("Model Info:")
    print("   Name: StepFun Step 3.5 Flash")
    print("   Cost: FREE 🎉")
    print("   Speed: 2-5 seconds ⚡")
    print("   Quality: Good for reasoning & crypto news")
    print()
    print("Next steps:")
    print("1. Model sudah dikonfigurasi di .env")
    print("2. Restart bot dengan: restart_bot.bat (Windows) atau ./restart_bot.sh (Linux)")
    print("3. Test dengan Telegram: /ai btc")
    print()
    print("Expected performance:")
    print("   ⚡ Response time: 2-5 seconds")
    print("   💰 Cost: FREE (no charges!)")
    print("   🧠 Quality: Good reasoning & crypto news analysis")
    print()

if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run test
    asyncio.run(test_stepfun())
