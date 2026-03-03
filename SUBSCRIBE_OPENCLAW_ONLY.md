# /subscribe Command - OpenClaw Credits Only ✅

## Status: UPDATED

`/subscribe` command sekarang fokus ke **OpenClaw Credits** saja.

---

## What Changed

### BEFORE (Old System):
- ❌ Monthly Premium (Rp 368k)
- ❌ 2 Months Premium (Rp 690k)
- ❌ 1 Year Premium (Rp 4.025k)
- ❌ Lifetime (Rp 7.475k)
- ❌ Automaton Access (Rp 2.3jt)

### NOW (New System):
- ✅ **OpenClaw Credits ONLY**
- ✅ Pay-as-you-go
- ✅ Minimum: Rp 100.000 (~$7 USD)
- ✅ No subscription needed

---

## New `/subscribe` Response

```
🤖 CryptoMentor AI 3.0 – OpenClaw Credits

🎯 NEW: OpenClaw AI Assistant
Powered by Claude Sonnet 4.5 - Your Personal AI Trading Assistant

💡 What is OpenClaw?
• 🧠 Advanced AI conversations
• 📊 Real-time crypto market analysis
• 🔍 Smart trading insights
• 💬 Natural language interface
• 🚀 Autonomous agent capabilities

💰 PRICING (Pay-as-you-go)

Credits = OpenRouter API Balance (Real-time)
Minimum Top-Up: Rp 100.000 (~$7 USD)

Recommended Amounts:
• Rp 100.000 → ~$7 credits
• Rp 200.000 → ~$14 credits
• Rp 500.000 → ~$35 credits
• Rp 1.000.000 → ~$70 credits

💳 PAYMENT METHODS

🏦 Transfer Bank (IDR)
Nama: NABIL FARREL AL FARI
Bank: Mandiri
No Rek: 1560018407074

📱 E-Money (IDR)
ShopeePay / GoPay / DANA
📞 0877-7927-4400

⛓️ Crypto (USD)
Network: BEP20 (Binance Smart Chain)
Address: 0xed7342ac9c22b1495af4d63f15a7c9768a028ea8

Supported: USDT, USDC, BNB (BEP20 only!)

✅ HOW TO TOP-UP

1️⃣ Choose amount (min. Rp 100.000)
2️⃣ Send payment via Bank/E-Money/Crypto
3️⃣ Send proof to admin: @BillFarr
4️⃣ Include this info:

✅ Amount: Rp XXX.XXX
✅ Your UID: 123456789
✅ Purpose: OpenClaw Credits

5️⃣ Credits added after verification!

📊 CHECK BALANCE
Use: /openclaw_balance

🚀 START USING
Just chat normally - OpenClaw is now default!
No commands needed, just type your question.

📌 NOTES
• Credits shared across all users
• Real-time sync with OpenRouter
• Admin manually adds credits
• No subscription needed
• Pay only for what you use

🎁 LEGACY USERS
Existing Premium/Lifetime users:
Your subscription remains active for old features.
OpenClaw is separate pay-as-you-go system.

---

💡 Quick Start:
1. Top-up credits (min. Rp 100k)
2. Start chatting with AI
3. Get trading insights instantly!

[💰 Top-Up Credits] [💳 Check Balance] [📞 Contact Admin]
```

---

## Legacy Users

### Existing Premium/Lifetime Users:
- ✅ **Tetap bisa pakai** fitur premium lama
- ✅ Subscription mereka **tidak hilang**
- ✅ OpenClaw adalah sistem **terpisah**
- ✅ Mereka bisa top-up OpenClaw jika mau

### New Users:
- ❌ **Tidak bisa** beli Premium/Lifetime lagi
- ✅ **Hanya bisa** top-up OpenClaw Credits
- ✅ Minimum Rp 100.000

---

## Minimum Top-Up: Rp 100.000

### Why Rp 100k?

**Conversion:**
- Rp 100.000 ≈ $7 USD
- $7 = ~700 credits (OpenRouter)
- Enough for ~50-100 AI conversations

**Benefits:**
- Not too small (admin effort)
- Not too big (user commitment)
- Good starting point for testing

---

## Payment Methods

### 1. Bank Transfer (IDR)
```
Nama: NABIL FARREL AL FARI
Bank: Mandiri
No Rek: 1560018407074
```

### 2. E-Money (IDR)
```
ShopeePay / GoPay / DANA
📞 0877-7927-4400
```

### 3. Crypto (USD)
```
Network: BEP20 (Binance Smart Chain)
Address: 0xed7342ac9c22b1495af4d63f15a7c9768a028ea8
Coins: USDT, USDC, BNB (BEP20 only!)
```

---

## User Flow

```
1. User: /subscribe
2. Bot: Shows OpenClaw Credits info
3. User: Clicks "💰 Top-Up Credits"
4. Bot: Shows amount options
5. User: Sends payment (min. Rp 100k)
6. User: Sends proof to @BillFarr
7. Admin: Verifies payment
8. Admin: Adds credits to OpenRouter
9. Admin: /admin_notify_credits 123456789 7
10. User: Gets notification
11. User: /openclaw_balance → See credits
12. User: Start chatting with AI!
```

---

## Admin Workflow

### When User Wants to Top-Up:

1. **User sends proof** (min. Rp 100k)
2. **Admin verifies** payment
3. **Admin adds credits** to OpenRouter
4. **Admin notifies** user: `/admin_notify_credits <user_id> <amount>`
5. **User checks** balance: `/openclaw_balance`

---

## Button Actions

### 💰 Top-Up Credits
- Callback: `deposit_start`
- Action: Show deposit amount options
- Handler: `deposit_callback_handler`

### 💳 Check Balance
- Callback: `balance_check`
- Action: Show OpenRouter balance
- Handler: Redirects to `openclaw_balance_command`

### 📞 Contact Admin
- URL: `https://t.me/BillFarr`
- Action: Open Telegram chat with admin

---

## Files Modified

1. **bot.py** - Updated `subscribe_command`
   - Removed old premium packages
   - Added OpenClaw Credits info
   - Added minimum Rp 100k
   - Added legacy user check

2. **handlers_openclaw_deposit.py** - Added `balance_check` callback
   - Redirects to balance command
   - Works from /subscribe buttons

---

## Testing

### Test 1: Subscribe Command
```
/subscribe
Expected: Show OpenClaw Credits info (not premium packages)
```

### Test 2: Top-Up Button
```
Click "💰 Top-Up Credits"
Expected: Show amount options
```

### Test 3: Check Balance Button
```
Click "💳 Check Balance"
Expected: Show OpenRouter balance
```

### Test 4: Legacy User
```
User with active premium runs /subscribe
Expected: See legacy user message + OpenClaw info
```

---

## Migration Notes

### Old Premium Users:
- ✅ Keep their subscription
- ✅ Can still use premium features
- ✅ Can optionally top-up OpenClaw

### New Users:
- ❌ Cannot buy Premium/Lifetime
- ✅ Must use OpenClaw Credits
- ✅ Minimum Rp 100k

### Database:
- No migration needed
- Old `subscription_end` field still works
- OpenClaw uses OpenRouter balance (no DB)

---

## Status

✅ `/subscribe` updated to OpenClaw only
✅ Minimum Rp 100k enforced
✅ Legacy users protected
✅ Payment methods updated
✅ Button callbacks working

**Ready to deploy!**

---

**Updated:** 2026-03-04
**System:** OpenClaw Credits Only
**Minimum:** Rp 100.000 (~$7 USD)
