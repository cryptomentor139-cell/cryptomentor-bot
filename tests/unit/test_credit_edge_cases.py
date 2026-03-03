"""
Unit tests for CreditManager edge cases.

Feature: dual-mode-offline-online
Task: 3.3 Write unit tests for credit edge cases
Requirements: 4.5

This test suite focuses on edge cases:
- Insufficient credits handling
- Negative credit amounts
- Zero credit amounts
- Concurrent credit operations
- Very large credit amounts
- Multiple rapid transactions
"""

import pytest
import os
from unittest.mock import patch, MagicMock, call
from datetime import datetime
from uuid import uuid4
import threading
import time

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


class TestCreditEdgeCases:
    """Test suite for CreditManager edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = CreditManager()
        self.test_user_id = 12345
        self.test_admin_id = 99999
    
    # ========================================================================
    # Insufficient Credits Handling Tests
    # ========================================================================
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_deduct_credits_exactly_insufficient_by_one(self, mock_get_credits):
        """Test deducting credits when balance is exactly 1 less than required."""
        # Arrange
        mock_get_credits.return_value = 99
        
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 100, "Test deduction")
        
        # Assert
        assert result.success is False
        assert "Insufficient credits" in result.error
        assert "Current: 99" in result.error
        assert "Required: 100" in result.error
        assert result.new_balance is None
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_deduct_credits_zero_balance(self, mock_get_credits):
        """Test deducting credits when user has zero balance."""
        # Arrange
        mock_get_credits.return_value = 0
        
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 1, "Test deduction")
        
        # Assert
        assert result.success is False
        assert "Insufficient credits" in result.error
        assert "Current: 0" in result.error
        assert result.new_balance is None
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_deduct_credits_large_deficit(self, mock_get_credits):
        """Test deducting credits when balance is far less than required."""
        # Arrange
        mock_get_credits.return_value = 10
        
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 1000, "Test deduction")
        
        # Assert
        assert result.success is False
        assert "Insufficient credits" in result.error
        assert "Current: 10" in result.error
        assert "Required: 1000" in result.error
    
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_deduct_credits_exact_balance(self, mock_get_credits, mock_deduct):
        """Test deducting credits when amount equals exact balance."""
        # Arrange
        mock_get_credits.side_effect = [100, 0]  # Before and after
        mock_deduct.return_value = True
        
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 100, "Test deduction")
        
        # Assert
        assert result.success is True
        assert result.new_balance == 0
        assert result.error is None
    
    @patch('app.dual_mode.credit_manager.db_has_sufficient_credits')
    def test_has_sufficient_credits_boundary_cases(self, mock_has_credits):
        """Test has_sufficient_credits with boundary values."""
        # Test exact match
        mock_has_credits.return_value = True
        assert self.manager.has_sufficient_credits(self.test_user_id, 100) is True
        
        # Test zero required
        assert self.manager.has_sufficient_credits(self.test_user_id, 0) is True
        
        # Test insufficient
        mock_has_credits.return_value = False
        assert self.manager.has_sufficient_credits(self.test_user_id, 101) is False
    
    # ========================================================================
    # Negative Credit Amount Tests
    # ========================================================================
    
    def test_deduct_credits_negative_amount(self):
        """Test deducting negative credit amount is rejected."""
        # Act
        result = self.manager.deduct_credits(self.test_user_id, -10, "Test deduction")
        
        # Assert
        assert result.success is False
        assert "must be positive" in result.error
        assert result.new_balance is None
    
    def test_deduct_credits_large_negative_amount(self):
        """Test deducting large negative amount is rejected."""
        # Act
        result = self.manager.deduct_credits(self.test_user_id, -999999, "Test deduction")
        
        # Assert
        assert result.success is False
        assert "must be positive" in result.error
    
    def test_add_credits_negative_amount(self):
        """Test adding negative credit amount is rejected."""
        # Act
        result = self.manager.add_credits(self.test_user_id, -50, "Test addition")
        
        # Assert
        assert result.success is False
        assert "must be positive" in result.error
        assert result.new_balance is None
    
    def test_add_credits_large_negative_amount(self):
        """Test adding large negative amount is rejected."""
        # Act
        result = self.manager.add_credits(self.test_user_id, -1000000, "Test addition")
        
        # Assert
        assert result.success is False
        assert "must be positive" in result.error
    
    # ========================================================================
    # Zero Credit Amount Tests
    # ========================================================================
    
    def test_deduct_credits_zero_amount(self):
        """Test deducting zero credits is rejected."""
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 0, "Test deduction")
        
        # Assert
        assert result.success is False
        assert "must be positive" in result.error
        assert result.new_balance is None
    
    def test_add_credits_zero_amount(self):
        """Test adding zero credits is rejected."""
        # Act
        result = self.manager.add_credits(self.test_user_id, 0, "Test addition")
        
        # Assert
        assert result.success is False
        assert "must be positive" in result.error
        assert result.new_balance is None
    
    # ========================================================================
    # Very Large Credit Amount Tests
    # ========================================================================
    
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_add_very_large_credit_amount(self, mock_get_credits, mock_add):
        """Test adding very large credit amount."""
        # Arrange
        large_amount = 999999999
        mock_get_credits.return_value = large_amount
        mock_add.return_value = True
        
        # Act
        result = self.manager.add_credits(self.test_user_id, large_amount, "Large grant")
        
        # Assert
        assert result.success is True
        assert result.new_balance == large_amount
        mock_add.assert_called_once_with(self.test_user_id, large_amount, "Large grant", None)
    
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_deduct_very_large_credit_amount(self, mock_get_credits, mock_deduct):
        """Test deducting very large credit amount with sufficient balance."""
        # Arrange
        large_amount = 999999999
        mock_get_credits.side_effect = [large_amount, 0]
        mock_deduct.return_value = True
        
        # Act
        result = self.manager.deduct_credits(self.test_user_id, large_amount, "Large deduction")
        
        # Assert
        assert result.success is True
        assert result.new_balance == 0
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_validate_admin_balance_very_large_amount(self, mock_get_credits):
        """Test validating very large admin balance."""
        # Arrange
        large_balance = 999999999
        mock_get_credits.return_value = large_balance
        
        # Act
        result = self.manager.validate_admin_balance(self.test_admin_id, large_balance)
        
        # Assert
        assert result.valid is True
        assert result.admin_balance == large_balance
    
    # ========================================================================
    # Concurrent Credit Operations Tests
    # ========================================================================
    
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_concurrent_deductions_sequential(self, mock_get_credits, mock_deduct):
        """Test multiple rapid sequential deductions."""
        # Arrange
        initial_balance = 1000
        # Each deduction calls get_user_credits twice (before and after)
        balances = []
        for i in range(10):
            balances.append(initial_balance - i * 10)  # Before deduction
            balances.append(initial_balance - (i + 1) * 10)  # After deduction
        
        mock_get_credits.side_effect = balances
        mock_deduct.return_value = True
        
        # Act - Perform 10 rapid deductions
        results = []
        for i in range(10):
            result = self.manager.deduct_credits(self.test_user_id, 10, f"Deduction {i+1}")
            results.append(result)
        
        # Assert
        assert all(r.success for r in results)
        assert results[0].new_balance == 990
        assert results[9].new_balance == 900
        assert mock_deduct.call_count == 10
    
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_concurrent_additions_sequential(self, mock_get_credits, mock_add):
        """Test multiple rapid sequential additions."""
        # Arrange
        initial_balance = 0
        # Each addition calls get_user_credits once (after addition)
        balances = []
        for i in range(10):
            balances.append(initial_balance + (i + 1) * 50)  # After addition
        
        mock_get_credits.side_effect = balances
        mock_add.return_value = True
        
        # Act - Perform 10 rapid additions
        results = []
        for i in range(10):
            result = self.manager.add_credits(self.test_user_id, 50, f"Addition {i+1}")
            results.append(result)
        
        # Assert
        assert all(r.success for r in results)
        assert results[0].new_balance == 50
        assert results[9].new_balance == 500
        assert mock_add.call_count == 10
    
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_concurrent_mixed_operations(self, mock_get_credits, mock_add, mock_deduct):
        """Test mixed additions and deductions in rapid succession."""
        # Arrange
        # add_credits calls get_user_credits once (after)
        # deduct_credits calls get_user_credits twice (before and after)
        balances = [
            150,  # After add 1
            150, 140,  # Before and after deduct 1
            190,  # After add 2
            190, 180,  # Before and after deduct 2
            230   # After add 3
        ]
        mock_get_credits.side_effect = balances
        mock_add.return_value = True
        mock_deduct.return_value = True
        
        # Act - Alternate between add and deduct
        results = []
        results.append(self.manager.add_credits(self.test_user_id, 50, "Add 1"))
        results.append(self.manager.deduct_credits(self.test_user_id, 10, "Deduct 1"))
        results.append(self.manager.add_credits(self.test_user_id, 50, "Add 2"))
        results.append(self.manager.deduct_credits(self.test_user_id, 10, "Deduct 2"))
        results.append(self.manager.add_credits(self.test_user_id, 50, "Add 3"))
        
        # Assert
        assert all(r.success for r in results)
        assert results[0].new_balance == 150
        assert results[1].new_balance == 140
        assert results[4].new_balance == 230
    
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_concurrent_deductions_with_race_condition(self, mock_get_credits, mock_deduct):
        """Test concurrent deductions that could cause race condition."""
        # Arrange - Simulate race condition where balance check passes but deduction fails
        mock_get_credits.return_value = 100  # Balance check shows sufficient
        mock_deduct.return_value = False  # But deduction fails (another transaction won)
        
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 50, "Concurrent deduction")
        
        # Assert
        assert result.success is False
        assert "Failed to deduct credits" in result.error
    
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_concurrent_additions_with_failure(self, mock_get_credits, mock_add):
        """Test concurrent additions where one fails."""
        # Arrange
        mock_get_credits.return_value = 100
        mock_add.return_value = False  # Simulate failure
        
        # Act
        result = self.manager.add_credits(self.test_user_id, 50, "Concurrent addition")
        
        # Assert
        assert result.success is False
        assert "Failed to add credits" in result.error
    
    # ========================================================================
    # Multiple Rapid Transactions Tests
    # ========================================================================
    
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_rapid_deductions_with_session_ids(self, mock_get_credits, mock_deduct):
        """Test rapid deductions with different session IDs."""
        # Arrange
        # Each deduction calls get_user_credits twice (before and after)
        balances = []
        for i in range(5):
            balances.append(1000 - i * 10)  # Before deduction
            balances.append(1000 - (i + 1) * 10)  # After deduction
        
        mock_get_credits.side_effect = balances
        mock_deduct.return_value = True
        
        # Act - Rapid deductions with unique session IDs
        results = []
        for i in range(5):
            session_id = uuid4()
            result = self.manager.deduct_credits(
                self.test_user_id, 
                10, 
                f"Online mode usage {i+1}",
                session_id
            )
            results.append(result)
        
        # Assert
        assert all(r.success for r in results)
        assert mock_deduct.call_count == 5
        # Verify each call had a unique session_id
        for i, call_args in enumerate(mock_deduct.call_args_list):
            assert call_args[0][3] is not None  # session_id is not None
    
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_rapid_additions_with_admin_ids(self, mock_get_credits, mock_add):
        """Test rapid additions with different admin IDs."""
        # Arrange
        balances = [0, 100, 200, 300, 400, 500]
        mock_get_credits.side_effect = balances
        mock_add.return_value = True
        
        # Act - Rapid additions from different admins
        results = []
        for i in range(5):
            admin_id = 90000 + i
            result = self.manager.add_credits(
                self.test_user_id,
                100,
                f"Admin grant {i+1}",
                admin_id
            )
            results.append(result)
        
        # Assert
        assert all(r.success for r in results)
        assert mock_add.call_count == 5
    
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_rapid_deductions_until_insufficient(self, mock_get_credits, mock_deduct):
        """Test rapid deductions until balance becomes insufficient."""
        # Arrange
        # Each deduction calls get_user_credits twice (before and after)
        # 10 successful deductions + 1 failed (only before check)
        balances = []
        for i in range(10):
            balances.append(100 - i * 10)  # Before deduction
            balances.append(100 - (i + 1) * 10)  # After deduction
        balances.append(0)  # Final check for 11th deduction (insufficient)
        
        mock_get_credits.side_effect = balances
        mock_deduct.return_value = True
        
        # Act - Deduct 10 credits repeatedly
        results = []
        for i in range(11):
            result = self.manager.deduct_credits(self.test_user_id, 10, f"Deduction {i+1}")
            results.append(result)
        
        # Assert
        # First 10 should succeed
        assert all(r.success for r in results[:10])
        # Last one should fail (balance is 0, need 10)
        assert results[10].success is False
        assert "Insufficient credits" in results[10].error
    
    # ========================================================================
    # Error Handling Tests
    # ========================================================================
    
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_deduct_credits_database_error(self, mock_get_credits, mock_deduct):
        """Test deduction handles database errors gracefully."""
        # Arrange
        mock_get_credits.return_value = 100
        mock_deduct.side_effect = Exception("Database connection error")
        
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 10, "Test deduction")
        
        # Assert
        assert result.success is False
        assert result.error is not None
        assert "Database connection error" in result.error
    
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_add_credits_database_error(self, mock_get_credits, mock_add):
        """Test addition handles database errors gracefully."""
        # Arrange
        mock_add.side_effect = Exception("Database timeout")
        
        # Act
        result = self.manager.add_credits(self.test_user_id, 50, "Test addition")
        
        # Assert
        assert result.success is False
        assert result.error is not None
        assert "Database timeout" in result.error
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_validate_admin_balance_database_error(self, mock_get_credits):
        """Test admin balance validation handles database errors."""
        # Arrange
        mock_get_credits.side_effect = Exception("API connection failed")
        
        # Act
        result = self.manager.validate_admin_balance(self.test_admin_id, 100)
        
        # Assert
        assert result.valid is False
        assert result.error is not None
        # When get_user_credits fails, it returns 0, so we get insufficient balance error
        assert "Insufficient admin balance" in result.error
        assert result.admin_balance == 0
    
    # ========================================================================
    # Edge Case Combinations
    # ========================================================================
    
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_deduct_one_credit_from_one_credit_balance(self, mock_get_credits, mock_deduct):
        """Test deducting 1 credit when balance is exactly 1."""
        # Arrange
        mock_get_credits.side_effect = [1, 0]
        mock_deduct.return_value = True
        
        # Act
        result = self.manager.deduct_credits(self.test_user_id, 1, "Minimum deduction")
        
        # Assert
        assert result.success is True
        assert result.new_balance == 0
    
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_add_one_credit_to_zero_balance(self, mock_get_credits, mock_add):
        """Test adding 1 credit to zero balance."""
        # Arrange
        mock_get_credits.return_value = 1
        mock_add.return_value = True
        
        # Act
        result = self.manager.add_credits(self.test_user_id, 1, "Minimum addition")
        
        # Assert
        assert result.success is True
        assert result.new_balance == 1
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_validate_admin_balance_exact_match(self, mock_get_credits):
        """Test validating admin balance when amount exactly matches balance."""
        # Arrange
        mock_get_credits.return_value = 500
        
        # Act
        result = self.manager.validate_admin_balance(self.test_admin_id, 500)
        
        # Assert
        assert result.valid is True
        assert result.admin_balance == 500
    
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    def test_validate_admin_balance_one_less(self, mock_get_credits):
        """Test validating admin balance when amount is one more than balance."""
        # Arrange
        mock_get_credits.return_value = 499
        
        # Act
        result = self.manager.validate_admin_balance(self.test_admin_id, 500)
        
        # Assert
        assert result.valid is False
        assert result.admin_balance == 499
        assert "Insufficient admin balance" in result.error


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
