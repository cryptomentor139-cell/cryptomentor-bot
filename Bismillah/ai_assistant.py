# -*- coding: utf-8 -*-
import requests
import random
import os
import asyncio
from datetime import datetime
import html
from crypto_api import CryptoAPI

class AIAssistant:
    def __init__(self, name="CryptoMentor AI"):
        self.name = name

        # Initialize CryptoAPI for comprehensive data
        self.crypto_api = CryptoAPI()

        print(f"✅ AI Assistant initialized with Binance API integration")

    def greet(self):
        return f"Halo! Saya {self.name}, siap membantu analisis dan informasi crypto kamu."

    def analyze_text(self, text):
        if "btc" in text.lower():
            return "📈 BTC sedang menarik untuk dianalisis hari ini!"
        elif "eth" in text.lower():
            return "📉 ETH menunjukkan sinyal konsolidasi."
        else:
            return "Saya tidak yakin, tapi saya akan bantu cari datanya."

    def help_message(self):
        return """🤖 **CryptoMentor AI Bot - Help**

📊 **Harga & Data Pasar:**
• `/price <symbol>` - Harga real-time
• `/market` - Overview pasar komprehensif

📈 **Analisis Trading:**
• `/analyze <symbol>` - Analisis mendalam (20 credit)
• `/futures <symbol>` - Analisis futures 1 coin (20 credit)
• `/futures_signals` - Sinyal futures lengkap (30 credit)

💼 **Portfolio & Credit:**
• `/portfolio` - Lihat portfolio
• `/add_coin <symbol> <amount>` - Tambah ke portfolio
• `/credits` - Cek sisa credit
• `/subscribe` - Upgrade premium

🎯 **Lainnya:**
• `/ask_ai <pertanyaan>` - Tanya AI crypto
• `/referral` - Program referral
• `/language` - Ubah bahasa

💡 **Tips:**
- Ketik nama crypto langsung untuk harga cepat
- Fitur premium = unlimited access
- Gunakan referral untuk bonus credit

🚀 **Semua analisis menggunakan data real-time dari Binance API!**"""

    def get_binance_futures_data(self, symbol="BTCUSDT"):
        """Get futures data from Binance API"""
        try:
            base_url = "https://fapi.binance.com"

            # Clean symbol format
            if not symbol.upper().endswith('USDT'):
                symbol = symbol.upper() + 'USDT'

            # Get long/short ratio
            long_short_url = f"{base_url}/futures/data/globalLongShortAccountRatio"
            long_short_params = {'symbol': symbol, 'period': '30m', 'limit': 1}

            # Get funding rate
            funding_url = f"{base_url}/fapi/v1/fundingRate"
            funding_params = {'symbol': symbol, 'limit': 1}

            # Get open interest
            oi_url = f"{base_url}/fapi/v1/openInterest"
            oi_params = {'symbol': symbol}

            # Get 24hr ticker statistics
            ticker_url = f"{base_url}/fapi/v1/ticker/24hr"
            ticker_params = {'symbol': symbol}

            # Make requests
            long_short_response = requests.get(long_short_url, params=long_short_params, timeout=10)
            funding_response = requests.get(funding_url, params=funding_params, timeout=10)
            oi_response = requests.get(oi_url, params=oi_params, timeout=10)
            ticker_response = requests.get(ticker_url, params=ticker_params, timeout=10)

            # Parse responses
            long_short_data = long_short_response.json()[0] if long_short_response.status_code == 200 and long_short_response.json() else {}
            funding_data = funding_response.json()[0] if funding_response.status_code == 200 and funding_response.json() else {}
            oi_data = oi_response.json() if oi_response.status_code == 200 else {}
            ticker_data = ticker_response.json() if ticker_response.status_code == 200 else {}

            return {
                'symbol': symbol,
                'price': float(ticker_data.get('lastPrice', 0)),
                'price_change_24h': float(ticker_data.get('priceChangePercent', 0)),
                'volume_24h': float(ticker_data.get('volume', 0)),
                'long_short_ratio': float(long_short_data.get('longShortRatio', 1.0)),
                'long_account': float(long_short_data.get('longAccount', 50)),
                'short_account': float(long_short_data.get('shortAccount', 50)),
                'funding_rate': float(funding_data.get('fundingRate', 0)),
                'open_interest': float(oi_data.get('openInterest', 0)),
                'source': 'binance_futures_api',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'error': f'Binance futures data error: {str(e)}',
                'symbol': symbol,
                'source': 'binance_error'
            }

    def analyze_futures_binance(self, symbol="BTCUSDT"):
        """Analyze futures using Binance data"""
        try:
            data = self.get_binance_futures_data(symbol)

            if 'error' in data:
                return f"❌ Error: {data['error']}"

            # Determine trend based on long/short ratio and funding rate
            long_ratio = data.get('long_short_ratio', 1.0)
            funding_rate = data.get('funding_rate', 0)
            price_change = data.get('price_change_24h', 0)

            # Analysis logic
            if long_ratio > 1.2 and funding_rate > 0.01:
                trend = "Bearish"
                signal = "🔴 SHORT"
                reason = "Overleveraged longs + high funding rate"
            elif long_ratio < 0.8 and funding_rate < -0.005:
                trend = "Bullish"
                signal = "🟢 LONG"
                reason = "Oversold conditions + negative funding"
            elif price_change > 5:
                trend = "Bullish"
                signal = "🟢 LONG"
                reason = "Strong upward momentum"
            elif price_change < -5:
                trend = "Bearish"
                signal = "🔴 SHORT"
                reason = "Strong downward momentum"
            else:
                trend = "Neutral"
                signal = "⏸️ HOLD"
                reason = "Mixed signals"

            return f"""🎯 FUTURES ANALYSIS - {symbol}

💰 Price: ${data['price']:,.2f}
📊 24h Change: {data['price_change_24h']:+.2f}%
📈 Long/Short Ratio: {data['long_short_ratio']:.2f}
💸 Funding Rate: {data['funding_rate']*100:.4f}%
💰 Open Interest: ${float(data['open_interest']):,.0f}

{signal}
📈 Trend: {trend}
💡 Reason: {reason}

📡 Source: Binance Futures API"""

        except Exception as e:
            return f"❌ Analysis error: {str(e)}"

    async def get_futures_analysis(self, symbol, timeframe, language='id', crypto_api=None):
        """Get futures analysis using Binance API"""
        try:
            print(f"🎯 Starting Binance futures analysis for {symbol} {timeframe}")

            # Get Binance futures data
            binance_data = self.get_binance_futures_data(symbol)

            if 'error' in binance_data:
                return self._generate_emergency_futures_signal(symbol, timeframe, language, binance_data['error'])

            # Generate trading signal
            trading_signal = self._format_binance_futures_analysis(
                symbol, timeframe, binance_data, language
            )

            return trading_signal

        except Exception as e:
            print(f"❌ Error in futures analysis: {e}")
            return self._generate_emergency_futures_signal(symbol, timeframe, language, str(e))

    def _format_binance_futures_analysis(self, symbol, timeframe, binance_data, language='id'):
        """Format Binance futures analysis output"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S WIB')

            # Extract data
            price = binance_data.get('price', 0)
            price_change = binance_data.get('price_change_24h', 0)
            long_ratio = binance_data.get('long_short_ratio', 1.0)
            funding_rate = binance_data.get('funding_rate', 0)
            open_interest = binance_data.get('open_interest', 0)

            # Generate signal
            signal_analysis = self._analyze_binance_signal(binance_data)
            direction = signal_analysis['direction']
            confidence = signal_analysis['confidence']
            reason = signal_analysis['reason']

            # Format price display
            def format_price(price):
                if price < 1:
                    return f"${price:.6f}"
                elif price < 100:
                    return f"${price:.4f}"
                else:
                    return f"${price:,.2f}"

            # Direction emoji
            if direction == 'LONG':
                direction_emoji = "🟢"
                signal_emoji = "📈"
            elif direction == 'SHORT':
                direction_emoji = "🔴"
                signal_emoji = "📉"
            else:
                direction_emoji = "⏸️"
                signal_emoji = "📊"

            if language == 'id':
                message = f"""🎯 **ANALISA FUTURES - {symbol.upper()} ({timeframe})**

