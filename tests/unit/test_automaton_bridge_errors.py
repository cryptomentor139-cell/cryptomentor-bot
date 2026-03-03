"""
Unit tests for AutomatonBridge API error scenarios.

Tests error handling for:
- Connection timeout
- Authentication failure
- Rate limiting

Feature: dual-mode-offline-online
Task: 10.5
Requirements: 12.1, 13.2, 13.7
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError

from app.dual_mode.automaton_bridge import (
    AutomatonBridge,
    AutomatonResponse,
    AgentStatus,
    ValidationResult
)


class TestConnectionTimeout:
    """Test suite for connection timeout scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict('os.environ', {
            'AUTOMATON_API_URL': 'https://api.automaton.test',
            'AUTOMATON_API_KEY': 'test_key_12345',
            'AUTOMATON_TIMEOUT': '30',
            'AUTOMATON_MAX_RETRIES': '3',
            'AUTOMATON_BACKOFF_FACTOR': '2'
        }):
            self.bridge = AutomatonBridge()
        
        self.test_agent_id = "agent_test_12345"
        self.test_message = "Analyze BTCUSDT"
        self.test_admin_id = 99999
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.post')
    def test_send_message_timeout_single_attempt(self, mock_post):
        """Test send_message handles timeout on first attempt."""
        # Arrange
        mock_post.side_effect = Timeout("Connection timed out")
        
        # Act
        response = self.bridge.send_message(self.test_agent_id, self.test_message)
        
        # Assert
        assert response.success is False
        assert response.error == "Request timed out. Please try again."
        assert response.message is None
        assert response.credits_used == 0
        # Should attempt 3 times (initial + 2 retries)
        assert mock_post.call_count == 3
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.post')
    def test_send_message_timeout_all_retries_exhausted(self, mock_post):
        """Test send_message exhausts all retries on persistent timeout."""
        # Arrange
        mock_post.side_effect = Timeout("Connection timed out")
        
        # Act
        response = self.bridge.send_message(self.test_agent_id, self.test_message)
        
        # Assert
        assert response.success is False
        assert "timed out" in response.error.lower()
        assert mock_post.call_count == 3  # Max retries
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_get_agent_status_timeout(self, mock_get):
        """Test get_agent_status handles timeout gracefully."""
        # Arrange
        mock_get.side_effect = Timeout("Connection timed out")
        
        # Act
        status = self.bridge.get_agent_status(self.test_agent_id)
        
        # Assert
        assert status.status == "error"
        assert "timeout" in status.error.lower()
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_validate_api_connection_timeout(self, mock_get):
        """Test validate_api_connection returns False on timeout."""
        # Arrange
        mock_get.side_effect = Timeout("Connection timed out")
        
        # Act
        result = self.bridge.validate_api_connection()
        
        # Assert
        assert result is False
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_get_admin_balance_timeout(self, mock_get):
        """Test get_admin_balance returns 0 on timeout."""
        # Arrange
        mock_get.side_effect = Timeout("Connection timed out")
        
        # Act
        balance = self.bridge.get_admin_balance(self.test_admin_id)
        
        # Assert
        assert balance == 0


