# -*- coding: utf-8 -*-
import requests
import random
import os
import asyncio
import time
from datetime import datetime

class AIAssistant:
    def __init__(self, name="CryptoMentor AI"):
        self.name = name

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

🚀 **Semua analisis menggunakan data real-time dari multiple API!**"""

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

            elif any(keyword in text_lower for keyword in ['apa itu crypto', 'cryptocurrency itu apa', 'kripto itu apa']):
                return """🌐 **Apa itu Cryptocurrency?**

Cryptocurrency adalah mata uang digital yang menggunakan kriptografi untuk keamanan dan beroperasi pada teknologi blockchain.

🔧 **Komponen Utama:**
- **Blockchain**: Database terdistribusi yang mencatat semua transaksi
- **Mining**: Proses validasi transaksi dan pembuatan blok baru
- **Wallet**: Tempat menyimpan cryptocurrency Anda dengan aman
- **Private Key**: Kunci rahasia untuk mengakses wallet
- **Public Key**: Alamat wallet untuk menerima crypto

💰 **Contoh Cryptocurrency Populer:**
- **Bitcoin (BTC)**: Cryptocurrency pertama dan terbesar
- **Ethereum (ETH)**: Platform smart contract
- **Binance Coin (BNB)**: Token exchange Binance
- **Solana (SOL)**: Blockchain cepat dan murah
- **Polygon (MATIC)**: Layer 2 untuk Ethereum

🌟 **Keuntungan Crypto:**
- Transaksi 24/7 tanpa bank
- Biaya transfer lebih murah
- Tidak ada batasan geografis
- Transparansi tinggi
- Potensi return investasi tinggi

⚠️ **Risiko Crypto:**
- Volatilitas tinggi (harga naik-turun drastis)
- Belum ada regulasi jelas
- Risiko kehilangan private key
- Scam dan fraud

💡 **Tips untuk Pemula:**
- Mulai dengan amount kecil
- Pelajari dasar-dasar dulu
- Gunakan exchange terpercaya
- Simpan di wallet sendiri (bukan di exchange)
- Jangan invest lebih dari yang bisa rugi

Gunakan `/price <symbol>` untuk cek harga crypto!"""

            elif any(keyword in text_lower for keyword in ['harga', 'price', 'berapa']):
                return "💰 Untuk cek harga crypto, gunakan command `/price <symbol>`.\nContoh: `/price btc`\n\nUntuk analisis lengkap dengan prediksi: `/analyze <symbol>`"

            elif any(keyword in text_lower for keyword in ['analisis', 'analyze', 'sinyal']):
                return "📊 Untuk analisis mendalam, gunakan `/analyze <symbol>` atau `/futures_signals` untuk sinyal futures harian.\n\n💡 **Tips**: Analisis mencakup technical analysis, sentiment, dan rekomendasi trading."

            elif any(keyword in text_lower for keyword in ['market', 'pasar', 'overview']):
                return "📈 Gunakan command `/market` untuk melihat overview pasar crypto secara keseluruhan.\n\nIngin tau tentang market cap, dominasi BTC, atau trend pasar?"

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
            if any(keyword in text_lower for keyword in ['what is bitcoin', 'explain bitcoin', 'bitcoin basics']):
                return """🪙 **What is Bitcoin?**

Bitcoin (BTC) is the world's first and largest cryptocurrency, created by Satoshi Nakamoto in 2009.

🔑 **Key Characteristics:**
- **Digital Currency**: Not controlled by any bank or government
- **Blockchain**: Secure distributed ledger technology
- **Limited Supply**: Only 21 million BTC will ever exist
- **Decentralized**: No central authority controls it

💡 **Bitcoin Use Cases:**
- Store of value (digital gold)
- Medium of exchange
- Hedge against inflation
- Investment asset

📈 **For beginners**: Start by learning about wallets, private keys, and how to buy BTC on legitimate exchanges.

