"""
OpenClaw CLI Bridge - Direct CLI Integration
Simpler and more reliable than REST API gateway approach
"""

import os
import json
import logging
import subprocess
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenClawCLIBridge:
    """
    Bridge to OpenClaw via CLI commands
    
    Uses subprocess to call openclaw CLI directly.
    More reliable than REST API for basic operations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CLI bridge with all necessary API keys
        
        Args:
            api_key: API key (from env if not provided)
        """
        # Use OpenRouter key as primary (works for all AI models)
        self.api_key = (
            api_key or 
            os.getenv('OPENROUTER_API_KEY') or
            os.getenv('ANTHROPIC_API_KEY') or 
            os.getenv('OPENCLAW_API_KEY')
        )
        
        # Set environment for openclaw CLI with ALL relevant API keys
        self.env = os.environ.copy()
        
        # Primary AI API Key (OpenRouter - works for Claude, GPT-4, Gemini, etc.)
        if self.api_key:
            self.env['OPENROUTER_API_KEY'] = self.api_key
            self.env['ANTHROPIC_API_KEY'] = self.api_key
            self.env['OPENCLAW_API_KEY'] = self.api_key
        
        # Set base URLs for OpenRouter
        self.env['ANTHROPIC_BASE_URL'] = 'https://openrouter.ai/api/v1'
        self.env['OPENCLAW_BASE_URL'] = 'https://openrouter.ai/api/v1'
        
        # Additional AI APIs (for autonomous operations)
        if os.getenv('DEEPSEEK_API_KEY'):
            self.env['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY')
            self.env['DEEPSEEK_BASE_URL'] = os.getenv('DEEPSEEK_BASE_URL', 'https://openrouter.ai/api/v1')
        
        if os.getenv('CEREBRAS_API_KEY'):
            self.env['CEREBRAS_API_KEY'] = os.getenv('CEREBRAS_API_KEY')
        
        # Crypto Data APIs (for market research)
        if os.getenv('CRYPTONEWS_API_KEY'):
            self.env['CRYPTONEWS_API_KEY'] = os.getenv('CRYPTONEWS_API_KEY')
        
        if os.getenv('HELIUS_API_KEY'):
            self.env['HELIUS_API_KEY'] = os.getenv('HELIUS_API_KEY')
        
        if os.getenv('CRYPTOCOMPARE_API_KEY'):
            self.env['CRYPTOCOMPARE_API_KEY'] = os.getenv('CRYPTOCOMPARE_API_KEY')
        
        # Database connections (for data persistence)
        if os.getenv('SUPABASE_URL'):
            self.env['SUPABASE_URL'] = os.getenv('SUPABASE_URL')
            self.env['SUPABASE_KEY'] = os.getenv('SUPABASE_KEY', '')
            self.env['SUPABASE_ANON_KEY'] = os.getenv('SUPABASE_ANON_KEY', '')
            self.env['SUPABASE_SERVICE_KEY'] = os.getenv('SUPABASE_SERVICE_KEY', '')
        
        # PostgreSQL (for advanced data operations)
        if os.getenv('PGHOST'):
            self.env['PGHOST'] = os.getenv('PGHOST')
            self.env['PGUSER'] = os.getenv('PGUSER', '')
            self.env['PGPASSWORD'] = os.getenv('PGPASSWORD', '')
            self.env['PGDATABASE'] = os.getenv('PGDATABASE', '')
            self.env['PGPORT'] = os.getenv('PGPORT', '5432')
        
        # Automaton/Conway API (for autonomous trading)
        if os.getenv('CONWAY_API_URL'):
            self.env['CONWAY_API_URL'] = os.getenv('CONWAY_API_URL')
            self.env['CONWAY_API_KEY'] = os.getenv('CONWAY_API_KEY', '')
        
        # Telegram (for notifications)
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            self.env['TELEGRAM_BOT_TOKEN'] = os.getenv('TELEGRAM_BOT_TOKEN')
        
        # Encryption & Security
        if os.getenv('ENCRYPTION_KEY'):
            self.env['ENCRYPTION_KEY'] = os.getenv('ENCRYPTION_KEY')
        
        if os.getenv('SESSION_SECRET'):
            self.env['SESSION_SECRET'] = os.getenv('SESSION_SECRET')
        
        logger.info("OpenClaw CLI Bridge initialized with full API access")
    
    def _run_command(
        self,
        args: List[str],
        timeout: int = 30,
        capture_output: bool = True
    ) -> Dict[str, Any]:
        """
        Run openclaw CLI command
        
        Args:
            args: Command arguments (without 'openclaw' prefix)
            timeout: Command timeout in seconds
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            Dict with stdout, stderr, returncode
        """
        try:
            # On Windows, use openclaw.cmd for proper execution
            openclaw_cmd = 'openclaw.cmd' if os.name == 'nt' else 'openclaw'
            cmd = [openclaw_cmd] + args
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                env=self.env,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                shell=True  # Required on Windows for .cmd files
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout after {timeout}s")
            return {
                'success': False,
                'error': 'Command timeout',
                'timeout': timeout
            }
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_health(self) -> bool:
        """
        Check if OpenClaw CLI is working
        
        Returns:
            True if CLI is accessible
        """
        result = self._run_command(['--version'], timeout=5)
        return result.get('success', False)
    
    def get_version(self) -> Optional[str]:
        """Get OpenClaw version"""
        result = self._run_command(['--version'], timeout=5)
        if result.get('success'):
            return result.get('stdout', '').strip()
        return None
    
    def send_message(
        self,
        target: str,
        message: str,
        channel: str = 'telegram'
    ) -> Dict[str, Any]:
        """
        Send message via OpenClaw
        
        Args:
            target: Target user/chat (phone number, username, etc)
            message: Message to send
            channel: Channel type (telegram, whatsapp, discord)
            
        Returns:
            Dict with result
        """
        args = [
            'message', 'send',
            '--channel', channel,
            '--target', target,
            '--message', message,
            '--json'
        ]
        
        result = self._run_command(args, timeout=60)
        
        if result.get('success'):
            try:
                # Try to parse JSON output
                output = result.get('stdout', '{}')
                data = json.loads(output)
                return {'success': True, 'data': data}
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'message': 'Message sent',
                    'raw_output': result.get('stdout')
                }
        else:
            return {
                'success': False,
                'error': result.get('stderr') or result.get('error')
            }
    
    def run_agent_task(
        self,
        task: str,
        target: Optional[str] = None,
        deliver: bool = False
    ) -> Dict[str, Any]:
        """
        Run agent task via OpenClaw
        
        Args:
            task: Task description for agent
            target: Optional target to send result to
            deliver: Whether to deliver result to target
            
        Returns:
            Dict with agent response
        """
        args = ['agent', '--message', task]
        
        if target:
            args.extend(['--to', target])
        
        if deliver:
            args.append('--deliver')
        
        args.append('--json')
        
        result = self._run_command(args, timeout=300)  # 5 min for complex tasks
        
        if result.get('success'):
            try:
                output = result.get('stdout', '{}')
                data = json.loads(output)
                return {'success': True, 'response': data}
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'response': result.get('stdout'),
                    'raw': True
                }
        else:
            return {
                'success': False,
                'error': result.get('stderr') or result.get('error')
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get OpenClaw status
        
        Returns:
            Dict with status info
        """
        result = self._run_command(['status', '--json'], timeout=10)
        
        if result.get('success'):
            try:
                output = result.get('stdout', '{}')
                data = json.loads(output)
                return {'success': True, 'status': data}
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'status': 'running',
                    'raw_output': result.get('stdout')
                }
        else:
            return {
                'success': False,
                'error': result.get('stderr') or result.get('error')
            }
    
    def list_skills(self) -> Dict[str, Any]:
        """
        List available OpenClaw skills
        
        Returns:
            Dict with skills list
        """
        result = self._run_command(['skills', '--json'], timeout=10)
        
        if result.get('success'):
            try:
                output = result.get('stdout', '{}')
                data = json.loads(output)
                return {'success': True, 'skills': data}
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'skills': result.get('stdout'),
                    'raw': True
                }
        else:
            return {
                'success': False,
                'error': result.get('stderr') or result.get('error')
            }
    
    def search_docs(self, query: str) -> Dict[str, Any]:
        """
        Search OpenClaw documentation
        
        Args:
            query: Search query
            
        Returns:
            Dict with search results
        """
        result = self._run_command(['docs', query], timeout=30)
        
        if result.get('success'):
            return {
                'success': True,
                'results': result.get('stdout')
            }
        else:
            return {
                'success': False,
                'error': result.get('stderr') or result.get('error')
            }
    
    def run_doctor(self) -> Dict[str, Any]:
        """
        Run OpenClaw health checks
        
        Returns:
            Dict with health check results
        """
        result = self._run_command(['doctor'], timeout=30)
        
        return {
            'success': result.get('success'),
            'report': result.get('stdout'),
            'issues': result.get('stderr')
        }


# Singleton instance
_cli_bridge = None

def get_openclaw_cli_bridge() -> OpenClawCLIBridge:
    """Get singleton instance of OpenClaw CLI bridge"""
    global _cli_bridge
    if _cli_bridge is None:
        _cli_bridge = OpenClawCLIBridge()
    return _cli_bridge
