"""
OpenClaw Gateway Bridge
Connect to real OpenClaw gateway for full autonomous capabilities
"""

import os
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenClawGatewayBridge:
    """
    Bridge to OpenClaw Gateway for autonomous agent capabilities
    
    Connects our Python bot to real OpenClaw (Node.js) gateway
    for full autonomous features: agent spawning, tool execution, etc.
    """
    
    def __init__(
        self,
        gateway_url: Optional[str] = None,
        auth_token: Optional[str] = None
    ):
        """
        Initialize gateway bridge
        
        Args:
            gateway_url: OpenClaw gateway URL (default: from env or localhost)
            auth_token: Gateway auth token (default: from env)
        """
        self.gateway_url = gateway_url or os.getenv(
            'OPENCLAW_GATEWAY_URL',
            'http://localhost:18789'
        )
        self.auth_token = auth_token or os.getenv(
            'OPENCLAW_GATEWAY_TOKEN',
            'deb2a3ab8a9bc891a1a47a7507cb01694c04cb26bd7fe538'
        )
        
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"OpenClaw Gateway Bridge initialized: {self.gateway_url}")
    
    def health_check(self) -> bool:
        """
        Check if gateway is running and accessible
        
        Returns:
            True if gateway is healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.gateway_url}/health",
                timeout=5
            )
            is_healthy = response.status_code == 200
            
            if is_healthy:
                logger.info("OpenClaw Gateway is healthy")
            else:
                logger.warning(f"OpenClaw Gateway unhealthy: {response.status_code}")
            
            return is_healthy
            
        except requests.exceptions.ConnectionError:
            logger.error("OpenClaw Gateway not reachable (connection refused)")
            return False
        except requests.exceptions.Timeout:
            logger.error("OpenClaw Gateway timeout")
            return False
        except Exception as e:
            logger.error(f"OpenClaw Gateway health check failed: {e}")
            return False
    
    def spawn_agent(
        self,
        user_id: int,
        task: str,
        model: str = "openrouter/openai/gpt-4.1",
        workspace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Spawn autonomous agent via OpenClaw gateway
        
        Note: OpenClaw gateway API might not support agent spawning via REST API.
        This is a placeholder implementation. Real OpenClaw uses Telegram/Discord channels.
        
        Args:
            user_id: Telegram user ID
            task: Task description for agent
            model: LLM model to use
            workspace: Optional workspace path
            
        Returns:
            Dict with agent_id and status, or error
        """
        try:
            # Try different possible endpoints
            endpoints = [
                "/api/agents/spawn",
                "/api/agents",
                "/agents/spawn",
                "/spawn"
            ]
            
            payload = {
                "userId": user_id,
                "task": task,
                "model": model
            }
            
            if workspace:
                payload["workspace"] = workspace
            
            last_error = None
            
            for endpoint in endpoints:
                try:
                    response = requests.post(
                        f"{self.gateway_url}{endpoint}",
                        headers=self.headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Agent spawned via {endpoint}: {result.get('agentId')}")
                        return result
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        last_error = f"Status {response.status_code}: {response.text}"
                        
                except requests.exceptions.RequestException as e:
                    last_error = str(e)
                    continue
            
            # All endpoints failed
            error_msg = f"Failed to spawn agent. Last error: {last_error}"
            logger.error(error_msg)
            return {
                "error": "Agent spawning not supported via REST API",
                "details": "OpenClaw gateway primarily uses Telegram/Discord channels for agent interaction",
                "suggestion": "Use OpenClaw's native Telegram bot (@billjunior_bot) or configure channel integration"
            }
                return result
            else:
                error_msg = f"Failed to spawn agent: {response.status_code}"
                logger.error(error_msg)
                return {"error": error_msg, "details": response.text}
                
        except Exception as e:
            logger.error(f"Error spawning agent: {e}")
            return {"error": str(e)}
    
    def chat_with_agent(
        self,
        agent_id: str,
        message: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send message to agent and get response
        
        Args:
            agent_id: Agent ID
            message: Message to send
            stream: Whether to stream response
            
        Returns:
            Dict with response and metadata
        """
        try:
            response = requests.post(
                f"{self.gateway_url}/api/agents/{agent_id}/chat",
                headers=self.headers,
                json={
                    "message": message,
                    "stream": stream
                },
                timeout=120  # Longer timeout for complex tasks
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Chat with agent {agent_id} successful")
                return result
            else:
                error_msg = f"Chat failed: {response.status_code}"
                logger.error(error_msg)
                return {"error": error_msg, "details": response.text}
                
        except Exception as e:
            logger.error(f"Error chatting with agent: {e}")
            return {"error": str(e)}
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent status and information
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Dict with agent status, progress, etc.
        """
        try:
            response = requests.get(
                f"{self.gateway_url}/api/agents/{agent_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to get status: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return {"error": str(e)}
    
    def list_agents(
        self,
        user_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List agents (optionally filtered by user or status)
        
        Args:
            user_id: Filter by user ID
            status: Filter by status (active, idle, completed, error)
            
        Returns:
            Dict with list of agents
        """
        try:
            params = {}
            if user_id:
                params["userId"] = user_id
            if status:
                params["status"] = status
            
            response = requests.get(
                f"{self.gateway_url}/api/agents",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to list agents: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return {"error": str(e)}
    
    def stop_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Stop/terminate an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Dict with success status
        """
        try:
            response = requests.post(
                f"{self.gateway_url}/api/agents/{agent_id}/stop",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Agent {agent_id} stopped")
                return {"success": True, "message": "Agent stopped"}
            else:
                return {
                    "error": f"Failed to stop agent: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error stopping agent: {e}")
            return {"error": str(e)}
    
    def execute_command(
        self,
        agent_id: str,
        command: str,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Execute command via agent
        
        Args:
            agent_id: Agent ID
            command: Command to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Dict with execution result
        """
        try:
            response = requests.post(
                f"{self.gateway_url}/api/agents/{agent_id}/execute",
                headers=self.headers,
                json={"command": command},
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Command executed on agent {agent_id}")
                return result
            else:
                return {
                    "error": f"Command execution failed: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {"error": str(e)}
    
    def get_agent_logs(
        self,
        agent_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get agent execution logs
        
        Args:
            agent_id: Agent ID
            limit: Number of log entries to retrieve
            
        Returns:
            Dict with log entries
        """
        try:
            response = requests.get(
                f"{self.gateway_url}/api/agents/{agent_id}/logs",
                headers=self.headers,
                params={"limit": limit},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to get logs: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error getting agent logs: {e}")
            return {"error": str(e)}
    
    def get_workspace_files(
        self,
        agent_id: str,
        path: str = "/"
    ) -> Dict[str, Any]:
        """
        List files in agent workspace
        
        Args:
            agent_id: Agent ID
            path: Path within workspace
            
        Returns:
            Dict with file list
        """
        try:
            response = requests.get(
                f"{self.gateway_url}/api/agents/{agent_id}/workspace",
                headers=self.headers,
                params={"path": path},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to list files: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error listing workspace files: {e}")
            return {"error": str(e)}
    
    def get_gateway_info(self) -> Dict[str, Any]:
        """
        Get gateway information and statistics
        
        Returns:
            Dict with gateway info
        """
        try:
            response = requests.get(
                f"{self.gateway_url}/api/info",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to get info: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error getting gateway info: {e}")
            return {"error": str(e)}


# Singleton instance
_gateway_bridge = None

def get_openclaw_gateway_bridge() -> OpenClawGatewayBridge:
    """Get singleton instance of OpenClaw gateway bridge"""
    global _gateway_bridge
    if _gateway_bridge is None:
        _gateway_bridge = OpenClawGatewayBridge()
    return _gateway_bridge
