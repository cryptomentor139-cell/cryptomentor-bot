#!/usr/bin/env python3
"""
Test script for the fixed /analyze command
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ai_assistant import AIAssistant
    from crypto_api import CryptoAPI
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    sys.exit(1)

def test_analyze_command():
    """Test the analyze command functionality"""
    print("🧪 Testing /analyze command functionality")
    print("=" * 50)

    try:
        # Initialize components
        print("🔧 Initializing components...")
        crypto_api = CryptoAPI()
        ai_assistant = AIAssistant()

        # Test symbols to analyze
        test_symbols = ['BTC', 'ETH', 'SOL']

        for symbol in test_symbols:
            print(f"\n📊 Testing analysis for {symbol}...")

            try:
                # Test comprehensive analysis
                analysis = ai_assistant.get_comprehensive_analysis(
                    symbol=symbol,
                    snd_data={},
                    price_data={},
                    language='id',
                    crypto_api=crypto_api
                )

                if analysis and len(analysis) > 100:
                    print(f"✅ {symbol} analysis successful ({len(analysis)} chars)")

                    # Show preview
                    preview = analysis[:200] + "..." if len(analysis) > 200 else analysis
                    print(f"📝 Preview: {preview}")
                else:
                    print(f"❌ {symbol} analysis failed or too short")

            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
                import traceback
                traceback.print_exc()

        print("\n✅ Analyze command test completed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_analyze_command()