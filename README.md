# 🤖 CryptoMentor AI Bot

AI-powered Telegram bot untuk analisis crypto market dengan Supply & Demand zones detection.

## ✨ Features

- 🤖 **AI Analysis** - StepFun Step 3.5 Flash (FREE model)
- 📊 **Market Analysis** - Real-time price & market data
- 🧠 **SnD Zones** - Supply & Demand zone detection
- 📈 **Futures Signals** - Multi-coin futures signals
- 💼 **Portfolio** - Track your crypto portfolio
- 👑 **Premium** - Unlimited access untuk premium users

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Prerequisites

- Telegram Bot Token (dari @BotFather)
- Supabase Account (untuk database)
- API Keys (optional tapi recommended):
  - CryptoCompare API Key
  - Helius API Key

### Environment Variables

Tambahkan di Railway Variables:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here
TOKEN=your_bot_token_here
ADMIN1=your_telegram_user_id
DEEPSEEK_API_KEY=your_openrouter_api_key
AI_MODEL=stepfun/step-3.5-flash

# Database (Required)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Optional
ADMIN2=second_admin_id
CRYPTOCOMPARE_API_KEY=your_cryptocompare_key
HELIUS_API_KEY=your_helius_key
WELCOME_CREDITS=100
```

### Deployment Steps

1. **Fork/Clone** repository ini
2. **Login** ke [Railway.app](https://railway.app)
3. **New Project** → Deploy from GitHub repo
4. **Add Variables** dari list di atas
5. **Deploy!** 🚀

Bot akan otomatis start dan online 24/7!

## 📚 Documentation

- [Railway Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md) - Complete guide
- [Railway Quick Start](RAILWAY_QUICK_START.md) - 15 menit deploy
- [StepFun Setup](STEPFUN_SETUP_COMPLETE.md) - AI configuration
- [Network Issue Fix](SOLUSI_DATA_REALTIME.md) - Troubleshooting

## 🛠️ Local Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/cryptomentor-bot.git
cd cryptomentor-bot

# Install dependencies
pip install -r requirements.txt

# Copy .env.example to .env
cp .env.example .env

# Edit .env dengan API keys Anda
nano .env

# Run bot
python main.py
```

### Commands

```bash
# Run bot
python main.py

# Test AI
python test_stepfun.py

# Test network
python test_binance_klines.py
```

## 📊 Bot Commands

### User Commands
- `/start` - Start bot & get welcome message
- `/menu` - Show main menu
- `/ai <symbol>` - AI market analysis (e.g., `/ai btc`)
- `/chat <message>` - Chat dengan AI
- `/price <symbol>` - Check crypto price
- `/spot <symbol>` - Spot analysis dengan SnD zones
- `/futures <symbol>` - Futures analysis dengan SnD zones
- `/portfolio` - View your portfolio
- `/credits` - Check your credits
- `/subscribe` - Premium subscription info

### Admin Commands
- `/broadcast <message>` - Broadcast ke semua users
- `/stats` - Bot statistics
- `/addcredits <user_id> <amount>` - Add credits to user
- `/setpremium <user_id> <days>` - Set premium status

## 💰 Pricing

### Railway Hosting
- **Free Tier**: $5 credit per bulan
- **Estimated Cost**: ~$9/month (setelah free credit)
- **Uptime**: 24/7

### Bot Credits (Free Users)
- Spot Analysis: 20 credits
- Futures Analysis: 20 credits
- Multi-Coin Signals: 60 credits

### Premium (Unlimited Access)
- Monthly: Rp 320,000
- 2 Months: Rp 600,000
- 1 Year: Rp 3,500,000
- Lifetime: Rp 6,500,000

## 🔧 Tech Stack

- **Language**: Python 3.11
- **Framework**: python-telegram-bot 22.6
- **AI**: StepFun Step 3.5 Flash (via OpenRouter)
- **Database**: Supabase + SQLite
- **APIs**: Binance, CoinGecko, CryptoCompare
- **Hosting**: Railway.app

## 📝 License

Private - All rights reserved

## 👥 Support

- Telegram: [@BillFarr](https://t.me/BillFarr)
- Bot: [@Subridujdirdsjbot](https://t.me/Subridujdirdsjbot)

## 🎉 Credits

Developed with ❤️ by CryptoMentor Team

---

**Happy Trading! 🚀**
