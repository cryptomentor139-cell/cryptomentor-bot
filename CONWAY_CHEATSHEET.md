# Conway Integration - Cheat Sheet

## 🎯 Quick Facts

- **Token:** USDC only
- **Network:** Base only
- **Tables:** 3 (simplified)
- **Env Vars:** 7 (simplified)
- **Timeline:** 1-2 weeks
- **Conway handles:** Wallets, deposits, security

## 📋 Environment Variables

```bash
TELEGRAM_BOT_TOKEN=<your_token>
SUPABASE_URL=<your_url>
SUPABASE_KEY=<your_key>
SUPABASE_SERVICE_KEY=<your_service_key>
CONWAY_API_URL=https://api.conway.tech
CONWAY_API_KEY=<your_conway_key>
ADMIN_IDS=1187119989,7255533151
```

## 🗄️ Database Tables

### user_automatons
- agent_wallet (Conway wallet)
- conway_deposit_address (for deposits)
- conway_credits (balance)
- survival_tier (normal/low/critical/dead)

### automaton_transactions
- type (spawn/deposit/earn/spend/fee)
- amount
- timestamp

### platform_revenue
- source (deposit_fee/performance_fee/spawn_fee)
- amount
- timestamp

## 🔌 Conway API Endpoints

```python
# Get deposit address
GET /api/v1/wallets/{user_id}/deposit-address

# Create agent
POST /api/v1/agents
Body: {user_id, name, genesis_prompt}

# Check balance
GET /api/v1/wallets/{agent_wallet}/balance

# Get transactions
GET /api/v1/wallets/{agent_wallet}/transactions
```

## 💰 Revenue Model

- **Deposit fee:** 2% (100 USDC → 98 USDC → 9,800 credits)
- **Performance fee:** 20% (50 USDC profit → 10 USDC fee)
- **Spawn fee:** 100,000 credits (one-time)

## 📱 User Commands

```
/spawn_agent - Create new agent
/agent_status - Check balance & tier
/deposit - Show deposit address
/agent_logs - Transaction history
```

## 🚀 Deployment Steps

1. Get Conway API key
2. Add to Railway variables
3. Run migration (002_automaton_simplified.sql)
4. Deploy bot
5. Test!

## ⚠️ Important

- ✅ USDC on Base only
- ❌ NO USDT
- ❌ NO Polygon
- ❌ NO Arbitrum

## 📚 Key Files

- `CONWAY_QUICK_DEPLOY.md` - 5-min deploy
- `CONWAY_ENV_SETUP.md` - Env setup
- `migrations/002_automaton_simplified.sql` - Migration
- `AUTOMATON_FINAL_SUMMARY.md` - Complete guide

## 🔗 Links

- Conway: https://conway.tech
- Docs: https://docs.conway.tech
- Support: support@conway.tech

---

**Version:** 2.0.0 (Simplified)
**Status:** Ready to deploy
