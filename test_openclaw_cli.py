#!/usr/bin/env python3
"""
Test OpenClaw CLI Bridge
Test direct CLI integration
"""

import sys
from app.openclaw_cli_bridge import OpenClawCLIBridge

def test_cli_installation():
    """Test if OpenClaw CLI is installed"""
    print("=" * 60)
    print("🧪 Testing OpenClaw CLI Installation")
    print("=" * 60)
    
    bridge = OpenClawCLIBridge()
    
    # Get version
    result = bridge.execute_command("--version")
    
    if result["success"]:
        print(f"✅ OpenClaw CLI installed")
        print(f"   Version: {result['stdout'].strip()}")
        return True
    else:
        print(f"❌ OpenClaw CLI not found")
        print(f"   Error: {result.get('error')}")
        print("\n📋 To install OpenClaw:")
        print("   iwr -useb https://openclaw.ai/install.ps1 | iex")
        return False

def test_cli_info():
    """Test getting OpenClaw info"""
    print("\n" + "=" * 60)
    print("🧪 Testing OpenClaw Info")
    print("=" * 60)
    
    bridge = OpenClawCLIBridge()
    result = bridge.get_info()
    
    if result["success"]:
        print("✅ Got OpenClaw info:")
        info = result.get("info", {})
        for key, value in info.items():
            print(f"   • {key}: {value}")
        return True
    else:
        print(f"⚠️ Could not get info: {result.get('error')}")
        return False

def test_cli_chat():
    """Test chat via CLI"""
    print("\n" + "=" * 60)
    print("🧪 Testing OpenClaw CLI Chat")
    print("=" * 60)
    
    bridge = OpenClawCLIBridge()
    
    print("\n1️⃣ Sending test message...")
    print("   Message: 'What is 2+2?'")
    
    result = bridge.chat(
        message="What is 2+2? Answer in one sentence.",
        model="openrouter/openai/gpt-4.1"
    )
    
    if result["success"]:
        print(f"✅ Got response:")
        print(f"   {result['response']}")
        return True
    else:
        print(f"❌ Chat failed: {result.get('error')}")
        return False

def test_cli_task():
    """Test running task via CLI"""
    print("\n" + "=" * 60)
    print("🧪 Testing OpenClaw CLI Task Execution")
    print("=" * 60)
    
    bridge = OpenClawCLIBridge()
    
    print("\n1️⃣ Running test task...")
    print("   Task: 'List 3 popular cryptocurrencies'")
    
    result = bridge.run_task(
        task="List 3 popular cryptocurrencies with their symbols. Be concise.",
        model="openrouter/openai/gpt-4.1"
    )
    
    if result["success"]:
        print(f"✅ Task completed:")
        print(f"   {result['output'][:200]}...")
        return True
    else:
        print(f"❌ Task failed: {result.get('error')}")
        return False

def main():
    """Run all tests"""
    print("\n🚀 OpenClaw CLI Bridge Test Suite\n")
    
    tests = [
        ("CLI Installation", test_cli_installation),
        ("CLI Info", test_cli_info),
        ("CLI Chat", test_cli_chat),
        ("CLI Task", test_cli_task)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            if not result and test_name == "CLI Installation":
                print("\n⚠️ OpenClaw CLI not installed. Stopping tests.")
                break
                
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\n🎉 OpenClaw CLI integration is working!")
        print("\nNext steps:")
        print("1. Integrate CLI bridge into bot")
        print("2. Add CLI-based commands")
        print("3. Test with Telegram bot")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nTroubleshooting:")
        print("1. Install OpenClaw: iwr -useb https://openclaw.ai/install.ps1 | iex")
        print("2. Verify installation: openclaw --version")
        print("3. Check OpenRouter API key in auth-profiles.json")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
