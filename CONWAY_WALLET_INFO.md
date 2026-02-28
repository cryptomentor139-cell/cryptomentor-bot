# Conway Automaton Wallet Information

## ⚠️ CRITICAL: Base Network Only

Conway Automaton **HANYA** menerima deposit melalui:
- **Token:** USDC
- **Network:** Base (Base Mainnet)
- **NO support untuk:** USDT, Polygon, Arbitrum, atau network lain

## Conway Wallet Address

Setiap user akan mendapatkan **deposit address** yang langsung terhubung ke Conway Automaton wallet mereka.

### Cara Kerja

1. **User spawn agent** → Platform generate unique deposit address
2. **User deposit USDC** → Ke address tersebut via Base network
3. **Conway detect deposit** → Otomatis credit ke agent wallet
4. **Agent consume credits** → Untuk trading operations

## Deposit Flow (Updated)

```
User deposits USDC → Base Network → Conway Wallet Address
                                            ↓
                                    Conway API detects
                                            ↓
                                    Credits added to agent
                                            ↓
                                    User notified via Telegram
```

## Important Notes

### ✅ Supported
- USDC on Base network
- Direct deposit to Conway wallet
- Automatic credit conversion
- Real-time balance updates

### ❌ NOT Supported
- USDT (any network)
- Polygon network
- Arbitrum network
- Ethereum mainnet
- Other ERC20 tokens

## User Instructions

When user requests deposit address, show:

```
💰 Fund Your Automaton

Deposit Address:
0x... (Conway wallet address)

⚠️ IMPORTANT:
✅ Token: USDC only
✅ Network: Base
❌ DO NOT send USDT
❌ DO NOT use Polygon/Arbitrum
❌ DO NOT send other tokens

Conversion Rate:
1 USDC = 100 Conway Credits

Minimum Deposit: 5 USDC
Platform Fee: 2%

After deposit:
- Credits appear in 1-2 minutes
- You'll receive confirmation
- Agent starts consuming credits
```

## Technical Implementation

### No Custodial Wallets Needed

Original design had custodial wallets, but with Conway's direct integration:
- ❌ No need to generate Ethereum wallets
- ❌ No need to encrypt private keys
- ❌ No need to monitor blockchain
- ✅ Conway provides deposit address
- ✅ Conway handles all blockchain operations
- ✅ We just call Conway API

### Simplified Architecture

```
User → Telegram Bot → Conway API → Agent Wallet
                         ↓
                    Deposit Address
                    Balance Check
                    Credit Transfer
```

### API Integration

```python
# Get deposit address for user
deposit_address = conway_api.get_deposit_address(user_id)

# Check balance
balance = conway_api.get_balance(agent_wallet)

# Transfer credits (if needed)
conway_api.transfer_credits(from_wallet, to_wallet, amount)
```

## Database Schema Changes

Since Conway handles wallets, we simplify:

### Remove (Not Needed)
- ❌ custodial_wallets table (Conway provides addresses)
- ❌ wallet_deposits table (Conway tracks deposits)
- ❌ wallet_withdrawals table (Conway handles withdrawals)
- ❌ Private key encryption (Conway manages keys)
- ❌ Blockchain monitoring (Conway does this)

### Keep (Still Needed)
- ✅ user_automatons table (Track user's agents)
- ✅ automaton_transactions table (Track credit usage)
- ✅ platform_revenue table (Track our fees)

## Updated Environment Variables

### Remove (Not Needed)
```bash
# ❌ No longer needed
POLYGON_RPC_URL
WALLET_ENCRYPTION_KEY
POLYGON_USDT_CONTRACT
POLYGON_USDC_CONTRACT
```

### Keep (Still Needed)
```bash
# ✅ Still required
CONWAY_API_URL=https://api.conway.tech
CONWAY_API_KEY=<your_api_key>
TELEGRAM_BOT_TOKEN=<your_token>
SUPABASE_URL=<your_url>
SUPABASE_KEY=<your_key>
ADMIN_IDS=<admin_ids>
```

## Revenue Model (Unchanged)

Platform still earns from:
- 💰 2% deposit fee (deducted before crediting)
- 💰 20% performance fee (from agent profits)
- 💰 Withdrawal fee (if applicable)

## Security Benefits

With Conway handling wallets:
- ✅ No private keys to manage
- ✅ No encryption key rotation
- ✅ No blockchain security concerns
- ✅ Conway's enterprise-grade security
- ✅ Simpler codebase
- ✅ Fewer attack vectors

## Migration Impact

### What Changes
1. Database schema simplified (3 tables instead of 6)
2. No wallet generation code needed
3. No blockchain monitoring needed
4. No encryption implementation needed
5. Simpler deployment (fewer dependencies)

### What Stays Same
1. User experience (deposit → get credits)
2. Agent spawning flow
3. Credit consumption tracking
4. Revenue collection
5. Admin dashboard

## Next Steps

1. ✅ Update database migration (remove custodial tables)
2. ✅ Update environment setup (remove blockchain vars)
3. ✅ Implement Conway API integration
4. ✅ Update deposit flow (use Conway addresses)
5. ✅ Test with Conway testnet

## Conway API Endpoints

### Get Deposit Address
```
GET /api/v1/wallets/{user_id}/deposit-address
Response: {
  "address": "0x...",
  "network": "base",
  "token": "USDC"
}
```

### Check Balance
```
GET /api/v1/wallets/{wallet_address}/balance
Response: {
  "balance": 10000,
  "currency": "conway_credits"
}
```

### Get Transaction History
```
GET /api/v1/wallets/{wallet_address}/transactions
Response: {
  "transactions": [...]
}
```

## Support

For Conway API issues:
- Documentation: https://docs.conway.tech
- Support: support@conway.tech
- Status: https://status.conway.tech

---

**Last Updated:** 2026-02-20
**Version:** 2.0.0 (Updated for Base network only)
**Status:** Ready for implementation
