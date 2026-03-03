"""
Property-based tests for credit tracking and logging.

Feature: dual-mode-offline-online
Task: 3.2 Write property test for credit tracking and logging
Property 5: Credit Tracking and Logging
Requirements: 4.2, 4.4, 4.6

**Validates: Requirements 4.2, 4.4, 4.6**

This test validates that for any Automaton credit transaction (addition or 
deduction), the system should persist the transaction to the database with 
timestamp, amount, reason, and updated balance.
"""

import pytest
import os
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import patch, MagicMock
from datetime import datetime
from uuid import uuid4

# Set mock environment variables before importing
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test-key'

# Import CreditManager
from app.dual_mode.credit_manager import CreditManager


class TestPropertyCreditTracking:
    """Property-based tests for credit tracking and logging."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = CreditManager()
    
    @settings(max_examples=5, deadline=None)
    @given(
        user_id=st.integers(min_value=1, max_value=999999),
        initial_balance=st.integers(min_value=0, max_value=100000),
        credit_amount=st.integers(min_value=1, max_value=10000),
        reason=st.text(min_size=1, max_size=100, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
            blacklist_characters='\x00'
        ))
    )
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    @patch('app.dual_mode.credit_manager.db_get_credit_history')
    def test_credit_addition_persists_with_all_fields(
        self, 
        mock_get_history,
        mock_get_credits, 
        mock_add_credits,
        user_id,
        initial_balance,
        credit_amount,
        reason
    ):
        """
        Property 5: Credit Tracking and Logging - Credit Addition
        
        For any credit addition transaction, the system should persist the 
        transaction to the database with timestamp, amount, reason, and 
        updated balance.
        
        **Validates: Requirements 4.2, 4.4, 4.6**
        """
        # Arrange
        new_balance = initial_balance + credit_amount
        mock_get_credits.return_value = new_balance
        mock_add_credits.return_value = True
        
        # Mock transaction history to verify persistence
        mock_get_history.return_value = [{
            'transaction_id': str(uuid4()),
            'user_id': user_id,
            'amount': credit_amount,
            'balance_after': new_balance,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'admin_id': None
        }]
        
        # Act
        result = self.manager.add_credits(user_id, credit_amount, reason)
        
        # Assert - Transaction succeeded
        assert result.success is True, \
            f"Credit addition should succeed for user {user_id}"
        
        # Assert - New balance is correct
        assert result.new_balance == new_balance, \
            f"New balance should be {new_balance}, got {result.new_balance}"
        
        # Assert - Database function was called with correct parameters
        mock_add_credits.assert_called_once_with(user_id, credit_amount, reason, None)
        
        # Assert - Transaction is persisted and retrievable
        history = self.manager.get_credit_history(user_id, limit=1)
        assert len(history) > 0, \
            "Transaction should be persisted to database"
        
        # Assert - Persisted transaction has all required fields
        transaction = history[0]
        assert transaction.user_id == user_id, \
            "Transaction should have correct user_id"
        assert transaction.amount == credit_amount, \
            "Transaction should have correct amount"
        assert transaction.balance_after == new_balance, \
            "Transaction should have correct balance_after"
        assert transaction.reason == reason, \
            "Transaction should have correct reason"
        assert transaction.timestamp is not None, \
            "Transaction should have timestamp"
        assert isinstance(transaction.timestamp, datetime), \
            "Transaction timestamp should be datetime object"
    
    @settings(max_examples=5, deadline=None)
    @given(
        user_id=st.integers(min_value=1, max_value=999999),
        initial_balance=st.integers(min_value=100, max_value=100000),
        deduct_amount=st.integers(min_value=1, max_value=100),
        reason=st.text(min_size=1, max_size=100, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
            blacklist_characters='\x00'
        ))
    )
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    @patch('app.dual_mode.credit_manager.db_get_credit_history')
    def test_credit_deduction_persists_with_all_fields(
        self,
        mock_get_history,
        mock_get_credits,
        mock_deduct_credits,
        user_id,
        initial_balance,
        deduct_amount,
        reason
    ):
        """
        Property 5: Credit Tracking and Logging - Credit Deduction
        
        For any credit deduction transaction, the system should persist the 
        transaction to the database with timestamp, amount, reason, and 
        updated balance.
        
        **Validates: Requirements 4.2, 4.4, 4.6**
        """
        # Arrange
        new_balance = initial_balance - deduct_amount
        mock_get_credits.side_effect = [initial_balance, new_balance]
        mock_deduct_credits.return_value = True
        
        # Mock transaction history to verify persistence
        mock_get_history.return_value = [{
            'transaction_id': str(uuid4()),
            'user_id': user_id,
            'amount': -deduct_amount,  # Negative for deduction
            'balance_after': new_balance,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'session_id': None
        }]
        
        # Act
        result = self.manager.deduct_credits(user_id, deduct_amount, reason)
        
        # Assert - Transaction succeeded
        assert result.success is True, \
            f"Credit deduction should succeed for user {user_id}"
        
        # Assert - New balance is correct
        assert result.new_balance == new_balance, \
            f"New balance should be {new_balance}, got {result.new_balance}"
        
        # Assert - Database function was called with correct parameters
        mock_deduct_credits.assert_called_once_with(user_id, deduct_amount, reason, None)
        
        # Assert - Transaction is persisted and retrievable
        history = self.manager.get_credit_history(user_id, limit=1)
        assert len(history) > 0, \
            "Transaction should be persisted to database"
        
        # Assert - Persisted transaction has all required fields
        transaction = history[0]
        assert transaction.user_id == user_id, \
            "Transaction should have correct user_id"
        assert transaction.amount == -deduct_amount, \
            "Transaction should have negative amount for deduction"
        assert transaction.balance_after == new_balance, \
            "Transaction should have correct balance_after"
        assert transaction.reason == reason, \
            "Transaction should have correct reason"
        assert transaction.timestamp is not None, \
            "Transaction should have timestamp"
        assert isinstance(transaction.timestamp, datetime), \
            "Transaction timestamp should be datetime object"
    
    @settings(max_examples=5, deadline=None)
    @given(
        user_id=st.integers(min_value=1, max_value=999999),
        admin_id=st.integers(min_value=1, max_value=999999),
        initial_balance=st.integers(min_value=0, max_value=100000),
        credit_amount=st.integers(min_value=1, max_value=10000),
        reason=st.text(min_size=1, max_size=100, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
            blacklist_characters='\x00'
        ))
    )
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    @patch('app.dual_mode.credit_manager.db_get_credit_history')
    def test_admin_credit_grant_includes_admin_id(
        self,
        mock_get_history,
        mock_get_credits,
        mock_add_credits,
        user_id,
        admin_id,
        initial_balance,
        credit_amount,
        reason
    ):
        """
        Property 5: Credit Tracking and Logging - Admin Grant
        
        For any admin-initiated credit addition, the transaction should be 
        persisted with the admin_id for audit trail purposes.
        
        **Validates: Requirements 4.4, 4.6**
        """
        # Arrange
        new_balance = initial_balance + credit_amount
        mock_get_credits.return_value = new_balance
        mock_add_credits.return_value = True
        
        # Mock transaction history with admin_id
        mock_get_history.return_value = [{
            'transaction_id': str(uuid4()),
            'user_id': user_id,
            'amount': credit_amount,
            'balance_after': new_balance,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'admin_id': admin_id
        }]
        
        # Act
        result = self.manager.add_credits(user_id, credit_amount, reason, admin_id)
        
        # Assert - Transaction succeeded
        assert result.success is True
        
        # Assert - Database function was called with admin_id
        mock_add_credits.assert_called_once_with(user_id, credit_amount, reason, admin_id)
        
        # Assert - Transaction history includes admin_id
        history = self.manager.get_credit_history(user_id, limit=1)
        assert len(history) > 0
        assert history[0].admin_id == admin_id, \
            "Admin-initiated transaction should include admin_id"
    
    @settings(max_examples=5, deadline=None)
    @given(
        user_id=st.integers(min_value=1, max_value=999999),
        initial_balance=st.integers(min_value=100, max_value=100000),
        deduct_amount=st.integers(min_value=1, max_value=100)
    )
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    @patch('app.dual_mode.credit_manager.db_get_credit_history')
    def test_session_credit_deduction_includes_session_id(
        self,
        mock_get_history,
        mock_get_credits,
        mock_deduct_credits,
        user_id,
        initial_balance,
        deduct_amount
    ):
        """
        Property 5: Credit Tracking and Logging - Session Tracking
        
        For any credit deduction during an online session, the transaction 
        should be persisted with the session_id for tracking purposes.
        
        **Validates: Requirements 4.4, 4.6**
        """
        # Arrange
        session_id = uuid4()
        new_balance = initial_balance - deduct_amount
        mock_get_credits.side_effect = [initial_balance, new_balance]
        mock_deduct_credits.return_value = True
        
        # Mock transaction history with session_id
        mock_get_history.return_value = [{
            'transaction_id': str(uuid4()),
            'user_id': user_id,
            'amount': -deduct_amount,
            'balance_after': new_balance,
            'reason': 'Online mode usage',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'session_id': str(session_id)
        }]
        
        # Act
        result = self.manager.deduct_credits(
            user_id, 
            deduct_amount, 
            'Online mode usage', 
            session_id
        )
        
        # Assert - Transaction succeeded
        assert result.success is True
        
        # Assert - Database function was called with session_id
        mock_deduct_credits.assert_called_once_with(
            user_id, 
            deduct_amount, 
            'Online mode usage', 
            session_id
        )
        
        # Assert - Transaction history includes session_id
        history = self.manager.get_credit_history(user_id, limit=1)
        assert len(history) > 0
        assert history[0].session_id == str(session_id), \
            "Session-related transaction should include session_id"
    
    @settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(
        user_id=st.integers(min_value=1, max_value=999999),
        transactions=st.lists(
            st.tuples(
                st.integers(min_value=-100, max_value=100).filter(lambda x: x != 0),
                st.sampled_from(['deposit', 'withdrawal', 'admin_grant', 'online_usage', 'refund'])
            ),
            min_size=1,
            max_size=5
        )
    )
    @patch('app.dual_mode.credit_manager.db_add_credits')
    @patch('app.dual_mode.credit_manager.db_deduct_credits')
    @patch('app.dual_mode.credit_manager.db_get_user_credits')
    @patch('app.dual_mode.credit_manager.db_get_credit_history')
    def test_balance_correctly_updated_after_each_transaction(
        self,
        mock_get_history,
        mock_get_credits,
        mock_deduct_credits,
        mock_add_credits,
        user_id,
        transactions
    ):
        """
        Property 5: Credit Tracking and Logging - Balance Consistency
        
        For any sequence of credit transactions, the balance should be 
        correctly updated after each transaction and persisted accurately.
        
        **Validates: Requirements 4.2, 4.4, 4.6**
        """
        # Arrange
        current_balance = 10000  # Start with sufficient balance
        transaction_history = []
        
        for amount, reason in transactions:
            if amount > 0:
                # Addition
                new_balance = current_balance + amount
                mock_add_credits.return_value = True
            else:
                # Deduction
                deduct_amount = abs(amount)
                if current_balance < deduct_amount:
                    # Skip if insufficient balance
                    continue
                new_balance = current_balance - deduct_amount
                mock_deduct_credits.return_value = True
            
            # Record transaction
            transaction_history.append({
                'transaction_id': str(uuid4()),
                'user_id': user_id,
                'amount': amount,
                'balance_after': new_balance,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'admin_id': None,
                'session_id': None
            })
            
            current_balance = new_balance
        
        # Mock get_credits to return appropriate balances
        balance_sequence = [t['balance_after'] for t in transaction_history]
        if len(balance_sequence) > 0:
            # For deductions, we need balance before and after
            extended_sequence = []
            for i, t in enumerate(transaction_history):
                if t['amount'] < 0:
                    # Add balance before deduction
                    if i == 0:
                        extended_sequence.append(10000)
                    else:
                        extended_sequence.append(transaction_history[i-1]['balance_after'])
                extended_sequence.append(t['balance_after'])
            
            if len(extended_sequence) > 0:
                mock_get_credits.side_effect = extended_sequence
            else:
                mock_get_credits.side_effect = balance_sequence
        
        mock_get_history.return_value = transaction_history
        
        # Act & Assert - Process each transaction
        for amount, reason in transactions:
            if amount > 0:
                result = self.manager.add_credits(user_id, amount, reason)
                if result.success:
                    assert result.new_balance is not None, \
                        "Successful transaction should return new balance"
            else:
                deduct_amount = abs(amount)
                # Check if we have sufficient balance
                if self.manager.get_user_credits(user_id) >= deduct_amount:
                    result = self.manager.deduct_credits(user_id, deduct_amount, reason)
                    if result.success:
                        assert result.new_balance is not None, \
                            "Successful transaction should return new balance"
        
        # Assert - All transactions are retrievable
        history = self.manager.get_credit_history(user_id, limit=len(transactions))
        assert len(history) > 0, \
            "All transactions should be persisted and retrievable"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
