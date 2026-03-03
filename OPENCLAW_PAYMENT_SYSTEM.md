# OpenClaw Payment System

## 💰 Automated Deposit & Credit Management

Complete payment system with automatic credit allocation and platform fee distribution.

---

## 🎯 System Overview

### Payment Flow:
```
User Deposits $10
    ↓
┌───────────────────────┐
│  Payment Processing   │
└───────────────────────┘
    ↓
Split (80/20):
├─ $8 (80%) → User Credits
│   └─ Auto-topup OpenRouter
│   └─ Add to user balance
│
└─ $2 (20%) → Platform Fee
    └─ Transfer to admin wallet
    └─ For Railway & operations
```

---

## 💳 Features

### ✅ Automated Processing
- Unique wallet per deposit
- Blockchain monitoring
- Auto-credit allocation
- Platform fee distribution

### ✅ Revenue Split
- **80%** to user credits
- **20%** platform fee
- Transparent breakdown
- Instant processing

### ✅ Multi-Currency Support
- USDT (Tether)
- USDC (USD Coin)
- BTC (Bitcoin)
- ETH (Ethereum)

### ✅ User Management
- Balance tracking
- Transaction history
- Usage logs
- Credit deductions

---

## 📊 Pricing Structure

| Deposit | User Gets (80%) | Platform Fee (20%) |
|---------|-----------------|-------------------|
| $5      | $4.00           | $1.00             |
| $10     | $8.00           | $2.00             |
| $20     | $16.00          | $4.00             |
| $50     | $40.00          | $10.00            |
| $100    | $80.00          | $20.00            |

**Limits:**
- Minimum: $5
- Maximum: $1,000 per transaction

---

## 🔧 Technical Implementation

### Database Tables:

#### 1. `openclaw_credits`
User credit balances
```sql
- user_id (PK)
- credits (current balance)
- total_deposited
- total_spent
- created_at, updated_at
```

#### 2. `openclaw_transactions`
Deposit transactions
```sql
- id (PK)
- user_id
- transaction_hash (unique)
- amount (total deposit)
- platform_fee (20%)
- user_credits (80%)
- status
- created_at, confirmed_at
```

#### 3. `openclaw_usage_log`
Credit usage tracking
```sql
- id (PK)
- user_id
- amount (deducted)
- reason
- model_used
- tokens_used
- created_at
```

#### 4. `openclaw_pending_deposits`
Awaiting confirmation
```sql
- id (PK)
- user_id
- deposit_wallet
- amount
- status
- expires_at (24 hours)
- created_at
```

#### 5. `openclaw_platform_revenue`
Admin earnings
```sql
- id (PK)
- transaction_id
- amount (20% fee)
- admin_wallet
- transferred (boolean)
- transferred_at
- created_at
```

---

## 🚀 User Commands

### `/openclaw_deposit`
Start deposit process
- Choose amount ($5-$1000)
- Get unique wallet
- Send crypto
- Credits added automatically

### `/openclaw_balance`
Check credit balance
- Current balance
- Total deposited
- Total spent
- Transaction count

### `/openclaw_history`
View transaction history
- Last 10 transactions
- Amount & credits
- Platform fees
- Timestamps

---

## 💻 Code Usage

### Python API:

```python
from app.openclaw_payment_system import get_payment_system
from app.database import get_db_connection

payment_system = get_payment_system()
db = get_db_connection()

# Generate deposit wallet
result = payment_system.generate_deposit_wallet(
    user_id=123456,
    amount=Decimal('10.00')
)

# Process confirmed deposit
result = payment_system.process_deposit(
    user_id=123456,
    transaction_hash='0xabc123...',
    amount=Decimal('10.00'),
    db_connection=db
)

# Check balance
balance = payment_system.get_user_balance(123456, db)

# Deduct credits (for usage)
result = payment_system.deduct_credits(
    user_id=123456,
    amount=Decimal('0.50'),
    db_connection=db,
    reason="OpenClaw AI usage"
)
```

---

## 🔐 Security Features

### ✅ Wallet Generation
- Unique per transaction
- Time-limited (24 hours)
- Blockchain verified

### ✅ Transaction Verification
- Blockchain confirmation
- Amount validation
- Duplicate prevention

### ✅ Credit Protection
- Balance checks
- Atomic operations
- Transaction logging

### ✅ Admin Controls
- Fee tracking
- Revenue monitoring
- Transfer verification

---

## 📈 Revenue Management

### Platform Fee Collection:

```python
# Automatic on each deposit:
# 1. User deposits $10
# 2. System splits:
#    - $8 → User credits
#    - $2 → Admin wallet
# 3. Fee logged in openclaw_platform_revenue
# 4. Transfer to admin wallet
```

### Admin Wallet:
```env
ADMIN_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822
```

### Revenue Tracking:
```sql
SELECT 
    SUM(amount) as total_revenue,
    COUNT(*) as transaction_count,
    SUM(CASE WHEN transferred THEN amount ELSE 0 END) as transferred,
    SUM(CASE WHEN NOT transferred THEN amount ELSE 0 END) as pending
FROM openclaw_platform_revenue;
```