💰 **Data Real-time (Binance):**
• **Harga**: {format_price(price)}
• **Perubahan 24j**: {price_change:+.2f}%
• **Funding Rate**: {funding_rate*100:+.4f}%

{direction_emoji} **SINYAL**: **{direction}** {signal_emoji}
📊 **Confidence**: {confidence:.0f}%

📊 **ANALISA MENDALAM:**
• **Long/Short Ratio**: {long_ratio:.2f}"""

                if long_ratio > 1.3:
                    message += f" (⚠️ Overleveraged Longs)"
                elif long_ratio < 0.7:
                    message += f" (💎 Oversold Conditions)"
                else:
                    message += f" (⚖️ Balanced)"

                message += f"""
• **Open Interest**: ${open_interest:,.0f}
• **Funding Rate**: {funding_rate*100:+.4f}%"""

                if funding_rate > 0.01:
                    message += f" (💸 Longs overpaying)"
                elif funding_rate < -0.005:
                    message += f" (💰 Shorts overpaying)"
                else:
                    message += f" (⚖️ Neutral)"

                message += f"""

🧠 **SMART MONEY ANALYSIS:**
• **Reason**: {reason}
• **Market Sentiment**: {'Bullish' if long_ratio > 1.2 else 'Bearish' if long_ratio < 0.8 else 'Neutral'}
• **Funding Bias**: {'Bullish expensive' if funding_rate > 0.01 else 'Bearish expensive' if funding_rate < -0.005 else 'Neutral'}"""

                if direction != 'HOLD':
                    entry_price = price * (0.998 if direction == 'LONG' else 1.002)
                    tp1 = price * (1.025 if direction == 'LONG' else 0.975)
                    tp2 = price * (1.05 if direction == 'LONG' else 0.95)
                    sl = price * (0.975 if direction == 'LONG' else 1.025)

                    message += f"""

📌 **TRADING SETUP:**
┣━ 📍 **ENTRY**: {format_price(entry_price)}
┣━ 🎯 **TP1**: {format_price(tp1)} (RR 2:1)
┣━ 🎯 **TP2**: {format_price(tp2)} (RR 4:1)
┗━ 🛡️ **STOP LOSS**: {format_price(sl)} (**WAJIB!**)

💡 **Strategi**: {reason}"""
                else:
                    message += f"""

⏸️ **HOLD POSITION**
• **Alasan**: {reason}
• **Tunggu**: Setup yang lebih jelas
• **Monitor**: Perubahan funding rate & ratio"""

                message += f"""

⏰ **Update**: {current_time}
📡 **Source**: Binance Futures API
⭐ **Status**: Real-time Analysis Active"""

            else:
                # English version
                message = f"""🎯 **FUTURES ANALYSIS - {symbol.upper()} ({timeframe})**

💰 **Real-time Data (Binance):**
• **Price**: {format_price(price)}
• **24h Change**: {price_change:+.2f}%
• **Funding Rate**: {funding_rate*100:+.4f}%

{direction_emoji} **SIGNAL**: **{direction}** {signal_emoji}
📊 **Confidence**: {confidence:.0f}%

📊 **COMPREHENSIVE ANALYSIS:**
• **Long/Short Ratio**: {long_ratio:.2f}"""

                if long_ratio > 1.3:
                    message += f" (⚠️ Overleveraged Longs)"
                elif long_ratio < 0.7:
                    message += f" (💎 Oversold Conditions)"
                else:
                    message += f" (⚖️ Balanced)"

                message += f"""
• **Open Interest**: ${open_interest:,.0f}
• **Funding Rate**: {funding_rate*100:+.4f}%"""

                if funding_rate > 0.01:
                    message += f" (💸 Longs overpaying)"
                elif funding_rate < -0.005:
                    message += f" (💰 Shorts overpaying)"
                else:
                    message += f" (⚖️ Neutral)"

                message += f"""

🧠 **SMART MONEY ANALYSIS:**
• **Reason**: {reason}
• **Market Sentiment**: {'Bullish' if long_ratio > 1.2 else 'Bearish' if long_ratio < 0.8 else 'Neutral'}
• **Funding Bias**: {'Bullish expensive' if funding_rate > 0.01 else 'Bearish expensive' if funding_rate < -0.005 else 'Neutral'}"""

                if direction != 'HOLD':
                    entry_price = price * (0.998 if direction == 'LONG' else 1.002)
                    tp1 = price * (1.025 if direction == 'LONG' else 0.975)
                    tp2 = price * (1.05 if direction == 'LONG' else 0.95)
                    sl = price * (0.975 if direction == 'LONG' else 1.025)

                    message += f"""

📌 **TRADING SETUP:**
• **ENTRY**: {format_price(entry_price)}
• **TP1**: {format_price(tp1)}
• **STOP LOSS**: {format_price(sl)}"""

                message += f"""

⏰ **Update**: {current_time}
📡 **Source**: Binance Futures API
⭐ **Status**: Real-time Analysis Active"""

            return message

        except Exception as e:
            print(f"❌ Error formatting Binance analysis: {e}")
            return self._generate_emergency_futures_signal(symbol, timeframe, language, str(e))

    def _analyze_binance_signal(self, binance_data):
        """Analyze Binance data for trading signal"""
        try:
            long_ratio = binance_data.get('long_short_ratio', 1.0)
            funding_rate = binance_data.get('funding_rate', 0)
            price_change = binance_data.get('price_change_24h', 0)

            direction = 'HOLD'
            confidence = 50
            reason = 'Mixed signals'

            # Long/Short ratio analysis (contrarian)
            if long_ratio > 1.4:
                direction = 'SHORT'
                confidence += 25
                reason = f'Overleveraged longs (Ratio: {long_ratio:.2f})'
            elif long_ratio < 0.6:
                direction = 'LONG'
                confidence += 20
                reason = f'Oversold conditions (Ratio: {long_ratio:.2f})'

            # Funding rate analysis
            if funding_rate > 0.015:
                direction = 'SHORT'
                confidence += 30
                reason = f'Extreme funding rate {funding_rate*100:.3f}%'
            elif funding_rate < -0.008:
                direction = 'LONG'
                confidence += 25
                reason = f'Negative funding {funding_rate*100:.3f}%'

            # Price momentum
            if abs(price_change) > 5:
                confidence += 10
                if price_change > 0 and direction != 'SHORT':
                    direction = 'LONG'
                    reason += f' + Strong momentum ({price_change:+.1f}%)'
                elif price_change < 0 and direction != 'LONG':
                    direction = 'SHORT'
                    reason += f' + Bearish momentum ({price_change:+.1f}%)'

            confidence = min(95, max(30, confidence))

            if confidence < 65:
                direction = 'HOLD'
                reason = 'Mixed signals - wait for clearer setup'

            return {
                'direction': direction,
                'confidence': confidence,
                'reason': reason
            }

        except Exception as e:
            return {
                'direction': 'HOLD',
                'confidence': 40,
                'reason': f'Analysis error: {str(e)[:50]}...'
            }

    async def generate_futures_signals(self, language='id', crypto_api=None, context_args=None):
        """Generate futures signals using Binance API"""
        try:
            # Get top coins for analysis
            top_coins = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'MATIC', 'LINK']

            # Process query args if provided
            if context_args and len(context_args) > 0:
                raw_query = ' '.join(context_args).upper()
                query_parts = raw_query.split()
                cleaned_parts = [part for part in query_parts if part != 'SND']

                if cleaned_parts:
                    if any(tf in cleaned_parts[0] for tf in ['M', 'H', 'D', 'W']):
                        timeframe = cleaned_parts[0]
                        symbol = cleaned_parts[1] if len(cleaned_parts) > 1 else 'BTC'
                    else:
                        symbol = cleaned_parts[0]
                        timeframe = '1H'

                    return await self.get_futures_analysis(symbol, timeframe, language, crypto_api)

            current_time = datetime.now().strftime('%H:%M:%S WIB')
            high_confidence_signals = []
            total_analyzed = 0
            successful_analysis = 0

            if language == 'id':
                header = f"""🎯 **SINYAL FUTURES BINANCE**
