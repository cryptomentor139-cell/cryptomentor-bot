# Cara Implementasi Isolated AI Trading System

## Ringkasan Solusi

Setiap user mendapat AI instance sendiri dengan balance terpisah. Ini memastikan:
- ✅ Profit distribution yang fair (proportional ke deposit)
- ✅ Child spawning independent per user
- ✅ Tidak ada conflict antar user
- ✅ Transparent tracking per user

## Langkah Implementasi

### Step 1: Apply Database Migration

```bash
cd Bismillah
python run_migration_008.py
```

Atau manual di Supabase:
```sql
-- Copy isi dari migrations/008_isolated_ai_instances.sql
-- Paste dan execute di Supabase SQL Editor
```

### Step 2: Update Bot Integration

Tambahkan di `bot.py` atau handler yang sesuai:

```python
from app.isolated_ai_manager import get_isolated_ai_manager

# Ketika user activate autonomous trading
async def activate_autonomous_trading(user_id: int, deposit_amount: float):
    """Activate autonomous trading for user"""
    
    # Get manager
    isolated_ai = get_isolated_ai_manager(db)
    
    # Create main AI agent for user
    agent = isolated_ai.create_user_main_agent(
        user_id=user_id,
        initial_balance=deposit_amount
    )
    
    # Update user record
    db.execute(
        "UPDATE users SET autonomous_trading_enabled = 1 WHERE id = ?",
        (user_id,)
    )
    db.commit()
    
    return agent

# Ketika AI earn profit dari trading
async def record_trading_profit(agent_id: str, profit: float, trade_info: str):
    """Record profit from AI trading"""
    
    isolated_ai = get_isolated_ai_manager(db)
    
    # Record profit
    isolated_ai.record_agent_profit(agent_id, profit, trade_info)
    
    # Check if eligible to spawn child
    eligible, suggested_balance = isolated_ai.check_spawn_eligibility(agent_id)
    
    if eligible:
        # Ask Automaton AI if it wants to spawn
        # (In reality, Automaton decides this)
        should_spawn = await ask_automaton_to_spawn(agent_id)
        
        if should_spawn:
            child = isolated_ai.spawn_child_agent(
                agent_id,
                suggested_balance,
                "Automaton AI decided to spawn based on earnings"
            )
            
            # Notify user
            await notify_user_child_spawned(agent_id, child)

# Show user their AI portfolio
async def show_ai_portfolio(user_id: int):
    """Show user's complete AI portfolio"""
    
    isolated_ai = get_isolated_ai_manager(db)
    portfolio = isolated_ai.get_user_ai_portfolio(user_id)
    
    message = f"""
📊 Your AI Trading Portfolio

💰 Total Balance: {portfolio['total_balance']:.2f} USDC
📈 Total Earnings: {portfolio['total_earnings']:.2f} USDC
🤖 Active Agents: {portfolio['agent_count']}

Agent Hierarchy:
"""
    
    for agent in portfolio['agents']:
        indent = "  " * (agent['generation'] - 1)
        message += f"\n{indent}Gen {agent['generation']}: {agent['agent_id']}"
        message += f"\n{indent}  Balance: {agent['isolated_balance']:.2f} USDC"
        message += f"\n{indent}  Earnings: {agent['total_earnings']:.2f} USDC"
        if agent['child_count'] > 0:
            message += f"\n{indent}  Children: {agent['child_count']}"
    
    return message
```

### Step 3: Integrate dengan Automaton Conway API

```python
import httpx
from app.isolated_ai_manager import get_isolated_ai_manager

async def sync_with_automaton_conway():
    """Sync local AI instances with Automaton Conway"""
    
    isolated_ai = get_isolated_ai_manager(db)
    
    # Get all active agents
    agents = db.execute(
        "SELECT agent_id, user_id, isolated_balance FROM automaton_agents WHERE status = 'active'"
    ).fetchall()
    
    for agent in agents:
        # Check status with Automaton Conway
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTOMATON_BASE_URL}/agents/{agent['agent_id']}/status",
                headers={"Authorization": f"Bearer {AUTOMATON_API_KEY}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Update local balance if changed
                if data['balance'] != agent['isolated_balance']:
                    profit = data['balance'] - agent['isolated_balance']
                    isolated_ai.record_agent_profit(
                        agent['agent_id'],
                        profit,
                        "Sync from Automaton Conway"
                    )
                
                # Check if Automaton spawned child
                if data.get('child_spawned'):
                    child_info = data['child_info']
                    isolated_ai.spawn_child_agent(
                        agent['agent_id'],
                        child_info['balance'],
                        f"Spawned by Automaton: {child_info['reason']}"
                    )
```

### Step 4: Add Menu Commands

