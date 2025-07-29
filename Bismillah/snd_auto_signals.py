import asyncio
import time
from datetime import datetime
from crypto_api import CryptoAPI
from database import Database

class SnDAutoSignals:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.crypto_api = CryptoAPI()
        self.db = Database()
        self.is_running = False
        self.scan_interval = 1800  # 30 minutes

        # Enhanced altcoin list with high volume potential
        self.target_symbols = [
            # Small/Medium cap with high volatility
            'ONDO', 'SEI', 'PEPE', 'MOODENG', 'SHIB', 'FLOKI', 
            'WIF', 'BONK', 'JUP', 'PYTH', 'RENDER', 'INJ', 
            'SUI', 'APT', 'OP', 'ARB', 'TIA', 'POPCAT', 
            'PENDLE', 'EIGEN', 'DOGE', 'MATIC', 'FET', 'AGIX',
            'GALA', 'SAND', 'MANA', 'AXS', 'CHZ', 'ENJ',
            # Additional promising altcoins
            'RUNE', 'KAVA', 'ALPHA', 'DYDX', 'GMX', 'PERP',
            'CRV', 'CVX', 'LDO', 'RPL', 'FXS', 'FRAX'
        ]

        self.min_confidence = 70  # Minimum confidence level
        self.last_scan_time = 0

    async def start_auto_scanner(self):
        """Start automatic SnD signal scanner"""
        if self.is_running:
            print("⚠️ Auto scanner already running")
            return

        self.is_running = True
        print(f"🚀 Starting enhanced SnD auto scanner for {len(self.target_symbols)} altcoins...")
        print(f"📊 Scan interval: {self.scan_interval} seconds ({self.scan_interval/60:.1f} minutes)")

        while self.is_running:
            try:
                await self.scan_and_send_signals()
                await asyncio.sleep(self.scan_interval)
            except Exception as e:
                print(f"❌ Error in auto scanner: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def stop_auto_scanner(self):
        """Stop automatic scanner"""
        self.is_running = False
        print("🛑 Enhanced SnD auto scanner stopped")

    async def scan_and_send_signals(self):
        """Scan symbols and send high-confidence signals"""
        scan_start = time.time()
        print(f"🔍 Scanning {len(self.target_symbols)} altcoins for enhanced SnD signals...")

        high_confidence_signals = []
        total_scanned = 0

        for symbol in self.target_symbols:
            try:
                signal = await self.analyze_enhanced_snd_signal(symbol)
                total_scanned += 1

                if signal and signal['confidence'] >= self.min_confidence:
                    high_confidence_signals.append(signal)
                    print(f"✅ High confidence signal found: {symbol} - {signal['confidence']:.1f}% ({signal['direction']})")

                # Rate limiting
                await asyncio.sleep(1)

            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
                continue

        scan_duration = time.time() - scan_start
        print(f"📊 Scan completed: {total_scanned}/{len(self.target_symbols)} coins analyzed in {scan_duration:.1f}s")

        if high_confidence_signals:
            print(f"🎯 Found {len(high_confidence_signals)} high-confidence signals")
            await self.send_signals_to_eligible_users(high_confidence_signals)
        else:
            print("📊 No high-confidence signals found in this scan")

        self.last_scan_time = time.time()

    async def analyze_enhanced_snd_signal(self, symbol):
        """Analyze enhanced SnD for a single symbol"""
        try:
            # Get comprehensive data
            snd_analysis = self.crypto_api.analyze_supply_demand(symbol, '1h')
            price_data = self.crypto_api.get_coinapi_price(symbol, force_refresh=True)
            futures_data = self.crypto_api.get_binance_long_short_ratio(symbol)

            if 'error' in snd_analysis or 'error' in price_data:
                return None

            current_price = price_data.get('price', 0)
            signals = snd_analysis.get('signals', [])
            confidence_score = snd_analysis.get('confidence_score', 50)

            if not signals or confidence_score < self.min_confidence:
                return None

            # Get the best signal
            best_signal = max(signals, key=lambda x: x.get('confidence', 0))

            # Enhanced confidence calculation
            enhanced_confidence = self._calculate_enhanced_confidence(
                best_signal, snd_analysis, futures_data, current_price
            )

            if enhanced_confidence < self.min_confidence:
                return None

            # Get market structure
            market_structure = snd_analysis.get('market_structure', {})

            # Calculate position sizing recommendation
            risk_level = self._calculate_risk_level(enhanced_confidence, market_structure)

            return {
                'symbol': symbol,
                'direction': best_signal['direction'],
                'entry_price': best_signal['entry_price'],
                'stop_loss': best_signal['stop_loss'],
                'take_profit_1': best_signal['take_profit_1'],
                'take_profit_2': best_signal['take_profit_2'],
                'confidence': enhanced_confidence,
                'risk_reward_ratio': best_signal['risk_reward_ratio'],
                'current_price': current_price,
                'trend': snd_analysis.get('trend', 'neutral'),
                'market_structure': market_structure['pattern'],
                'risk_level': risk_level,
                'timeframe': '1h',
                'scan_time': datetime.now().strftime('%H:%M:%S'),
                'reason': best_signal['reason'],
                'zone_strength': best_signal.get('zone_strength', 50)
            }

        except Exception as e:
            print(f"❌ Error in enhanced SnD analysis for {symbol}: {e}")
            return None

    def _calculate_enhanced_confidence(self, signal, snd_analysis, futures_data, current_price):
        """Calculate enhanced confidence with multiple factors"""
        base_confidence = signal.get('confidence', 50)

        # Factor 1: Risk/Reward ratio
        rr_ratio = signal.get('risk_reward_ratio', 1)
        if rr_ratio > 3:
            base_confidence += 15
        elif rr_ratio > 2:
            base_confidence += 10
        elif rr_ratio > 1.5:
            base_confidence += 5

        # Factor 2: Market structure alignment
        market_structure = snd_analysis.get('market_structure', {})
        if market_structure.get('pattern') in ['uptrend', 'downtrend']:
            base_confidence += 10
        elif market_structure.get('strength') == 'strong':
            base_confidence += 5

        # Factor 3: Trend score alignment
        trend_score = snd_analysis.get('trend_score', 1)
        if trend_score >= 2:
            base_confidence += 8
        elif trend_score >= 1:
            base_confidence += 4

        # Factor 4: Futures sentiment alignment
        if 'error' not in futures_data:
            long_ratio = futures_data.get('long_ratio', 50)
            direction = signal.get('direction', '')

            if direction == 'LONG' and long_ratio < 40:  # Contrarian bullish
                base_confidence += 8
            elif direction == 'SHORT' and long_ratio > 65:  # Contrarian bearish
                base_confidence += 8

        # Factor 5: Zone strength
        zone_strength = signal.get('zone_strength', 50)
        if zone_strength > 80:
            base_confidence += 10
        elif zone_strength > 60:
            base_confidence += 5

        return min(95, max(30, base_confidence))

    def _calculate_risk_level(self, confidence, market_structure):
        """Calculate risk level for position sizing"""
        if confidence >= 85 and market_structure.get('strength') == 'strong':
            return 'low'
        elif confidence >= 75:
            return 'medium'
        else:
            return 'high'

    async def send_signals_to_eligible_users(self, signals):
        """Send signals to admin and lifetime users only"""
        try:
            # Get eligible users (admin and lifetime)
            eligible_users = self.db.get_eligible_auto_signal_users()

            if not eligible_users:
                print("❌ No eligible users found for auto signals")
                return

            print(f"📤 Sending {len(signals)} signals to {len(eligible_users)} eligible users")

            # Format signals message
            signals_message = self._format_signals_message(signals)

            success_count = 0
            for user_data in eligible_users:
                user_id = user_data.get('user_id')
                if not user_id:
                    continue

                try:
                    await self.bot.application.bot.send_message(
                        chat_id=user_id,
                        text=signals_message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    success_count += 1
                    await asyncio.sleep(0.1)  # Rate limiting

                except Exception as e:
                    print(f"❌ Failed to send signal to user {user_id}: {e}")
                    continue

            print(f"✅ Auto signals sent to {success_count}/{len(eligible_users)} users")

            # Log the broadcast
            self.db.log_auto_signals_broadcast(len(signals), success_count, len(eligible_users))

        except Exception as e:
            print(f"❌ Error sending auto signals: {e}")

    def _format_signals_message(self, signals):
        """Format signals into a readable message"""
        message = f"""🚨 **AUTO SIGNALS - SUPPLY & DEMAND ANALYSIS**

🕐 **Scan Time**: {datetime.now().strftime('%H:%M:%S WIB')}
📊 **Signals Found**: {len(signals)}

"""

        for i, signal in enumerate(signals[:5], 1):  # Limit to top 5 signals
            direction_emoji = "🟢" if signal['direction'] == 'LONG' else "🔴"
            confidence_emoji = "🔥" if signal['confidence'] >= 85 else "⭐" if signal['confidence'] >= 75 else "💡"

            message += f"""**{i}. {signal['symbol']} {direction_emoji}**
{confidence_emoji} **Confidence**: {signal['confidence']:.1f}%
📈 **Direction**: {signal['direction']}
💰 **Entry**: ${signal['entry_price']:.4f}
🛑 **Stop Loss**: ${signal['stop_loss']:.4f}
🎯 **TP1**: ${signal['take_profit_1']:.4f}
🎯 **TP2**: ${signal['take_profit_2']:.4f}
📊 **R/R**: {signal['risk_reward_ratio']:.1f}:1
🔄 **Trend**: {signal['trend'].title()}
⚡ **Structure**: {signal['market_structure'].replace('_', ' ').title()}

"""

        message += f"""⚠️ **TRADING DISCLAIMER:**
• Signals berbasis Supply & Demand analysis
• Gunakan proper risk management
• Position sizing sesuai risk level
• DYOR sebelum trading

🎯 **Auto Signals hanya untuk Admin & Lifetime users**
📡 **Next scan in {self.scan_interval/60:.0f} minutes**"""

        return message

# Initialize function for the auto signals system
def initialize_auto_signals(bot_instance):
    """Initialize the auto signals system"""
    try:
        auto_signals = SnDAutoSignals(bot_instance)
        print("✅ Enhanced SnD Auto Signals system initialized")
        return auto_signals
    except Exception as e:
        print(f"❌ Failed to initialize auto signals: {e}")
        return None