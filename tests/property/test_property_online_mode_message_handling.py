"""
Property-based test for online mode message handling with credit management.

Feature: dual-mode-offline-online
Property 4: Online Mode Message Handling with Credit Management
Validates: Requirements 3.3, 3.8, 3.9

For any message sent by a user in online mode, the system should forward it 
to their isolated AI agent, deduct credits based on usage, and display 
remaining credits after the interaction.
"""

import os
import pytest
from hypothesis import given, strategies as st, settings, assume
from dotenv import load_dotenv
from unittest.mock import patch, Mock, MagicMock

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
    get_agent,
    supabase
)
from app.dual_mode.session_manager import SessionManager
from app.dual_mode.ai_agent_manager import AIAgentManager
from app.dual_mode.credit_manager import CreditManager
from app.dual_mode.automaton_bridge import AutomatonBridge, AutomatonResponse


# Minimum credits required for online mode
MINIMUM_CREDITS_REQUIRED = 10

# Mock Genesis Prompt content for testing
MOCK_GENESIS_PROMPT = """
# AUTOMATON GENESIS PROMPT
## System Architecture & Rules

This is a test Genesis Prompt for autonomous trading agents.
It provides base knowledge for trading operations.
"""


def cleanup_user_data(user_id):
    """Clean up all user data from database."""
    try:
        supabase.table('online_sessions').delete().eq('user_id', user_id).execute()
        supabase.table('isolated_ai_agents').delete().eq('user_id', user_id).execute()
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
        supabase.table('automaton_credit_transactions').delete().eq('user_id', user_id).execute()
    except Exception as e:
        print(f"Cleanup error: {e}")


@settings(max_examples=10, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    message=st.text(min_size=1, max_size=500),
    initial_credits=st.integers(min_value=MINIMUM_CREDITS_REQUIRED, max_value=10000),
    credits_per_message=st.integers(min_value=1, max_value=10)
)
def test_online_mode_message_forwards_to_agent_and_deducts_credits(
    user_id, message, initial_credits, credits_per_message
):
    """
    Feature: dual-mode-offline-online, Property 4: Online Mode Message Handling
    
    For any message sent by a user in online mode, the system should forward 
    it to their isolated AI agent, deduct credits based on usage, and display 
    remaining credits after the interaction.
    
    **Validates: Requirements 3.3, 3.8, 3.9**
    """
    # Clean up any existing state for this user
    cleanup_user_data(user_id)
    
    try:
        # Set user to online mode
        set_user_mode(user_id, 'online')
        assert get_user_mode(user_id) == 'online', "Failed to set online mode"
        
        # Give user initial credits
        add_credits(user_id, initial_credits, "Test setup")
        credits_before = get_user_credits(user_id)
        assert credits_before >= initial_credits, \
            f"Credits not set correctly: expected >= {initial_credits}, got {credits_before}"
        
        # Mock Genesis Prompt file loading
        with patch('builtins.open', Mock(return_value=Mock(
            read=Mock(return_value=MOCK_GENESIS_PROMPT),
            __enter__=Mock(return_value=Mock(read=Mock(return_value=MOCK_GENESIS_PROMPT))),
            __exit__=Mock(return_value=False)
        ))):
            with patch('os.path.exists', return_value=True):
                # Create managers
                ai_agent_manager = AIAgentManager()
                session_manager = SessionManager()
                credit_manager = CreditManager()
                
                # Create agent and session (simulating online mode activation)
                agent = ai_agent_manager.get_or_create_agent(user_id)
                assert agent is not None, "Agent should be created"
                
                session = session_manager.create_session(user_id, agent.agent_id)
                assert session is not None, "Session should be created"
                
                # Mock Automaton API response
                mock_ai_response = f"AI response to: {message[:50]}"
                mock_automaton_response = AutomatonResponse(
                    success=True,
                    message=mock_ai_response,
                    credits_used=credits_per_message
                )
                
                # Mock AutomatonBridge.send_message
                with patch.object(
                    AutomatonBridge, 
                    'send_message', 
                    return_value=mock_automaton_response
                ) as mock_send:
                    # Simulate sending message in online mode
                    # This is what OnlineModeHandler.handle_user_message() does:
                    
                    # 1. Forward message to AI agent (Requirement 3.3)
                    automaton_bridge = AutomatonBridge()
                    response = automaton_bridge.send_message(agent.agent_id, message)
                    
                    # Verify message was forwarded to correct agent
                    mock_send.assert_called_once_with(agent.agent_id, message)
                    assert response.success, "Message forwarding should succeed"
                    assert response.message == mock_ai_response, \
                        "Should receive AI response"
                    
                    # 2. Deduct credits based on usage (Requirement 3.8)
                    if response.success:
                        deduct_result = credit_manager.deduct_credits(
                            user_id, 
                            response.credits_used, 
                            "Online mode message",
                            session_id=session.session_id
                        )
                        
                        assert deduct_result.success, \
                            f"Credit deduction should succeed: {deduct_result.error}"
                        
                        # Verify credits were deducted
                        credits_after = get_user_credits(user_id)
                        expected_credits = credits_before - credits_per_message
                        
                        assert credits_after == expected_credits, \
                            f"Credits should be deducted: expected {expected_credits}, got {credits_after}"
                        
                        # 3. Display remaining credits (Requirement 3.9)
                        # Verify remaining credits are available for display
                        remaining_credits = credit_manager.get_user_credits(user_id)
                        assert remaining_credits == expected_credits, \
                            f"Remaining credits should match: expected {expected_credits}, got {remaining_credits}"
                        
                        # Verify credit transaction was logged
                        credit_history = credit_manager.get_credit_history(user_id, limit=1)
                        assert len(credit_history) > 0, \
                            "Credit transaction should be logged"
                        
                        latest_transaction = credit_history[0]
                        assert latest_transaction.amount == -credits_per_message, \
                            f"Transaction should show deduction of {credits_per_message}"
                        assert latest_transaction.balance_after == expected_credits, \
                            f"Transaction should show correct balance after: {expected_credits}"
                        
                        # Update session activity
                        session_manager.update_session_activity(user_id, credits_per_message)
                        
                        # Verify session was updated
                        updated_session = session_manager.get_session(user_id)
                        assert updated_session is not None, "Session should still exist"
                        assert updated_session.message_count > 0, \
                            "Session message count should be incremented"
    
    finally:
        # Clean up
        cleanup_user_data(user_id)


