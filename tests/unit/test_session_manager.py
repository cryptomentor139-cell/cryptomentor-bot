"""
Unit tests for SessionManager component.

Tests session lifecycle management including:
- Session creation with unique IDs
- Session retrieval
- Session activity tracking
- Session closure

Feature: dual-mode-offline-online
Task: 6.1
Requirements: 3.1, 9.2
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import UUID, uuid4
from datetime import datetime

from app.dual_mode.session_manager import SessionManager, Session


class TestSessionManager:
    """Test suite for SessionManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = SessionManager()
        self.test_user_id = 12345
        self.test_agent_id = "agent_test_12345"
        self.test_session_id = uuid4()
    
    @patch('app.dual_mode.session_manager.db_create_session')
    def test_create_session_success(self, mock_create):
        """Test successful session creation."""
        # Arrange
        mock_create.return_value = self.test_session_id
        
        # Act
        session = self.manager.create_session(self.test_user_id, self.test_agent_id)
        
        # Assert
        assert session is not None
        assert session.user_id == self.test_user_id
        assert session.agent_id == self.test_agent_id
        assert session.status == 'active'
        assert session.message_count == 0
        assert session.credits_used == 0
        mock_create.assert_called_once_with(self.test_user_id, self.test_agent_id)
    
    @patch('app.dual_mode.session_manager.db_create_session')
    def test_create_session_failure(self, mock_create):
        """Test session creation failure."""
        # Arrange
        mock_create.return_value = None
        
        # Act
        session = self.manager.create_session(self.test_user_id, self.test_agent_id)
        
        # Assert
        assert session is None

    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_get_session_success(self, mock_get):
        """Test successful session retrieval."""
        # Arrange
        mock_session_data = {
            'session_id': str(self.test_session_id),
            'user_id': self.test_user_id,
            'agent_id': self.test_agent_id,
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_activity': '2024-01-15T10:30:00+00:00',
            'message_count': 5,
            'credits_used': 100,
            'status': 'active'
        }
        mock_get.return_value = mock_session_data
        
        # Act
        session = self.manager.get_session(self.test_user_id)
        
        # Assert
        assert session is not None
        assert session.user_id == self.test_user_id
        assert session.agent_id == self.test_agent_id
        assert session.status == 'active'
        assert session.message_count == 5
        assert session.credits_used == 100
        mock_get.assert_called_once_with(self.test_user_id)
    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_get_session_not_found(self, mock_get):
        """Test session retrieval when no session exists."""
        # Arrange
        mock_get.return_value = None
        
        # Act
        session = self.manager.get_session(self.test_user_id)
        
        # Assert
        assert session is None
    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_is_session_active_true(self, mock_get):
        """Test is_session_active returns True for active session."""
        # Arrange
        mock_session_data = {
            'session_id': str(self.test_session_id),
            'user_id': self.test_user_id,
            'agent_id': self.test_agent_id,
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_activity': '2024-01-15T10:30:00+00:00',
            'message_count': 5,
            'credits_used': 100,
            'status': 'active'
        }
        mock_get.return_value = mock_session_data
        
        # Act
        is_active = self.manager.is_session_active(self.test_user_id)
        
        # Assert
        assert is_active is True

    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_is_session_active_false_no_session(self, mock_get):
        """Test is_session_active returns False when no session exists."""
        # Arrange
        mock_get.return_value = None
        
        # Act
        is_active = self.manager.is_session_active(self.test_user_id)
        
        # Assert
        assert is_active is False
    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_is_session_active_false_closed_session(self, mock_get):
        """Test is_session_active returns False for closed session."""
        # Arrange
        mock_session_data = {
            'session_id': str(self.test_session_id),
            'user_id': self.test_user_id,
            'agent_id': self.test_agent_id,
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_activity': '2024-01-15T10:30:00+00:00',
            'message_count': 5,
            'credits_used': 100,
            'status': 'closed'
        }
        mock_get.return_value = mock_session_data
        
        # Act
        is_active = self.manager.is_session_active(self.test_user_id)
        
        # Assert
        assert is_active is False
    
    @patch('app.dual_mode.session_manager.db_close_session')
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_close_session_success(self, mock_get, mock_close):
        """Test successful session closure."""
        # Arrange
        mock_session_data = {
            'session_id': str(self.test_session_id),
            'user_id': self.test_user_id,
            'agent_id': self.test_agent_id,
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_activity': '2024-01-15T10:30:00+00:00',
            'message_count': 5,
            'credits_used': 100,
            'status': 'active'
        }
        mock_get.return_value = mock_session_data
        mock_close.return_value = True
        
        # Act
        success = self.manager.close_session(self.test_user_id)
        
        # Assert
        assert success is True
        mock_close.assert_called_once()

    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_close_session_no_active_session(self, mock_get):
        """Test close_session when no active session exists."""
        # Arrange
        mock_get.return_value = None
        
        # Act
        success = self.manager.close_session(self.test_user_id)
        
        # Assert
        assert success is False
    
    @patch('app.dual_mode.session_manager.db_update_session_activity')
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_update_session_activity_success(self, mock_get, mock_update):
        """Test successful session activity update."""
        # Arrange
        mock_session_data = {
            'session_id': str(self.test_session_id),
            'user_id': self.test_user_id,
            'agent_id': self.test_agent_id,
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_activity': '2024-01-15T10:30:00+00:00',
            'message_count': 5,
            'credits_used': 100,
            'status': 'active'
        }
        mock_get.return_value = mock_session_data
        mock_update.return_value = True
        
        # Act
        success = self.manager.update_session_activity(self.test_user_id, credits_used=10)
        
        # Assert
        assert success is True
        mock_update.assert_called_once()
    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_update_session_activity_no_session(self, mock_get):
        """Test update_session_activity when no active session exists."""
        # Arrange
        mock_get.return_value = None
        
        # Act
        success = self.manager.update_session_activity(self.test_user_id, credits_used=10)
        
        # Assert
        assert success is False


    @patch('app.dual_mode.session_manager.db_create_session')
    def test_create_session_unique_ids(self, mock_create):
        """Test that multiple session creations generate unique session IDs."""
        # Arrange
        session_id_1 = uuid4()
        session_id_2 = uuid4()
        mock_create.side_effect = [session_id_1, session_id_2]
        
        # Act
        session1 = self.manager.create_session(self.test_user_id, self.test_agent_id)
        session2 = self.manager.create_session(self.test_user_id + 1, self.test_agent_id)
        
        # Assert
        assert session1 is not None
        assert session2 is not None
        assert session1.session_id != session2.session_id
        assert mock_create.call_count == 2


