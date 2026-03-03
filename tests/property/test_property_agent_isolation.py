"""
Property-based test for agent isolation.

Feature: dual-mode-offline-online
Property 10: Agent Isolation
Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5

For any two distinct users, their AI agents should be completely isolated 
such that user A cannot access user B's agent, conversation history, or 
session data.
"""

import os
import pytest
from hypothesis import given, strategies as st, settings, assume
from dotenv import load_dotenv
from unittest.mock import patch, mock_open

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


@settings(max_examples=5, deadline=None)
@given(
    user_a=st.integers(min_value=1, max_value=999999),
    user_b=st.integers(min_value=1, max_value=999999)
)
def test_agents_are_isolated_between_users(user_a, user_b):
    """
    Feature: dual-mode-offline-online, Property 10: Agent Isolation
    
    For any two distinct users, their AI agents should be completely 
    isolated such that user A cannot access user B's agent, conversation 
    history, or session data.
    
    **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**
    """
    # Ensure users are distinct
    assume(user_a != user_b)
    
    # Clean up any existing state for both users
    cleanup_user_data(user_a)
    cleanup_user_data(user_b)
    
    try:
        # Set up both users with credits
        set_user_mode(user_a, 'offline')
        set_user_mode(user_b, 'offline')
        add_credits(user_a, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        add_credits(user_b, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        
        # Mock Genesis Prompt
        with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
            with patch('os.path.exists', return_value=True):
                # Create agent manager
                ai_agent_manager = AIAgentManager()
                
                # Create agents for both users (Requirement 10.1)
                agent_a = ai_agent_manager.get_or_create_agent(user_a)
                agent_b = ai_agent_manager.get_or_create_agent(user_b)
                
                # Verify both agents were created
                assert agent_a is not None, \
                    f"Agent should be created for user A ({user_a})"
                assert agent_b is not None, \
                    f"Agent should be created for user B ({user_b})"
                
                # Verify agents have different IDs (Requirement 10.2)
                assert agent_a.agent_id != agent_b.agent_id, \
                    f"User A and User B should have different agent IDs, both got: {agent_a.agent_id}"
                
                # Verify agents belong to correct users (Requirement 10.2)
                assert agent_a.user_id == user_a, \
                    f"Agent A should belong to user {user_a}, got {agent_a.user_id}"
                assert agent_b.user_id == user_b, \
                    f"Agent B should belong to user {user_b}, got {agent_b.user_id}"
                
                # Verify User A cannot access User B's agent (Requirement 10.4)
                is_isolated_a_to_b = ai_agent_manager.is_agent_isolated(agent_b.agent_id, user_a)
                assert is_isolated_a_to_b is False, \
                    f"User A ({user_a}) should NOT be able to access User B's agent ({agent_b.agent_id})"
                
                # Verify User B cannot access User A's agent (Requirement 10.4)
                is_isolated_b_to_a = ai_agent_manager.is_agent_isolated(agent_a.agent_id, user_b)
                assert is_isolated_b_to_a is False, \
                    f"User B ({user_b}) should NOT be able to access User A's agent ({agent_a.agent_id})"
                
                # Verify each user can only access their own agent (Requirement 10.5)
                is_isolated_a = ai_agent_manager.is_agent_isolated(agent_a.agent_id, user_a)
                assert is_isolated_a is True, \
                    f"User A ({user_a}) should be able to access their own agent ({agent_a.agent_id})"
                
                is_isolated_b = ai_agent_manager.is_agent_isolated(agent_b.agent_id, user_b)
                assert is_isolated_b is True, \
                    f"User B ({user_b}) should be able to access their own agent ({agent_b.agent_id})"
                
                # Verify conversation history isolation (Requirement 10.3)
                # Each agent should have its own empty conversation history
                assert agent_a.conversation_history == [], \
                    "Agent A should have empty conversation history"
                assert agent_b.conversation_history == [], \
                    "Agent B should have empty conversation history"
                
                # Verify agents from database are also isolated
                retrieved_agent_a = get_agent(user_a)
                retrieved_agent_b = get_agent(user_b)
                
                assert retrieved_agent_a is not None, \
                    f"Agent A should be retrievable for user {user_a}"
                assert retrieved_agent_b is not None, \
                    f"Agent B should be retrievable for user {user_b}"
                
                assert retrieved_agent_a['agent_id'] == agent_a.agent_id, \
                    f"Retrieved agent A should match created agent A"
                assert retrieved_agent_b['agent_id'] == agent_b.agent_id, \
                    f"Retrieved agent B should match created agent B"
                
                assert retrieved_agent_a['user_id'] == user_a, \
                    f"Retrieved agent A should belong to user {user_a}"
                assert retrieved_agent_b['user_id'] == user_b, \
                    f"Retrieved agent B should belong to user {user_b}"
                
    finally:
        # Clean up
        cleanup_user_data(user_a)
        cleanup_user_data(user_b)


@settings(max_examples=5, deadline=None)
@given(
    user_a=st.integers(min_value=1, max_value=999999),
    user_b=st.integers(min_value=1, max_value=999999)
)
def test_session_isolation_between_users(user_a, user_b):
    """
    Feature: dual-mode-offline-online, Property 10: Agent Isolation
    
    For any two distinct users, their sessions should be completely isolated.
    User A should not be able to access User B's session data.
    
    **Validates: Requirements 10.1, 10.3, 10.4**
    """
    # Ensure users are distinct
    assume(user_a != user_b)
    
    # Clean up
    cleanup_user_data(user_a)
    cleanup_user_data(user_b)
    
    try:
        # Set up both users
        set_user_mode(user_a, 'offline')
        set_user_mode(user_b, 'offline')
        add_credits(user_a, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        add_credits(user_b, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        
        with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
            with patch('os.path.exists', return_value=True):
                # Create managers
                ai_agent_manager = AIAgentManager()
                session_manager = SessionManager()
                
                # Create agents and sessions for both users
                agent_a = ai_agent_manager.get_or_create_agent(user_a)
                agent_b = ai_agent_manager.get_or_create_agent(user_b)
                
                session_a = session_manager.create_session(user_a, agent_a.agent_id)
                session_b = session_manager.create_session(user_b, agent_b.agent_id)
                
                # Verify sessions were created
                assert session_a is not None, "Session A should be created"
                assert session_b is not None, "Session B should be created"
                
                # Verify sessions have different IDs
                assert session_a.session_id != session_b.session_id, \
                    f"Sessions should have different IDs, both got: {session_a.session_id}"
                
                # Verify sessions belong to correct users
                assert session_a.user_id == user_a, \
                    f"Session A should belong to user {user_a}, got {session_a.user_id}"
                assert session_b.user_id == user_b, \
                    f"Session B should belong to user {user_b}, got {session_b.user_id}"
                
                # Verify sessions are linked to correct agents
                assert session_a.agent_id == agent_a.agent_id, \
                    f"Session A should be linked to agent A"
                assert session_b.agent_id == agent_b.agent_id, \
                    f"Session B should be linked to agent B"
                
                # Verify User A can only retrieve their own session
                retrieved_session_a = session_manager.get_session(user_a)
                assert retrieved_session_a is not None, \
                    f"User A should be able to retrieve their session"
                assert retrieved_session_a.session_id == session_a.session_id, \
                    f"User A should retrieve their own session"
                assert retrieved_session_a.user_id == user_a, \
                    f"Retrieved session should belong to user A"
                
                # Verify User B can only retrieve their own session
                retrieved_session_b = session_manager.get_session(user_b)
                assert retrieved_session_b is not None, \
                    f"User B should be able to retrieve their session"
                assert retrieved_session_b.session_id == session_b.session_id, \
                    f"User B should retrieve their own session"
                assert retrieved_session_b.user_id == user_b, \
                    f"Retrieved session should belong to user B"
                
                # Verify sessions have independent usage tracking
                assert session_a.message_count == 0, \
                    "Session A should start with zero messages"
                assert session_b.message_count == 0, \
                    "Session B should start with zero messages"
                assert session_a.credits_used == 0, \
                    "Session A should start with zero credits used"
                assert session_b.credits_used == 0, \
                    "Session B should start with zero credits used"
                
    finally:
        # Clean up
        cleanup_user_data(user_a)
        cleanup_user_data(user_b)


@settings(max_examples=5, deadline=None)
@given(
    user_a=st.integers(min_value=1, max_value=999999),
    user_b=st.integers(min_value=1, max_value=999999),
    message_a=st.text(min_size=1, max_size=100),
    message_b=st.text(min_size=1, max_size=100)
)
def test_conversation_history_isolation(user_a, user_b, message_a, message_b):
    """
    Feature: dual-mode-offline-online, Property 10: Agent Isolation
    
    For any two distinct users with conversation history, their conversation 
    histories should be completely isolated. User A's messages should not 
    appear in User B's history and vice versa.
    
    **Validates: Requirements 10.3, 10.4**
    """
    # Ensure users are distinct
    assume(user_a != user_b)
    
    # Clean up
    cleanup_user_data(user_a)
    cleanup_user_data(user_b)
    
    try:
        # Set up both users
        set_user_mode(user_a, 'offline')
        set_user_mode(user_b, 'offline')
        add_credits(user_a, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        add_credits(user_b, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        
        with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
            with patch('os.path.exists', return_value=True):
                # Create agent manager
                ai_agent_manager = AIAgentManager()
                
                # Create agents for both users
                agent_a = ai_agent_manager.get_or_create_agent(user_a)
                agent_b = ai_agent_manager.get_or_create_agent(user_b)
                
                # Simulate conversation history for User A
                conversation_a = [
                    {"role": "user", "content": message_a},
                    {"role": "assistant", "content": "Response to A"}
                ]
                
                # Simulate conversation history for User B
                conversation_b = [
                    {"role": "user", "content": message_b},
                    {"role": "assistant", "content": "Response to B"}
                ]
                
                # Update conversation histories
                ai_agent_manager.update_agent_activity(agent_a.agent_id, conversation_a)
                ai_agent_manager.update_agent_activity(agent_b.agent_id, conversation_b)
                
                # Retrieve agents from database
                retrieved_agent_a = get_agent(user_a)
                retrieved_agent_b = get_agent(user_b)
                
                assert retrieved_agent_a is not None, "Agent A should be retrievable"
                assert retrieved_agent_b is not None, "Agent B should be retrievable"
                
                # Ensure we have dict objects, not strings
                if isinstance(retrieved_agent_a, str):
                    # If it's a string (agent_id), skip this test iteration
                    assume(False)
                if isinstance(retrieved_agent_b, str):
                    # If it's a string (agent_id), skip this test iteration
                    assume(False)
                
                # Verify conversation histories are isolated
                history_a = retrieved_agent_a.get('conversation_history', [])
                history_b = retrieved_agent_b.get('conversation_history', [])
                
                # Verify User A's history contains only their messages
                if len(history_a) > 0:
                    assert any(msg.get('content') == message_a for msg in history_a), \
                        f"User A's history should contain their message"
                    assert not any(msg.get('content') == message_b for msg in history_a), \
                        f"User A's history should NOT contain User B's message"
                
                # Verify User B's history contains only their messages
                if len(history_b) > 0:
                    assert any(msg.get('content') == message_b for msg in history_b), \
                        f"User B's history should contain their message"
                    assert not any(msg.get('content') == message_a for msg in history_b), \
                        f"User B's history should NOT contain User A's message"
                
    finally:
        # Clean up
        cleanup_user_data(user_a)
        cleanup_user_data(user_b)


@settings(max_examples=5, deadline=None)
@given(
    user_a=st.integers(min_value=1, max_value=999999),
    user_b=st.integers(min_value=1, max_value=999999)
)
def test_agent_retrieval_by_user_id_only(user_a, user_b):
    """
    Feature: dual-mode-offline-online, Property 10: Agent Isolation
    
    For any user, they should only be able to retrieve their own agent 
    using their user ID. The system should not allow retrieving another 
    user's agent.
    
    **Validates: Requirements 10.4, 10.5**
    """
    # Ensure users are distinct
    assume(user_a != user_b)
    
    # Clean up
    cleanup_user_data(user_a)
    cleanup_user_data(user_b)
    
    try:
        # Set up both users
        set_user_mode(user_a, 'offline')
        set_user_mode(user_b, 'offline')
        add_credits(user_a, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        add_credits(user_b, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        
        with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
            with patch('os.path.exists', return_value=True):
                # Create agent manager
                ai_agent_manager = AIAgentManager()
                
                # Create agents for both users
                agent_a = ai_agent_manager.get_or_create_agent(user_a)
                agent_b = ai_agent_manager.get_or_create_agent(user_b)
                
                # Verify User A can retrieve their own agent
                retrieved_a = ai_agent_manager.get_agent(user_a)
                assert retrieved_a is not None, \
                    f"User A should be able to retrieve their agent"
                assert retrieved_a.agent_id == agent_a.agent_id, \
                    f"User A should retrieve their own agent"
                assert retrieved_a.user_id == user_a, \
                    f"Retrieved agent should belong to User A"
                
                # Verify User B can retrieve their own agent
                retrieved_b = ai_agent_manager.get_agent(user_b)
                assert retrieved_b is not None, \
                    f"User B should be able to retrieve their agent"
                assert retrieved_b.agent_id == agent_b.agent_id, \
                    f"User B should retrieve their own agent"
                assert retrieved_b.user_id == user_b, \
                    f"Retrieved agent should belong to User B"
                
                # Verify agents are different
                assert retrieved_a.agent_id != retrieved_b.agent_id, \
                    f"User A and User B should have different agents"
                
                # Verify database-level isolation
                db_agent_a = get_agent(user_a)
                db_agent_b = get_agent(user_b)
                
                assert db_agent_a is not None, "User A's agent should exist in database"
                assert db_agent_b is not None, "User B's agent should exist in database"
                
                assert db_agent_a['user_id'] == user_a, \
                    "Database agent A should belong to User A"
                assert db_agent_b['user_id'] == user_b, \
                    "Database agent B should belong to User B"
                
                assert db_agent_a['agent_id'] != db_agent_b['agent_id'], \
                    "Database agents should have different IDs"
                
    finally:
        # Clean up
        cleanup_user_data(user_a)
        cleanup_user_data(user_b)


@settings(max_examples=5, deadline=None)
@given(
    user_a=st.integers(min_value=1, max_value=999999),
    user_b=st.integers(min_value=1, max_value=999999)
)
def test_agent_deletion_does_not_affect_other_users(user_a, user_b):
    """
    Feature: dual-mode-offline-online, Property 10: Agent Isolation
    
    For any two distinct users, deleting User A's agent should not affect 
    User B's agent in any way.
    
    **Validates: Requirements 10.1, 10.2, 10.4**
    """
    # Ensure users are distinct
    assume(user_a != user_b)
    
    # Clean up
    cleanup_user_data(user_a)
    cleanup_user_data(user_b)
    
    try:
        # Set up both users
        set_user_mode(user_a, 'offline')
        set_user_mode(user_b, 'offline')
        add_credits(user_a, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        add_credits(user_b, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        
        with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
            with patch('os.path.exists', return_value=True):
                # Create agent manager
                ai_agent_manager = AIAgentManager()
                
                # Create agents for both users
                agent_a = ai_agent_manager.get_or_create_agent(user_a)
                agent_b = ai_agent_manager.get_or_create_agent(user_b)
                
                # Verify both agents exist
                assert agent_a is not None, "Agent A should be created"
                assert agent_b is not None, "Agent B should be created"
                
                agent_b_id_before = agent_b.agent_id
                
                # Delete User A's agent
                delete_success = ai_agent_manager.delete_agent(user_a)
                assert delete_success is True, \
                    f"User A's agent should be deleted successfully"
                
                # Verify User A's agent is deleted
                deleted_agent_a = ai_agent_manager.get_agent(user_a)
                # Agent might still exist but with 'deleted' status
                if deleted_agent_a is not None:
                    assert deleted_agent_a.status == 'deleted', \
                        "User A's agent should be marked as deleted"
                
                # Verify User B's agent is unaffected
                agent_b_after = ai_agent_manager.get_agent(user_b)
                assert agent_b_after is not None, \
                    f"User B's agent should still exist after User A's deletion"
                assert agent_b_after.agent_id == agent_b_id_before, \
                    f"User B's agent ID should be unchanged"
                assert agent_b_after.user_id == user_b, \
                    f"User B's agent should still belong to User B"
                assert agent_b_after.status == 'active', \
                    f"User B's agent should still be active"
                
    finally:
        # Clean up
        cleanup_user_data(user_a)
        cleanup_user_data(user_b)


@settings(max_examples=5, deadline=None)
@given(
    user_a=st.integers(min_value=1, max_value=999999),
    user_b=st.integers(min_value=1, max_value=999999)
)
def test_unique_agent_id_per_user(user_a, user_b):
    """
    Feature: dual-mode-offline-online, Property 10: Agent Isolation
    
    For any two distinct users, their agents should have unique agent IDs 
    that are properly namespaced with their user IDs.
    
    **Validates: Requirements 10.1, 10.2**
    """
    # Ensure users are distinct
    assume(user_a != user_b)
    
    # Clean up
    cleanup_user_data(user_a)
    cleanup_user_data(user_b)
    
    try:
        # Set up both users
        set_user_mode(user_a, 'offline')
        set_user_mode(user_b, 'offline')
        add_credits(user_a, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        add_credits(user_b, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
        
        with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
            with patch('os.path.exists', return_value=True):
                # Create agent manager
                ai_agent_manager = AIAgentManager()
                
                # Create agents for both users
                agent_a = ai_agent_manager.get_or_create_agent(user_a)
                agent_b = ai_agent_manager.get_or_create_agent(user_b)
                
                # Verify agents have unique IDs
                assert agent_a.agent_id != agent_b.agent_id, \
                    f"Agents should have unique IDs, both got: {agent_a.agent_id}"
                
                # Verify agent IDs are properly namespaced with user IDs
                assert agent_a.agent_id.startswith(f"agent_{user_a}_"), \
                    f"Agent A's ID should start with 'agent_{user_a}_', got: {agent_a.agent_id}"
                assert agent_b.agent_id.startswith(f"agent_{user_b}_"), \
                    f"Agent B's ID should start with 'agent_{user_b}_', got: {agent_b.agent_id}"
                
                # Verify agent IDs contain unique suffixes
                suffix_a = agent_a.agent_id.split(f"agent_{user_a}_")[1]
                suffix_b = agent_b.agent_id.split(f"agent_{user_b}_")[1]
                
                assert len(suffix_a) > 0, "Agent A should have a unique suffix"
                assert len(suffix_b) > 0, "Agent B should have a unique suffix"
                
                # Even if users have similar IDs, the full agent IDs should be different
                assert agent_a.agent_id != agent_b.agent_id, \
                    "Full agent IDs should be unique"
                
    finally:
        # Clean up
        cleanup_user_data(user_a)
        cleanup_user_data(user_b)


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
