"""
AutomatonBridge - Interface with Automaton API for AI agent operations

This module provides the bridge between the bot and the Automaton API,
handling message sending, agent status checks, credit validation, and
retry logic with exponential backoff.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class AutomatonResponse:
    """Response from Automaton API"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    credits_used: int = 0
    data: Optional[Dict[str, Any]] = None


@dataclass
class AgentStatus:
    """Status of an AI agent"""
    agent_id: str
    is_active: bool
    message_count: int
    last_activity: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of admin balance validation"""
    success: bool
    balance: int = 0
    error: Optional[str] = None


class AutomatonBridge:
    """Bridge to Automaton API for AI agent operations"""
    
    def __init__(self):
        """Initialize Automaton Bridge with configuration"""
        self.api_url = os.getenv('AUTOMATON_API_URL')
        self.api_key = os.getenv('AUTOMATON_API_KEY')
        self.timeout = int(os.getenv('AUTOMATON_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('AUTOMATON_MAX_RETRIES', '3'))
        self.backoff_factor = int(os.getenv('AUTOMATON_BACKOFF_FACTOR', '2'))
        
        if not self.api_url or not self.api_key:
            logger.warning("Automaton API credentials not configured")
        
        # Configure session with retry strategy
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry configuration"""
        session = requests.Session()
        
        # Configure retry strategy (only for connection errors, not for HTTP errors)
        retry_strategy = Retry(
            total=0,  # We'll handle retries manually for better control
            backoff_factor=self.backoff_factor
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
        return session
    
    def send_message(self, agent_id: str, message: str) -> AutomatonResponse:
        """
        Send message to Automaton AI agent
        
        Args:
            agent_id: Unique identifier for the AI agent
            message: User message to send to the agent
            
        Returns:
            AutomatonResponse with success status and response message
        """
        if not self.api_url or not self.api_key:
            return AutomatonResponse(
                success=False,
                error="Automaton API not configured"
            )
        
        endpoint = f"{self.api_url}/agents/{agent_id}/message"
        payload = {"message": message}
        
        def _send():
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        try:
            result = self.retry_with_backoff(_send, max_retries=self.max_retries)
            
            return AutomatonResponse(
                success=True,
                message=result.get('response', ''),
                credits_used=result.get('credits_used', 1),
                data=result
            )
        
        except requests.exceptions.Timeout:
            logger.error(f"Timeout sending message to agent {agent_id}")
            return AutomatonResponse(
                success=False,
                error="Request timed out. Please try again."
            )
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error sending message to agent {agent_id}")
            return AutomatonResponse(
                success=False,
                error="Unable to connect to Automaton service."
            )
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error sending message to agent {agent_id}: {e}")
            return AutomatonResponse(
                success=False,
                error=f"API error: {e.response.status_code}"
            )
        
        except Exception as e:
            logger.error(f"Unexpected error sending message to agent {agent_id}: {e}")
            return AutomatonResponse(
                success=False,
                error="An unexpected error occurred."
            )
    
    def get_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """
        Get status of an AI agent
        
        Args:
            agent_id: Unique identifier for the AI agent
            
        Returns:
            AgentStatus if successful, None otherwise
        """
        if not self.api_url or not self.api_key:
            logger.warning("Automaton API not configured")
            return None
        
        endpoint = f"{self.api_url}/agents/{agent_id}/status"
        
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return AgentStatus(
                agent_id=agent_id,
                is_active=data.get('is_active', False),
                message_count=data.get('message_count', 0),
                last_activity=data.get('last_activity')
            )
        
        except Exception as e:
            logger.error(f"Error getting agent status for {agent_id}: {e}")
            return None
    
    def validate_api_connection(self) -> bool:
        """
        Validate connection to Automaton API
        
        Returns:
            True if connection is valid, False otherwise
        """
        if not self.api_url or not self.api_key:
            return False
        
        endpoint = f"{self.api_url}/health"
        
        try:
            response = self.session.get(endpoint, timeout=5)
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"API connection validation failed: {e}")
            return False
    
    def get_admin_balance(self, admin_id: int) -> int:
        """
        Get admin's Automaton credit balance
        
        Args:
            admin_id: Admin user ID
            
        Returns:
            Credit balance, or 0 if error
        """
        if not self.api_url or not self.api_key:
            logger.warning("Automaton API not configured")
            return 0
        
        endpoint = f"{self.api_url}/admin/{admin_id}/balance"
        
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return data.get('balance', 0)
        
        except Exception as e:
            logger.error(f"Error getting admin balance for {admin_id}: {e}")
            return 0
    
    def deduct_admin_credits(self, admin_id: int, amount: int) -> bool:
        """
        Deduct credits from admin's Automaton balance
        
        Args:
            admin_id: Admin user ID
            amount: Amount of credits to deduct
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_url or not self.api_key:
            logger.warning("Automaton API not configured")
            return False
        
        endpoint = f"{self.api_url}/admin/{admin_id}/deduct"
        payload = {"amount": amount}
        
        try:
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return True
        
        except Exception as e:
            logger.error(f"Error deducting admin credits for {admin_id}: {e}")
            return False
    
    def retry_with_backoff(
        self,
        operation: Callable,
        max_retries: int = 3
    ) -> Any:
        """
        Retry operation with exponential backoff
        
        Args:
            operation: Callable to retry
            max_retries: Maximum number of retry attempts
            
        Returns:
            Result of successful operation
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return operation()
            
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exception = e
                
                if attempt < max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
            
            except Exception as e:
                # Don't retry on non-transient errors
                logger.error(f"Non-retryable error: {e}")
                raise
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        
        raise RuntimeError("Retry logic failed unexpectedly")


# Global instance
_automaton_bridge = None


def get_automaton_bridge() -> AutomatonBridge:
    """Get or create global AutomatonBridge instance"""
    global _automaton_bridge
    
    if _automaton_bridge is None:
        _automaton_bridge = AutomatonBridge()
    
    return _automaton_bridge
