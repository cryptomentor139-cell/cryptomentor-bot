# 🚀 Apply Migration 006: Centralized Wallet System

## ⚡ Quick Start (Recommended)

### Option 1: Supabase SQL Editor (Easiest)

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Select your project: `xrbqnocovfymdikngaza`

2. **Open SQL Editor**
   - Click "SQL Editor" in left sidebar
   - Click "New Query"

3. **Copy & Paste Migration**
   - Open file: `migrations/006_centralized_wallet_system.sql`
   - Copy ALL content (Ctrl+A, Ctrl+C)
   - Paste into SQL Editor

4. **Run Migration**
   - Click "Run" button (or press Ctrl+Enter)
   - Wait for completion (~5-10 seconds)
   - You should see "Success. No rows returned"

5. **Verify Tables Created**
   - Click "Table Editor" in left sidebar
   - You should see new tables:
     - `pending_deposits`
     - `deposit_transactions`
     - `user_credits_balance`
     - `webhook_logs`
     - `credit_transactions`

✅ **Done!** Migration applied successfully.

---

## 📋 What This Migration Does

### New Tables Created:

1. **pending_deposits**
   - Tracks users who clicked deposit button
   - Status: waiting, deposited, expired
   - 24-hour expiry

2. **deposit_transactions**
   - All deposits to centralized wallet
   - Transaction hash, amount, network, token
   - User attribution and status tracking
   - Conway credits conversion

3. **user_credits_balance**
   - Aggregated credits per user
   - Total deposits, available credits, spent credits
   - First/last deposit tracking

4. **webhook_logs**
   - Logs all Conway Dashboard webhooks
   - Request/response data
   - Processing status and errors

5. **credit_transactions**
   - Audit log of all credit movements
   - Deposits, spending, refunds, bonuses
   - Balance before/after tracking

### Triggers & Functions:

- **update_user_credits_on_deposit()**: Auto-updates user balance when deposit is credited
- **update_updated_at_column()**: Auto-updates timestamps
- Triggers on deposit_transactions and user_credits_balance

### Views:

- **v_recent_deposits**: Recent deposits with user info
- **v_user_deposit_summary**: User deposit statistics

---

## 🔍 Verify Migration

Run this query in SQL Editor to verify:

```sql
-- Check all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'pending_deposits',
    'deposit_transactions',
    'user_credits_balance',
    'webhook_logs',
    'credit_transactions'
)
ORDER BY table_name;
```

You should see 5 rows returned.

---

## 📊 Test Queries

### Check pending deposits:
```sql
SELECT * FROM pending_deposits ORDER BY created_at DESC LIMIT 10;
```

### Check deposit transactions:
```sql
SELECT * FROM deposit_transactions ORDER BY created_at DESC LIMIT 10;
```

### Check user credits:
```sql
SELECT * FROM user_credits_balance ORDER BY total_conway_credits DESC LIMIT 10;
```

### View recent deposits:
```sql
SELECT * FROM v_recent_deposits LIMIT 10;
```

---

## ⚠️ Troubleshooting

### Error: "relation already exists"
- Tables already created, migration already applied
- Safe to ignore

### Error: "permission denied"
- Make sure you're using service_role key
- Check SUPABASE_SERVICE_KEY in .env

### Error: "syntax error"
- Make sure you copied the ENTIRE migration file
- Check for any missing characters

---

## 📞 Next Steps After Migration

1. ✅ Migration applied
2. ⏭️ Update `menu_handlers.py` for centralized wallet
3. ⏭️ Create webhook receiver endpoint
4. ⏭️ Setup Conway Dashboard webhook URL
5. ⏭️ Test deposit flow

---

## 🔗 Centralized Wallet Address

```
0x63116672bef9f26fd906cd2a57550f7a13925822
```

This is the ONE wallet where all users will deposit.
Connected to Conway Automaton Dashboard for auto-conversion.

---

**Ready?** Open Supabase SQL Editor and paste the migration! 🚀
