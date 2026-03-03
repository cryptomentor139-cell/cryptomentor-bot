"""
ModeStateManager - Core mode state management for dual-mode system.

This module provides the ModeStateManager class responsible for:
- Tracking user mode state (offline/online)
- Managing mode transitions with validation
- Maintaining mode history for audit trail
- Preserving state during transitions

Feature: dual-mode-offline-online
Task: 2.1
Requirements: 1.1, 1.2, 1.7, 1.8
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
import time

# Import database functions
from app.dual_mode_db import (
    get_user_mode as db_get_user_mode,
    set_user_mode as db_set_user_mode,
    get_offline_state as db_get_offline_state,
    get_mode_history as db_get_mode_history,
    log_mode_transition,
    has_sufficient_credits,
    get_active_session
)


@dataclass
class UserModeState:
    """User mode state data model."""
    user_id: int
    current_mode: str  # 'offline' | 'online'
    previous_mode: Optional[str]
    last_transition: datetime
    transition_count: int
    offline_state: Optional[Dict]
    online_session_id: Optional[str]


@dataclass
class ModeTransition:
    """Mode transition record."""
    user_id: int
    from_mode: Optional[str]
    to_mode: str
    success: bool
    error_message: Optional[str]
    duration_ms: Optional[int]
    timestamp: datetime


@dataclass
class TransitionResult:
    """Result of a mode transition operation."""
    success: bool
    message: str
    error: Optional[str] = None
    session_id: Optional[UUID] = None
    duration_ms: Optional[int] = None


class ModeStateManager:
    """
    Manages user mode state and transitions for dual-mode system.
    
    Responsibilities:
    - Track user mode (offline/online)
    - Handle mode transitions with validation
    - Preserve state during transitions
    - Maintain audit trail
    """
    
    # Minimum credits required for online mode
    MINIMUM_CREDITS_REQUIRED = 10
    
    def __init__(self):
        """Initialize ModeStateManager."""
        pass
    
    def get_user_mode(self, user_id: int) -> str:
        """
        Get user's current mode.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Current mode: 'offline' or 'online'
            
        Requirements: 1.7
        """
        return db_get_user_mode(user_id)
    
    def set_user_mode(self, user_id: int, mode: str, 
                      offline_state: Optional[Dict] = None,
                      session_id: Optional[UUID] = None) -> bool:
        """
        Set user's current mode.
        
        Args:
            user_id: Telegram user ID
            mode: New mode ('offline' or 'online')
            offline_state: Optional offline context to preserve
            session_id: Optional online session ID
            
        Returns:
            True if successful, False otherwise
            
        Requirements: 1.7, 1.8
        """
        if mode not in ['offline', 'online']:
            print(f"Invalid mode: {mode}")
            return False
        
        return db_set_user_mode(user_id, mode, offline_state, session_id)
    
    def is_offline_mode(self, user_id: int) -> bool:
        """
        Check if user is in offline mode.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is in offline mode
            
        Requirements: 1.1
        """
        return self.get_user_mode(user_id) == 'offline'
    
    def is_online_mode(self, user_id: int) -> bool:
        """
        Check if user is in online mode.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is in online mode
            
        Requirements: 1.2
        """
        return self.get_user_mode(user_id) == 'online'
    
    def transition_mode(self, user_id: int, from_mode: str, to_mode: str) -> TransitionResult:
        """
        Transition user from one mode to another with validation.
        
        This method handles:
        - Credit validation for online mode
        - State preservation during transitions
        - Graceful session cleanup
        - Audit logging
        - Performance tracking
        
        Args:
            user_id: Telegram user ID
            from_mode: Current mode ('offline' or 'online')
            to_mode: Target mode ('offline' or 'online')
            
        Returns:
            TransitionResult with success status and details
            
        Requirements: 1.3, 1.4, 1.5, 1.6, 9.1, 9.2, 9.4, 9.5, 9.6
        """
        start_time = time.time()
        
        # Validate modes
        if to_mode not in ['offline', 'online']:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Invalid target mode: {to_mode}"
            log_mode_transition(user_id, from_mode, to_mode, False, error_msg, duration_ms)
            return TransitionResult(
                success=False,
                message="Invalid mode specified",
                error=error_msg,
                duration_ms=duration_ms
            )
        
        # Verify current mode matches from_mode
        current_mode = self.get_user_mode(user_id)
        if current_mode != from_mode:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Mode mismatch: expected {from_mode}, got {current_mode}"
            log_mode_transition(user_id, from_mode, to_mode, False, error_msg, duration_ms)
            return TransitionResult(
                success=False,
                message="Mode state mismatch",
                error=error_msg,
                duration_ms=duration_ms
            )
        
        # If transitioning to online mode, validate credits
        if to_mode == 'online':
            if not has_sufficient_credits(user_id, self.MINIMUM_CREDITS_REQUIRED):
                duration_ms = int((time.time() - start_time) * 1000)
                error_msg = f"Insufficient credits (minimum: {self.MINIMUM_CREDITS_REQUIRED})"
                log_mode_transition(user_id, from_mode, to_mode, False, error_msg, duration_ms)
                return TransitionResult(
                    success=False,
                    message="Insufficient Automaton credits. Use /credits to check balance and learn how to obtain credits.",
                    error=error_msg,
                    duration_ms=duration_ms
                )
        
        # Preserve offline state if transitioning from offline
        offline_state = None
        if from_mode == 'offline':
            offline_state = db_get_offline_state(user_id)
        
        # Close active session if transitioning from online
        session_id = None
        if from_mode == 'online':
            active_session = get_active_session(user_id)
            if active_session:
                from app.dual_mode_db import close_session
                close_session(UUID(active_session['session_id']))
        
        # Perform the transition
        success = self.set_user_mode(user_id, to_mode, offline_state, session_id)
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log the transition
        if success:
            log_mode_transition(user_id, from_mode, to_mode, True, None, duration_ms)
            return TransitionResult(
                success=True,
                message=f"Successfully switched to {to_mode} mode",
                session_id=session_id,
                duration_ms=duration_ms
            )
        else:
            error_msg = "Failed to update mode state in database"
            log_mode_transition(user_id, from_mode, to_mode, False, error_msg, duration_ms)
            return TransitionResult(
                success=False,
                message="Mode transition failed. Please try again.",
                error=error_msg,
                duration_ms=duration_ms
            )
    
    def get_mode_history(self, user_id: int, limit: int = 10) -> List[ModeTransition]:
        """
        Get user's mode transition history for audit trail.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of transitions to return (default: 10)
            
        Returns:
            List of ModeTransition records
            
        Requirements: 1.8
        """
        history_data = db_get_mode_history(user_id, limit)
        
        transitions = []
        for record in history_data:
            transitions.append(ModeTransition(
                user_id=record['user_id'],
                from_mode=record.get('from_mode'),
                to_mode=record['to_mode'],
                success=record['success'],
                error_message=record.get('error_message'),
                duration_ms=record.get('duration_ms'),
                timestamp=datetime.fromisoformat(record['timestamp'])
            ))
        
        return transitions
    
    def get_user_state(self, user_id: int) -> Optional[UserModeState]:
        """
        Get complete user mode state.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            UserModeState object or None if not found
        """
        from app.dual_mode_db import supabase
        
        try:
            result = supabase.table('user_mode_states').select('*').eq('user_id', user_id).execute()
            
            if not result.data or len(result.data) == 0:
                return None
            
            data = result.data[0]
            
            return UserModeState(
                user_id=data['user_id'],
                current_mode=data['current_mode'],
                previous_mode=data.get('previous_mode'),
                last_transition=datetime.fromisoformat(data['last_transition']),
                transition_count=data['transition_count'],
                offline_state=data.get('offline_state'),
                online_session_id=data.get('online_session_id')
            )
        except Exception as e:
            print(f"Error getting user state: {e}")
            return None
    
    def validate_mode_access(self, user_id: int, required_mode: str) -> bool:
        """
        Validate if user can access a specific mode.
        
        Args:
            user_id: Telegram user ID
            required_mode: Mode to validate ('offline' or 'online')
            
        Returns:
            True if user can access the mode, False otherwise
        """
        if required_mode == 'offline':
            # Offline mode is always accessible
            return True
        
        if required_mode == 'online':
            # Online mode requires sufficient credits
            return has_sufficient_credits(user_id, self.MINIMUM_CREDITS_REQUIRED)
        
        return False
