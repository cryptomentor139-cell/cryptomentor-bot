#!/usr/bin/env python3
"""
Test OpenClaw Gateway Connection
Run this after starting OpenClaw gateway
"""

import sys
import time
import requests
from app.openclaw_gateway_bridge import OpenClawGatewayBridge

def test_gateway_connection():
    """Test basic gateway connection"""
    print("=" * 60)
    print("🧪 OpenClaw Gateway Connection Test")
    print("=" * 60)
    
    # Initialize bridge
    print("\n1️⃣ Initializing gateway bridge...")
    bridge = OpenClawGatewayBridge()
    print(f"   Gateway URL: {bridge.gateway_url}")
    print(f"   Auth Token: {bridge.auth_token[:20]}...")
    
    # Health check
    print("\n2️⃣ Testing gateway health...")
    is_healthy = bridge.health_check()
    
    if not is_healthy:
        print("   ❌ Gateway is NOT running or not accessible")
        print("\n📋 To start gateway:")
        print("   1. Open new terminal")
        print("   2. cd D:/OpenClaw")
        print("   3. openclaw gateway")
        print("   4. Wait for 'Gateway listening on port 18789'")
        print("   5. Run this test again")
        return False
    
    print("   ✅ Gateway is healthy!")
    
    # Get gateway info
    print("\n3️⃣ Getting gateway information...")
    info = bridge.get_gateway_info()
    
    if 'error' in info:
        print(f"   ⚠️ Could not get info: {info['error']}")
    else:
        print(f"   ✅ Gateway info retrieved:")
        for key, value in info.items():
            print(f"      • {key}: {value}")
    
    # List agents
    print("\n4️⃣ Listing existing agents...")
    agents = bridge.list_agents()
    
    if 'error' in agents:
        print(f"   ⚠️ Could not list agents: {agents['error']}")
    else:
        agent_list = agents.get('agents', [])
        print(f"   ✅ Found {len(agent_list)} agents")
        for agent in agent_list[:5]:  # Show first 5
            print(f"      • {agent.get('id')}: {agent.get('status')}")
    
    print("\n" + "=" * 60)
    print("✅ Gateway connection test PASSED!")
    print("=" * 60)
    return True

def test_spawn_agent():
    """Test spawning a simple agent"""
    print("\n" + "=" * 60)
    print("🤖 Testing Agent Spawn")
    print("=" * 60)
    
    bridge = OpenClawGatewayBridge()
    
    # Check health first
    if not bridge.health_check():
        print("❌ Gateway not running. Start gateway first.")
        return False
    
    print("\n1️⃣ Spawning test agent...")
    print("   Task: 'Say hello and tell me the current time'")
    
    result = bridge.spawn_agent(
        user_id=1187119989,  # Your user ID
        task="Say hello and tell me the current time",
        model="openrouter/openai/gpt-4.1"
    )
    
    if 'error' in result:
        print(f"   ❌ Failed to spawn agent: {result['error']}")
        if 'details' in result:
            print(f"   Details: {result['details']}")
        return False
    
    agent_id = result.get('agentId')
    print(f"   ✅ Agent spawned successfully!")
    print(f"   Agent ID: {agent_id}")
    
    # Wait a bit for agent to process
    print("\n2️⃣ Waiting for agent to process task...")
    time.sleep(5)
    
    # Get agent status
    print("\n3️⃣ Checking agent status...")
    status = bridge.get_agent_status(agent_id)
    
    if 'error' in status:
        print(f"   ⚠️ Could not get status: {status['error']}")
    else:
        print(f"   ✅ Agent status:")
        print(f"      • Status: {status.get('status')}")
        print(f"      • Progress: {status.get('progress', 'N/A')}")
    
    # Get agent logs
    print("\n4️⃣ Getting agent logs...")
    logs = bridge.get_agent_logs(agent_id, limit=10)
    
    if 'error' in logs:
        print(f"   ⚠️ Could not get logs: {logs['error']}")
    else:
        log_entries = logs.get('logs', [])
        print(f"   ✅ Retrieved {len(log_entries)} log entries:")
        for log in log_entries[:5]:  # Show first 5
            print(f"      • {log.get('timestamp')}: {log.get('message')[:50]}...")
    
    print("\n" + "=" * 60)
    print(f"✅ Agent spawn test PASSED!")
    print(f"   Agent ID: {agent_id}")
    print("=" * 60)
    
    return True

