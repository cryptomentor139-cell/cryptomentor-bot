# Conway Cloud API Integration
# Handles all interactions with Conway Automaton API

import os
import requests
import time
from typing import Dict, Optional, Any
from datetime import datetime

class ConwayIntegration:
    """
    Conway Cloud API client for Automaton integration
    
    Features:
    - Generate deposit addresses for agents
    - Check credit balances
    - Transfer credits
    - Spawn autonomous agents
    - Query agent status
    - Retry logic with exponential backoff
    """
    
    def __init__(self):
        self.api_url = os.getenv('CONWAY_API_URL', 'https://api.conway.tech')
        self.api_key = os.getenv('CONWAY_API_KEY')
        
        if not self.api_key:
            raise ValueError("CONWAY_API_KEY environment variable not set")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1  # seconds
        self.max_delay = 30  # seconds
        
        print(f"✅ Conway API client initialized: {self.api_url}")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and exponential backoff
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body (for POST/PUT)
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            Exception: After max retries exceeded
        """
        url = f"{self.api_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=30
                )
                
                # Success
                if response.status_code in [200, 201]:
                    return response.json()
                
                # Client error (don't retry)
                if 400 <= response.status_code < 500:
                    error_msg = f"Conway API client error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('message', 'Unknown error')}"
                    except:
                        error_msg += f" - {response.text}"
                    
                    print(f"❌ {error_msg}")
                    raise Exception(error_msg)
                
                # Server error (retry)
                if response.status_code >= 500:
                    print(f"⚠️ Conway API server error: {response.status_code} (attempt {attempt + 1}/{self.max_retries})")
                    
                    if attempt < self.max_retries - 1:
                        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                        print(f"⏳ Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception(f"Conway API server error after {self.max_retries} retries")
            
            except requests.exceptions.Timeout:
                print(f"⚠️ Conway API timeout (attempt {attempt + 1}/{self.max_retries})")
                
                if attempt < self.max_retries - 1:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    print(f"⏳ Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(f"Conway API timeout after {self.max_retries} retries")
            
            except requests.exceptions.ConnectionError:
                print(f"⚠️ Conway API connection error (attempt {attempt + 1}/{self.max_retries})")
                
                if attempt < self.max_retries - 1:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    print(f"⏳ Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(f"Conway API connection error after {self.max_retries} retries")
            
            except Exception as e:
                print(f"❌ Conway API unexpected error: {e}")
                raise
        
        raise Exception("Conway API request failed after all retries")
    
    def health_check(self) -> bool:
        """
        Check if Conway API is accessible
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self._make_request('GET', '/api/v1/health')
            return response.get('status') == 'ok'
        except Exception as e:
            print(f"❌ Conway API health check failed: {e}")
            return False
    
    def generate_deposit_address(self, user_id: int, agent_name: str) -> Optional[str]:
        """
        Generate a unique deposit address for an agent
        
        Conway provides USDC deposit addresses on Base network
        
        Args:
            user_id: Telegram user ID
            agent_name: Name for the agent
            
        Returns:
            Deposit address (0x...) or None if failed
        """
        try:
            data = {
                'user_id': user_id,
                'agent_name': agent_name,
                'network': 'base',
                'token': 'USDC'
            }
            
            response = self._make_request('POST', '/api/v1/agents/address', data=data)
            
            address = response.get('deposit_address')
            if address:
                print(f"✅ Generated deposit address for user {user_id}: {address}")
                return address
            else:
                print(f"❌ No deposit address in response: {response}")
                return None
        
        except Exception as e:
            print(f"❌ Failed to generate deposit address: {e}")
            return None
    
    def get_credit_balance(self, deposit_address: str) -> Optional[float]:
        """
        Get current credit balance for an agent
        
        Args:
            deposit_address: Agent's deposit address
            
        Returns:
            Credit balance or None if failed
        """
        try:
            params = {'address': deposit_address}
            response = self._make_request('GET', '/api/v1/agents/balance', params=params)
            
            balance = response.get('balance')
            if balance is not None:
                print(f"✅ Balance for {deposit_address}: {balance} credits")
                return float(balance)
            else:
                print(f"❌ No balance in response: {response}")
                return None
        
        except Exception as e:
            print(f"❌ Failed to get credit balance: {e}")
            return None
    
    def spawn_agent(
        self, 
        deposit_address: str, 
        agent_name: str,
        genesis_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Spawn a new autonomous trading agent
        
        Args:
            deposit_address: Agent's deposit address (for funding)
            agent_name: Name for the agent
            genesis_prompt: Initial instructions for the agent
            
        Returns:
            Dict with 'success', 'agent_id', 'message'
        """
        try:
            data = {
                'deposit_address': deposit_address,
                'agent_name': agent_name,
                'genesis_prompt': genesis_prompt or "You are an autonomous trading agent. Trade wisely and maximize profits."
            }
            
            response = self._make_request('POST', '/api/v1/agents/spawn', data=data)
            
            if response.get('success'):
                agent_id = response.get('agent_id')
                print(f"✅ Agent spawned successfully: {agent_id}")
                return {
                    'success': True,
                    'agent_id': agent_id,
                    'message': 'Agent spawned successfully'
                }
            else:
                error_msg = response.get('message', 'Unknown error')
                print(f"❌ Failed to spawn agent: {error_msg}")
                return {
                    'success': False,
                    'agent_id': None,
                    'message': error_msg
                }
        
        except Exception as e:
            print(f"❌ Failed to spawn agent: {e}")
            return {
                'success': False,
                'agent_id': None,
                'message': str(e)
            }
    
    def get_agent_status(self, deposit_address: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of an agent
        
        Args:
            deposit_address: Agent's deposit address
            
        Returns:
            Dict with agent status or None if failed
        """
        try:
            params = {'address': deposit_address}
            response = self._make_request('GET', '/api/v1/agents/status', params=params)
            
            if response.get('success'):
                status = {
                    'is_active': response.get('is_active', False),
                    'balance': response.get('balance', 0),
                    'last_active': response.get('last_active'),
                    'total_trades': response.get('total_trades', 0),
                    'total_profit': response.get('total_profit', 0),
                    'total_loss': response.get('total_loss', 0)
                }
                print(f"✅ Agent status retrieved: {deposit_address}")
                return status
            else:
                print(f"❌ Failed to get agent status: {response.get('message')}")
                return None
        
        except Exception as e:
            print(f"❌ Failed to get agent status: {e}")
            return None
    
    def get_agent_transactions(
        self, 
        deposit_address: str, 
        limit: int = 20
    ) -> Optional[list]:
        """
        Get recent transactions for an agent
        
        Args:
            deposit_address: Agent's deposit address
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions or None if failed
        """
        try:
            params = {
                'address': deposit_address,
                'limit': limit
            }
            response = self._make_request('GET', '/api/v1/agents/transactions', params=params)
            
            if response.get('success'):
                transactions = response.get('transactions', [])
                print(f"✅ Retrieved {len(transactions)} transactions for {deposit_address}")
                return transactions
            else:
                print(f"❌ Failed to get transactions: {response.get('message')}")
                return None
        
        except Exception as e:
            print(f"❌ Failed to get transactions: {e}")
            return None


# Singleton instance
_conway_client = None

def get_conway_client() -> ConwayIntegration:
    """
    Get singleton Conway API client instance
    
    Returns:
        ConwayIntegration instance
    """
    global _conway_client
    if _conway_client is None:
        _conway_client = ConwayIntegration()
    return _conway_client
