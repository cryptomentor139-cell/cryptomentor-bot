"""
OnlineModeHandler for dual-mode offline-online system.

This module handles all online mode operations including activation,
deactivation, message handling with AI agent forwarding, credit management,
and UI formatting.

Feature: dual-mode-offline-online
Requirements: 1.4, 1.5, 3.3, 3.6, 3.8, 3.9
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# Import managers
from app.dual_mode.session_manager import SessionManager
from app.dual_mode.ai_agent_manager import AIAgentManager
from app.dual_mode.credit_manager import CreditManager
from app.dual_mode.automaton_bridge import AutomatonBridge
from app.dual_mode.genesis_prompt_loader import GenesisPromptLoader

# Import database functions
from app.dual_mode_db import (
    get_user_mode,
    set_user_mode,
    get_user_credits
)


# Minimum credits required for online mode
MINIMUM_CREDITS_REQUIRED = 10


@dataclass
class ActivationResult:
    """Result of online mode activation"""
    success: bool
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


@dataclass
class AIResponse:
    """Response from AI agent interaction"""
    success: bool
    message: Optional[str] = None
    credits_used: int = 0
    credits_remaining: int = 0
    error: Optional[str] = None


class OnlineModeHandler:
    """
    Handles online mode operations with AI agent integration.
    
    Responsibilities:
    - Activate online mode with credit validation
    - Deactivate online mode with graceful cleanup
    - Handle user messages with AI agent forwarding
    - Manage credit deduction per interaction
    - Format responses with online mode UI
    
    Online mode provides AI-powered trading assistance through isolated
    Automaton agents. Each user has their own agent initialized with the
    Genesis Prompt. Credits are deducted based on usage.
    """
    
    def __init__(self):
        """Initialize OnlineModeHandler with required managers."""
        self.session_manager = SessionManager()
        self.ai_agent_manager = AIAgentManager()
        self.credit_manager = CreditManager()
        self.automaton_bridge = AutomatonBridge()
        self.genesis_prompt_loader = GenesisPromptLoader()
    
    def activate_online_mode(self, user_id: int) -> ActivationResult:
        """
        Activate online mode for a user with credit check and session creation.
        
        This method:
        1. Checks if user has sufficient Automaton credits
        2. Creates or retrieves user's isolated AI agent
        3. Creates a new session for the interaction
        4. Sets user mode to 'online'
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            ActivationResult with success status and session details
            
        Requirements: 1.4, 1.5
        """
        try:
            # Check if user has sufficient credits
            current_credits = self.credit_manager.get_user_credits(user_id)
            
            if current_credits < MINIMUM_CREDITS_REQUIRED:
                return ActivationResult(
                    success=False,
                    error=f"Insufficient credits. You have {current_credits} credits, "
                          f"but need at least {MINIMUM_CREDITS_REQUIRED} to activate online mode.",
                    message="To obtain Automaton credits, please contact the admin or make a deposit."
                )
            
            # Get or create isolated AI agent
            agent = self.ai_agent_manager.get_or_create_agent(user_id)
            
            if agent is None:
                return ActivationResult(
                    success=False,
                    error="Failed to initialize AI agent. Please try again."
                )
            
            # Create new session
            session = self.session_manager.create_session(user_id, agent.agent_id)
            
            if session is None:
                return ActivationResult(
                    success=False,
                    error="Failed to create session. Please try again."
                )
            
            # Set user mode to online
            set_user_mode(user_id, 'online')
            
            return ActivationResult(
                success=True,
                session_id=session.session_id,
                agent_id=agent.agent_id,
                message=f"[ONLINE - AI] 🤖 Welcome to online mode! "
                       f"Your AI agent is ready. You have {current_credits} credits available."
            )
            
        except Exception as e:
            print(f"Error activating online mode: {e}")
            return ActivationResult(
                success=False,
                error=f"An error occurred: {str(e)}"
            )
    
    def deactivate_online_mode(self, user_id: int) -> bool:
        """
        Deactivate online mode with graceful cleanup.
        
        This method:
        1. Closes the active session
        2. Sets user mode to 'offline'
        3. Preserves agent for future use
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if deactivation successful, False otherwise
            
        Requirements: 1.5
        """
        try:
            # Close active session
            session_closed = self.session_manager.close_session(user_id)
            
            if not session_closed:
                print(f"Warning: No active session found for user {user_id}")
            
            # Set user mode to offline
            set_user_mode(user_id, 'offline')
            
            return True
            
        except Exception as e:
            print(f"Error deactivating online mode: {e}")
            return False
    
    def handle_user_message(self, user_id: int, message: str) -> AIResponse:
        """
        Handle user message with AI agent forwarding and credit management.
        
        This method implements the core online mode flow:
        1. Verify user is in online mode
        2. Get user's isolated AI agent
        3. Forward message to Automaton API
        4. Deduct credits based on usage
        5. Update session activity
        6. Return formatted response with remaining credits
        
        Args:
            user_id: Telegram user ID
            message: User's message to send to AI agent
            
        Returns:
            AIResponse with AI's response and credit information
            
        Requirements: 3.3, 3.8, 3.9
        """
        try:
            # Verify user is in online mode
            current_mode = get_user_mode(user_id)
            
            if current_mode != 'online':
                return AIResponse(
                    success=False,
                    error="You are not in online mode. Use /online to activate."
                )
            
            # Get user's agent
            agent = self.ai_agent_manager.get_agent(user_id)
            
            if agent is None:
                return AIResponse(
                    success=False,
                    error="AI agent not found. Please reactivate online mode with /online."
                )
            
            # Get active session
            session = self.session_manager.get_session(user_id)
            
            if session is None:
                return AIResponse(
                    success=False,
                    error="No active session. Please reactivate online mode with /online."
                )
            
            # Check if user has sufficient credits before sending
            credits_before = self.credit_manager.get_user_credits(user_id)
            
            if credits_before < 1:
                return AIResponse(
                    success=False,
                    error="Insufficient credits. Please add more credits to continue.",
                    credits_remaining=credits_before
                )
            
            # Forward message to AI agent via Automaton API (Requirement 3.3)
            automaton_response = self.automaton_bridge.send_message(
                agent.agent_id,
                message
            )
            
            # If API call failed, don't deduct credits (Requirement 12.3)
            if not automaton_response.success:
                return AIResponse(
                    success=False,
                    error=automaton_response.error or "Failed to communicate with AI agent.",
                    credits_remaining=credits_before
                )
            
            # Deduct credits based on usage (Requirement 3.8)
            credits_used = automaton_response.credits_used
            deduct_result = self.credit_manager.deduct_credits(
                user_id,
                credits_used,
                "Online mode message",
                session_id=session.session_id
            )
            
            if not deduct_result.success:
                # This shouldn't happen since we checked before, but handle it
                return AIResponse(
                    success=False,
                    error=deduct_result.error or "Failed to deduct credits.",
                    credits_remaining=credits_before
                )
            
            # Update session activity
            self.session_manager.update_session_activity(user_id, credits_used)
            
            # Get remaining credits (Requirement 3.9)
            credits_remaining = self.credit_manager.get_user_credits(user_id)
            
            # Return formatted response
            return AIResponse(
                success=True,
                message=automaton_response.message,
                credits_used=credits_used,
                credits_remaining=credits_remaining
            )
            
        except Exception as e:
            print(f"Error handling user message: {e}")
            return AIResponse(
                success=False,
                error=f"An error occurred: {str(e)}"
            )
    
    def get_online_menu(self) -> Dict[str, Any]:
        """
        Get online mode menu with inline keyboard.
        
        Returns:
            Dictionary representing inline keyboard markup
            
        Requirements: 3.6
        """
        # This will be implemented when integrating with Telegram bot
        # For now, return a simple structure
        return {
            'inline_keyboard': [
                [
                    {'text': '💬 Chat with AI', 'callback_data': 'online_chat'},
                    {'text': '📊 Get Signal', 'callback_data': 'online_signal'}
                ],
                [
                    {'text': '💰 Check Credits', 'callback_data': 'check_credits'},
                    {'text': '📴 Go Offline', 'callback_data': 'go_offline'}
                ]
            ]
        }
    
    def format_online_response(self, ai_message: str, credits_remaining: int) -> str:
        """
        Format online mode response with prefix and credit display.
        
        This method adds the [ONLINE - AI] prefix and displays remaining
        credits after each interaction as required.
        
        Args:
            ai_message: Message from AI agent
            credits_remaining: User's remaining credit balance
            
        Returns:
            Formatted response string
            
        Requirements: 3.9, 8.2, 8.3
        """
        formatted = f"[ONLINE - AI] 🤖\n\n{ai_message}\n\n"
        formatted += f"💰 Credits remaining: {credits_remaining}"
        
        return formatted
    
    def get_insufficient_credits_message(self, current_credits: int) -> str:
        """
        Get message to display when user has insufficient credits.
        
        Args:
            current_credits: User's current credit balance
            
        Returns:
            Formatted message with instructions
            
        Requirements: 1.6, 4.3
        """
        message = f"❌ Insufficient Automaton credits.\n\n"
        message += f"Current balance: {current_credits} credits\n"
        message += f"Required: {MINIMUM_CREDITS_REQUIRED} credits\n\n"
        message += "To obtain credits:\n"
        message += "1. Contact admin for initial deposit\n"
        message += "2. Use /credits to check your balance\n"
        message += "3. Once you have credits, use /online to activate"
        
        return message
