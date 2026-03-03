"""
Unit tests for AIAgentManager.

Tests the AI agent management functionality including:
- Agent creation with Genesis Prompt injection
- Agent retrieval with lazy initialization
- Agent isolation validation
- Agent deletion

Feature: dual-mode-offline-online
Task: 7.1 Create AIAgentManager class
Requirements: 3.2, 10.1, 10.2, 10.5, 11.2
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
import uuid

from app.dual_mode.ai_agent_manager import AIAgentManager, Agent


# Mock Genesis Prompt content
MOCK_GENESIS_PROMPT = """
# AUTOMATON GENESIS PROMPT
## System Architecture & Rules

This is a test Genesis Prompt for autonomous trading agents.
"""


@pytest.fixture
def mock_genesis_prompt_loader():
    """Mock GenesisPromptLoader."""
    loader = Mock()
    loader.get_current_prompt.return_value = MOCK_GENESIS_PROMPT
    return loader


@pytest.fixture
def ai_agent_manager(mock_genesis_prompt_loader):
    """Create AIAgentManager instance with mock loader."""
    return AIAgentManager(genesis_prompt_loader=mock_genesis_prompt_loader)


@pytest.fixture
def ai_agent_manager_no_loader():
    """Create AIAgentManager instance without loader (will load from file)."""
    return AIAgentManager()


class TestAIAgentManagerInitialization:
    """Test AIAgentManager initialization."""
    
    def test_init_with_loader(self, mock_genesis_prompt_loader):
        """Test initialization with GenesisPromptLoader."""
        manager = AIAgentManager(genesis_prompt_loader=mock_genesis_prompt_loader)
        assert manager.genesis_prompt_loader == mock_genesis_prompt_loader
    
    def test_init_without_loader(self):
        """Test initialization without GenesisPromptLoader."""
        manager = AIAgentManager()
        assert manager.genesis_prompt_loader is None


class TestInitializeAgent:
    """Test agent initialization with Genesis Prompt injection."""
    
    @patch('app.dual_mode.ai_agent_manager.db_create_agent')
    def test_initialize_agent_success(self, mock_db_create, ai_agent_manager):
        """Test successful agent initialization."""
        # Arrange
        user_id = 12345
        mock_db_create.return_value = True
        
        # Act
        agent = ai_agent_manager.initialize_agent(user_id, MOCK_GENESIS_PROMPT)
        
        # Assert
        assert agent is not None
        assert agent.user_id == user_id
        assert agent.genesis_prompt == MOCK_GENESIS_PROMPT
        assert agent.agent_id.startswith(f"agent_{user_id}_")
        assert agent.status == 'active'
        assert agent.total_messages == 0
        assert len(agent.conversation_history) == 0
        
        # Verify database call
        mock_db_create.assert_called_once()
        call_args = mock_db_create.call_args[0]
        assert call_args[0] == user_id
        assert call_args[1].startswith(f"agent_{user_id}_")
        assert call_args[2] == MOCK_GENESIS_PROMPT
    
    @patch('app.dual_mode.ai_agent_manager.db_create_agent')
    def test_initialize_agent_database_failure(self, mock_db_create, ai_agent_manager):
        """Test agent initialization when database creation fails."""
        # Arrange
        user_id = 12345
        mock_db_create.return_value = False
        
        # Act
        agent = ai_agent_manager.initialize_agent(user_id, MOCK_GENESIS_PROMPT)
        
        # Assert
        assert agent is None
        mock_db_create.assert_called_once()
    
    @patch('app.dual_mode.ai_agent_manager.db_create_agent')
    def test_initialize_agent_exception(self, mock_db_create, ai_agent_manager):
        """Test agent initialization when exception occurs."""
        # Arrange
        user_id = 12345
        mock_db_create.side_effect = Exception("Database error")
        
        # Act
        agent = ai_agent_manager.initialize_agent(user_id, MOCK_GENESIS_PROMPT)
        
        # Assert
        assert agent is None


class TestGetAgent:
    """Test agent retrieval."""
    
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_get_agent_success(self, mock_db_get, ai_agent_manager):
        """Test successful agent retrieval."""
        # Arrange
        user_id = 12345
        agent_id = f"agent_{user_id}_abc123"
        mock_db_get.return_value = {
            'agent_id': agent_id,
            'user_id': user_id,
            'genesis_prompt': MOCK_GENESIS_PROMPT,
            'conversation_history': [],
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_used': '2024-01-15T10:00:00+00:00',
            'total_messages': 0,
            'status': 'active'
        }
        
        # Act
        agent = ai_agent_manager.get_agent(user_id)
        
        # Assert
        assert agent is not None
        assert agent.agent_id == agent_id
        assert agent.user_id == user_id
        assert agent.genesis_prompt == MOCK_GENESIS_PROMPT
        assert agent.status == 'active'
        mock_db_get.assert_called_once_with(user_id)
    
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_get_agent_not_found(self, mock_db_get, ai_agent_manager):
        """Test agent retrieval when agent doesn't exist."""
        # Arrange
        user_id = 12345
        mock_db_get.return_value = None
        
        # Act
        agent = ai_agent_manager.get_agent(user_id)
        
        # Assert
        assert agent is None
        mock_db_get.assert_called_once_with(user_id)
    
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_get_agent_exception(self, mock_db_get, ai_agent_manager):
        """Test agent retrieval when exception occurs."""
        # Arrange
        user_id = 12345
        mock_db_get.side_effect = Exception("Database error")
        
        # Act
        agent = ai_agent_manager.get_agent(user_id)
        
        # Assert
        assert agent is None