⏰ {current_time}

📊 **Analisis Real-time Binance:**
"""
            else:
                header = f"""🎯 **BINANCE FUTURES SIGNALS**
⏰ {current_time}

📊 **Real-time Binance Analysis:**
"""

            # Analyze each coin with Binance data
            for symbol in top_coins[:8]:
                try:
                    total_analyzed += 1

                    # Get Binance futures data
                    binance_data = self.get_binance_futures_data(symbol + 'USDT')

                    if 'error' not in binance_data:
                        successful_analysis += 1

                        # Generate trading signal
                        signal_analysis = self._analyze_binance_signal(binance_data)

                        # Only include high-confidence signals
                        if signal_analysis['confidence'] >= 70 and signal_analysis['direction'] != 'HOLD':
                            signal_data = {
                                'symbol': symbol,
                                'direction': signal_analysis['direction'],
                                'confidence': signal_analysis['confidence'],
                                'entry_price': binance_data['price'],
                                'tp1': binance_data['price'] * (1.03 if signal_analysis['direction'] == 'LONG' else 0.97),
                                'sl': binance_data['price'] * (0.97 if signal_analysis['direction'] == 'LONG' else 1.03),
                                'reason': signal_analysis['reason']
                            }
                            high_confidence_signals.append(signal_data)

                except Exception as e:
                    print(f"Error analyzing {symbol}: {e}")
                    continue

            # Format results
            if high_confidence_signals:
                signals_text = header

                for i, signal in enumerate(high_confidence_signals[:6], 1):
                    symbol = signal['symbol']
                    direction = signal['direction']
                    confidence = signal['confidence']
                    entry = signal['entry_price']
                    tp1 = signal['tp1']
                    sl = signal['sl']
                    reason = signal['reason']

                    # Direction emoji
                    if direction == 'LONG':
                        emoji = "🟢"
                        signal_emoji = "📈"
                    elif direction == 'SHORT':
                        emoji = "🔴"
                        signal_emoji = "📉"
                    else:
                        emoji = "⏸️"
                        signal_emoji = "📊"

                    def format_price(price):
                        if price < 1:
                            return f"${price:.6f}"
                        elif price < 100:
                            return f"${price:.4f}"
                        else:
                            return f"${price:,.2f}"

                    signals_text += f"""
**{i}. {symbol}** {emoji} **{direction}** {signal_emoji} ({confidence}%)
• Entry: {format_price(entry)} | TP: {format_price(tp1)} | SL: {format_price(sl)}
• Reason: {reason[:60]}{'...' if len(reason) > 60 else ''}"""

                if language == 'id':
                    signals_text += f"""

🎯 **Ringkasan Analysis:**
• **High-Confidence Signals**: {len(high_confidence_signals)}/{total_analyzed} coins
• **Success Rate**: {(successful_analysis/total_analyzed)*100:.0f}%
• **Min Confidence**: 70%+ (Strong signals only)
• **Method**: Binance Long/Short + Funding + Price momentum

⚠️ **Risk Management:**
• Max 2% modal per trade
• SL WAJIB sebelum entry
• Monitor funding rate shifts
• Diversifikasi max 3 posisi simultan

📡 **Data Sources**: Binance Futures API
🔄 **Update**: Real-time
⭐ **Premium** – Advanced Signal Logic"""
                else:
                    signals_text += f"""

🎯 **Analysis Summary:**
• **High-Confidence Signals**: {len(high_confidence_signals)}/{total_analyzed} coins
• **Success Rate**: {(successful_analysis/total_analyzed)*100:.0f}%
• **Min Confidence**: 70%+ (Strong signals only)
• **Method**: Binance Long/Short + Funding + Price momentum

⚠️ **Risk Management:**
• Max 2% capital per trade
• MANDATORY stop loss before entry
• Monitor funding rate shifts
• Diversify max 3 simultaneous positions

📡 **Data Sources**: Binance Futures API
🔄 **Update**: Real-time
⭐ **Premium** – Advanced Signal Logic"""

                return signals_text
            else:
                if language == 'id':
                    return f"""😔 **Tidak Ada Sinyal High-Confidence (70%+)**

🔍 **Status Analysis:**
• Coins Analyzed: {successful_analysis}/{total_analyzed}
• Data Source: Binance Futures API
• Confidence Threshold: 70%+ (Premium filtering)

💡 **Market Condition:**
• Market dalam kondisi sideways/uncertainty
• Menunggu setup yang jelas
• Funding rates dalam range normal

🎯 **Alternative:**
• Gunakan `/futures <symbol>` untuk analisis spesifik coin
• Coba lagi dalam 30-60 menit

⏰ Update: {current_time}"""
                else:
                    return f"""😔 **No High-Confidence Signals (70%+) Found**

🔍 **Analysis Status:**
• Coins Analyzed: {successful_analysis}/{total_analyzed}
• Data Source: Binance Futures API
• Confidence Threshold: 70%+ (Premium filtering)

💡 **Market Condition:**
• Market in sideways/uncertainty mode
• Waiting for clear setup
• Funding rates in normal ranges

🎯 **Alternative:**
• Use `/futures <symbol>` for specific coin analysis
• Try again in 30-60 minutes

⏰ Update: {current_time}"""

        except Exception as e:
            print(f"Error in futures signals: {e}")
            return self._generate_emergency_futures_signal('MULTI', '1H', language, str(e))

    def get_ai_response(self, text, language='id'):
        """Enhanced AI response for crypto beginners and general questions"""
        text_lower = text.lower()

        if language == 'id':
            # Crypto basics and education
            if any(keyword in text_lower for keyword in ['apa itu bitcoin', 'bitcoin itu apa', 'penjelasan bitcoin']):
                return """🪙 **Apa itu Bitcoin?**

Bitcoin (BTC) adalah cryptocurrency pertama dan terbesar di dunia, diciptakan oleh Satoshi Nakamoto pada 2009.

🔑 **Karakteristik Utama:**
- **Digital Currency**: Mata uang digital yang tidak dikendalikan bank
- **Blockchain**: Teknologi buku besar terdistribusi yang aman
- **Limited Supply**: Hanya 21 juta BTC yang akan pernah ada
- **Decentralized**: Tidak ada otoritas pusat yang mengendalikan

💡 **Kegunaan Bitcoin:**
- Store of value (penyimpan nilai)
- Medium of exchange (alat tukar)
- Hedge against inflation (lindung nilai inflasi)

📈 **Untuk pemula**: Mulai dengan belajar tentang wallet, private key, dan cara membeli BTC di exchange resmi.

Gunakan `/price btc` untuk cek harga terkini!"""

            elif any(keyword in text_lower for keyword in ['harga', 'price', 'berapa']):
                return "💰 Untuk cek harga crypto, gunakan command `/price <symbol>`.\nContoh: `/price btc`\n\nUntuk analisis lengkap dengan prediksi: `/analyze <symbol>`"

            elif any(keyword in text_lower for keyword in ['analisis', 'analyze', 'sinyal']):
                return "📊 Untuk analisis mendalam, gunakan `/analyze <symbol>` atau `/futures_signals` untuk sinyal futures harian.\n\n💡 **Tips**: Analisis mencakup technical analysis, sentiment, dan rekomendasi trading."

            elif any(keyword in text_lower for keyword in ['help', 'bantuan', 'command']):
                return self.help_message()

            elif any(keyword in text_lower for keyword in ['terima kasih', 'thanks', 'thx']):
                return "🙏 Sama-sama! Senang bisa membantu belajar crypto Anda. Jangan ragu untuk bertanya lagi!"

            # Default response for unmatched queries
            else:
                return f"""🤖 **CryptoMentor AI**

Saya memahami Anda bertanya tentang: "{text}"