def test_chat_with_agent():
    """Test chatting with an agent"""
    print("\n" + "=" * 60)
    print("💬 Testing Agent Chat")
    print("=" * 60)
    
    bridge = OpenClawGatewayBridge()
    
    # First spawn an agent
    print("\n1️⃣ Spawning chat agent...")
    spawn_result = bridge.spawn_agent(
        user_id=1187119989,
        task="You are a helpful assistant. Answer questions concisely.",
        model="openrouter/openai/gpt-4.1"
    )
    
    if 'error' in spawn_result:
        print(f"   ❌ Failed to spawn: {spawn_result['error']}")
        return False
    
    agent_id = spawn_result.get('agentId')
    print(f"   ✅ Agent spawned: {agent_id}")
    
    # Wait for initialization
    time.sleep(3)
    
    # Send a message
    print("\n2️⃣ Sending message to agent...")
    print("   Message: 'What is 2+2?'")
    
    chat_result = bridge.chat_with_agent(
        agent_id=agent_id,
        message="What is 2+2?"
    )
    
    if 'error' in chat_result:
        print(f"   ❌ Chat failed: {chat_result['error']}")
        return False
    
    response = chat_result.get('response', 'No response')
    print(f"   ✅ Agent response:")
    print(f"      {response}")
    
    # Send another message
    print("\n3️⃣ Sending follow-up message...")
    print("   Message: 'What about 5*5?'")
    
    chat_result2 = bridge.chat_with_agent(
        agent_id=agent_id,
        message="What about 5*5?"
    )
    
    if 'error' in chat_result2:
        print(f"   ⚠️ Follow-up failed: {chat_result2['error']}")
    else:
        response2 = chat_result2.get('response', 'No response')
        print(f"   ✅ Agent response:")
        print(f"      {response2}")
    
    # Stop agent
    print("\n4️⃣ Stopping agent...")
    stop_result = bridge.stop_agent(agent_id)
    
    if 'error' in stop_result:
        print(f"   ⚠️ Could not stop: {stop_result['error']}")
    else:
        print(f"   ✅ Agent stopped")
    
    print("\n" + "=" * 60)
    print("✅ Chat test PASSED!")
    print("=" * 60)
    
    return True

def main():
    """Run all tests"""
    print("\n🚀 OpenClaw Gateway Test Suite")
    print("Make sure OpenClaw gateway is running first!")
    print("\nTo start gateway:")
    print("  1. Open new terminal")
    print("  2. cd D:/OpenClaw")
    print("  3. openclaw gateway")
    print("\nPress Enter when gateway is ready...")
    input()
    
    tests = [
        ("Gateway Connection", test_gateway_connection),
        ("Agent Spawn", test_spawn_agent),
        ("Agent Chat", test_chat_with_agent)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {test_name}")
            print(f"{'='*60}")
            result = test_func()
            results.append((test_name, result))
            
            if not result:
                print(f"\n⚠️ {test_name} failed. Stopping tests.")
                break
                
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
            break
    
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
        print("\n🎉 OpenClaw Gateway is working perfectly!")
        print("\nNext steps:")
        print("1. Integrate gateway commands into bot")
        print("2. Test with Telegram bot")
        print("3. Deploy to Railway")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nTroubleshooting:")
        print("1. Make sure gateway is running: openclaw gateway")
        print("2. Check gateway logs for errors")
        print("3. Verify auth token in openclaw.json")
        print("4. Try restarting gateway")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
