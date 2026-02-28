# 🔄 Automaton Architecture Update - Conway Direct Integration

## Critical Change: Base Network Only

**IMPORTANT:** Conway Automaton hanya menerima **USDC via Base network**. Ini mengubah arsitektur dari design awal.

## What Changed

### Original Design (Complex)
```
User → Custodial Wallet (Platform) → Polygon/Base/Arbitrum → Conway
       ↓
   - Generate Ethereum wallets
   - Encrypt private keys
   - Monitor blockchain (USDT/USDC)
   - Handle deposits/withdrawals
   - Manage gas fees
```

### New Design (Simplified)
```
User → Conway Wallet (Direct) → Base Network → Agent
       ↓
   - Conway provides deposit address
   - Conway monitors blockchain
   - Conway handles all operations
   - We just call API
```

## Architecture Comparison

### Before (6 Tables + Blockchain)
1. ✅ custodial_wallets - Platform-managed wallets
2. ✅ wallet_deposits - Track deposits
3. ✅ wallet_withdrawals - Handle withdrawals
4. ✅ user_automatons - Agent records
5. ✅ automaton_transactions - Transaction history
6. ✅ platform_revenue - Revenue tracking

**Plus:**
- Blockchain monitoring service
- Wallet encryption system
- Private key management
- Multi-network support (Polygon, Base, Arbitrum)
- Multi-token support (USDT, USDC)

### After (3 Tables Only)
1. ✅ user_automatons - Agent records (with Conway deposit address)
2. ✅ automaton_transactions - Transaction history
3. ✅ platform_revenue - Revenue tracking

**Removed:**
- ❌ custodial_wallets (Conway provides addresses)
- ❌ wallet_deposits (Conway tracks deposits)
- ❌ wallet_withdrawals (Conway handles withdrawals)
- ❌ Blockchain monitoring (Conway does this)
- ❌ Wallet encryption (Conway manages keys)
- ❌ Private key management (Conway handles security)

## Benefits of Simplified Architecture

### 1. Security
- ✅ No private keys to manage
- ✅ No encryption key rotation
- ✅ No blockchain security concerns
- ✅ Conway's enterprise-grade security
- ✅ Fewer attack vectors

### 2. Simplicity
- ✅ 50% fewer database tables
- ✅ No blockchain monitoring code
- ✅ No wallet generation code
- ✅ No encryption implementation
- ✅ Simpler deployment

### 3. Reliability
- ✅ Conway handles blockchain complexity
- ✅ No RPC node failures
- ✅ No gas fee management
- ✅ Automatic retry logic
- ✅ Better uptime

### 4. Cost
- ✅ No RPC node costs (Alchemy/Infura)
- ✅ No gas fees to manage
- ✅ Simpler infrastructure
- ✅ Lower maintenance

### 5. Development Speed
- ✅ Faster implementation
- ✅ Less code to maintain
- ✅ Fewer dependencies
- ✅ Easier testing

## Updated Data Flow

### Deposit Flow
```
1. User spawns agent
   ↓
2. Bot calls Conway API: get_deposit_address(user_id)
   ↓
3. Conway returns: Base network USDC address
   ↓
4. Bot shows address to user with QR code
   ↓
5. User deposits USDC to address (Base network)
   ↓
6. Conway detects deposit automatically
   ↓
7. Conway credits agent wallet
   ↓
8. Conway webhook notifies our bot
   ↓
9. Bot notifies user via Telegram
```

### Agent Spawn Flow
```
1. User clicks "Spawn Agent"
   ↓
2. Bot verifies premium status
   ↓
3. Bot verifies 100k credits
   ↓
4. Bot deducts 100k credits
   ↓
5. Bot calls Conway API: create_agent(user_id, name, prompt)
   ↓
6. Conway creates agent + deposit address
   ↓
7. Conway returns agent_wallet + deposit_address
   ↓
8. Bot saves to user_automatons table
   ↓
9. Bot notifies user with deposit address
```

### Balance Check Flow
```
1. User clicks "Agent Status"
   ↓
2. Bot calls Conway API: get_balance(agent_wallet)
   ↓
3. Conway returns current balance
   ↓
4. Bot calculates survival tier
   ↓
5. Bot shows status to user
```

