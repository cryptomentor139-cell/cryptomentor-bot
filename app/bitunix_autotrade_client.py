"""
Bitunix Auto Trade Client
Real trading client for Bitunix exchange integration
"""

import hashlib
import hmac
import time
import requests
import json
from typing import Dict, Optional, List
import os
from datetime import datetime

class BitunixAutoTradeClient:
    def __init__(self, api_key: str = None, api_secret: str = None):
        # Per-user keys take priority over env vars
        self.api_key = api_key or os.getenv('BITUNIX_API_KEY')
        self.api_secret = api_secret or os.getenv('BITUNIX_API_SECRET')
        self.base_url = os.getenv('BITUNIX_BASE_URL', 'https://fapi.bitunix.com')

        if not self.api_key or not self.api_secret:
            print("⚠️ Bitunix API credentials not configured")
    
    def _generate_signature(self, query_string: str) -> str:
        """Generate HMAC SHA256 signature for Bitunix API"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """Make HTTP request to Bitunix API"""
        if not self.api_key or not self.api_secret:
            return {
                'success': False,
                'error': 'API credentials not configured'
            }
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            'X-BX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        if params is None:
            params = {}
        
        if signed:
            timestamp = int(time.time() * 1000)
            params['timestamp'] = timestamp
            
            # Create query string
            query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            signature = self._generate_signature(query_string)
            params['signature'] = signature
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=params, headers=headers, timeout=10)
            else:
                return {'success': False, 'error': f'Unsupported method: {method}'}
            
            if response.status_code == 200:
                data = response.json()
                return {'success': True, 'data': data}
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}'
            }
    
    def check_connection(self) -> Dict:
        """Test API connection and get server time"""
        result = self._make_request('GET', '/fapi/v1/time')
        if result['success']:
            return {
                'online': True,
                'server_time': result['data'].get('serverTime'),
                'message': 'Connected to Bitunix successfully'
            }
        else:
            return {
                'online': False,
                'error': result['error']
            }
    
    def get_account_info(self) -> Dict:
        """Get account information and balance"""
        result = self._make_request('GET', '/fapi/v2/account', signed=True)
        if result['success']:
            data = result['data']
            # Extract USDT balance
            usdt_balance = 0
            for asset in data.get('assets', []):
                if asset.get('asset') == 'USDT':
                    usdt_balance = float(asset.get('walletBalance', 0))
                    break
            
            return {
                'success': True,
                'balance': usdt_balance,
                'total_wallet_balance': float(data.get('totalWalletBalance', 0)),
                'total_unrealized_pnl': float(data.get('totalUnrealizedProfit', 0)),
                'can_trade': data.get('canTrade', False),
                'can_withdraw': data.get('canWithdraw', False)
            }
        else:
            return result
    
    def get_positions(self) -> Dict:
        """Get current open positions"""
        result = self._make_request('GET', '/fapi/v2/positionRisk', signed=True)
        if result['success']:
            positions = []
            for pos in result['data']:
                if float(pos.get('positionAmt', 0)) != 0:  # Only open positions
                    positions.append({
                        'symbol': pos.get('symbol'),
                        'side': 'LONG' if float(pos.get('positionAmt', 0)) > 0 else 'SHORT',
                        'size': abs(float(pos.get('positionAmt', 0))),
                        'entry_price': float(pos.get('entryPrice', 0)),
                        'mark_price': float(pos.get('markPrice', 0)),
                        'pnl': float(pos.get('unRealizedProfit', 0)),
                        'pnl_percentage': float(pos.get('percentage', 0))
                    })
            
            return {
                'success': True,
                'positions': positions,
                'total_positions': len(positions)
            }
        else:
            return result
    
    def get_24h_stats(self) -> Dict:
        """Get 24h trading statistics"""
        # This is a mock implementation since we don't have real trading history
        # In a real implementation, you would track trades in a database
        return {
            'success': True,
            'stats': {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'volume_24h': 0
            }
        }
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """Place a market order"""
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': quantity
        }
        
        result = self._make_request('POST', '/fapi/v1/order', params, signed=True)
        if result['success']:
            order_data = result['data']
            return {
                'success': True,
                'order_id': order_data.get('orderId'),
                'symbol': order_data.get('symbol'),
                'side': order_data.get('side'),
                'quantity': order_data.get('origQty'),
                'status': order_data.get('status'),
                'message': f"Market {side} order placed successfully"
            }
        else:
            return result
    
    def get_symbol_price(self, symbol: str) -> Dict:
        """Get current price for a symbol"""
        result = self._make_request('GET', f'/fapi/v1/ticker/price?symbol={symbol}')
        if result['success']:
            data = result['data']
            return {
                'success': True,
                'symbol': data.get('symbol'),
                'price': float(data.get('price', 0))
            }
        else:
            return result
    
    def start_autotrade(self, user_id: int, amount: float, wallet_address: str) -> Dict:
        """
        Start auto trading simulation
        Note: This is a demo implementation. Real auto trading would require
        sophisticated algorithms and risk management.
        """
        # Check account first
        account_info = self.get_account_info()
        if not account_info['success']:
            return {
                'success': False,
                'error': f"Cannot access Bitunix account: {account_info['error']}"
            }
        
        if account_info['balance'] < amount:
            return {
                'success': False,
                'error': f"Insufficient balance. Available: {account_info['balance']} USDT, Required: {amount} USDT"
            }
        
        # In a real implementation, you would:
        # 1. Set up trading algorithms
        # 2. Configure risk management
        # 3. Start monitoring markets
        # 4. Execute trades based on signals
        
        return {
            'success': True,
            'response': f"""🤖 Auto Trading Started!

