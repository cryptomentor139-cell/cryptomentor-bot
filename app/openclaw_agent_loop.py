"""
OpenClaw Agentic Loop - Autonomous Agent Controller
Implements multi-step reasoning with function calling
"""

import os
import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenClawAgenticLoop:
    """
    Agentic loop controller for autonomous agent
    Handles multi-step reasoning and tool execution
    """
    
    MAX_ITERATIONS = 5  # Safety limit
    
    def __init__(self, openclaw_manager, agent_tools):
        """
        Initialize agentic loop
        
        Args:
            openclaw_manager: OpenClaw Manager instance
            agent_tools: OpenClaw Agent Tools instance
        """
        self.manager = openclaw_manager
        self.tools = agent_tools
        self.api_key = openclaw_manager.api_key
        self.base_url = openclaw_manager.base_url
        self.model = openclaw_manager.MODEL
    
    def chat_with_tools(
        self,
        user_id: int,
        assistant_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Tuple[str, int, int, int, List[Dict]]:
        """
        Chat with autonomous agent that can use tools
        
        Args:
            user_id: Telegram user ID
            assistant_id: Assistant ID
            message: User message
            conversation_id: Optional conversation ID
            
        Returns:
            Tuple of (response, input_tokens, output_tokens, credits_cost, tool_calls)
        """
        try:
            # Get assistant info
            assistant = self.manager.get_assistant_info(assistant_id)
            if not assistant:
                raise ValueError(f"Assistant {assistant_id} not found")
            
            # Verify ownership
            if assistant['user_id'] != user_id:
                raise ValueError(f"Assistant {assistant_id} does not belong to user {user_id}")
            
            # Check if user is admin (admins get tool access)
            is_admin = self.manager._is_admin(user_id)
            
            if not is_admin:
                # Non-admin: use basic chat without tools
                return self._basic_chat(user_id, assistant_id, message, conversation_id)
            
            # Admin: use agentic loop with tools
            return self._agentic_chat(user_id, assistant_id, message, conversation_id, assistant)
            
        except Exception as e:
            logger.error(f"Error in chat_with_tools: {e}")
            raise
    
    def _basic_chat(
        self,
        user_id: int,
        assistant_id: str,
        message: str,
        conversation_id: Optional[str]
    ) -> Tuple[str, int, int, int, List[Dict]]:
        """Basic chat without tools for non-admin users"""
        response, input_tokens, output_tokens, credits_cost = self.manager.chat(
            user_id=user_id,
            assistant_id=assistant_id,
            message=message,
            conversation_id=conversation_id
        )
        return response, input_tokens, output_tokens, credits_cost, []
    
    def _agentic_chat(
        self,
        user_id: int,
        assistant_id: str,
        message: str,
        conversation_id: Optional[str],
        assistant: Dict
    ) -> Tuple[str, int, int, int, List[Dict]]:
        """
        Agentic chat with tool calling for admin users
        Implements autonomous multi-step reasoning
        """
        import requests
        
        # Get or create conversation
        if not conversation_id:
            conversation_id = self.manager._create_conversation(assistant_id, user_id)
        
        # Get conversation history
        history = self.manager._get_conversation_history(conversation_id, limit=20)
        
        # Build messages
        messages = []
        for msg in history:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Get tools schema
        tools_schema = self.tools.get_tools_schema()
        
        # Agentic loop
        iteration = 0
        total_input_tokens = 0
        total_output_tokens = 0
        tool_calls_log = []
        
        while iteration < self.MAX_ITERATIONS:
            iteration += 1
            logger.info(f"Agentic loop iteration {iteration}/{self.MAX_ITERATIONS}")
            
            # Prepare API request
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://cryptomentor.ai',
                'X-Title': 'CryptoMentor OpenClaw Agent'
            }
            
            # Build messages with system prompt
            api_messages = [
                {"role": "system", "content": assistant['system_prompt']}
            ] + messages
            
            payload = {
                'model': self.model,
                'messages': api_messages,
                'max_tokens': 8192,
                'temperature': 0.7,
                'tools': tools_schema,
                'tool_choice': 'auto'  # Let model decide when to use tools
            }
            
            # Call API
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            # Track tokens
            total_input_tokens += data['usage']['prompt_tokens']
            total_output_tokens += data['usage']['completion_tokens']
            
            # Get response
            choice = data['choices'][0]
            finish_reason = choice['finish_reason']
            assistant_message = choice['message']
            
            # Check if model wants to call tools
            if finish_reason == 'tool_calls' and 'tool_calls' in assistant_message:
                # Model wants to use tools
                tool_calls = assistant_message['tool_calls']
                
                logger.info(f"Model requested {len(tool_calls)} tool calls")
                
                # Add assistant message to history
                messages.append(assistant_message)
                
                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call['function']['name']
                    tool_args = json.loads(tool_call['function']['arguments'])
                    tool_call_id = tool_call['id']
                    
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    
                    # Execute tool
                    tool_result = self.tools.execute_tool(tool_name, tool_args)
                    
                    # Log tool call
                    tool_calls_log.append({
                        'tool': tool_name,
                        'arguments': tool_args,
                        'result': tool_result,
                        'iteration': iteration
                    })
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": json.dumps(tool_result)
                    })
                
                # Continue loop to let model process tool results
                continue
            
            else:
                # Model finished - no more tools needed
                final_response = assistant_message.get('content', '')
                
                logger.info(f"Agentic loop completed in {iteration} iterations")
                
                # Calculate credits cost
                credits_cost = self.manager._calculate_credits_cost(
                    total_input_tokens,
                    total_output_tokens
                )
                
                # Admin: no charge
                logger.info(f"Admin {user_id} using OpenClaw Agent (no charge)")
                credits_cost = 0
                
                # Save messages
                self.manager._save_message(
                    conversation_id=conversation_id,
                    role='user',
                    content=message,
                    input_tokens=0,
                    output_tokens=0,
                    credits_cost=0
                )
                
                self.manager._save_message(
                    conversation_id=conversation_id,
                    role='assistant',
                    content=final_response,
                    input_tokens=total_input_tokens,
                    output_tokens=total_output_tokens,
                    credits_cost=credits_cost
                )
                
                # Update stats
                self.manager._update_conversation_stats(
                    conversation_id=conversation_id,
                    tokens=total_input_tokens + total_output_tokens,
                    credits=credits_cost
                )
                
                self.manager._update_assistant_stats(
                    assistant_id=assistant_id,
                    tokens=total_input_tokens + total_output_tokens,
                    credits=credits_cost
                )
                
                return (
                    final_response,
                    total_input_tokens,
                    total_output_tokens,
                    credits_cost,
                    tool_calls_log
                )
        
        # Max iterations reached
        logger.warning(f"Max iterations ({self.MAX_ITERATIONS}) reached")
        
        return (
            "I've reached my thinking limit. Let me know if you need anything else!",
            total_input_tokens,
            total_output_tokens,
            0,
            tool_calls_log
        )


def get_openclaw_agentic_loop(openclaw_manager, agent_tools):
    """Get OpenClaw agentic loop instance"""
    return OpenClawAgenticLoop(openclaw_manager, agent_tools)
