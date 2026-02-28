# 🏗️ Arsitektur 2 Server Railway - Bot & Automaton

## Overview

Sistem ini menggunakan **2 server Railway yang TERPISAH**:

```
┌─────────────────────────────────────────────────────────────┐
│                    RAILWAY DEPLOYMENT                       │
└─────────────────────────────────────────────────────────────┘

Server 1: BOT (Python)                Server 2: AUTOMATON (Node.js)
┌──────────────────────┐              ┌──────────────────────┐
│  Folder: Bismillah/  │              │ Folder: automaton/   │
│  Language: Python    │              │ Language: TypeScript │
│  Framework: Telegram │              │ Framework: Express   │
│  Bot API             │              │ Conway Framework     │
│                      │              │                      │
│  - bot.py            │◄────HTTP────►│  - index.ts          │
│  - handlers_*.py     │   API Call   │  - conway/*.ts       │
│  - conway_integration│              │  - payment/*.ts      │
│    .py               │              │                      │
└──────────────────────┘              └──────────────────────┘
         │                                      │
         │                                      │
         ▼                                      ▼
    Supabase DB                          Conway Credits
    (User data)                          (Blockchain)
```

## Folder Structure

### Server 1: Bot (Python)
```
Bismillah/
├── bot.py                          # Main bot
├── app/
│   ├── handlers_automaton.py      # /spawn_agent, /deposit
│   ├── conway_integration.py      # Conway API client
│   └── automaton_manager.py       # Agent management
├── .env                            # Bot environment
└── requirements.txt                # Python dependencies
```

### Server 2: Automaton (Node.js)
```
automaton/
├── src/
│   ├── index.ts                    # Main server
│   ├── conway/                     # Conway logic
│   ├── payment/                    # Payment handling
│   └── telegram/                   # Telegram integration
├── .env                            # Automaton environment
└── package.json                    # Node dependencies
```

## Masalah Deposit Address

### ❌ Masalah Awal
Bot mencoba call endpoint di Automaton server:
```python
# Bot (Python) tries to call:
POST https://automaton-production-a899.up.railway.app/api/v1/agents/address

# But Automaton server doesn't have this endpoint!
# Result: 404 Not Found
```

### ✅ Solusi yang Benar

**TIDAK PERLU** tambah endpoint di Automaton server!

Gunakan **Centralized Custodial Wallet** di Bot server:

```python
# Bot (Python) - conway_integration.py
def generate_deposit_address(self, user_id, agent_name):
    # Return centralized wallet address (no API call needed)
    return os.getenv('CENTRALIZED_WALLET_ADDRESS')
```

## Kenapa Solusi Ini Benar?

### 1. Tidak Perlu API Call
```
BEFORE (❌ Error):
Bot → HTTP Request → Automaton → Generate Address → Return
      (404 Not Found)

AFTER (✅ Works):
Bot → Read ENV Variable → Return Address
      (No API call needed)
```

### 2. Centralized Wallet
Semua user deposit ke wallet yang sama:
```
User A ──┐
User B ──┼──> 0x63116672bef9f26fd906cd2a57550f7a13925822
User C ──┘    (Centralized Custodial Wallet)
```

### 3. Tracking di Database
```sql
-- Bot's Supabase database tracks deposits
CREATE TABLE user_automatons (
    user_id BIGINT,
    conway_deposit_address VARCHAR(42),  -- Same for all users
    conway_credits DECIMAL(20, 2)
);
```

## Kapan Bot Call Automaton API?

Bot HANYA call Automaton API untuk:

### 1. Health Check
```python
GET /health
# Check if Automaton is alive
```

### 2. Spawn Agent (Future)
```python
POST /api/v1/agents/spawn
# Create autonomous trading agent
```

### 3. Agent Status (Future)
```python
GET /api/v1/agents/{agent_id}/status
# Get agent performance
```

## Deployment Strategy

### Server 1: Bot
```bash
# Railway Project 1: Bot
cd Bismillah/
git push origin main
# Railway auto-deploys from Bismillah/ folder
```

**Environment Variables:**
```bash
TELEGRAM_BOT_TOKEN=...
SUPABASE_URL=...
CONWAY_API_URL=https://automaton-production-a899.up.railway.app
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822
```

### Server 2: Automaton
```bash
# Railway Project 2: Automaton
cd automaton/
git push origin main
# Railway auto-deploys from automaton/ folder
```

**Environment Variables:**
```bash
CONWAY_API_KEY=...
DATABASE_URL=...
WALLET_PRIVATE_KEY=...
```

## Communication Flow

### User Spawns Agent

```
1. User: /spawn_agent MyBot
   ↓
2. Bot (Python):
   - Check user credits
   - Generate deposit address (from ENV, no API call)
   - Save to Supabase
   ↓
3. Bot Response:
   ✅ Agent Berhasil Dibuat!
   📍 Deposit Address: 0x63116672bef9f26fd906cd2a57550f7a13925822
```

### User Deposits USDC

```
1. User sends USDC to: 0x63116672bef9f26fd906cd2a57550f7a13925822
   ↓
2. Blockchain confirms transaction
   ↓
3. Deposit Monitor (Bot):
   - Detects deposit
   - Credits user account in Supabase
   ↓
4. Bot notifies user:
   💰 Deposit received! +3000 credits
```

### Agent Starts Trading (Future)

```
1. User: /start_trading
   ↓
2. Bot (Python):
   POST /api/v1/agents/spawn
   → Automaton Server
   ↓
3. Automaton (Node.js):
   - Creates autonomous agent
   - Starts trading logic
   - Returns agent_id
   ↓
4. Bot saves agent_id to Supabase
```

## Key Differences

| Aspect | Bot Server | Automaton Server |
|--------|-----------|------------------|
| Language | Python | TypeScript/Node.js |
| Purpose | User interface | Autonomous agents |
| Database | Supabase | Conway Credits |
| Deployment | Railway Project 1 | Railway Project 2 |
| Folder | `Bismillah/` | `automaton/` |
| Port | 8080 | 3000 |

## What Changed?

### ✅ Bot Server (Bismillah/)
- Modified `conway_integration.py`
- Now uses centralized wallet address
- No API call to Automaton for deposit address

### ❌ Automaton Server (automaton/)
- **NO CHANGES NEEDED**
- Doesn't need deposit address endpoint
- Continues to handle agent logic only

## Testing

### Test Bot (Python)
```bash
cd Bismillah
python test_deposit_address_fix.py
# ✅ Should pass - uses centralized wallet
```

### Test Automaton (Node.js)
```bash
cd automaton
npm test
# ✅ Should pass - no changes made
```

## Summary

### Problem
Bot tried to call non-existent endpoint on Automaton server for deposit address generation.

### Solution
Bot now uses centralized custodial wallet address from environment variable - no API call needed.

### Result
- ✅ Bot can generate deposit addresses
- ✅ No changes needed to Automaton server
- ✅ Simpler architecture
- ✅ Faster response (no HTTP call)

### Architecture
```
2 Separate Servers:
1. Bot (Python) - User interface, deposit tracking
2. Automaton (Node.js) - Autonomous agent logic

Bot uses centralized wallet for deposits.
Automaton handles agent trading logic.
```

**Both servers work independently!** 🚀
