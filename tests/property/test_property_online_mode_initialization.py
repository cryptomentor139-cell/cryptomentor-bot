"""
Property-based test for online mode initialization.

Feature: dual-mode-offline-online
Property 3: Online Mode Initialization
Validates: Requirements 3.1, 3.2

For any user activating online mode for the first time, the system should 
create a new isolated session and initialize their personal AI agent with 
the Genesis Prompt.
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
@given(user_id=st.integers(min_value=1, max_value=999999))
def test_online_mode_creates_isolated_agent_and_session(user_id):
    """
    Feature: dual-mode-offline-online, Property 3: Online Mode Initialization
    
    For any user activating online mode for the first time, the system should 
    create a new isolated session and initialize their personal AI agent with 
    the Genesis Prompt.
    
    **Validates: Requirements 3.1, 3.2**
    """
    # Clean up any existing state for this user
    cleanup_user_data(user_id)
    
    # Set user to offline mode initially
    set_user_mode(user_id, 'offline')
    assert get_user_mode(user_id) == 'offline', "Failed to set initial offline mode"
    
    # Give user sufficient credits for online mode
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
    actual_credits = get_user_credits(user_id)
    assert actual_credits >= MINIMUM_CREDITS_REQUIRED, \
        f"Credits not set correctly: expected >= {MINIMUM_CREDITS_REQUIRED}, got {actual_credits}"
    
    # Verify user has no existing agent
    existing_agent = get_agent(user_id)
    assert existing_agent is None, \
        f"User should not have an existing agent before first online mode activation"
    
    # Verify user has no active session
    existing_session = get_active_session(user_id)
    assert existing_session is None, \
        f"User should not have an active session before online mode activation"
    
    # Mock the Genesis Prompt file loading
    with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
        with patch('os.path.exists', return_value=True):
            # Create AI agent manager and session manager
            ai_agent_manager = AIAgentManager()
            session_manager = SessionManager()
            
            # Activate online mode by creating agent and session
            # This simulates what OnlineModeHandler.activate_online_mode() does
            
            # Step 1: Create or get AI agent (Requirement 3.2)
            agent = ai_agent_manager.get_or_create_agent(user_id)
            
            # Verify agent was created
            assert agent is not None, \
                "Agent should be created for first-time online mode activation"
            
            # Verify agent belongs to user
            assert agent.user_id == user_id, \
                f"Agent user_id should be {user_id}, got {agent.user_id}"
            
            # Verify agent has Genesis Prompt (Requirement 3.2)
            assert agent.genesis_prompt is not None, \
                "Agent should have Genesis Prompt"
            assert len(agent.genesis_prompt) > 0, \
                "Genesis Prompt should not be empty"
            assert "AUTOMATON GENESIS PROMPT" in agent.genesis_prompt, \
                "Genesis Prompt should contain expected content"
            
            # Verify agent is active
            assert agent.status == 'active', \
                f"Agent status should be 'active', got '{agent.status}'"
            
            # Verify agent has unique ID
            assert agent.agent_id is not None, \
                "Agent should have a unique agent_id"
            assert agent.agent_id.startswith(f"agent_{user_id}_"), \
                f"Agent ID should start with 'agent_{user_id}_', got '{agent.agent_id}'"
            
            # Verify agent starts with empty conversation history
            assert agent.conversation_history == [], \
                "Agent should start with empty conversation history"
            assert agent.total_messages == 0, \
                "Agent should start with zero messages"
            
            # Step 2: Create session (Requirement 3.1)
            session = session_manager.create_session(user_id, agent.agent_id)
            
            # Verify session was created
            assert session is not None, \
                "Session should be created for online mode activation"
            
            # Verify session belongs to user
            assert session.user_id == user_id, \
                f"Session user_id should be {user_id}, got {session.user_id}"
            
            # Verify session is linked to agent
            assert session.agent_id == agent.agent_id, \
                f"Session should be linked to agent {agent.agent_id}, got {session.agent_id}"
            
            # Verify session is active
            assert session.status == 'active', \
                f"Session status should be 'active', got '{session.status}'"
            
            # Verify session has unique ID
            assert session.session_id is not None, \
                "Session should have a unique session_id"
            
            # Verify session starts with zero usage
            assert session.message_count == 0, \
                "Session should start with zero messages"
            assert session.credits_used == 0, \
                "Session should start with zero credits used"
            
            # Verify agent can be retrieved from database
            retrieved_agent = get_agent(user_id)
            assert retrieved_agent is not None, \
                "Agent should be retrievable from database"
            assert retrieved_agent['user_id'] == user_id, \
                "Retrieved agent should belong to correct user"
            assert retrieved_agent['agent_id'] == agent.agent_id, \
                "Retrieved agent should have correct agent_id"
            
            # Verify session can be retrieved from database
            retrieved_session = get_active_session(user_id)
            assert retrieved_session is not None, \
                "Session should be retrievable from database"
            assert retrieved_session['user_id'] == user_id, \
                "Retrieved session should belong to correct user"
            assert retrieved_session['session_id'] == session.session_id, \
                "Retrieved session should have correct session_id"
    
    # Clean up
    cleanup_user_data(user_id)


@settings(max_examples=5, deadline=None)
@given(user_id=st.integers(min_value=1, max_value=999999))
def test_agent_isolation_per_user(user_id):
    """
    Feature: dual-mode-offline-online, Property 3: Online Mode Initialization
    
    For any user activating online mode, their AI agent should be completely 
    isolated and unique to them.
    
    **Validates: Requirements 3.2, 10.1, 10.2**
    """
    # Clean up
    cleanup_user_data(user_id)
    
    # Set up user
    set_user_mode(user_id, 'offline')
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
    
    # Mock Genesis Prompt
    with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
        with patch('os.path.exists', return_value=True):
            # Create agent manager
            ai_agent_manager = AIAgentManager()
            
            # Create agent for user
            agent = ai_agent_manager.get_or_create_agent(user_id)
            assert agent is not None, "Agent should be created"
            
            # Verify agent isolation
            is_isolated = ai_agent_manager.is_agent_isolated(agent.agent_id, user_id)
            assert is_isolated is True, \
                f"Agent {agent.agent_id} should be isolated for user {user_id}"
            
            # Verify agent cannot be accessed by different user
            different_user_id = user_id + 1
            is_isolated_for_different_user = ai_agent_manager.is_agent_isolated(
                agent.agent_id, 
                different_user_id
            )
            assert is_isolated_for_different_user is False, \
                f"Agent {agent.agent_id} should NOT be accessible by user {different_user_id}"
    
    # Clean up
    cleanup_user_data(user_id)


@settings(max_examples=5, deadline=None)
@given(user_id=st.integers(min_value=1, max_value=999999))
def test_genesis_prompt_injection_on_initialization(user_id):
    """
    Feature: dual-mode-offline-online, Property 3: Online Mode Initialization
    
    For any user activating online mode for the first time, their AI agent 
    should be initialized with the Genesis Prompt as the base system prompt.
    
    **Validates: Requirements 3.2, 11.2**
    """
    # Clean up
    cleanup_user_data(user_id)
    
    # Set up user
    set_user_mode(user_id, 'offline')
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
    
    # Mock Genesis Prompt with specific content
    test_genesis_content = """
