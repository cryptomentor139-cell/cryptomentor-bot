#!/usr/bin/env python3
"""
Test script for new API integrations
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from crypto_api import CryptoAPI
    from ai_assistant import AIAssistant
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    sys.exit(1)

def test_new_apis():
    """Test all API integrations"""
    print("🧪 CryptoMentor AI - API Integration Test")
    print("=" * 50)

    connection_results = {
        'working_apis': 0,
        'apis': {}
    }

    try:
        # Test CryptoAPI
        print("\n📡 Testing CryptoAPI...")
        crypto_api = CryptoAPI()

        # Test price retrieval
        btc_price = crypto_api.get_crypto_price('BTC')
        if btc_price and btc_price.get('success'):
            print(f"✅ CryptoAPI working - BTC: ${btc_price.get('price', 0):,.2f}")
            connection_results['apis']['CryptoAPI'] = {'status': 'success', 'price': btc_price.get('price')}
            connection_results['working_apis'] += 1
        else:
            print(f"❌ CryptoAPI failed - {btc_price.get('error', 'Unknown error')}")
            connection_results['apis']['CryptoAPI'] = {'status': 'failed', 'error': btc_price.get('error', 'Unknown error')}

        # Test AI Assistant
        print("\n🤖 Testing AI Assistant...")
        ai = AIAssistant()

        # Test basic analysis
        analysis = ai.get_ai_response("What is Bitcoin?", 'en')
        if analysis and len(analysis) > 50:
            print("✅ AI Assistant working")
            connection_results['apis']['AI_Assistant'] = {'status': 'success'}
            connection_results['working_apis'] += 1
        else:
            print("❌ AI Assistant failed")
            connection_results['apis']['AI_Assistant'] = {'status': 'failed', 'error': 'Short or no response'}

        # Summary
        print(f"\n📊 Test Results:")
        print(f"✅ Working APIs: {connection_results['working_apis']}")
        print(f"❌ Failed APIs: {len(connection_results['apis']) - connection_results['working_apis']}")

        # Recommendations
        if connection_results.get('working_apis', 0) < 2:
            print("\n💡 Recommendations:")
            for api_name, api_result in connection_results.get('apis', {}).items():
                if api_result.get('status') != 'success':
                    print(f"  - Fix {api_name}: {api_result.get('error', 'Unknown error')}")

        return True

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_new_apis()