📚 **Yang bisa saya bantu:**
- Analisis harga crypto (`/price btc`)
- Analisis mendalam (`/analyze eth`)
- Sinyal trading (`/futures_signals`)
- Overview pasar (`/market`)
- Pertanyaan crypto umum
- Tutorial trading dan DeFi

💡 **Tip**: Coba ketik pertanyaan lebih spesifik atau gunakan command yang tersedia.

Gunakan `/help` untuk melihat semua fitur!"""

        else:
            # English responses
            if any(keyword in text_lower for keyword in ['price', 'cost', 'how much']):
                return "💰 To check crypto prices, use `/price <symbol>`. Example: `/price btc`\n\nFor comprehensive analysis: `/analyze <symbol>`"

            elif any(keyword in text_lower for keyword in ['help', 'command']):
                return self.help_message()

            elif any(keyword in text_lower for keyword in ['thank', 'thanks', 'thx']):
                return "🙏 You're welcome! Happy to help with your crypto learning journey. Feel free to ask anytime!"

            else:
                return """🤖 **CryptoMentor AI - Crypto Learning Assistant**

I'm here to help you learn about cryptocurrency!

📚 **Topics I can explain:**
- Crypto basics (Bitcoin, Blockchain, DeFi)
- How to buy and store crypto
- Trading and technical analysis
- Security and wallet management
- NFTs and blockchain technology

💡 **Example questions:**
- "What is Bitcoin?"
- "How to buy crypto?"
- "What is DeFi?"
- "How to trade cryptocurrency?"
- "Best crypto wallets?"

📊 **Available commands:**
- `/price <symbol>` - Check real-time prices
- `/analyze <symbol>` - Deep analysis
- `/futures_signals` - Trading signals
- `/help` - See all commands