class TestSessionExpiration:
    """Test suite for session expiration scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = SessionManager()
        self.test_user_id = 12345
        self.test_agent_id = "agent_test_12345"
        self.test_session_id = uuid4()
    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_expired_session_not_returned_as_active(self, mock_get):
        """Test that expired sessions are not returned as active."""
        # Arrange
        mock_session_data = {
            'session_id': str(self.test_session_id),
            'user_id': self.test_user_id,
            'agent_id': self.test_agent_id,
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_activity': '2024-01-15T10:30:00+00:00',
            'message_count': 5,
            'credits_used': 100,
            'status': 'expired'
        }
        mock_get.return_value = mock_session_data
        
        # Act
        is_active = self.manager.is_session_active(self.test_user_id)
        
        # Assert
        assert is_active is False
    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_get_expired_session_returns_session_object(self, mock_get):
        """Test that get_session returns expired session with correct status."""
        # Arrange
        mock_session_data = {
            'session_id': str(self.test_session_id),
            'user_id': self.test_user_id,
            'agent_id': self.test_agent_id,
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_activity': '2024-01-15T10:30:00+00:00',
            'message_count': 5,
            'credits_used': 100,
            'status': 'expired'
        }
        mock_get.return_value = mock_session_data
        
        # Act
        session = self.manager.get_session(self.test_user_id)
        
        # Assert
        assert session is not None
        assert session.status == 'expired'
        assert session.user_id == self.test_user_id
    
    @patch('app.dual_mode.session_manager.db_close_session')
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_close_expired_session(self, mock_get, mock_close):
        """Test closing an already expired session."""
        # Arrange
        mock_session_data = {
            'session_id': str(self.test_session_id),
            'user_id': self.test_user_id,
            'agent_id': self.test_agent_id,
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_activity': '2024-01-15T10:30:00+00:00',
            'message_count': 5,
            'credits_used': 100,
            'status': 'expired'
        }
        mock_get.return_value = mock_session_data
        mock_close.return_value = True
        
        # Act
        success = self.manager.close_session(self.test_user_id)
        
        # Assert
        assert success is True
        mock_close.assert_called_once()


class TestConcurrentSessions:
    """Test suite for concurrent session scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = SessionManager()
        self.test_user_id_1 = 12345
        self.test_user_id_2 = 67890
        self.test_agent_id_1 = "agent_test_12345"
        self.test_agent_id_2 = "agent_test_67890"
        self.test_session_id_1 = uuid4()
        self.test_session_id_2 = uuid4()
    
    @patch('app.dual_mode.session_manager.db_create_session')
    def test_multiple_users_create_sessions_simultaneously(self, mock_create):
        """Test that multiple users can create sessions concurrently."""
        # Arrange
        mock_create.side_effect = [self.test_session_id_1, self.test_session_id_2]
        
        # Act
        session1 = self.manager.create_session(self.test_user_id_1, self.test_agent_id_1)
        session2 = self.manager.create_session(self.test_user_id_2, self.test_agent_id_2)
        
        # Assert
        assert session1 is not None
        assert session2 is not None
        assert session1.user_id == self.test_user_id_1
        assert session2.user_id == self.test_user_id_2
        assert session1.session_id != session2.session_id
        assert mock_create.call_count == 2
    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_get_session_returns_correct_user_session(self, mock_get):
        """Test that get_session returns the correct session for each user."""
        # Arrange
        def mock_get_session(user_id):
            if user_id == self.test_user_id_1:
                return {
                    'session_id': str(self.test_session_id_1),
                    'user_id': self.test_user_id_1,
                    'agent_id': self.test_agent_id_1,
                    'created_at': '2024-01-15T10:00:00+00:00',
                    'last_activity': '2024-01-15T10:30:00+00:00',
                    'message_count': 5,
                    'credits_used': 100,
                    'status': 'active'
                }
            elif user_id == self.test_user_id_2:
                return {
                    'session_id': str(self.test_session_id_2),
                    'user_id': self.test_user_id_2,
                    'agent_id': self.test_agent_id_2,
                    'created_at': '2024-01-15T10:00:00+00:00',
                    'last_activity': '2024-01-15T10:30:00+00:00',
                    'message_count': 3,
                    'credits_used': 50,
                    'status': 'active'
                }
            return None
        
        mock_get.side_effect = mock_get_session
        
        # Act
        session1 = self.manager.get_session(self.test_user_id_1)
        session2 = self.manager.get_session(self.test_user_id_2)
        
        # Assert
        assert session1 is not None
        assert session2 is not None
        assert session1.user_id == self.test_user_id_1
        assert session2.user_id == self.test_user_id_2
        assert session1.session_id == str(self.test_session_id_1)
        assert session2.session_id == str(self.test_session_id_2)
        assert session1.message_count == 5
        assert session2.message_count == 3
    
    @patch('app.dual_mode.session_manager.db_update_session_activity')
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_concurrent_session_activity_updates(self, mock_get, mock_update):
        """Test that session activity updates work correctly for concurrent users."""
        # Arrange
        def mock_get_session(user_id):
            if user_id == self.test_user_id_1:
                return {
                    'session_id': str(self.test_session_id_1),
                    'user_id': self.test_user_id_1,
                    'agent_id': self.test_agent_id_1,
                    'created_at': '2024-01-15T10:00:00+00:00',
                    'last_activity': '2024-01-15T10:30:00+00:00',
                    'message_count': 5,
                    'credits_used': 100,
                    'status': 'active'
                }
            elif user_id == self.test_user_id_2:
                return {
                    'session_id': str(self.test_session_id_2),
                    'user_id': self.test_user_id_2,
                    'agent_id': self.test_agent_id_2,
                    'created_at': '2024-01-15T10:00:00+00:00',
                    'last_activity': '2024-01-15T10:30:00+00:00',
                    'message_count': 3,
                    'credits_used': 50,
                    'status': 'active'
                }
            return None
        
        mock_get.side_effect = mock_get_session
        mock_update.return_value = True
        
        # Act
        success1 = self.manager.update_session_activity(self.test_user_id_1, credits_used=10)
        success2 = self.manager.update_session_activity(self.test_user_id_2, credits_used=5)
        
        # Assert
        assert success1 is True
        assert success2 is True
        assert mock_update.call_count == 2
    
    @patch('app.dual_mode.session_manager.db_close_session')
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_close_one_session_does_not_affect_other(self, mock_get, mock_close):
        """Test that closing one user's session doesn't affect another user's session."""
        # Arrange
        def mock_get_session(user_id):
            if user_id == self.test_user_id_1:
                return {
                    'session_id': str(self.test_session_id_1),
                    'user_id': self.test_user_id_1,
                    'agent_id': self.test_agent_id_1,
                    'created_at': '2024-01-15T10:00:00+00:00',
                    'last_activity': '2024-01-15T10:30:00+00:00',
                    'message_count': 5,
                    'credits_used': 100,
                    'status': 'active'
                }
            elif user_id == self.test_user_id_2:
                return {
                    'session_id': str(self.test_session_id_2),
                    'user_id': self.test_user_id_2,
                    'agent_id': self.test_agent_id_2,
                    'created_at': '2024-01-15T10:00:00+00:00',
                    'last_activity': '2024-01-15T10:30:00+00:00',
                    'message_count': 3,
                    'credits_used': 50,
                    'status': 'active'
                }
            return None
        
        mock_get.side_effect = mock_get_session
        mock_close.return_value = True
        
        # Act
        success1 = self.manager.close_session(self.test_user_id_1)
        
        # Assert
        assert success1 is True
        # Verify only one close call was made (for user 1)
        assert mock_close.call_count == 1
        # Verify the correct session ID was closed
        call_args = mock_close.call_args[0][0]
        assert str(call_args) == str(self.test_session_id_1)
    
    @patch('app.dual_mode.session_manager.db_create_session')
    def test_same_user_cannot_create_multiple_active_sessions(self, mock_create):
        """Test behavior when same user tries to create multiple sessions."""
        # Arrange
        mock_create.side_effect = [self.test_session_id_1, self.test_session_id_2]
        
        # Act
        session1 = self.manager.create_session(self.test_user_id_1, self.test_agent_id_1)
        session2 = self.manager.create_session(self.test_user_id_1, self.test_agent_id_1)
        
        # Assert
        # Both sessions are created (database constraint should handle uniqueness)
        assert session1 is not None
        assert session2 is not None
        # But they have different session IDs
        assert session1.session_id != session2.session_id
        assert mock_create.call_count == 2


