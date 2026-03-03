"""
Unit tests for CreditManager class.

Feature: dual-mode-offline-online
Task: 3.1 Create CreditManager class with credit operations
Requirements: 4.1, 4.2, 4.4, 4.6, 13.3, 13.5
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from datetime import datetime
from uuid import uuid4

# Set mock environment variables before importing
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test-key'

# Import CreditManager
from app.dual_mode.credit_manager import (
    CreditManager,
    CreditResult,
    CreditTransaction,
    ValidationResult
)


class TestCreditManager:
    """Test suite for CreditManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = CreditManager()
        self.test_user_id = 12345
        self.test_admin_id = 99999
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_get_user_credits_success(self, mock_get_credits):
        """Test getting user credits successfully."""
        # Arrange
        mock_get_credits.return_value = 100
        
        # Act
        balance = self.manager.get_user_credits(self.test_user_id)
        
        # Assert
        assert balance == 100
        mock_get_credits.assert_called_once_with(self.test_user_id)
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_get_user_credits_error_returns_zero(self, mock_get_credits):
        """Test getting user credits returns 0 on error."""
        # Arrange
        mock_get_credits.side_effect = Exception("Database error")
        
        # Act
        balance = self.manager.get_user_credits(self.test_user_id)
        
        # Assert
        assert balance == 0
    
    @patch('app.dual_mode.credit_manager.db_has_sufficient_credits')
    def test_has_sufficient_credits_true(self, mock_has_credits):
        """Test checking sufficient credits returns True."""
        # Arrange
        mock_has_credits.return_value = True
        
        # Act
        result = self.manager.has_sufficient_credits(self.test_user_id, 50)
        
        # Assert
        assert result is True
        mock_has_credits.assert_called_once_with(self.test_user_id, 50)
    
    @patch('app.dual_mode.credit_manager.db_has_sufficient_credits')
    def test_has_sufficient_credits_false(self, mock_has_credits):
        """Test checking sufficient credits returns False."""
        # Arrange
        mock_has_credits.return_value = False
        
        # Act
        result = self.manager.has_sufficient_credits(self.test_user_id, 150)
        
        # Assert
        assert result is False
    
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_deduct_credits_success(self, mock_get_credits, mock_deduct):
        """Test deducting credits successfully."""
        # Arrange
        mock_get_credits.side_effect = [100, 90]  # Before and after
        mock_deduct.return_value = True
        
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 10, "Test deduction")
        
        # Assert
        assert result.success is True
        assert result.new_balance == 90
        assert result.error is None
        mock_deduct.assert_called_once_with(self.test_user_id, 10, "Test deduction", None)
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_deduct_credits_insufficient_balance(self, mock_get_credits):
        """Test deducting credits with insufficient balance."""
        # Arrange
        mock_get_credits.return_value = 5
        
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 10, "Test deduction")
        
        # Assert
        assert result.success is False
        assert "Insufficient credits" in result.error
        assert result.new_balance is None
    
    def test_deduct_credits_negative_amount(self):
        """Test deducting credits with negative amount."""
        # Act
        result = self.manager.deduct_credits(self.test_user_id, -10, "Test deduction")
        
        # Assert
        assert result.success is False
        assert "must be positive" in result.error
    
    def test_deduct_credits_zero_amount(self):
        """Test deducting credits with zero amount."""
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 0, "Test deduction")
        
        # Assert
        assert result.success is False
        assert "must be positive" in result.error
    
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_deduct_credits_with_session_id(self, mock_get_credits, mock_deduct):
        """Test deducting credits with session ID."""
        # Arrange
        mock_get_credits.side_effect = [100, 95]
        mock_deduct.return_value = True
        session_id = uuid4()
        
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 5, "Online mode usage", session_id)
        
        # Assert
        assert result.success is True
        mock_deduct.assert_called_once_with(self.test_user_id, 5, "Online mode usage", session_id)
    
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_add_credits_success(self, mock_get_credits, mock_add):
        """Test adding credits successfully."""
        # Arrange
        mock_get_credits.return_value = 150
        mock_add.return_value = True
        
        # Act
        result = self.manager.add_credits(self.test_user_id, 50, "Admin grant")
        
        # Assert
        assert result.success is True
        assert result.new_balance == 150
        assert result.error is None
        mock_add.assert_called_once_with(self.test_user_id, 50, "Admin grant", None)
    
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_add_credits_with_admin_id(self, mock_get_credits, mock_add):
        """Test adding credits with admin ID."""
        # Arrange
        mock_get_credits.return_value = 200
        mock_add.return_value = True
        
        # Act
        result = self.manager.add_credits(
            self.test_user_id, 
            100, 
            "Admin grant", 
            self.test_admin_id
        )
        
        # Assert
        assert result.success is True
        mock_add.assert_called_once_with(
            self.test_user_id, 
            100, 
            "Admin grant", 
            self.test_admin_id
        )
    
    def test_add_credits_negative_amount(self):
        """Test adding credits with negative amount."""
        # Act
        result = self.manager.add_credits(self.test_user_id, -50, "Test addition")
        
        # Assert
        assert result.success is False
        assert "must be positive" in result.error
    
    def test_add_credits_zero_amount(self):
        """Test adding credits with zero amount."""
        # Act
        result = self.manager.add_credits(self.test_user_id, 0, "Test addition")
        
        # Assert
        assert result.success is False
        assert "must be positive" in result.error
    
    @patch('app.dual_mode.credit_manager.db_get_credit_history')
    def test_get_credit_history_success(self, mock_get_history):
        """Test getting credit history successfully."""
        # Arrange
        mock_history = [
            {
                'transaction_id': 'txn-1',
                'user_id': self.test_user_id,
                'amount': 100,
                'balance_after': 100,
                'reason': 'Initial deposit',
                'timestamp': '2024-01-15T10:00:00+00:00',
                'admin_id': self.test_admin_id
            },
            {
                'transaction_id': 'txn-2',
                'user_id': self.test_user_id,
                'amount': -10,
                'balance_after': 90,
                'reason': 'Online mode usage',
                'timestamp': '2024-01-15T11:00:00+00:00',
                'session_id': 'session-123'
            }
        ]
        mock_get_history.return_value = mock_history
        
        # Act
        history = self.manager.get_credit_history(self.test_user_id, limit=10)
        
        # Assert
        assert len(history) == 2
        assert history[0].transaction_id == 'txn-1'
        assert history[0].amount == 100
        assert history[0].admin_id == self.test_admin_id
        assert history[1].transaction_id == 'txn-2'
        assert history[1].amount == -10
        assert history[1].session_id == 'session-123'
        mock_get_history.assert_called_once_with(self.test_user_id, 10)
    
    @patch('app.dual_mode.credit_manager.db_get_credit_history')
    def test_get_credit_history_empty(self, mock_get_history):
        """Test getting credit history with no transactions."""
        # Arrange
        mock_get_history.return_value = []
        
        # Act
        history = self.manager.get_credit_history(self.test_user_id)
        
        # Assert
        assert len(history) == 0
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_validate_admin_balance_sufficient(self, mock_get_credits):
        """Test validating admin balance with sufficient credits."""
        # Arrange
        mock_get_credits.return_value = 1000
        
        # Act
        result = self.manager.validate_admin_balance(self.test_admin_id, 500)
        
        # Assert
        assert result.valid is True
        assert result.admin_balance == 1000
        assert result.error is None
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_validate_admin_balance_insufficient(self, mock_get_credits):
        """Test validating admin balance with insufficient credits."""
        # Arrange
        mock_get_credits.return_value = 100
        
        # Act
        result = self.manager.validate_admin_balance(self.test_admin_id, 500)
        
        # Assert
        assert result.valid is False
        assert result.admin_balance == 100
        assert "Insufficient admin balance" in result.error
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_validate_admin_balance_error(self, mock_get_credits):
        """Test validating admin balance with error."""
        # Arrange
        mock_get_credits.side_effect = Exception("API error")
        
        # Act
        result = self.manager.validate_admin_balance(self.test_admin_id, 500)
        
        # Assert
        assert result.valid is False
        assert result.error is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
