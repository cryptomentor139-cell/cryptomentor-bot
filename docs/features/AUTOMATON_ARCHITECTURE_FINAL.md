# Automaton Architecture - Final Clarity

## 🏗️ 2 SERVER RAILWAY ARCHITECTURE

### Server 1: AUTOMATON SERVER (Separate Railway)
```
Location: Separate folder (NOT in Bismillah/)
Railway: automaton-production.railway.app
Purpose: Run Automaton AI autonomously
API: Exposed via Conway API
```

**What it does:**
- Runs latest Automaton version
- Manages AI agents autonomously
- Provides API endpoints for bot to call
- Handles trading logic, wallet management, etc.

**Environment Variables:**
- `CONWAY_API_KEY` - API key for authentication
- `CONWAY_API_URL` - Base URL for API
- Other Automaton-specific configs

---

### Server 2: BOT SERVER (Bismillah/ folder)
```
Location: Bismillah/ folder
Railway: cryptomentor-bot.railway.app
Purpose: Telegram bot orchestration
Integration: HTTP API calls to Automaton Server
```

**What it does:**
- Handles Telegram user interactions
- Calls Automaton API via HTTP requests
- Manages user database (Supabase)
- Sends signals, processes commands, etc.

**Integration Method:**
- Uses `app/conway_integration.py` for API calls
- NO subprocess, NO database access to Automaton
- Pure HTTP REST API communication

---

## 🔌 INTEGRATION FLOW

```
User → Telegram Bot → Bot Server (Railway #1)
                          ↓
                    HTTP API Call
                          ↓
                   Automaton Server (Railway #2)
                          ↓
                    Conway API Response
                          ↓
                   Bot Server processes
                          ↓
                   Response to User
```

---

## 📁 FILES IN BOT SERVER (Bismillah/)

### ✅ NEEDED (Currently Used):
1. **`app/conway_integration.py`**
   - Conway API client
   - HTTP requests to Automaton API
   - Methods: `spawn_agent()`, `get_agent_status()`, `get_credit_balance()`

2. **`app/handlers_automaton.py`**
   - Telegram command handlers
   - Routes commands to API handlers

3. **`app/handlers_automaton_api.py`**
   - API integration handlers
   - Calls Conway API for Automaton operations

### ❌ NOT NEEDED (Can be removed):
1. **`automaton_bot_client.py`** - Old local client (subprocess-based)
2. **`automaton_autotrade_client.py`** - Old local client (subprocess-based)
3. **`bot_v3_*.py`** - Example files
4. **`AUTO_TRADE_INTEGRATION_GUIDE.md`** - Template/guide
5. **`KIRO_PROMPT_FOR_V3_BOT.md`** - Template/guide

These files are for LOCAL development where Automaton runs on same machine.
In production, we use HTTP API instead.

---

## 🔑 ENVIRONMENT VARIABLES

### Bot Server (.env):
```bash
# Automaton API (Conway)
CONWAY_API_URL=https://automaton-xxx.railway.app
CONWAY_API_KEY=your_api_key_here

# Centralized Wallet
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822

# Other bot configs...
```

### Automaton Server (.env):
```bash
# Automaton-specific configs
# (Managed separately in Automaton Railway deployment)
```

---

## 🎯 KEY POINTS

1. **Bot ONLY calls API** - No direct Automaton code in bot
2. **Automaton runs independently** - Latest version on separate Railway
3. **Communication via HTTP** - REST API calls only
4. **No file sharing** - Each server has own codebase
5. **API Key authentication** - Secure communication

---

## 🚀 DEPLOYMENT

### Bot Server:
```bash
cd Bismillah
git add .
git commit -m "Update"
git push origin main
# Railway auto-deploys
```

### Automaton Server:
```bash
# Managed separately
# No changes needed from bot side
```

---

## ✅ CURRENT STATUS

- ✅ Automaton Server: Running with latest version
- ✅ Bot Server: Integrated via Conway API
- ✅ API Communication: Working
- ✅ No local Automaton files needed in bot

---

## 📝 CONCLUSION

**Bot folder (`Bismillah/`) does NOT need Automaton client files.**

Bot only needs:
1. Conway API integration (`app/conway_integration.py`)
2. API handlers (`app/handlers_automaton_api.py`)
3. Environment variables (CONWAY_API_URL, CONWAY_API_KEY)

Everything else is handled by Automaton Server on separate Railway deployment.

---

**Date**: 2026-02-23
**Status**: ✅ Architecture Confirmed
**Action**: No changes needed to bot for Automaton integration
