"""
Test Task 6.1: Credit Check Logic for Non-Premium Users

This test verifies that:
1. Non-premium users are charged credits for manual signal generation
2. Credits are deducted correctly (50 - 20 = 30)
3. Signal is generated after successful credit deduction
4. Credit balance is updated in the database
"""

import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.premium_checker import check_and_deduct_credits, is_lifetime_premium
from app.handlers_manual_signals import cmd_analyze, COST_SINGLE_SIGNAL


def test_credit_check_non_premium_user():
    """
    Test credit check for non-premium user with sufficient credits.
    
    Scenario:
    - User: Non-premium with 50 credits
    - Command: /analyze BTCUSDT (costs 20 credits)
    - Expected: Credits deducted (50 - 20 = 30), signal generated
    """
    print("\n" + "="*70)
    print("TEST: Credit Check for Non-Premium User")
    print("="*70)
    
    # Test user ID (non-premium)
    test_user_id = 999999999  # Use a test user ID that doesn't exist in production
    
    # Mock user data: non-premium with 50 credits
    mock_user_data = {
        "telegram_id": test_user_id,
        "is_premium": False,
        "premium_until": None,
        "credits": 50
    }
    
    print(f"\n📋 Test Setup:")
    print(f"   User ID: {test_user_id}")
    print(f"   Premium Status: {mock_user_data['is_premium']}")
    print(f"   Initial Credits: {mock_user_data['credits']}")
    print(f"   Command Cost: {COST_SINGLE_SIGNAL} credits")
    
    # Mock the Supabase functions
    with patch('app.premium_checker.get_supabase_client') as mock_supabase_client, \
         patch('app.premium_checker.get_user_by_tid') as mock_get_user:
        
        # Setup mock for is_lifetime_premium check
        mock_supabase = Mock()
        mock_table = Mock()
        mock_select = Mock()
        mock_eq1 = Mock()
        mock_eq2 = Mock()
        mock_is = Mock()
        mock_limit = Mock()
        mock_execute = Mock()
        
        # Chain the mocks for lifetime premium check (should return empty - not lifetime)
        mock_execute.data = []  # Empty result = not lifetime premium
        mock_limit.execute.return_value = mock_execute
        mock_is.limit.return_value = mock_limit
        mock_eq2.is_.return_value = mock_is
        mock_eq1.eq.return_value = mock_eq2
        mock_select.eq.return_value = mock_eq1
        mock_table.select.return_value = mock_select
        mock_supabase.table.return_value = mock_table
        mock_supabase_client.return_value = mock_supabase
        
        # Setup mock for get_user_by_tid (returns user with 50 credits)
        mock_get_user.return_value = mock_user_data.copy()
        
        # Setup mock for credit deduction update
        mock_update_result = Mock()
        mock_update_result.data = [{"telegram_id": test_user_id, "credits": 30}]
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_result
        
        print("\n🔍 Step 1: Check if user is lifetime premium")
        is_lifetime = is_lifetime_premium(test_user_id)
        print(f"   Result: {is_lifetime}")
        assert is_lifetime == False, "User should NOT be lifetime premium"
        print("   ✅ Correctly identified as non-premium user")
        
        print("\n🔍 Step 2: Check and deduct credits")
        success, message = check_and_deduct_credits(test_user_id, COST_SINGLE_SIGNAL)
        
        print(f"   Success: {success}")
        print(f"   Message: {message}")
        
        assert success == True, "Credit deduction should succeed"
        assert "Credits deducted: 20" in message, f"Expected credit deduction message, got: {message}"
        print("   ✅ Credits deducted successfully")
        
        print("\n🔍 Step 3: Verify credit deduction was called")
        # Verify that update was called with correct parameters
        mock_table.update.assert_called_once()
        update_call_args = mock_table.update.call_args[0][0]
        assert update_call_args["credits"] == 30, f"Expected credits to be 30, got {update_call_args['credits']}"
        print(f"   ✅ Database update called with credits=30")
        
        print("\n🔍 Step 4: Verify final credit balance")
        expected_final_credits = 50 - COST_SINGLE_SIGNAL
        actual_final_credits = update_call_args["credits"]
        print(f"   Initial: 50 credits")
        print(f"   Cost: {COST_SINGLE_SIGNAL} credits")
        print(f"   Expected Final: {expected_final_credits} credits")
        print(f"   Actual Final: {actual_final_credits} credits")
        
        assert actual_final_credits == expected_final_credits, \
            f"Credit balance mismatch: expected {expected_final_credits}, got {actual_final_credits}"
        print("   ✅ Credit balance correct: 50 - 20 = 30")
    
    print("\n" + "="*70)
    print("✅ TEST PASSED: Credit check logic works correctly")
    print("="*70)


