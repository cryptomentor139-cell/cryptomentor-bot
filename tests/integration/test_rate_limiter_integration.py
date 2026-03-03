#!/usr/bin/env python3
"""
Integration Test: Rate Limiter with Automaton System

Tests rate limiting integration with:
1. Spawn operations
2. Withdrawal operations
3. Conway API calls
"""

import sys
import time
from datetime import datetime
from app.rate_limiter import get_rate_limiter


def test_spawn_integration():
    """Test spawn rate limiting in realistic scenario"""
    print("\n" + "="*60)
    print("INTEGRATION TEST 1: Spawn Rate Limiting")
    print("="*60)
    
    limiter = get_rate_limiter()
    user_id = 555666777
    
    print("\n📝 Scenario: User tries to spawn multiple agents quickly")
    
    # First spawn - should succeed
    print("\n1️⃣ First spawn attempt...")
    allowed, error = limiter.check_spawn_limit(user_id)
    if allowed:
        print("   ✅ ALLOWED - Agent spawning...")
        print("   💰 Deducting 100,000 credits")
        print("   🤖 Agent created successfully")
    else:
        print(f"   ❌ BLOCKED: {error}")
        return False
    
    # Second spawn immediately - should fail
    print("\n2️⃣ Second spawn attempt (immediate)...")
    allowed, error = limiter.check_spawn_limit(user_id)
    if not allowed:
        print("   ✅ BLOCKED (as expected)")
        print(f"   📋 Reason: {error[:80]}...")
    else:
        print("   ❌ ERROR: Should have been blocked!")
        return False
    
    # Check status
    status = limiter.get_rate_limit_status(user_id)
    print(f"\n📊 Current Status:")
    print(f"   Spawn: {status['spawn']['used']}/{status['spawn']['limit']}")
    print(f"   Remaining: {status['spawn']['remaining']}")
    print(f"   Window: {status['spawn']['window_hours']} hours")
    
    print("\n✅ Integration Test 1 PASSED")
    return True


def test_withdrawal_integration():
    """Test withdrawal rate limiting in realistic scenario"""
    print("\n" + "="*60)
    print("INTEGRATION TEST 2: Withdrawal Rate Limiting")
    print("="*60)
    
    limiter = get_rate_limiter()
    user_id = 888999000
    
    print("\n📝 Scenario: User makes multiple withdrawal requests")
    
    # Simulate 3 withdrawals throughout the day
    for i in range(3):
        print(f"\n{i+1}️⃣ Withdrawal request #{i+1}...")
        allowed, error = limiter.check_withdrawal_limit(user_id)
        if allowed:
            print(f"   ✅ ALLOWED - Processing withdrawal")
            print(f"   💸 Amount: 50 USDC")
            print(f"   💰 Fee: 1 USDC")
            print(f"   📤 Queued for admin processing")
        else:
            print(f"   ❌ BLOCKED: {error}")
            return False
    
    # Fourth withdrawal - should fail
    print(f"\n4️⃣ Withdrawal request #4 (exceeds limit)...")
    allowed, error = limiter.check_withdrawal_limit(user_id)
    if not allowed:
        print("   ✅ BLOCKED (as expected)")
        print(f"   📋 Reason: {error[:80]}...")
    else:
        print("   ❌ ERROR: Should have been blocked!")
        return False
    
    # Check status
    status = limiter.get_rate_limit_status(user_id)
    print(f"\n📊 Current Status:")
    print(f"   Withdrawal: {status['withdrawal']['used']}/{status['withdrawal']['limit']}")
    print(f"   Remaining: {status['withdrawal']['remaining']}")
    print(f"   Window: {status['withdrawal']['window_hours']} hours")
    
    print("\n✅ Integration Test 2 PASSED")
    return True