## Updated Database Schema

### user_automatons (Updated)
```sql
CREATE TABLE user_automatons (
  id UUID PRIMARY KEY,
  user_id BIGINT NOT NULL,
  agent_wallet TEXT UNIQUE NOT NULL,
  agent_name TEXT NOT NULL,
  conway_deposit_address TEXT UNIQUE NOT NULL,  -- NEW: Conway deposit address
  genesis_prompt TEXT,
  conway_credits DECIMAL(18, 2) DEFAULT 0,
  survival_tier TEXT DEFAULT 'normal',
  created_at TIMESTAMP DEFAULT NOW(),
  last_active TIMESTAMP DEFAULT NOW(),
  status TEXT DEFAULT 'active',
  total_earnings DECIMAL(18, 6) DEFAULT 0,
  total_expenses DECIMAL(18, 6) DEFAULT 0
);
```

### automaton_transactions (Unchanged)
```sql
CREATE TABLE automaton_transactions (
  id UUID PRIMARY KEY,
  automaton_id UUID REFERENCES user_automatons(id),
  type TEXT CHECK (type IN ('spawn', 'deposit', 'earn', 'spend', 'performance_fee')),
  amount DECIMAL(18, 6) NOT NULL,
  description TEXT,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

### platform_revenue (Unchanged)
```sql
CREATE TABLE platform_revenue (
  id UUID PRIMARY KEY,
  source TEXT CHECK (source IN ('deposit_fee', 'performance_fee', 'spawn_fee')),
  amount DECIMAL(18, 6) NOT NULL,
  agent_id UUID REFERENCES user_automatons(id),
  user_id BIGINT,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

## Updated Environment Variables

### Required (7 variables)
```bash
TELEGRAM_BOT_TOKEN=<your_token>
SUPABASE_URL=<your_url>
SUPABASE_KEY=<your_key>
SUPABASE_SERVICE_KEY=<your_service_key>
CONWAY_API_URL=https://api.conway.tech
CONWAY_API_KEY=<your_conway_key>
ADMIN_IDS=1187119989,7255533151
```

### Removed (5 variables)
```bash
# ❌ No longer needed
POLYGON_RPC_URL
WALLET_ENCRYPTION_KEY
POLYGON_USDT_CONTRACT
POLYGON_USDC_CONTRACT
BASE_USDC_CONTRACT
```

## Conway API Integration

### Key Endpoints

#### 1. Get Deposit Address
```python
GET /api/v1/wallets/{user_id}/deposit-address

Response:
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "network": "base",
  "token": "USDC"
}
```

#### 2. Create Agent
```python
POST /api/v1/agents

Body:
{
  "user_id": 1187119989,
  "name": "Trading Bot Alpha",
  "genesis_prompt": "You are an autonomous trading agent..."
}

Response:
{
  "agent_id": "agent_abc123",
  "agent_wallet": "0x...",
  "deposit_address": "0x...",
  "initial_credits": 0
}
```

#### 3. Check Balance
```python
GET /api/v1/wallets/{agent_wallet}/balance

Response:
{
  "balance": 10000,
  "currency": "conway_credits",
  "last_updated": "2026-02-20T10:30:00Z"
}
```

#### 4. Get Transactions
```python
GET /api/v1/wallets/{agent_wallet}/transactions

Response:
{
  "transactions": [
    {
      "type": "deposit",
      "amount": 500,
      "timestamp": "2026-02-20T10:00:00Z"
    }
  ]
}
```

## Implementation Tasks (Updated)

### Task 1: Database Setup ✅
- [x] Create simplified migration script
- [x] 3 tables instead of 6
- [x] Add conway_deposit_address column
- [x] Remove custodial wallet tables

### Task 2: Conway API Integration (Next)
- [ ] Create `app/conway_integration.py`
- [ ] Implement get_deposit_address()
- [ ] Implement create_agent()
- [ ] Implement get_balance()
- [ ] Implement get_transactions()
- [ ] Add retry logic with exponential backoff

### Task 3: Agent Manager (Simplified)
- [ ] Create `app/automaton_manager.py`
- [ ] Implement spawn_agent() - calls Conway API
- [ ] Implement get_agent_status() - calls Conway API
- [ ] Implement calculate_survival_tier()
- [ ] No wallet generation needed!
- [ ] No encryption needed!

### Task 4: Telegram Handlers
- [ ] Create `app/handlers_automaton.py`
- [ ] Implement spawn_agent_command
- [ ] Implement agent_status_command
- [ ] Implement deposit_command (show Conway address)
- [ ] Implement balance_command
- [ ] Implement agent_logs_command

### Task 5: Revenue Manager
- [ ] Create `app/revenue_manager.py`
- [ ] Track deposit fees (2%)
- [ ] Track performance fees (20%)
- [ ] Track spawn fees (100k credits)
- [ ] Generate revenue reports

## User Experience (Unchanged)

User flow tetap sama, hanya backend yang simplified:

```
1. User: /spawn_agent
   Bot: "Creating your agent..."
   Bot: "✅ Agent created! Deposit USDC to: 0x..."

2. User deposits USDC via Base network
   Conway: Detects deposit
   Bot: "✅ Received 100 USDC = 9,800 credits (2% fee)"

3. User: /agent_status
   Bot: "🤖 Agent Alpha
         💰 Credits: 9,800
         📊 Tier: Normal
         ⏱️ Runtime: ~49 days"

4. Agent trades and earns profit
   Bot: "✅ Trade closed: +50 USDC profit
         💰 Your share: 40 USDC (80%)
         🏦 Platform fee: 10 USDC (20%)"
```

## Migration Path

### For New Deployments
1. Use `002_automaton_simplified.sql`
2. Set up 7 environment variables
3. Implement Conway API integration
4. Deploy and test

### For Existing Deployments (If Any)
1. Backup existing data
2. Run `002_automaton_simplified.sql`
3. Migrate data if needed
4. Update environment variables
5. Deploy new code

## Testing Strategy

### 1. Conway API Tests
```python
def test_get_deposit_address():
    address = conway.get_deposit_address(user_id=123)
    assert address.startswith('0x')
    assert len(address) == 42

def test_create_agent():
    agent = conway.create_agent(
        user_id=123,
        name="Test Agent",
        prompt="Test prompt"
    )
    assert agent['agent_wallet']
    assert agent['deposit_address']

def test_get_balance():
    balance = conway.get_balance(agent_wallet="0x...")
    assert balance >= 0
```

### 2. Integration Tests
```python
def test_spawn_flow():
    # User spawns agent
    result = spawn_agent(user_id=123, name="Test")
    assert result['success']
    assert result['deposit_address']
    
    # Check database
    agent = db.get_agent(user_id=123)
    assert agent['conway_deposit_address']
```

### 3. End-to-End Tests
```python
def test_full_deposit_flow():
    # 1. Spawn agent
    agent = spawn_agent(user_id=123)
    
    # 2. Simulate deposit (testnet)
    deposit_usdc(agent['deposit_address'], amount=100)
    
    # 3. Wait for Conway to detect
    time.sleep(60)
    
    # 4. Check balance updated
    balance = get_agent_balance(agent['agent_wallet'])
    assert balance == 9800  # 100 USDC - 2% fee = 98 USDC = 9800 credits
```

## Timeline (Updated)

### Original Estimate: 4-5 weeks
- Week 1: Database + Wallet + Encryption
- Week 2: Blockchain monitoring + Deposits
- Week 3: Agent spawning + UI
- Week 4: Revenue + Testing
- Week 5: Deployment

### New Estimate: 2-3 weeks
- Week 1: Database + Conway API + Agent spawning
- Week 2: UI + Revenue + Testing
- Week 3: Deployment + Monitoring

**Time saved: 2 weeks!**

## Conclusion

Dengan Conway handling semua blockchain operations:
- ✅ 50% faster development
- ✅ 50% less code to maintain
- ✅ Better security (no private keys)
- ✅ Better reliability (Conway's infrastructure)
- ✅ Lower costs (no RPC nodes)
- ✅ Same user experience

**Status:** Ready to implement simplified architecture
**Next:** Implement Conway API integration (Task 2)

---

**Last Updated:** 2026-02-20
**Version:** 2.0.0 (Simplified Architecture)
**Author:** Kiro AI Assistant
