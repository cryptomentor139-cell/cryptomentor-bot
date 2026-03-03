#!/usr/bin/env python3
"""
Test Automaton Manager

Tests agent spawning, status tracking, and lifecycle management.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from database import Database
from automaton_manager import get_automaton_manager

def test_spawn_agent():
    """Test agent spawning"""
    print("\n" + "="*60)
    print("TEST 1: Spawn Agent")
    print("="*60)
    
    # Initialize database
    db = Database()
    manager = get_automaton_manager(db)
    
    # Test user (must be premium with credits)
    test_user_id = 1187119989
    
    # Check user status
    user = db.get_user(test_user_id)
    if not user:
        print(f"❌ User {test_user_id} not found")
        return None
    
    print(f"User: {user['first_name']} (@{user['username']})")
    print(f"Premium: {user['is_premium']}")
    print(f"Credits: {user['credits']:,}")
    
    if not user['is_premium']:
        print("⚠️ User is not premium - spawning will fail")
    
    if user['credits'] < 100000:
        print(f"⚠️ Insufficient credits - need 100,000, have {user['credits']:,}")
    
    # Spawn agent
    print("\nSpawning agent...")
    result = manager.spawn_agent(
        user_id=test_user_id,
        agent_name="Test Trading Bot Alpha",
        genesis_prompt="You are a test trading agent. Focus on learning and small trades."
    )
    
    if result['success']:
        print(f"✅ Agent spawned successfully!")
        print(f"   Agent ID: {result['agent_id']}")
        print(f"   Deposit Address: {result['deposit_address']}")
        print(f"   Spawn Fee: {result['spawn_fee']:,} credits")
        print(f"   Remaining Credits: {result['remaining_credits']:,}")
        return result['agent_id']
    else:
        print(f"❌ Failed to spawn agent: {result['message']}")
        return None

def test_get_agent_status(agent_id):
    """Test agent status retrieval"""
    print("\n" + "="*60)
    print("TEST 2: Get Agent Status")
    print("="*60)
    
    if not agent_id:
        print("⚠️ Skipping (no agent ID)")
        return None
    
    db = Database()
    manager = get_automaton_manager(db)
    
    print(f"Getting status for agent {agent_id}...")
    status = manager.get_agent_status(agent_id)
    
    if status:
        print(f"✅ Agent status retrieved:")
        print(f"   Name: {status['agent_name']}")
        print(f"   Wallet: {status['agent_wallet']}")
        print(f"   Deposit Address: {status['deposit_address']}")
        print(f"   Balance: {status['balance']:,.2f} credits")
        print(f"   Survival Tier: {status['survival_tier']}")
        print(f"   Status: {status['status']}")
        print(f"   Runtime: ~{status['runtime_days']:.1f} days")
        print(f"   Total Earnings: ${status['total_earnings']:.2f}")
        print(f"   Total Expenses: ${status['total_expenses']:.2f}")
        print(f"   Net P&L: ${status['net_pnl']:.2f}")
        return status
    else:
        print("❌ Failed to get agent status")
        return None

def test_get_user_agents():
    """Test getting all user agents"""
    print("\n" + "="*60)
    print("TEST 3: Get User Agents")
    print("="*60)
    
    db = Database()
    manager = get_automaton_manager(db)
    
    test_user_id = 1187119989
    
    print(f"Getting all agents for user {test_user_id}...")
    agents = manager.get_user_agents(test_user_id)
    
    if agents:
        print(f"✅ Found {len(agents)} agent(s):")
        for i, agent in enumerate(agents, 1):
            print(f"\n   Agent {i}:")
            print(f"   - Name: {agent['agent_name']}")
            print(f"   - Balance: {agent['balance']:,.2f} credits")
            print(f"   - Tier: {agent['survival_tier']}")
            print(f"   - Runtime: ~{agent['runtime_days']:.1f} days")
        return agents
    else:
        print("⚠️ No agents found for this user")
        return []

def test_survival_tier_calculation():
    """Test survival tier calculation"""
    print("\n" + "="*60)
    print("TEST 4: Survival Tier Calculation")
    print("="*60)
    
    db = Database()
    manager = get_automaton_manager(db)
    
    test_cases = [
        (15000, 'normal'),
        (7500, 'low_compute'),
        (2500, 'critical'),
        (500, 'dead'),
        (0, 'dead')
    ]
    
    print("Testing tier calculations:")
    all_passed = True
    for credits, expected_tier in test_cases:
        actual_tier = manager._calculate_survival_tier(credits)
        status = "✅" if actual_tier == expected_tier else "❌"
        print(f"   {status} {credits:,} credits → {actual_tier} (expected: {expected_tier})")
        if actual_tier != expected_tier:
            all_passed = False
    
    if all_passed:
        print("\n✅ All tier calculations passed")
    else:
        print("\n❌ Some tier calculations failed")
    
    return all_passed

def test_runtime_estimation():
    """Test runtime estimation"""
    print("\n" + "="*60)
    print("TEST 5: Runtime Estimation")
    print("="*60)
    
    db = Database()
    manager = get_automaton_manager(db)
    
    test_cases = [
        (10000, 200, 50.0),   # 10k credits / 200 per day = 50 days
        (5000, 200, 25.0),    # 5k credits / 200 per day = 25 days
        (1000, 200, 5.0),     # 1k credits / 200 per day = 5 days
        (0, 200, 0.0)         # 0 credits = 0 days
    ]
    
    print("Testing runtime estimations:")
    all_passed = True
    for credits, daily, expected_days in test_cases:
        actual_days = manager._estimate_runtime(credits, daily)
        status = "✅" if abs(actual_days - expected_days) < 0.1 else "❌"
        print(f"   {status} {credits:,} credits @ {daily}/day → {actual_days:.1f} days (expected: {expected_days:.1f})")
        if abs(actual_days - expected_days) >= 0.1:
            all_passed = False
    
    if all_passed:
        print("\n✅ All runtime estimations passed")
    else:
        print("\n❌ Some runtime estimations failed")
    
    return all_passed

def run_all_tests():
    """Run all Automaton Manager tests"""
    print("\n" + "="*60)
    print("AUTOMATON MANAGER TEST SUITE")
    print("="*60)
    
    # Check environment
    print("\n📋 Checking environment...")
    if not os.getenv('SUPABASE_URL'):
        print("❌ SUPABASE_URL not set")
        return False
    
    if not os.getenv('SUPABASE_SERVICE_KEY'):
        print("❌ SUPABASE_SERVICE_KEY not set")
        return False
    
    if not os.getenv('CONWAY_API_KEY'):
        print("❌ CONWAY_API_KEY not set")
        return False
    
    print("✅ Environment configured")
    
    # Run tests
    results = {}
    
    # Test 1: Spawn agent
    agent_id = test_spawn_agent()
    results['spawn'] = agent_id is not None
    
    # Test 2: Get agent status
    if agent_id:
        status = test_get_agent_status(agent_id)
        results['status'] = status is not None
    else:
        print("\n⚠️ Skipping status test (no agent spawned)")
        results['status'] = False
    
    # Test 3: Get user agents
    agents = test_get_user_agents()
    results['user_agents'] = len(agents) > 0
    
    # Test 4: Tier calculation
    results['tier_calc'] = test_survival_tier_calculation()
    
    # Test 5: Runtime estimation
    results['runtime_est'] = test_runtime_estimation()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Automaton Manager is working.")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the logs above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