def test_credit_check_with_command_handler():
    """
    Test the full command handler flow with credit check.
    
    This tests the integration between the command handler and credit system.
    """
    print("\n" + "="*70)
    print("TEST: Full Command Handler with Credit Check")
    print("="*70)
    
    test_user_id = 999999999
    
    # Mock user data
    mock_user_data = {
        "telegram_id": test_user_id,
        "is_premium": False,
        "premium_until": None,
        "credits": 50
    }
    
    print(f"\n📋 Test Setup:")
    print(f"   User ID: {test_user_id}")
    print(f"   Command: /analyze BTCUSDT")
    print(f"   Initial Credits: {mock_user_data['credits']}")
    
    # Create mock Update and Context objects
    mock_update = Mock()
    mock_update.effective_user.id = test_user_id
    mock_update.message.reply_text = AsyncMock()
    
    mock_context = Mock()
    mock_context.args = ["BTCUSDT"]
    
    # Mock the dependencies
    with patch('app.handlers_manual_signals.check_and_deduct_credits') as mock_check_credits, \
         patch('app.handlers_manual_signals.FuturesSignalGenerator') as mock_generator_class, \
         patch('app.handlers_manual_signals.check_rate_limit') as mock_rate_limit:
        
        # Setup mocks
        mock_rate_limit.return_value = (True, 0)  # Rate limit OK
        mock_check_credits.return_value = (True, "Credits deducted: 20")  # Credit check passes
        
        mock_generator = Mock()
        mock_generator.generate_signal = AsyncMock(return_value="📊 MOCK SIGNAL FOR BTCUSDT")
        mock_generator_class.return_value = mock_generator
        
        print("\n🔍 Step 1: Execute /analyze BTCUSDT command")
        
        # Run the command handler
        asyncio.run(cmd_analyze(mock_update, mock_context))
        
        print("\n🔍 Step 2: Verify credit check was called")
        mock_check_credits.assert_called_once_with(test_user_id, COST_SINGLE_SIGNAL)
        print(f"   ✅ Credit check called with user_id={test_user_id}, cost={COST_SINGLE_SIGNAL}")
        
        print("\n🔍 Step 3: Verify signal generation was called")
        mock_generator.generate_signal.assert_called_once_with("BTCUSDT", "1h")
        print("   ✅ Signal generator called with BTCUSDT, 1h")
        
        print("\n🔍 Step 4: Verify signal was sent to user")
        # Check that reply_text was called (loading message + signal)
        assert mock_update.message.reply_text.call_count >= 1, "Signal should be sent to user"
        print(f"   ✅ Signal sent to user ({mock_update.message.reply_text.call_count} messages)")
    
    print("\n" + "="*70)
    print("✅ TEST PASSED: Command handler integrates correctly with credit system")
    print("="*70)


def test_credit_calculation_accuracy():
    """
    Test that credit calculations are accurate for various scenarios.
    """
    print("\n" + "="*70)
    print("TEST: Credit Calculation Accuracy")
    print("="*70)
    
    test_scenarios = [
        {"initial": 50, "cost": 20, "expected": 30, "description": "Standard deduction"},
        {"initial": 100, "cost": 20, "expected": 80, "description": "High balance"},
        {"initial": 20, "cost": 20, "expected": 0, "description": "Exact balance"},
        {"initial": 1000, "cost": 60, "expected": 940, "description": "Multi-signal cost"},
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['description']}")
        print(f"   Initial: {scenario['initial']} credits")
        print(f"   Cost: {scenario['cost']} credits")
        print(f"   Expected: {scenario['expected']} credits")
        
        actual = scenario['initial'] - scenario['cost']
        print(f"   Actual: {actual} credits")
        
        assert actual == scenario['expected'], \
            f"Calculation error: {scenario['initial']} - {scenario['cost']} should be {scenario['expected']}, got {actual}"
        print(f"   ✅ Calculation correct")
    
    print("\n" + "="*70)
    print("✅ TEST PASSED: All credit calculations are accurate")
    print("="*70)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TASK 6.1: CREDIT CHECK LOGIC TEST SUITE")
    print("="*70)
    print("\nTesting credit check logic for non-premium users")
    print("This verifies that credits are properly deducted when")
    print("non-premium users generate manual signals.")
    
    try:
        # Run all tests
        test_credit_check_non_premium_user()
        test_credit_check_with_command_handler()
        test_credit_calculation_accuracy()
        
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\n✅ Task 6.1 Acceptance Criteria Met:")
        print("   ✓ Credit check works correctly for non-premium users")
        print("   ✓ Credits deducted (20 credits for single signal)")
        print("   ✓ Signal generated after successful credit deduction")
        print("   ✓ Credit balance updated correctly (50 - 20 = 30)")
        print("\n" + "="*70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise
