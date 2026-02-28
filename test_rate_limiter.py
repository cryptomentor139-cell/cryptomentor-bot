#!/usr/bin/env python3
"""
Test Rate Limiter - Verify rate limiting functionality

Tests:
1. Spawn rate limiting (1 per hour)
2. Withdrawal rate limiting (3 per day)
3. API exponential backoff
4. Rate limit status retrieval
5. Admin reset functionality
"""

import time
from datetime import datetime, timedelta
from app.rate_limiter import get_rate_limiter


def test_spawn_rate_limit():
    """Test spawn operation rate limiting (1 per hour)"""
    print("\n" + "="*60)
    print("TEST 1: Spawn Rate Limiting (1 per hour)")
    print("="*60)
    
    limiter = get_rate_limiter()
    test_user_id = 123456789
    
    # First spawn should succeed
    allowed, error = limiter.check_spawn_limit(test_user_id)
    assert allowed == True, "First spawn should be allowed"
    assert error is None, "No error message expected"
    print("✅ First spawn: ALLOWED")
    
    # Second spawn should fail (within 1 hour)
    allowed, error = limiter.check_spawn_limit(test_user_id)
    assert allowed == False, "Second spawn should be blocked"
    assert error is not None, "Error message expected"
    assert "Rate limit exceeded" in error, "Error should mention rate limit"
    print(f"✅ Second spawn: BLOCKED")
    print(f"   Error message: {error[:80]}...")
    
    # Check status
    status = limiter.get_rate_limit_status(test_user_id)
    print(f"\n📊 Rate Limit Status:")
    print(f"   Spawn: {status['spawn']['used']}/{status['spawn']['limit']} used")
    print(f"   Remaining: {status['spawn']['remaining']}")
    
    # Admin reset
    limiter.reset_user_limits(test_user_id, 'spawn')
    allowed, error = limiter.check_spawn_limit(test_user_id)
    assert allowed == True, "Spawn should be allowed after reset"
    print("\n✅ After admin reset: ALLOWED")
    
    print("\n✅ TEST 1 PASSED: Spawn rate limiting works correctly")


def test_withdrawal_rate_limit():
    """Test withdrawal rate limiting (3 per day)"""
    print("\n" + "="*60)
    print("TEST 2: Withdrawal Rate Limiting (3 per day)")
    print("="*60)
    
    limiter = get_rate_limiter()
    test_user_id = 987654321
    
    # First 3 withdrawals should succeed
    for i in range(3):
        allowed, error = limiter.check_withdrawal_limit(test_user_id)
        assert allowed == True, f"Withdrawal {i+1} should be allowed"
        assert error is None, "No error message expected"
        print(f"✅ Withdrawal {i+1}: ALLOWED")
    
    # Fourth withdrawal should fail
    allowed, error = limiter.check_withdrawal_limit(test_user_id)
    assert allowed == False, "Fourth withdrawal should be blocked"
    assert error is not None, "Error message expected"
    assert "Withdrawal limit exceeded" in error, "Error should mention withdrawal limit"
    print(f"✅ Withdrawal 4: BLOCKED")
    print(f"   Error message: {error[:80]}...")
    
    # Check status
    status = limiter.get_rate_limit_status(test_user_id)
    print(f"\n📊 Rate Limit Status:")
    print(f"   Withdrawal: {status['withdrawal']['used']}/{status['withdrawal']['limit']} used")
    print(f"   Remaining: {status['withdrawal']['remaining']}")
    
    print("\n✅ TEST 2 PASSED: Withdrawal rate limiting works correctly")