class TestGetOrCreateAgent:
    """Test lazy agent initialization."""
    
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_get_or_create_returns_existing(self, mock_db_get, ai_agent_manager):
        """Test get_or_create returns existing agent."""
        # Arrange
        user_id = 12345
        agent_id = f"agent_{user_id}_abc123"
        mock_db_get.return_value = {
            'agent_id': agent_id,
            'user_id': user_id,
            'genesis_prompt': MOCK_GENESIS_PROMPT,
            'conversation_history': [],
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_used': '2024-01-15T10:00:00+00:00',
            'total_messages': 5,
            'status': 'active'
        }
        
        # Act
        agent = ai_agent_manager.get_or_create_agent(user_id)
        
        # Assert
        assert agent is not None
        assert agent.agent_id == agent_id
        assert agent.total_messages == 5
        mock_db_get.assert_called_once_with(user_id)
    
    @patch('app.dual_mode.ai_agent_manager.db_create_agent')
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_get_or_create_creates_new(self, mock_db_get, mock_db_create, ai_agent_manager):
        """Test get_or_create creates new agent when none exists."""
        # Arrange
        user_id = 12345
        mock_db_get.return_value = None
        mock_db_create.return_value = True
        
        # Act
        agent = ai_agent_manager.get_or_create_agent(user_id)
        
        # Assert
        assert agent is not None
        assert agent.user_id == user_id
        assert agent.genesis_prompt == MOCK_GENESIS_PROMPT
        assert agent.total_messages == 0
        mock_db_get.assert_called_once_with(user_id)
        mock_db_create.assert_called_once()
    
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_get_or_create_fails_to_load_prompt(self, mock_db_get, ai_agent_manager_no_loader):
        """Test get_or_create fails when Genesis Prompt can't be loaded."""
        # Arrange
        user_id = 12345
        mock_db_get.return_value = None
        
        with patch('builtins.open', side_effect=FileNotFoundError):
            # Act
            agent = ai_agent_manager_no_loader.get_or_create_agent(user_id)
            
            # Assert
            assert agent is None


