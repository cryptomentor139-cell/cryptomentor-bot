"""
Property-based test for mode activation with credit validation.

Feature: dual-mode-offline-online
Property 1: Mode Activation with Credit Validation
Validates: Requirements 1.3, 1.4, 1.5, 1.6

For any user attempting to activate online mode, the system should check their 
Automaton credits, and if sufficient credits exist, activate online mode and 
create a session; otherwise, display instructions for obtaining credits.
"""

import os
import pytest
from hypothesis import given, strategies as st, settings
from dotenv import load_dotenv
from uuid import UUID

# Load environment variables from .env file
load_dotenv()

# Check if environment variables are set
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    pytest.skip(
        "SUPABASE_URL and SUPABASE_KEY must be set to run these tests",
        allow_module_level=True
    )

from app.dual_mode_db import (
    get_user_mode,
    set_user_mode,
    add_credits,
    get_user_credits,
    get_active_session,
    supabase
)
from app.dual_mode.mode_state_manager import ModeStateManager


# Minimum credits required for online mode (from design spec)
MINIMUM_CREDITS_REQUIRED = 10


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    credits=st.integers(min_value=0, max_value=100000)
)
def test_online_mode_activation_requires_credits(user_id, credits):
    """
    Feature: dual-mode-offline-online, Property 1: Mode Activation with Credit Validation
    
    For any user attempting to activate online mode, the system should check 
    their Automaton credits, and if sufficient credits exist, activate online 
    mode and create a session; otherwise, display instructions for obtaining credits.
    
    **Validates: Requirements 1.3, 1.4, 1.5, 1.6**
    """
    # Clean up any existing state for this user
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set user to offline mode initially
    set_user_mode(user_id, 'offline')
    assert get_user_mode(user_id) == 'offline', "Failed to set initial offline mode"
    
    # Set user credits
    if credits > 0:
        add_credits(user_id, credits, "Test setup")
    
    # Verify credits were set correctly
    actual_credits = get_user_credits(user_id)
    assert actual_credits == credits, \
        f"Credits not set correctly: expected {credits}, got {actual_credits}"
    
    # Create ModeStateManager instance
    manager = ModeStateManager()
    
    # Attempt to transition to online mode
    result = manager.transition_mode(user_id, 'offline', 'online')
    
    # Verify behavior based on credit amount
    if credits >= MINIMUM_CREDITS_REQUIRED:
        # Requirement 1.5: If user has sufficient credits, activate online mode
        assert result.success, \
            f"Transition should succeed with {credits} credits (>= {MINIMUM_CREDITS_REQUIRED})"
        
        # Verify mode was changed to online
        current_mode = get_user_mode(user_id)
        assert current_mode == 'online', \
            f"Mode should be 'online' after successful transition, got '{current_mode}'"
        
        # Note: Session creation is handled by OnlineModeHandler in the full implementation
        # This test validates the credit check and mode transition logic in ModeStateManager
        
    else:
        # Requirement 1.6: If user lacks sufficient credits, display instructions
        assert not result.success, \
            f"Transition should fail with {credits} credits (< {MINIMUM_CREDITS_REQUIRED})"
        
        # Verify error message contains instructions for obtaining credits
        assert "obtain credits" in result.message.lower() or "insufficient" in result.message.lower(), \
            f"Error message should mention obtaining credits or insufficient balance: {result.message}"
        
        # Verify mode was NOT changed to online
        current_mode = get_user_mode(user_id)
        assert current_mode != 'online', \
            f"Mode should NOT be 'online' after failed transition, got '{current_mode}'"
        
        # Verify mode remains offline
        assert current_mode == 'offline', \
            f"Mode should remain 'offline' after failed transition, got '{current_mode}'"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    credits=st.integers(min_value=MINIMUM_CREDITS_REQUIRED, max_value=100000)
)
def test_sufficient_credits_always_allows_online_mode(user_id, credits):
    """
    Feature: dual-mode-offline-online, Property 1: Mode Activation with Credit Validation
    
    For any user with sufficient credits (>= minimum required), online mode 
    activation should always succeed.
    
    **Validates: Requirements 1.4, 1.5**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set user to offline mode
    set_user_mode(user_id, 'offline')
    
    # Add sufficient credits
    add_credits(user_id, credits, "Test setup")
    
    # Verify credits
    actual_credits = get_user_credits(user_id)
    assert actual_credits >= MINIMUM_CREDITS_REQUIRED, \
        f"Credits should be >= {MINIMUM_CREDITS_REQUIRED}, got {actual_credits}"
    
    # Attempt transition
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'online')
    
    # Should always succeed with sufficient credits
    assert result.success, \
        f"Transition should succeed with {credits} credits: {result.error}"
    
    # Verify mode changed
    assert get_user_mode(user_id) == 'online', \
        "Mode should be 'online' after successful transition"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    credits=st.integers(min_value=0, max_value=MINIMUM_CREDITS_REQUIRED - 1)
)
def test_insufficient_credits_always_blocks_online_mode(user_id, credits):
    """
    Feature: dual-mode-offline-online, Property 1: Mode Activation with Credit Validation
    
    For any user with insufficient credits (< minimum required), online mode 
    activation should always fail with instructions.
    
    **Validates: Requirements 1.4, 1.6**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set user to offline mode
    set_user_mode(user_id, 'offline')
    
    # Add insufficient credits
    if credits > 0:
        add_credits(user_id, credits, "Test setup")
    
    # Verify credits are insufficient
    actual_credits = get_user_credits(user_id)
    assert actual_credits < MINIMUM_CREDITS_REQUIRED, \
        f"Credits should be < {MINIMUM_CREDITS_REQUIRED}, got {actual_credits}"
    
    # Attempt transition
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'online')
    
    # Should always fail with insufficient credits
    assert not result.success, \
        f"Transition should fail with {credits} credits"
    
    # Should provide instructions
    assert "obtain credits" in result.message.lower() or "insufficient" in result.message.lower(), \
        f"Error message should mention obtaining credits: {result.message}"
    
    # Mode should remain offline
    assert get_user_mode(user_id) == 'offline', \
        "Mode should remain 'offline' after failed transition"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999)
)
def test_boundary_credit_amount_exactly_minimum(user_id):
    """
    Feature: dual-mode-offline-online, Property 1: Mode Activation with Credit Validation
    
    For any user with exactly the minimum required credits, online mode 
    activation should succeed (boundary test).
    
    **Validates: Requirements 1.4, 1.5**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set user to offline mode
    set_user_mode(user_id, 'offline')
    
    # Add exactly minimum credits
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED, "Test setup")
    
    # Verify credits
    actual_credits = get_user_credits(user_id)
    assert actual_credits == MINIMUM_CREDITS_REQUIRED, \
        f"Credits should be exactly {MINIMUM_CREDITS_REQUIRED}, got {actual_credits}"
    
    # Attempt transition
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'online')
    
    # Should succeed with exactly minimum credits
    assert result.success, \
        f"Transition should succeed with exactly {MINIMUM_CREDITS_REQUIRED} credits: {result.error}"
    
    # Verify mode changed
    assert get_user_mode(user_id) == 'online', \
        "Mode should be 'online' with exactly minimum credits"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999)
)
def test_boundary_credit_amount_one_below_minimum(user_id):
    """
    Feature: dual-mode-offline-online, Property 1: Mode Activation with Credit Validation
    
    For any user with one credit below the minimum required, online mode 
    activation should fail (boundary test).
    
    **Validates: Requirements 1.4, 1.6**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set user to offline mode
    set_user_mode(user_id, 'offline')
    
    # Add one credit below minimum
    credits_below = MINIMUM_CREDITS_REQUIRED - 1
    if credits_below > 0:
        add_credits(user_id, credits_below, "Test setup")
    
    # Verify credits
    actual_credits = get_user_credits(user_id)
    assert actual_credits == credits_below, \
        f"Credits should be {credits_below}, got {actual_credits}"
    
    # Attempt transition
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'online')
    
    # Should fail with one credit below minimum
    assert not result.success, \
        f"Transition should fail with {credits_below} credits (one below minimum)"
    
    # Should provide instructions
    assert "obtain credits" in result.message.lower() or "insufficient" in result.message.lower(), \
        f"Error message should mention obtaining credits: {result.message}"
    
    # Mode should remain offline
    assert get_user_mode(user_id) == 'offline', \
        "Mode should remain 'offline' after failed transition"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    credits=st.integers(min_value=0, max_value=100000)
)
def test_credit_check_happens_before_mode_change(user_id, credits):
    """
    Feature: dual-mode-offline-online, Property 1: Mode Activation with Credit Validation
    
    For any user attempting to activate online mode, the credit check should 
    happen BEFORE the mode state is changed, ensuring atomicity.
    
    **Validates: Requirements 1.4**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set user to offline mode
    set_user_mode(user_id, 'offline')
    initial_mode = get_user_mode(user_id)
    assert initial_mode == 'offline', "Initial mode should be offline"
    
    # Set credits
    if credits > 0:
        add_credits(user_id, credits, "Test setup")
    
    # Attempt transition
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'online')
    
    # Get final mode
    final_mode = get_user_mode(user_id)
    
    # Verify consistency: if transition failed, mode should not have changed
    if not result.success:
        assert final_mode == initial_mode, \
            f"Mode should not change on failed transition: was {initial_mode}, now {final_mode}"
    
    # Verify consistency: if transition succeeded, mode should have changed
    if result.success:
        assert final_mode == 'online', \
            f"Mode should change to 'online' on successful transition, got {final_mode}"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
