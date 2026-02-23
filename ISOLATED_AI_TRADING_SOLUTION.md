# Solusi: Isolated AI Trading Per User

## Problem Statement

Ketika banyak user menggunakan fitur trading otomatis dengan deposit berbeda-beda:
- User A: 100 USDC
- User B: 1000 USDC  
- User C: 50 USDC

Jika mereka semua menggunakan AI utama yang sama, pembagian profit dari child agents yang di-spawn tidak akan fair.

## Solusi: Isolated AI Instance

### Arsitektur

```
AUTOMATON CONWAY (Main Pool)
    │
    ├─► User A's Isolated AI Instance
    │   ├─ Balance: 100 USDC
    │   ├─ Profit: 5% = 5 USDC
    │   └─ Child spawned when this instance earns enough
    │
    ├─► User B's Isolated AI Instance
    │   ├─ Balance: 1000 USDC
    │   ├─ Profit: 5% = 50 USDC
    │   └─ Child spawned when this instance earns enough
    │
    └─► User C's Isolated AI Instance
        ├─ Balance: 50 USDC
        ├─ Profit: 5% = 2.5 USDC
        └─ Child spawned when this instance earns enough
```

### Key Principles

1. **One AI Instance Per User**
   - Setiap user punya AI agent sendiri
   - Balance AI = deposit user
   - Profit AI = profit user (proportional)

2. **Independent Child Spawning**
   - Child agent di-spawn dari AI instance user, bukan dari pool utama
   - Threshold spawn berdasarkan earning AI instance tersebut
   - Child agent juga milik user yang sama

3. **Fair Profit Distribution**
   - User dengan deposit lebih besar → AI instance dengan balance lebih besar
   - Profit percentage sama untuk semua (misal 5%)
   - Absolute profit berbeda sesuai deposit

## Implementation Strategy

### Database Schema Addition

```sql
-- Add to automaton_agents table
ALTER TABLE automaton_agents ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);
ALTER TABLE automaton_agents ADD COLUMN IF NOT EXISTS parent_agent_id TEXT REFERENCES automaton_agents(agent_id);
ALTER TABLE automaton_agents ADD COLUMN IF NOT EXISTS generation INTEGER DEFAULT 1;
ALTER TABLE automaton_agents ADD COLUMN IF NOT EXISTS isolated_balance DECIMAL(20,8) DEFAULT 0;
```

### Agent Hierarchy

```
User A
  └─ Main AI Agent (Gen 1) - Balance: 100 USDC
      ├─ Child Agent 1 (Gen 2) - Spawned when Gen 1 earned 50 USDC
      └─ Child Agent 2 (Gen 2) - Spawned when Gen 1 earned 100 USDC

User B  
  └─ Main AI Agent (Gen 1) - Balance: 1000 USDC
      ├─ Child Agent 1 (Gen 2) - Spawned when Gen 1 earned 50 USDC
      ├─ Child Agent 2 (Gen 2) - Spawned when Gen 1 earned 100 USDC
      └─ Child Agent 3 (Gen 2) - Spawned when Gen 1 earned 150 USDC
```

### Spawn Logic

```python
# Founder AI memutuskan spawn berdasarkan:
# - Total earnings dari AI instance user
# - Tidak ada minimum, AI yang decide
# - Tapi spawn hanya untuk AI instance user tersebut

if ai_instance.total_earnings >= ai_instance.spawn_threshold:
    # Spawn child untuk user yang sama
    child_agent = spawn_child_agent(
        user_id=ai_instance.user_id,
        parent_agent_id=ai_instance.agent_id,
        generation=ai_instance.generation + 1
    )
```

## Benefits

1. **Fair Distribution**: Setiap user dapat profit sesuai depositnya
2. **Isolated Risk**: Kerugian satu user tidak affect user lain
3. **Transparent**: User bisa track AI instance mereka sendiri
4. **Scalable**: Bisa spawn child agents per user tanpa conflict

## User Experience

### User View
```
📊 Your AI Trading Status

Main AI Agent: #ABC123
├─ Balance: 100 USDC
├─ Total Earned: 15 USDC (+15%)
├─ Active Trades: 3
└─ Child Agents: 1

Child Agent #1: #DEF456
├─ Balance: 10 USDC (from parent earnings)
├─ Total Earned: 2 USDC (+20%)
└─ Active Trades: 1

Total Portfolio: 127 USDC (+27%)
```

## Migration Path

1. **Phase 1**: Add user_id to existing agents
2. **Phase 2**: Implement isolated balance tracking
3. **Phase 3**: Update spawn logic to be user-specific
4. **Phase 4**: Add UI for user to see their AI hierarchy

## Cost Structure

- **Deposit Fee**: 5% (sudah ada)
- **Performance Fee**: 20% dari profit (sudah ada)
- **AI Maintenance**: Deducted from AI instance balance
- **Child Spawn Cost**: Paid from parent AI earnings

## Next Steps

1. Create migration script for database schema
2. Update AutomatonManager to support user_id
3. Implement isolated balance tracking
4. Add child spawning logic per user
5. Create UI for user AI hierarchy view
