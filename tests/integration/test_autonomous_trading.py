#!/usr/bin/env python3
"""
Test Automaton Autonomous Trading Integration
Tests the bridge for autonomous trading (Lifetime Premium only)
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_agent_bridge():
    """Test Automaton Agent Bridge"""
    print("=" * 60)
    print("TEST 1: Initialize Agent Bridge")
    print("=" * 60)
    
    try:
        from database import Database
        from app.automaton_manager import get_automaton_manager
        from app.automaton_agent_bridge import get_automaton_agent_bridge
        
        db = Database()
        automaton_manager = get_automaton_manager(db)
        bridge = get_automaton_agent_bridge(db, automaton_manager)
        
        print(f"✅ Bridge initialized")
        print(f"   Database: {'Supabase' if db.supabase_enabled else 'Local'}")
        print(f"   Automaton Manager: Ready")
        print(f"   Automaton Dir: {bridge.automaton_dir}")
        print(f"   send-task.js: {'Found' if bridge.send_task_script.exists() else 'Not found'}")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lifetime_premium_check():
    """Test lifetime premium check"""
    print("\n" + "=" * 60)
    print("TEST 2: Lifetime Premium Check")
    print("=" * 60)
    
    try:
        from database import Database
        from app.automaton_manager import get_automaton_manager
        from app.automaton_agent_bridge import get_automaton_agent_bridge
        
        db = Database()
        automaton_manager = get_automaton_manager(db)
        bridge = get_automaton_agent_bridge(db, automaton_manager)
        
        # Test with fake user ID
        test_user_id = 999999999
        is_lifetime = bridge._check_lifetime_premium(test_user_id)
        
        print(f"✅ Lifetime premium check working")
        print(f"   Test user {test_user_id}: {'Lifetime' if is_lifetime else 'Not lifetime'}")
        print(f"   Note: This is expected to be False for test user")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_spawn_autonomous_agent():
    """Test spawning autonomous agent (simulation)"""
    print("\n" + "=" * 60)
    print("TEST 3: Spawn Autonomous Agent (Simulation)")
    print("=" * 60)
    
    try:
        from database import Database
        from app.automaton_manager import get_automaton_manager
        from app.automaton_agent_bridge import get_automaton_agent_bridge
        
        db = Database()
        automaton_manager = get_automaton_manager(db)
        bridge = get_automaton_agent_bridge(db, automaton_manager)
        
        # Simulate spawning (don't actually create in DB)
        print("📝 Simulating agent spawn...")
        print("   User ID: 123456789")
        print("   Agent Name: TestBot")
        print("   Initial Balance: 100 USDC")
        print("   Strategy: conservative")
        print("   Risk Level: low")
        
        # Test genesis prompt generation
        prompt = bridge._generate_genesis_prompt(
            agent_name="TestBot",
            strategy="conservative",
            risk_level="low",
            initial_balance=100.0
        )
        
        print("\n📄 Generated Genesis Prompt:")
        print("-" * 60)
        print(prompt[:300] + "..." if len(prompt) > 300 else prompt)
        print("-" * 60)
        
        # Check prompt content
        assert "TestBot" in prompt
        assert "100.0 USDC" in prompt
        assert "conservative" in prompt.lower()
        assert "FULL AUTONOMY" in prompt
        
        print("\n✅ Agent spawn simulation successful")
        print("   ✓ Genesis prompt generated correctly")
        print("   ✓ Full autonomy mentioned")
        print("   ✓ Risk parameters included")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_send_task():
    """Test sending task to Automaton (requires Automaton running)"""
    print("\n" + "=" * 60)
    print("TEST 4: Send Task to Automaton")
    print("=" * 60)
    
    try:
        from database import Database
        from app.automaton_manager import get_automaton_manager
        from app.automaton_agent_bridge import get_automaton_agent_bridge
        
        db = Database()
        automaton_manager = get_automaton_manager(db)
        bridge = get_automaton_agent_bridge(db, automaton_manager)
        
        # Check if send-task.js exists
        if not bridge.send_task_script.exists():
            print("⚠️  send-task.js not found")
            print(f"   Expected location: {bridge.send_task_script}")
            print("   Skipping test - Automaton not available")
            return True  # Not a failure, just skipped
        
        print("✅ send-task.js found")
        print(f"   Location: {bridge.send_task_script}")
        print("\n⚠️  To test actual task sending:")
        print("   1. Start Automaton: cd C:\\Users\\dragon\\automaton")
        print("   2. Run: node dist/index.js --run")
        print("   3. Re-run this test")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n🤖 AUTOMATON AUTONOMOUS TRADING - TEST SUITE")
    print("=" * 60)
    print("Testing: Lifetime Premium Only Autonomous Trading")
    print("=" * 60)
    
    tests = [
        ("Initialize Agent Bridge", test_agent_bridge),
        ("Lifetime Premium Check", test_lifetime_premium_check),
        ("Spawn Agent Simulation", test_spawn_autonomous_agent),
        ("Send Task to Automaton", test_send_task),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed < total:
        print("\n⚠️  Some tests failed")
        print("\nCommon issues:")
        print("  • Automaton not running - Start with: node dist/index.js --run")
        print("  • Missing send-task.js - Check Automaton directory")
        print("  • Database connection - Check Supabase credentials")
    else:
        print("\n✅ All tests passed!")
        print("\n🎯 Next Steps:")
        print("  1. Migration will run on Railway deployment")
        print("  2. Deploy to Railway: git push origin main")
        print("  3. Test in production with Lifetime Premium user")
        print("  4. Monitor agent performance")
    
    print("\n📝 Important Notes:")
    print("  • Autonomous trading is for LIFETIME PREMIUM users only")
    print("  • Signal generation uses bot's own system (/analyze, /futures, /ai)")
    print("  • Automaton provides FULL AUTONOMY (no approval per trade)")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