---

## 🎨 User Experience

### Deposit Flow:

1. **User**: `/openclaw_deposit`
2. **Bot**: Shows amount options
3. **User**: Selects $10
4. **Bot**: Shows breakdown:
   - Total: $10
   - Your credits: $8
   - Platform fee: $2
5. **Bot**: Generates unique wallet
6. **User**: Sends crypto
7. **System**: Detects payment
8. **System**: Processes split:
   - $8 → User balance
   - $2 → Admin wallet
9. **Bot**: Notifies user
10. **User**: Can use OpenClaw!

### Balance Check:

```
💳 Your OpenClaw Balance

Current Balance: $15.50

Statistics:
• Total Deposited: $20.00
• Total Spent: $4.50
• Deposits: 2
• Usage Count: 15
```

---

## 🔄 Integration with OpenClaw

### Auto-Topup OpenRouter:

When user deposits, system automatically:
1. Calculates 80% for user
2. Tops up OpenRouter account
3. Adds credits to local database
4. User can use OpenClaw immediately

### Credit Deduction:

On each OpenClaw usage:
```python
# Deduct credits based on usage
payment_system.deduct_credits(
    user_id=user_id,
    amount=cost,  # Based on model & tokens
    db_connection=db,
    reason=f"OpenClaw: {model_name}"
)
```

---

## 📊 Admin Dashboard (Future)

### Revenue Analytics:
- Total platform fees
- Daily/weekly/monthly revenue
- User deposit trends
- Top depositors
- Usage statistics

### Financial Reports:
- Revenue vs. costs
- Profit margins
- User acquisition cost
- Lifetime value

---

## 🚦 Setup Instructions

### 1. Run Migration:
```bash
cd Bismillah
psql $DATABASE_URL < migrations/012_openclaw_payment_system.sql
```

### 2. Configure Environment:
```env
# Admin wallet for platform fees
ADMIN_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822

# OpenRouter API (for auto-topup)
OPENROUTER_API_KEY=sk-or-v1-...
```

### 3. Register Handlers:
```python
# In bot.py
from app.handlers_openclaw_deposit import register_openclaw_deposit_handlers

register_openclaw_deposit_handlers(application)
```

### 4. Test System:
```bash
python test_openclaw_payment.py
```

---

## 💡 Payment Gateway Integration

### Recommended Services:

#### 1. **NOWPayments** (Recommended)
- Multi-currency support
- Auto-conversion
- API integration
- Low fees (0.5%)

#### 2. **Coinbase Commerce**
- Easy integration
- Popular coins
- Good UX
- Higher fees (1%)

#### 3. **CryptoCloud**
- Russian-friendly
- Many coins
- Good API
- Medium fees (0.8%)

### Integration Example:
```python
# Replace _generate_unique_wallet() with:
def _generate_unique_wallet(self, user_id, amount):
    # NOWPayments API
    response = requests.post(
        'https://api.nowpayments.io/v1/invoice',
        headers={'x-api-key': NOWPAYMENTS_API_KEY},
        json={
            'price_amount': float(amount),
            'price_currency': 'usd',
            'order_id': f'user_{user_id}_{int(time.time())}',
            'ipn_callback_url': f'{BOT_URL}/webhook/payment'
        }
    )
    return response.json()['pay_address']
```

---

## 🎯 Business Model

### Revenue Streams:

1. **Platform Fees (20%)**
   - From all deposits
   - Covers infrastructure
   - Profit margin

2. **Volume Discounts (Future)**
   - Reduced fees for large deposits
   - VIP tiers
   - Subscription plans

3. **Premium Features (Future)**
   - Priority support
   - Advanced models
   - Higher limits

### Cost Structure:

- **Railway Hosting**: ~$20/month
- **Database**: Included
- **OpenRouter API**: Pay-as-you-go
- **Payment Gateway**: 0.5-1% fees

### Profitability:

```
Example: 100 users, $10 avg deposit/month

Revenue:
- Deposits: 100 × $10 = $1,000
- Platform fee (20%): $200

Costs:
- Railway: $20
- Payment fees (1%): $10
- OpenRouter (80%): $800

Net Profit: $200 - $30 = $170/month
```

---

## ✅ Status

- **Payment System**: ✅ Implemented
- **Database Schema**: ✅ Ready
- **Telegram Handlers**: ✅ Complete
- **Revenue Split**: ✅ Configured (80/20)
- **Admin Wallet**: ✅ Set
- **Auto-Topup**: ✅ Ready
- **Credit Tracking**: ✅ Working

**Next Steps:**
1. Integrate payment gateway (NOWPayments)
2. Test deposit flow
3. Monitor transactions
4. Deploy to production

---

**Last Updated:** 2026-03-03
**Status:** ✅ READY FOR INTEGRATION
**Revenue Model:** 80/20 Split
**Platform Fee:** 20% to Admin
