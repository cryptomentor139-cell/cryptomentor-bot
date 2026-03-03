"""
Quick OpenClaw Test - Skip slow checks
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from openclaw_cli_bridge import get_openclaw_cli_bridge


def quick_test():
    """Quick test without slow doctor check"""
    
    print("=" * 60)
    print("OpenClaw Quick Test")
    print("=" * 60)
    
    bridge = get_openclaw_cli_bridge()
    
    # Test 1: Health check
    print("\n✓ Testing CLI accessibility...")
    is_healthy = bridge.check_health()
    
    if not is_healthy:
        print("❌ OpenClaw CLI not accessible!")
        return False
    
    print("✅ OpenClaw CLI is working!")
    
    # Test 2: Get version
    version = bridge.get_version()
    print(f"✅ Version: {version}")
    
    print("\n" + "=" * 60)
    print("🎉 OpenClaw CLI Bridge Ready!")
    print("=" * 60)
    
    print("\n📋 Integration Summary:")
    print("✓ OpenClaw CLI installed and accessible")
    print("✓ Python bridge working")
    print("✓ Ready to integrate with Telegram bot")
    
    print("\n🚀 Next Steps:")
    print("1. Configure ANTHROPIC_API_KEY in .env")
    print("2. Optionally start gateway: openclaw gateway")
    print("3. Add OpenClaw handlers to bot")
    
    return True


if __name__ == "__main__":
    try:
        success = quick_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
