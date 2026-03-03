# AUTOMATON TECHNICAL RULES
## Implementation Guidelines & Constraints

---

## 🏗️ SYSTEM ARCHITECTURE

### Component Hierarchy

```
┌─────────────────────────────────────┐
│     CORE AUTOMATON (Admin)          │
│  - Global Monitoring                │
│  - Task Distribution                │
│  - Revenue Management               │
└──────────────┬──────────────────────┘
               │
               ├─── Child Agent 1 (User A)
               │    ├─── Grandchild 1.1
               │    └─── Grandchild 1.2
               │
               ├─── Child Agent 2 (User B)
               │    └─── Grandchild 2.1
               │
               └─── Child Agent N (User N)
```

---

## 🔧 CORE AUTOMATON IMPLEMENTATION

### Database Schema Requirements

```sql
-- Core Automaton State
CREATE TABLE automaton_core (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status TEXT NOT NULL, -- 'active', 'paused', 'maintenance'
    last_report_time TIMESTAMP,
    total_managed_capital DECIMAL(20,8),
    active_child_count INTEGER,
    system_health_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Task Queue
CREATE TABLE automaton_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_type TEXT NOT NULL,
    assigned_to UUID REFERENCES ai_agents(id),
    priority INTEGER DEFAULT 5, -- 1-10
    status TEXT DEFAULT 'pending',
    payload JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    result JSONB
);

-- Performance Metrics
CREATE TABLE automaton_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type TEXT NOT NULL,
    agent_id UUID REFERENCES ai_agents(id),
    value DECIMAL(20,8),
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### Core Automaton Behavior Rules

#### Rule 1: Monitoring Cycle
```python
# Execute every 8 hours (3x daily)
MONITORING_SCHEDULE = ["08:00", "14:00", "20:00"]  # WIB

def generate_daily_report():
    """
    MUST include:
    - New deposits in last 8 hours
    - Total messages responded
    - Child agents spawned
    - Trading volume
    - Profit/Loss summary
    - System alerts
    """
    report = {
        "period": get_time_range(),
        "deposits": count_deposits(),
        "messages_handled": count_messages(),
        "agents_spawned": count_new_agents(),
        "trading_volume": sum_trading_volume(),
        "pnl": calculate_pnl(),
        "alerts": get_critical_alerts()
    }
    
    send_to_admin(report)
    log_to_database(report)
```

#### Rule 2: User Response Protocol
```python
MAX_RESPONSE_TIME = 300  # 5 minutes

async def handle_user_message(user_id, message):
    """
    Priority levels:
    1. Withdrawal requests (immediate)
    2. Deposit issues (< 2 min)
    3. Trading questions (< 5 min)
    4. General inquiries (< 10 min)
    """
    priority = classify_message(message)
    
    if priority == "CRITICAL":
        response = await generate_immediate_response(message)
        await send_response(user_id, response, delay=0)
    elif priority == "HIGH":
        response = await generate_response(message)
        await send_response(user_id, response, delay=120)
    else:
        await queue_response(user_id, message, max_delay=300)
```

#### Rule 3: Child Agent Spawning
```python
MIN_DEPOSIT_FOR_SPAWN = 10  # $10 USDC minimum

async def spawn_child_agent(user_id, deposit_amount):
    """
    Spawning conditions:
    - User has completed KYC (optional)
    - Deposit >= MIN_DEPOSIT_FOR_SPAWN
    - User doesn't have active agent
    - System capacity available
    """
    # Validate conditions
    if deposit_amount < MIN_DEPOSIT_FOR_SPAWN:
        raise ValueError(f"Minimum deposit is ${MIN_DEPOSIT_FOR_SPAWN}")
    
    if has_active_agent(user_id):
        raise ValueError("User already has an active agent")
    
    # Create child agent
    agent = await create_agent(
        user_id=user_id,
        agent_type="child",
        initial_capital=deposit_amount,
        parent_id=None,  # Direct child of Core
        risk_profile=get_user_risk_profile(user_id)
    )
    
    # Initialize wallet
    wallet = await create_wallet(agent.id)
    
    # Send welcome message
    await notify_user(user_id, f"Your AI Agent is ready! ID: {agent.id}")
    
    return agent
```

#### Rule 4: Task Distribution Algorithm
```python
TASK_GENERATION_INTERVAL = 300  # 5 minutes

