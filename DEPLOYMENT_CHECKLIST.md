# Manual Deposit System - Deployment Checklist

## Pre-Deployment Checklist ✅

### Code Changes
- [x] Admin credit commands created (`app/handlers_admin_credits.py`)
- [x] Admin commands registered in `bot.py`
- [x] Deposit flow updated in `menu_handlers.py`
- [x] "Kirim Bukti Transfer" button added
- [x] Deposit guide updated with manual verification steps
- [x] Auto-detection references removed

### Documentation
- [x] `MANUAL_DEPOSIT_SYSTEM.md` - Technical reference
- [x] `DEPLOY_MANUAL_DEPOSIT.md` - Deployment guide
- [x] `ADMIN_CREDIT_GUIDE.md` - Admin usage guide
- [x] `MANUAL_DEPOSIT_COMPLETE.md` - Implementation summary
- [x] `test_manual_deposit.py` - Test suite
- [x] `DEPLOYMENT_CHECKLIST.md` - This checklist

### Testing
- [x] Code compiles without errors
- [x] Imports work correctly
- [x] Deposit flow handlers exist
- [x] Admin commands defined

## Deployment Steps

### 1. Commit Changes
```bash
cd Bismillah
git add .
git commit -m "feat: implement manual deposit verification system

- Add admin credit management commands
- Update deposit flow for manual verification  
- Add 'Send Transfer Proof' button
- Update deposit guide with manual steps
- Remove auto-detection references

Closes: Manual deposit verification requirement"

git push origin main
```

### 2. Monitor Railway Deployment
- [ ] Check Railway dashboard for deployment status
- [ ] Wait for build to complete
- [ ] Check deployment logs

### 3. Verify Bot Startup
Look for these messages in Railway logs:
- [ ] `✅ Bot initialized`
- [ ] `✅ Admin credits handlers registered`
- [ ] `✅ Application handlers registered successfully`

## Post-Deployment Testing

### Test 1: Admin Commands Registration
**Expected**: Commands should be available

```bash
# In Telegram as admin:
/admin_add_credits
```

**Expected Response**: Format instructions

**Status**: [ ] Pass [ ] Fail

---

### Test 2: Check Credits Command
**Expected**: Should show user info and credits

```bash
# In Telegram as admin:
/admin_check_credits YOUR_USER_ID
```

**Expected Response**: User info with credit balance

**Status**: [ ] Pass [ ] Fail

---

### Test 3: Add Credits Command
**Expected**: Should add credits and notify user

```bash
# In Telegram as admin:
/admin_add_credits YOUR_USER_ID 3000 Test deposit
```

**Expected Response**: 
- Admin sees success message
- User receives notification

**Status**: [ ] Pass [ ] Fail

---

### Test 4: User Deposit Flow
**Expected**: User sees deposit instructions

```bash
# In Telegram as regular user:
1. Go to main menu
2. Click "🤖 AI Agent"
3. Click "💰 Deposit Sekarang"
```

**Expected**:
- [ ] Wallet address shown
- [ ] QR code link shown
- [ ] "📤 Kirim Bukti Transfer" button visible
- [ ] "❓ Cara Deposit" button visible

**Status**: [ ] Pass [ ] Fail

---

### Test 5: Send Proof Button
**Expected**: Opens chat with admin

```bash
# In Telegram as regular user:
1. In deposit screen
2. Click "📤 Kirim Bukti Transfer ke Admin"
```

**Expected**: Opens Telegram chat with admin

**Status**: [ ] Pass [ ] Fail

---

### Test 6: Deposit Guide
**Expected**: Shows manual verification instructions

```bash
# In Telegram as regular user:
1. In deposit screen
2. Click "❓ Cara Deposit"
```

**Expected**:
- [ ] Shows manual verification steps
- [ ] Mentions sending proof to admin
- [ ] Shows User ID in instructions
- [ ] Shows $30 minimum requirement

**Status**: [ ] Pass [ ] Fail