class TestIsAgentIsolated:
    """Test agent isolation validation (security)."""
    
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_is_agent_isolated_valid(self, mock_db_get, ai_agent_manager):
        """Test isolation validation for valid agent."""
        # Arrange
        user_id = 12345
        agent_id = f"agent_{user_id}_abc123"
        mock_db_get.return_value = {
            'agent_id': agent_id,
            'user_id': user_id,
            'genesis_prompt': MOCK_GENESIS_PROMPT,
            'conversation_history': [],
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_used': '2024-01-15T10:00:00+00:00',
            'total_messages': 0,
            'status': 'active'
        }
        
        # Act
        is_isolated = ai_agent_manager.is_agent_isolated(agent_id, user_id)
        
        # Assert
        assert is_isolated is True
        mock_db_get.assert_called_once_with(user_id)
    
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_is_agent_isolated_no_agent(self, mock_db_get, ai_agent_manager):
        """Test isolation validation when agent doesn't exist."""
        # Arrange
        user_id = 12345
        agent_id = "agent_12345_abc123"
        mock_db_get.return_value = None
        
        # Act
        is_isolated = ai_agent_manager.is_agent_isolated(agent_id, user_id)
        
        # Assert
        assert is_isolated is False
    
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_is_agent_isolated_wrong_agent_id(self, mock_db_get, ai_agent_manager):
        """Test isolation validation with wrong agent ID."""
        # Arrange
        user_id = 12345
        correct_agent_id = f"agent_{user_id}_abc123"
        wrong_agent_id = f"agent_{user_id}_xyz789"
        mock_db_get.return_value = {
            'agent_id': correct_agent_id,
            'user_id': user_id,
            'genesis_prompt': MOCK_GENESIS_PROMPT,
            'conversation_history': [],
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_used': '2024-01-15T10:00:00+00:00',
            'total_messages': 0,
            'status': 'active'
        }
        
        # Act
        is_isolated = ai_agent_manager.is_agent_isolated(wrong_agent_id, user_id)
        
        # Assert
        assert is_isolated is False
    
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_is_agent_isolated_inactive_agent(self, mock_db_get, ai_agent_manager):
        """Test isolation validation with inactive agent."""
        # Arrange
        user_id = 12345
        agent_id = f"agent_{user_id}_abc123"
        mock_db_get.return_value = {
            'agent_id': agent_id,
            'user_id': user_id,
            'genesis_prompt': MOCK_GENESIS_PROMPT,
            'conversation_history': [],
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_used': '2024-01-15T10:00:00+00:00',
            'total_messages': 0,
            'status': 'deleted'
        }
        
        # Act
        is_isolated = ai_agent_manager.is_agent_isolated(agent_id, user_id)
        
        # Assert
        assert is_isolated is False


class TestDeleteAgent:
    """Test agent deletion."""
    
    @patch('app.dual_mode.ai_agent_manager.db_delete_agent')
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_delete_agent_success(self, mock_db_get, mock_db_delete, ai_agent_manager):
        """Test successful agent deletion."""
        # Arrange
        user_id = 12345
        agent_id = f"agent_{user_id}_abc123"
        mock_db_get.return_value = {
            'agent_id': agent_id,
            'user_id': user_id,
            'genesis_prompt': MOCK_GENESIS_PROMPT,
            'conversation_history': [],
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_used': '2024-01-15T10:00:00+00:00',
            'total_messages': 0,
            'status': 'active'
        }
        mock_db_delete.return_value = True
        
        # Act
        result = ai_agent_manager.delete_agent(user_id)
        
        # Assert
        assert result is True
        mock_db_get.assert_called_once_with(user_id)
        mock_db_delete.assert_called_once_with(user_id)
    
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_delete_agent_not_found(self, mock_db_get, ai_agent_manager):
        """Test agent deletion when agent doesn't exist."""
        # Arrange
        user_id = 12345
        mock_db_get.return_value = None
        
        # Act
        result = ai_agent_manager.delete_agent(user_id)
        
        # Assert
        assert result is False
        mock_db_get.assert_called_once_with(user_id)
    
    @patch('app.dual_mode.ai_agent_manager.db_delete_agent')
    @patch('app.dual_mode.ai_agent_manager.db_get_agent')
    def test_delete_agent_database_failure(self, mock_db_get, mock_db_delete, ai_agent_manager):
        """Test agent deletion when database operation fails."""
        # Arrange
        user_id = 12345
        agent_id = f"agent_{user_id}_abc123"
        mock_db_get.return_value = {
            'agent_id': agent_id,
            'user_id': user_id,
            'genesis_prompt': MOCK_GENESIS_PROMPT,
            'conversation_history': [],
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_used': '2024-01-15T10:00:00+00:00',
            'total_messages': 0,
            'status': 'active'
        }
        mock_db_delete.return_value = False
        
        # Act
        result = ai_agent_manager.delete_agent(user_id)
        
        # Assert
        assert result is False


