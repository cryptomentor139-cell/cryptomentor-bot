"""
OpenClaw Per-User Credit System
Manages individual user credit balances allocated from OpenRouter
"""

import logging
from typing import Tuple, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


def get_user_credits(db, user_id: int) -> Decimal:
    """
    Get user's current credit balance
    
    Args:
        db: Database instance
        user_id: Telegram user ID
        
    Returns:
        User's credit balance as Decimal
    """
    try:
        cursor = db.cursor()
        
        # Ensure user exists in credits table
        cursor.execute("""
            INSERT INTO openclaw_user_credits (user_id, credits, total_allocated, total_used)
            VALUES (%s, 0, 0, 0)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id,))
        db.commit()
        
        # Get balance
        cursor.execute("""
            SELECT credits FROM openclaw_user_credits WHERE user_id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return Decimal(str(result[0]))
        return Decimal('0')
        
    except Exception as e:
        logger.error(f"Error getting user credits: {e}")
        return Decimal('0')


def deduct_credits(
    db,
    user_id: int,
    amount: Decimal,
    assistant_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    message_id: Optional[str] = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    model_used: str = 'openai/gpt-4.1'
) -> Tuple[bool, Decimal, str]:
    """
    Deduct credits from user's balance
    
    Args:
        db: Database instance
        user_id: Telegram user ID
        amount: Amount to deduct (in USD)
        assistant_id: Optional assistant ID
        conversation_id: Optional conversation ID
        message_id: Optional message ID
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model_used: Model name
        
    Returns:
        Tuple of (success, new_balance, message)
    """
    try:
        cursor = db.cursor()
        
        # Get current balance
        cursor.execute("""
            SELECT credits FROM openclaw_user_credits WHERE user_id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            cursor.close()
            return False, Decimal('0'), "User not found in credit system"
        
        balance_before = Decimal(str(result[0]))
        
        # Check if sufficient balance
        if balance_before < amount:
            cursor.close()
            return False, balance_before, f"Insufficient credits. Need ${amount:.4f}, have ${balance_before:.4f}"
        
        # Deduct credits
        cursor.execute("""
            UPDATE openclaw_user_credits
            SET credits = credits - %s,
                total_used = total_used + %s
            WHERE user_id = %s
        """, (float(amount), float(amount), user_id))
        
        balance_after = balance_before - amount
        
        # Log usage
        cursor.execute("""
            INSERT INTO openclaw_credit_usage (
                user_id, assistant_id, conversation_id, message_id,
                credits_used, input_tokens, output_tokens, model_used,
                balance_before, balance_after
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, assistant_id, conversation_id, message_id,
            float(amount), input_tokens, output_tokens, model_used,
            float(balance_before), float(balance_after)
        ))
        
        db.commit()
        cursor.close()
        
        logger.info(f"Deducted ${amount:.4f} from user {user_id}. New balance: ${balance_after:.4f}")
        
        return True, balance_after, "Credits deducted successfully"
        
    except Exception as e:
        logger.error(f"Error deducting credits: {e}")
        db.rollback()
        return False, Decimal('0'), f"Error: {str(e)}"


def add_credits(
    db,
    user_id: int,
    amount: Decimal,
    admin_id: int,
    reason: str = 'Manual allocation'
) -> Tuple[bool, Decimal, str]:
    """
    Add credits to user's balance (admin only)
    
    Args:
        db: Database instance
        user_id: Telegram user ID
        amount: Amount to add (in USD)
        admin_id: Admin user ID
        reason: Reason for allocation
        
    Returns:
        Tuple of (success, new_balance, message)
    """
    try:
        cursor = db.cursor()
        
        # Ensure user exists
        cursor.execute("""
            INSERT INTO openclaw_user_credits (user_id, credits, total_allocated, total_used)
            VALUES (%s, 0, 0, 0)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id,))
        
        # Get current balance
        cursor.execute("""
            SELECT credits FROM openclaw_user_credits WHERE user_id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        balance_before = Decimal(str(result[0])) if result else Decimal('0')
        
        # Add credits
        cursor.execute("""
            UPDATE openclaw_user_credits
            SET credits = credits + %s,
                total_allocated = total_allocated + %s
            WHERE user_id = %s
        """, (float(amount), float(amount), user_id))
        
        balance_after = balance_before + amount
        
        db.commit()
        cursor.close()
        
        logger.info(f"Added ${amount:.4f} to user {user_id} by admin {admin_id}. New balance: ${balance_after:.4f}")
        
        return True, balance_after, "Credits added successfully"
        
    except Exception as e:
        logger.error(f"Error adding credits: {e}")
        db.rollback()
        return False, Decimal('0'), f"Error: {str(e)}"


def get_total_allocated(db) -> Decimal:
    """
    Get total credits allocated to all users
    
    Args:
        db: Database instance
        
    Returns:
        Total allocated credits as Decimal
    """
    try:
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT COALESCE(SUM(credits), 0) as total
            FROM openclaw_user_credits
        """)
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return Decimal(str(result[0]))
        return Decimal('0')
        
    except Exception as e:
        logger.error(f"Error getting total allocated: {e}")
        return Decimal('0')


def check_allocation_limit(db, amount: Decimal, openrouter_balance: Decimal) -> Tuple[bool, str]:
    """
    Check if allocation would exceed OpenRouter balance
    
    Args:
        db: Database instance
        amount: Amount to allocate
        openrouter_balance: Current OpenRouter balance
        
    Returns:
        Tuple of (can_allocate, message)
    """
    try:
        total_allocated = get_total_allocated(db)
        new_total = total_allocated + amount
        
        if new_total > openrouter_balance:
            available = openrouter_balance - total_allocated
            return False, (
                f"Cannot allocate ${amount:.2f}. "
                f"Would exceed OpenRouter balance by ${new_total - openrouter_balance:.2f}. "
                f"Available: ${available:.2f}"
            )
        
        return True, f"OK. After allocation: ${new_total:.2f} / ${openrouter_balance:.2f}"
        
    except Exception as e:
        logger.error(f"Error checking allocation limit: {e}")
        return False, f"Error: {str(e)}"

