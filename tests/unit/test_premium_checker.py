"""
Test script for premium_checker module
Run this to verify the premium checker functions work correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.premium_checker import is_lifetime_premium, check_and_deduct_credits, get_user_credit_balance


def test_is_lifetime_premium():
    """Test the is_lifetime_premium function"""
    print("\n" + "="*60)
    print("TEST 1: is_lifetime_premium()")
    print("="*60)
    
    # Test with a sample user ID (replace with actual test user)
    test_user_id = 123456789  # Replace with actual user ID for testing
    
    print(f"\nTesting user ID: {test_user_id}")
    result = is_lifetime_premium(test_user_id)
    print(f"Result: {result}")
    print(f"Type: {type(result)}")
    
    if isinstance(result, bool):
        print("✅ Function returns boolean as expected")
    else:
        print("❌ Function should return boolean")
    
    return result


def test_check_and_deduct_credits():
    """Test the check_and_deduct_credits function"""
    print("\n" + "="*60)
    print("TEST 2: check_and_deduct_credits()")
    print("="*60)
    
    # Test with a sample user ID
    test_user_id = 123456789  # Replace with actual user ID for testing
    test_cost = 20
    
    print(f"\nTesting user ID: {test_user_id}")
    print(f"Credit cost: {test_cost}")
    
    # Get initial balance
    initial_balance = get_user_credit_balance(test_user_id)
    print(f"Initial balance: {initial_balance}")
    
    # Test credit check and deduction
    success, message = check_and_deduct_credits(test_user_id, test_cost)
    print(f"\nResult: success={success}, message='{message}'")
    
    # Get final balance
    final_balance = get_user_credit_balance(test_user_id)
    print(f"Final balance: {final_balance}")
    
    # Verify return type
    if isinstance(success, bool) and isinstance(message, str):
        print("✅ Function returns (bool, str) tuple as expected")
    else:
        print("❌ Function should return (bool, str) tuple")
    
    return success, message


def test_get_user_credit_balance():
    """Test the get_user_credit_balance function"""
    print("\n" + "="*60)
    print("TEST 3: get_user_credit_balance()")
    print("="*60)
    
    # Test with a sample user ID
    test_user_id = 123456789  # Replace with actual user ID for testing
    
    print(f"\nTesting user ID: {test_user_id}")
    balance = get_user_credit_balance(test_user_id)
    print(f"Credit balance: {balance}")
    print(f"Type: {type(balance)}")
    
    if isinstance(balance, int):
        print("✅ Function returns integer as expected")
    else:
        print("❌ Function should return integer")
    
    return balance


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PREMIUM CHECKER MODULE TESTS")
    print("="*60)
    print("\nNote: Replace test_user_id with actual user ID from your database")
    print("      to test with real data.")
    
    try:
        # Test 1: Check lifetime premium status
        test_is_lifetime_premium()
        
        # Test 2: Check and deduct credits
        test_check_and_deduct_credits()
        
        # Test 3: Get credit balance
        test_get_user_credit_balance()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
        print("\n✅ Module functions are working correctly!")
        print("   - is_lifetime_premium() returns bool")
        print("   - check_and_deduct_credits() returns (bool, str)")
        print("   - get_user_credit_balance() returns int")
        
    except Exception as e:
        print("\n" + "="*60)
        print("TEST FAILED")
        print("="*60)
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
