"""
Property Test: Genesis Prompt Injection

Feature: dual-mode-offline-online
Property 11: For any newly created AI agent, the system should inject the current 
Genesis Prompt as the system prompt, ensuring all agents have consistent base 
knowledge for trading operations.

Validates: Requirements 11.2, 11.5, 11.6
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from app.dual_mode.genesis_prompt_loader import GenesisPromptLoader, get_genesis_prompt_loader
from app.dual_mode.ai_agent_manager import AIAgentManager
import tempfile
import os


# Sample Genesis Prompt content for testing
SAMPLE_GENESIS_PROMPT = """
# Genesis Prompt for AI Trading Agent

You are an AI trading assistant specialized in cryptocurrency trading.

## Core Capabilities:
- Technical analysis
- Market sentiment analysis
- Risk management
- Trade signal generation

## Trading Rules:
1. Always consider risk management
2. Provide clear entry and exit points
3. Include stop-loss recommendations
4. Explain your reasoning

## Response Format:
- Be concise and actionable
- Use clear language
- Provide specific recommendations
"""


@pytest.fixture
def temp_genesis_prompt_file():
    """Create a temporary Genesis Prompt file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(SAMPLE_GENESIS_PROMPT)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def genesis_loader(temp_genesis_prompt_file):
    """Create a Genesis Prompt Loader with a temporary file."""
    return GenesisPromptLoader(prompt_file_path=temp_genesis_prompt_file)


