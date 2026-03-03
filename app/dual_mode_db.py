"""
Database connection utilities for dual-mode offline-online system.

This module provides database access functions for:
- User mode state management
- Online session management
- Isolated AI agent management
- Automaton credit transactions
- Mode transition logging

Feature: dual-mode-offline-online
Requirements: 1.7, 4.4, 10.2
"""

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

import os
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from uuid import UUID
import json
from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================================
# User Mode State Functions
# ============================================================================

def get_user_mode(user_id: int) -> str:
    """
    Get user's current mode (offline or online).
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Current mode: 'offline' or 'online' (defaults to 'offline')
    """
    try:
        result = supabase.table('user_mode_states').select('current_mode').eq('user_id', user_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]['current_mode']
        
        # Default to offline if no record exists
        return 'offline'
    except Exception as e:
        print(f"Error getting user mode: {e}")
        return 'offline'


def set_user_mode(user_id: int, mode: str, offline_state: Optional[Dict] = None, 
                  session_id: Optional[UUID] = None) -> bool:
    """
    Set user's current mode and update state.
    
    Args:
        user_id: Telegram user ID
        mode: New mode ('offline' or 'online')
        offline_state: Optional offline mode context to preserve
        session_id: Optional online session ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get current mode for transition tracking
        current = supabase.table('user_mode_states').select('*').eq('user_id', user_id).execute()
        
        data = {
            'user_id': user_id,
            'current_mode': mode,
            'last_transition': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if offline_state is not None:
            data['offline_state'] = json.dumps(offline_state)
        
        if session_id is not None:
            data['online_session_id'] = str(session_id)
        
        if current.data and len(current.data) > 0:
            # Update existing record
            old_mode = current.data[0]['current_mode']
            data['previous_mode'] = old_mode
            data['transition_count'] = current.data[0]['transition_count'] + 1
            
            supabase.table('user_mode_states').update(data).eq('user_id', user_id).execute()
        else:
            # Insert new record
            data['transition_count'] = 0
            data['created_at'] = datetime.utcnow().isoformat()
            
            supabase.table('user_mode_states').insert(data).execute()
        
        return True
    except Exception as e:
        print(f"Error setting user mode: {e}")
        return False


def get_offline_state(user_id: int) -> Optional[Dict]:
    """
    Get preserved offline mode state for user.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Offline state dictionary or None
    """
    try:
        result = supabase.table('user_mode_states').select('offline_state').eq('user_id', user_id).execute()
        
        if result.data and len(result.data) > 0:
            state = result.data[0]['offline_state']
            if state:
                return json.loads(state) if isinstance(state, str) else state
        
        return None
    except Exception as e:
        print(f"Error getting offline state: {e}")
        return None


def get_mode_history(user_id: int, limit: int = 10) -> List[Dict]:
    """
    Get user's mode transition history.
    
    Args:
        user_id: Telegram user ID
        limit: Maximum number of transitions to return
        
    Returns:
        List of transition records
    """
    try:
        result = supabase.table('mode_transition_log')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('timestamp', desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting mode history: {e}")
        return []


# ============================================================================
# Online Session Functions
# ============================================================================

def create_session(user_id: int, agent_id: str) -> Optional[UUID]:
    """
    Create a new online session for user.
    
    Args:
        user_id: Telegram user ID
        agent_id: Isolated AI agent ID
        
    Returns:
        Session UUID or None if failed
    """
    try:
        data = {
            'user_id': user_id,
            'agent_id': agent_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'message_count': 0,
            'credits_used': 0,
            'status': 'active'
        }
        
        result = supabase.table('online_sessions').insert(data).execute()
        
        if result.data and len(result.data) > 0:
            return UUID(result.data[0]['session_id'])
        
        return None
    except Exception as e:
        print(f"Error creating session: {e}")
        return None


def get_active_session(user_id: int) -> Optional[Dict]:
    """
    Get user's active online session.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Session data or None
    """
    try:
        result = supabase.table('online_sessions')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('status', 'active')\
            .order('last_activity', desc=True)\
            .limit(1)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        return None
    except Exception as e:
        print(f"Error getting active session: {e}")
        return None


def update_session_activity(session_id: UUID, credits_used: int = 0) -> bool:
    """
    Update session last activity and credit usage.
    
    Args:
        session_id: Session UUID
        credits_used: Additional credits used (incremental)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get current session data
        result = supabase.table('online_sessions').select('*').eq('session_id', str(session_id)).execute()
        
        if not result.data or len(result.data) == 0:
            return False
        
        current = result.data[0]
        
        data = {
            'last_activity': datetime.utcnow().isoformat(),
            'message_count': current['message_count'] + 1,
            'credits_used': current['credits_used'] + credits_used
        }
        
        supabase.table('online_sessions').update(data).eq('session_id', str(session_id)).execute()
        
        return True
    except Exception as e:
        print(f"Error updating session activity: {e}")
        return False


