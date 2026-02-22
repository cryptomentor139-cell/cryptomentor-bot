# 🚀 Deploy Deposit Address Fix - NOW

## ✅ Code Already Pushed

```bash
✅ Commit: Fix: Use centralized custodial wallet for deposit address generation
✅ Pushed to: origin/main
✅ Railway will auto-deploy
```

## 🔧 Railway Configuration

### Step 1: Add Environment Variable

1. Go to Railway dashboard: https://railway.app
2. Select your project
3. Click on your service
4. Go to "Variables" tab
5. Add new variable:

```
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822
```

6. Click "Add" or "Save"
7. Railway will automatically redeploy

### Step 2: Wait for Deployment

Railway will:
1. Pull latest code from GitHub
2. Rebuild the application
3. Restart the service
4. Apply new environment variable

⏱️ This takes ~2-5 minutes

### Step 3: Verify Deployment

Check Railway logs for:
```
✅ Conway API client initialized: https://automaton-production-a899.up.railway.app
✅ Automaton Manager initialized
```

## 🧪 Test in Production

### Test 1: Check Bot is Running

Open Telegram bot and send:
```
/start
```

Expected: Bot responds with welcome message

### Test 2: Spawn Agent

Send:
```
/spawn_agent TestBot
```

Expected response:
```
✅ Agent Berhasil Dibuat!

🤖 Nama: TestBot
💼 Wallet: agent_abc123...
📍 Deposit Address:
0x63116672bef9f26fd906cd2a57550f7a13925822

⚠️ Agent belum aktif!
Deposit USDC ke address di atas untuk mengaktifkan agent.
```

### Test 3: Check Deposit Command

Send:
```
/deposit
```

Expected response:
```
💰 Deposit USDC (Base Network)

📍 Deposit Address:
0x63116672bef9f26fd906cd2a57550f7a13925822

📱 QR Code:
[QR code URL]

🌐 Network:
• Base Network (WAJIB)
...
```

## ✅ Success Criteria

- [x] Code pushed to GitHub
- [ ] Environment variable added to Railway
- [ ] Railway deployment successful
- [ ] Bot responds to /start
- [ ] /spawn_agent shows deposit address
- [ ] Deposit address = 0x63116672bef9f26fd906cd2a57550f7a13925822
- [ ] /deposit shows correct address and QR code

## 🐛 Troubleshooting

### Issue: Bot not responding

**Check:**
1. Railway logs for errors
2. Service is running (not crashed)
3. Environment variables loaded

**Solution:**
```bash
# Check Railway logs
railway logs

# Restart service if needed
railway restart
```

### Issue: Deposit address not showing

**Check:**
1. `CENTRALIZED_WALLET_ADDRESS` in Railway variables
2. Value is correct (42 chars, starts with 0x)
3. No typos in variable name

**Solution:**
1. Go to Railway Variables
2. Verify variable exists
3. Check value matches: `0x63116672bef9f26fd906cd2a57550f7a13925822`
4. Redeploy if needed

### Issue: Wrong deposit address

**Check:**
1. Environment variable value
2. Code is latest version
3. Railway pulled latest commit

**Solution:**
```bash
# Force redeploy
railway up --detach
```

## 📊 Monitoring

### Check Logs

```bash
# View Railway logs
railway logs --tail

# Look for:
✅ Conway API client initialized
✅ Automaton Manager initialized
✅ Using centralized deposit address for user [user_id]
```

### Check Database

```sql
-- Check agents created
SELECT 
    id,
    user_id,
    agent_name,
    conway_deposit_address,
    conway_credits,
    created_at
FROM user_automatons
ORDER BY created_at DESC
LIMIT 10;

-- All should have same deposit address
```

## 📝 Post-Deployment Checklist

- [ ] Railway deployment successful
- [ ] Environment variable added
- [ ] Bot responds to commands
- [ ] Deposit address generation works
- [ ] Address matches centralized wallet
- [ ] QR code displays correctly
- [ ] Documentation updated
- [ ] Team notified

## 🎯 Next Steps

### 1. Monitor First Deposits

When users start depositing:
- Check transactions on basescan.org
- Verify deposits are detected
- Confirm credits are credited
- Monitor for any issues

### 2. Setup Deposit Monitor

Ensure deposit monitor service is running:
```python
# Check if deposit monitor is active
from app.deposit_monitor import DepositMonitor

monitor = DepositMonitor(db, conway)
# Should be running in background
```

### 3. Test Withdrawal Flow

When users request withdrawals:
- Admin processes via `/withdraw` command
- Verify withdrawal from centralized wallet
- Confirm user receives funds
- Update documentation if needed

## 📚 Documentation

**For Users:**
- `CARA_DEPOSIT_USDC.md` - Deposit guide (Indonesian)

**For Developers:**
- `FIX_DEPOSIT_ADDRESS_COMPLETE.md` - Technical details
- `DEPOSIT_ADDRESS_FIX_SUMMARY.md` - Summary

**For Testing:**
- `test_deposit_address_fix.py` - Unit test
- `test_spawn_agent_flow.py` - Integration test

## 🆘 Support

If issues occur:
1. Check Railway logs
2. Review documentation
3. Test locally first
4. Check environment variables
5. Verify database state

## Summary

✅ **Code:** Pushed to GitHub
✅ **Fix:** Centralized custodial wallet
✅ **Address:** 0x63116672bef9f26fd906cd2a57550f7a13925822
✅ **Network:** Base
✅ **Token:** USDC
✅ **Tests:** All passing

**Action Required:**
1. Add `CENTRALIZED_WALLET_ADDRESS` to Railway
2. Wait for auto-deploy
3. Test in production

**Ready to go!** 🚀
