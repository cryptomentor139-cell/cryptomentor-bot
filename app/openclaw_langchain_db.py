"""
OpenClaw LangChain Database Layer
Unified database management using SQLAlchemy
"""

import os
import logging
from typing import Optional, Dict, Any
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from langchain_community.chat_message_histories import SQLChatMessageHistory

logger = logging.getLogger(__name__)


class OpenClawDatabase:
    """
    Unified database layer for OpenClaw
    Handles both SQLite (local/Railway) and PostgreSQL (production)
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database (default: from env or cryptomentor.db)
        """
        # Determine database URL
        database_url = os.getenv('DATABASE_URL')
        
        if database_url and database_url.startswith('postgres'):
            # PostgreSQL (Railway production)
            # Fix postgres:// to postgresql://
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            self.connection_string = database_url
            self.db_type = 'postgresql'
            logger.info("Using PostgreSQL database")
        else:
            # SQLite (local or Railway with volume)
            if db_path is None:
                db_path = os.getenv('DATABASE_PATH', 'cryptomentor.db')
            self.connection_string = f"sqlite:///{db_path}"
            self.db_type = 'sqlite'
            logger.info(f"Using SQLite database: {db_path}")
        
        # Create engine with appropriate settings
        if self.db_type == 'sqlite':
            self.engine = create_engine(
                self.connection_string,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            self.engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,
                echo=False
            )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info("OpenClaw database initialized successfully")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def get_user_history(self, user_id: int) -> SQLChatMessageHistory:
        """
        Get conversation history for user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            SQLChatMessageHistory instance
        """
        return SQLChatMessageHistory(
            session_id=f"openclaw_user_{user_id}",
            connection_string=self.connection_string,
            table_name="openclaw_chat_history"
        )
    
    def get_user_credits(self, user_id: int) -> Decimal:
        """
        Get user's current credit balance
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Credit balance as Decimal
        """
        with self.get_session() as session:
            try:
                result = session.execute(
                    text("SELECT credits FROM openclaw_user_credits WHERE user_id = :user_id"),
                    {"user_id": user_id}
                ).fetchone()
                
                if result:
                    return Decimal(str(result[0]))
                return Decimal('0')
            
            except Exception as e:
                logger.error(f"Error getting user credits: {e}")
                return Decimal('0')
    
    def add_credits(
        self,
        user_id: int,
        amount: Decimal,
        admin_id: Optional[int] = None,
        reason: str = 'Manual allocation'
    ) -> Dict[str, Any]:
        """
        Add credits to user's balance
        
        Args:
            user_id: Telegram user ID
            amount: Amount to add
            admin_id: Admin user ID (optional)
            reason: Reason for allocation
            
        Returns:
            Result dict with success status and new balance
        """
        with self.get_session() as session:
            try:
                # Ensure user exists
                session.execute(
                    text("""
                        INSERT INTO openclaw_user_credits (user_id, credits, total_allocated, total_used)
                        VALUES (:user_id, 0, 0, 0)
                        ON CONFLICT (user_id) DO NOTHING
                    """),
                    {"user_id": user_id}
                )
                
                # Get current balance
                result = session.execute(
                    text("SELECT credits FROM openclaw_user_credits WHERE user_id = :user_id"),
                    {"user_id": user_id}
                ).fetchone()
                
                balance_before = Decimal(str(result[0])) if result else Decimal('0')
                
                # Add credits
                session.execute(
                    text("""
                        UPDATE openclaw_user_credits
                        SET credits = credits + :amount,
                            total_allocated = total_allocated + :amount,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = :user_id
                    """),
                    {"user_id": user_id, "amount": float(amount)}
                )
                
                # Log allocation
                if admin_id:
                    session.execute(
                        text("""
                            INSERT INTO openclaw_credit_allocations 
                            (user_id, admin_id, amount, reason)
                            VALUES (:user_id, :admin_id, :amount, :reason)
                        """),
                        {
                            "user_id": user_id,
                            "admin_id": admin_id,
                            "amount": float(amount),
                            "reason": reason
                        }
                    )
                
                session.commit()
                
                balance_after = balance_before + amount
                
                logger.info(f"Added ${amount:.4f} to user {user_id}. New balance: ${balance_after:.4f}")
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'amount_added': float(amount),
                    'balance_before': float(balance_before),
                    'balance_after': float(balance_after)
                }
            
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding credits: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
    
    def deduct_credits(
        self,
        user_id: int,
        amount: Decimal,
        reason: str = 'OpenClaw usage'
    ) -> Dict[str, Any]:
        """
        Deduct credits from user's balance
        
        Args:
            user_id: Telegram user ID
            amount: Amount to deduct
            reason: Reason for deduction
            
        Returns:
            Result dict with success status and new balance
        """
        with self.get_session() as session:
            try:
                # Get current balance
                result = session.execute(
                    text("SELECT credits FROM openclaw_user_credits WHERE user_id = :user_id"),
                    {"user_id": user_id}
                ).fetchone()
                
                if not result:
                    return {
                        'success': False,
                        'error': 'User not found'
                    }
                
                balance_before = Decimal(str(result[0]))
                
                # Check sufficient balance
                if balance_before < amount:
                    return {
                        'success': False,
                        'error': f'Insufficient credits. Need ${amount:.4f}, have ${balance_before:.4f}'
                    }
                
                # Deduct credits
                session.execute(
                    text("""
                        UPDATE openclaw_user_credits
                        SET credits = credits - :amount,
                            total_used = total_used + :amount,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = :user_id
                    """),
                    {"user_id": user_id, "amount": float(amount)}
                )
                
                # Log usage
                session.execute(
                    text("""
                        INSERT INTO openclaw_credit_usage 
                        (user_id, credits_used, balance_before, balance_after)
                        VALUES (:user_id, :amount, :balance_before, :balance_after)
                    """),
                    {
                        "user_id": user_id,
                        "amount": float(amount),
                        "balance_before": float(balance_before),
                        "balance_after": float(balance_before - amount)
                    }
                )
                
                session.commit()
                
                balance_after = balance_before - amount
                
                logger.info(f"Deducted ${amount:.4f} from user {user_id}. New balance: ${balance_after:.4f}")
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'amount_deducted': float(amount),
                    'balance_before': float(balance_before),
                    'balance_after': float(balance_after)
                }
            
            except Exception as e:
                session.rollback()
                logger.error(f"Error deducting credits: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system-wide statistics
        
        Returns:
            Dict with system stats
        """
        with self.get_session() as session:
            try:
                result = session.execute(
                    text("""
                        SELECT 
                            COUNT(*) as user_count,
                            COALESCE(SUM(credits), 0) as total_credits,
                            COALESCE(SUM(total_allocated), 0) as total_allocated,
                            COALESCE(SUM(total_used), 0) as total_used
                        FROM openclaw_user_credits
                    """)
                ).fetchone()
                
                if result:
                    return {
                        'user_count': result[0],
                        'total_credits': float(result[1]),
                        'total_allocated': float(result[2]),
                        'total_used': float(result[3])
                    }
                
                return {
                    'user_count': 0,
                    'total_credits': 0.0,
                    'total_allocated': 0.0,
                    'total_used': 0.0
                }
            
            except Exception as e:
                logger.error(f"Error getting system stats: {e}")
                return {
                    'user_count': 0,
                    'total_credits': 0.0,
                    'total_allocated': 0.0,
                    'total_used': 0.0
                }
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()
        logger.info("Database connection closed")


# Global database instance
_db_instance: Optional[OpenClawDatabase] = None


def get_openclaw_db() -> OpenClawDatabase:
    """
    Get global OpenClaw database instance
    
    Returns:
        OpenClawDatabase instance
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = OpenClawDatabase()
    
    return _db_instance