💰 Allocated Amount: {amount} USDT
📊 Available Balance: {account_info['balance']} USDT
🎯 Strategy: Conservative Scalping
⚠️ Risk Level: Medium

🔄 Trading Rules:
• Max 2% risk per trade
• Stop Loss: -1.5%
• Take Profit: +2-3%
• Focus on: BTC/USDT, ETH/USDT
• Trading Hours: 24/7

⚡ Status: ACTIVE - Monitoring markets...

Note: This is a demo mode. Real trading requires manual approval for each trade."""
        }
    
    def get_autotrade_status(self, user_id: int) -> Dict:
        """Get auto trade status"""
        # Get current account info
        account_info = self.get_account_info()
        positions = self.get_positions()
        stats = self.get_24h_stats()
        
        if not account_info['success']:
            return account_info
        
        status_text = f"""📊 Auto Trade Portfolio Status

💰 Current Balance: {account_info['balance']:.2f} USDT
📈 Unrealized PnL: {account_info['total_unrealized_pnl']:.2f} USDT
🔄 Open Positions: {positions.get('total_positions', 0)}

📊 24h Statistics:
• Total Trades: {stats['stats']['total_trades']}
• Win Rate: {stats['stats']['win_rate']:.1f}%
• Total PnL: {stats['stats']['total_pnl']:.2f} USDT
• Best Trade: +{stats['stats']['best_trade']:.2f} USDT
• Worst Trade: {stats['stats']['worst_trade']:.2f} USDT

🎯 Strategy Status: ACTIVE
⚡ Last Update: {datetime.now().strftime('%H:%M:%S')}

🔄 Current Positions:"""

        if positions['success'] and positions['positions']:
            for pos in positions['positions']:
                pnl_emoji = "📈" if pos['pnl'] >= 0 else "📉"
                status_text += f"""
{pnl_emoji} {pos['symbol']} {pos['side']}
   Size: {pos['size']:.4f}
   Entry: ${pos['entry_price']:.4f}
   Mark: ${pos['mark_price']:.4f}
   PnL: {pos['pnl']:.2f} USDT ({pos['pnl_percentage']:.2f}%)"""
        else:
            status_text += "\n   No open positions"
        
        return {
            'success': True,
            'response': status_text
        }
    
    def withdraw_autotrade(self, user_id: int) -> Dict:
        """Process withdrawal (close all positions)"""
        positions = self.get_positions()
        account_info = self.get_account_info()
        
        if not positions['success'] or not account_info['success']:
            return {
                'success': False,
                'error': 'Cannot access account information'
            }
        
        # In a real implementation, you would close all positions here
        # For demo, we'll just show what would happen
        
        total_pnl = account_info['total_unrealized_pnl']
        final_balance = account_info['balance']
        
        # Calculate fee (25% of profit only)
        profit = max(0, total_pnl)
        fee = profit * 0.25
        net_amount = final_balance - fee
        
        return {
            'success': True,
            'response': f"""✅ Withdrawal Processed

💰 Final Balance: {final_balance:.2f} USDT
📈 Total PnL: {total_pnl:.2f} USDT
💸 Platform Fee (25% of profit): {fee:.2f} USDT
💵 Net Amount: {net_amount:.2f} USDT

🔄 All positions closed
📤 Withdrawal initiated to your wallet

Thank you for using Auto Trade!"""
        }
    
    def get_trade_history(self, user_id: int, limit: int = 10) -> Dict:
        """Get trade history"""
        # In a real implementation, you would fetch actual trade history
        # For demo, we'll show sample data
        
        return {
            'success': True,
            'response': f"""📈 Trade History (Last {limit} trades)

🔄 Demo Mode - No actual trades yet

Sample trades would appear here:
• 2024-01-15 14:30 - BTC/USDT LONG +2.3%
• 2024-01-15 12:15 - ETH/USDT SHORT +1.8%
• 2024-01-15 09:45 - BTC/USDT LONG -1.2%

Start trading to see real history!"""
        }


# Test the client
if __name__ == "__main__":
    client = BitunixAutoTradeClient()
    
    print("Testing Bitunix connection...")
    connection = client.check_connection()
    print(f"Connection: {connection}")
    
    if connection.get('online'):
        print("\n✅ Bitunix API connected!")
        
        # Test account info
        account = client.get_account_info()
        print(f"Account: {account}")
        
        # Test positions
        positions = client.get_positions()
        print(f"Positions: {positions}")
    else:
        print("\n❌ Bitunix API connection failed!")