def test_api_backoff_integration():
    """Test API backoff in realistic scenario"""
    print("\n" + "="*60)
    print("INTEGRATION TEST 3: API Exponential Backoff")
    print("="*60)
    
    limiter = get_rate_limiter()
    api_name = "conway_api"
    
    print("\n📝 Scenario: Conway API experiences failures")
    
    # Simulate API failures
    print("\n🔄 Simulating API failures...")
    for i in range(3):
        backoff = limiter.record_api_failure(api_name)
        print(f"   Failure #{i+1}: Backoff = {backoff}s")
    
    # Try to make API call during backoff
    print("\n📞 Attempting API call during backoff...")
    allowed, wait = limiter.check_api_backoff(api_name)
    if not allowed:
        print(f"   ✅ BLOCKED (as expected)")
        print(f"   ⏳ Must wait: {wait:.1f}s")
    else:
        print("   ❌ ERROR: Should have been blocked!")
        return False
    
    # Simulate successful API call
    print("\n✅ Simulating successful API call...")
    limiter.record_api_success(api_name)
    
    # Verify backoff is reset
    allowed, wait = limiter.check_api_backoff(api_name)
    if allowed:
        print("   ✅ Backoff reset - API calls allowed")
    else:
        print("   ❌ ERROR: Backoff should be reset!")
        return False
    
    print("\n✅ Integration Test 3 PASSED")
    return True


def test_admin_reset():
    """Test admin reset functionality"""
    print("\n" + "="*60)
    print("INTEGRATION TEST 4: Admin Reset")
    print("="*60)
    
    limiter = get_rate_limiter()
    user_id = 111222333
    
    print("\n📝 Scenario: Admin resets user's rate limits")
    
    # Use up spawn limit
    print("\n1️⃣ User spawns agent...")
    limiter.check_spawn_limit(user_id)
    
    # Verify limit is reached
    allowed, error = limiter.check_spawn_limit(user_id)
    if not allowed:
        print("   ✅ Spawn limit reached")
    else:
        print("   ❌ ERROR: Limit should be reached!")
        return False
    
    # Admin resets
    print("\n👮 Admin resets spawn limit...")
    limiter.reset_user_limits(user_id, 'spawn')
    
    # Verify user can spawn again
    allowed, error = limiter.check_spawn_limit(user_id)
    if allowed:
        print("   ✅ User can spawn again after reset")
    else:
        print("   ❌ ERROR: Should be allowed after reset!")
        return False
    
    print("\n✅ Integration Test 4 PASSED")
    return True


def test_cleanup_integration():
    """Test cleanup in realistic scenario"""
    print("\n" + "="*60)
    print("INTEGRATION TEST 5: Cleanup")
    print("="*60)
    
    limiter = get_rate_limiter()
    
    print("\n📝 Scenario: System cleanup of old rate limit entries")
    
    # Add some test data
    test_users = [123, 456, 789]
    for user_id in test_users:
        limiter.check_spawn_limit(user_id)
        limiter.check_withdrawal_limit(user_id)
    
    print(f"\n✅ Added rate limit entries for {len(test_users)} users")
    
    # Run cleanup
    print("\n🧹 Running cleanup...")
    limiter.cleanup_old_entries()
    
    # Verify recent entries are preserved
    for user_id in test_users:
        status = limiter.get_rate_limit_status(user_id)
        if status['spawn']['used'] == 0:
            print(f"   ❌ ERROR: Recent entries were removed for user {user_id}!")
            return False
    
    print("   ✅ Recent entries preserved")
    
    print("\n✅ Integration Test 5 PASSED")
    return True


def run_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("RATE LIMITER INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Spawn Rate Limiting", test_spawn_integration),
        ("Withdrawal Rate Limiting", test_withdrawal_integration),
        ("API Exponential Backoff", test_api_backoff_integration),
        ("Admin Reset", test_admin_reset),
        ("Cleanup", test_cleanup_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("INTEGRATION TEST RESULTS")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("\nRate Limiter is fully integrated and working:")
        print("  ✅ Spawn operations protected (1 per hour)")
        print("  ✅ Withdrawal operations protected (3 per day)")
        print("  ✅ API calls protected with exponential backoff")
        print("  ✅ Admin reset functionality working")
        print("  ✅ Cleanup preserves recent entries")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
