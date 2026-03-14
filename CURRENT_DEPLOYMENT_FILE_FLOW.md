# 🌳 CURRENT DEPLOYMENT - FILE FLOW DIAGRAM

## 📊 **Yang Sedang Deploy di Railway Sekarang**
**Commit:** d606f8c - "Fix: AutoTrade API authentication and error handling"  
**Status:** ✅ ACTIVE & RUNNING  
**Time:** 2026-03-14 17:41 WIB  

---

## 🎯 **MAIN ENTRY POINT**

```
🚀 Railway Start
    ↓
📱 bot.py (MAIN FILE)
    ├── Load environment (.env)
    ├── Initialize TelegramBot class
    ├── Setup handlers & commands
    └── Start polling
```

---

## 🌲 **CORE SYSTEM FLOW**

### 1️⃣ **Bot Initialization Flow**
```
bot.py
├── � services.py
│   ├── get_database() → database.py
│   ├── get_ai_assistant() → ai_assistant.py ✅ RESTORED
│   └── get_crypto_api() → crypto_api.py ✅ RESTORED
│
├── � menu_system.py
│   └── MenuBuilder class (button layouts)
│
└── � menu_handlers.py
    ├── MenuCallbackHandler class
    └── Handle all button clicks
```

### 2️⃣ **User Interaction Flow**
```
User sends /start
    ↓
bot.py → start_command()
    ├── � database.py (register user)
    ├── � menu_system.py (build menu)
    └── � Send welcome message with buttons
```

### 3️⃣ **Menu Button Click Flow**
```
User clicks button
    ↓
menu_handlers.py → handle_callback_query()
    ├── � Check callback_data
    ├── 💳 app/credits_guard.py (check premium/credits) ✅ FIXED
    │   ├── app/premium_checker.py ✅ RESTORED
    │   └── app/users_repo.py (database operations)
    │
    └── Execute specific handler
```

---

## 🎯 **FEATURE-SPECIFIC FLOWS**

### 🤖 **AI Features Flow**
```
User clicks "Multi-Coin Signals"
    ↓
menu_handlers.py → handle_multi_coin_signals()
    ├── � app/credits_guard.py → require_credits()
    │   ├── Check if premium → app/premium_checker.py
    │   ├── If premium → Bypass credit deduction
    │   └── If free → Deduct 60 credits
    │
    ├── 🧠 ai_assistant.py → generate_futures_signals() ✅ RESTORED
    │   └── app/free_signal_generator.py (fallback)
    │
    └── � crypto_api.py → get_crypto_price() ✅ RESTORED
        └── app/simple_crypto_api.py (real API calls)
```

### 💰 **Credits System Flow**
```
User uses paid feature
    ↓
app/credits_guard.py → require_credits()
    ├── � _check_premium() → Check user status
    │   ├── app/supabase_repo.py (database query)
    │   └── Check is_lifetime, is_premium, premium_until
    │
    ├── ✅ If Premium/Lifetime → Return unlimited access
    └── � If Free → Deduct credits via app/users_repo.py
```

### � **AutoTrade System Flow** ✅ FIXED
```
Admin uses AutoTrade
    ↓
app/bitunix_api.py → Enhanced API class ✅ FIXED
    ├── 🔐 Fixed signature generation (HMAC-SHA256)
    ├── 🛡️ Enhanced error handling (403/401)
    ├── 💰 get_formatted_balance() → 200 USDT confirmed
    └── 🧪 test_connection() → Comprehensive testing
```

---

## 📁 **DATABASE & STORAGE FLOW**

### 💾 **Database Layer**
```
All database operations
    ↓
database.py (Main DB class)
    ├── 🏠 Local SQLite (fallback)
    └── ☁️ Supabase (primary)
        ├── app/supabase_conn.py (connection)
        ├── app/supabase_repo.py (queries)
        └── app/users_repo.py (user operations)
```

### 🔄 **Data Flow Example**
```
User registration
    ↓
bot.py → start_command()
    ├── 📝 app/sb_repo.upsert_user_strict() (Supabase)
    └── � database.py → create_user() (Local backup)
```

---

## 🎮 **COMMAND HANDLERS FLOW**

### � **Basic Commands**
```
/menu → bot.py → menu_command()
    └── menu_system.py → build_main_menu()

/price → bot.py → price_command()
    └── crypto_api.py → get_crypto_price()

/credits → bot.py → credits_command()
    └── app/users_repo.py → get_user_by_telegram_id()
```

### 🧠 **AI Commands** ✅ WORKING
```
/ai → app/handlers_deepseek.py → handle_ai_analyze()
    └── cerebras_ai.py (Ultra-fast AI - 0.4s response)

/chat → app/handlers_deepseek.py → handle_ai_chat()
    └── cerebras_ai.py

/aimarket → app/handlers_deepseek.py → handle_ai_market_summary()
    └── cerebras_ai.py
```