Tambahkan di menu handler:

```python
# /ai_portfolio - Show AI portfolio
async def cmd_ai_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if user has autonomous trading enabled
    user = db.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,)).fetchone()
    
    if not user or not user['autonomous_trading_enabled']:
        await update.message.reply_text(
            "❌ You don't have autonomous trading enabled.\n"
            "Use /automaton to activate it first."
        )
        return
    
    # Show portfolio
    portfolio_msg = await show_ai_portfolio(user['id'])
    await update.message.reply_text(portfolio_msg)

# /ai_status <agent_id> - Show specific agent status
async def cmd_ai_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ai_status <agent_id>")
        return
    
    agent_id = context.args[0]
    isolated_ai = get_isolated_ai_manager(db)
    
    try:
        agent = isolated_ai.get_agent_info(agent_id)
        
        msg = f"""
🤖 AI Agent Status

ID: {agent['agent_id']}
Generation: {agent['generation']}
Balance: {agent['isolated_balance']:.2f} USDC
Total Earnings: {agent['total_earnings']:.2f} USDC
Status: {agent['status']}
Children: {agent['child_count']}
"""
        
        if agent['parent_agent_id']:
            msg += f"\nParent: {agent['parent_agent_id']}"
        
        await update.message.reply_text(msg)
        
    except ValueError as e:
        await update.message.reply_text(f"❌ {str(e)}")
```

## Testing

Jalankan test untuk verify:

```bash
cd Bismillah
python test_isolated_ai.py
```

Expected output:
```
✅ ALL TESTS PASSED!

Conclusion:
- Each user gets isolated AI instance
- Profit distribution is fair and proportional
- Child spawning works independently per user
- Multi-generation hierarchy is supported
```

## Deployment ke Railway

1. Commit changes:
```bash
git add .
git commit -m "Add isolated AI trading system"
git push origin main
```

2. Update Railway environment variables (jika perlu):
```
AUTOMATON_BASE_URL=https://api.conway.so
AUTOMATON_API_KEY=your_api_key
```

3. Railway akan auto-deploy

4. Verify migration applied:
```bash
# Check di Railway logs
# Atau manual run migration via Railway console
```

## Monitoring

### Check User Portfolio
```sql
SELECT * FROM user_ai_hierarchy WHERE user_id = 123;
```

### Check All Active Agents
```sql
SELECT 
    user_id,
    COUNT(*) as agent_count,
    SUM(isolated_balance) as total_balance,
    SUM(total_earnings) as total_earnings
FROM automaton_agents
WHERE status = 'active'
GROUP BY user_id;
```

### Check Agent Hierarchy
```sql
WITH RECURSIVE agent_tree AS (
    -- Root agents (generation 1)
    SELECT agent_id, user_id, parent_agent_id, generation, isolated_balance, 1 as level
    FROM automaton_agents
    WHERE generation = 1 AND status = 'active'
    
    UNION ALL
    
    -- Child agents
    SELECT a.agent_id, a.user_id, a.parent_agent_id, a.generation, a.isolated_balance, t.level + 1
    FROM automaton_agents a
    JOIN agent_tree t ON a.parent_agent_id = t.agent_id
    WHERE a.status = 'active'
)
SELECT * FROM agent_tree ORDER BY user_id, level, agent_id;
```

## FAQ

### Q: Apakah setiap user harus bayar fee untuk spawn child?
A: Tidak. Child di-spawn dari earnings AI instance user tersebut. Tidak ada additional fee.

### Q: Berapa minimum deposit untuk autonomous trading?
A: Sama seperti sebelumnya (misal 10 USDC). Ini jadi initial balance AI instance user.

### Q: Apakah user bisa punya lebih dari 1 main agent?
A: Tidak. Setiap user hanya punya 1 main agent (Generation 1). Child agents di-spawn otomatis oleh AI.

### Q: Bagaimana jika user withdraw?
A: Withdraw dari total portfolio balance (sum of all agent balances). Proportionally deducted dari semua agents.

### Q: Apakah child agent bisa spawn grandchild?
A: Ya! Tidak ada limit generation depth. Tapi semakin dalam, semakin kecil balance-nya.

## Next Steps

1. ✅ Database migration applied
2. ✅ Isolated AI manager implemented
3. ✅ Tests passed
4. ⏳ Integrate dengan bot handlers
5. ⏳ Integrate dengan Automaton Conway API
6. ⏳ Add UI/menu commands
7. ⏳ Deploy to Railway
8. ⏳ Monitor and optimize

## Support

Jika ada issue:
1. Check Railway logs
2. Check database dengan queries di atas
3. Run test_isolated_ai.py locally
4. Check Automaton Conway API status