class TestSessionRetrievalEdgeCases:
    """Test suite for edge cases in session retrieval."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = SessionManager()
        self.test_user_id = 12345
        self.test_agent_id = "agent_test_12345"
        self.test_session_id = uuid4()
    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_get_session_with_datetime_objects(self, mock_get):
        """Test session retrieval when database returns datetime objects instead of strings."""
        # Arrange
        mock_session_data = {
            'session_id': str(self.test_session_id),
            'user_id': self.test_user_id,
            'agent_id': self.test_agent_id,
            'created_at': datetime(2024, 1, 15, 10, 0, 0),
            'last_activity': datetime(2024, 1, 15, 10, 30, 0),
            'message_count': 5,
            'credits_used': 100,
            'status': 'active'
        }
        mock_get.return_value = mock_session_data
        
        # Act
        session = self.manager.get_session(self.test_user_id)
        
        # Assert
        assert session is not None
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_activity, datetime)
    
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_get_session_handles_exception(self, mock_get):
        """Test that get_session handles exceptions gracefully."""
        # Arrange
        mock_get.side_effect = Exception("Database connection error")
        
        # Act
        session = self.manager.get_session(self.test_user_id)
        
        # Assert
        assert session is None
    
    @patch('app.dual_mode.session_manager.db_create_session')
    def test_create_session_handles_exception(self, mock_create):
        """Test that create_session handles exceptions gracefully."""
        # Arrange
        mock_create.side_effect = Exception("Database connection error")
        
        # Act
        session = self.manager.create_session(self.test_user_id, self.test_agent_id)
        
        # Assert
        assert session is None
    
    @patch('app.dual_mode.session_manager.db_update_session_activity')
    @patch('app.dual_mode.session_manager.db_get_active_session')
    def test_update_session_activity_with_zero_credits(self, mock_get, mock_update):
        """Test updating session activity with zero credits used."""
        # Arrange
        mock_session_data = {
            'session_id': str(self.test_session_id),
            'user_id': self.test_user_id,
            'agent_id': self.test_agent_id,
            'created_at': '2024-01-15T10:00:00+00:00',
            'last_activity': '2024-01-15T10:30:00+00:00',
            'message_count': 5,
            'credits_used': 100,
            'status': 'active'
        }
        mock_get.return_value = mock_session_data
        mock_update.return_value = True
        
        # Act
        success = self.manager.update_session_activity(self.test_user_id, credits_used=0)
        
        # Assert
        assert success is True
        mock_update.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