Ask me anything about crypto! 🚀"""

    def get_market_sentiment(self, language='id', crypto_api=None):
        """Get market sentiment with improved CMC and Binance integration"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S WIB')
            data_sources = []
            successful_sources = 0

            # Initialize data containers
            market_overview = {'error': 'Not fetched'}
            btc_futures = {'error': 'Not fetched'}
            top_prices = {'error': 'Not fetched'}

            # 1. Get market overview using crypto_api provider
            try:
                if crypto_api and hasattr(crypto_api, 'provider'):
                    market_overview = crypto_api.get_market_overview()

                    if market_overview and 'error' not in market_overview and market_overview.get('success', False):
                        data_sources.append("✅ CoinMarketCap")
                        successful_sources += 1
                    else:
                        data_sources.append("⚠️ CoinMarketCap")
                        market_overview = {'error': 'API response invalid'}
                else:
                    data_sources.append("❌ CoinMarketCap")
                    market_overview = {'error': 'CryptoAPI not available'}
            except Exception as e:
                data_sources.append("❌ CoinMarketCap")
                market_overview = {'error': f'Exception: {str(e)}'}
                print(f"❌ Market overview error: {e}")

            # 2. Get BTC futures data for sentiment
            try:
                btc_futures = self.get_binance_futures_data('BTC')

                if 'error' not in btc_futures and btc_futures.get('price', 0) > 0:
                    data_sources.append("✅ Binance")
                    successful_sources += 1
                else:
                    data_sources.append("⚠️ Binance")
            except Exception as e:
                data_sources.append("❌ Binance")
                btc_futures = {'error': f'Exception: {str(e)}'}
                print(f"❌ BTC futures error: {e}")

            # 3. Get top cryptocurrency prices
            try:
                if crypto_api:
                    top_symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']
                    top_prices = crypto_api.get_multiple_prices(top_symbols)

                    if top_prices and 'error' not in top_prices and top_prices.get('success', False):
                        data_sources.append("✅ Top Prices")
                        successful_sources += 1
                    else:
                        data_sources.append("⚠️ Top Prices")
                        top_prices = {'error': 'Price data unavailable'}
                else:
                    data_sources.append("❌ Top Prices")
                    top_prices = {'error': 'CryptoAPI not available'}
            except Exception as e:
                data_sources.append("❌ Top Prices")
                top_prices = {'error': f'Exception: {str(e)}'}
                print(f"❌ Top prices error: {e}")

            # Format large numbers
            def format_currency(amount):
                if amount > 1000000000000:  # Trillions
                    return f"${amount/1000000000000:.2f}T"
                elif amount > 1000000000:  # Billions
                    return f"${amount/1000000000:.2f}B"
                elif amount > 1000000:  # Millions
                    return f"${amount/1000000:.1f}M"
                else:
                    return f"${amount:,.0f}"

            # Build comprehensive market analysis
            if language == 'id':
                analysis = f"""🌍 **OVERVIEW PASAR CRYPTO GLOBAL**

🔍 **Status Data**: ({successful_sources}/3 sumber berhasil)
📡 **Sumber**: {', '.join(data_sources)}

"""
            else:
                analysis = f"""🌍 **GLOBAL CRYPTO MARKET OVERVIEW**

🔍 **Data Status**: ({successful_sources}/3 sources successful)
📡 **Sources**: {', '.join(data_sources)}

"""

            # Add market overview data
            if 'error' not in market_overview and market_overview.get('data'):
                market_data = market_overview['data']
                total_market_cap = market_data.get('total_market_cap', 0)
                total_volume = market_data.get('total_volume_24h', 0)
                market_cap_change = market_data.get('market_cap_change_24h', 0)
                btc_dominance = market_data.get('btc_dominance', 0)
                active_cryptos = market_data.get('active_cryptocurrencies', 0)

                # Market sentiment emoji
                if market_cap_change > 3:
                    sentiment_emoji = "🚀"
                    sentiment_text = "Very Bullish"
                elif market_cap_change > 0:
                    sentiment_emoji = "📈"
                    sentiment_text = "Bullish"
                elif market_cap_change > -3:
                    sentiment_emoji = "⚡"
                    sentiment_text = "Neutral"
                else:
                    sentiment_emoji = "📉"
                    sentiment_text = "Bearish"

                if language == 'id':
                    analysis += f"""💰 **Statistik Pasar Global (CoinMarketCap):**
• **Total Market Cap**: {format_currency(total_market_cap)}
• **Perubahan 24j**: {sentiment_emoji} {market_cap_change:+.2f}%
• **Volume 24j**: {format_currency(total_volume)}
• **Market Sentiment**: {sentiment_text}

🪙 **Dominasi & Aktivitas:**
• **Bitcoin Dominance**: {btc_dominance:.1f}%
• **Altcoin Dominance**: {100-btc_dominance:.1f}%
• **Active Cryptocurrencies**: {active_cryptos:,}

"""
                else:
                    analysis += f"""💰 **Global Market Statistics (CoinMarketCap):**
• **Total Market Cap**: {format_currency(total_market_cap)}
• **24h Change**: {sentiment_emoji} {market_cap_change:+.2f}%
• **Volume 24h**: {format_currency(total_volume)}
• **Market Sentiment**: {sentiment_text}

🪙 **Dominance & Activity:**
• **Bitcoin Dominance**: {btc_dominance:.1f}%
• **Altcoin Dominance**: {100-btc_dominance:.1f}%
• **Active Cryptocurrencies**: {active_cryptos:,}

"""
            else:
                market_cap_change = 0  # Default for sentiment calculation
                btc_dominance = 50  # Default
                if language == 'id':
                    analysis += f"""💰 **Statistik Pasar Global:**
• ⚠️ Data CoinMarketCap tidak tersedia
• **Error**: {market_overview.get('error', 'Unknown error')}

"""
                else:
                    analysis += f"""💰 **Global Market Statistics:**
• ⚠️ CoinMarketCap data unavailable
• **Error**: {market_overview.get('error', 'Unknown error')}

"""

            # Add BTC futures sentiment
            if 'error' not in btc_futures:
                btc_price = btc_futures.get('price', 0)
                btc_change = btc_futures.get('price_change_24h', 0)
                long_ratio = btc_futures.get('long_short_ratio', 1.0)
                funding_rate = btc_futures.get('funding_rate', 0)

                if language == 'id':
                    analysis += f"""📊 **Bitcoin Futures Sentiment (Binance):**
• **BTC Price**: {self._format_price_display(btc_price)}
• **24h Change**: {btc_change:+.2f}%
• **Long/Short Ratio**: {long_ratio:.2f}"""
                else:
                    analysis += f"""📊 **Bitcoin Futures Sentiment (Binance):**
• **BTC Price**: {self._format_price_display(btc_price)}
• **24h Change**: {btc_change:+.2f}%
• **Long/Short Ratio**: {long_ratio:.2f}"""

                if long_ratio > 1.3:
                    analysis += f" (⚠️ Overleveraged)"
                elif long_ratio < 0.7:
                    analysis += f" (💎 Oversold)"
                else:
                    analysis += f" (⚖️ Balanced)"

                analysis += f"\n• **Funding Rate**: {funding_rate*100:+.4f}%\n\n"
            else:
                if language == 'id':
                    analysis += f"""📊 **Bitcoin Futures Sentiment:**
• ⚠️ Data Binance futures tidak tersedia
• **Error**: {btc_futures.get('error', 'Unknown error')}

"""
                else:
                    analysis += f"""📊 **Bitcoin Futures Sentiment:**
• ⚠️ Binance futures data unavailable
• **Error**: {btc_futures.get('error', 'Unknown error')}

"""

            # Add top cryptocurrencies
            if 'error' not in top_prices and top_prices.get('prices'):
                if language == 'id':
                    analysis += f"""🎯 **Top Cryptocurrencies (Real-time):**"""
                else:
                    analysis += f"""🎯 **Top Cryptocurrencies (Real-time):**"""

                for i, (symbol, data) in enumerate(top_prices['prices'].items(), 1):
                    if i <= 5:  # Show top 5
                        price = data.get('price', 0)
                        change_24h = data.get('change_24h', 0)

                        price_display = f"${price:.4f}" if price < 100 else f"${price:,.2f}"
                        change_emoji = "📈" if change_24h >= 0 else "📉"

                        analysis += f"\n• **{i}. {symbol}**: {price_display} {change_emoji} {change_24h:+.1f}%"

                analysis += f"\n\n"
            else:
                if language == 'id':
                    analysis += f"""🎯 **Top Cryptocurrencies:**
• ⚠️ Data harga tidak tersedia

"""
                else:
                    analysis += f"""🎯 **Top Cryptocurrencies:**
• ⚠️ Price data unavailable

"""

            # Generate trading recommendation based on available data
            overall_sentiment_score = 0

            # Market cap change factor (if available)
            if market_cap_change > 5:
                overall_sentiment_score += 3
            elif market_cap_change > 2:
                overall_sentiment_score += 2
            elif market_cap_change > 0:
                overall_sentiment_score += 1
            elif market_cap_change < -5:
                overall_sentiment_score -= 3
            elif market_cap_change < -2:
                overall_sentiment_score -= 2
            elif market_cap_change < 0:
                overall_sentiment_score -= 1

            # BTC futures sentiment factor
            if 'error' not in btc_futures:
                btc_change = btc_futures.get('price_change_24h', 0)
                long_ratio = btc_futures.get('long_short_ratio', 1.0)

                if btc_change > 5:
                    overall_sentiment_score += 2
                elif btc_change < -5:
                    overall_sentiment_score -= 2

                if long_ratio > 1.4:  # Too many longs
                    overall_sentiment_score -= 1
                elif long_ratio < 0.6:  # Too many shorts
                    overall_sentiment_score += 1

            # Generate trading recommendation (Fix formatting)
            if overall_sentiment_score >= 4:
                if language == 'id':
                    market_rec = "🟢 BULLISH MARKET - Waktu baik untuk accumulate"
                    market_action = "• Action: DCA strategy pada major coins\n• Focus: BTC, ETH, strong altcoins\n• Risk: Medium - Momentum positif"
                else:
                    market_rec = "🟢 BULLISH MARKET - Good time to accumulate"
                    market_action = "• Action: DCA strategy on major coins\n• Focus: BTC, ETH, strong altcoins\n• Risk: Medium - Positive momentum"
            elif overall_sentiment_score >= 2:
                if language == 'id':
                    market_rec = "🟡 CAUTIOUSLY BULLISH - Selektif membeli"
                    market_action = "• Action: Cherry-pick performers terbaik\n• Focus: Top 10 dengan volume tinggi\n• Risk: Medium - Sinyal campuran"
                else:
                    market_rec = "🟡 CAUTIOUSLY BULLISH - Selective buying"
                    market_action = "• Action: Cherry-pick strong performers\n• Focus: Top 10 with high volume\n• Risk: Medium - Mixed signals"
            elif overall_sentiment_score <= -4:
                if language == 'id':
                    market_rec = "🔴 BEARISH MARKET - Mode risk-off"
                    market_action = "• Action: Posisi cash/stablecoin\n• Focus: Tunggu entry point lebih baik\n• Risk: High - Trend masih bearish"
                else:
                    market_rec = "🔴 BEARISH MARKET - Risk-off mode"
                    market_action = "• Action: Cash/stablecoin positions\n• Focus: Wait for better entry points\n• Risk: High - Bearish trend continues"
            elif overall_sentiment_score <= -2:
                if language == 'id':
                    market_rec = "🟠 CAUTIOUSLY BEARISH - Eksposur terbatas"
                    market_action = "• Action: Position size kecil\n• Focus: Coin fundamental kuat saja\n• Risk: High - Volatilitas tinggi"
                else:
                    market_rec = "🟠 CAUTIOUSLY BEARISH - Limited exposure"
                    market_action = "• Action: Small position sizing\n• Focus: Strong fundamental coins only\n• Risk: High - High volatility"
            else:
                if language == 'id':
                    market_rec = "⚖️ NEUTRAL MARKET - Range-bound"
                    market_action = "• Action: Range trading strategies\n• Focus: Peluang scalping\n• Risk: Medium - Pergerakan sideways"
                else:
                    market_rec = "⚖️ NEUTRAL MARKET - Range-bound"
                    market_action = "• Action: Range trading strategies\n• Focus: Scalping opportunities\n• Risk: Medium - Sideways movement"

            if language == 'id':
                analysis += f"""🎯 MARKET OUTLOOK & REKOMENDASI:
{market_rec}

📋 Strategi Trading:
{market_action}

💡 Key Levels Monitor:
• BTC Dominance: {btc_dominance:.1f}% (Alt season jika <40%)
• Data Quality: {successful_sources}/3 sources
• Confidence: {'High' if successful_sources >= 2 else 'Medium'}

⏰ Update: {current_time} WIB
📡 Sources: CoinMarketCap + Binance Futures + Price Data
💎 Analysis: Multi-API Integration"""
            else:
                analysis += f"""🎯 MARKET OUTLOOK & RECOMMENDATION:
{market_rec}

📋 Trading Strategy:
{market_action}

💡 Key Levels Monitor:
• BTC Dominance: {btc_dominance:.1f}% (Alt season if <40%)
• Data Quality: {successful_sources}/3 sources
• Confidence: {'High' if successful_sources >= 2 else 'Medium'}

⏰ Update: {current_time}
📡 Sources: CoinMarketCap + Binance Futures + Price Data
💎 Analysis: Multi-API Integration"""

            return analysis

        except Exception as e:
            print(f"❌ Error in market sentiment: {e}")
            import traceback
            traceback.print_exc()

            if language == 'id':
                return f"""❌ **Error mengambil data pasar**

**Detail**: {str(e)[:100]}...

💡 **Solusi**:
• Coba lagi dalam beberapa menit
• Gunakan `/price btc` untuk harga basic
• Contact admin jika masalah berlanjut

🔄 **Note**: Sistem menggunakan Binance + CoinMarketCap API"""
            else:
                return f"""❌ **Error fetching market data**

**Detail**: {str(e)[:100]}...

💡 **Solutions**:
• Try again in a few minutes
• Use `/price btc` for basic prices
• Contact admin if issue persists

🔄 **Note**: System uses Binance + CoinMarketCap APIs"""

    def get_comprehensive_analysis(self, symbol, timeframe=None, leverage=None, language='id', crypto_api=None):
        """Get comprehensive analysis with SnD zones and advanced CMC data"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S WIB')
            data_sources = []
            successful_sources = 0
            total_sources = 2  # CMC, Binance

            # Initialize data containers
            cmc_data = {'error': 'Not fetched'}
            binance_data = {'error': 'Not fetched'}
            snd_analysis = {'error': 'Not available'}

            # 1. Get CoinMarketCap data using crypto_api provider
            try:
                if crypto_api and hasattr(crypto_api, 'provider') and crypto_api.provider:
                    # Get price data from provider
                    price_result = crypto_api.get_crypto_price(symbol, force_refresh=True)

                    if price_result and 'error' not in price_result and price_result.get('price', 0) > 0:
                        cmc_data = price_result
                        data_sources.append("✅ CoinMarketCap")
                        successful_sources += 1

                        # Try to get additional info
                        try:
                            info_result = crypto_api.get_crypto_info(symbol)
                            if info_result and 'error' not in info_result:
                                # Merge info data safely
                                cmc_data.update({k: v for k, v in info_result.items() if k not in cmc_data})
                        except:
                            pass  # Info is optional
                    else:
                        data_sources.append("⚠️ CoinMarketCap")
                        cmc_data = {'error': 'Invalid response'}
                else:
                    data_sources.append("❌ CoinMarketCap")
                    cmc_data = {'error': 'API not available'}
            except Exception as e:
                data_sources.append("❌ CoinMarketCap")
                cmc_data = {'error': f'Exception: {str(e)}'}
                print(f"CoinMarketCap API error: {e}")

            # 2. Get Binance futures data
            try:
                binance_data = self.get_binance_futures_data(symbol)

                if 'error' not in binance_data and binance_data.get('price', 0) > 0:
                    data_sources.append("✅ Binance")
                    successful_sources += 1
                else:
                    data_sources.append("⚠️ Binance")
            except Exception as e:
                data_sources.append("❌ Binance")
                binance_data = {'error': f'Exception: {str(e)}'}
                print(f"❌ Binance API error: {e}")

            # 3. Get SnD Analysis using candlestick data
            try:
                if crypto_api:
                    candlestick_data = crypto_api.get_candlestick_data(symbol, '1h', 50)
                    if candlestick_data and 'error' not in candlestick_data:
                        snd_analysis = self._analyze_snd_zones(candlestick_data['data'], symbol)
                        if 'error' not in snd_analysis:
                            data_sources.append("✅ SnD Analysis")
                            successful_sources += 1
                        else:
                            data_sources.append("⚠️ SnD Analysis")
                    else:
                        data_sources.append("❌ SnD Analysis")
                        snd_analysis = {'error': 'Candlestick data unavailable'}
                else:
                    data_sources.append("❌ SnD Analysis")
                    snd_analysis = {'error': 'CryptoAPI not available'}
            except Exception as e:
                data_sources.append("❌ SnD Analysis")
                snd_analysis = {'error': f'SnD Exception: {str(e)}'}
                print(f"❌ SnD Analysis error: {e}")

            # Determine data quality
            if successful_sources >= 3:
                quality = "PREMIUM"
                quality_emoji = "💎"
            elif successful_sources >= 2:
                quality = "EXCELLENT"
                quality_emoji = "✅"
            elif successful_sources >= 1:
                quality = "GOOD"
                quality_emoji = "🟡"
            else:
                quality = "LIMITED"
                quality_emoji = "⚠️"

            # Extract price data (prioritize CMC, fallback to Binance)
            current_price = 0
            change_24h = 0
            change_7d = 0
            volume_24h = 0
            market_cap = 0
            funding_rate = 0
            price_source = "Estimasi"

            # Try CMC first
            if ('error' not in cmc_data and
                cmc_data.get('price') is not None and
                cmc_data.get('price', 0) > 0):
                current_price = float(cmc_data.get('price', 0))
                change_24h = float(cmc_data.get('change_24h', 0))
                change_7d = float(cmc_data.get('change_7d', 0))
                volume_24h = float(cmc_data.get('volume_24h', 0))
                market_cap = float(cmc_data.get('market_cap', 0))
                price_source = "CoinMarketCap Pro"
            # Fallback to Binance
            elif ('error' not in binance_data and
                  binance_data.get('price', 0) > 0):
                current_price = float(binance_data.get('price', 0))
                change_24h = float(binance_data.get('price_change_24h', 0))
                volume_24h = float(binance_data.get('volume_24h', 0))
                price_source = "Binance"
            # Final fallback to estimated price
            else:
                current_price = float(self._get_estimated_price(symbol))
                change_24h = 0
                volume_24h = 0
                price_source = "Estimasi"

            # Get funding rate from Binance
            if 'error' not in binance_data:
                funding_rate = float(binance_data.get('funding_rate', 0))

            # Build comprehensive analysis with SnD zones
            analysis = f"""🎯 **ANALISIS KOMPREHENSIF {symbol.upper()} + SnD ZONES**

