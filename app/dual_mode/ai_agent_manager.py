"""
AI Agent Manager for dual-mode offline-online system.

This module manages isolated AI agent instances for each user in online mode.
Each user has their own isolated agent that is initialized with the Genesis Prompt.
The manager handles agent creation, retrieval, isolation validation, and cleanup.

Feature: dual-mode-offline-online
Requirements: 3.2, 10.1, 10.2, 10.5, 11.2
"""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

# Import database functions
from app.dual_mode_db import (
    create_agent as db_create_agent,
    get_agent as db_get_agent,
    delete_agent as db_delete_agent,
    update_agent_activity as db_update_agent_activity
)


@dataclass
class Agent:
    """
    Represents an isolated AI agent for a user.
    
    Attributes:
        agent_id: Unique agent identifier
        user_id: Telegram user ID (owner)
        genesis_prompt: Base system prompt for trading
        conversation_history: List of messages
        created_at: Agent creation timestamp
        last_used: Last interaction timestamp
        total_messages: Total message count
        status: Agent status (active, inactive, deleted)
    """
    agent_id: str
    user_id: int
    genesis_prompt: str
    conversation_history: list
    created_at: datetime
    last_used: datetime
    total_messages: int
    status: str


class AIAgentManager:
    """
    Manages isolated AI agent instances for online mode users.
    
    Responsibilities:
    - Create and initialize agents with Genesis Prompt
    - Retrieve agents with lazy initialization
    - Validate agent isolation (security)
    - Delete agents for cleanup
    
    Each user has exactly one isolated agent that is completely separate
    from other users' agents. The agent is initialized with the Genesis
    Prompt which provides base knowledge for autonomous trading operations.
    """
    
    def __init__(self, genesis_prompt_loader=None):
        """
        Initialize the AIAgentManager.
        
        Args:
            genesis_prompt_loader: Optional GenesisPromptLoader instance
                                  If None, will load from file directly
        """
        self.genesis_prompt_loader = genesis_prompt_loader
    
    def get_or_create_agent(self, user_id: int) -> Optional[Agent]:
        """
        Get existing agent or create new one with lazy initialization.
        
        This method implements lazy initialization - it first checks if
        the user already has an agent. If not, it creates a new one with
        the Genesis Prompt. This ensures each user has exactly one agent.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Agent object if successful, None otherwise
            
        Requirements: 3.2, 10.1, 10.2
        """
        try:
            # Try to get existing agent
            existing_agent = self.get_agent(user_id)
            
            if existing_agent is not None:
                print(f"Retrieved existing agent for user {user_id}")
                return existing_agent
            
            # No existing agent, create new one
            print(f"Creating new agent for user {user_id}")
            
            # Load Genesis Prompt
            genesis_prompt = self._load_genesis_prompt()
            
            if genesis_prompt is None:
                print(f"Failed to load Genesis Prompt for user {user_id}")
                return None
            
            # Initialize new agent
            return self.initialize_agent(user_id, genesis_prompt)
            
        except Exception as e:
            print(f"Error in get_or_create_agent: {e}")
            return None
    
    def get_agent(self, user_id: int) -> Optional[Agent]:
        """
        Get user's existing isolated AI agent.
        
        This method retrieves the agent from the database without creating
        a new one. Returns None if the user doesn't have an agent yet.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Agent object if exists, None otherwise
            
        Requirements: 10.2, 10.5
        """
        try:
            # Get agent from database
            agent_data = db_get_agent(user_id)
            
            if agent_data is None:
                return None
            
            # Convert database record to Agent object
            return Agent(
                agent_id=agent_data['agent_id'],
                user_id=agent_data['user_id'],
                genesis_prompt=agent_data['genesis_prompt'],
                conversation_history=agent_data.get('conversation_history', []),
                created_at=datetime.fromisoformat(agent_data['created_at'].replace('Z', '+00:00'))
                    if isinstance(agent_data['created_at'], str)
                    else agent_data['created_at'],
                last_used=datetime.fromisoformat(agent_data['last_used'].replace('Z', '+00:00'))
                    if isinstance(agent_data['last_used'], str)
                    else agent_data['last_used'],
                total_messages=agent_data['total_messages'],
                status=agent_data['status']
            )
            
        except Exception as e:
            print(f"Error getting agent: {e}")
            return None
    
    def initialize_agent(self, user_id: int, genesis_prompt: str) -> Optional[Agent]:
        """
        Initialize a new AI agent with Genesis Prompt injection.
        
        This method creates a new isolated agent for the user and injects
        the Genesis Prompt as the base system prompt. The Genesis Prompt
        provides the agent with knowledge about autonomous trading, risk
        management, and communication protocols.
        
        Args:
            user_id: Telegram user ID
            genesis_prompt: Base system prompt for trading operations
            
        Returns:
            Agent object if successful, None otherwise
            
        Requirements: 3.2, 11.2
        """
        try:
            # Generate unique agent ID
            agent_id = f"agent_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Create agent in database with Genesis Prompt
            success = db_create_agent(user_id, agent_id, genesis_prompt)
            
            if not success:
                print(f"Failed to create agent in database for user {user_id}")
                return None
            
            # Return Agent object
            print(f"Initialized agent {agent_id} for user {user_id}")
            
            return Agent(
                agent_id=agent_id,
                user_id=user_id,
                genesis_prompt=genesis_prompt,
                conversation_history=[],
                created_at=datetime.utcnow(),
                last_used=datetime.utcnow(),
                total_messages=0,
                status='active'
            )
            
        except Exception as e:
            print(f"Error initializing agent: {e}")
            return None
    
    def is_agent_isolated(self, agent_id: str, user_id: int) -> bool:
        """
        Validate that agent belongs to user (security validation).
        
        This method performs security validation to ensure that the
        specified agent actually belongs to the specified user. This
        prevents users from accessing other users' agents.
        
        Args:
            agent_id: Agent identifier to validate
            user_id: User ID claiming ownership
            
        Returns:
            True if agent belongs to user, False otherwise
            
        Requirements: 10.1, 10.2, 10.5
        """
        try:
            # Get agent from database
            agent = self.get_agent(user_id)
            
            if agent is None:
                print(f"No agent found for user {user_id}")
                return False
            
            # Verify agent ID matches
            if agent.agent_id != agent_id:
                print(f"Agent ID mismatch: expected {agent.agent_id}, got {agent_id}")
                return False
            
            # Verify user ID matches
            if agent.user_id != user_id:
                print(f"User ID mismatch: agent belongs to {agent.user_id}, not {user_id}")
                return False
            
            # Verify agent is active
            if agent.status != 'active':
                print(f"Agent {agent_id} is not active (status: {agent.status})")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validating agent isolation: {e}")
            return False
    
    def delete_agent(self, user_id: int) -> bool:
        """
        Delete user's AI agent (cleanup).
        
        This method performs a soft delete by marking the agent as
        'deleted' in the database. The agent data is preserved for
        audit purposes but the agent is no longer accessible.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if deletion successful, False otherwise
            
        Requirements: 10.5
        """
        try:
            # Verify agent exists
            agent = self.get_agent(user_id)
            
            if agent is None:
                print(f"No agent found for user {user_id}")
                return False
            
            # Soft delete in database
            success = db_delete_agent(user_id)
            
            if success:
                print(f"Deleted agent {agent.agent_id} for user {user_id}")
            else:
                print(f"Failed to delete agent for user {user_id}")
            
            return success
            
        except Exception as e:
            print(f"Error deleting agent: {e}")
            return False
    
    def update_agent_activity(self, agent_id: str, conversation_history: Optional[list] = None) -> bool:
        """
        Update agent's last activity timestamp and conversation history.
        
        This method should be called after each interaction with the agent
        to track usage and maintain conversation context.
        
        Args:
            agent_id: Agent identifier
            conversation_history: Optional updated conversation history
            
        Returns:
            True if update successful, False otherwise
            
        Requirements: 3.2
        """
        try:
            success = db_update_agent_activity(agent_id, conversation_history)
            
            if success:
                print(f"Updated activity for agent {agent_id}")
            else:
                print(f"Failed to update activity for agent {agent_id}")
            
            return success
            
        except Exception as e:
            print(f"Error updating agent activity: {e}")
            return False
    
    def _load_genesis_prompt(self) -> Optional[str]:
        """
        Load Genesis Prompt from file or loader.
        
        This internal method loads the Genesis Prompt either from a
        GenesisPromptLoader instance (if provided) or directly from
        the AUTOMATON_GENESIS_PROMPT.md file.
        
        Returns:
            Genesis Prompt content or None if failed
            
        Requirements: 11.2
        """
        try:
            # Use loader if provided
            if self.genesis_prompt_loader is not None:
                return self.genesis_prompt_loader.get_current_prompt()
            
            # Otherwise load from file
            import os
            prompt_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'AUTOMATON_GENESIS_PROMPT.md'
            )
            
            if not os.path.exists(prompt_path):
                print(f"Genesis Prompt file not found: {prompt_path}")
                return None
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"Loaded Genesis Prompt from {prompt_path}")
            return content
            
        except Exception as e:
            print(f"Error loading Genesis Prompt: {e}")
            return None