class TestAuthenticationFailure:
    """Test suite for authentication failure scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict('os.environ', {
            'AUTOMATON_API_URL': 'https://api.automaton.test',
            'AUTOMATON_API_KEY': 'test_key_12345',
            'AUTOMATON_TIMEOUT': '30',
            'AUTOMATON_MAX_RETRIES': '3',
            'AUTOMATON_BACKOFF_FACTOR': '2'
        }):
            self.bridge = AutomatonBridge()
        
        self.test_agent_id = "agent_test_12345"
        self.test_message = "Analyze BTCUSDT"
        self.test_admin_id = 99999
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.post')
    def test_send_message_authentication_failure_401(self, mock_post):
        """Test send_message handles 401 authentication error."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        # Act
        response = self.bridge.send_message(self.test_agent_id, self.test_message)
        
        # Assert
        assert response.success is False
        assert "authentication" in response.error.lower() or "api key" in response.error.lower()
        assert response.credits_used == 0
        # Should NOT retry on auth errors
        assert mock_post.call_count == 1
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.post')
    def test_send_message_authentication_failure_403(self, mock_post):
        """Test send_message handles 403 forbidden error."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": "Access forbidden"}
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        # Act
        response = self.bridge.send_message(self.test_agent_id, self.test_message)
        
        # Assert
        assert response.success is False
        assert "forbidden" in response.error.lower() or "access" in response.error.lower()
        assert mock_post.call_count == 1  # No retries on auth errors
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_get_agent_status_authentication_failure(self, mock_get):
        """Test get_agent_status handles authentication failure."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        # Act
        status = self.bridge.get_agent_status(self.test_agent_id)
        
        # Assert
        assert status.status == "error"
        assert "authentication" in status.error.lower() or "unauthorized" in status.error.lower()
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_validate_api_connection_authentication_failure(self, mock_get):
        """Test validate_api_connection returns False on auth failure."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        # Act
        result = self.bridge.validate_api_connection()
        
        # Assert
        assert result is False
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_get_admin_balance_authentication_failure(self, mock_get):
        """Test get_admin_balance returns 0 on auth failure."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        # Act
        balance = self.bridge.get_admin_balance(self.test_admin_id)
        
        # Assert
        assert balance == 0


class TestRateLimiting:
    """Test suite for rate limiting scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict('os.environ', {
            'AUTOMATON_API_URL': 'https://api.automaton.test',
            'AUTOMATON_API_KEY': 'test_key_12345',
            'AUTOMATON_TIMEOUT': '30',
            'AUTOMATON_MAX_RETRIES': '3',
            'AUTOMATON_BACKOFF_FACTOR': '2'
        }):
            self.bridge = AutomatonBridge()
        
        self.test_agent_id = "agent_test_12345"
        self.test_message = "Analyze BTCUSDT"
        self.test_admin_id = 99999
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.post')
    def test_send_message_rate_limit_429(self, mock_post):
        """Test send_message handles 429 rate limit error."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_response.headers = {"Retry-After": "60"}
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        # Act
        response = self.bridge.send_message(self.test_agent_id, self.test_message)
        
        # Assert
        assert response.success is False
        assert "rate limit" in response.error.lower()
        assert response.credits_used == 0
        # Should retry on rate limit errors
        assert mock_post.call_count == 3
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.post')
    @patch('app.dual_mode.automaton_bridge.time.sleep')
    def test_send_message_rate_limit_with_backoff(self, mock_sleep, mock_post):
        """Test send_message uses exponential backoff on rate limit."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        # Act
        response = self.bridge.send_message(self.test_agent_id, self.test_message)
        
        # Assert
        assert response.success is False
        # Verify exponential backoff was used (2^0=1, 2^1=2 seconds)
        assert mock_sleep.call_count >= 2
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        # Verify increasing sleep times
        assert sleep_calls[0] < sleep_calls[1]
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.post')
    def test_send_message_rate_limit_eventual_success(self, mock_post):
        """Test send_message succeeds after rate limit on retry."""
        # Arrange
        mock_rate_limit_response = Mock()
        mock_rate_limit_response.status_code = 429
        mock_rate_limit_response.raise_for_status.side_effect = HTTPError(response=mock_rate_limit_response)
        
        mock_success_response = Mock()
        mock_success_response.status_code = 200
        mock_success_response.json.return_value = {
            "message": "Analysis complete",
            "credits_used": 5
        }
        
        # First call fails with rate limit, second succeeds
        mock_post.side_effect = [mock_rate_limit_response, mock_success_response]
        
        # Act
        response = self.bridge.send_message(self.test_agent_id, self.test_message)
        
        # Assert
        assert response.success is True
        assert response.message == "Analysis complete"
        assert response.credits_used == 5
        assert mock_post.call_count == 2
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_get_agent_status_rate_limit(self, mock_get):
        """Test get_agent_status handles rate limit error."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        # Act
        status = self.bridge.get_agent_status(self.test_agent_id)
        
        # Assert
        assert status.status == "error"
        assert "rate limit" in status.error.lower()
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_validate_api_connection_rate_limit(self, mock_get):
        """Test validate_api_connection handles rate limit."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        # Act
        result = self.bridge.validate_api_connection()
        
        # Assert
        assert result is False
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_get_admin_balance_rate_limit(self, mock_get):
        """Test get_admin_balance returns 0 on rate limit."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        # Act
        balance = self.bridge.get_admin_balance(self.test_admin_id)
        
        # Assert
        assert balance == 0


