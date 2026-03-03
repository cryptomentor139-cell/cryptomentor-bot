# Automaton Access Fee - Deployment Checklist

## Pre-Deployment (Local Testing) ✅

- [x] Database migration created (`003_add_automaton_access.sql`)
- [x] Migration tested locally (41 lifetime users got access)
- [x] Database methods implemented (`has_automaton_access`, `grant_automaton_access`)
- [x] Automaton Manager updated with access check
- [x] Subscribe command updated with pricing
- [x] Test suite created and passing
- [x] Admin tool created (`grant_automaton_access.py`)
- [x] Documentation complete

## Deployment Steps

### 1. Backup Database (CRITICAL)
```bash
# Backup Supabase database before migration
# Use Supabase dashboard: Database > Backups > Create backup
```

### 2. Run Supabase Migration
Open Supabase SQL Editor and run:

```sql
-- Add automaton_access column
ALTER TABLE users ADD COLUMN IF NOT EXISTS automaton_access BOOLEAN DEFAULT FALSE;

-- Grant access to existing lifetime users
UPDATE users 
SET automaton_access = TRUE 
WHERE subscription_end IS NULL AND is_premium = TRUE;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_users_automaton_access ON users(automaton_access);

-- Verify migration
SELECT 
    COUNT(*) FILTER (WHERE automaton_access = TRUE) as with_access,
    COUNT(*) FILTER (WHERE is_premium = TRUE AND automaton_access = FALSE) as premium_without_access,
    COUNT(*) FILTER (WHERE is_premium = TRUE AND subscription_end IS NULL) as lifetime_users
FROM users;
```

Expected results:
- `with_access`: Should match number of lifetime users (~41)
- `premium_without_access`: Should be ~9
- `lifetime_users`: Should be ~41

### 3. Deploy Code to Railway

#### Option A: Git Push (Recommended)
```bash
cd Bismillah
git add .
git commit -m "feat: Add Automaton access fee (Rp2,000,000)"
git push origin main
```

Railway will auto-deploy.

#### Option B: Manual Deploy
1. Go to Railway dashboard
2. Select your project
3. Click "Deploy"
4. Wait for deployment to complete

### 4. Verify Deployment

#### Test 1: Check Database
```python
# Run on Railway console or locally with production DB
from database import Database
db = Database()

# Check migration
db.cursor.execute("SELECT COUNT(*) FROM users WHERE automaton_access = 1")
print(f"Users with access: {db.cursor.fetchone()[0]}")
```

#### Test 2: Test Subscribe Command
1. Send `/subscribe` to bot
2. Verify "🤖 AUTOMATON ACCESS" section appears
3. Verify pricing shows Rp2,000,000

#### Test 3: Test Access Control (Lifetime User)
1. Use a lifetime user account
2. Try to spawn agent
3. Should work without issues

#### Test 4: Test Access Control (Regular Premium)
1. Use a regular premium user account
2. Try to spawn agent
3. Should get error: "Automaton access required. Pay Rp2,000,000 one-time fee via /subscribe"

#### Test 5: Test Grant Access
```bash
# On Railway or locally
python grant_automaton_access.py list
python grant_automaton_access.py check <user_id>
```

### 5. Monitor for Issues

Check Railway logs for:
- Database connection errors
- Migration errors
- Access check errors

```bash
# Watch logs
railway logs --follow
```

### 6. Announce to Users

Send broadcast message:
```
🚀 NEW FEATURE: Automaton AI Trading Agents!

Spawn autonomous trading agents that trade 24/7 on your behalf.

💎 Access Requirements:
✅ Premium subscription (any tier)
✅ Automaton Access (Rp2,000,000 one-time)

🎁 LIFETIME USERS: FREE ACCESS!
Your Automaton access is already activated.

📱 Regular Premium users:
Use /subscribe to purchase Automaton Access

Try it now: /automaton or 🤖 AI Agent menu
```

## Post-Deployment

### Monitor First Week
- Track how many users try to spawn agents
- Track how many users inquire about Automaton access
- Track payment conversions
- Monitor for any errors or issues

### Admin Tasks
- Process Automaton access payments
- Grant access using `grant_automaton_access.py`
- Track revenue from Automaton access fees

### Revenue Tracking
```python
# Weekly revenue check
from database import Database
db = Database()

# Count paid access (exclude lifetime)
db.cursor.execute("""
    SELECT COUNT(*) FROM users 
    WHERE automaton_access = 1 
    AND subscription_end IS NOT NULL
""")
paid_count = db.cursor.fetchone()[0]

revenue = paid_count * 2_000_000
print(f"Automaton Access Revenue: Rp{revenue:,}")
```

## Rollback Plan (If Needed)

If critical issues occur:

### 1. Revert Code
```bash
git revert HEAD
git push origin main
```

### 2. Revert Database (Only if necessary)
```sql
-- Remove column (CAUTION: Loses data)
ALTER TABLE users DROP COLUMN IF EXISTS automaton_access;
```

### 3. Restore from Backup
Use Supabase dashboard to restore from backup created in Step 1.

## Success Criteria

- ✅ Migration runs without errors
- ✅ Lifetime users have automatic access
- ✅ Regular premium users see access requirement
- ✅ Subscribe command shows Automaton pricing
- ✅ Admin can grant access successfully
- ✅ No errors in Railway logs
- ✅ Users can spawn agents after getting access

## Support

### Common User Questions

**Q: Why can't I spawn agents?**
A: You need Automaton Access (Rp2,000,000). Use /subscribe to purchase.

**Q: I'm a Lifetime user, do I need to pay?**
A: No! Lifetime users get FREE Automaton access.

**Q: I paid but still can't spawn agents?**
A: Contact admin @BillFarr with your payment proof and Telegram ID.

**Q: Is this a monthly fee?**
A: No, it's a ONE-TIME payment. Pay once, use forever.

### Admin Support

If users report issues:
1. Check their premium status: `db.is_user_premium(user_id)`
2. Check their access: `db.has_automaton_access(user_id)`
3. Check their credits: `user['credits']` (need >= 100,000)
4. Grant access if payment confirmed: `db.grant_automaton_access(user_id)`

## Files to Deploy

- `database.py` - Updated with access methods
- `app/automaton_manager.py` - Updated with access check
- `bot.py` - Updated /subscribe command
- `migrations/003_add_automaton_access.sql` - Migration script
- `grant_automaton_access.py` - Admin tool

## Documentation

- `AUTOMATON_ACCESS_FEE_COMPLETE.md` - Full documentation
- `AUTOMATON_ACCESS_QUICK_SUMMARY.md` - Quick reference
- `ADMIN_GRANT_AUTOMATON_ACCESS.md` - Admin guide
- `AUTOMATON_ACCESS_DEPLOYMENT.md` - This file

---

**Ready to deploy?** Follow the steps above carefully and monitor closely after deployment.

**Questions?** Check the documentation or contact the development team.

🚀 **Good luck with the deployment!**
