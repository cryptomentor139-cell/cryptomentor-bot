"""
Credit Manager for Automaton Credits.

This module provides credit management operations with atomic transactions,
validation, and audit logging for the dual-mode offline-online system.

Feature: dual-mode-offline-online
Requirements: 4.1, 4.2, 4.4, 4.6, 13.3, 13.5
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Import database functions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dual_mode_db import (
    get_user_credits as db_get_user_credits,
    add_credits as db_add_credits,
    deduct_credits as db_deduct_credits,
    get_credit_history as db_get_credit_history,
    has_sufficient_credits as db_has_sufficient_credits
)


@dataclass
class CreditResult:
    """Result of a credit operation."""
    success: bool
    new_balance: Optional[int] = None
    error: Optional[str] = None
    transaction_id: Optional[str] = None


@dataclass
class CreditTransaction:
    """Credit transaction record."""
    transaction_id: str
    user_id: int
    amount: int
    balance_after: int
    reason: str
    timestamp: datetime
    admin_id: Optional[int] = None
    session_id: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of admin balance validation."""
    valid: bool
    admin_balance: Optional[int] = None
    error: Optional[str] = None


class CreditManager:
    """
    Manages Automaton credit operations with atomic transactions.
    
    This class provides:
    - Credit balance queries
    - Credit additions and deductions with atomic transactions
    - Credit transaction history
    - Admin balance validation for Automaton API
    """
    
    def __init__(self):
        """Initialize CreditManager."""
        pass
    
    def get_user_credits(self, user_id: int) -> int:
        """
        Get user's current Automaton credit balance.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Current credit balance (0 if no transactions exist)
            
        Requirements: 4.1, 4.2
        """
        try:
            return db_get_user_credits(user_id)
        except Exception as e:
            print(f"Error getting user credits: {e}")
            return 0
    
    def has_sufficient_credits(self, user_id: int, required: int) -> bool:
        """
        Check if user has sufficient credits for an operation.
        
        Args:
            user_id: Telegram user ID
            required: Required credit amount
            
        Returns:
            True if user has enough credits, False otherwise
            
        Requirements: 4.1, 4.2
        """
        try:
            return db_has_sufficient_credits(user_id, required)
        except Exception as e:
            print(f"Error checking sufficient credits: {e}")
            return False
    
    def deduct_credits(self, user_id: int, amount: int, reason: str, 
                      session_id: Optional[UUID] = None) -> CreditResult:
        """
        Deduct credits from user account with atomic transaction.
        
        This operation is atomic - either the full deduction succeeds or
        nothing changes. Validates sufficient balance before deduction.
        
        Args:
            user_id: Telegram user ID
            amount: Credits to deduct (must be positive)
            reason: Transaction reason for audit trail
            session_id: Optional related session ID
            
        Returns:
            CreditResult with success status and new balance
            
        Requirements: 4.4, 4.6
        """
        try:
            # Validate amount
            if amount <= 0:
                return CreditResult(
                    success=False,
                    error="Amount must be positive"
                )
            
            # Check sufficient balance
            current_balance = self.get_user_credits(user_id)
            if current_balance < amount:
                return CreditResult(
                    success=False,
                    error=f"Insufficient credits. Current: {current_balance}, Required: {amount}"
                )
            
            # Perform atomic deduction
            success = db_deduct_credits(user_id, amount, reason, session_id)
            
            if success:
                new_balance = self.get_user_credits(user_id)
                return CreditResult(
                    success=True,
                    new_balance=new_balance
                )
            else:
                return CreditResult(
                    success=False,
                    error="Failed to deduct credits"
                )
                
        except Exception as e:
            print(f"Error deducting credits: {e}")
            return CreditResult(
                success=False,
                error=str(e)
            )
    
    def add_credits(self, user_id: int, amount: int, reason: str, 
                   admin_id: Optional[int] = None) -> CreditResult:
        """
        Add credits to user account with atomic transaction.
        
        This operation is atomic - either the full addition succeeds or
        nothing changes. Logs transaction with admin ID if provided.
        
        Args:
            user_id: Telegram user ID
            amount: Credits to add (must be positive)
            reason: Transaction reason for audit trail
            admin_id: Optional admin who initiated transaction
            
        Returns:
            CreditResult with success status and new balance
            
        Requirements: 4.4, 4.6
        """
        try:
            # Validate amount
            if amount <= 0:
                return CreditResult(
                    success=False,
                    error="Amount must be positive"
                )
            
            # Perform atomic addition
            success = db_add_credits(user_id, amount, reason, admin_id)
            
            if success:
                new_balance = self.get_user_credits(user_id)
                return CreditResult(
                    success=True,
                    new_balance=new_balance
                )
            else:
                return CreditResult(
                    success=False,
                    error="Failed to add credits"
                )
                
        except Exception as e:
            print(f"Error adding credits: {e}")
            return CreditResult(
                success=False,
                error=str(e)
            )
    
    def get_credit_history(self, user_id: int, limit: int = 20) -> List[CreditTransaction]:
        """
        Get user's credit transaction history.
        
        Returns transactions in reverse chronological order (newest first).
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of transactions to return (default: 20)
            
        Returns:
            List of CreditTransaction objects
            
        Requirements: 4.4, 4.6
        """
        try:
            history = db_get_credit_history(user_id, limit)
            
            # Convert to CreditTransaction objects
            transactions = []
            for record in history:
                transaction = CreditTransaction(
                    transaction_id=record.get('transaction_id', ''),
                    user_id=record['user_id'],
                    amount=record['amount'],
                    balance_after=record['balance_after'],
                    reason=record['reason'],
                    timestamp=datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')),
                    admin_id=record.get('admin_id'),
                    session_id=record.get('session_id')
                )
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error getting credit history: {e}")
            return []
    
    def validate_admin_balance(self, admin_id: int, amount: int) -> ValidationResult:
        """
        Validate that admin has sufficient balance in Automaton API.
        
        This checks the admin's Automaton API balance to ensure they have
        enough credits to grant to users. This prevents over-allocation.
        
        Args:
            admin_id: Admin user ID
            amount: Amount to validate
            
        Returns:
            ValidationResult with validation status and admin balance
            
        Requirements: 13.3, 13.5
        """
        try:
            # For now, we'll use the same credit system for admin
            # In production, this would call Automaton API to check admin balance
            admin_balance = self.get_user_credits(admin_id)
            
            if admin_balance < amount:
                return ValidationResult(
                    valid=False,
                    admin_balance=admin_balance,
                    error=f"Insufficient admin balance. Available: {admin_balance}, Requested: {amount}"
                )
            
            return ValidationResult(
                valid=True,
                admin_balance=admin_balance
            )
            
        except Exception as e:
            print(f"Error validating admin balance: {e}")
            return ValidationResult(
                valid=False,
                error=str(e)
            )