def close_session(session_id: UUID) -> bool:
    """
    Close an online session.
    
    Args:
        session_id: Session UUID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        data = {
            'status': 'closed',
            'closed_at': datetime.utcnow().isoformat()
        }
        
        supabase.table('online_sessions').update(data).eq('session_id', str(session_id)).execute()
        
        return True
    except Exception as e:
        print(f"Error closing session: {e}")
        return False


# ============================================================================
# Isolated AI Agent Functions
# ============================================================================

def create_agent(user_id: int, agent_id: str, genesis_prompt: str) -> bool:
    """
    Create a new isolated AI agent for user.
    
    Args:
        user_id: Telegram user ID
        agent_id: Unique agent identifier
        genesis_prompt: Base system prompt
        
    Returns:
        True if successful, False otherwise
    """
    try:
        data = {
            'agent_id': agent_id,
            'user_id': user_id,
            'genesis_prompt': genesis_prompt,
            'conversation_history': json.dumps([]),
            'created_at': datetime.utcnow().isoformat(),
            'last_used': datetime.utcnow().isoformat(),
            'total_messages': 0,
            'status': 'active'
        }
        
        supabase.table('isolated_ai_agents').insert(data).execute()
        
        return True
    except Exception as e:
        print(f"Error creating agent: {e}")
        return False


def get_agent(user_id: int) -> Optional[Dict]:
    """
    Get user's isolated AI agent.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Agent data or None
    """
    try:
        result = supabase.table('isolated_ai_agents')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        return None
    except Exception as e:
        print(f"Error getting agent: {e}")
        return None


def update_agent_activity(agent_id: str, conversation_history: Optional[List] = None) -> bool:
    """
    Update agent last used timestamp and conversation history.
    
    Args:
        agent_id: Agent identifier
        conversation_history: Optional updated conversation history
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get current agent data
        result = supabase.table('isolated_ai_agents').select('*').eq('agent_id', agent_id).execute()
        
        if not result.data or len(result.data) == 0:
            return False
        
        current = result.data[0]
        
        data = {
            'last_used': datetime.utcnow().isoformat(),
            'total_messages': current['total_messages'] + 1
        }
        
        if conversation_history is not None:
            data['conversation_history'] = json.dumps(conversation_history)
        
        supabase.table('isolated_ai_agents').update(data).eq('agent_id', agent_id).execute()
        
        return True
    except Exception as e:
        print(f"Error updating agent activity: {e}")
        return False