class TestConnectionErrors:
    """Test suite for connection error scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict('os.environ', {
            'AUTOMATON_API_URL': 'https://api.automaton.test',
            'AUTOMATON_API_KEY': 'test_key_12345',
            'AUTOMATON_TIMEOUT': '30',
            'AUTOMATON_MAX_RETRIES': '3',
            'AUTOMATON_BACKOFF_FACTOR': '2'
        }):
            self.bridge = AutomatonBridge()
        
        self.test_agent_id = "agent_test_12345"
        self.test_message = "Analyze BTCUSDT"
        self.test_admin_id = 99999
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.post')
    def test_send_message_connection_error(self, mock_post):
        """Test send_message handles connection error."""
        # Arrange
        mock_post.side_effect = ConnectionError("Failed to establish connection")
        
        # Act
        response = self.bridge.send_message(self.test_agent_id, self.test_message)
        
        # Assert
        assert response.success is False
        assert "connection" in response.error.lower()
        assert response.credits_used == 0
        assert mock_post.call_count == 3  # Should retry
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_get_agent_status_connection_error(self, mock_get):
        """Test get_agent_status handles connection error."""
        # Arrange
        mock_get.side_effect = ConnectionError("Failed to establish connection")
        
        # Act
        status = self.bridge.get_agent_status(self.test_agent_id)
        
        # Assert
        assert status.status == "error"
        assert "connection" in status.error.lower()
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_validate_api_connection_connection_error(self, mock_get):
        """Test validate_api_connection returns False on connection error."""
        # Arrange
        mock_get.side_effect = ConnectionError("Failed to establish connection")
        
        # Act
        result = self.bridge.validate_api_connection()
        
        # Assert
        assert result is False
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.get')
    def test_get_admin_balance_connection_error(self, mock_get):
        """Test get_admin_balance returns 0 on connection error."""
        # Arrange
        mock_get.side_effect = ConnectionError("Failed to establish connection")
        
        # Act
        balance = self.bridge.get_admin_balance(self.test_admin_id)
        
        # Assert
        assert balance == 0


class TestServerErrors:
    """Test suite for server error scenarios (5xx)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict('os.environ', {
            'AUTOMATON_API_URL': 'https://api.automaton.test',
            'AUTOMATON_API_KEY': 'test_key_12345',
            'AUTOMATON_TIMEOUT': '30',
            'AUTOMATON_MAX_RETRIES': '3',
            'AUTOMATON_BACKOFF_FACTOR': '2'
        }):
            self.bridge = AutomatonBridge()
        
        self.test_agent_id = "agent_test_12345"
        self.test_message = "Analyze BTCUSDT"
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.post')
    def test_send_message_server_error_500(self, mock_post):
        """Test send_message handles 500 internal server error."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        # Act
        response = self.bridge.send_message(self.test_agent_id, self.test_message)
        
        # Assert
        assert response.success is False
        assert "server error" in response.error.lower() or "500" in response.error
        assert response.credits_used == 0
        # Should retry on server errors
        assert mock_post.call_count == 3
    
    @patch('app.dual_mode.automaton_bridge.requests.Session.post')
    def test_send_message_service_unavailable_503(self, mock_post):
        """Test send_message handles 503 service unavailable."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.json.return_value = {"error": "Service temporarily unavailable"}
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        # Act
        response = self.bridge.send_message(self.test_agent_id, self.test_message)
        
        # Assert
        assert response.success is False
        assert "unavailable" in response.error.lower() or "503" in response.error
        assert mock_post.call_count == 3  # Should retry