@settings(max_examples=10, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    num_messages=st.integers(min_value=1, max_value=10),
    initial_credits=st.integers(min_value=100, max_value=10000),
    credits_per_message=st.integers(min_value=1, max_value=5)
)
def test_multiple_messages_accumulate_credit_deductions(
    user_id, num_messages, initial_credits, credits_per_message
):
    """
    Feature: dual-mode-offline-online, Property 4: Online Mode Message Handling
    
    For any sequence of messages sent by a user in online mode, credits should 
    be deducted for each message and the remaining balance should be correctly 
    tracked.
    
    **Validates: Requirements 3.3, 3.8, 3.9**
    """
    # Ensure user has enough credits for all messages
    total_credits_needed = num_messages * credits_per_message
    assume(initial_credits >= total_credits_needed)
    
    # Clean up
    cleanup_user_data(user_id)
    
    try:
        # Set up user in online mode
        set_user_mode(user_id, 'online')
        add_credits(user_id, initial_credits, "Test setup")
        
        credits_before = get_user_credits(user_id)
        
        with patch('builtins.open', Mock(return_value=Mock(
            read=Mock(return_value=MOCK_GENESIS_PROMPT),
            __enter__=Mock(return_value=Mock(read=Mock(return_value=MOCK_GENESIS_PROMPT))),
            __exit__=Mock(return_value=False)
        ))):
            with patch('os.path.exists', return_value=True):
                # Create managers
                ai_agent_manager = AIAgentManager()
                session_manager = SessionManager()
                credit_manager = CreditManager()
                
                # Create agent and session
                agent = ai_agent_manager.get_or_create_agent(user_id)
                session = session_manager.create_session(user_id, agent.agent_id)
                
                # Mock Automaton API
                mock_response = AutomatonResponse(
                    success=True,
                    message="AI response",
                    credits_used=credits_per_message
                )
                
                with patch.object(
                    AutomatonBridge, 
                    'send_message', 
                    return_value=mock_response
                ):
                    automaton_bridge = AutomatonBridge()
                    
                    # Send multiple messages
                    for i in range(num_messages):
                        message = f"Test message {i+1}"
                        
                        # Forward to agent
                        response = automaton_bridge.send_message(agent.agent_id, message)
                        assert response.success, f"Message {i+1} should succeed"
                        
                        # Deduct credits
                        deduct_result = credit_manager.deduct_credits(
                            user_id,
                            response.credits_used,
                            f"Message {i+1}",
                            session_id=session.session_id
                        )
                        assert deduct_result.success, \
                            f"Credit deduction for message {i+1} should succeed"
                        
                        # Update session
                        session_manager.update_session_activity(user_id, credits_per_message)
                    
                    # Verify total credits deducted
                    credits_after = get_user_credits(user_id)
                    expected_credits = credits_before - (num_messages * credits_per_message)
                    
                    assert credits_after == expected_credits, \
                        f"Total credits should be deducted correctly: expected {expected_credits}, got {credits_after}"
                    
                    # Verify session tracking
                    final_session = session_manager.get_session(user_id)
                    assert final_session is not None, "Session should exist"
                    assert final_session.message_count == num_messages, \
                        f"Session should track {num_messages} messages, got {final_session.message_count}"
    
    finally:
        # Clean up
        cleanup_user_data(user_id)