def test_api_exponential_backoff():
    """Test API exponential backoff"""
    print("\n" + "="*60)
    print("TEST 3: API Exponential Backoff")
    print("="*60)
    
    limiter = get_rate_limiter()
    api_name = "test_api"
    
    # First call should be allowed
    allowed, wait = limiter.check_api_backoff(api_name)
    assert allowed == True, "First API call should be allowed"
    assert wait is None, "No wait time expected"
    print("✅ First API call: ALLOWED")
    
    # Record failures and check backoff
    backoff_times = []
    for i in range(5):
        backoff = limiter.record_api_failure(api_name)
        backoff_times.append(backoff)
        print(f"   Failure {i+1}: Backoff = {backoff}s")
    
    # Verify exponential growth: 1s, 2s, 4s, 8s, 16s
    assert backoff_times[0] == 1, "First backoff should be 1s"
    assert backoff_times[1] == 2, "Second backoff should be 2s"
    assert backoff_times[2] == 4, "Third backoff should be 4s"
    assert backoff_times[3] == 8, "Fourth backoff should be 8s"
    assert backoff_times[4] == 16, "Fifth backoff should be 16s"
    print("✅ Exponential backoff pattern verified: 1s → 2s → 4s → 8s → 16s")
    
    # Check that API is blocked during backoff
    allowed, wait = limiter.check_api_backoff(api_name)
    assert allowed == False, "API should be blocked during backoff"
    assert wait is not None, "Wait time should be provided"
    print(f"✅ API blocked during backoff: wait {wait:.1f}s")
    
    # Record success to reset backoff
    limiter.record_api_success(api_name)
    allowed, wait = limiter.check_api_backoff(api_name)
    assert allowed == True, "API should be allowed after success"
    print("✅ Backoff reset after success")
    
    print("\n✅ TEST 3 PASSED: API exponential backoff works correctly")


def test_rate_limit_status():
    """Test rate limit status retrieval"""
    print("\n" + "="*60)
    print("TEST 4: Rate Limit Status Retrieval")
    print("="*60)
    
    limiter = get_rate_limiter()
    test_user_id = 111222333
    
    # Use some limits
    limiter.check_spawn_limit(test_user_id)
    limiter.check_withdrawal_limit(test_user_id)
    limiter.check_withdrawal_limit(test_user_id)
    
    # Get status
    status = limiter.get_rate_limit_status(test_user_id)
    
    print(f"\n📊 Rate Limit Status for user {test_user_id}:")
    print(f"\n   Spawn:")
    print(f"      Used: {status['spawn']['used']}/{status['spawn']['limit']}")
    print(f"      Remaining: {status['spawn']['remaining']}")
    print(f"      Window: {status['spawn']['window_hours']} hours")
    
    print(f"\n   Withdrawal:")
    print(f"      Used: {status['withdrawal']['used']}/{status['withdrawal']['limit']}")
    print(f"      Remaining: {status['withdrawal']['remaining']}")
    print(f"      Window: {status['withdrawal']['window_hours']} hours")
    
    assert status['spawn']['used'] == 1, "Spawn should show 1 used"
    assert status['spawn']['remaining'] == 0, "Spawn should show 0 remaining"
    assert status['withdrawal']['used'] == 2, "Withdrawal should show 2 used"
    assert status['withdrawal']['remaining'] == 1, "Withdrawal should show 1 remaining"
    
    print("\n✅ TEST 4 PASSED: Rate limit status retrieval works correctly")


def test_cleanup():
    """Test cleanup of old entries"""
    print("\n" + "="*60)
    print("TEST 5: Cleanup Old Entries")
    print("="*60)
    
    limiter = get_rate_limiter()
    
    # Add some test data
    test_user_id = 444555666
    limiter.check_spawn_limit(test_user_id)
    limiter.check_withdrawal_limit(test_user_id)
    
    print("✅ Added test rate limit entries")
    
    # Run cleanup (won't remove recent entries)
    limiter.cleanup_old_entries()
    
    # Verify entries still exist
    status = limiter.get_rate_limit_status(test_user_id)
    assert status['spawn']['used'] == 1, "Recent spawn entry should still exist"
    assert status['withdrawal']['used'] == 1, "Recent withdrawal entry should still exist"
    
    print("✅ Recent entries preserved after cleanup")
    
    print("\n✅ TEST 5 PASSED: Cleanup works correctly")


def run_all_tests():
    """Run all rate limiter tests"""
    print("\n" + "="*60)
    print("RATE LIMITER TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_spawn_rate_limit()
        test_withdrawal_rate_limit()
        test_api_exponential_backoff()
        test_rate_limit_status()
        test_cleanup()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nRate Limiter is working correctly!")
        print("\nFeatures verified:")
        print("  ✅ Spawn rate limiting (1 per hour)")
        print("  ✅ Withdrawal rate limiting (3 per day)")
        print("  ✅ API exponential backoff (1s → 2s → 4s → 8s → 16s)")
        print("  ✅ Rate limit status retrieval")
        print("  ✅ Admin reset functionality")
        print("  ✅ Cleanup of old entries")
        
        return True
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