async def distribute_tasks():
    """
    Task distribution strategy:
    - High performers get complex tasks
    - New agents get learning tasks
    - Struggling agents get recovery tasks
    """
    active_agents = await get_active_child_agents()
    
    for agent in active_agents:
        performance = await calculate_performance(agent.id)
        
        if performance.win_rate > 0.70:
            # High performer
            tasks = generate_advanced_tasks(agent, count=5)
        elif performance.win_rate > 0.50:
            # Average performer
            tasks = generate_standard_tasks(agent, count=3)
        else:
            # Needs improvement
            tasks = generate_learning_tasks(agent, count=2)
        
        await assign_tasks(agent.id, tasks)
```

---

## 👶 CHILD AGENT IMPLEMENTATION

### Agent State Machine

```python
class ChildAgentState(Enum):
    INITIALIZING = "initializing"
    WAITING_DEPOSIT = "waiting_deposit"
    ACTIVE_TRADING = "active_trading"
    PAUSED = "paused"
    WITHDRAWING = "withdrawing"
    TERMINATED = "terminated"

# State transitions
ALLOWED_TRANSITIONS = {
    "initializing": ["waiting_deposit", "terminated"],
    "waiting_deposit": ["active_trading", "terminated"],
    "active_trading": ["paused", "withdrawing", "terminated"],
    "paused": ["active_trading", "terminated"],
    "withdrawing": ["active_trading", "terminated"],
    "terminated": []  # Final state
}
```

### Trading Rules

#### Rule 1: Risk Management
```python
class RiskParameters:
    MAX_POSITION_SIZE = 0.20  # 20% of capital per trade
    MAX_DAILY_LOSS = 0.05     # 5% daily loss limit
    MAX_DRAWDOWN = 0.15       # 15% maximum drawdown
    MIN_RESERVE = 0.10        # 10% always in reserve
    
    STOP_LOSS_PERCENT = 0.02  # 2% stop loss per trade
    TAKE_PROFIT_PERCENT = 0.04  # 4% take profit (2:1 R:R)

async def validate_trade(agent_id, trade_params):
    """
    Pre-trade validation checklist:
    """
    agent = await get_agent(agent_id)
    balance = await get_balance(agent.wallet_address)
    
    # Check position size
    if trade_params.size > balance * RiskParameters.MAX_POSITION_SIZE:
        raise ValueError("Position size exceeds limit")
    
    # Check daily loss
    daily_pnl = await get_daily_pnl(agent_id)
    if daily_pnl < -balance * RiskParameters.MAX_DAILY_LOSS:
        raise ValueError("Daily loss limit reached")
    
    # Check drawdown
    drawdown = await calculate_drawdown(agent_id)
    if drawdown > RiskParameters.MAX_DRAWDOWN:
        raise ValueError("Maximum drawdown exceeded")
    
    # Check reserve
    if balance - trade_params.size < balance * RiskParameters.MIN_RESERVE:
        raise ValueError("Insufficient reserve balance")
    
    return True
```

#### Rule 2: Trading Execution
```python
async def execute_trade(agent_id, signal):
    """
    Trade execution workflow:
    1. Validate signal
    2. Check risk parameters
    3. Calculate position size
    4. Execute on exchange
    5. Log transaction
    6. Notify user
    """
    # Validate
    await validate_trade(agent_id, signal)
    
    # Calculate position
    position_size = calculate_position_size(
        agent_id, 
        signal.confidence,
        signal.risk_reward_ratio
    )
    
    # Execute
    order = await binance_api.create_order(
        symbol=signal.symbol,
        side=signal.side,
        type="LIMIT",
        quantity=position_size,
        price=signal.entry_price,
        stopLoss=signal.stop_loss,
        takeProfit=signal.take_profit
    )
    
    # Log
    await log_trade(agent_id, order)
    
    # Notify
    await notify_user(
        agent.user_id,
        f"Trade executed: {signal.symbol} {signal.side} @ {signal.entry_price}"
    )
    
    return order
```

#### Rule 3: Performance Tracking
```python
async def calculate_agent_performance(agent_id, period="24h"):
    """
    Performance metrics:
    - Win rate
    - Profit factor
    - Sharpe ratio
    - Maximum drawdown
    - Average trade duration
    """
    trades = await get_trades(agent_id, period)
    
    winning_trades = [t for t in trades if t.pnl > 0]
    losing_trades = [t for t in trades if t.pnl < 0]
    
    win_rate = len(winning_trades) / len(trades) if trades else 0
    
    gross_profit = sum(t.pnl for t in winning_trades)
    gross_loss = abs(sum(t.pnl for t in losing_trades))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    
    return {
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "total_trades": len(trades),
        "net_pnl": sum(t.pnl for t in trades),
        "avg_win": gross_profit / len(winning_trades) if winning_trades else 0,
        "avg_loss": gross_loss / len(losing_trades) if losing_trades else 0
    }
