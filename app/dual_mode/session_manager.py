"""
SessionManager for dual-mode offline-online system.

This module manages isolated AI agent sessions for online mode users.
Each session represents a window of interaction between a user and their
isolated AI agent, tracking activity, message count, and credit usage.

Feature: dual-mode-offline-online
Requirements: 3.1, 9.2
"""

from typing import Optional
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime

# Import database functions
from app.dual_mode_db import (
    create_session as db_create_session,
    get_active_session as db_get_active_session,
    update_session_activity as db_update_session_activity,
    close_session as db_close_session
)


@dataclass
class Session:
    """
    Represents an online mode session.
    
    Attributes:
        session_id: Unique session identifier
        user_id: Telegram user ID
        agent_id: Isolated AI agent identifier
        created_at: Session creation timestamp
        last_activity: Last user interaction timestamp
        message_count: Total messages in this session
        credits_used: Automaton credits consumed
        status: Session status (active, closed, expired)
    """
    session_id: str
    user_id: int
    agent_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int
    credits_used: int
    status: str


class SessionManager:
    """
    Manages isolated AI agent sessions for online mode.
    
    Responsibilities:
    - Create new sessions with unique session IDs
    - Retrieve active sessions for users
    - Track session activity and credit usage
    - Close sessions gracefully
    
    Each user can have one active session at a time. When a user switches
    to online mode, a new session is created. When they switch back to
    offline mode or close the session, it is marked as closed.
    """
    
    def __init__(self):
        """Initialize the SessionManager."""
        pass
    
    def create_session(self, user_id: int, agent_id: str) -> Optional[Session]:
        """
        Create a new online session for a user.
        
        This method creates a new session in the database with a unique
        session ID. The session is marked as 'active' and tracks the
        user's interactions with their isolated AI agent.
        
        Args:
            user_id: Telegram user ID
            agent_id: Isolated AI agent identifier
            
        Returns:
            Session object if successful, None otherwise
            
        Requirements: 3.1, 9.2
        """
        try:
            # Create session in database
            session_id = db_create_session(user_id, agent_id)
            
            if session_id is None:
                print(f"Failed to create session for user {user_id}")
                return None
            
            # Return Session object
            return Session(
                session_id=str(session_id),
                user_id=user_id,
                agent_id=agent_id,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                message_count=0,
                credits_used=0,
                status='active'
            )
        except Exception as e:
            print(f"Error creating session: {e}")
            return None

    
    def get_session(self, user_id: int) -> Optional[Session]:
        """
        Get the active session for a user.
        
        This method retrieves the user's currently active session from
        the database. If no active session exists, returns None.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Session object if active session exists, None otherwise
            
        Requirements: 3.1
        """
        try:
            # Get active session from database
            session_data = db_get_active_session(user_id)
            
            if session_data is None:
                return None
            
            # Convert database record to Session object
            return Session(
                session_id=session_data['session_id'],
                user_id=session_data['user_id'],
                agent_id=session_data['agent_id'],
                created_at=datetime.fromisoformat(session_data['created_at'].replace('Z', '+00:00')) 
                    if isinstance(session_data['created_at'], str) 
                    else session_data['created_at'],
                last_activity=datetime.fromisoformat(session_data['last_activity'].replace('Z', '+00:00'))
                    if isinstance(session_data['last_activity'], str)
                    else session_data['last_activity'],
                message_count=session_data['message_count'],
                credits_used=session_data['credits_used'],
                status=session_data['status']
            )
        except Exception as e:
            print(f"Error getting session: {e}")
            return None

    
    def is_session_active(self, user_id: int) -> bool:
        """
        Check if a user has an active session.
        
        This is a convenience method that checks whether the user
        currently has an active online mode session.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user has an active session, False otherwise
            
        Requirements: 3.1
        """
        try:
            session = self.get_session(user_id)
            return session is not None and session.status == 'active'
        except Exception as e:
            print(f"Error checking session status: {e}")
            return False
    
    def close_session(self, user_id: int) -> bool:
        """
        Close the active session for a user.
        
        This method gracefully closes the user's active session by
        marking it as 'closed' in the database. This should be called
        when the user switches from online mode to offline mode.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if session closed successfully, False otherwise
            
        Requirements: 9.2
        """
        try:
            # Get active session
            session = self.get_session(user_id)
            
            if session is None:
                print(f"No active session found for user {user_id}")
                return False
            
            # Close session in database
            session_id = UUID(session.session_id)
            success = db_close_session(session_id)
            
            if success:
                print(f"Session {session.session_id} closed for user {user_id}")
            else:
                print(f"Failed to close session {session.session_id} for user {user_id}")
            
            return success
        except Exception as e:
            print(f"Error closing session: {e}")
            return False

    
    def update_session_activity(self, user_id: int, credits_used: int = 0) -> bool:
        """
        Update session activity timestamp and credit usage.
        
        This method should be called after each user interaction in
        online mode to track activity and credit consumption. It updates
        the last_activity timestamp, increments the message count, and
        adds to the credits_used counter.
        
        Args:
            user_id: Telegram user ID
            credits_used: Additional credits consumed (incremental)
            
        Returns:
            True if update successful, False otherwise
            
        Requirements: 3.1
        """
        try:
            # Get active session
            session = self.get_session(user_id)
            
            if session is None:
                print(f"No active session found for user {user_id}")
                return False
            
            # Update session activity in database
            session_id = UUID(session.session_id)
            success = db_update_session_activity(session_id, credits_used)
            
            if success:
                print(f"Session {session.session_id} activity updated for user {user_id}")
            else:
                print(f"Failed to update session {session.session_id} for user {user_id}")
            
            return success
        except Exception as e:
            print(f"Error updating session activity: {e}")
            return False
