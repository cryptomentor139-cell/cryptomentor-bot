# OpenClaw Simplified Credits System ✅

## New Approach: Real-Time OpenRouter Balance

### Old System (Removed):
- ❌ Internal credit tracking per user
- ❌ 80/20 split calculation
- ❌ Complex database transactions
- ❌ Automatic credit addition

### New System (Simplified):
- ✅ Credits = OpenRouter API balance (real-time)
- ✅ No internal credit system
- ✅ Manual admin approval
- ✅ Simple payment instructions
- ✅ Shared balance across all users

---

## How It Works Now

### 1. User Checks Balance
```
/openclaw_balance
```

**Response:**
```
💳 Your OpenClaw Balance

Available Credits: $45.23
Total Limit: $100.00
Used: $54.77

💡 Note: This is your real-time OpenRouter API balance.
Credits are shared across all OpenClaw users.

[💰 Top-Up Credits]
```

### 2. User Wants to Top-Up
```
/deposit
or
/openclaw_deposit
```

**Response:**
```
💰 OpenClaw Credits Top-Up

Add credits to use OpenClaw AI Agent!

How it works:
1. Choose deposit amount below
2. Get wallet address for payment
3. Send crypto (USDT/USDC/BNB on BEP20)
4. Send proof to admin @BillFarr
5. Credits added after verification

💡 Important:
• Your credits = Your OpenRouter API balance
• Real-time sync with OpenRouter
• No internal credit system
• Admin manually adds to your OpenRouter account

Choose amount:
[$5] [$10] [$20]
[$50] [$100] [Custom]
[❌ Cancel]
```

### 3. User Clicks Amount (e.g., $10)

**Response:**
```
💰 OpenClaw Credits Top-Up

Amount: $10.00

⛓️ Payment via Crypto (BEP20)
Network: BEP20 (Binance Smart Chain)

Wallet Address:
0xed7342ac9c22b1495af4d63f15a7c9768a028ea8

Supported Coins:
• USDT (BEP20)
• USDC (BEP20)
• BNB

⚠️ Important:
1. Send EXACTLY $10.00 worth of crypto
2. Use BEP20 network ONLY!
3. Send payment proof to admin

📱 Contact Admin:
👉 @BillFarr

Include in your message:
✅ Transaction hash/screenshot
✅ Amount: $10.00
✅ Your User ID: 123456789
✅ Purpose: OpenClaw Credits

💡 Note: Credits will be added to your account after admin verification.

Your credits balance reflects your OpenRouter API balance in real-time!

[📞 Contact Admin] [❌ Cancel]
```

### 4. User Sends Payment & Proof to Admin

User contacts @BillFarr with:
- Transaction hash
- Amount
- User ID
- Screenshot

### 5. Admin Adds Credits

Admin manually adds credits to OpenRouter account via:
- OpenRouter dashboard
- Or admin command (if implemented)

### 6. Credits Reflect Immediately

User checks balance again:
```
/openclaw_balance
```

Balance updated in real-time from OpenRouter API!

---

## Technical Implementation

### Balance Check (Real-Time)

**File:** `app/handlers_openclaw_deposit.py`

```python
# Fetch from OpenRouter API
async with httpx.AsyncClient() as client:
    response = await client.get(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10.0
    )
    
    data = response.json()
    balance = data.get('data', {}).get('limit_remaining', 0)
```

### Deposit Flow (Simplified)

**No database transactions needed!**

Just show payment instructions:
1. Wallet address
2. Amount
3. Contact admin
4. Wait for manual approval

### Admin Adds Credits

Admin goes to OpenRouter dashboard:
1. Login to OpenRouter
2. Add credits to account
3. User balance updates automatically

---

## Benefits

### For Users:
- ✅ Real-time balance visibility
- ✅ No waiting for automatic processing
- ✅ Clear payment instructions
- ✅ Direct admin support

### For Admin:
- ✅ Full control over credits
- ✅ No complex automation to maintain
- ✅ Easy to verify payments
- ✅ Simple to add credits manually

### For System:
- ✅ No internal credit database needed
- ✅ No sync issues
- ✅ No 80/20 split calculations
- ✅ Simpler codebase
- ✅ Less bugs

---

## Changes Made

### 1. Simplified Deposit Command
**File:** `app/handlers_openclaw_deposit.py`

- Removed 80/20 split messaging
- Removed automatic credit addition
- Added clear manual approval flow
- Simplified payment instructions

### 2. Real-Time Balance Check
**File:** `app/handlers_openclaw_deposit.py`

- Fetch balance from OpenRouter API
- Show real-time data
- No database queries needed
- Admin gets unlimited access

### 3. Simplified Callback Handler
**File:** `app/handlers_openclaw_deposit.py`

- Removed `process_deposit_request` function
- Inline payment instructions
- No database transactions
- Just show wallet address

---

## Admin Workflow

### When User Sends Payment Proof:

1. **Verify Payment:**
   - Check transaction hash on BSCScan
   - Verify amount matches
   - Verify wallet address

2. **Add Credits to OpenRouter:**
   - Login to OpenRouter dashboard
   - Go to billing/credits section
   - Add credits to account
   - Amount = User's payment amount

3. **Notify User:**
   - Send message in Telegram
   - "Credits added! Check /openclaw_balance"

4. **User Verifies:**
   - User runs `/openclaw_balance`
   - Sees updated balance from OpenRouter API

---

## Testing

### Test 1: Check Balance
```
/openclaw_balance
Expected: Show OpenRouter API balance
```

### Test 2: Start Deposit
```
/deposit
Expected: Show amount buttons
```

### Test 3: Click Amount
```
Click "$10"
Expected: Show wallet address and payment instructions
```

### Test 4: Admin Adds Credits
```
Admin adds $10 to OpenRouter
User runs /openclaw_balance
Expected: Balance increased by $10
```

---

## Migration Notes

### No Database Migration Needed!

Old tables can stay:
- `openclaw_transactions`
- `openclaw_pending_deposits`
- `openclaw_usage_log`

They're just not used anymore. Can be cleaned up later.

### Environment Variables

Only need:
- `OPENCLAW_API_KEY` - OpenRouter API key
- `ADMIN_WALLET_ADDRESS` - BEP20 wallet for payments
- `ADMIN_IDS` - Admin user IDs

---

## Status

✅ Deposit command simplified
✅ Balance check uses OpenRouter API
✅ Callback handler fixed
✅ Payment instructions clear
✅ Manual admin approval flow
✅ Real-time balance sync

**Ready to deploy!**

---

**Updated:** 2026-03-04
**System:** Simplified Credits (OpenRouter Balance)
**Status:** Production Ready