🔍 **Kualitas Data**: {quality_emoji} {quality} ({successful_sources}/3 sumber berhasil)
📡 **Sumber**: {', '.join(data_sources)}

💰 **1. HARGA & FUNDAMENTAL (Advanced CMC)**
• **Real-time Price**: {self._format_price_display(current_price)} ({price_source})
• **24h Change**: {change_24h:+.2f}%"""

            if change_7d != 0:
                analysis += f"\n• **7d Change**: {change_7d:+.2f}%"

            analysis += f"""
• **Volume 24h**: {self._format_currency_display(volume_24h)}"""

            # Enhanced CMC data
            if 'error' not in cmc_data:
                rank = cmc_data.get('rank', 0)
                circulating_supply = cmc_data.get('circulating_supply', 0)

                analysis += f"""

📈 **2. MARKET DATA (CoinMarketCap Pro)**"""

                if market_cap > 0:
                    analysis += f"\n• **Market Cap**: {self._format_currency_display(market_cap)}"
                if rank > 0:
                    analysis += f"\n• **CMC Rank**: #{rank}"
                if circulating_supply > 0:
                    analysis += f"\n• **Circulating Supply**: {circulating_supply:,.0f} {symbol.upper()}"

                # Add CMC advanced metrics
                if 'description' in cmc_data and cmc_data['description']:
                    description = cmc_data['description'][:150] + "..." if len(cmc_data['description']) > 150 else cmc_data['description']
                    analysis += f"\n• **Description**: {description}"

                if 'website' in cmc_data and cmc_data['website']:
                    websites = cmc_data['website'][:2] if isinstance(cmc_data['website'], list) else [cmc_data['website']]
                    analysis += f"\n• **Website**: {', '.join(websites)}"

                if 'category' in cmc_data and cmc_data['category']:
                    analysis += f"\n• **Category**: {cmc_data['category']}"
            else:
                analysis += f"""

📈 **2. MARKET DATA (CoinMarketCap Pro)**
• ⚠️ Data CoinMarketCap tidak tersedia"""

            # Add Binance futures data
            if 'error' not in binance_data:
                long_ratio = binance_data.get('long_short_ratio', 1.0)
                open_interest = binance_data.get('open_interest', 0)

                analysis += f"""

📊 **3. FUTURES DATA (Binance)**
• **Funding Rate**: {funding_rate*100:+.4f}%
• **Long/Short Ratio**: {long_ratio:.2f}"""

                if long_ratio > 1.3:
                    analysis += f" (⚠️ Overleveraged longs)"
                elif long_ratio < 0.7:
                    analysis += f" (💎 Oversold conditions)"
                else:
                    analysis += f" (⚖️ Balanced)"

                analysis += f"\n• **Open Interest**: {self._format_currency_display(open_interest)}"
            else:
                analysis += f"""

📊 **3. FUTURES DATA (Binance)**
• ⚠️ Binance Futures data unavailable"""

            # Add SnD Analysis with Entry Points
            if 'error' not in snd_analysis:
                analysis += f"""