Use `/price btc` to check current price!"""

            elif any(keyword in text_lower for keyword in ['price', 'cost', 'how much']):
                return "💰 To check crypto prices, use `/price <symbol>`. Example: `/price btc`\n\nFor comprehensive analysis: `/analyze <symbol>`"

            elif any(keyword in text_lower for keyword in ['analysis', 'analyze', 'signal']):
                return "📊 For deep analysis, use `/analyze <symbol>` or `/futures_signals` for daily futures signals.\n\nExample: `/analyze btc` or `/futures_signals`\n💡 **Note**: Analysis includes technical analysis, sentiment, and trading recommendations."

            elif any(keyword in text_lower for keyword in ['market', 'overview']):
                return "📈 Use `/market` command to see overall crypto market overview.\n\nWant to know about market cap, BTC dominance, or market trends?"

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
        """Get comprehensive market sentiment with advanced sideways detection and detailed analysis"""
        try:
            if not crypto_api:
                return self._get_fallback_market_data(language)

            # Check CoinMarketCap availability
            if not crypto_api.cmc_provider or not crypto_api.cmc_provider.api_key:
                print("❌ CoinMarketCap API not available, using enhanced fallback")
                return self._get_enhanced_fallback_market_data(language, crypto_api)

            print("📊 Getting advanced market overview from CoinMarketCap...")
            market_overview = crypto_api.get_market_overview()

            if 'error' in market_overview:
                print(f"❌ CoinMarketCap market overview failed: {market_overview.get('error')}")
                return self._get_enhanced_fallback_market_data(language, crypto_api)

            # Get comprehensive data for enhanced analysis
            btc_data = crypto_api.get_coinapi_price('BTC', force_refresh=True)
            eth_data = crypto_api.get_coinapi_price('ETH', force_refresh=True)

            # Get multiple altcoins for market condition analysis
            altcoins = ['BNB', 'SOL', 'ADA', 'AVAX', 'MATIC']
            altcoin_data = {}
            for coin in altcoins:
                price_data = crypto_api.get_coinapi_price(coin, force_refresh=True)
                if 'error' not in price_data:
                    altcoin_data[coin] = price_data

            # Analyze overall market condition
            market_condition = self._analyze_overall_market_condition(btc_data, eth_data, altcoin_data, crypto_api)

            # Enhanced market analysis
            total_cap = market_overview.get('total_market_cap', 0)
            cap_change = market_overview.get('market_cap_change_24h', 0)
            btc_dominance = market_overview.get('btc_dominance', 0)
            eth_dominance = market_overview.get('eth_dominance', 0)
            total_volume = market_overview.get('total_volume_24h', 0)

            # Get BTC and ETH prices with change
            btc_price = btc_data.get('price', market_overview.get('btc_price', 0))
            btc_change = btc_data.get('change_24h', market_overview.get('btc_change_24h', 0))
            eth_price = eth_data.get('price', market_overview.get('eth_price', 0))
            eth_change = eth_data.get('change_24h', market_overview.get('eth_change_24h', 0))

            if language == 'id':
                result = f"""🌍 **OVERVIEW PASAR CRYPTO GLOBAL ADVANCED**

💰 **Kapitalisasi Pasar (CoinMarketCap):**
• **Total Market Cap**: ${total_cap/1000000000:.1f}B ({cap_change:+.1f}%)
• **24h Volume**: ${total_volume/1000000000:.1f}B
• **Dominasi BTC**: {btc_dominance:.1f}%
• **Dominasi ETH**: {eth_dominance:.1f}%

📊 **Koin Utama (Real-time CoinAPI):**
• **Bitcoin**: ${btc_price:,.0f} ({btc_change:+.1f}%)
• **Ethereum**: ${eth_price:,.0f} ({eth_change:+.1f}%)

🧠 **ANALISIS KONDISI PASAR:**
• **Overall Condition**: {market_condition.get('overall_condition', 'Mixed')}
• **Market Phase**: {market_condition.get('market_phase', 'Transition')}
• **Volatility Level**: {market_condition.get('volatility_level', 'Medium')}
• **Correlation Score**: {market_condition.get('correlation_score', 0):.1f}/10"""

                # Detailed market sentiment analysis
                if market_condition.get('overall_condition') == 'sideways':
                    result += f"""

🔄 **KONDISI SIDEWAYS MARKET TERDETEKSI**

📊 **Analisis Detailed Sideways:**
• **BTC Range**: ${market_condition.get('btc_support', 0):,.0f} - ${market_condition.get('btc_resistance', 0):,.0f}
• **ETH Range**: ${market_condition.get('eth_support', 0):,.0f} - ${market_condition.get('eth_resistance', 0):,.0f}
• **Sideways Duration**: {market_condition.get('sideways_duration', 0)} hari
• **Volume Trend**: {market_condition.get('volume_trend', 'Stable')}

⚠️ **Mengapa Market Sideways:**
• Tidak ada catalyst fundamental yang kuat
• Institutional buying/selling seimbang
• Profit taking setelah movement sebelumnya
• Menunggu konfirmasi trend baru

💡 **Strategi Trading Sideways:**
• **Range Trading**: Buy support, Sell resistance
• **Breakout Preparation**: Set alerts di level kunci
• **Position Size**: Lebih kecil untuk risk management
• **Timeframe**: Focus pada scalping dan day trading

🎯 **Level Breakout Kunci:**
• **BTC Bullish**: > ${market_condition.get('btc_resistance', 0):,.0f}
• **BTC Bearish**: < ${market_condition.get('btc_support', 0):,.0f}
• **Volume Required**: > {market_condition.get('avg_volume', 0):,.0f}

