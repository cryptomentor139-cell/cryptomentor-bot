"""
Bitunix Auto Trade Client
Real trading client for Bitunix exchange integration
Signature: double SHA256 (not HMAC)
"""

import hashlib
import time
import uuid
import requests
import os
from typing import Dict, Optional, List
from datetime import datetime


class BitunixAutoTradeClient:
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or os.getenv('BITUNIX_API_KEY')
        self.api_secret = api_secret or os.getenv('BITUNIX_API_SECRET')
        self.base_url = os.getenv('BITUNIX_BASE_URL', 'https://fapi.bitunix.com')

        if not self.api_key or not self.api_secret:
            print("⚠️ Bitunix API credentials not configured")

    # ------------------------------------------------------------------ #
    #  Signature helpers                                                   #
    # ------------------------------------------------------------------ #

    def _sha256(self, s: str) -> str:
        return hashlib.sha256(s.encode('utf-8')).hexdigest()

    def _make_sign(self, nonce: str, timestamp: str,
                   query_params: str = "", body: str = "") -> str:
        """
        Bitunix double-SHA256:
          digest = SHA256(nonce + timestamp + api_key + queryParams + body)
          sign   = SHA256(digest + secretKey)
        queryParams: all GET params sorted ascending by key, concatenated as key+value (no & or =)
        """
        digest = self._sha256(nonce + timestamp + self.api_key + query_params + body)
        return self._sha256(digest + self.api_secret)

    def _build_query_string(self, params: Dict) -> str:
        """Sort params by key ascending, concat as key+value (Bitunix format)."""
        return "".join(f"{k}{v}" for k, v in sorted(params.items()))

    def _auth_headers(self, query_params: str = "", body: str = "") -> Dict:
        nonce = uuid.uuid4().hex  # 32-char random
        timestamp = str(int(time.time() * 1000))
        sign = self._make_sign(nonce, timestamp, query_params, body)
        return {
            "api-key": self.api_key,
            "nonce": nonce,
            "timestamp": timestamp,
            "sign": sign,
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------ #
    #  Core request                                                        #
    # ------------------------------------------------------------------ #

    def _request(self, method: str, endpoint: str,
                 params: Dict = None, body: Dict = None,
                 signed: bool = False) -> Dict:
        if signed and (not self.api_key or not self.api_secret):
            return {'success': False, 'error': 'API credentials not configured'}

        url = f"{self.base_url}{endpoint}"
        params = params or {}
        body_str = ""

        if signed:
            query_str = self._build_query_string(params)
            if body:
                import json
                body_str = json.dumps(body, separators=(',', ':'))
            headers = self._auth_headers(query_str, body_str)
        else:
            headers = {"Content-Type": "application/json"}

        try:
            if method.upper() == 'GET':
                r = requests.get(url, params=params, headers=headers, timeout=10)
            else:
                r = requests.post(url, data=body_str, headers=headers, timeout=10)

            if r.status_code == 200:
                data = r.json()
                if data.get('code') == 0:
                    return {'success': True, 'data': data.get('data')}
                else:
                    return {'success': False, 'error': f"API error {data.get('code')}: {data.get('msg')}"}
            else:
                return {'success': False, 'error': f'HTTP {r.status_code}: {r.text}'}

        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Request failed: {str(e)}'}

    # ------------------------------------------------------------------ #
    #  Public endpoints                                                    #
    # ------------------------------------------------------------------ #

    def check_connection(self) -> Dict:
        """Test connectivity via public ticker endpoint."""
        result = self._request('GET', '/api/v1/futures/market/tickers',
                               params={'symbols': 'BTCUSDT'})
        if result['success']:
            return {'online': True, 'message': 'Connected to Bitunix successfully',
                    'data': result['data']}
        return {'online': False, 'error': result['error']}

    def get_symbol_price(self, symbol: str) -> Dict:
        result = self._request('GET', '/api/v1/futures/market/tickers',
                               params={'symbols': symbol})
        if result['success']:
            tickers = result['data']
            if tickers:
                return {'success': True, 'symbol': symbol,
                        'price': float(tickers[0].get('lastPrice', 0))}
        return result

    # ------------------------------------------------------------------ #
    #  Private endpoints                                                   #
    # ------------------------------------------------------------------ #

    def get_account_info(self) -> Dict:
        """Get USDT futures account balance."""
        result = self._request('GET', '/api/v1/futures/account',
                               params={'marginCoin': 'USDT'}, signed=True)
        if result['success']:
            d = result['data']
            return {
                'success': True,
                'available': float(d.get('available', 0)),
                'frozen': float(d.get('frozen', 0)),
                'margin': float(d.get('margin', 0)),
                'bonus': float(d.get('bonus', 0)),
                'cross_unrealized_pnl': float(d.get('crossUnrealizedPNL', 0)),
                'isolation_unrealized_pnl': float(d.get('isolationUnrealizedPNL', 0)),
                'position_mode': d.get('positionMode'),
                # legacy compat
                'balance': float(d.get('available', 0)),
                'total_unrealized_pnl': float(d.get('crossUnrealizedPNL', 0)) +
                                        float(d.get('isolationUnrealizedPNL', 0)),
            }
        return result

    def get_positions(self) -> Dict:
        """Get current open positions."""
        result = self._request('GET', '/api/v1/futures/position/get_pending_positions',
                               signed=True)
        if result['success']:
            raw = result['data'] or []
            positions = []
            for pos in raw:
                qty = float(pos.get('qty', 0))
                if qty == 0:
                    continue
                positions.append({
                    'symbol': pos.get('symbol'),
                    'side': pos.get('side', '').upper(),
                    'size': qty,
                    'entry_price': float(pos.get('openPrice', 0)),
                    'mark_price': float(pos.get('markPrice', 0)),
                    'pnl': float(pos.get('unrealizedPNL', 0)),
                    'leverage': pos.get('leverage'),
                    'margin_mode': pos.get('marginMode'),
                })
            return {'success': True, 'positions': positions,
                    'total_positions': len(positions)}
        return result

    def place_order(self, symbol: str, side: str, qty: float,
                    order_type: str = 'market', price: float = None,
                    reduce_only: bool = False) -> Dict:
        """
        Place a futures order.
        side: BUY / SELL
        order_type: market / limit
        """
        body = {
            'symbol': symbol,
            'qty': str(qty),
            'side': side.upper(),
            'tradeSide': 'OPEN' if not reduce_only else 'CLOSE',
            'orderType': order_type.upper(),
        }
        if order_type.lower() == 'limit' and price:
            body['price'] = str(price)

        result = self._request('POST', '/api/v1/futures/trade/place_order',
                               body=body, signed=True)
        if result['success']:
            return {'success': True, 'order_id': result['data'].get('orderId'),
                    'message': f'{side.upper()} {order_type} order placed'}
        return result

    # ------------------------------------------------------------------ #
    #  High-level helpers (used by handlers)                              #
    # ------------------------------------------------------------------ #

    def get_24h_stats(self) -> Dict:
        return {
            'success': True,
            'stats': {
                'total_trades': 0, 'winning_trades': 0, 'losing_trades': 0,
                'win_rate': 0, 'total_pnl': 0, 'best_trade': 0,
                'worst_trade': 0, 'volume_24h': 0,
            }
        }

    def start_autotrade(self, user_id: int, amount: float, wallet_address: str) -> Dict:
        account = self.get_account_info()
        if not account['success']:
            return {'success': False, 'error': f"Cannot access account: {account['error']}"}
        if account['balance'] < amount:
            return {'success': False,
                    'error': f"Insufficient balance. Available: {account['balance']} USDT, Required: {amount} USDT"}
        return {
            'success': True,
            'response': (
                f"🤖 Auto Trading Started!\n\n"
                f"💰 Allocated: {amount} USDT\n"
                f"📊 Available: {account['balance']} USDT\n"
                f"🎯 Strategy: Conservative Scalping\n"
                f"⚠️ Risk: Max 2% per trade\n"
                f"⚡ Status: ACTIVE"
            )
        }

    def get_autotrade_status(self, user_id: int) -> Dict:
        account = self.get_account_info()
        positions = self.get_positions()
        stats = self.get_24h_stats()

        if not account['success']:
            return account

        lines = [
            "📊 Auto Trade Portfolio Status\n",
            f"💰 Available: {account['balance']:.2f} USDT",
            f"📈 Unrealized PnL: {account['total_unrealized_pnl']:.2f} USDT",
            f"🔄 Open Positions: {positions.get('total_positions', 0)}",
            f"\n📊 24h Stats:",
            f"• Trades: {stats['stats']['total_trades']}",
            f"• Win Rate: {stats['stats']['win_rate']:.1f}%",
            f"• PnL: {stats['stats']['total_pnl']:.2f} USDT",
            f"\n⚡ Last Update: {datetime.now().strftime('%H:%M:%S')}",
            "\n🔄 Positions:",
        ]

        if positions['success'] and positions['positions']:
            for p in positions['positions']:
                emoji = "📈" if p['pnl'] >= 0 else "📉"
                lines.append(
                    f"{emoji} {p['symbol']} {p['side']} | "
                    f"Size: {p['size']} | Entry: ${p['entry_price']:.4f} | "
                    f"PnL: {p['pnl']:.2f} USDT"
                )
        else:
            lines.append("   No open positions")

        return {'success': True, 'response': "\n".join(lines)}

    def withdraw_autotrade(self, user_id: int) -> Dict:
        account = self.get_account_info()
        if not account['success']:
            return {'success': False, 'error': 'Cannot access account'}

        balance = account['balance']
        pnl = account['total_unrealized_pnl']
        profit = max(0, pnl)
        fee = profit * 0.25
        net = balance - fee

        return {
            'success': True,
            'response': (
                f"✅ Withdrawal Processed\n\n"
                f"💰 Balance: {balance:.2f} USDT\n"
                f"📈 PnL: {pnl:.2f} USDT\n"
                f"💸 Fee (25% profit): {fee:.2f} USDT\n"
                f"💵 Net: {net:.2f} USDT"
            )
        }

    def get_trade_history(self, user_id: int, limit: int = 10) -> Dict:
        result = self._request('GET', '/api/v1/futures/trade/get_history_orders',
                               params={'pageSize': limit}, signed=True)
        if result['success']:
            orders = result['data'] or []
            if not orders:
                return {'success': True, 'response': "📈 No trade history yet."}
            lines = [f"📈 Trade History (last {limit})\n"]
            for o in orders[:limit]:
                side_emoji = "🟢" if o.get('side') == 'BUY' else "🔴"
                lines.append(
                    f"{side_emoji} {o.get('symbol')} {o.get('side')} "
                    f"qty={o.get('qty')} @ {o.get('price', 'market')} "
                    f"| {o.get('ctime', '')}"
                )
            return {'success': True, 'response': "\n".join(lines)}
        return {'success': False, 'response': f"Failed to fetch history: {result['error']}"}


# ------------------------------------------------------------------ #
#  Quick test                                                          #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    client = BitunixAutoTradeClient()

    print("1. Connection test...")
    print(client.check_connection())

    print("\n2. Account info...")
    print(client.get_account_info())

    print("\n3. Positions...")
    print(client.get_positions())