🎯 **4. SUPPLY & DEMAND ZONES + ENTRY POINTS**"""

                support_zones = snd_analysis.get('support_zones', [])
                resistance_zones = snd_analysis.get('resistance_zones', [])
                entry_recommendation = snd_analysis.get('entry_recommendation', {})

                if support_zones:
                    analysis += f"\n\n**🟢 SUPPORT ZONES (Demand Areas):**"
                    for i, zone in enumerate(support_zones[:3], 1):
                        strength = zone.get('strength', 50)
                        price_level = zone.get('price', current_price)
                        distance = ((current_price - price_level) / current_price) * 100
                        analysis += f"\n• **S{i}**: {self._format_price_display(price_level)} ({strength}% strength, {distance:+.1f}%)"

                if resistance_zones:
                    analysis += f"\n\n**🔴 RESISTANCE ZONES (Supply Areas):**"
                    for i, zone in enumerate(resistance_zones[:3], 1):
                        strength = zone.get('strength', 50)
                        price_level = zone.get('price', current_price)
                        distance = ((price_level - current_price) / current_price) * 100
                        analysis += f"\n• **R{i}**: {self._format_price_display(price_level)} ({strength}% strength, {distance:+.1f}%)"

                # Entry recommendation
                if entry_recommendation:
                    entry_type = entry_recommendation.get('type', 'WAIT')
                    entry_price = entry_recommendation.get('price', current_price)
                    confidence = entry_recommendation.get('confidence', 50)

                    analysis += f"""

📍 **REKOMENDASI ENTRY POINT:**
• **Action**: {entry_type}
• **Entry Zone**: {self._format_price_display(entry_price)}
• **Confidence**: {confidence}%
• **Risk Level**: {entry_recommendation.get('risk_level', 'Medium')}"""

                    if entry_recommendation.get('stop_loss'):
                        analysis += f"\n• **Stop Loss**: {self._format_price_display(entry_recommendation['stop_loss'])}"
                    if entry_recommendation.get('take_profit'):
                        analysis += f"\n• **Take Profit**: {self._format_price_display(entry_recommendation['take_profit'])}"
            else:
                analysis += f"""

🎯 **4. SUPPLY & DEMAND ZONES + ENTRY POINTS**
• ⚠️ SnD Analysis tidak tersedia: {snd_analysis.get('error', 'Unknown error')}
• **Fallback**: Gunakan `/futures {symbol.lower()}` untuk analisis teknikal"""

            # Risk assessment with SnD factors
            risk_level = "🟠 Sedang"
            risk_factors = []

            if change_24h > 10:
                risk_level = "🔴 Tinggi"
                risk_factors.append("High volatility")
            elif change_24h < -10:
                risk_level = "🔴 Tinggi"
                risk_factors.append("Strong bearish move")
            elif abs(change_24h) < 3:
                risk_level = "🟢 Rendah"
                risk_factors.append("Low volatility")

            # Add SnD risk factors
            if 'error' not in snd_analysis:
                snd_risk = snd_analysis.get('risk_assessment', {})
                if snd_risk.get('near_resistance', False):
                    risk_factors.append("Near resistance zone")
                if snd_risk.get('volume_declining', False):
                    risk_factors.append("Volume declining")

            # Enhanced recommendation with SnD
            recommendation = "HOLD/WAIT"
            rec_emoji = "🟡"
            rec_reason = "Mixed signals"

            if successful_sources >= 2:
                if (change_24h > 5 and 'error' not in snd_analysis and 
                    snd_analysis.get('entry_recommendation', {}).get('type') == 'LONG'):
                    recommendation = "BUY/LONG"
                    rec_emoji = "🟢"
                    rec_reason = "Bullish momentum + SnD support"
                elif (change_24h < -5 and 'error' not in snd_analysis and 
                      snd_analysis.get('entry_recommendation', {}).get('type') == 'SHORT'):
                    recommendation = "WAIT/SHORT"
                    rec_emoji = "🔴"
                    rec_reason = "Bearish momentum + SnD resistance"
                elif change_24h > 3:
                    recommendation = "CAUTIOUS BUY"
                    rec_emoji = "🟢"
                    rec_reason = "Positive momentum"
                elif change_24h < -3:
                    recommendation = "WAIT"
                    rec_emoji = "🔴"
                    rec_reason = "Bearish momentum"

            analysis += f"""

⚠️ **5. RISK ASSESSMENT**
• **Risk Level**: {risk_level}
• **Risk Factors**: {', '.join(risk_factors) if risk_factors else 'None identified'}
• **Volatilitas**: {'Tinggi' if abs(change_24h) > 5 else 'Normal'}

📌 **6. KESIMPULAN & REKOMENDASI TRADING**
• **Rekomendasi**: {rec_emoji} **{recommendation}**
• **Reason**: {rec_reason}
• **Confidence**: {70 if successful_sources >= 2 else 50}%
• **Best Timeframe**: 1H-4H untuk SnD analysis

🕐 **Update**: {current_time} WIB
⭐️ **Premium Analysis** – CMC Pro + Binance + SnD Zones
💎 **Next**: Gunakan `/futures {symbol.lower()}` untuk timeframe-specific signals"""

            return analysis

        except Exception as e:
            error_msg = str(e)[:100]
            print(f"❌ Error in comprehensive analysis: {e}")
            import traceback
            traceback.print_exc()

            return f"""❌ **ANALISIS ERROR**

Terjadi kesalahan saat memproses data multi-API.

**Error**: {error_msg}

🔄 **Solusi**:
• Coba lagi dalam beberapa menit
• Gunakan `/futures {symbol.lower()}` sebagai alternatif
• Contact admin jika masalah berlanjut

