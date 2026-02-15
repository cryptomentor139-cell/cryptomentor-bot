import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
import requests
import logging

class DeepSeekAI:
    """CryptoMentor AI Assistant untuk analisis market dan chat santai"""

    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://openrouter.ai/api/v1')
        
        # Use StepFun Step 3.5 Flash - FREE & FAST model for reasoning & crypto news
        # Options:
        # - "stepfun/step-3.5-flash" = FREE, CEPAT (2-5 detik), bagus untuk reasoning & berita
        # - "openai/gpt-3.5-turbo" = Berbayar, reliable (3-5s)
        # - "deepseek/deepseek-chat" = Lambat tapi reasoning detail (10-15s)
        self.model = os.getenv('AI_MODEL', 'stepfun/step-3.5-flash')  # Default to FREE model
        
        self.available = bool(self.api_key)
        self.provider = 'openrouter'
        
        if self.available:
            print(f"✅ CryptoMentor AI initialized (Provider: OpenRouter, Model: {self.model})")
        else:
            print("⚠️ DEEPSEEK_API_KEY not found in environment")

    async def analyze_market_with_reasoning(
        self, 
        symbol: str, 
        market_data: Dict[str, Any],
        indicators: Optional[Dict] = None,
        language: str = 'id'
    ) -> str:
        """
        Analisis market dengan reasoning mendalam menggunakan CryptoMentor AI
        
        Args:
            symbol: Symbol crypto (e.g., 'BTC', 'ETH')
            market_data: Data market dari Binance (price, volume, change, dll)
            indicators: Technical indicators (RSI, MACD, dll)
            language: Bahasa response ('id' atau 'en')
        """
        if not self.available:
            return "❌ CryptoMentor AI tidak tersedia. Pastikan API key sudah dikonfigurasi."

        try:
            # Prepare context untuk DeepSeek
            current_price = market_data.get('price', 0)
            change_24h = market_data.get('change_24h', 0)
            volume_24h = market_data.get('volume_24h', 0)
            
            # Format data untuk AI
            market_context = f"""
Analisis Market untuk {symbol}:

Data Real-time:
- Harga Saat Ini: ${current_price:,.2f}
- Perubahan 24j: {change_24h:+.2f}%
- Volume 24j: ${volume_24h:,.0f}

"""
            
            if indicators:
                market_context += f"""
Technical Indicators:
{json.dumps(indicators, indent=2)}
"""

            # Prompt untuk CryptoMentor AI
            system_prompt = """Kamu adalah CryptoMentor AI, expert crypto analyst dengan pengalaman 10+ tahun di trading cryptocurrency. 
Tugasmu adalah memberikan analisis market yang mendalam dengan reasoning yang jelas dan mudah dipahami.

Berikan analisis yang mencakup:
1. Kondisi market saat ini (bullish/bearish/sideways)
2. Reasoning di balik kondisi tersebut
3. Level support dan resistance penting
4. Potensi pergerakan harga ke depan
5. Risk dan opportunity yang ada
6. Rekomendasi trading yang actionable

Gunakan bahasa yang santai tapi profesional. Jelaskan dengan detail tapi tetap mudah dipahami."""

            if language == 'en':
                system_prompt = """You are CryptoMentor AI, an expert crypto analyst with 10+ years of experience in cryptocurrency trading.
Your task is to provide in-depth market analysis with clear and easy-to-understand reasoning.

Provide analysis that includes:
1. Current market condition (bullish/bearish/sideways)
2. Reasoning behind the condition
3. Important support and resistance levels
4. Potential price movements ahead
5. Risks and opportunities
6. Actionable trading recommendations

Use casual but professional language. Explain in detail but keep it easy to understand."""

            user_prompt = f"{market_context}\n\nBerikan analisis mendalam dengan reasoning yang jelas untuk kondisi market {symbol} saat ini."
            
            if language == 'en':
                user_prompt = f"{market_context}\n\nProvide in-depth analysis with clear reasoning for the current {symbol} market condition."

            # Call CryptoMentor AI
            response = await self._call_deepseek_api(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )

            if response:
                # Format response dengan header
                header = f"""🤖 **CRYPTOMENTOR AI ANALYSIS - {symbol}**
📊 **Market Data**: ${current_price:,.2f} ({change_24h:+.2f}%)
🕐 **Analysis Time**: {datetime.now().strftime('%H:%M:%S WIB')}

---

"""
                return header + response
            else:
                return "❌ Gagal mendapatkan analisis dari CryptoMentor AI"

        except Exception as e:
            print(f"Error in CryptoMentor AI market analysis: {e}")
            return f"❌ Error: {str(e)}"
        async def analyze_market_simple(
            self,
            symbol: str,
            market_data: Dict[str, Any],
            language: str = 'id'
        ) -> str:
            """
            Analisis market sederhana tanpa memerlukan OHLCV data
            Hanya menggunakan data dasar: price, change_24h, volume_24h

            Args:
                symbol: Symbol crypto (e.g., 'BTC', 'ETH')
                market_data: Data market dasar dari crypto_api.get_crypto_price()
                language: Bahasa response ('id' atau 'en')
            """
            if not self.available:
                return "❌ CryptoMentor AI tidak tersedia. Pastikan API key sudah dikonfigurasi."

            try:
                # Extract basic market data
                current_price = market_data.get('price', 0)
                change_24h = market_data.get('change_24h', 0)
                volume_24h = market_data.get('volume_24h', 0)
                high_24h = market_data.get('high_24h', current_price)
                low_24h = market_data.get('low_24h', current_price)

                # Calculate additional metrics
                price_range_24h = ((high_24h - low_24h) / low_24h * 100) if low_24h > 0 else 0
                current_position = ((current_price - low_24h) / (high_24h - low_24h) * 100) if (high_24h - low_24h) > 0 else 50

                # Determine market condition
                if change_24h > 5:
                    condition = "BULLISH KUAT 🚀"
                elif change_24h > 2:
                    condition = "BULLISH 📈"
                elif change_24h > -2:
                    condition = "SIDEWAYS ↔️"
                elif change_24h > -5:
                    condition = "BEARISH 📉"
                else:
                    condition = "BEARISH KUAT 🔻"

                # Format market context untuk AI
                market_context = f"""
    Analisis Market untuk {symbol}:

    📊 Data Real-time:
    - Harga Saat Ini: ${current_price:,.2f}
    - Perubahan 24j: {change_24h:+.2f}%
    - Volume 24j: ${volume_24h:,.0f}
    - High 24j: ${high_24h:,.2f}
    - Low 24j: ${low_24h:,.2f}
    - Range 24j: {price_range_24h:.2f}%
    - Posisi dalam Range: {current_position:.1f}%

    📈 Kondisi Market: {condition}
    """

                # Prompt untuk CryptoMentor AI
                system_prompt = """Kamu adalah CryptoMentor AI, expert crypto analyst dengan pengalaman 10+ tahun di trading cryptocurrency.
    Tugasmu adalah memberikan analisis market yang mendalam dengan reasoning yang jelas dan mudah dipahami.

    Berikan analisis yang mencakup:
    1. Kondisi market saat ini dan interpretasinya
    2. Reasoning di balik pergerakan harga 24 jam terakhir
    3. Analisis volume dan volatilitas
    4. Potensi pergerakan harga ke depan (short-term)
    5. Level-level penting yang perlu diperhatikan
    6. Risk dan opportunity yang ada
    7. Rekomendasi trading yang actionable dengan risk management

    Gunakan bahasa yang santai tapi profesional. Jelaskan dengan detail tapi tetap mudah dipahami.
    Jangan lupa selalu ingatkan tentang risk management dan bahwa trading itu berisiko."""

                if language == 'en':
                    system_prompt = """You are CryptoMentor AI, an expert crypto analyst with 10+ years of experience in cryptocurrency trading.
    Your task is to provide in-depth market analysis with clear and easy-to-understand reasoning.

    Provide analysis that includes:
    1. Current market condition and its interpretation
    2. Reasoning behind the 24-hour price movement
    3. Volume and volatility analysis
    4. Potential short-term price movements
    5. Important levels to watch
    6. Risks and opportunities
    7. Actionable trading recommendations with risk management

    Use casual but professional language. Explain in detail but keep it easy to understand.
    Always remind about risk management and that trading is risky."""

                user_prompt = f"{market_context}\n\nBerikan analisis mendalam dengan reasoning yang jelas untuk kondisi market {symbol} saat ini."

                if language == 'en':
                    user_prompt = f"{market_context}\n\nProvide in-depth analysis with clear reasoning for the current {symbol} market condition."

                # Call CryptoMentor AI
                response = await self._call_deepseek_api(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt
                )

                if response:
                    # Format response dengan header (rebranded)
                    header = f"""🤖 **CRYPTOMENTOR AI ANALYSIS - {symbol}**
    📊 **Market Data**: ${current_price:,.2f} ({change_24h:+.2f}%)
    🕐 **Analysis Time**: {datetime.now().strftime('%H:%M:%S WIB')}

    ---

    """
                    return header + response
                else:
                    return "❌ Gagal mendapatkan analisis dari CryptoMentor AI"

            except Exception as e:
                print(f"Error in CryptoMentor AI market analysis: {e}")
                return f"❌ Error: {str(e)}"


    async def analyze_market_simple(
        self, 
        symbol: str, 
        market_data: Dict[str, Any],
        language: str = 'id',
        include_advanced_data: bool = True
    ) -> str:
        """
        Analisis market sederhana tanpa memerlukan OHLCV data
        Hanya menggunakan data dasar: price, change_24h, volume_24h
        
        Args:
            symbol: Symbol crypto (e.g., 'BTC', 'ETH')
            market_data: Data market dasar dari crypto_api.get_crypto_price()
            language: Bahasa response ('id' atau 'en')
        """
        if not self.available:
            return "❌ CryptoMentor AI tidak tersedia. Pastikan API key sudah dikonfigurasi."

        try:
            # Extract basic market data
            current_price = market_data.get('price', 0)
            change_24h = market_data.get('change_24h', 0)
            volume_24h = market_data.get('volume_24h', 0)
            high_24h = market_data.get('high_24h', current_price)
            low_24h = market_data.get('low_24h', current_price)
            
            # Calculate additional metrics
            price_range_24h = ((high_24h - low_24h) / low_24h * 100) if low_24h > 0 else 0
            current_position = ((current_price - low_24h) / (high_24h - low_24h) * 100) if (high_24h - low_24h) > 0 else 50
            
            # Determine market condition
            if change_24h > 5:
                condition = "BULLISH KUAT 🚀"
            elif change_24h > 2:
                condition = "BULLISH 📈"
            elif change_24h > -2:
                condition = "SIDEWAYS ↔️"
            elif change_24h > -5:
                condition = "BEARISH 📉"
            else:
                condition = "BEARISH KUAT 🔻"
            
            # Format market context untuk AI
            market_context = f"""
Analisis Market untuk {symbol}:

📊 Data Real-time:
- Harga Saat Ini: ${current_price:,.2f}
- Perubahan 24j: {change_24h:+.2f}%
- Volume 24j: ${volume_24h:,.0f}
- High 24j: ${high_24h:,.2f}
- Low 24j: ${low_24h:,.2f}
- Range 24j: {price_range_24h:.2f}%
- Posisi dalam Range: {current_position:.1f}%

📈 Kondisi Market: {condition}
"""
            
            # Add advanced data if available
            advanced_context = ""
            if include_advanced_data:
                try:
                    from app.providers.advanced_data_provider import advanced_data_provider
                    enhanced_data = await advanced_data_provider.get_enhanced_market_context(symbol)
                    advanced_context = advanced_data_provider.format_enhanced_context(enhanced_data)
                except Exception as e:
                    print(f"Error getting advanced data: {e}")
            
            market_context += advanced_context
            
            # Prompt untuk CryptoMentor AI (OPTIMIZED for speed)
            system_prompt = """Kamu adalah CryptoMentor AI, expert crypto analyst.
Berikan analisis SINGKAT dan PADAT (maksimal 400 kata) yang mencakup:
1. Kondisi market saat ini (1-2 kalimat)
2. Reasoning utama (2-3 poin)
3. Level penting (support/resistance)
4. Rekomendasi trading (singkat)
5. Risk warning (1 kalimat)

Gunakan bahasa yang jelas dan to-the-point. Fokus pada insight yang actionable."""

            if language == 'en':
                system_prompt = """You are CryptoMentor AI, expert crypto analyst.
Provide BRIEF and CONCISE analysis (max 400 words) covering:
1. Current market condition (1-2 sentences)
2. Main reasoning (2-3 points)
3. Key levels (support/resistance)
4. Trading recommendation (brief)
5. Risk warning (1 sentence)

Use clear and to-the-point language. Focus on actionable insights."""

            user_prompt = f"{market_context}\n\nBerikan analisis SINGKAT dan PADAT untuk {symbol}. Fokus pada insight yang paling penting."
            
            if language == 'en':
                user_prompt = f"{market_context}\n\nProvide in-depth analysis with clear reasoning for the current {symbol} market condition."

            # Call CryptoMentor AI
            response = await self._call_deepseek_api(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )

            if response:
                # Format response dengan header (rebranded)
                header = f"""🤖 **CRYPTOMENTOR AI ANALYSIS - {symbol}**
📊 **Market Data**: ${current_price:,.2f} ({change_24h:+.2f}%)
🕐 **Analysis Time**: {datetime.now().strftime('%H:%M:%S WIB')}

---

"""
                return header + response
            else:
                return "❌ Gagal mendapatkan analisis dari CryptoMentor AI"

        except Exception as e:
            print(f"Error in CryptoMentor AI market analysis: {e}")
            return f"❌ Error: {str(e)}"

    async def chat_about_market(
        self, 
        user_message: str,
        context: Optional[Dict] = None,
        language: str = 'id'
    ) -> str:
        """
        Chat santai dengan user tentang market
        
        Args:
            user_message: Pesan dari user
            context: Context tambahan (market data, history, dll)
            language: Bahasa response
        """
        if not self.available:
            return "❌ CryptoMentor AI tidak tersedia. Pastikan API key sudah dikonfigurasi."

        try:
            # System prompt untuk chat mode
            system_prompt = """Kamu adalah CryptoMentor AI, assistant yang friendly dan knowledgeable tentang cryptocurrency.
Kamu bisa ngobrol santai dengan user tentang market, trading, dan crypto secara umum.

Karaktermu:
- Santai tapi tetap informatif
- Bisa kasih insight yang valuable
- Tidak terlalu formal
- Bisa pakai emoji untuk ekspresif
- Jujur kalau tidak tahu sesuatu
- Selalu ingatkan tentang risk management

Kamu bisa diskusi tentang:
- Analisis market dan price action
- Trading strategy dan tips
- News dan trend crypto
- Technical analysis
- Risk management
- Dan topik crypto lainnya

Jangan memberikan financial advice yang pasti, selalu ingatkan bahwa trading itu berisiko."""

            if language == 'en':
                system_prompt = """You are a friendly and knowledgeable AI assistant about cryptocurrency.
You can chat casually with users about markets, trading, and crypto in general.

Your characteristics:
- Casual but informative
- Can provide valuable insights
- Not too formal
- Can use emojis to be expressive
- Honest when you don't know something
- Always remind about risk management

You can discuss:
- Market analysis and price action
- Trading strategies and tips
- Crypto news and trends
- Technical analysis
- Risk management
- And other crypto topics

Don't give definite financial advice, always remind that trading is risky."""

            # Add context if available
            context_text = ""
            if context:
                context_text = f"\n\nContext:\n{json.dumps(context, indent=2)}\n"

            full_prompt = f"{context_text}\nUser: {user_message}"

            # Call DeepSeek API
            response = await self._call_deepseek_api(
                system_prompt=system_prompt,
                user_prompt=full_prompt
            )

            if response:
                return f"🤖 **CryptoMentor AI**:\n\n{response}"
            else:
                return "❌ Gagal mendapatkan response dari CryptoMentor AI"

        except Exception as e:
            print(f"Error in CryptoMentor AI chat: {e}")
            return f"❌ Error: {str(e)}"

    async def _call_deepseek_api(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: float = 0.5,
        max_tokens: int = 600  # Reduced from 1000 to 600 for faster response
    ) -> Optional[str]:
        """Call DeepSeek API via OpenRouter with ULTRA AGGRESSIVE timeout"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/yourusername/crypto-bot",
                "X-Title": "Crypto Analysis Bot"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            # Use asyncio to run requests in executor with ULTRA AGGRESSIVE timeout
            loop = asyncio.get_event_loop()
            
            # Set timeout to 8 seconds max for API call (reduced from 15s)
            try:
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: requests.post(
                            f"{self.base_url}/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=8  # 8 second HTTP timeout (reduced from 15s)
                        )
                    ),
                    timeout=10  # 10 second overall timeout (reduced from 20s)
                )
            except asyncio.TimeoutError:
                print(f"⚠️ OpenRouter API timeout after 10 seconds")
                return "⚠️ AI response timeout. Signal tetap valid tanpa AI reasoning."

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None

        except asyncio.TimeoutError:
            print(f"⚠️ API call timeout")
            return "⚠️ AI response timeout. Signal tetap valid tanpa AI reasoning."
        except Exception as e:
            print(f"Error calling DeepSeek API: {e}")
            return None

    def get_market_summary_prompt(self, market_data: List[Dict]) -> str:
        """Generate prompt untuk market summary"""
        summary = "Market Overview:\n\n"
        
        for coin in market_data[:10]:  # Top 10 coins
            symbol = coin.get('symbol', 'N/A')
            price = coin.get('price', 0)
            change = coin.get('change_24h', 0)
            volume = coin.get('volume_24h', 0)
            
            summary += f"- {symbol}: ${price:,.2f} ({change:+.2f}%) Vol: ${volume:,.0f}\n"
        
        return summary

    async def generate_spot_signal_reasoning(self, symbol: str, signal_data: dict) -> str:
        """Generate AI reasoning for spot trading signal - ULTRA FAST"""
        if not self.available:
            return ""
        
        try:
            # ULTRA MINIMAL context - only essentials
            context = f"""Spot {symbol}: ${signal_data['current_price']:,.2f}
Trend: {signal_data['trend']} | Confidence: {signal_data['confidence']:.0f}%
Buy Zones: {len(signal_data.get('buy_zones', []))} zones detected"""
            
            # ULTRA SHORT prompt for speed
            system_prompt = """Expert crypto analyst. Berikan reasoning SANGAT SINGKAT (max 100 kata):
1. Kenapa setup ini bagus?
2. Cara eksekusi DCA
3. Risk management

Padat, jelas, actionable."""

            user_prompt = f"{context}\n\nReasoning singkat untuk spot signal ini."
            
            # DRASTICALLY reduced tokens for SPEED
            reasoning = await self._call_deepseek_api(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.5,
                max_tokens=150  # Reduced from 400 to 150 for SPEED
            )
            
            if reasoning:
                return f"\n\n🤖 <b>AI INSIGHT</b>:\n{reasoning}"
            else:
                return ""
                
        except Exception as e:
            print(f"Error generating spot signal reasoning: {e}")
            return ""