📈 **Altcoin Impact:**
• **Correlation**: {'Tinggi' if market_condition.get('altcoin_correlation', 0) > 0.7 else 'Rendah'}
• **Altseason Probability**: {market_condition.get('altseason_prob', 0):.0f}%
• **Best Performers**: {', '.join(market_condition.get('best_performers', ['N/A']))}"""

                elif cap_change > 3:
                    result += f"\n• 🚀 **Bullish Strong** - Market cap naik {cap_change:.1f}%"
                elif cap_change > 1:
                    result += f"\n• 📈 **Bullish** - Market cap naik {cap_change:.1f}%"
                elif cap_change > -1:
                    result += f"\n• 📊 **Consolidation** - Market cap stabil ({cap_change:+.1f}%)"
                elif cap_change > -3:
                    result += f"\n• 📉 **Bearish** - Market cap turun {cap_change:.1f}%"
                else:
                    result += f"\n• 🔻 **Bearish Strong** - Market cap turun {cap_change:.1f}%"

                # Enhanced BTC dominance analysis
                if btc_dominance > 60:
                    result += f"""

👑 **BTC DOMINANCE ANALYSIS:**
• **Dominance**: {btc_dominance:.1f}% (Tinggi)
• **Altcoin Impact**: Bearish untuk altcoin
• **Strategy**: Focus pada BTC, avoid altcoin long
• **Next Phase**: Tunggu dominance turun untuk altseason"""
                elif btc_dominance > 50:
                    result += f"""

⚖️ **BTC DOMINANCE ANALYSIS:**
• **Dominance**: {btc_dominance:.1f}% (Normal)
• **Altcoin Impact**: Seimbang
• **Strategy**: Selective altcoin trading
• **Next Phase**: Monitor direction untuk trend"""
                else:
                    result += f"""

🌈 **ALTCOIN SEASON ACTIVE:**
• **BTC Dominance**: {btc_dominance:.1f}% (Rendah)
• **Altcoin Impact**: Bullish untuk altcoin
• **Strategy**: Focus pada quality altcoin
• **Risk**: BTC bisa bounce back kapan saja"""

            else:
                result = f"""🌍 **ADVANCED GLOBAL CRYPTO MARKET OVERVIEW**

💰 **Market Capitalization (CoinMarketCap):**
• **Total Market Cap**: ${total_cap/1000000000:.1f}B ({cap_change:+.1f}%)
• **24h Volume**: ${total_volume/1000000000:.1f}B
• **BTC Dominance**: {btc_dominance:.1f}%
• **ETH Dominance**: {eth_dominance:.1f}%

📊 **Major Coins (Real-time CoinAPI):**
• **Bitcoin**: ${btc_price:,.0f} ({btc_change:+.1f}%)
• **Ethereum**: ${eth_price:,.0f} ({eth_change:+.1f}%)

🧠 **MARKET CONDITION ANALYSIS:**
• **Overall Condition**: {market_condition.get('overall_condition', 'Mixed')}
• **Market Phase**: {market_condition.get('market_phase', 'Transition')}
• **Volatility Level**: {market_condition.get('volatility_level', 'Medium')}
• **Correlation Score**: {market_condition.get('correlation_score', 0):.1f}/10"""

                # Detailed market sentiment analysis for English
                if market_condition.get('overall_condition') == 'sideways':
                    result += f"""

🔄 **SIDEWAYS MARKET CONDITION DETECTED**

📊 **Detailed Sideways Analysis:**
• **BTC Range**: ${market_condition.get('btc_support', 0):,.0f} - ${market_condition.get('btc_resistance', 0):,.0f}
• **ETH Range**: ${market_condition.get('eth_support', 0):,.0f} - ${market_condition.get('eth_resistance', 0):,.0f}
• **Sideways Duration**: {market_condition.get('sideways_duration', 0)} days
• **Volume Trend**: {market_condition.get('volume_trend', 'Stable')}

⚠️ **Why Market is Sideways:**
• No strong fundamental catalyst
• Balanced institutional buying/selling
• Profit taking after previous movements
• Waiting for new trend confirmation

💡 **Sideways Trading Strategy:**
• **Range Trading**: Buy support, Sell resistance
• **Breakout Preparation**: Set alerts at key levels
• **Position Size**: Smaller for risk management
• **Timeframe**: Focus on scalping and day trading

🎯 **Key Breakout Levels:**
• **BTC Bullish**: > ${market_condition.get('btc_resistance', 0):,.0f}
• **BTC Bearish**: < ${market_condition.get('btc_support', 0):,.0f}
• **Volume Required**: > {market_condition.get('avg_volume', 0):,.0f}