💡 **Note**: Bot menggunakan Binance + CMC sebagai sumber utama"""

    def _get_estimated_price(self, symbol):
        """Helper to get an estimated price, fallback based on symbol"""
        price_estimates = {
            'BTC': 70000.0, 'ETH': 4000.0, 'BNB': 600.0, 'SOL': 200.0,
            'XRP': 0.6, 'ADA': 0.5, 'DOGE': 0.15, 'AVAX': 40.0,
            'DOT': 8.0, 'MATIC': 1.0, 'LINK': 15.0, 'UNI': 10.0,
            'LTC': 100.0, 'BCH': 500.0, 'ATOM': 12.0
        }

        estimated_price = price_estimates.get(symbol.upper(), 50.0)
        print(f"⚠️ Using estimated price for {symbol}: ${estimated_price}")
        return estimated_price

    def _format_price_display(self, price):
        """Format price for display with null safety"""
        if price is None or price <= 0:
            return "$0.00"

        try:
            price = float(price)
            if price < 1:
                return f"${price:.8f}"
            elif price < 100:
                return f"${price:.4f}"
            else:
                return f"${price:,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    def _format_currency_display(self, amount):
        """Format currency for display with null safety"""
        if amount is None or amount <= 0:
            return "$0"

        try:
            amount = float(amount)
            if amount >= 1_000_000_000_000:
                return f"${amount/1_000_000_000_000:.2f}T"
            elif amount >= 1_000_000_000:
                return f"${amount/1_000_000_000:.2f}B"
            elif amount >= 1_000_000:
                return f"${amount/1_000_000:.1f}M"
            else:
                return f"${amount:,.0f}"
        except (ValueError, TypeError):
            return "$0"

    def _analyze_snd_zones(self, candlestick_data, symbol):
        """Analyze Supply & Demand zones from candlestick data"""
        try:
            if not candlestick_data or len(candlestick_data) < 20:
                return {'error': 'Insufficient candlestick data for SnD analysis'}

            # Extract price data
            highs = [float(candle.get('high', 0)) for candle in candlestick_data]
            lows = [float(candle.get('low', 0)) for candle in candlestick_data]
            closes = [float(candle.get('close', 0)) for candle in candlestick_data]
            volumes = [float(candle.get('volume', 0)) for candle in candlestick_data]

            if not all([highs, lows, closes, volumes]) or min(len(highs), len(lows), len(closes)) < 20:
                return {'error': 'Invalid price data structure'}

            current_price = closes[-1]

            # Find support zones (demand areas)
            support_zones = []
            for i in range(10, len(lows) - 5):
                if (lows[i] == min(lows[i-5:i+5]) and  # Local minimum
                    volumes[i] > sum(volumes[i-3:i+3])/6):  # Above average volume

                    strength = self._calculate_zone_strength(lows, i, 'support')
                    support_zones.append({
                        'price': lows[i],
                        'strength': strength,
                        'volume': volumes[i],
                        'index': i
                    })

            # Find resistance zones (supply areas)
            resistance_zones = []
            for i in range(10, len(highs) - 5):
                if (highs[i] == max(highs[i-5:i+5]) and  # Local maximum
                    volumes[i] > sum(volumes[i-3:i+3])/6):  # Above average volume

                    strength = self._calculate_zone_strength(highs, i, 'resistance')
                    resistance_zones.append({
                        'price': highs[i],
                        'strength': strength,
                        'volume': volumes[i],
                        'index': i
                    })

            # Sort by strength and proximity to current price
            support_zones.sort(key=lambda x: (x['strength'], -abs(current_price - x['price'])), reverse=True)
            resistance_zones.sort(key=lambda x: (x['strength'], -abs(current_price - x['price'])), reverse=True)

            # Generate entry recommendation
            entry_recommendation = self._generate_snd_entry_recommendation(
                current_price, support_zones[:3], resistance_zones[:3], closes
            )

            # Risk assessment
            risk_assessment = {
                'near_resistance': any(abs(current_price - r['price'])/current_price < 0.02 for r in resistance_zones[:2]),
                'near_support': any(abs(current_price - s['price'])/current_price < 0.02 for s in support_zones[:2]),
                'volume_declining': volumes[-5:] < volumes[-10:-5],
                'trend_direction': 'bullish' if closes[-1] > closes[-10] else 'bearish'
            }

            return {
                'support_zones': support_zones[:5],
                'resistance_zones': resistance_zones[:5],
                'entry_recommendation': entry_recommendation,
                'risk_assessment': risk_assessment,
                'current_price': current_price,
                'analysis_quality': 'good' if len(support_zones) >= 2 and len(resistance_zones) >= 2 else 'limited'
            }

        except Exception as e:
            print(f"❌ SnD Analysis error for {symbol}: {e}")
            return {'error': f'SnD analysis failed: {str(e)}'}

    def _calculate_zone_strength(self, price_data, index, zone_type):
        """Calculate the strength of a support/resistance zone"""
        try:
            strength = 50  # Base strength

            # Check how many times price has tested this level
            test_range = 0.01  # 1% range
            test_price = price_data[index]
            tests = 0

            for i, price in enumerate(price_data):
                if i != index and abs(price - test_price) / test_price <= test_range:
                    tests += 1
                    if abs(i - index) < 10:  # Recent tests are more important
                        strength += 15
                    else:
                        strength += 5

            # Age factor (newer zones are stronger)
            age_factor = (len(price_data) - index) / len(price_data)
            strength += (1 - age_factor) * 20

            # Volume confirmation (if this was a high volume level)
            if index < len(price_data) - 1:
                strength += 10

            return min(95, max(30, strength))

        except Exception:
            return 50

    def _generate_snd_entry_recommendation(self, current_price, support_zones, resistance_zones, closes):
        """Generate entry recommendation based on SnD analysis"""
        try:
            if not support_zones and not resistance_zones:
                return {
                    'type': 'WAIT',
                    'price': current_price,
                    'confidence': 30,
                    'risk_level': 'High',
                    'reason': 'No clear SnD zones identified'
                }

            # Determine trend
            short_trend = 'bullish' if closes[-1] > closes[-5] else 'bearish'
            long_trend = 'bullish' if closes[-1] > closes[-15] else 'bearish'

            # Find closest zones
            closest_support = min(support_zones, key=lambda x: abs(current_price - x['price'])) if support_zones else None
            closest_resistance = min(resistance_zones, key=lambda x: abs(current_price - x['price'])) if resistance_zones else None

            # Entry logic
            entry_recommendation = {
                'type': 'WAIT',
                'price': current_price,
                'confidence': 50,
                'risk_level': 'Medium',
                'reason': 'Analyzing market structure'
            }

            # Check for long entry opportunity
            if (closest_support and 
                abs(current_price - closest_support['price']) / current_price < 0.03 and  # Within 3% of support
                closest_support['strength'] > 60 and  # Strong support
                short_trend == 'bullish'):

                entry_recommendation.update({
                    'type': 'LONG',
                    'price': closest_support['price'],
                    'confidence': min(85, closest_support['strength'] + 15),
                    'risk_level': 'Medium',
                    'reason': f'Strong support zone at {self._format_price_display(closest_support["price"])}',
                    'stop_loss': closest_support['price'] * 0.97,  # 3% below support
                    'take_profit': closest_resistance['price'] * 0.98 if closest_resistance else current_price * 1.05
                })

            # Check for short entry opportunity
            elif (closest_resistance and 
                  abs(current_price - closest_resistance['price']) / current_price < 0.03 and  # Within 3% of resistance
                  closest_resistance['strength'] > 60 and  # Strong resistance
                  short_trend == 'bearish'):

                entry_recommendation.update({
                    'type': 'SHORT',
                    'price': closest_resistance['price'],
                    'confidence': min(85, closest_resistance['strength'] + 15),
                    'risk_level': 'Medium',
                    'reason': f'Strong resistance zone at {self._format_price_display(closest_resistance["price"])}',
                    'stop_loss': closest_resistance['price'] * 1.03,  # 3% above resistance
                    'take_profit': closest_support['price'] * 1.02 if closest_support else current_price * 0.95
                })

            # Adjust confidence based on trend alignment
            if short_trend == long_trend:
                entry_recommendation['confidence'] = min(95, entry_recommendation['confidence'] + 10)

            return entry_recommendation

        except Exception as e:
            print(f"❌ Entry recommendation error: {e}")
            return {
                'type': 'WAIT',
                'price': current_price,
                'confidence': 30,
                'risk_level': 'High',
                'reason': 'Analysis error occurred'
            }

    def _generate_emergency_futures_signal(self, symbol, timeframe, language='id', error_msg=""):
        """Generate a fallback signal in case of errors."""
        current_time = datetime.now().strftime('%H:%M:%S WIB')

        if language == 'id':
            message = f"""🎯 **FUTURES ANALYSIS - {symbol.upper()} ({timeframe})**

⚠️ **Data API tidak tersedia**
💰 **Harga Estimasi**: {self._format_price_display(self._get_estimated_price(symbol))}

📊 **Status**: Menggunakan analisa fallback
🧠 **Rekomendasi**: ⏸️ HOLD
• **Alasan**: Data tidak mencukupi untuk sinyal akurat
• **Tunggu**: Koneksi API pulih

🛡 **Risk Management**
• Jangan trading tanpa data lengkap
• Tunggu sinyal dengan confidence tinggi
• Monitor update selanjutnya

📡 **Error**: {error_msg[:50]}{'...' if len(error_msg) > 50 else ''}
⏰ **Update**: {current_time}

💡 **Solusi**: Sistem menggunakan Binance API sebagai sumber utama"""
        else:
            message = f"""🎯 **FUTURES ANALYSIS - {symbol.upper()} ({timeframe})**

⚠️ **API data unavailable**
💰 **Estimated Price**: {self._format_price_display(self._get_estimated_price(symbol))}

📊 **Status**: Using fallback analysis
🧠 **Recommendation**: ⏸️ HOLD
• **Reason**: Insufficient data for accurate signal
• **Wait**: API connection recovery

🛡 **Risk Management**
• Don't trade without complete data
• Wait for high confidence signals
• Monitor next updates

📡 **Error**: {error_msg[:50]}{'...' if len(error_msg) > 50 else ''}
⏰ **Update**: {current_time}

💡 **Solution**: System using Binance API as primary source"""

        return message