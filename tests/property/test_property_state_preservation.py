"""
Property-based test for state preservation during transitions.

Feature: dual-mode-offline-online
Property 9: State Preservation During Transitions
Validates: Requirements 9.1, 9.2, 9.3

For any mode transition, the system should preserve the previous mode's state,
gracefully close any active sessions, maintain user data integrity, and complete
the transition without data loss.
"""

import os
import pytest
from hypothesis import given, strategies as st, settings, assume
from dotenv import load_dotenv
from uuid import UUID
import json
from datetime import datetime

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
    create_session,
    close_session,
    get_offline_state,
    create_agent,
    get_agent,
    supabase
)
from app.dual_mode.mode_state_manager import ModeStateManager


# Minimum credits required for online mode
MINIMUM_CREDITS_REQUIRED = 10


# Strategy for generating offline state data
@st.composite
def offline_state_strategy(draw):
    """Generate random offline state data."""
    # Generate datetime and convert to ISO format string
    dt = draw(st.datetimes(
        min_value=datetime(2024, 1, 1),
        max_value=datetime(2024, 12, 31)
    ))
    
    return {
        'last_symbol': draw(st.sampled_from(['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT'])),
        'last_timeframe': draw(st.sampled_from(['1h', '4h', '1d'])),
        'trading_context': {
            'analysis_count': draw(st.integers(min_value=0, max_value=100)),
            'last_analysis_time': dt.isoformat(),
            'preferences': {
                'show_smc': draw(st.booleans()),
                'show_indicators': draw(st.booleans())
            }
        }
    }


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    offline_state=offline_state_strategy()
)
def test_offline_state_preserved_during_transition_to_online(user_id, offline_state):
    """
    Feature: dual-mode-offline-online, Property 9: State Preservation During Transitions
    
    For any transition from offline to online mode, the system should preserve
    the offline state so it can be restored when returning to offline mode.
    
    **Validates: Requirements 9.1**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set user to offline mode with state
    set_user_mode(user_id, 'offline', offline_state=offline_state)
    assert get_user_mode(user_id) == 'offline'
    
    # Verify offline state was stored
    stored_state = get_offline_state(user_id)
    assert stored_state is not None, "Offline state should be stored"
    assert stored_state == offline_state, \
        f"Stored state doesn't match: expected {offline_state}, got {stored_state}"
    
    # Add sufficient credits for online mode
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED + 10, "Test setup")
    
    # Transition to online mode
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'online')
    
    assert result.success, f"Transition should succeed: {result.error}"
    assert get_user_mode(user_id) == 'online'
    
    # Verify offline state is still preserved after transition
    preserved_state = get_offline_state(user_id)
    assert preserved_state is not None, "Offline state should be preserved after transition"
    assert preserved_state == offline_state, \
        f"Preserved state doesn't match original: expected {offline_state}, got {preserved_state}"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    session_messages=st.integers(min_value=1, max_value=50),
    credits_used=st.integers(min_value=1, max_value=100)
)
def test_active_session_closed_gracefully_during_transition_to_offline(user_id, session_messages, credits_used):
    """
    Feature: dual-mode-offline-online, Property 9: State Preservation During Transitions
    
    For any transition from online to offline mode, the system should gracefully
    close any active sessions without data loss.
    
    **Validates: Requirements 9.2**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Create agent for user
    agent_id = f"agent_{user_id}"
    create_agent(user_id, agent_id, "Test genesis prompt")
    
    # Add credits and set to online mode
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED + 100, "Test setup")
    set_user_mode(user_id, 'online')
    assert get_user_mode(user_id) == 'online'
    
    # Create an active session
    session_id = create_session(user_id, agent_id)
    assert session_id is not None, "Session should be created"
    
    # Simulate session activity
    from app.dual_mode_db import update_session_activity
    for _ in range(session_messages):
        update_session_activity(session_id, credits_used=1)
    
    # Verify session is active
    active_session = get_active_session(user_id)
    assert active_session is not None, "Session should be active"
    assert active_session['status'] == 'active'
    assert active_session['message_count'] == session_messages
    
    # Store session data before transition
    session_data_before = {
        'session_id': active_session['session_id'],
        'message_count': active_session['message_count'],
        'credits_used': active_session['credits_used']
    }
    
    # Transition to offline mode
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'online', 'offline')
    
    assert result.success, f"Transition should succeed: {result.error}"
    assert get_user_mode(user_id) == 'offline'
    
    # Verify session was closed gracefully
    active_session_after = get_active_session(user_id)
    assert active_session_after is None, "No active session should exist after transition"
    
    # Verify session data was preserved (status changed to 'closed')
    closed_session = supabase.table('online_sessions')\
        .select('*')\
        .eq('session_id', session_data_before['session_id'])\
        .execute()
    
    assert closed_session.data and len(closed_session.data) > 0, \
        "Session record should still exist"
    
    session_record = closed_session.data[0]
    assert session_record['status'] == 'closed', "Session should be marked as closed"
    assert session_record['message_count'] == session_data_before['message_count'], \
        "Message count should be preserved"
    assert session_record['closed_at'] is not None, "Closed timestamp should be set"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    initial_credits=st.integers(min_value=MINIMUM_CREDITS_REQUIRED, max_value=1000),
    offline_state=offline_state_strategy()
)
def test_user_data_integrity_maintained_during_transitions(user_id, initial_credits, offline_state):
    """
    Feature: dual-mode-offline-online, Property 9: State Preservation During Transitions
    
    For any mode transition, user data (credits, state, history) should maintain
    integrity without corruption or loss.
    
    **Validates: Requirements 9.3**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set up initial state
    set_user_mode(user_id, 'offline', offline_state=offline_state)
    add_credits(user_id, initial_credits, "Initial credits")
    
    # Capture initial data
    initial_mode = get_user_mode(user_id)
    initial_credit_balance = get_user_credits(user_id)
    initial_offline_state = get_offline_state(user_id)
    
    assert initial_mode == 'offline'
    assert initial_credit_balance == initial_credits
    assert initial_offline_state == offline_state
    
    # Transition to online mode
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'online')
    
    assert result.success, f"Transition to online should succeed: {result.error}"
    
    # Verify data integrity after transition to online
    assert get_user_mode(user_id) == 'online', "Mode should be online"
    assert get_user_credits(user_id) == initial_credit_balance, \
        "Credits should not change during transition"
    assert get_offline_state(user_id) == offline_state, \
        "Offline state should be preserved"
    
    # Transition back to offline mode
    result = manager.transition_mode(user_id, 'online', 'offline')
    
    assert result.success, f"Transition to offline should succeed: {result.error}"
    
    # Verify data integrity after transition back to offline
    assert get_user_mode(user_id) == 'offline', "Mode should be offline"
    assert get_user_credits(user_id) == initial_credit_balance, \
        "Credits should remain unchanged after round-trip transition"
    assert get_offline_state(user_id) == offline_state, \
        "Offline state should still be preserved after round-trip"
    
    # Verify transition history was logged
    from app.dual_mode_db import get_mode_history
    history = get_mode_history(user_id, limit=10)
    
    assert len(history) >= 2, "At least 2 transitions should be logged"
    
    # Verify both transitions were successful
    for transition in history[:2]:
        assert transition['success'], "All transitions should be successful"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    offline_state=offline_state_strategy(),
    credits=st.integers(min_value=MINIMUM_CREDITS_REQUIRED, max_value=1000)
)
def test_no_data_loss_during_failed_transition(user_id, offline_state, credits):
    """
    Feature: dual-mode-offline-online, Property 9: State Preservation During Transitions
    
    For any failed mode transition, no data should be lost and the user should
    remain in their previous mode with all data intact.
    
    **Validates: Requirements 9.3, 9.6**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set up initial state
    set_user_mode(user_id, 'offline', offline_state=offline_state)
    add_credits(user_id, credits, "Test setup")
    
    # Capture initial data
    initial_mode = get_user_mode(user_id)
    initial_credits = get_user_credits(user_id)
    initial_state = get_offline_state(user_id)
    
    # Attempt transition with invalid mode (should fail)
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'invalid_mode')
    
    assert not result.success, "Transition with invalid mode should fail"
    
    # Verify no data was lost
    assert get_user_mode(user_id) == initial_mode, \
        "Mode should remain unchanged after failed transition"
    assert get_user_credits(user_id) == initial_credits, \
        "Credits should remain unchanged after failed transition"
    assert get_offline_state(user_id) == initial_state, \
        "Offline state should remain unchanged after failed transition"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    offline_state=offline_state_strategy()
)
def test_offline_state_can_be_restored_after_online_session(user_id, offline_state):
    """
    Feature: dual-mode-offline-online, Property 9: State Preservation During Transitions
    
    For any user who transitions from offline to online and back, their offline
    state should be fully restorable.
    
    **Validates: Requirements 9.1**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set up offline mode with state
    set_user_mode(user_id, 'offline', offline_state=offline_state)
    original_state = get_offline_state(user_id)
    assert original_state == offline_state
    
    # Add credits and transition to online
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED + 50, "Test setup")
    
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'offline', 'online')
    assert result.success
    
    # Verify state is preserved during online mode
    state_during_online = get_offline_state(user_id)
    assert state_during_online == offline_state, \
        "Offline state should be preserved during online mode"
    
    # Transition back to offline
    result = manager.transition_mode(user_id, 'online', 'offline')
    assert result.success
    
    # Verify state is fully restored
    restored_state = get_offline_state(user_id)
    assert restored_state == offline_state, \
        f"Offline state should be fully restored: expected {offline_state}, got {restored_state}"
    
    # Verify all fields match
    assert restored_state['last_symbol'] == offline_state['last_symbol']
    assert restored_state['last_timeframe'] == offline_state['last_timeframe']
    assert restored_state['trading_context'] == offline_state['trading_context']
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999)
)
def test_multiple_sessions_closed_gracefully(user_id):
    """
    Feature: dual-mode-offline-online, Property 9: State Preservation During Transitions
    
    For any user with multiple session history, transitioning to offline should
    only close the active session while preserving historical session data.
    
    **Validates: Requirements 9.2**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Create agent
    agent_id = f"agent_{user_id}"
    create_agent(user_id, agent_id, "Test genesis prompt")
    
    # Add credits
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED + 100, "Test setup")
    
    # Create and close a historical session
    set_user_mode(user_id, 'online')
    historical_session_id = create_session(user_id, agent_id)
    assert historical_session_id is not None
    close_session(historical_session_id)
    
    # Create a new active session
    active_session_id = create_session(user_id, agent_id)
    assert active_session_id is not None
    
    # Verify we have one active and one closed session
    all_sessions = supabase.table('online_sessions')\
        .select('*')\
        .eq('user_id', user_id)\
        .execute()
    
    assert len(all_sessions.data) == 2, "Should have 2 sessions"
    
    active_count = sum(1 for s in all_sessions.data if s['status'] == 'active')
    closed_count = sum(1 for s in all_sessions.data if s['status'] == 'closed')
    
    assert active_count == 1, "Should have 1 active session"
    assert closed_count == 1, "Should have 1 closed session"
    
    # Transition to offline
    manager = ModeStateManager()
    result = manager.transition_mode(user_id, 'online', 'offline')
    assert result.success
    
    # Verify only the active session was closed
    all_sessions_after = supabase.table('online_sessions')\
        .select('*')\
        .eq('user_id', user_id)\
        .execute()
    
    assert len(all_sessions_after.data) == 2, "Should still have 2 sessions"
    
    # All sessions should now be closed
    for session in all_sessions_after.data:
        assert session['status'] == 'closed', "All sessions should be closed"
        assert session['closed_at'] is not None, "All sessions should have closed_at timestamp"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
    except:
        pass


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
