"""
Property-based test for mode transition performance.

Feature: dual-mode-offline-online
Property 15: Mode Transition Performance
Validates: Requirements 9.4, 9.5

For any mode transition, the system should complete the operation within 2 seconds 
and display a loading indicator during the transition.
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
    supabase
)
from app.dual_mode.mode_state_manager import ModeStateManager


# Maximum allowed transition duration in milliseconds (2 seconds = 2000ms)
MAX_TRANSITION_DURATION_MS = 2000

# Minimum credits required for online mode
MINIMUM_CREDITS_REQUIRED = 10


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    from_mode=st.sampled_from(['offline', 'online']),
    to_mode=st.sampled_from(['offline', 'online'])
)
def test_mode_transition_completes_within_2_seconds(user_id, from_mode, to_mode):
    """
    Feature: dual-mode-offline-online, Property 15: Mode Transition Performance
    
    For any mode transition, the system should complete the operation within 
    2 seconds and display a loading indicator during the transition.
    
    **Validates: Requirements 9.4, 9.5**
    """
    # Skip if from_mode and to_mode are the same (not a real transition)
    if from_mode == to_mode:
        return
    
    # Clean up any existing state for this user
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set user to initial mode
    set_user_mode(user_id, from_mode)
    assert get_user_mode(user_id) == from_mode, f"Failed to set initial mode to {from_mode}"
    
    # If transitioning to online mode, ensure user has sufficient credits
    if to_mode == 'online':
        add_credits(user_id, MINIMUM_CREDITS_REQUIRED + 100, "Test setup")
        actual_credits = get_user_credits(user_id)
        assert actual_credits >= MINIMUM_CREDITS_REQUIRED, \
            f"Failed to set sufficient credits: expected >= {MINIMUM_CREDITS_REQUIRED}, got {actual_credits}"
    
    # Create ModeStateManager instance
    manager = ModeStateManager()
    
    # Perform the transition
    result = manager.transition_mode(user_id, from_mode, to_mode)
    
    # Requirement 9.5: Transition should complete within 2 seconds
    assert result.duration_ms is not None, \
        "Transition result should include duration_ms"
    
    assert result.duration_ms <= MAX_TRANSITION_DURATION_MS, \
        f"Transition took {result.duration_ms}ms, exceeds maximum of {MAX_TRANSITION_DURATION_MS}ms (2 seconds)"
    
    # Verify the transition was successful (given we provided sufficient credits)
    assert result.success, \
        f"Transition from {from_mode} to {to_mode} should succeed: {result.error}"
    
    # Verify mode was actually changed
    final_mode = get_user_mode(user_id)
    assert final_mode == to_mode, \
        f"Mode should be '{to_mode}' after transition, got '{final_mode}'"
    
    # Requirement 9.4: Verify transition duration is logged
    # Check that the transition was logged in the mode_transition_log table
    try:
        log_result = supabase.table('mode_transition_log') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('from_mode', from_mode) \
            .eq('to_mode', to_mode) \
            .order('timestamp', desc=True) \
            .limit(1) \
            .execute()
        
        assert log_result.data and len(log_result.data) > 0, \
            "Transition should be logged in mode_transition_log table"
        
        log_entry = log_result.data[0]
        assert log_entry['success'] == True, \
            "Logged transition should be marked as successful"
        
        assert log_entry['duration_ms'] is not None, \
            "Logged transition should include duration_ms"
        
        assert log_entry['duration_ms'] == result.duration_ms, \
            f"Logged duration ({log_entry['duration_ms']}ms) should match result duration ({result.duration_ms}ms)"
    except Exception as e:
        pytest.fail(f"Failed to verify transition logging: {e}")
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('mode_transition_log').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999)
)
def test_offline_to_online_transition_performance(user_id):
    """
    Feature: dual-mode-offline-online, Property 15: Mode Transition Performance
    
    For any offline to online mode transition with sufficient credits, the 
    system should complete within 2 seconds.
    
    **Validates: Requirements 9.4, 9.5**
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
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED + 100, "Test setup")
    
    # Perform transition
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'online')
    
    # Verify success
    assert result.success, f"Transition should succeed: {result.error}"
    
    # Verify performance
    assert result.duration_ms is not None, "Result should include duration_ms"
    assert result.duration_ms <= MAX_TRANSITION_DURATION_MS, \
        f"Offline to online transition took {result.duration_ms}ms, exceeds {MAX_TRANSITION_DURATION_MS}ms"
    
    # Verify mode changed
    assert get_user_mode(user_id) == 'online', "Mode should be 'online' after transition"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('mode_transition_log').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999)
)
def test_online_to_offline_transition_performance(user_id):
    """
    Feature: dual-mode-offline-online, Property 15: Mode Transition Performance
    
    For any online to offline mode transition, the system should complete 
    within 2 seconds (including graceful session cleanup).
    
    **Validates: Requirements 9.4, 9.5**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set user to online mode (requires credits first)
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED + 100, "Test setup")
    set_user_mode(user_id, 'online')
    assert get_user_mode(user_id) == 'online', "Failed to set initial online mode"
    
    # Perform transition to offline
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'online', 'offline')
    
    # Verify success
    assert result.success, f"Transition should succeed: {result.error}"
    
    # Verify performance
    assert result.duration_ms is not None, "Result should include duration_ms"
    assert result.duration_ms <= MAX_TRANSITION_DURATION_MS, \
        f"Online to offline transition took {result.duration_ms}ms, exceeds {MAX_TRANSITION_DURATION_MS}ms"
    
    # Verify mode changed
    assert get_user_mode(user_id) == 'offline', "Mode should be 'offline' after transition"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('mode_transition_log').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999)
)
def test_failed_transition_also_completes_quickly(user_id):
    """
    Feature: dual-mode-offline-online, Property 15: Mode Transition Performance
    
    Even failed transitions (e.g., insufficient credits) should complete 
    within 2 seconds and log the duration.
    
    **Validates: Requirements 9.4, 9.5**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set user to offline mode with insufficient credits
    set_user_mode(user_id, 'offline')
    # Don't add credits, so transition to online will fail
    
    # Attempt transition to online (should fail due to insufficient credits)
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'online')
    
    # Verify it failed
    assert not result.success, "Transition should fail with insufficient credits"
    
    # Verify performance even for failed transitions
    assert result.duration_ms is not None, "Failed transition should still include duration_ms"
    assert result.duration_ms <= MAX_TRANSITION_DURATION_MS, \
        f"Failed transition took {result.duration_ms}ms, exceeds {MAX_TRANSITION_DURATION_MS}ms"
    
    # Verify mode did not change
    assert get_user_mode(user_id) == 'offline', "Mode should remain 'offline' after failed transition"
    
    # Verify failed transition is also logged
    try:
        log_result = supabase.table('mode_transition_log') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('from_mode', 'offline') \
            .eq('to_mode', 'online') \
            .order('timestamp', desc=True) \
            .limit(1) \
            .execute()
        
        assert log_result.data and len(log_result.data) > 0, \
            "Failed transition should be logged"
        
        log_entry = log_result.data[0]
        assert log_entry['success'] == False, \
            "Logged transition should be marked as failed"
        
        assert log_entry['duration_ms'] is not None, \
            "Failed transition log should include duration_ms"
    except Exception as e:
        pytest.fail(f"Failed to verify failed transition logging: {e}")
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('mode_transition_log').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999)
)
def test_transition_duration_is_always_positive(user_id):
    """
    Feature: dual-mode-offline-online, Property 15: Mode Transition Performance
    
    For any mode transition, the duration should always be a positive number 
    (sanity check for timing logic).
    
    **Validates: Requirements 9.5**
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
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED + 100, "Test setup")
    
    # Perform transition
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'online')
    
    # Verify duration is positive
    assert result.duration_ms is not None, "Result should include duration_ms"
    assert result.duration_ms > 0, \
        f"Duration should be positive, got {result.duration_ms}ms"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('mode_transition_log').delete().eq('user_id', user_id).execute()
    except:
        pass


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
