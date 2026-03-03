# 🤖 Automaton AI + AI Agent Menu Integration

## 🎯 Konsep

Menggabungkan **Automaton AI Dashboard** (yang sudah running) dengan **AI Agent Menu** (yang sudah ada di bot) untuk membuat autonomous trading agents yang dikelola oleh AI.

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT                             │
│                                                             │
│  User → Menu AI Agent → Spawn Child Agent                  │
│                              ↓                              │
│                    Create Agent Record                      │
│                              ↓                              │
│                    Link to Automaton AI                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              AUTOMATON AI DASHBOARD                         │
│                                                             │
│  - Receives agent instructions                              │
│  - Analyzes market autonomously                             │
│  - Makes trading decisions                                  │
│  - Executes trades via Conway API                           │
│  - Reports back to bot                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  CONWAY API                                 │
│                                                             │
│  - Manages USDC balance                                     │
│  - Executes trades                                          │
│  - Tracks P&L                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Integration Flow

### 1. User Spawns Agent (via Menu)

```
User clicks: Menu → AI Agent → Spawn New Agent
    ↓
Bot creates agent record in database
    ↓
Bot sends initialization task to Automaton AI
    ↓
Automaton AI receives agent context:
- Agent ID
- User ID
- Initial balance (USDC)
- Trading strategy
- Risk parameters
    ↓
Automaton AI starts autonomous trading loop
```

### 2. Autonomous Trading Loop

```
Automaton AI (continuous loop):
    ↓
1. Analyze market conditions
    ↓
2. Check agent balance (via Conway API)
    ↓
3. Make trading decision
    ↓
4. Execute trade (if conditions met)
    ↓
5. Update agent status in database
    ↓
6. Sleep for interval (e.g., 5 minutes)
    ↓
Repeat
```

### 3. User Monitors Agent (via Menu)

```
User clicks: Menu → AI Agent → Agent Status
    ↓
Bot queries database for agent info
    ↓
Bot queries Automaton AI for latest activity
    ↓
Bot displays:
- Current balance
- Active trades
- P&L
- Recent decisions
- Next action
```

## 🛠️ Implementation Plan

### Phase 1: Basic Integration ✅

**Files to Create:**
1. `app/automaton_agent_bridge.py` - Bridge between bot and Automaton AI
2. Update `menu_handlers.py` - Add Automaton AI integration to AI Agent menu
3. Update `app/handlers_automaton.py` - Add autonomous trading functions

**Key Functions:**
```python
# app/automaton_agent_bridge.py

class AutomatonAgentBridge:
    """Bridge between Telegram bot and Automaton AI for agent management"""
    
    def spawn_autonomous_agent(self, user_id, agent_name, initial_balance):
        """Spawn agent and link to Automaton AI"""
        
    def send_agent_instruction(self, agent_id, instruction):
        """Send instruction to Automaton AI for specific agent"""
        
    def get_agent_activity(self, agent_id):
        """Get latest activity from Automaton AI"""
        
    def start_trading_loop(self, agent_id):
        """Start autonomous trading loop in Automaton AI"""
        
    def stop_trading_loop(self, agent_id):
        """Stop autonomous trading loop"""
```

### Phase 2: Trading Strategy

**Automaton AI Prompt Template:**
```
You are an autonomous trading agent managing USDC for user {user_id}.

Agent ID: {agent_id}
Current Balance: {balance} USDC
Risk Level: {risk_level}
Strategy: {strategy}

Your tasks:
1. Monitor market conditions every 5 minutes
2. Analyze trading opportunities
3. Execute trades when conditions are favorable
4. Manage risk (max 5% per trade)
5. Report significant events

Current market data:
{market_data}

What is your next action?
```

### Phase 3: Safety & Controls

**Safety Features:**
- Max trade size: 5% of balance
- Stop loss: Automatic at -10%
- Daily loss limit: -20%
- Require user approval for trades > $100
- Emergency stop button

## 📝 Database Schema Updates

### Add to `user_automatons` table:

```sql
ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS
    automaton_ai_task_id TEXT,           -- Link to Automaton AI task
    trading_enabled BOOLEAN DEFAULT false, -- Enable/disable trading
    strategy TEXT DEFAULT 'conservative',  -- Trading strategy
    risk_level TEXT DEFAULT 'low',        -- Risk level
    max_trade_size_pct FLOAT DEFAULT 5.0, -- Max % per trade
    daily_loss_limit_pct FLOAT DEFAULT 20.0, -- Daily loss limit
    last_trade_at TIMESTAMP,              -- Last trade timestamp
    total_trades INTEGER DEFAULT 0,       -- Total trades executed
    winning_trades INTEGER DEFAULT 0,     -- Winning trades
    losing_trades INTEGER DEFAULT 0;      -- Losing trades
```

## 🎮 User Interface Updates

### AI Agent Menu (Updated)

```
🤖 AI Agent Menu

Your Agents:
├─ Agent 1: TradingBot Alpha
│  ├─ Status: 🟢 Active Trading
│  ├─ Balance: 150.50 USDC
│  ├─ P&L: +15.50 USDC (+11.5%)
│  └─ Last Trade: 5 min ago
│
└─ Agent 2: Conservative Bot
   ├─ Status: 🟡 Monitoring
   ├─ Balance: 200.00 USDC
   ├─ P&L: +5.00 USDC (+2.5%)
   └─ Last Trade: 2 hours ago

[➕ Spawn New Agent]
[📊 View Details]
[⚙️ Settings]
[🔴 Emergency Stop All]
[🔙 Back to Main Menu]
```

### Agent Details View

```
🤖 Agent: TradingBot Alpha

📊 Performance:
├─ Current Balance: 150.50 USDC
├─ Initial Balance: 135.00 USDC
├─ Total P&L: +15.50 USDC (+11.5%)
├─ Win Rate: 65% (13/20 trades)
└─ Active Since: 2 days ago

🎯 Current Status:
├─ Mode: 🟢 Active Trading
├─ Strategy: Aggressive
├─ Risk Level: Medium
└─ Next Check: 3 minutes

📈 Recent Activity:
├─ 5 min ago: Bought BTCUSDT @ 45,250
├─ 1 hour ago: Sold ETHUSDT @ 2,850 (+2.5%)
└─ 3 hours ago: Monitoring market

⚙️ Actions:
[▶️ Start Trading] [⏸️ Pause] [🛑 Stop]
[📝 Change Strategy] [⚙️ Settings]
[🔙 Back]
```

## 🚀 Quick Start Implementation

Saya akan buat file-file yang diperlukan untuk integration ini. Apakah Anda ingin saya lanjutkan dengan:

1. **Option A: Full Integration** (Complete autonomous trading)
   - Automaton AI makes all decisions
   - Executes trades automatically
   - User just monitors

2. **Option B: Semi-Autonomous** (Hybrid approach)
   - Automaton AI analyzes and recommends
   - User approves trades
   - More control for user

3. **Option C: Assisted Trading** (AI advisor)
   - Automaton AI provides signals
   - User executes manually
   - Safest option

Mana yang Anda prefer? Atau saya buat semua 3 mode dan user bisa pilih?