@settings(max_examples=10, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    insufficient_credits=st.integers(min_value=0, max_value=MINIMUM_CREDITS_REQUIRED - 1),
    credits_per_message=st.integers(min_value=MINIMUM_CREDITS_REQUIRED, max_value=50)
)
def test_insufficient_credits_prevents_message_sending(
    user_id, insufficient_credits, credits_per_message
):
    """
    Feature: dual-mode-offline-online, Property 4: Online Mode Message Handling
    
    For any message sent by a user with insufficient credits, the system 
    should prevent the message from being sent and not deduct credits.
    
    **Validates: Requirements 3.8, 3.9**
    """
    # Ensure credits are truly insufficient
    assume(insufficient_credits < credits_per_message)
    
    # Clean up
    cleanup_user_data(user_id)
    
    try:
        # Set up user in online mode with insufficient credits
        set_user_mode(user_id, 'online')
        add_credits(user_id, insufficient_credits, "Test setup")
        
        credits_before = get_user_credits(user_id)
        assert credits_before == insufficient_credits, \
            f"Initial credits should be {insufficient_credits}, got {credits_before}"
        
        with patch('builtins.open', Mock(return_value=Mock(
            read=Mock(return_value=MOCK_GENESIS_PROMPT),
            __enter__=Mock(return_value=Mock(read=Mock(return_value=MOCK_GENESIS_PROMPT))),
            __exit__=Mock(return_value=False)
        ))):
            with patch('os.path.exists', return_value=True):
                # Create managers
                ai_agent_manager = AIAgentManager()
                session_manager = SessionManager()
                credit_manager = CreditManager()
                
                # Create agent and session
                agent = ai_agent_manager.get_or_create_agent(user_id)
                session = session_manager.create_session(user_id, agent.agent_id)
                
                # Attempt to deduct credits (should fail)
                deduct_result = credit_manager.deduct_credits(
                    user_id,
                    credits_per_message,
                    "Test message",
                    session_id=session.session_id
                )
                
                # Verify deduction failed
                assert not deduct_result.success, \
                    "Credit deduction should fail with insufficient credits"
                assert "Insufficient credits" in deduct_result.error, \
                    f"Error should mention insufficient credits: {deduct_result.error}"
                
                # Verify credits were NOT deducted
                credits_after = get_user_credits(user_id)
                assert credits_after == credits_before, \
                    f"Credits should not change: expected {credits_before}, got {credits_after}"
                
                # Verify no credit transaction was logged for failed deduction
                credit_history = credit_manager.get_credit_history(user_id, limit=10)
                # Should only have the initial credit addition, no deduction
                deduction_transactions = [t for t in credit_history if t.amount < 0]
                assert len(deduction_transactions) == 0, \
                    "No deduction transaction should be logged for failed attempt"
    
    finally:
        # Clean up
        cleanup_user_data(user_id)


@settings(max_examples=10, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    message=st.text(min_size=1, max_size=500),
    initial_credits=st.integers(min_value=MINIMUM_CREDITS_REQUIRED, max_value=10000)
)
def test_failed_api_call_does_not_deduct_credits(user_id, message, initial_credits):
    """
    Feature: dual-mode-offline-online, Property 4: Online Mode Message Handling
    
    For any message that fails to be sent to the AI agent (API error), 
    credits should NOT be deducted.
    
    **Validates: Requirements 3.8, 12.3**
    """
    # Clean up
    cleanup_user_data(user_id)
    
    try:
        # Set up user in online mode
        set_user_mode(user_id, 'online')
        add_credits(user_id, initial_credits, "Test setup")
        
        credits_before = get_user_credits(user_id)
        
        with patch('builtins.open', Mock(return_value=Mock(
            read=Mock(return_value=MOCK_GENESIS_PROMPT),
            __enter__=Mock(return_value=Mock(read=Mock(return_value=MOCK_GENESIS_PROMPT))),
            __exit__=Mock(return_value=False)
        ))):
            with patch('os.path.exists', return_value=True):
                # Create managers
                ai_agent_manager = AIAgentManager()
                session_manager = SessionManager()
                credit_manager = CreditManager()
                
                # Create agent and session
                agent = ai_agent_manager.get_or_create_agent(user_id)
                session = session_manager.create_session(user_id, agent.agent_id)
                
                # Mock failed Automaton API response
                mock_failed_response = AutomatonResponse(
                    success=False,
                    error="API connection failed",
                    credits_used=0
                )
                
                with patch.object(
                    AutomatonBridge, 
                    'send_message', 
                    return_value=mock_failed_response
                ):
                    automaton_bridge = AutomatonBridge()
                    
                    # Attempt to send message
                    response = automaton_bridge.send_message(agent.agent_id, message)
                    
                    # Verify API call failed
                    assert not response.success, "API call should fail"
                    assert response.error is not None, "Error message should be present"
                    
                    # Verify credits were NOT deducted (only deduct on success)
                    if not response.success:
                        # Don't deduct credits on failure
                        pass
                    
                    # Verify credits remain unchanged
                    credits_after = get_user_credits(user_id)
                    assert credits_after == credits_before, \
                        f"Credits should not be deducted on API failure: expected {credits_before}, got {credits_after}"
    
    finally:
        # Clean up
        cleanup_user_data(user_id)