---

### Test 7: User Notification
**Expected**: User receives notification when credits added

```bash
# As admin:
/admin_add_credits USER_ID 3000 Test notification

# As user:
# Check for notification message
```

**Expected**: User receives message with:
- [ ] Credits added amount
- [ ] New balance
- [ ] Note from admin
- [ ] Instructions to spawn agent

**Status**: [ ] Pass [ ] Fail

---

### Test 8: Credit Balance Check
**Expected**: User can check their balance

```bash
# In Telegram as user:
/balance
```

**Expected**: Shows credit balance

**Status**: [ ] Pass [ ] Fail

---

### Test 9: Spawn Agent with Credits
**Expected**: User can spawn agent after $30 deposit

```bash
# As admin, add $30 worth of credits:
/admin_add_credits USER_ID 3000 Test spawn

# As user:
/spawn_agent TestBot
```

**Expected**: 
- [ ] Agent spawns successfully
- [ ] No "minimum deposit" error

**Status**: [ ] Pass [ ] Fail

---

### Test 10: Database Logging
**Expected**: Transactions are logged

```bash
# Check Supabase:
1. Go to Supabase dashboard
2. Open credit_transactions table
3. Look for recent entries
```

**Expected**:
- [ ] Transaction logged
- [ ] Admin ID recorded
- [ ] Amount correct
- [ ] Description included

**Status**: [ ] Pass [ ] Fail

---

## Rollback Plan

If critical issues found:

### Option 1: Quick Fix
```bash
# Fix the issue
git add .
git commit -m "fix: [description]"
git push origin main
```

### Option 2: Revert
```bash
# Revert to previous commit
git revert HEAD
git push origin main
```

### Option 3: Full Rollback
```bash
# Reset to previous working commit
git reset --hard <previous-commit-hash>
git push origin main --force
```

## Success Criteria

All tests must pass:
- [ ] Admin commands work
- [ ] User deposit flow works
- [ ] "Send Proof" button works
- [ ] Deposit guide shows correct info
- [ ] User notifications work
- [ ] Credits are tracked in database
- [ ] Users can spawn agent after deposit

## Known Issues

None currently. Document any issues found during testing:

1. Issue: 
   - Description:
   - Severity: [ ] Critical [ ] High [ ] Medium [ ] Low
   - Workaround:
   - Fix:

## Support Contacts

- **Admin**: Check ADMIN_IDS in Railway environment
- **Database**: Supabase dashboard
- **Logs**: Railway deployment logs
- **Code**: GitHub repository

## Post-Deployment Tasks

After successful deployment:

- [ ] Update users about new deposit process
- [ ] Monitor for deposit requests
- [ ] Respond to deposit proofs within 1 hour
- [ ] Keep transaction records
- [ ] Monitor Railway logs for errors

## Monitoring

### Daily Checks:
- [ ] Check Railway logs for errors
- [ ] Check for pending deposit requests
- [ ] Verify bot is responding
- [ ] Check database connection

### Weekly Checks:
- [ ] Review credit transactions
- [ ] Check for unusual patterns
- [ ] Verify all deposits processed
- [ ] Update documentation if needed

## Documentation Links

- Technical Reference: `MANUAL_DEPOSIT_SYSTEM.md`
- Admin Guide: `ADMIN_CREDIT_GUIDE.md`
- Deployment Guide: `DEPLOY_MANUAL_DEPOSIT.md`
- Implementation Summary: `MANUAL_DEPOSIT_COMPLETE.md`

## Notes

Add any additional notes during deployment:

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Railway Deployment ID**: _____________
**Status**: [ ] Success [ ] Failed [ ] Rolled Back

---

## Final Sign-Off

- [ ] All pre-deployment checks passed
- [ ] Code deployed successfully
- [ ] All post-deployment tests passed
- [ ] Documentation updated
- [ ] Team notified
- [ ] Monitoring in place

**Signed**: _____________
**Date**: _____________