class TestUpdateAgentActivity:
    """Test agent activity updates."""
    
    @patch('app.dual_mode.ai_agent_manager.db_update_agent_activity')
    def test_update_agent_activity_success(self, mock_db_update, ai_agent_manager):
        """Test successful activity update."""
        # Arrange
        agent_id = "agent_12345_abc123"
        conversation_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        mock_db_update.return_value = True
        
        # Act
        result = ai_agent_manager.update_agent_activity(agent_id, conversation_history)
        
        # Assert
        assert result is True
        mock_db_update.assert_called_once_with(agent_id, conversation_history)
    
    @patch('app.dual_mode.ai_agent_manager.db_update_agent_activity')
    def test_update_agent_activity_without_history(self, mock_db_update, ai_agent_manager):
        """Test activity update without conversation history."""
        # Arrange
        agent_id = "agent_12345_abc123"
        mock_db_update.return_value = True
        
        # Act
        result = ai_agent_manager.update_agent_activity(agent_id)
        
        # Assert
        assert result is True
        mock_db_update.assert_called_once_with(agent_id, None)
    
    @patch('app.dual_mode.ai_agent_manager.db_update_agent_activity')
    def test_update_agent_activity_failure(self, mock_db_update, ai_agent_manager):
        """Test activity update when database operation fails."""
        # Arrange
        agent_id = "agent_12345_abc123"
        mock_db_update.return_value = False
        
        # Act
        result = ai_agent_manager.update_agent_activity(agent_id)
        
        # Assert
        assert result is False


class TestLoadGenesisPrompt:
    """Test Genesis Prompt loading."""
    
    def test_load_genesis_prompt_from_loader(self, ai_agent_manager, mock_genesis_prompt_loader):
        """Test loading Genesis Prompt from loader."""
        # Act
        prompt = ai_agent_manager._load_genesis_prompt()
        
        # Assert
        assert prompt == MOCK_GENESIS_PROMPT
        mock_genesis_prompt_loader.get_current_prompt.assert_called_once()
    
    def test_load_genesis_prompt_from_file(self, ai_agent_manager_no_loader):
        """Test loading Genesis Prompt from file."""
        # Arrange
        mock_file_content = MOCK_GENESIS_PROMPT
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch('os.path.exists', return_value=True):
                # Act
                prompt = ai_agent_manager_no_loader._load_genesis_prompt()
                
                # Assert
                assert prompt == MOCK_GENESIS_PROMPT
    
    def test_load_genesis_prompt_file_not_found(self, ai_agent_manager_no_loader):
        """Test loading Genesis Prompt when file doesn't exist."""
        # Arrange
        with patch('os.path.exists', return_value=False):
            # Act
            prompt = ai_agent_manager_no_loader._load_genesis_prompt()
            
            # Assert
            assert prompt is None
    
    def test_load_genesis_prompt_exception(self, ai_agent_manager_no_loader):
        """Test loading Genesis Prompt when exception occurs."""
        # Arrange
        with patch('builtins.open', side_effect=Exception("File read error")):
            with patch('os.path.exists', return_value=True):
                # Act
                prompt = ai_agent_manager_no_loader._load_genesis_prompt()
                
                # Assert
                assert prompt is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
