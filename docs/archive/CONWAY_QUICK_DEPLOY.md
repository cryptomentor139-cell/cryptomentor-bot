# 🚀 Conway Integration - Quick Deploy (5 Minutes)

## TL;DR - Simplified Architecture

Conway handles wallets → We just call API → Much simpler!

## Step 1: Get Conway API Key (2 min)

1. Go to https://conway.tech
2. Sign up / Login
3. Dashboard → API Keys → Create New
4. Copy the key (save it!)

## Step 2: Add to Railway (1 min)

Railway Dashboard → Variables → Add:

```bash
CONWAY_API_URL=https://api.conway.tech
CONWAY_API_KEY=<paste_your_key_here>
```

**Existing variables** (should already be set):
- ✅ TELEGRAM_BOT_TOKEN
- ✅ SUPABASE_URL
- ✅ SUPABASE_KEY
- ✅ SUPABASE_SERVICE_KEY
- ✅ ADMIN_IDS

## Step 3: Run Database Migration (1 min)

Supabase SQL Editor → Run:
```sql
-- Copy from: Bismillah/migrations/002_automaton_simplified.sql
```

Creates 3 tables:
- user_automatons
- automaton_transactions
- platform_revenue

## Step 4: Test Conway API (1 min)

```bash
curl -H "Authorization: Bearer YOUR_KEY" \
  https://api.conway.tech/api/v1/health
```

Should return: `{"status":"ok"}`

## Step 5: Deploy (30 sec)

```bash
git add .
git commit -m "Add Conway integration"
git push
```

Done! ✅

---

## What's Different?

### ❌ Removed (Conway handles these)
- Custodial wallets
- Private key encryption
- Blockchain monitoring
- Multi-network support
- USDT support

### ✅ Simplified
- 3 tables instead of 6
- 7 env vars instead of 12
- No blockchain code
- No encryption code
- Just API calls

## User Flow

```
1. User: /spawn_agent
   → Bot calls Conway API
   → Conway creates agent + deposit address
   → Bot shows: "Deposit USDC to: 0x... (Base network)"

2. User deposits USDC
   → Conway detects automatically
   → Conway credits agent
   → Bot notifies user

3. User: /agent_status
   → Bot calls Conway API
   → Shows balance + tier
```

## Important Notes

### ⚠️ Base Network Only
- Token: USDC only
- Network: Base only
- NO Polygon, NO Arbitrum, NO USDT

### ✅ Conway Handles
- Wallet generation
- Deposit detection
- Balance tracking
- Transaction history
- Security

### ✅ We Handle
- User interface (Telegram)
- Agent spawning flow
- Revenue tracking
- Notifications

## Environment Variables

### Required (7 total)
```bash
TELEGRAM_BOT_TOKEN=<your_token>
SUPABASE_URL=<your_url>
SUPABASE_KEY=<your_key>
SUPABASE_SERVICE_KEY=<your_service_key>
CONWAY_API_URL=https://api.conway.tech
CONWAY_API_KEY=<your_conway_key>
ADMIN_IDS=1187119989,7255533151
```

### Not Needed Anymore
```bash
# ❌ Removed
POLYGON_RPC_URL
WALLET_ENCRYPTION_KEY
POLYGON_USDT_CONTRACT
POLYGON_USDC_CONTRACT
```

## Database Tables

### user_automatons
```sql
- id (UUID)
- user_id (BIGINT)
- agent_wallet (TEXT) - Conway wallet
- agent_name (TEXT)
- conway_deposit_address (TEXT) - For deposits
- conway_credits (DECIMAL)
- survival_tier (TEXT)
- status (TEXT)
```

### automaton_transactions
```sql
- id (UUID)
- automaton_id (UUID)
- type (TEXT) - spawn/deposit/earn/spend/fee
- amount (DECIMAL)
- description (TEXT)
- timestamp (TIMESTAMP)
```

### platform_revenue
```sql
- id (UUID)
- source (TEXT) - deposit_fee/performance_fee/spawn_fee
- amount (DECIMAL)
- agent_id (UUID)
- user_id (BIGINT)
- timestamp (TIMESTAMP)
```

## Conway API Endpoints

### Get Deposit Address
```
GET /api/v1/wallets/{user_id}/deposit-address
→ Returns Base network USDC address
```

### Create Agent
```
POST /api/v1/agents
Body: {user_id, name, genesis_prompt}
→ Returns agent_wallet + deposit_address
```

### Check Balance
```
GET /api/v1/wallets/{agent_wallet}/balance
→ Returns current Conway credits
```

### Get Transactions
```
GET /api/v1/wallets/{agent_wallet}/transactions
→ Returns transaction history
```

## Testing

```bash
# Test environment
python test_conway_env.py

# Should show:
✅ All 7 variables set
✅ Conway API connection successful
```

## Troubleshooting

### Error: "Conway API authentication failed"
**Fix:** Check API key in Railway variables

### Error: "Invalid network"
**Fix:** User must use Base network, not Polygon

### Error: "Token not supported"
**Fix:** User must send USDC, not USDT

## Next Steps

After deployment:
1. Test agent spawning
2. Test deposit address generation
3. Test balance checking
4. Monitor Conway API logs
5. Ready for users!

## Benefits

- ✅ 50% faster development
- ✅ 50% less code
- ✅ Better security
- ✅ Better reliability
- ✅ Lower costs
- ✅ Same UX

## Support

- Conway API: support@conway.tech
- Documentation: https://docs.conway.tech
- Status: https://status.conway.tech

---

**Time to deploy:** 5 minutes
**Complexity:** Low
**Status:** Ready to go!

🚀 Let's ship it!
