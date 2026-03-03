"""
Test OpenClaw Environment Variables
Verify all API keys are properly passed to OpenClaw CLI
"""

import sys
import os

# Load .env file
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from openclaw_cli_bridge import get_openclaw_cli_bridge


def test_env_vars():
    """Test that all environment variables are properly set"""
    
    print("=" * 60)
    print("OpenClaw Environment Variables Test")
    print("=" * 60)
    
    bridge = get_openclaw_cli_bridge()
    
    # Check which API keys are available
    api_keys = {
        'ANTHROPIC_API_KEY': 'Claude AI (Primary)',
        'OPENCLAW_API_KEY': 'OpenClaw',
        'DEEPSEEK_API_KEY': 'DeepSeek AI',
        'CEREBRAS_API_KEY': 'Cerebras AI',
        'CRYPTONEWS_API_KEY': 'Crypto News',
        'HELIUS_API_KEY': 'Helius RPC (Solana)',
        'CRYPTOCOMPARE_API_KEY': 'CryptoCompare',
        'SUPABASE_URL': 'Supabase Database',
        'PGHOST': 'PostgreSQL Database',
        'CONWAY_API_URL': 'Conway/Automaton API',
        'TELEGRAM_BOT_TOKEN': 'Telegram Bot',
        'ENCRYPTION_KEY': 'Encryption',
        'SESSION_SECRET': 'Session Security'
    }
    
    print("\n📋 Available API Keys & Services:")
    print("-" * 60)
    
    available_count = 0
    missing_count = 0
    
    for key, description in api_keys.items():
        if key in bridge.env and bridge.env[key]:
            # Mask the key for security
            value = bridge.env[key]
            if len(value) > 20:
                masked = f"{value[:8]}...{value[-4:]}"
            else:
                masked = f"{value[:4]}...{value[-2:]}"
            
            print(f"✅ {description:30} ({key})")
            print(f"   Value: {masked}")
            available_count += 1
        else:
            print(f"❌ {description:30} ({key})")
            missing_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"   ✅ Available: {available_count}/{len(api_keys)}")
    print(f"   ❌ Missing: {missing_count}/{len(api_keys)}")
    print("=" * 60)
    
    # Check critical keys
    critical_keys = ['ANTHROPIC_API_KEY', 'OPENCLAW_API_KEY']
    critical_available = all(
        key in bridge.env and bridge.env[key] 
        for key in critical_keys
    )
    
    if critical_available:
        print("\n✅ CRITICAL KEYS: All present")
        print("   OpenClaw can run autonomously!")
    else:
        print("\n⚠️ CRITICAL KEYS: Some missing")
        print("   OpenClaw may have limited functionality")
    
    # Additional capabilities check
    print("\n🎯 Autonomous Capabilities:")
    print("-" * 60)
    
    capabilities = {
        'AI Reasoning': 'ANTHROPIC_API_KEY' in bridge.env,
        'Alternative AI': 'DEEPSEEK_API_KEY' in bridge.env or 'CEREBRAS_API_KEY' in bridge.env,
        'Crypto Data': 'CRYPTONEWS_API_KEY' in bridge.env or 'CRYPTOCOMPARE_API_KEY' in bridge.env,
        'Blockchain Data': 'HELIUS_API_KEY' in bridge.env,
        'Data Persistence': 'SUPABASE_URL' in bridge.env or 'PGHOST' in bridge.env,
        'Autonomous Trading': 'CONWAY_API_URL' in bridge.env,
        'Notifications': 'TELEGRAM_BOT_TOKEN' in bridge.env,
        'Security': 'ENCRYPTION_KEY' in bridge.env
    }
    
    for capability, available in capabilities.items():
        status = "✅ Enabled" if available else "❌ Disabled"
        print(f"{status:15} {capability}")
    
    enabled_count = sum(1 for v in capabilities.values() if v)
    print(f"\n📊 Capabilities: {enabled_count}/{len(capabilities)} enabled")
    
    if enabled_count >= 6:
        print("\n🚀 Status: FULLY AUTONOMOUS")
        print("   OpenClaw has access to all major services!")
    elif enabled_count >= 4:
        print("\n✅ Status: MOSTLY AUTONOMOUS")
        print("   OpenClaw can operate with most features")
    else:
        print("\n⚠️ Status: LIMITED AUTONOMY")
        print("   Some features may not work")
    
    return critical_available


if __name__ == "__main__":
    try:
        success = test_env_vars()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
