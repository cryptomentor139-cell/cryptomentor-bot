
# -*- coding: utf-8 -*-
import requests
import random
import os
import asyncio
import time
from datetime import datetime, timedelta
from supabase import create_client, Client
import numpy as np
import pandas as pd
import json

# Check for TA-Lib availability
TALIB_AVAILABLE = False
try:
    import talib
    TALIB_AVAILABLE = True
    print("✅ TA-Lib found and loaded.")
except ImportError:
    print("⚠️ TA-Lib not found. Falling back to pandas_ta or manual calculations.")

# Check for pandas_ta availability
ta = None
try:
    import pandas_ta as ta
    print("✅ pandas_ta found and loaded.")
except ImportError:
    print("⚠️ pandas_ta not found. Falling back to manual calculations.")


class AIAssistant:
    def __init__(self, name="CryptoMentor AI"):
        self.name = name
        self.coinapi_key = os.getenv("COINAPI_API_KEY")
        self.cmc_api_key = os.getenv("COINMARKETCAP_API_KEY")
        
        self.coinapi_headers = {
            "X-CoinAPI-Key": self.coinapi_key
        } if self.coinapi_key else {}
        
        self.cmc_headers = {
            "X-CMC_PRO_API_KEY": self.cmc_api_key,
            "Accept": "application/json"
        } if self.cmc_api_key else {}

        # Initialize Supabase connection
        self.supabase = self._init_supabase()

        # Auto Signal System
        self.auto_signal_enabled = True
        self.auto_signal_task = None
        self.last_signal_time = {}  # Track last signal time per symbol
        self.signal_cooldown = 60 * 60  # 1 hour cooldown as requested
        self.scan_interval = 5 * 60  # 5 minutes scan interval
        self.target_symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'AVAX', 'MATIC', 'DOT', 'LINK']
        self.last_sent_signals = {}  # Anti-duplicate mechanism

        # Enhanced Parameters
        self.confidence_threshold = 75.0  # Minimum confidence for signals
        self.timeframes = ['5MIN', '1HRS', '4HRS']  # Multi-timeframe analysis

        print(f"✅ AI Assistant initialized with CoinAPI + CoinMarketCap integration")

    def _init_supabase(self):
        """Initialize Supabase client"""
        try:
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_anon_key = <REDACTED_SUPABASE_KEY>

            if not supabase_url or not supabase_anon_key:
                print("⚠️ Supabase credentials not found in environment variables")
                return None

            supabase: Client = create_client(supabase_url, supabase_anon_key)
            print("✅ Supabase connection established")
            return supabase
        except Exception as e:
            print(f"❌ Failed to initialize Supabase: {e}")
            return None

    def save_user(self, user_id, username="", first_name="", last_name=""):
        """Save user to Supabase database using centralized user management"""
        try:
            if not self.supabase:
                return False

            # Use centralized Supabase user management from database
            from supabase_users import SupabaseUsers
            supabase_users = SupabaseUsers()

            return supabase_users.add_user(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                status='free'
            )

        except Exception as e:
            print(f"❌ Error saving user {user_id}: {e}")
            return False

    def get_user(self, user_id):
        """Get user data from Supabase using centralized user management"""
        try:
            from supabase_users import SupabaseUsers
            supabase_users = SupabaseUsers()

            return supabase_users.get_user(user_id)

        except Exception as e:
            print(f"❌ Error getting user {user_id}: {e}")
            return None

    def update_user_status(self, user_id, status):
        """Update user status in Supabase using centralized user management"""
        try:
            from supabase_users import SupabaseUsers
            supabase_users = SupabaseUsers()

            return supabase_users.update_user_status(user_id, status)

        except Exception as e:
            print(f"❌ Error updating user status: {e}")
            return False

    def greet(self):
        return f"Halo! Saya {self.name}, siap membantu analisis dan informasi crypto kamu."

    def analyze_text(self, text):
        """Simple text analysis for crypto mentions"""
        text_lower = text.lower()
        if "btc" in text_lower:
            return "📈 BTC sedang menarik untuk dianalisis hari ini!"
        elif "eth" in text_lower:
            return "📉 ETH menunjukkan sinyal konsolidasi."
        else:
            return "Saya tidak yakin, tapi saya akan bantu cari datanya."

    def help_message(self):
        return """🤖 **CryptoMentor AI - Help**

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

🚀 **Semua analisis menggunakan data real-time dari CoinAPI + CoinMarketCap!**"""

    # ============ COINAPI DATA METHODS ============

    def get_coinapi_price(self, symbol="BTC"):
        """Get price data from CoinAPI"""
        try:
            if "/" not in symbol:
                symbol = f"{symbol.upper()}/USD"

            url = f"https://rest.coinapi.io/v1/exchangerate/{symbol}"
            response = requests.get(url, headers=self.coinapi_headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'price': data.get('rate', 0),
                    'source': 'coinapi',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'error': f'CoinAPI error: {response.status_code}', 'symbol': symbol}

        except Exception as e:
            return {'error': f'CoinAPI request failed: {str(e)}', 'symbol': symbol}

    def get_coinapi_ohlcv(self, symbol="BTC", period_id="1HRS", limit=200):
        """Get OHLCV data from CoinAPI for technical analysis"""
        try:
            # Symbol mapping for major cryptocurrencies
            symbol_mapping = {
                'BTC': 'BITSTAMP_SPOT_BTC_USD',
                'ETH': 'BITSTAMP_SPOT_ETH_USD',
                'LTC': 'BITSTAMP_SPOT_LTC_USD',
                'XRP': 'BITSTAMP_SPOT_XRP_USD',
                'SOL': 'COINBASE_SPOT_SOL_USD',
                'ADA': 'COINBASE_SPOT_ADA_USD',
                'DOT': 'COINBASE_SPOT_DOT_USD',
                'LINK': 'COINBASE_SPOT_LINK_USD',
                'MATIC': 'COINBASE_SPOT_MATIC_USD',
                'AVAX': 'COINBASE_SPOT_AVAX_USD',
                'DOGE': 'COINBASE_SPOT_DOGE_USD'
            }

            coinapi_symbol = symbol_mapping.get(symbol.upper(), f"COINBASE_SPOT_{symbol.upper()}_USD")

            url = f"https://rest.coinapi.io/v1/ohlcv/{coinapi_symbol}/history"
            params = {
                'period_id': period_id,
                'limit': limit
            }

            response = requests.get(url, headers=self.coinapi_headers, params=params, timeout=20)

            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'coinapi_symbol': coinapi_symbol,
                    'period_id': period_id,
                    'data': data,
                    'source': 'coinapi_ohlcv',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'error': f'CoinAPI OHLCV error: {response.status_code}', 'symbol': symbol}

        except Exception as e:
            return {'error': f'CoinAPI OHLCV failed: {str(e)}', 'symbol': symbol}

    # ============ COINMARKETCAP DATA METHODS ============

    def get_cmc_global_metrics(self):
        """Get global market metrics from CoinMarketCap"""
        try:
            if not self.cmc_api_key:
                return {'error': 'CoinMarketCap API key not configured'}

            url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
            response = requests.get(url, headers=self.cmc_headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                quote = data.get('data', {}).get('quote', {}).get('USD', {})
                
                return {
                    'total_market_cap': quote.get('total_market_cap', 0),
                    'total_volume_24h': quote.get('total_volume_24h', 0),
                    'btc_dominance': data.get('data', {}).get('btc_dominance', 0),
                    'market_cap_change_24h': quote.get('total_market_cap_yesterday_percentage_change', 0),
                    'volume_change_24h': quote.get('total_volume_24h_yesterday_percentage_change', 0),
                    'source': 'coinmarketcap_global',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'error': f'CMC global metrics error: {response.status_code}'}

        except Exception as e:
            return {'error': f'CMC global metrics failed: {str(e)}'}

    # ============ ENHANCED TECHNICAL ANALYSIS ============

    def calculate_enhanced_indicators(self, ohlcv_data):
        """Calculate enhanced technical indicators with error handling"""
        try:
            if not ohlcv_data or len(ohlcv_data) < 200:
                return {'success': False, 'error': 'Insufficient data for indicators (need 200+ candles)'}

            # Extract price data
            closes = np.array([float(candle.get('price_close', 0)) for candle in ohlcv_data])
            highs = np.array([float(candle.get('price_high', 0)) for candle in ohlcv_data])
            lows = np.array([float(candle.get('price_low', 0)) for candle in ohlcv_data])
            volumes = np.array([float(candle.get('volume_traded', 0)) for candle in ohlcv_data])

            # Calculate indicators based on available library
            if TALIB_AVAILABLE:
                # Use TA-Lib for precise calculations
                ema50 = talib.EMA(closes, timeperiod=50)
                ema200 = talib.EMA(closes, timeperiod=200)
                rsi = talib.RSI(closes, timeperiod=14)
                macd, macd_signal, macd_hist = talib.MACD(closes)
                atr = talib.ATR(highs, lows, closes, timeperiod=14)
            else:
                # Fallback to manual calculations
                ema50 = self._calculate_ema(closes, 50)
                ema200 = self._calculate_ema(closes, 200)
                rsi = self._calculate_rsi(closes, 14)
                macd = self._calculate_macd(closes)
                macd_hist = self._calculate_macd_histogram(closes)
                atr = self._calculate_atr(highs, lows, closes, 14)

            # Volume oscillator
            vol_fast = self._calculate_sma(volumes, 14)
            vol_slow = self._calculate_sma(volumes, 28)
            vol_oscillator = ((vol_fast - vol_slow) / np.maximum(vol_slow, 1)) * 100

            # Get latest values with null checks
            current_price = closes[-1] if len(closes) > 0 else 0
            current_ema50 = ema50[-1] if len(ema50) > 0 and not np.isnan(ema50[-1]) else 0
            current_ema200 = ema200[-1] if len(ema200) > 0 and not np.isnan(ema200[-1]) else 0
            current_rsi = rsi[-1] if len(rsi) > 0 and not np.isnan(rsi[-1]) else 50
            current_macd = macd[-1] if len(macd) > 0 and not np.isnan(macd[-1]) else 0
            current_macd_hist = macd_hist[-1] if len(macd_hist) > 0 and not np.isnan(macd_hist[-1]) else 0
            current_atr = atr[-1] if len(atr) > 0 and not np.isnan(atr[-1]) else current_price * 0.02
            current_vol_osc = vol_oscillator[-1] if len(vol_oscillator) > 0 and not np.isnan(vol_oscillator[-1]) else 0

            # Determine trend
            trend = "bullish" if current_ema50 > current_ema200 else "bearish"

            return {
                'success': True,
                'current_price': current_price,
                'ema50': current_ema50,
                'ema200': current_ema200,
                'rsi': current_rsi,
                'macd': current_macd,
                'macd_histogram': current_macd_hist,
                'atr': current_atr,
                'volume_oscillator': current_vol_osc,
                'trend': trend,
                'atr_avg': np.mean(atr[-14:]) if len(atr) >= 14 else current_atr
            }

        except Exception as e:
            return {'success': False, 'error': f'Technical analysis failed: {str(e)}'}

    def calculate_confidence_score(self, technical_5m, technical_1h, technical_4h, global_metrics):
        """Calculate confidence score based on technical + macro factors"""
        try:
            technical_score = 0
            macro_score = 0

            # TECHNICAL ANALYSIS SCORING (50 points max)
            # Use 1H timeframe as primary for scoring
            tech_data = technical_1h if technical_1h.get('success') else technical_4h

            if tech_data and tech_data.get('success'):
                # EMA Trend alignment (15 points)
                ema50 = tech_data.get('ema50', 0)
                ema200 = tech_data.get('ema200', 0)
                if ema50 > ema200:  # Bullish trend
                    technical_score += 15
                elif ema50 < ema200:  # Bearish trend (for SHORT signals)
                    technical_score += 15

                # RSI healthy zone (10 points for 45-65, 5 points for 40-70)
                rsi = tech_data.get('rsi', 50)
                if 45 <= rsi <= 65:
                    technical_score += 10
                elif 40 <= rsi <= 70:
                    technical_score += 5

                # MACD histogram alignment (10 points)
                macd_hist = tech_data.get('macd_histogram', 0)
                if (ema50 > ema200 and macd_hist > 0) or (ema50 < ema200 and macd_hist < 0):
                    technical_score += 10

                # Volume oscillator (5 points)
                vol_osc = tech_data.get('volume_oscillator', 0)
                if vol_osc > 0:
                    technical_score += 5

                # ATR volatility health (5 points)
                atr = tech_data.get('atr', 0)
                atr_avg = tech_data.get('atr_avg', 0)
                if atr > atr_avg:
                    technical_score += 5

            # MACRO ANALYSIS SCORING (50 points max)
            if global_metrics and 'error' not in global_metrics:
                # Market cap change (15 points for >1% up, 5 points for <3% down)
                mc_change = global_metrics.get('market_cap_change_24h', 0)
                if mc_change > 1:
                    macro_score += 15
                elif mc_change > -3:
                    macro_score += 5

                # Volume change (10 points for >5% up)
                vol_change = global_metrics.get('volume_change_24h', 0)
                if vol_change > 5:
                    macro_score += 10

                # BTC dominance stability (10 points for ±1%)
                btc_dom = global_metrics.get('btc_dominance', 50)
                # Assume previous BTC dominance was around 50% (simplified)
                if abs(btc_dom - 50) <= 1:
                    macro_score += 10

                # Global sentiment alignment (15 points)
                if mc_change > 0 and vol_change > 0:
                    macro_score += 15

            total_score = min(100, technical_score + macro_score)
            
            return {
                'total_score': total_score,
                'technical_score': technical_score,
                'macro_score': macro_score,
                'meets_threshold': total_score >= self.confidence_threshold
            }

        except Exception as e:
            return {
                'total_score': 0,
                'technical_score': 0,
                'macro_score': 0,
                'meets_threshold': False,
                'error': str(e)
            }

    def multi_timeframe_analysis(self, symbol):
        """Perform multi-timeframe analysis for enhanced signals"""
        try:
            # Get OHLCV data for all timeframes
            data_5m = self.get_coinapi_ohlcv(symbol, '5MIN', 200)
            data_1h = self.get_coinapi_ohlcv(symbol, '1HRS', 200)
            data_4h = self.get_coinapi_ohlcv(symbol, '4HRS', 200)

            # Calculate indicators for each timeframe
            tech_5m = None
            tech_1h = None
            tech_4h = None

            if 'error' not in data_5m:
                tech_5m = self.calculate_enhanced_indicators(data_5m.get('data', []))

            if 'error' not in data_1h:
                tech_1h = self.calculate_enhanced_indicators(data_1h.get('data', []))

            if 'error' not in data_4h:
                tech_4h = self.calculate_enhanced_indicators(data_4h.get('data', []))

            # Get global market metrics
            global_metrics = self.get_cmc_global_metrics()

            # Calculate confidence score
            confidence = self.calculate_confidence_score(tech_5m, tech_1h, tech_4h, global_metrics)

            # Multi-timeframe confirmation
            timeframe_alignment = self.check_timeframe_alignment(tech_5m, tech_1h, tech_4h)

            return {
                'symbol': symbol,
                'technical_5m': tech_5m,
                'technical_1h': tech_1h,
                'technical_4h': tech_4h,
                'global_metrics': global_metrics,
                'confidence_score': confidence,
                'timeframe_alignment': timeframe_alignment,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'symbol': symbol,
                'error': f'Multi-timeframe analysis failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

    def check_timeframe_alignment(self, tech_5m, tech_1h, tech_4h):
        """Check if 5m and 1H timeframes are aligned for signal confirmation"""
        try:
            if not tech_5m or not tech_1h or not tech_5m.get('success') or not tech_1h.get('success'):
                return {'aligned': False, 'reason': 'Insufficient timeframe data'}

            # Check trend alignment between 5m and 1H
            trend_5m = tech_5m.get('trend')
            trend_1h = tech_1h.get('trend')

            if trend_5m == trend_1h:
                return {
                    'aligned': True,
                    'direction': trend_5m,
                    'reason': f'5m and 1H both show {trend_5m} trend'
                }
            else:
                return {
                    'aligned': False,
                    'reason': f'Conflicting trends: 5m={trend_5m}, 1H={trend_1h}'
                }

        except Exception as e:
            return {'aligned': False, 'reason': f'Alignment check failed: {str(e)}'}

    # ============ SIGNAL GENERATION METHODS ============

    def generate_enhanced_signal(self, symbol):
        """Generate enhanced signal with confidence scoring"""
        try:
            # Check cooldown
            current_time = time.time()
            if symbol in self.last_signal_time:
                time_since_last = current_time - self.last_signal_time[symbol]
                if time_since_last < self.signal_cooldown:
                    return None

            # Perform multi-timeframe analysis
            analysis = self.multi_timeframe_analysis(symbol)

            if 'error' in analysis:
                return None

            confidence = analysis.get('confidence_score', {})
            timeframe_alignment = analysis.get('timeframe_alignment', {})

            # Check if signal meets criteria
            if not confidence.get('meets_threshold', False):
                return None

            if not timeframe_alignment.get('aligned', False):
                return None

            # Determine signal direction
            direction = 'BUY' if timeframe_alignment.get('direction') == 'bullish' else 'SELL'

            # Get technical data for signal levels
            tech_1h = analysis.get('technical_1h', {})
            current_price = tech_1h.get('current_price', 0)
            atr = tech_1h.get('atr', current_price * 0.02)

            # Calculate entry, stop loss, and take profit levels
            if direction == 'BUY':
                entry_price = current_price
                stop_loss = current_price - (atr * 2)
                tp1 = current_price + (atr * 2)
                tp2 = current_price + (atr * 4)
            else:  # SELL
                entry_price = current_price
                stop_loss = current_price + (atr * 2)
                tp1 = current_price - (atr * 2)
                tp2 = current_price - (atr * 4)

            # Store signal timestamp
            self.last_signal_time[symbol] = current_time

            # Save signal to Supabase for cooldown tracking
            self.save_signal_to_supabase(symbol, direction, confidence.get('total_score'), current_time)

            return {
                'symbol': symbol,
                'direction': direction,
                'confidence': confidence.get('total_score', 0),
                'technical_score': confidence.get('technical_score', 0),
                'macro_score': confidence.get('macro_score', 0),
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'tp1': tp1,
                'tp2': tp2,
                'current_price': current_price,
                'ema50': tech_1h.get('ema50', 0),
                'ema200': tech_1h.get('ema200', 0),
                'rsi': tech_1h.get('rsi', 0),
                'macd': tech_1h.get('macd', 0),
                'atr': atr,
                'market_cap_change': analysis.get('global_metrics', {}).get('market_cap_change_24h', 0),
                'volume_change': analysis.get('global_metrics', {}).get('volume_change_24h', 0),
                'timeframe_confirmation': '5m & 1H selaras',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error generating enhanced signal for {symbol}: {e}")
            return None

    def save_signal_to_supabase(self, symbol, direction, confidence, timestamp):
        """Save signal to Supabase for cooldown tracking"""
        try:
            if not self.supabase:
                return False

            signal_data = {
                'symbol': symbol,
                'direction': direction,
                'confidence': confidence,
                'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                'created_at': datetime.now().isoformat()
            }

            self.supabase.table('futures_signals').insert(signal_data).execute()
            return True

        except Exception as e:
            print(f"Error saving signal to Supabase: {e}")
            return False

    # ============ MAIN API METHODS ============

    def analyze_futures_coinapi(self, symbol="BTC", user_id=None):
        """Enhanced futures analysis using CoinAPI + CMC data"""
        try:
            if user_id:
                self.save_user(user_id)

            # Generate enhanced signal
            signal = self.generate_enhanced_signal(symbol)

            if not signal:
                # Provide basic analysis even if no strong signal
                basic_analysis = self.multi_timeframe_analysis(symbol)
                tech_1h = basic_analysis.get('technical_1h', {})
                current_price = tech_1h.get('current_price', 0) if tech_1h else 0

                return f"""🎯 FUTURES ANALYSIS - {symbol}

💰 **Current Price**: ${self._format_price(current_price)}
⚠️ **Status**: Tidak ada sinyal dengan confidence ≥ 75%

💡 **Alasan**:
• Multi-timeframe tidak selaras
• Confidence score terlalu rendah
• Cooldown period masih aktif

🔄 **Saran**:
• Tunggu konfirmasi yang lebih kuat
• Monitor perubahan trend
• Coba lagi dalam 1 jam

📊 **Data Source**: CoinAPI + CoinMarketCap
🕐 **Analysis Time**: {datetime.now().strftime('%H:%M:%S WIB')}"""

            # Format signal output
            direction_emoji = "🟢" if signal['direction'] == 'BUY' else "🔴"
            
            return f"""🚀 FUTURES SIGNAL - {symbol}

{direction_emoji} **SIGNAL**: **{signal['direction']}** (Confidence: {signal['confidence']:.1f}%)

💰 **PRICE DATA**:
• Current Price: ${self._format_price(signal['current_price'])}
• Entry: ${self._format_price(signal['entry_price'])}
• Stop Loss: ${self._format_price(signal['stop_loss'])}
• TP1: ${self._format_price(signal['tp1'])}
• TP2: ${self._format_price(signal['tp2'])}

📊 **TECHNICAL INDICATORS**:
• EMA50: ${self._format_price(signal['ema50'])}
• EMA200: ${self._format_price(signal['ema200'])}
• RSI: {signal['rsi']:.1f}
• MACD: {signal['macd']:.4f}
• ATR: {signal['atr']:.4f}

🌍 **MARKET METRICS**:
• Market Cap Change: {signal['market_cap_change']:+.2f}%
• Volume Change: {signal['volume_change']:+.2f}%

🎯 **CONFIDENCE BREAKDOWN**:
• Technical Score: {signal['technical_score']}/50
• Macro Score: {signal['macro_score']}/50
• Total: {signal['confidence']:.1f}/100
• Timeframe: {signal['timeframe_confirmation']}

⚠️ **RISK MANAGEMENT**:
• Position size: Max 2-3% modal
• Stop Loss WAJIB sebelum entry
• Take profit bertahap
• Monitor market conditions

📡 **Data**: CoinAPI + CoinMarketCap Real-time
🕐 **Signal Time**: {datetime.now().strftime('%H:%M:%S WIB')}"""

        except Exception as e:
            return f"❌ Enhanced futures analysis error: {str(e)}"

    async def generate_futures_signals(self, language='id', crypto_api=None, query_args=None):
        """Generate multiple futures signals with enhanced analysis"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S WIB')

            # Target symbols for analysis
            symbols_to_analyze = self.target_symbols[:5]  # Analyze top 5 symbols

            # Process query args if provided
            if query_args and len(query_args) > 0:
                first_arg = query_args[0].upper()
                if first_arg in self.target_symbols:
                    symbols_to_analyze = [first_arg]

            signals_found = []

            for symbol in symbols_to_analyze:
                try:
                    signal = self.generate_enhanced_signal(symbol)
                    if signal:
                        signals_found.append(signal)
                except Exception as e:
                    print(f"Error analyzing {symbol}: {e}")
                    continue

            if not signals_found:
                return f"""❌ **FUTURES SIGNALS - NO SIGNALS**

🕐 **Scan Time**: {current_time}
⚠️ **Status**: Tidak ditemukan sinyal dengan confidence ≥ 75%

💡 **Kemungkinan Penyebab:**
• Multi-timeframe tidak selaras
• Market dalam kondisi sideways
• Cooldown period aktif
• Confidence score rendah

🔄 **Solusi:**
• Coba lagi dalam 1 jam
• Monitor perubahan market global
• Gunakan `/futures btc` untuk analisis spesifik

📊 **Data Source**: CoinAPI + CoinMarketCap Enhanced Analysis"""

            # Format signals message
            message = f"""🚨 **ENHANCED FUTURES SIGNALS**

🕐 **Scan Time**: {current_time}
📊 **Signals Found**: {len(signals_found)} (Confidence ≥ 75%)
⚡ **Analysis**: Multi-timeframe + Global Macro

"""

            for i, signal in enumerate(signals_found, 1):
                direction_emoji = "🟢" if signal['direction'] == 'BUY' else "🔴"
                
                message += f"""**{i}. {signal['symbol']} {direction_emoji} {signal['direction']}**
🔥 **Confidence**: {signal['confidence']:.1f}% ({signal['technical_score']}+{signal['macro_score']})
💰 **Entry**: ${self._format_price(signal['entry_price'])}
🛑 **Stop Loss**: ${self._format_price(signal['stop_loss'])}
🎯 **TP1**: ${self._format_price(signal['tp1'])} | **TP2**: ${self._format_price(signal['tp2'])}
📊 **EMA50**: {self._format_price(signal['ema50'])} | **EMA200**: {self._format_price(signal['ema200'])}
📈 **RSI**: {signal['rsi']:.1f} | **MACD**: {signal['macd']:.4f} | **ATR**: {signal['atr']:.4f}
🌍 **Market Cap**: {signal['market_cap_change']:+.2f}% | **Volume**: {signal['volume_change']:+.2f}%

"""

            message += f"""⚠️ **ENHANCED RISK MANAGEMENT:**
• Sinyal berdasarkan multi-timeframe confirmation
• Confidence score minimum 75% (technical + macro)
• Cooldown 1 jam per coin untuk kualitas sinyal
• WAJIB gunakan Stop Loss
• Take profit bertahap untuk maksimalkan profit

🤖 **ENHANCED FEATURES:**
• ✅ Multi-timeframe analysis (5m, 1H, 4H)
• ✅ Global market macro filtering
• ✅ Advanced confidence scoring
• ✅ Anti-spam cooldown system

📡 **Data**: CoinAPI + CoinMarketCap Professional
🔄 **Update**: {current_time} WIB"""

            return message

        except Exception as e:
            return f"❌ Error generating enhanced futures signals: {str(e)}"

    def get_futures_analysis(self, symbol, timeframe, language='id', crypto_api=None):
        """Get enhanced futures analysis for specific symbol and timeframe"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S WIB')

            # Perform multi-timeframe analysis
            analysis = self.multi_timeframe_analysis(symbol)

            if 'error' in analysis:
                return f"❌ Error: {analysis['error']}"

            # Get appropriate technical data based on requested timeframe
            tech_data = None
            if '5' in timeframe or '15' in timeframe or '30' in timeframe:
                tech_data = analysis.get('technical_5m')
            elif '1h' in timeframe.lower() or '60' in timeframe:
                tech_data = analysis.get('technical_1h')
            else:
                tech_data = analysis.get('technical_4h')

            if not tech_data or not tech_data.get('success'):
                return f"❌ Gagal mendapatkan data teknikal untuk timeframe {timeframe}"

            confidence = analysis.get('confidence_score', {})
            global_metrics = analysis.get('global_metrics', {})

            current_price = tech_data.get('current_price', 0)
            
            # Generate signal levels
            atr = tech_data.get('atr', current_price * 0.02)
            trend = tech_data.get('trend', 'sideways')

            if trend == 'bullish':
                direction = 'LONG'
                entry = current_price
                sl = current_price - (atr * 2)
                tp1 = current_price + (atr * 2)
                tp2 = current_price + (atr * 3.5)
                direction_emoji = "🟢"
            else:
                direction = 'SHORT'
                entry = current_price
                sl = current_price + (atr * 2)
                tp1 = current_price - (atr * 2)
                tp2 = current_price - (atr * 3.5)
                direction_emoji = "🔴"

            analysis_text = f"""🚨 **ENHANCED FUTURES ANALYSIS - {symbol} ({timeframe.upper()})**

💰 **CURRENT DATA**:
• Price: ${self._format_price(current_price)}
• Trend: {trend.upper()}
• Timeframe: {timeframe.upper()}

{direction_emoji} **SIGNAL: {direction}**
• Entry: ${self._format_price(entry)}
• Stop Loss: ${self._format_price(sl)}
• TP1: ${self._format_price(tp1)}
• TP2: ${self._format_price(tp2)}

📊 **TECHNICAL INDICATORS**:
• EMA50: ${self._format_price(tech_data.get('ema50', 0))}
• EMA200: ${self._format_price(tech_data.get('ema200', 0))}
• RSI: {tech_data.get('rsi', 0):.1f}
• MACD: {tech_data.get('macd', 0):.4f}
• MACD Histogram: {tech_data.get('macd_histogram', 0):.4f}
• ATR: {tech_data.get('atr', 0):.4f}
• Volume Oscillator: {tech_data.get('volume_oscillator', 0):.1f}%

🌍 **GLOBAL MARKET METRICS**:"""

            if 'error' not in global_metrics:
                analysis_text += f"""
• Market Cap Change 24h: {global_metrics.get('market_cap_change_24h', 0):+.2f}%
• Volume Change 24h: {global_metrics.get('volume_change_24h', 0):+.2f}%
• BTC Dominance: {global_metrics.get('btc_dominance', 0):.1f}%
• Total Market Cap: ${global_metrics.get('total_market_cap', 0)/1e12:.2f}T"""
            else:
                analysis_text += f"""
• Status: ⚠️ Data makro tidak tersedia
• Reason: {global_metrics.get('error', 'Unknown')}"""

            analysis_text += f"""

🎯 **CONFIDENCE ANALYSIS**:
• Technical Score: {confidence.get('technical_score', 0)}/50
• Macro Score: {confidence.get('macro_score', 0)}/50
• **Total Confidence**: {confidence.get('total_score', 0):.1f}/100
• Signal Quality: {'✅ HIGH' if confidence.get('total_score', 0) >= 75 else '⚠️ MODERATE' if confidence.get('total_score', 0) >= 60 else '❌ LOW'}

⚠️ **RISK MANAGEMENT**:
• Gunakan maksimal 2-3% modal per trade
• Stop Loss WAJIB sebelum entry
• Take profit bertahap (50% TP1, 50% TP2)
• Monitor global market conditions
• Confidence minimum 75% untuk auto-signal

📡 **Enhanced Data**: CoinAPI Multi-timeframe + CoinMarketCap Global
🔄 **Analysis Time**: {current_time} WIB
💎 **Quality**: Professional Grade Analysis"""

            return analysis_text

        except Exception as e:
            return f"❌ Error in enhanced futures analysis: {str(e)}"

    def get_market_sentiment(self, language='id', crypto_api=None):
        """Get comprehensive market sentiment using CMC global data"""
        try:
            current_time = datetime.now().strftime('%H:%M:%S WIB')
            
            # Get global metrics from CoinMarketCap
            global_data = self.get_cmc_global_metrics()
            
            if 'error' in global_data:
                return f"❌ Error getting market data: {global_data['error']}"

            # Get sample price data for major cryptocurrencies
            btc_price = self.get_coinapi_price('BTC')
            eth_price = self.get_coinapi_price('ETH')

            # Calculate sentiment score
            sentiment_score = 0
            sentiment_factors = []

            # Market cap change analysis
            mc_change = global_data.get('market_cap_change_24h', 0)
            if mc_change > 2:
                sentiment_score += 25
                sentiment_factors.append(f"📈 Market cap naik {mc_change:+.2f}% (Bullish)")
            elif mc_change > 0:
                sentiment_score += 15
                sentiment_factors.append(f"📊 Market cap naik {mc_change:+.2f}% (Netral+)")
            elif mc_change > -3:
                sentiment_score += 5
                sentiment_factors.append(f"📉 Market cap turun {mc_change:+.2f}% (Netral-)")
            else:
                sentiment_factors.append(f"🔴 Market cap turun {mc_change:+.2f}% (Bearish)")

            # Volume analysis
            vol_change = global_data.get('volume_change_24h', 0)
            if vol_change > 10:
                sentiment_score += 20
                sentiment_factors.append(f"🚀 Volume naik {vol_change:+.2f}% (Strong Interest)")
            elif vol_change > 5:
                sentiment_score += 10
                sentiment_factors.append(f"📈 Volume naik {vol_change:+.2f}% (Good Interest)")
            elif vol_change > -5:
                sentiment_score += 5
                sentiment_factors.append(f"📊 Volume stabil {vol_change:+.2f}% (Normal)")
            else:
                sentiment_factors.append(f"📉 Volume turun {vol_change:+.2f}% (Low Interest)")

            # BTC dominance analysis
            btc_dom = global_data.get('btc_dominance', 50)
            if 45 <= btc_dom <= 55:
                sentiment_score += 15
                sentiment_factors.append(f"⚖️ BTC dominance sehat {btc_dom:.1f}%")
            else:
                sentiment_factors.append(f"📊 BTC dominance {btc_dom:.1f}%")

            # Overall sentiment
            if sentiment_score >= 50:
                overall_sentiment = "🟢 BULLISH"
                sentiment_desc = "Market menunjukkan sinyal positif kuat"
            elif sentiment_score >= 30:
                overall_sentiment = "🟡 NETRAL POSITIF"
                sentiment_desc = "Market cenderung positif dengan beberapa kekhawatiran"
            elif sentiment_score >= 15:
                overall_sentiment = "🟠 NETRAL NEGATIF"
                sentiment_desc = "Market menunjukkan kekhawatiran dengan beberapa sinyal positif"
            else:
                overall_sentiment = "🔴 BEARISH"
                sentiment_desc = "Market menunjukkan sinyal negatif kuat"

            market_analysis = f"""🌍 **MARKET SENTIMENT ANALYSIS**

📊 **OVERALL SENTIMENT**: {overall_sentiment}
💭 **Assessment**: {sentiment_desc}
🎯 **Confidence Score**: {sentiment_score}/100

💰 **GLOBAL MARKET DATA**:
• Total Market Cap: ${global_data.get('total_market_cap', 0)/1e12:.2f}T
• Market Cap Change 24h: {mc_change:+.2f}%
• Total Volume 24h: ${global_data.get('total_volume_24h', 0)/1e9:.1f}B
• Volume Change 24h: {vol_change:+.2f}%
• BTC Dominance: {btc_dom:.1f}%

🔍 **SENTIMENT FACTORS**:"""

            for factor in sentiment_factors:
                market_analysis += f"\n• {factor}"

            # Add major crypto prices
            if 'error' not in btc_price and 'error' not in eth_price:
                market_analysis += f"""

💎 **MAJOR CRYPTOCURRENCIES**:
• Bitcoin (BTC): ${self._format_price(btc_price.get('price', 0))}
• Ethereum (ETH): ${self._format_price(eth_price.get('price', 0))}"""

            market_analysis += f"""

🎯 **TRADING IMPLICATIONS**:"""

            if sentiment_score >= 50:
                market_analysis += """
• ✅ Kondisi baik untuk posisi LONG
• ✅ DCA strategy recommended
• ⚠️ Tetap gunakan stop loss"""
            elif sentiment_score >= 30:
                market_analysis += """
• 🟡 Hati-hati dengan posisi besar
• ✅ Scalping opportunities tersedia
• ⚠️ Monitor news & events"""
            else:
                market_analysis += """
• 🔴 Hindari posisi LONG besar
• ✅ Short opportunities mungkin ada
• 🛡️ Fokus pada risk management"""

            market_analysis += f"""

📡 **Data Source**: CoinMarketCap Global + CoinAPI Prices
🔄 **Update Time**: {current_time} WIB
💎 **Professional Market Analysis**"""

            return market_analysis

        except Exception as e:
            return f"❌ Market sentiment analysis error: {str(e)}"

    # ============ AUTO SIGNAL SYSTEM ============

    async def start_auto_signal_system(self, bot_instance=None):
        """Start the Auto Signal background task with enhanced analysis"""
        if self.auto_signal_task is None or self.auto_signal_task.done():
            self.bot_instance = bot_instance
            self.auto_signal_task = asyncio.create_task(self._auto_signal_background_loop())
            print("🚀 ENHANCED AUTO SIGNAL: Multi-timeframe detection started")
            print(f"📊 Scanning {len(self.target_symbols)} symbols every {self.scan_interval//60} minutes")
            print(f"🛡️ Cooldown: {self.signal_cooldown//60} minutes per signal")
            print(f"🎯 Minimum confidence: {self.confidence_threshold}%")

    async def stop_auto_signal_system(self):
        """Stop the Auto Signal background task"""
        if self.auto_signal_task and not self.auto_signal_task.done():
            self.auto_signal_task.cancel()
            try:
                await self.auto_signal_task
            except asyncio.CancelledError:
                pass
            print("🛑 ENHANCED AUTO SIGNAL: Background detection stopped")

    async def _auto_signal_background_loop(self):
        """Enhanced background loop for signal detection"""
        print("🔄 ENHANCED AUTO SIGNAL: Background loop started")

        while True:
            try:
                await self._scan_for_enhanced_signals()
                await asyncio.sleep(self.scan_interval)
            except asyncio.CancelledError:
                print("🛑 ENHANCED AUTO SIGNAL: Background loop cancelled")
                break
            except Exception as e:
                print(f"❌ ENHANCED AUTO SIGNAL: Error in background loop: {e}")
                await asyncio.sleep(60)

    async def _scan_for_enhanced_signals(self):
        """Scan symbols for enhanced signals with confidence ≥ 75%"""
        try:
            current_time = time.time()
            print(f"🔍 ENHANCED AUTO SIGNAL: Scanning at {datetime.now().strftime('%H:%M:%S')}")

            valid_signals = []

            for symbol in self.target_symbols:
                try:
                    # Generate enhanced signal
                    signal = self.generate_enhanced_signal(symbol)

                    if signal and signal.get('confidence', 0) >= self.confidence_threshold:
                        # Check for duplicate prevention
                        signal_key = f"{symbol}_{signal['direction']}_{signal['confidence']:.0f}"
                        if signal_key not in self.last_sent_signals:
                            valid_signals.append(signal)
                            self.last_sent_signals[signal_key] = current_time
                            print(f"✅ ENHANCED SIGNAL: {symbol} - {signal['direction']} (Confidence: {signal['confidence']:.1f}%)")

                    # Rate limiting
                    await asyncio.sleep(1)

                except Exception as e:
                    print(f"❌ ENHANCED AUTO SIGNAL: Error analyzing {symbol}: {e}")
                    continue

            # Clean old duplicate entries (older than 2 hours)
            cutoff_time = current_time - (2 * 3600)
            self.last_sent_signals = {k: v for k, v in self.last_sent_signals.items() if v > cutoff_time}

            if valid_signals:
                print(f"🚀 ENHANCED AUTO SIGNAL: Found {len(valid_signals)} signals with confidence ≥ 75%")
                await self._send_enhanced_auto_signals(valid_signals)
            else:
                print("📊 ENHANCED AUTO SIGNAL: No signals meet confidence threshold")

        except Exception as e:
            print(f"❌ ENHANCED AUTO SIGNAL: Error in scan: {e}")

    async def _send_enhanced_auto_signals(self, signals):
        """Send enhanced auto signals to eligible users"""
        if not self.bot_instance:
            print("❌ ENHANCED AUTO SIGNAL: Bot instance not available")
            return

        try:
            # Get eligible users
            from supabase_users import SupabaseUsers
            supabase_users = SupabaseUsers()
            eligible_users = supabase_users.get_eligible_auto_signal_users()

            if not eligible_users and hasattr(self.bot_instance, 'db'):
                eligible_users = self.bot_instance.db.get_eligible_auto_signal_users()

            if not eligible_users:
                print("❌ ENHANCED AUTO SIGNAL: No eligible users found")
                return

            # Format enhanced auto signal message
            message = self._format_enhanced_auto_signal_message(signals)

            # Send to eligible users
            success_count = 0
            for user in eligible_users:
                try:
                    user_id = user['telegram_id']
                    await self.bot_instance.application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=None
                    )
                    success_count += 1
                    print(f"✅ ENHANCED AUTO SIGNAL: Sent to {user['first_name']} ({user['type']})")
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"❌ ENHANCED AUTO SIGNAL: Failed to send to user {user.get('telegram_id', 'unknown')}: {e}")

            print(f"🚀 ENHANCED AUTO SIGNAL: Successfully sent to {success_count}/{len(eligible_users)} users")

        except Exception as e:
            print(f"❌ ENHANCED AUTO SIGNAL: Error sending signals: {e}")

    def _format_enhanced_auto_signal_message(self, signals):
        """Format enhanced auto signals with detailed analysis"""
        current_time = datetime.now().strftime('%H:%M:%S WIB')

        message = f"""🚀 AUTO SIGNAL - ENHANCED ANALYSIS

🕐 Detection Time: {current_time}
📊 High-Quality Signals: {len(signals)} (Confidence ≥ 75%)
⚡ Analysis: Multi-timeframe + Global Macro + CoinAPI + CMC

"""

        for i, signal in enumerate(signals[:3], 1):  # Limit to top 3 signals
            direction_emoji = "🟢" if signal['direction'] == 'BUY' else "🔴"

            message += f"""**{i}. {signal['symbol']} {direction_emoji} {signal['direction']}**
🔥 **Confidence**: {signal['confidence']:.1f}% ({signal['technical_score']}+{signal['macro_score']})
💰 **Entry**: ${self._format_price(signal['entry_price'])}
🛑 **Stop Loss**: ${self._format_price(signal['stop_loss'])}
🎯 **TP1**: ${self._format_price(signal['tp1'])} | **TP2**: ${self._format_price(signal['tp2'])}
📊 **EMA50**: {self._format_price(signal['ema50'])} | **EMA200**: {self._format_price(signal['ema200'])}
📈 **RSI**: {signal['rsi']:.1f} | **MACD**: {signal['macd']:.4f}
🌍 **Market**: MC {signal['market_cap_change']:+.1f}% | Vol {signal['volume_change']:+.1f}%
✅ **Timeframe**: {signal['timeframe_confirmation']}

"""

        message += f"""⚠️ **ENHANCED RISK MANAGEMENT**:
• Multi-timeframe confirmation (5m & 1H selaras)
• Global macro filtering aktif
• Confidence score minimum 75%
• Cooldown 1 jam per coin untuk kualitas
• WAJIB gunakan Stop Loss
• Take profit bertahap untuk maksimalkan profit

🤖 **ADVANCED FEATURES**:
• ✅ CoinAPI multi-timeframe OHLCV analysis
• ✅ CoinMarketCap global market filtering
• ✅ Technical + Macro confidence scoring
• ✅ Anti-spam & duplicate prevention
• ✅ Professional-grade signal quality

📡 **Data Sources**: 
• Technical: CoinAPI Multi-timeframe OHLCV
• Macro: CoinMarketCap Global Metrics
• Quality: Professional Trading Algorithms

🔄 **Update**: {current_time} WIB
💎 **Exclusive for Admin & Lifetime Users**"""

        return message

    # ============ HELPER METHODS ============

    def _format_price(self, price):
        """Format price display"""
        if price < 1:
            return f"{price:.6f}"
        elif price < 100:
            return f"{price:.4f}"
        else:
            return f"{price:,.2f}"

    def _calculate_ema(self, prices, period):
        """Calculate EMA manually if no library available"""
        alpha = 2 / (period + 1)
        ema = np.zeros_like(prices)
        ema[0] = prices[0]

        for i in range(1, len(prices)):
            ema[i] = alpha * prices[i] + (1 - alpha) * ema[i-1]

        return ema

    def _calculate_sma(self, prices, period):
        """Calculate SMA manually"""
        sma = np.zeros_like(prices)
        for i in range(period-1, len(prices)):
            sma[i] = np.mean(prices[i-period+1:i+1])
        return sma

    def _calculate_rsi(self, prices, period):
        """Calculate RSI manually"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gains = np.zeros_like(prices)
        avg_losses = np.zeros_like(prices)

        # Initial averages
        avg_gains[period] = np.mean(gains[:period])
        avg_losses[period] = np.mean(losses[:period])

        # Calculate RSI
        for i in range(period + 1, len(prices)):
            avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i-1]) / period
            avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i-1]) / period

        rs = avg_gains / np.maximum(avg_losses, 1e-10)
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_atr(self, highs, lows, closes, period):
        """Calculate ATR manually"""
        tr = np.maximum(highs - lows,
                       np.maximum(np.abs(highs - np.roll(closes, 1)),
                                 np.abs(lows - np.roll(closes, 1))))
        tr[0] = highs[0] - lows[0]  # First TR

        atr = np.zeros_like(tr)
        atr[period-1] = np.mean(tr[:period])

        for i in range(period, len(tr)):
            atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period

        return atr

    def _calculate_macd(self, prices):
        """Calculate MACD manually"""
        ema12 = self._calculate_ema(prices, 12)
        ema26 = self._calculate_ema(prices, 26)
        return ema12 - ema26

    def _calculate_macd_histogram(self, prices):
        """Calculate MACD histogram manually"""
        macd = self._calculate_macd(prices)
        signal = self._calculate_ema(macd, 9)
        return macd - signal

    # ============ COMPATIBILITY METHODS ============

    def get_comprehensive_analysis(self, symbol, futures_data=None, market_data=None, language='id', user_id=None):
        """Enhanced comprehensive analysis with CoinAPI + CMC integration"""
        try:
            if user_id:
                self.save_user(user_id)

            current_time = datetime.now().strftime('%H:%M:%S WIB')

            # Perform multi-timeframe analysis
            analysis = self.multi_timeframe_analysis(symbol)

            if 'error' in analysis:
                return f"❌ **ANALISIS ERROR**: {analysis['error']}"

            # Get data from analysis
            tech_1h = analysis.get('technical_1h', {})
            global_metrics = analysis.get('global_metrics', {})
            confidence = analysis.get('confidence_score', {})

            current_price = tech_1h.get('current_price', 0) if tech_1h else 0
            
            # Generate trading recommendation
            total_confidence = confidence.get('total_score', 0)
            if total_confidence >= 75:
                recommendation_level = "STRONG"
                rec_emoji = "🔥"
            elif total_confidence >= 60:
                recommendation_level = "MODERATE"  
                rec_emoji = "⭐"
            else:
                recommendation_level = "WEAK"
                rec_emoji = "💡"

            trend = tech_1h.get('trend', 'sideways') if tech_1h else 'sideways'
            if trend == 'bullish':
                recommendation = f"{recommendation_level} BUY/LONG"
                trend_emoji = "📈"
            else:
                recommendation = f"{recommendation_level} SELL/SHORT"
                trend_emoji = "📉"

            analysis_text = f"""🎯 **ANALISIS KOMPREHENSIF {symbol.upper()}**

💰 **1. HARGA REAL-TIME (CoinAPI)**
• **Current Price**: ${self._format_price(current_price)}
• **Source**: Multi-exchange aggregated data

📊 **2. TECHNICAL ANALYSIS (Multi-Timeframe)**"""

            if tech_1h and tech_1h.get('success'):
                analysis_text += f"""
• **EMA50**: ${self._format_price(tech_1h.get('ema50', 0))}
• **EMA200**: ${self._format_price(tech_1h.get('ema200', 0))}
• **RSI**: {tech_1h.get('rsi', 0):.1f}
• **MACD**: {tech_1h.get('macd', 0):.4f}
• **MACD Histogram**: {tech_1h.get('macd_histogram', 0):.4f}
• **ATR**: {tech_1h.get('atr', 0):.4f}
• **Volume Oscillator**: {tech_1h.get('volume_oscillator', 0):.1f}%
• **Trend**: {trend_emoji} {trend.upper()}"""
            else:
                analysis_text += f"""
• ⚠️ Technical data unavailable
• Reason: Insufficient OHLCV data"""

            analysis_text += f"""

🌍 **3. GLOBAL MARKET METRICS (CoinMarketCap)**"""

            if 'error' not in global_metrics:
                analysis_text += f"""
• **Market Cap Change 24h**: {global_metrics.get('market_cap_change_24h', 0):+.2f}%
• **Volume Change 24h**: {global_metrics.get('volume_change_24h', 0):+.2f}%
• **BTC Dominance**: {global_metrics.get('btc_dominance', 0):.1f}%
• **Total Market Cap**: ${global_metrics.get('total_market_cap', 0)/1e12:.2f}T"""
            else:
                analysis_text += f"""
• ⚠️ Global metrics unavailable
• Reason: {global_metrics.get('error', 'API limit or connection issue')}"""

            analysis_text += f"""

🎯 **4. CONFIDENCE SCORE ANALYSIS**
• **Technical Score**: {confidence.get('technical_score', 0)}/50
• **Macro Score**: {confidence.get('macro_score', 0)}/50
• **Total Confidence**: {total_confidence:.1f}/100
• **Quality Rating**: {'🔥 EXCELLENT' if total_confidence >= 75 else '⭐ GOOD' if total_confidence >= 60 else '💡 FAIR'}

📌 **5. KESIMPULAN & REKOMENDASI**
• **Rekomendasi**: {rec_emoji} **{recommendation}**
• **Confidence Level**: {total_confidence:.1f}%
• **Risk Assessment**: {'Low' if total_confidence >= 75 else 'Medium' if total_confidence >= 60 else 'High'}

⚠️ **RISK MANAGEMENT**:
• Gunakan position sizing yang tepat
• WAJIB pasang stop loss
• Monitor global market conditions
• Confidence minimum 75% untuk high-conviction trades

🕐 **Analysis Time**: {current_time} WIB
📡 **Data Sources**: CoinAPI + CoinMarketCap Professional
⭐️ **Enhanced Multi-Timeframe Analysis**"""

            return analysis_text

        except Exception as e:
            return f"❌ **ENHANCED ANALYSIS ERROR**: {str(e)[:100]}"

    def get_ai_response(self, text, language='id', user_id=None):
        """Enhanced AI response for crypto questions"""
        # Save user if provided
        if user_id:
            self.save_user(user_id)

        text_lower = text.lower()

        if language == 'id':
            if any(keyword in text_lower for keyword in ['apa itu bitcoin', 'bitcoin itu apa']):
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

💎 **Enhanced CryptoMentor**: Gunakan `/analyze btc` untuk analisis mendalam dengan data CoinAPI + CoinMarketCap!"""

            elif any(keyword in text_lower for keyword in ['harga', 'price', 'berapa']):
                return """💰 **Cek Harga Crypto Real-time**

🔥 **Commands tersedia:**
• `/price <symbol>` - Harga real-time dari CoinAPI
• `/analyze <symbol>` - Analisis mendalam + confidence score
• `/futures_signals` - Sinyal trading profesional

💎 **Enhanced Features:**
• Multi-timeframe analysis (5m, 1H, 4H)
• Global market macro filtering
• Confidence scoring system
• Professional trading signals

🚀 **Contoh**: `/price btc` atau `/analyze eth`"""

            elif any(keyword in text_lower for keyword in ['analisis', 'analyze', 'sinyal', 'signal']):
                return """📊 **Enhanced Analysis & Signals**

🔥 **Professional Commands:**
• `/analyze <symbol>` - Multi-timeframe analysis + confidence score
• `/futures <symbol>` - Enhanced futures analysis per coin
• `/futures_signals` - Professional trading signals (confidence ≥ 75%)

💎 **Enhanced Features:**
• CoinAPI multi-timeframe OHLCV data
• CoinMarketCap global macro filtering
• Advanced confidence scoring (technical + macro)
• Auto-signal system untuk lifetime users

🎯 **Contoh**: `/futures btc` atau `/futures_signals`"""

            elif any(keyword in text_lower for keyword in ['help', 'bantuan', 'command']):
                return self.help_message()

            elif any(keyword in text_lower for keyword in ['terima kasih', 'thanks', 'thx']):
                return """🙏 **Terima kasih sudah menggunakan CryptoMentor AI Enhanced!**

🚀 **Yang baru di versi Enhanced:**
• Multi-timeframe analysis (5m, 1H, 4H)
• CoinAPI + CoinMarketCap integration
• Advanced confidence scoring
• Professional auto-signal system

💎 Jangan ragu bertanya atau gunakan commands profesional kami!"""

            else:
                return f"""🤖 **CryptoMentor AI Enhanced**

Saya memahami Anda bertanya tentang: "{text}"

🚀 **Enhanced Capabilities:**
• Multi-timeframe technical analysis
• Global macro market filtering
• Professional confidence scoring
• Real-time CoinAPI + CMC data

📚 **Yang bisa saya bantu:**
- Enhanced price analysis (`/analyze btc`)
- Professional futures signals (`/futures_signals`)
- Global market sentiment (`/market`)
- Multi-timeframe confirmations

💡 **Tip**: Gunakan commands enhanced kami untuk analisis profesional!"""

        else:
            return """🤖 **CryptoMentor AI Enhanced - Professional Crypto Analysis**

I'm your enhanced crypto analysis assistant with professional-grade features!

🚀 **Enhanced Features:**
- Multi-timeframe technical analysis (5m, 1H, 4H)
- CoinAPI + CoinMarketCap data integration
- Advanced confidence scoring system
- Professional auto-signal system

📚 **Professional Services:**
- Real-time price analysis with confidence scores
- Enhanced futures signals (≥75% confidence)
- Global market macro filtering
- Multi-timeframe confirmation system

💡 **Available commands:**
- `/analyze <symbol>` - Enhanced multi-timeframe analysis
- `/futures_signals` - Professional trading signals
- `/market` - Global market sentiment
- `/help` - See all enhanced commands

Ask me anything about crypto with our professional analysis tools! 🚀"""
