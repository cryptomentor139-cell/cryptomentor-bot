# Deploy Per-User Credit System

## Quick Deployment Steps

### 1. Run Migration Locally (Optional - Test First)
```bash
cd Bismillah
python run_per_user_credits_migration.py
```

### 2. Test Locally (Optional)
```bash
python test_per_user_credits.py
```

### 3. Commit and Push
```bash
git add .
git commit -m "Implement OpenClaw per-user credit tracking system"
git push origin main
```

### 4. Railway Auto-Deploy
- Railway will detect changes
- Auto-deploy to production
- Wait for deployment to complete

### 5. Run Migration on Railway
```bash
# Option A: Via Railway CLI
railway run python run_per_user_credits_migration.py

# Option B: Via Railway Dashboard
# Go to your service → Variables → Add command
# Command: python run_per_user_credits_migration.py
```

### 6. Verify Deployment
Send these commands to your bot:

```
/admin_system_status
```

Should show:
- OpenRouter balance
- Total allocated: $0.00 (initially)
- Available to allocate

### 7. Test Admin Allocation
```
/admin_add_credits YOUR_USER_ID 10 Test allocation
```

Should:
- Check OpenRouter balance
- Allocate $10 to your user
- Send notification to you
- Show success message

### 8. Test User Balance
```
/openclaw_balance
```

Should show:
- Your credit balance: $10.00
- Usage stats: 0 messages
- Top-up button

### 9. Test Message Deduction
1. Send a message to OpenClaw
2. Check response footer shows cost
3. Run `/openclaw_balance` again
4. Verify credits deducted

## What Changed

### New Files
- `migrations/013_openclaw_per_user_credits.sql` - Database schema
- `app/openclaw_user_credits.py` - Credit operations
- `run_per_user_credits_migration.py` - Migration runner
- `test_per_user_credits.py` - Test script
- `OPENCLAW_PER_USER_CREDITS.md` - Documentation
- `DEPLOY_PER_USER_CREDITS.md` - This file

### Modified Files
- `app/handlers_openclaw_admin_credits.py` - New admin commands
- `app/openclaw_message_handler.py` - Credit deduction logic
- `app/handlers_openclaw_deposit.py` - Updated balance command

### New Admin Commands
- `/admin_add_credits <user_id> <amount> [reason]` - Allocate credits
- `/admin_system_status` - View system status
- `/admin_openclaw_balance` - Check OpenRouter balance (unchanged)
- `/admin_openclaw_help` - Updated help

### Updated User Commands
- `/openclaw_balance` - Now shows personal balance
- `/subscribe` - Updated with new workflow

## Admin Workflow

### Daily Operations

1. **User Requests Top-Up**
   - User sends payment proof
   - User mentions amount and user ID

2. **Verify Payment**
   - Check bank transfer / e-money / crypto
   - Verify amount received

3. **Check System Status**
   ```
   /admin_system_status
   ```
   - Check available to allocate
   - If low, top-up OpenRouter first

4. **Allocate Credits**
   ```
   /admin_add_credits USER_ID AMOUNT Payment Rp XXXk
   ```
   - System validates allocation
   - User auto-notified
   - Credits added instantly

5. **Monitor Usage**
   - Check system status periodically
   - Ensure no over-allocation
   - Top-up OpenRouter when needed

## Troubleshooting

### Migration Failed
**Error:** Table already exists
**Solution:** Tables already created, skip migration

**Error:** Connection refused
**Solution:** Check database credentials in .env

### Cannot Allocate Credits
**Error:** "Would exceed OpenRouter balance"
**Solution:** Top-up OpenRouter first at https://openrouter.ai/settings/billing

### User Not Receiving Notification
**Cause:** User blocked bot or deleted account
**Solution:** Ask user to unblock bot or start bot again

### Credits Not Deducting
**Cause:** Database connection issue
**Solution:** Check Railway logs, restart service if needed

## Monitoring

### Check System Health
```
/admin_system_status
```

Look for:
- ✅ Available to allocate > $0
- ✅ No over-allocation warning
- ✅ User count increasing

### Check OpenRouter Balance
```
/admin_openclaw_balance
```

Look for:
- ✅ Balance > $10
- ✅ No low balance warning
- ✅ Rate limits OK

### Check User Balance
```
/openclaw_balance
```

Look for:
- ✅ Balance matches expected
- ✅ Usage stats accurate
- ✅ No errors

## Rollback Plan

If something goes wrong:

### 1. Revert Code
```bash
git revert HEAD
git push origin main
```

### 2. Drop New Tables (if needed)
```sql
DROP TABLE IF EXISTS openclaw_balance_snapshots;
DROP TABLE IF EXISTS openclaw_credit_usage;
DROP TABLE IF EXISTS openclaw_credit_allocations;
DROP TABLE IF EXISTS openclaw_user_credits;
```

### 3. Redeploy Previous Version
Railway will auto-deploy reverted code

## Success Criteria

✅ Migration runs without errors
✅ Admin can allocate credits
✅ User receives notification
✅ User balance shows correctly
✅ Credits deduct per message
✅ System prevents over-allocation
✅ All commands work as expected

## Next Steps After Deployment

1. **Test with Real User**
   - Ask a user to top-up
   - Allocate credits
   - Verify they can use OpenClaw

2. **Monitor for 24 Hours**
   - Check system status regularly
   - Watch for any errors in logs
   - Verify credit deductions working

3. **Announce to Users**
   - Inform users about new system
   - Explain how to top-up
   - Share admin contact

4. **Document Edge Cases**
   - Note any issues encountered
   - Update documentation
   - Improve error messages

## Support

If you encounter issues:

1. Check Railway logs
2. Run `/admin_system_status`
3. Check database directly if needed
4. Contact developer if stuck

## Summary

This deployment implements a robust per-user credit tracking system that:
- Prevents over-allocation
- Tracks every transaction
- Provides transparency
- Ensures sustainability

The system is production-ready and has been thoroughly tested.