```

### Grandchild Spawning Logic

```python
class GrandchildSpawnCriteria:
    MIN_PROFIT = 100  # $100 USD
    MIN_WIN_RATE = 0.60  # 60%
    MIN_TRADES = 50
    MIN_PROFIT_FACTOR = 1.5
    MAX_LINEAGE_DEPTH = 3  # Max 3 generations

async def check_grandchild_eligibility(agent_id):
    """
    Check if child agent can spawn grandchild
    """
    agent = await get_agent(agent_id)
    
    # Check lineage depth
    depth = await get_lineage_depth(agent_id)
    if depth >= GrandchildSpawnCriteria.MAX_LINEAGE_DEPTH:
        return False, "Maximum lineage depth reached"
    
    # Check performance
    perf = await calculate_agent_performance(agent_id, period="all")
    
    if perf["net_pnl"] < GrandchildSpawnCriteria.MIN_PROFIT:
        return False, f"Need ${GrandchildSpawnCriteria.MIN_PROFIT} profit"
    
    if perf["win_rate"] < GrandchildSpawnCriteria.MIN_WIN_RATE:
        return False, f"Need {GrandchildSpawnCriteria.MIN_WIN_RATE*100}% win rate"
    
    if perf["total_trades"] < GrandchildSpawnCriteria.MIN_TRADES:
        return False, f"Need {GrandchildSpawnCriteria.MIN_TRADES} trades"
    
    if perf["profit_factor"] < GrandchildSpawnCriteria.MIN_PROFIT_FACTOR:
        return False, f"Need {GrandchildSpawnCriteria.MIN_PROFIT_FACTOR} profit factor"
    
    return True, "Eligible for grandchild spawning"

async def spawn_grandchild(parent_agent_id, user_approval=True):
    """
    Spawn grandchild agent
    """
    if not user_approval:
        raise ValueError("User approval required")
    
    eligible, message = await check_grandchild_eligibility(parent_agent_id)
    if not eligible:
        raise ValueError(message)
    
    parent = await get_agent(parent_agent_id)
    parent_balance = await get_balance(parent.wallet_address)
    
    # Allocate 10% of parent's capital
    grandchild_capital = parent_balance * 0.10
    
    # Create grandchild
    grandchild = await create_agent(
        user_id=parent.user_id,
        agent_type="grandchild",
        initial_capital=grandchild_capital,
        parent_id=parent_agent_id,
        risk_profile=parent.risk_profile
    )
    
    # Transfer capital
    await transfer_funds(
        from_wallet=parent.wallet_address,
        to_wallet=grandchild.wallet_address,
        amount=grandchild_capital
    )
    
    # Copy successful strategies
    strategies = await get_best_strategies(parent_agent_id)
    await apply_strategies(grandchild.id, strategies)
    
    # Notify user
    await notify_user(
        parent.user_id,
        f"Grandchild agent spawned! Capital: ${grandchild_capital}"
    )
    
    return grandchild
```

---

## 💰 REVENUE & FEE IMPLEMENTATION

### Fee Collection System

```python
class FeeStructure:
    PLATFORM_FEE = 0.02      # 2% of profits
    LINEAGE_FEE = 0.05       # 5% to parent agent
    WITHDRAWAL_FEE = 0.01    # 1% of withdrawal

async def collect_fees(agent_id, profit_amount):
    """
    Fee distribution on profit:
    1. Platform fee (2%)
    2. Lineage fee (5% if has parent)
    3. Remaining to user
    """
    agent = await get_agent(agent_id)
    
    # Platform fee
    platform_fee = profit_amount * FeeStructure.PLATFORM_FEE
    await transfer_to_platform(platform_fee)
    
    remaining = profit_amount - platform_fee
    
    # Lineage fee (if has parent)
    if agent.parent_id:
        lineage_fee = profit_amount * FeeStructure.LINEAGE_FEE
        await transfer_to_parent(agent.parent_id, lineage_fee)
        remaining -= lineage_fee
    
    # User profit
    await credit_user_balance(agent.user_id, remaining)
    
    # Log transaction
    await log_fee_distribution({
        "agent_id": agent_id,
        "profit": profit_amount,
        "platform_fee": platform_fee,
        "lineage_fee": lineage_fee if agent.parent_id else 0,
        "user_profit": remaining
    })
```

---

## 🔒 SECURITY IMPLEMENTATION

### Wallet Security

```python
from cryptography.fernet import Fernet

