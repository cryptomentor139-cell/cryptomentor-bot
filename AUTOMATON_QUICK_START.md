# 🚀 Automaton Integration - Quick Start Guide

## TL;DR - Deploy in 10 Minutes

### 1. Generate Encryption Key (1 min)
```bash
cd Bismillah
python generate_encryption_key.py
```
Copy the key that appears.

### 2. Add to Railway (2 min)
Railway Dashboard → Variables → Add these:
```
WALLET_ENCRYPTION_KEY=<paste_key_here>
POLYGON_RPC_URL=https://polygon-rpc.com
CONWAY_API_URL=https://api.conway.tech
CONWAY_API_KEY=<your_conway_key>
```

### 3. Run Database Migration (2 min)
Supabase SQL Editor → Paste & Run:
```sql
-- Copy from: Bismillah/migrations/001_automaton_tables.sql
```

### 4. Test Everything (2 min)
```bash
python test_env.py
```
Should see all ✅ green checkmarks.

### 5. Deploy (3 min)
```bash
git add .
git commit -m "Add Automaton - Task 1"
git push
```

Done! ✅

---

## Detailed Steps

### Step 1: Generate Encryption Key

```bash
cd Bismillah
python generate_encryption_key.py
```

You'll see:
```
🔐 WALLET ENCRYPTION KEY GENERATOR
✅ Key generated successfully!
✅ Encryption test passed

📋 YOUR WALLET ENCRYPTION KEY:
WALLET_ENCRYPTION_KEY=gAAAAABl...

🔒 SECURITY INSTRUCTIONS:
1. Copy the key above and add it to Railway
2. Store backup in password manager
3. NEVER commit to git
```

**Action:** Copy the key (starts with `gAAAAAB...`)

### Step 2: Configure Railway

Go to: https://railway.app → Your Project → Variables

Click "New Variable" and add:

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `WALLET_ENCRYPTION_KEY` | `gAAAAAB...` | From step 1 |
| `POLYGON_RPC_URL` | `https://polygon-rpc.com` | Or Alchemy/Infura |
| `CONWAY_API_URL` | `https://api.conway.tech` | Conway API base |
| `CONWAY_API_KEY` | `ck_...` | From Conway dashboard |
| `POLYGON_USDT_CONTRACT` | `0xc2132D05D31c914a87C6611C10748AEb04B58e8F` | Pre-configured |
| `POLYGON_USDC_CONTRACT` | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | Pre-configured |

**Existing variables** (should already be set):
- ✅ `TELEGRAM_BOT_TOKEN`
- ✅ `SUPABASE_URL`
- ✅ `SUPABASE_KEY`
- ✅ `SUPABASE_SERVICE_KEY`
- ✅ `ADMIN_IDS`

### Step 3: Run Database Migration

1. Open Supabase: https://app.supabase.com
2. Go to: SQL Editor
3. Open file: `Bismillah/migrations/001_automaton_tables.sql`
4. Copy all content
5. Paste in SQL Editor
6. Click "Run"

**Verify:**
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%automaton%' OR table_name LIKE '%wallet%';
```

Should show:
```
custodial_wallets
wallet_deposits
wallet_withdrawals
user_automatons
automaton_transactions
platform_revenue
```

### Step 4: Test Environment

```bash
python test_env.py
```

**Expected output:**
```
🔍 CHECKING ENVIRONMENT VARIABLES
✅ TELEGRAM_BOT_TOKEN: 12345678...
✅ SUPABASE_URL: https://...
✅ SUPABASE_KEY: eyJhbG...
✅ SUPABASE_SERVICE_KEY: eyJhbG...
✅ POLYGON_RPC_URL: https://...
✅ WALLET_ENCRYPTION_KEY: gAAAAAB...
✅ CONWAY_API_URL: https://api.conway.tech
✅ CONWAY_API_KEY: ck_...
✅ ADMIN_IDS: 1187119989,7255533151

✅ All 9 required variables are set!

🔐 TESTING WALLET ENCRYPTION KEY
✅ Encryption key format is valid
✅ Encryption test passed
✅ Decryption test passed
✅ Wallet encryption key is fully functional!