# AUTOMATON GENESIS PROMPT
## Trading Rules
1. Always analyze market conditions
2. Use risk management
3. Provide clear signals
"""
    
    with patch('builtins.open', mock_open(read_data=test_genesis_content)):
        with patch('os.path.exists', return_value=True):
            # Create agent manager
            ai_agent_manager = AIAgentManager()
            
            # Create agent
            agent = ai_agent_manager.get_or_create_agent(user_id)
            assert agent is not None, "Agent should be created"
            
            # Verify Genesis Prompt was injected
            assert agent.genesis_prompt == test_genesis_content, \
                "Agent should have Genesis Prompt injected"
            
            # Verify Genesis Prompt contains expected sections
            assert "AUTOMATON GENESIS PROMPT" in agent.genesis_prompt, \
                "Genesis Prompt should contain header"
            assert "Trading Rules" in agent.genesis_prompt, \
                "Genesis Prompt should contain trading rules"
            
            # Verify agent from database also has Genesis Prompt
            retrieved_agent = get_agent(user_id)
            assert retrieved_agent is not None, "Agent should be in database"
            assert retrieved_agent['genesis_prompt'] == test_genesis_content, \
                "Database agent should have Genesis Prompt"
    
    # Clean up
    cleanup_user_data(user_id)


@settings(max_examples=5, deadline=None)
@given(user_id=st.integers(min_value=1, max_value=999999))
def test_session_and_agent_properly_linked(user_id):
    """
    Feature: dual-mode-offline-online, Property 3: Online Mode Initialization
    
    For any user activating online mode, the session and agent should be 
    properly linked together.
    
    **Validates: Requirements 3.1, 3.2**
    """
    # Clean up
    cleanup_user_data(user_id)
    
    # Set up user
    set_user_mode(user_id, 'offline')
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
    
    with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
        with patch('os.path.exists', return_value=True):
            # Create managers
            ai_agent_manager = AIAgentManager()
            session_manager = SessionManager()
            
            # Create agent
            agent = ai_agent_manager.get_or_create_agent(user_id)
            assert agent is not None, "Agent should be created"
            
            # Create session linked to agent
            session = session_manager.create_session(user_id, agent.agent_id)
            assert session is not None, "Session should be created"
            
            # Verify linkage
            assert session.agent_id == agent.agent_id, \
                f"Session should be linked to agent {agent.agent_id}, got {session.agent_id}"
            
            assert session.user_id == agent.user_id, \
                f"Session and agent should belong to same user {user_id}"
            
            # Verify both are retrievable and linked
            retrieved_agent = get_agent(user_id)
            retrieved_session = get_active_session(user_id)
            
            assert retrieved_agent is not None, "Agent should be in database"
            assert retrieved_session is not None, "Session should be in database"
            
            assert retrieved_session['agent_id'] == retrieved_agent['agent_id'], \
                "Retrieved session should be linked to retrieved agent"
    
    # Clean up
    cleanup_user_data(user_id)


@settings(max_examples=5, deadline=None)
@given(user_id=st.integers(min_value=1, max_value=999999))
def test_subsequent_activation_reuses_existing_agent(user_id):
    """
    Feature: dual-mode-offline-online, Property 3: Online Mode Initialization
    
    For any user activating online mode a second time (after having an agent), 
    the system should reuse the existing agent rather than creating a new one.
    
    **Validates: Requirements 3.2, 10.1**
    """
    # Clean up
    cleanup_user_data(user_id)
    
    # Set up user
    set_user_mode(user_id, 'offline')
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
    
    with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
        with patch('os.path.exists', return_value=True):
            # Create agent manager
            ai_agent_manager = AIAgentManager()
            
            # First activation - create agent
            agent1 = ai_agent_manager.get_or_create_agent(user_id)
            assert agent1 is not None, "First agent should be created"
            first_agent_id = agent1.agent_id
            
            # Second activation - should reuse existing agent
            agent2 = ai_agent_manager.get_or_create_agent(user_id)
            assert agent2 is not None, "Second call should return agent"
            
            # Verify same agent is returned
            assert agent2.agent_id == first_agent_id, \
                f"Should reuse existing agent {first_agent_id}, got {agent2.agent_id}"
            
            assert agent2.user_id == user_id, \
                "Reused agent should belong to same user"
            
            # Verify only one agent exists in database
            retrieved_agent = get_agent(user_id)
            assert retrieved_agent is not None, "Agent should exist in database"
            assert retrieved_agent['agent_id'] == first_agent_id, \
                "Database should have only the first agent"
    
    # Clean up
    cleanup_user_data(user_id)


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    num_activations=st.integers(min_value=2, max_value=5)
)
def test_multiple_activations_maintain_agent_consistency(user_id, num_activations):
    """
    Feature: dual-mode-offline-online, Property 3: Online Mode Initialization
    
    For any user activating online mode multiple times, the same agent should 
    be consistently returned across all activations.
    
    **Validates: Requirements 3.2, 10.1, 10.2**
    """
    # Clean up
    cleanup_user_data(user_id)
    
    # Set up user
    set_user_mode(user_id, 'offline')
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
    
    with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
        with patch('os.path.exists', return_value=True):
            # Create agent manager
            ai_agent_manager = AIAgentManager()
            
            # Track agent IDs across activations
            agent_ids = []
            
            # Perform multiple activations
            for i in range(num_activations):
                agent = ai_agent_manager.get_or_create_agent(user_id)
                assert agent is not None, f"Agent should be returned on activation {i+1}"
                agent_ids.append(agent.agent_id)
            
            # Verify all activations returned the same agent
            unique_agent_ids = set(agent_ids)
            assert len(unique_agent_ids) == 1, \
                f"All activations should return same agent, got {len(unique_agent_ids)} different agents"
            
            # Verify the consistent agent ID
            consistent_agent_id = agent_ids[0]
            for i, agent_id in enumerate(agent_ids):
                assert agent_id == consistent_agent_id, \
                    f"Activation {i+1} returned different agent: expected {consistent_agent_id}, got {agent_id}"
    
    # Clean up
    cleanup_user_data(user_id)


@settings(max_examples=5, deadline=None)
@given(user_id=st.integers(min_value=1, max_value=999999))
def test_new_session_created_each_activation(user_id):
    """
    Feature: dual-mode-offline-online, Property 3: Online Mode Initialization
    
    For any user activating online mode, a new session should be created 
    each time (even if they have an existing agent).
    
    **Validates: Requirements 3.1**
    """
    # Clean up
    cleanup_user_data(user_id)
    
    # Set up user
    set_user_mode(user_id, 'offline')
    add_credits(user_id, MINIMUM_CREDITS_REQUIRED * 10, "Test setup")
    
    with patch('builtins.open', mock_open(read_data=MOCK_GENESIS_PROMPT)):
        with patch('os.path.exists', return_value=True):
            # Create managers
            ai_agent_manager = AIAgentManager()
            session_manager = SessionManager()
            
            # Create agent (will be reused)
            agent = ai_agent_manager.get_or_create_agent(user_id)
            assert agent is not None, "Agent should be created"
            
            # First session
            session1 = session_manager.create_session(user_id, agent.agent_id)
            assert session1 is not None, "First session should be created"
            session1_id = session1.session_id
            
            # Close first session
            session_manager.close_session(user_id)
            
            # Second session (new activation)
            session2 = session_manager.create_session(user_id, agent.agent_id)
            assert session2 is not None, "Second session should be created"
            session2_id = session2.session_id
            
            # Verify different sessions were created
            assert session2_id != session1_id, \
                f"New session should be created, got same session ID: {session1_id}"
            
            # Verify both sessions linked to same agent
            assert session1.agent_id == agent.agent_id, \
                "First session should be linked to agent"
            assert session2.agent_id == agent.agent_id, \
                "Second session should be linked to same agent"
    
    # Clean up
    cleanup_user_data(user_id)


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
