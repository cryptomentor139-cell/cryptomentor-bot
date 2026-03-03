"""
Unit tests for ModeStateManager class.

Feature: dual-mode-offline-online
Task: 2.1
Requirements: 1.1, 1.2, 1.7, 1.8
"""

import pytest
import sys
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
from uuid import uuid4

# Mock the database module before importing ModeStateManager
sys.modules['app.dual_mode_db'] = MagicMock()

# Import the class to test
from app.dual_mode.mode_state_manager import (
    ModeStateManager,
    TransitionResult,
    UserModeState,
    ModeTransition
)


class TestModeStateManager:
    """Test suite for ModeStateManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ModeStateManager()
        self.test_user_id = 12345
    
    @patch('app.dual_mode.mode_state_manager.db_get_user_mode')
    def test_get_user_mode_returns_offline_by_default(self, mock_get_mode):
        """Test that get_user_mode returns 'offline' by default."""
        mock_get_mode.return_value = 'offline'
        
        mode = self.manager.get_user_mode(self.test_user_id)
        
        assert mode == 'offline'
        mock_get_mode.assert_called_once_with(self.test_user_id)
    
    @patch('app.dual_mode.mode_state_manager.db_get_user_mode')
    def test_get_user_mode_returns_online(self, mock_get_mode):
        """Test that get_user_mode returns 'online' when set."""
        mock_get_mode.return_value = 'online'
        
        mode = self.manager.get_user_mode(self.test_user_id)
        
        assert mode == 'online'
    
    @patch('app.dual_mode.mode_state_manager.db_set_user_mode')
    def test_set_user_mode_offline(self, mock_set_mode):
        """Test setting user mode to offline."""
        mock_set_mode.return_value = True
        
        result = self.manager.set_user_mode(self.test_user_id, 'offline')
        
        assert result is True
        mock_set_mode.assert_called_once_with(self.test_user_id, 'offline', None, None)
    
    @patch('app.dual_mode.mode_state_manager.db_set_user_mode')
    def test_set_user_mode_online_with_session(self, mock_set_mode):
        """Test setting user mode to online with session ID."""
        mock_set_mode.return_value = True
        session_id = uuid4()
        
        result = self.manager.set_user_mode(self.test_user_id, 'online', session_id=session_id)
        
        assert result is True
        mock_set_mode.assert_called_once_with(self.test_user_id, 'online', None, session_id)
    
    def test_set_user_mode_invalid_mode(self):
        """Test that invalid mode returns False."""
        result = self.manager.set_user_mode(self.test_user_id, 'invalid_mode')
        
        assert result is False
    
    @patch('app.dual_mode.mode_state_manager.db_get_user_mode')
    def test_is_offline_mode_true(self, mock_get_mode):
        """Test is_offline_mode returns True when user is offline."""
        mock_get_mode.return_value = 'offline'
        
        result = self.manager.is_offline_mode(self.test_user_id)
        
        assert result is True
    
    @patch('app.dual_mode.mode_state_manager.db_get_user_mode')
    def test_is_offline_mode_false(self, mock_get_mode):
        """Test is_offline_mode returns False when user is online."""
        mock_get_mode.return_value = 'online'
        
        result = self.manager.is_offline_mode(self.test_user_id)
        
        assert result is False
    
    @patch('app.dual_mode.mode_state_manager.db_get_user_mode')
    def test_is_online_mode_true(self, mock_get_mode):
        """Test is_online_mode returns True when user is online."""
        mock_get_mode.return_value = 'online'
        
        result = self.manager.is_online_mode(self.test_user_id)
        
        assert result is True
    
    @patch('app.dual_mode.mode_state_manager.db_get_user_mode')
    def test_is_online_mode_false(self, mock_get_mode):
        """Test is_online_mode returns False when user is offline."""
        mock_get_mode.return_value = 'offline'
        
        result = self.manager.is_online_mode(self.test_user_id)
        
        assert result is False
    
    @patch('app.dual_mode.mode_state_manager.log_mode_transition')
    @patch('app.dual_mode.mode_state_manager.db_set_user_mode')
    @patch('app.dual_mode.mode_state_manager.has_sufficient_credits')
    @patch('app.dual_mode.mode_state_manager.db_get_offline_state')
    @patch('app.dual_mode.mode_state_manager.db_get_user_mode')
    def test_transition_offline_to_online_success(
        self, mock_get_mode, mock_get_state, mock_has_credits, 
        mock_set_mode, mock_log
    ):
        """Test successful transition from offline to online mode."""
        mock_get_mode.return_value = 'offline'
        mock_get_state.return_value = {'last_symbol': 'BTCUSDT'}
        mock_has_credits.return_value = True
        mock_set_mode.return_value = True
        
        result = self.manager.transition_mode(self.test_user_id, 'offline', 'online')
        
        assert result.success is True
        assert 'online mode' in result.message
        assert result.duration_ms is not None
        mock_log.assert_called_once()
    
    @patch('app.dual_mode.mode_state_manager.log_mode_transition')
    @patch('app.dual_mode.mode_state_manager.has_sufficient_credits')
    @patch('app.dual_mode.mode_state_manager.db_get_user_mode')
    def test_transition_offline_to_online_insufficient_credits(
        self, mock_get_mode, mock_has_credits, mock_log
    ):
        """Test transition to online fails with insufficient credits."""
        mock_get_mode.return_value = 'offline'
        mock_has_credits.return_value = False
        
        result = self.manager.transition_mode(self.test_user_id, 'offline', 'online')
        
        assert result.success is False
        assert 'Insufficient' in result.message
        assert result.error is not None
        mock_log.assert_called_once()
    
    @patch('app.dual_mode.mode_state_manager.log_mode_transition')
    @patch('app.dual_mode.mode_state_manager.db_set_user_mode')
    @patch('app.dual_mode.mode_state_manager.get_active_session')
    @patch('app.dual_mode.mode_state_manager.db_get_user_mode')
    def test_transition_online_to_offline_closes_session(
        self, mock_get_mode, mock_get_session, mock_set_mode, mock_log
    ):
        """Test transition from online to offline closes active session."""
        mock_get_mode.return_value = 'online'
        mock_get_session.return_value = {'session_id': str(uuid4())}
        mock_set_mode.return_value = True
        
        with patch('app.dual_mode_db.close_session') as mock_close:
            result = self.manager.transition_mode(self.test_user_id, 'online', 'offline')
            
            assert result.success is True
            mock_close.assert_called_once()
    
    @patch('app.dual_mode.mode_state_manager.log_mode_transition')
    @patch('app.dual_mode.mode_state_manager.db_get_user_mode')
    def test_transition_invalid_target_mode(self, mock_get_mode, mock_log):
        """Test transition with invalid target mode fails."""
        mock_get_mode.return_value = 'offline'
        
        result = self.manager.transition_mode(self.test_user_id, 'offline', 'invalid')
        
        assert result.success is False
        assert 'Invalid' in result.message
        mock_log.assert_called_once()
    
    @patch('app.dual_mode.mode_state_manager.log_mode_transition')
    @patch('app.dual_mode.mode_state_manager.db_get_user_mode')
    def test_transition_mode_mismatch(self, mock_get_mode, mock_log):
        """Test transition fails when current mode doesn't match from_mode."""
        mock_get_mode.return_value = 'online'
        
        result = self.manager.transition_mode(self.test_user_id, 'offline', 'online')
        
        assert result.success is False
        assert 'mismatch' in result.message
        mock_log.assert_called_once()
    
    @patch('app.dual_mode.mode_state_manager.db_get_mode_history')
    def test_get_mode_history(self, mock_get_history):
        """Test getting mode transition history."""
        mock_get_history.return_value = [
            {
                'user_id': self.test_user_id,
                'from_mode': 'offline',
                'to_mode': 'online',
                'success': True,
                'error_message': None,
                'duration_ms': 150,
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        
        history = self.manager.get_mode_history(self.test_user_id, limit=5)
        
        assert len(history) == 1
        assert isinstance(history[0], ModeTransition)
        assert history[0].user_id == self.test_user_id
        assert history[0].success is True
        mock_get_history.assert_called_once_with(self.test_user_id, 5)
    
    def test_validate_mode_access_offline_always_true(self):
        """Test that offline mode is always accessible."""
        result = self.manager.validate_mode_access(self.test_user_id, 'offline')
        
        assert result is True
    
    @patch('app.dual_mode.mode_state_manager.has_sufficient_credits')
    def test_validate_mode_access_online_with_credits(self, mock_has_credits):
        """Test online mode access with sufficient credits."""
        mock_has_credits.return_value = True
        
        result = self.manager.validate_mode_access(self.test_user_id, 'online')
        
        assert result is True
    
    @patch('app.dual_mode.mode_state_manager.has_sufficient_credits')
    def test_validate_mode_access_online_without_credits(self, mock_has_credits):
        """Test online mode access without sufficient credits."""
        mock_has_credits.return_value = False
        
        result = self.manager.validate_mode_access(self.test_user_id, 'online')
        
        assert result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