📊 TEST SUMMARY
✅ Environment Variables: PASSED
✅ Encryption Key: PASSED
✅ Admin Configuration: PASSED
✅ Polygon RPC: PASSED
✅ Supabase Connection: PASSED

✅ ALL TESTS PASSED (5/5)
```

If you see ❌ errors, check:
- Railway variables are set correctly
- No typos in variable names
- Keys are valid and not expired

### Step 5: Deploy to Railway

```bash
# Stage all files
git add .

# Commit with message
git commit -m "Add Automaton integration - Task 1 complete"

# Push to trigger Railway deploy
git push origin main
```

**Monitor deployment:**
1. Go to Railway dashboard
2. Click on your service
3. Go to "Deployments" tab
4. Watch logs for:
   - ✅ "Build successful"
   - ✅ "Deployment successful"
   - ✅ "Bot started"

### Step 6: Verify Deployment

Check Railway logs for:
```
✅ Database class integrated with Supabase
✅ Bot started successfully
✅ Polling for updates...
```

**No errors should appear!**

---

## Troubleshooting

### Error: "Encryption key invalid"
**Fix:** Regenerate key with `python generate_encryption_key.py`

### Error: "RPC connection failed"
**Fix:** Use Alchemy or Infura instead of public RPC:
```
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
```

### Error: "Conway API authentication failed"
**Fix:** Check API key in Conway dashboard, regenerate if needed

### Error: "Database connection failed"
**Fix:** Verify Supabase credentials, check if database is paused

### Error: "Table already exists"
**Fix:** Tables already created, skip migration step

---

## What You Just Built

### Database Tables (6 new tables)
- ✅ `custodial_wallets` - User Ethereum wallets
- ✅ `wallet_deposits` - Deposit tracking
- ✅ `wallet_withdrawals` - Withdrawal management
- ✅ `user_automatons` - Agent records
- ✅ `automaton_transactions` - Transaction history
- ✅ `platform_revenue` - Revenue tracking

### Infrastructure
- ✅ Wallet encryption system (Fernet)
- ✅ Polygon blockchain connection
- ✅ Conway Cloud API integration
- ✅ Secure environment variables
- ✅ Database indexes for performance

### Security
- ✅ Private keys encrypted
- ✅ Master key in Railway only
- ✅ No secrets in code
- ✅ Admin access controlled

---

## Next Steps

### Task 2: Wallet Manager (Next)
Will implement:
- Wallet generation (Ethereum)
- Private key encryption
- Database persistence
- Property-based tests

**Start with:**
```bash
# Read the spec
cat .kiro/specs/automaton-integration/tasks.md

# Check Task 2 requirements
# Implement app/wallet_manager.py
```

### Checkpoint After Task 5
After Tasks 2-5, we'll verify:
- ✅ Wallet generation works
- ✅ Deposit detection works
- ✅ Conway API integration works
- ✅ All tests pass

---

## Files Created

| File | Purpose |
|------|---------|
| `migrations/001_automaton_tables.sql` | Database schema |
| `RAILWAY_ENV_SETUP.md` | Environment guide |
| `generate_encryption_key.py` | Key generator |
| `test_env.py` | Environment tester |
| `AUTOMATON_DEPLOYMENT_CHECKLIST.md` | Full checklist |
| `AUTOMATON_TASK1_COMPLETE.md` | Task 1 summary |
| `AUTOMATON_QUICK_START.md` | This guide |

---

## Support

Need help?

1. **Check logs:** Railway dashboard → Logs
2. **Test environment:** `python test_env.py`
3. **Review docs:** `RAILWAY_ENV_SETUP.md`
4. **Check database:** Supabase dashboard

---

## Success Checklist

- [ ] Encryption key generated
- [ ] Railway variables configured
- [ ] Database migration run
- [ ] All tests passing
- [ ] Bot deployed successfully
- [ ] No errors in logs
- [ ] Ready for Task 2

---

**Time to complete:** 10 minutes
**Difficulty:** Easy
**Status:** ✅ Task 1 Complete
**Next:** Task 2 - Wallet Manager

🚀 Let's build the future of autonomous AI trading!
