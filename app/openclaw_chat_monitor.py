"""
OpenClaw Chat Monitor
Logs all chat attempts for admin review and credit management
"""

import logging
from datetime import datetime
from typing import Optional
from app.openclaw_db_helper import get_openclaw_db_connection

logger = logging.getLogger(__name__)


class OpenClawChatMonitor:
    """
    Monitor all OpenClaw chat attempts
    
    Tracks:
    - Users trying to use OpenClaw without credits
    - All OpenClaw usage (successful and failed)
    - User questions/requests for admin review
    """
    
    @staticmethod
    def log_chat_attempt(
        user_id: int,
        username: Optional[str],
        message: str,
        has_credits: bool,
        balance: float = 0.0,
        success: bool = False
    ):
        """
        Log chat attempt to database
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            message: User's message/question
            has_credits: Whether user has credits
            balance: Current balance
            success: Whether request was successful
        """
        try:
            db = get_openclaw_db_connection()
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT INTO openclaw_chat_monitor (
                    user_id, username, message, has_credits,
                    balance, success, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                user_id,
                username,
                message[:500],  # Limit message length
                has_credits,
                balance,
                success
            ))
            
            db.commit()
            
            # Log to file for admin review
            status = "SUCCESS" if success else ("NO_CREDITS" if not has_credits else "FAILED")
            logger.info(
                f"OpenClaw Chat [{status}] - "
                f"User: {user_id} (@{username}) - "
                f"Balance: ${balance:.2f} - "
                f"Message: {message[:100]}"
            )
            
        except Exception as e:
            logger.error(f"Error logging chat attempt: {e}")
    
    @staticmethod
    def get_recent_attempts(limit: int = 50):
        """
        Get recent chat attempts for admin review
        
        Args:
            limit: Number of attempts to retrieve
            
        Returns:
            List of recent attempts
        """
        try:
            db = get_openclaw_db_connection()
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT 
                    user_id, username, message, has_credits,
                    balance, success, created_at
                FROM openclaw_chat_monitor
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error getting recent attempts: {e}")
            return []
    
    @staticmethod
    def get_users_without_credits(limit: int = 20):
        """
        Get users who tried to use OpenClaw without credits
        
        Args:
            limit: Number of users to retrieve
            
        Returns:
            List of users without credits
        """
        try:
            db = get_openclaw_db_connection()
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT 
                    user_id,
                    username,
                    COUNT(*) as attempt_count,
                    MAX(created_at) as last_attempt,
                    MAX(message) as last_message
                FROM openclaw_chat_monitor
                WHERE has_credits = FALSE
                GROUP BY user_id, username
                ORDER BY last_attempt DESC
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error getting users without credits: {e}")
            return []


# Add table to migration if not exists
MONITOR_TABLE_SQL = """
-- OpenClaw chat monitoring table
CREATE TABLE IF NOT EXISTS openclaw_chat_monitor (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username VARCHAR(255),
    message TEXT,
    has_credits BOOLEAN DEFAULT FALSE,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    success BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_openclaw_monitor_user ON openclaw_chat_monitor(user_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_monitor_credits ON openclaw_chat_monitor(has_credits);
CREATE INDEX IF NOT EXISTS idx_openclaw_monitor_created ON openclaw_chat_monitor(created_at);

COMMENT ON TABLE openclaw_chat_monitor IS 'Logs all OpenClaw chat attempts for admin monitoring';
"""