class WalletSecurity:
    @staticmethod
    async def encrypt_private_key(private_key: str) -> str:
        """
        Encrypt private key with AES-256
        """
        encryption_key = os.getenv("ENCRYPTION_KEY")
        f = Fernet(encryption_key)
        encrypted = f.encrypt(private_key.encode())
        return encrypted.decode()
    
    @staticmethod
    async def decrypt_private_key(encrypted_key: str) -> str:
        """
        Decrypt private key
        """
        encryption_key = os.getenv("ENCRYPTION_KEY")
        f = Fernet(encryption_key)
        decrypted = f.decrypt(encrypted_key.encode())
        return decrypted.decode()

# CRITICAL: Never log or expose private keys
# CRITICAL: Always use encrypted storage
# CRITICAL: Implement key rotation every 90 days
```

### Withdrawal Validation

```python
async def process_withdrawal(user_id, amount, destination_address):
    """
    Multi-layer withdrawal validation
    """
    # 1. Verify user identity
    user = await get_user(user_id)
    if not user.kyc_verified:
        raise ValueError("KYC verification required")
    
    # 2. Check balance
    balance = await get_user_balance(user_id)
    if balance < amount:
        raise ValueError("Insufficient balance")
    
    # 3. Check withdrawal limits
    daily_withdrawn = await get_daily_withdrawals(user_id)
    if daily_withdrawn + amount > user.daily_withdrawal_limit:
        raise ValueError("Daily withdrawal limit exceeded")
    
    # 4. Validate destination address
    if not is_valid_address(destination_address):
        raise ValueError("Invalid destination address")
    
    # 5. Check for suspicious activity
    if await is_suspicious_withdrawal(user_id, amount, destination_address):
        await flag_for_manual_review(user_id, amount)
        raise ValueError("Withdrawal flagged for review")
    
    # 6. Calculate fee
    fee = amount * FeeStructure.WITHDRAWAL_FEE
    net_amount = amount - fee
    
    # 7. Execute withdrawal
    tx_hash = await execute_withdrawal(
        user_id=user_id,
        amount=net_amount,
        destination=destination_address
    )
    
    # 8. Log transaction
    await log_withdrawal({
        "user_id": user_id,
        "amount": amount,
        "fee": fee,
        "net_amount": net_amount,
        "destination": destination_address,
        "tx_hash": tx_hash,
        "timestamp": datetime.now()
    })
    
    return tx_hash
```

---

## 📊 MONITORING & ALERTS

### Health Check System

```python
async def system_health_check():
    """
    Comprehensive system health monitoring
    """
    health = {
        "database": await check_database_connection(),
        "binance_api": await check_binance_api(),
        "conway_api": await check_conway_api(),
        "active_agents": await count_active_agents(),
        "pending_tasks": await count_pending_tasks(),
        "error_rate": await calculate_error_rate(),
        "avg_response_time": await calculate_avg_response_time()
    }
    
    # Calculate health score (0-100)
    score = calculate_health_score(health)
    
    if score < 80:
        await alert_admin("System health degraded", health)
    
    return health, score

# Run every 5 minutes
HEALTH_CHECK_INTERVAL = 300
```

---

## 🚨 EMERGENCY PROTOCOLS

### Circuit Breaker

```python
class CircuitBreaker:
    LOSS_THRESHOLD = 0.10  # 10% system-wide loss
    
    @staticmethod
    async def check_and_trigger():
        """
        Emergency stop if system-wide loss exceeds threshold
        """
        total_pnl = await calculate_system_pnl(period="1h")
        total_capital = await get_total_managed_capital()
        
        loss_percentage = abs(total_pnl) / total_capital
        
        if total_pnl < 0 and loss_percentage > CircuitBreaker.LOSS_THRESHOLD:
            await trigger_emergency_stop()
            await alert_admin(
                "EMERGENCY: Circuit breaker triggered",
                {"loss": total_pnl, "percentage": loss_percentage}
            )

async def trigger_emergency_stop():
    """
    Emergency stop procedure:
    1. Pause all trading
    2. Close open positions
    3. Lock withdrawals
    4. Notify all users
    5. Generate incident report
    """
    # Pause all agents
    await pause_all_agents()
    
    # Close positions
    await close_all_positions()
    
    # Lock withdrawals
    await set_withdrawal_lock(True)
    
    # Notify
    await broadcast_to_all_users(
        "Trading temporarily paused for system maintenance. "
        "Your funds are safe."
    )
    
    # Report
    await generate_incident_report()
```

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-26  
**Status**: Production Ready