@given(user_id=st.integers(min_value=1, max_value=999999))
@settings(max_examples=10, deadline=None)
def test_genesis_prompt_injection_on_agent_creation(user_id):
    """
    Property 11: Genesis Prompt Injection
    
    For any newly created AI agent, the system should inject the current 
    Genesis Prompt as the system prompt.
    """
    # Create temporary Genesis Prompt file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(SAMPLE_GENESIS_PROMPT)
        temp_path = f.name
    
    try:
        # Create loader and load the Genesis Prompt
        genesis_loader = GenesisPromptLoader(prompt_file_path=temp_path)
        genesis_prompt = genesis_loader.get_current_prompt()
        
        # Verify prompt was loaded
        assert genesis_prompt is not None
        assert len(genesis_prompt) > 0
        assert "Genesis Prompt" in genesis_prompt
        
        # Create AI agent manager
        manager = AIAgentManager()
        
        # Delete existing agent if any
        manager.delete_agent(user_id)
        
        # Initialize a new agent with the Genesis Prompt
        agent = manager.initialize_agent(user_id, genesis_prompt)
        
        # Verify the agent was created with the Genesis Prompt
        assert agent is not None
        assert agent.user_id == user_id
        assert agent.genesis_prompt == genesis_prompt
        assert "Genesis Prompt" in agent.genesis_prompt
        
        # Verify the prompt contains expected sections
        assert "Core Capabilities" in agent.genesis_prompt
        assert "Trading Rules" in agent.genesis_prompt
        assert "Response Format" in agent.genesis_prompt
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@given(
    user_id=st.integers(min_value=1, max_value=999999),
    num_agents=st.integers(min_value=2, max_value=5)
)
@settings(max_examples=10, deadline=None)
def test_all_agents_receive_same_genesis_prompt(user_id, num_agents):
    """
    Property 11: Consistent Genesis Prompt Across Agents
    
    For any set of newly created AI agents, all should receive the same 
    Genesis Prompt version.
    """
    # Create temporary Genesis Prompt file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(SAMPLE_GENESIS_PROMPT)
        temp_path = f.name
    
    try:
        # Create loader and load the Genesis Prompt
        genesis_loader = GenesisPromptLoader(prompt_file_path=temp_path)
        genesis_prompt = genesis_loader.get_current_prompt()
        prompt_version = genesis_loader.get_prompt_version()
        
        # Create multiple agents
        manager = AIAgentManager()
        agents = []
        
        for i in range(num_agents):
            agent_user_id = user_id + i
            # Delete existing agent if any
            manager.delete_agent(agent_user_id)
            agent = manager.initialize_agent(agent_user_id, genesis_prompt)
            agents.append(agent)
        
        # Verify all agents have the same Genesis Prompt
        for agent in agents:
            assert agent is not None
            assert agent.genesis_prompt == genesis_prompt
            # All agents should have the same prompt version
            assert genesis_loader._generate_version_hash(agent.genesis_prompt) == prompt_version
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@given(user_id=st.integers(min_value=1, max_value=999999))
@settings(max_examples=10, deadline=None)
def test_genesis_prompt_reload_affects_new_agents(user_id):
    """
    Property 11: Genesis Prompt Reload
    
    When the Genesis Prompt is reloaded, new agents should receive the 
    updated prompt while existing agents retain their original prompt.
    """
    # Create temporary Genesis Prompt file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(SAMPLE_GENESIS_PROMPT)
        temp_path = f.name
    
    try:
        # Create loader and load initial prompt
        loader = GenesisPromptLoader(prompt_file_path=temp_path)
        initial_prompt = loader.get_current_prompt()
        initial_version = loader.get_prompt_version()
        
        # Create first agent with initial prompt
        manager = AIAgentManager()
        # Delete existing agents if any
        manager.delete_agent(user_id)
        manager.delete_agent(user_id + 1)
        
        agent1 = manager.initialize_agent(user_id, initial_prompt)
        
        # Modify the Genesis Prompt file
        updated_prompt = SAMPLE_GENESIS_PROMPT + "\n\n## Updated Section\n- New feature added"
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(updated_prompt)
        
        # Reload the prompt
        reloaded_prompt = loader.reload_prompt()
        reloaded_version = loader.get_prompt_version()
        
        # Verify the prompt was updated
        assert reloaded_prompt != initial_prompt
        assert reloaded_version != initial_version
        assert "Updated Section" in reloaded_prompt
        
        # Create second agent with reloaded prompt
        agent2 = manager.initialize_agent(user_id + 1, reloaded_prompt)
        
        # Verify agent1 still has initial prompt (immutable)
        assert agent1 is not None
        assert agent1.genesis_prompt == initial_prompt
        assert "Updated Section" not in agent1.genesis_prompt
        
        # Verify agent2 has updated prompt
        assert agent2 is not None
        assert agent2.genesis_prompt == reloaded_prompt
        assert "Updated Section" in agent2.genesis_prompt
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_genesis_prompt_caching(genesis_loader):
    """
    Test that Genesis Prompt is cached in memory for performance.
    """
    # First load
    prompt1 = genesis_loader.load_prompt()
    load_time1 = genesis_loader.get_last_loaded_time()
    
    # Second call should use cache
    prompt2 = genesis_loader.get_current_prompt()
    load_time2 = genesis_loader.get_last_loaded_time()
    
    # Verify same prompt returned
    assert prompt1 == prompt2
    
    # Verify load time didn't change (cache was used)
    assert load_time1 == load_time2
    
    # Verify loader reports as loaded
    assert genesis_loader.is_loaded()


def test_genesis_prompt_version_tracking(genesis_loader):
    """
    Test that Genesis Prompt version is tracked correctly.
    """
    # Load prompt
    prompt = genesis_loader.load_prompt()
    version = genesis_loader.get_prompt_version()
    
    # Verify version is generated
    assert version is not None
    assert len(version) == 8  # First 8 characters of SHA256
    
    # Verify version is consistent
    version2 = genesis_loader.get_prompt_version()
    assert version == version2


def test_genesis_prompt_file_not_found():
    """
    Test error handling when Genesis Prompt file doesn't exist.
    """
    loader = GenesisPromptLoader(prompt_file_path="nonexistent_file.md")
    
    with pytest.raises(FileNotFoundError):
        loader.load_prompt()


def test_genesis_prompt_singleton():
    """
    Test that get_genesis_prompt_loader returns a singleton instance.
    """
    loader1 = get_genesis_prompt_loader()
    loader2 = get_genesis_prompt_loader()
    
    # Verify same instance
    assert loader1 is loader2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
