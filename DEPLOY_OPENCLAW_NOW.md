# 🚀 Deploy OpenClaw to Railway - NOW!

## Quick Deployment Steps

### 1. Commit Changes ✅

```bash
cd Bismillah

git add .
git commit -m "Add OpenClaw payment system with monitoring"
git push origin main
```

### 2. Run Database Migration 📊

Di Railway dashboard atau via CLI:

```bash
# Option A: Via Railway CLI
railway run psql $DATABASE_URL < migrations/012_openclaw_payment_system.sql

# Option B: Via Railway dashboard
# 1. Go to your project
# 2. Click "Data" tab
# 3. Click "Query"
# 4. Copy-paste content dari migrations/012_openclaw_payment_system.sql
# 5. Click "Run"
```

### 3. Set Environment Variables 🔐

Di Railway dashboard, tambahkan:

```env
ADMIN_WALLET_ADDRESS=0xed7342ac9c22b1495af4d63f15a7c9768a028ea8
```

(API keys lainnya sudah ada)

### 4. Restart Service 🔄

```bash
# Via CLI
railway restart

# Or via dashboard
# Click "Restart" button
```

### 5. Test Commands 🧪

Di Telegram bot:

```
/openclaw_status
→ Should show OpenClaw info

/openclaw_deposit
→ Should show deposit options

/openclaw_balance
→ Should show $0.00

/openclaw_monitor (admin only)
→ Should show dashboard
```

---

## ✅ What's Being Deployed

### New Features:

1. **Payment System**
   - `/openclaw_deposit` - Add credits
   - `/openclaw_balance` - Check balance
   - `/openclaw_history` - Transaction history

2. **Credit Management**
   - Auto 80/20 split
   - Platform fee to admin wallet
   - User balance tracking

3. **Admin Tools**
   - `/openclaw_add_credits` - Add credits to user
   - `/openclaw_check_user` - Check user stats
   - `/openclaw_list_users` - List all users
   - `/openclaw_monitor` - Dashboard

4. **Monitoring**
   - Log all chat attempts
   - Track users without credits
   - Revenue tracking

### New Database Tables:

- `openclaw_credits` - User balances
- `openclaw_transactions` - Deposits (80/20 split)
- `openclaw_usage_log` - Usage tracking
- `openclaw_pending_deposits` - Awaiting payment
- `openclaw_platform_revenue` - Admin fees (20%)
- `openclaw_chat_monitor` - All chat attempts

---

## 🎯 Expected Behavior

### For Users:

```
User: /openclaw_ask "What is Bitcoin?"
Bot: ❌ Insufficient Credits
     Use /openclaw_deposit to add credits

User: /openclaw_deposit
Bot: 💰 Choose amount: $5, $10, $20, $50, $100

User: Selects $10
Bot: Shows wallet address & 80/20 split
     Contact @BillFarr with proof

Admin: Confirms payment & adds credits
User: Can now use OpenClaw!
```

### For Admin:

```
Admin: /openclaw_monitor
Bot: Shows dashboard with stats

Admin: /openclaw_check_user 123456
Bot: Shows user balance & history

Admin: /openclaw_add_credits 123456 10.00
Bot: ✅ Credits added!

Admin: Reviews openclaw_chat_monitor table
     → Sees all users who tried without credits
     → Can add credits manually
```

---

## 📊 Revenue Flow

```
User deposits $10
    ↓
Sends to: 0xed7342ac9c22b1495af4d63f15a7c9768a028ea8
    ↓
Admin confirms
    ↓
System splits:
├─ $8 (80%) → User credits
└─ $2 (20%) → Admin wallet (already there!)
    ↓
User can use OpenClaw
Admin keeps 20% for Railway & ops
```

---

## ⚠️ Important Notes

### OpenClaw CLI:
- **NOT running on Railway** (requires Node.js + separate server)
- Payment system **WORKS** on Railway
- Users can deposit & get credits
- When they try to use: Shows "Setup Required" message
- Admin can still manage credits

### Full OpenClaw Features:
- Requires separate VPS/server
- See `OPENCLAW_RAILWAY_DEPLOYMENT.md` for details
- Optional - payment system works standalone

---

## 🔍 Verification

After deployment, check logs:

```
✅ OpenClaw CLI handlers registered (status, help, ask)
✅ OpenClaw deposit handlers registered (payment & credits)
✅ OpenClaw admin handlers registered (monitoring & management)
```

Test in Telegram:
- ✅ `/openclaw_deposit` works
- ✅ `/openclaw_balance` works
- ✅ `/openclaw_status` works
- ✅ `/openclaw_monitor` works (admin)

---

## 🚀 Deploy Now!

```bash
# 1. Commit
git add .
git commit -m "Add OpenClaw payment system"
git push

# 2. Migrate
railway run psql $DATABASE_URL < migrations/012_openclaw_payment_system.sql

# 3. Set env
# Add ADMIN_WALLET_ADDRESS in Railway dashboard

# 4. Restart
railway restart

# 5. Test
# Try commands in Telegram
```

---

**Status:** ✅ READY TO DEPLOY
**Time:** ~5 minutes
**Risk:** Low (only adds new features)
**Rollback:** Easy (just revert commit)

**GO! 🚀**
