
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Bismillah.ai_assistant import AIAssistant
from Bismillah.crypto_api import CryptoAPI
from Bismillah.data_provider import DataProvider

async def main():
    try:
        print("🔄 Testing futures signals generation...")
        
        # Initialize components
        data_provider = DataProvider()
        crypto_api = CryptoAPI(data_provider)
        ai = AIAssistant()
        
        # Test with small set
        test_symbols = ['BTC', 'ETH']
        print(f"Testing with symbols: {test_symbols}")
        
        result = await ai.generate_futures_signals('test', crypto_api, test_symbols)
        
        assert isinstance(result, list), f"Result should be list, got {type(result)}"
        assert all(isinstance(x, dict) for x in result), "All items should be dict"
        
        print(f"✅ Success! Generated {len(result)} signals")
        for i, signal in enumerate(result[:2]):
            print(f"  {i+1}. {signal.get('coin', 'Unknown')}: {signal.get('error', 'OK')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