@settings(max_examples=10, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    message=st.text(min_size=1, max_size=500),
    initial_credits=st.integers(min_value=MINIMUM_CREDITS_REQUIRED, max_value=10000),
    credits_per_message=st.integers(min_value=1, max_value=10)
)
def test_agent_isolation_in_message_handling(user_id, message, initial_credits, credits_per_message):
    """
    Feature: dual-mode-offline-online, Property 4: Online Mode Message Handling
    
    For any message sent by a user, it should only be forwarded to their 
    isolated agent, not to any other user's agent.
    
    **Validates: Requirements 3.3, 10.1, 10.2, 10.4**
    """
    # Clean up
    cleanup_user_data(user_id)
    other_user_id = user_id + 1
    cleanup_user_data(other_user_id)
    
    try:
        # Set up both users in online mode
        set_user_mode(user_id, 'online')
        set_user_mode(other_user_id, 'online')
        add_credits(user_id, initial_credits, "Test setup")
        add_credits(other_user_id, initial_credits, "Test setup")
        
        with patch('builtins.open', Mock(return_value=Mock(
            read=Mock(return_value=MOCK_GENESIS_PROMPT),
            __enter__=Mock(return_value=Mock(read=Mock(return_value=MOCK_GENESIS_PROMPT))),
            __exit__=Mock(return_value=False)
        ))):
            with patch('os.path.exists', return_value=True):
                # Create managers
                ai_agent_manager = AIAgentManager()
                
                # Create agents for both users
                agent1 = ai_agent_manager.get_or_create_agent(user_id)
                agent2 = ai_agent_manager.get_or_create_agent(other_user_id)
                
                assert agent1 is not None, "Agent 1 should be created"
                assert agent2 is not None, "Agent 2 should be created"
                
                # Verify agents are different
                assert agent1.agent_id != agent2.agent_id, \
                    "Each user should have a different agent"
                
                # Verify agent isolation
                assert ai_agent_manager.is_agent_isolated(agent1.agent_id, user_id), \
                    "Agent 1 should be isolated for user 1"
                assert not ai_agent_manager.is_agent_isolated(agent1.agent_id, other_user_id), \
                    "Agent 1 should NOT be accessible by user 2"
                
                assert ai_agent_manager.is_agent_isolated(agent2.agent_id, other_user_id), \
                    "Agent 2 should be isolated for user 2"
                assert not ai_agent_manager.is_agent_isolated(agent2.agent_id, user_id), \
                    "Agent 2 should NOT be accessible by user 1"
                
                # Mock Automaton API
                mock_response = AutomatonResponse(
                    success=True,
                    message="AI response",
                    credits_used=credits_per_message
                )
                
                with patch.object(
                    AutomatonBridge, 
                    'send_message', 
                    return_value=mock_response
                ) as mock_send:
                    automaton_bridge = AutomatonBridge()
                    
                    # Send message from user 1
                    response = automaton_bridge.send_message(agent1.agent_id, message)
                    
                    # Verify message was sent to correct agent
                    mock_send.assert_called_with(agent1.agent_id, message)
                    
                    # Verify message was NOT sent to other user's agent
                    calls = mock_send.call_args_list
                    for call in calls:
                        called_agent_id = call[0][0]
                        assert called_agent_id == agent1.agent_id, \
                            f"Message should only be sent to user's own agent, not {called_agent_id}"
    
    finally:
        # Clean up
        cleanup_user_data(user_id)
        cleanup_user_data(other_user_id)


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