def delete_agent(user_id: int) -> bool:
    """
    Mark agent as deleted (soft delete).
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        data = {
            'status': 'deleted'
        }
        
        supabase.table('isolated_ai_agents').update(data).eq('user_id', user_id).execute()
        
        return True
    except Exception as e:
        print(f"Error deleting agent: {e}")
        return False


# ============================================================================
# Automaton Credit Functions
# ============================================================================

def get_user_credits(user_id: int) -> int:
    """
    Get user's current Automaton credit balance.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Credit balance (0 if no transactions exist)
    """
    try:
        result = supabase.table('automaton_credit_transactions')\
            .select('balance_after')\
            .eq('user_id', user_id)\
            .order('timestamp', desc=True)\
            .limit(1)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]['balance_after']
        
        return 0
    except Exception as e:
        print(f"Error getting user credits: {e}")
        return 0


def add_credits(user_id: int, amount: int, reason: str, admin_id: Optional[int] = None) -> bool:
    """
    Add Automaton credits to user account.
    
    Args:
        user_id: Telegram user ID
        amount: Credits to add (positive integer)
        reason: Transaction reason
        admin_id: Optional admin who initiated transaction
        
    Returns:
        True if successful, False otherwise
    """
    try:
        current_balance = get_user_credits(user_id)
        new_balance = current_balance + amount
        
        data = {
            'user_id': user_id,
            'amount': amount,
            'balance_after': new_balance,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if admin_id is not None:
            data['admin_id'] = admin_id
        
        supabase.table('automaton_credit_transactions').insert(data).execute()
        
        return True
    except Exception as e:
        print(f"Error adding credits: {e}")
        return False


def deduct_credits(user_id: int, amount: int, reason: str, session_id: Optional[UUID] = None) -> bool:
    """
    Deduct Automaton credits from user account.
    
    Args:
        user_id: Telegram user ID
        amount: Credits to deduct (positive integer)
        reason: Transaction reason
        session_id: Optional related session
        
    Returns:
        True if successful, False otherwise
    """
    try:
        current_balance = get_user_credits(user_id)
        
        if current_balance < amount:
            print(f"Insufficient credits: user {user_id} has {current_balance}, needs {amount}")
            return False
        
        new_balance = current_balance - amount
        
        data = {
            'user_id': user_id,
            'amount': -amount,  # Negative for deduction
            'balance_after': new_balance,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if session_id is not None:
            data['session_id'] = str(session_id)
        
        supabase.table('automaton_credit_transactions').insert(data).execute()
        
        return True
    except Exception as e:
        print(f"Error deducting credits: {e}")
        return False


def get_credit_history(user_id: int, limit: int = 20) -> List[Dict]:
    """
    Get user's credit transaction history.
    
    Args:
        user_id: Telegram user ID
        limit: Maximum number of transactions to return
        
    Returns:
        List of transaction records
    """
    try:
        result = supabase.table('automaton_credit_transactions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('timestamp', desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting credit history: {e}")
        return []


# ============================================================================
# Mode Transition Logging
# ============================================================================

def log_mode_transition(user_id: int, from_mode: Optional[str], to_mode: str, 
                        success: bool, error_message: Optional[str] = None,
                        duration_ms: Optional[int] = None) -> bool:
    """
    Log a mode transition event.
    
    Args:
        user_id: Telegram user ID
        from_mode: Previous mode (None for first activation)
        to_mode: New mode
        success: Whether transition succeeded
        error_message: Optional error details
        duration_ms: Optional transition duration
        
    Returns:
        True if logged successfully, False otherwise
    """
    try:
        data = {
            'user_id': user_id,
            'to_mode': to_mode,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if from_mode is not None:
            data['from_mode'] = from_mode
        
        if error_message is not None:
            data['error_message'] = error_message
        
        if duration_ms is not None:
            data['duration_ms'] = duration_ms
        
        supabase.table('mode_transition_log').insert(data).execute()
        
        return True
    except Exception as e:
        print(f"Error logging mode transition: {e}")
        return False


# ============================================================================
# Statistics and Monitoring
# ============================================================================

def get_mode_statistics() -> Dict:
    """
    Get system-wide mode statistics.
    
    Returns:
        Dictionary with mode statistics
    """
    try:
        # Get user mode distribution
        mode_result = supabase.table('user_mode_states').select('current_mode').execute()
        
        offline_count = sum(1 for r in mode_result.data if r['current_mode'] == 'offline')
        online_count = sum(1 for r in mode_result.data if r['current_mode'] == 'online')
        
        # Get active sessions
        session_result = supabase.table('online_sessions').select('session_id').eq('status', 'active').execute()
        active_sessions = len(session_result.data) if session_result.data else 0
        
        # Get transition stats
        transition_result = supabase.table('mode_transition_log').select('success').execute()
        total_transitions = len(transition_result.data) if transition_result.data else 0
        failed_transitions = sum(1 for r in transition_result.data if not r['success'])
        
        return {
            'total_users': len(mode_result.data) if mode_result.data else 0,
            'offline_users': offline_count,
            'online_users': online_count,
            'active_sessions': active_sessions,
            'total_transitions': total_transitions,
            'failed_transitions': failed_transitions,
            'success_rate': (total_transitions - failed_transitions) / total_transitions * 100 if total_transitions > 0 else 100
        }
    except Exception as e:
        print(f"Error getting mode statistics: {e}")
        return {
            'total_users': 0,
            'offline_users': 0,
            'online_users': 0,
            'active_sessions': 0,
            'total_transitions': 0,
            'failed_transitions': 0,
            'success_rate': 0
        }


# ============================================================================
# Utility Functions
# ============================================================================

def has_sufficient_credits(user_id: int, required: int) -> bool:
    """
    Check if user has sufficient credits.
    
    Args:
        user_id: Telegram user ID
        required: Required credit amount
        
    Returns:
        True if user has enough credits, False otherwise
    """
    current_balance = get_user_credits(user_id)
    return current_balance >= required


def is_online_mode(user_id: int) -> bool:
    """
    Check if user is in online mode.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is in online mode, False otherwise
    """
    return get_user_mode(user_id) == 'online'


def is_offline_mode(user_id: int) -> bool:
    """
    Check if user is in offline mode.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is in offline mode, False otherwise
    """
    return get_user_mode(user_id) == 'offline'