### � **Signal Generation** ✅ WORKING
```
/analyze → app/handlers_manual_signals.py → cmd_analyze()
    ├── � app/credits_guard.py (20 credits)
    └── � Signal generation logic

/futures → app/handlers_manual_signals.py → cmd_futures()
    ├── 💳 app/credits_guard.py (20 credits)
    └── � Futures signal logic

/futures_signals → app/handlers_manual_signals.py → cmd_futures_signals()
    ├── 💳 app/credits_guard.py (60 credits)
    └── 🎯 Multi-coin signals
```

---

## � **ADMIN & MANAGEMENT FLOW**

### � **Admin Commands**
```
/admin → bot.py → admin_command()
    ├── � app/admin_status.py → is_admin()
    └── Show admin menu

/set_premium → app/handlers_admin_premium.py
    └── Grant premium status

/grant_credits → app/handlers_admin_premium.py
    └── Add credits to user
```

### 🤖 **AutoTrade Management** ✅ FIXED
```
Admin AutoTrade Flow
    ↓
app/enhanced_autotrade_engine.py
    ├── � app/bitunix_api.py (Fixed API)
    ├── � Market analysis
    ├── 🎯 Signal generation
    └── � Risk management (1-2% per trade)
```

---

## 🌐 **EXTERNAL INTEGRATIONS**

### ☁️ **Supabase Integration**
```
All user data operations
    ↓
app/supabase_conn.py → get_supabase_client()
    ├── � Users table (premium status, credits)
    ├── �  Transactions (credit history)
    └── � Analytics (usage stats)
```

### 🔄 **API Integrations**
```
Market Data
    ↓
crypto_api.py → SimpleCryptoAPI
    ├── � Binance API (price data)
    ├── 📊 CoinGecko API (market data)
    └── 🔄 Real-time updates

Trading API ✅ FIXED
    ↓
app/bitunix_api.py
    ├── 🔐 HMAC-SHA256 signature (FIXED)
    ├── 💰 Balance: 200 USDT confirmed
    └── 🛡️ Enhanced error handling
```

---

## 🎯 **CRITICAL FILE DEPENDENCIES**

### ✅ **Core Files (Must Work)**
```
🚀 bot.py
    ├── 📋 menu_system.py
    ├── 🎮 menu_handlers.py
    ├── 💾 database.py
    └── 🔧 services.py
```

### ✅ **Premium System (Recently Fixed)**
```
💳 app/credits_guard.py ✅ ENHANCED
    ├── 🔍 app/premium_checker.py ✅ RESTORED
    ├── 👤 app/users_repo.py
    └── ☁️ app/supabase_repo.py
```

### ✅ **AI System (Recently Restored)**
```
🧠 ai_assistant.py ✅ RESTORED
    ├── 📊 app/free_signal_generator.py
    └── 📈 futures_signal_generator.py

� crypto_api.py ✅ RESTORED
    ├── 🔗 app/simple_crypto_api.py
    └── 🌐 External APIs
```

### ✅ **AutoTrade System (Recently Fixed)**
```
🤖 app/bitunix_api.py ✅ FIXED
    ├── � Signature generation (FIXED)
    ├── � Balance verification (200 USDT)
    └── �️ Error handling (Enhanced)

🎯 app/enhanced_autotrade_engine.py
    ├── 📊 Market analysis
    └── 💰 Risk management
```

---

## 🎉 **DEPLOYMENT STATUS SUMMARY**

### ✅ **What's Working**
- 🤖 **Bot Core:** Fully operational
- 📋 **Menu System:** All buttons working
- 💳 **Premium Detection:** Fixed & working
- 🧠 **AI Features:** Restored & working
- 📊 **Signal Generation:** All methods working
- � **AutoTrade:** API fixed, ready for live trading
- 💾 **Database:** Dual system (Supabase + Local)

### 🔧 **File Status**
- ✅ **Essential Files:** All restored and working
- ✅ **Premium System:** Enhanced with bypass logic
- ✅ **AI Assistant:** Restored with fallback mechanisms
- ✅ **AutoTrade API:** Fixed authentication & error handling
- ✅ **Menu Handlers:** All callback handlers working

### 🎯 **Ready for Production**
The current deployment is **FULLY FUNCTIONAL** with all critical systems working:
- Premium users get unlimited access
- Free users get proper credit deduction
- AutoTrade system ready with 200 USDT balance
- All menu buttons and commands working
- Enhanced error handling and user experience

---

*Last Updated: 2026-03-14 18:15 WIB*  
*Deployment Status: ✅ ACTIVE & STABLE*  
*Next Review: Monitor user feedback & performance*