📈 **Altcoin Impact:**
• **Correlation**: {'High' if market_condition.get('altcoin_correlation', 0) > 0.7 else 'Low'}
• **Altseason Probability**: {market_condition.get('altseason_prob', 0):.0f}%
• **Best Performers**: {', '.join(market_condition.get('best_performers', ['N/A']))}"""

                # Regular sentiment analysis for non-sideways markets
                elif cap_change > 3:
                    result += f"\n• 🚀 **Strong Bullish** - Market cap up {cap_change:.1f}%"
                elif cap_change > 1:
                    result += f"\n• 📈 **Bullish** - Market cap up {cap_change:.1f}%"
                elif cap_change > -1:
                    result += f"\n• 📊 **Consolidation** - Market cap stable ({cap_change:+.1f}%)"
                elif cap_change > -3:
                    result += f"\n• 📉 **Bearish** - Market cap down {cap_change:.1f}%"
                else:
                    result += f"\n• 🔻 **Strong Bearish** - Market cap down {cap_change:.1f}%"

            # Add comprehensive futures market data
            btc_futures = crypto_api.get_comprehensive_futures_data('BTC')
            if 'error' not in btc_futures:
                funding_data = btc_futures.get('funding_rate_data', {})
                oi_data = btc_futures.get('open_interest_data', {})
                ls_data = btc_futures.get('long_short_ratio_data', {})
                liq_data = btc_futures.get('liquidation_data', {})

                if 'error' not in funding_data:
                    funding_rate = funding_data.get('last_funding_rate', 0) * 100
                    oi_value = oi_data.get('open_interest', 0)
                    long_ratio = ls_data.get('long_ratio', 50) if 'error' not in ls_data else 50
                    total_liq = liq_data.get('total_liquidation', 0) if 'error' not in liq_data else 0

                    if language == 'id':
                        result += f"""

⚡ **ADVANCED FUTURES METRICS (BTC):**
• **Funding Rate**: {funding_rate:.3f}%
• **Open Interest**: ${oi_value:,.0f}
• **Long/Short Ratio**: {long_ratio:.1f}% / {100-long_ratio:.1f}%
• **24h Liquidations**: ${total_liq:,.0f}

📊 **Interpretasi Futures:**"""

                    if funding_rate > 0.05:
                        result += f"\n• 🔴 **Extreme Greed** - Funding rate sangat tinggi, potential top"
                    elif funding_rate > 0.01:
                        result += f"\n• 🟡 **Bullish Sentiment** - Funding rate positif, bullish bias"
                    elif funding_rate < -0.05:
                        result += f"\n• 🔴 **Extreme Fear** - Funding rate sangat rendah, potential bottom"
                    elif funding_rate < -0.01:
                        result += f"\n• 🟡 **Bearish Sentiment** - Funding rate negatif, bearish bias"
                    else:
                        result += f"\n• 🟢 **Balanced Market** - Funding rate netral, market seimbang"

                    if long_ratio > 70:
                        result += f"\n• ⚠️ **Long Dominance** - Risk short squeeze"
                    elif long_ratio < 30:
                        result += f"\n• ⚠️ **Short Dominance** - Risk long squeeze"
                    else:
                        result += f"\n• ✅ **Balanced Positions** - Healthy long/short distribution"

                    else:
                        result += f"""

⚡ **ADVANCED FUTURES METRICS (BTC):**
• **Funding Rate**: {funding_rate:.3f}%
• **Open Interest**: ${oi_value:,.0f}
• **Long/Short Ratio**: {long_ratio:.1f}% / {100-long_ratio:.1f}%
• **24h Liquidations**: ${total_liq:,.0f}

📊 **Futures Interpretation:**"""

                    if funding_rate > 0.05:
                        result += f"\n• 🔴 **Extreme Greed** - Very high funding, possible top"
                    elif funding_rate > 0.01:
                        result += f"\n• 🟡 **Bullish Sentiment** - High positive funding"
                    elif funding_rate < -0.05:
                        result += f"\n• 🔴 **Extreme Fear** - Very low funding, possible bottom"
                    elif funding_rate < -0.01:
                        result += f"\n• 🟡 **Bearish Sentiment** - Negative funding"
                    else:
                        result += f"\n• 🟢 **Balanced Market** - Neutral funding"

                    if long_ratio > 70:
                        result += f"\n• ⚠️ **Long Dominance** - Short squeeze risk"
                    elif long_ratio < 30:
                        result += f"\n• ⚠️ **Short Dominance** - Long squeeze risk"
                    else:
                        result += f"\n• ✅ **Balanced Positions** - Healthy ratio"

            current_time = datetime.now().strftime('%H:%M WIB')
            result += f"""

⏰ **Update**: {current_time}
🔄 **Source**: CoinMarketCap Global + CoinAPI Real-time + Binance Futures
📊 **Analysis**: Advanced market condition detection with sideways recognition"""

            return result

        except Exception as e:
            return f"❌ Error in advanced comprehensive analysis ID: {str(e)}"