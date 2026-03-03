# OpenClaw Per-User Credit System

## Overview

Implemented a per-user credit tracking system where:
- Each user has their own credit balance
- Admin allocates credits from OpenRouter balance to specific users
- Credits are deducted per message automatically
- Total allocated credits cannot exceed OpenRouter balance

## Key Features

### 1. Per-User Credit Balances
- Each user has individual credit balance in database
- Credits allocated by admin from OpenRouter balance
- Real-time tracking of usage per message

### 2. Safety Checks
- System prevents over-allocation
- Total user credits ≤ OpenRouter balance
- Automatic validation before each allocation

### 3. Transparent Tracking
- Every allocation logged with admin ID and reason
- Every message usage logged with token counts
- Periodic balance snapshots for auditing

## Database Schema

### Tables Created

1. **openclaw_user_credits**
   - `user_id` - Telegram user ID (primary key)
   - `credits` - Current available balance
   - `total_allocated` - Total ever allocated
   - `total_used` - Total ever used

2. **openclaw_credit_allocations**
   - Logs every admin allocation
   - Tracks OpenRouter balance before/after
   - Records reason for allocation

3. **openclaw_credit_usage**
   - Logs every message sent
   - Tracks tokens used and cost
   - Records balance before/after

4. **openclaw_balance_snapshots**
   - Periodic system status snapshots
   - OpenRouter vs allocated comparison
   - User count tracking

## Admin Commands

### /admin_add_credits <user_id> <amount> [reason]
Allocate credits to specific user

**Example:**
```
/admin_add_credits 123456789 7 Payment Rp 100k
```

**Features:**
- Checks OpenRouter balance first
- Validates total allocated won't exceed balance
- Auto-notifies user
- Logs allocation with reason

### /admin_system_status
View system-wide credit status

**Shows:**
- OpenRouter balance
- Total allocated to users
- Available to allocate
- Top users by balance
- Usage statistics

### /admin_openclaw_balance
Check OpenRouter API balance (real-time)

**Shows:**
- Current balance
- Usage percentage
- Rate limits
- Quick links to top-up

### /admin_openclaw_help
Show all admin commands with examples

## User Commands

### /openclaw_balance
Check personal credit balance

**Shows:**
- Available credits
- Total used
- Message count
- Average cost per message

### /subscribe
View payment options and top-up

**Shows:**
- Payment methods (Bank/E-Money/Crypto)
- Minimum top-up (Rp 100k)
- Admin contact info

## Workflow

### For Admin

1. **User Pays**
   - User sends payment (Rp 100k = ~$7)
   - User sends proof to admin

2. **Admin Verifies**
   - Check bank transfer / e-money / crypto transaction
   - Verify amount received

3. **Admin Tops Up OpenRouter** (if needed)
   - Go to https://openrouter.ai/settings/billing
   - Add credits to OpenRouter account

4. **Admin Allocates Credits**
   ```
   /admin_add_credits 123456789 7 Payment Rp 100k
   ```
   - System checks if allocation is safe
   - Credits added to user's balance
   - User auto-notified

5. **Monitor System**
   ```
   /admin_system_status
   ```
   - Check total allocated vs OpenRouter balance
   - Ensure no over-allocation

### For User

1. **Check Balance**
   ```
   /openclaw_balance
   ```

2. **Top-Up Credits**
   ```
   /subscribe
   ```
   - View payment options
   - Send payment
   - Send proof to @BillFarr

3. **Use OpenClaw**
   - Just chat normally
   - Credits deducted automatically
   - Cost shown after each message

## Credit Deduction

### Automatic Per-Message
- Credits deducted after each AI response
- Based on actual token usage
- Formula: `(input_tokens * $0.0000025) + (output_tokens * $0.00001)`

### Example Costs
- Simple question: ~$0.01-0.02
- Chart analysis: ~$0.03-0.05
- Deep analysis: ~$0.05-0.10

### Admin Bypass
- Admin users get free unlimited access
- No credit deduction for admin
- Useful for testing and support

## Safety Features

### 1. Over-Allocation Prevention
```python
if new_total_allocated > openrouter_balance:
    return "Cannot allocate - would exceed balance"
```

### 2. Insufficient Balance Check
```python
if user_credits < message_cost:
    return "Insufficient credits"
```

### 3. Transaction Logging
- Every allocation logged
- Every usage logged
- Audit trail for disputes

## Migration

### Run Migration
```bash
cd Bismillah
python run_per_user_credits_migration.py
```

### Verify Migration
```sql
-- Check tables exist
SELECT * FROM openclaw_user_credits LIMIT 1;
SELECT * FROM openclaw_credit_allocations LIMIT 1;
SELECT * FROM openclaw_credit_usage LIMIT 1;
SELECT * FROM openclaw_balance_snapshots LIMIT 1;
```

## Deployment

### 1. Push to GitHub
```bash
git add .
git commit -m "Implement per-user credit tracking system"
git push origin main
```

### 2. Railway Auto-Deploy
- Railway will detect changes
- Auto-deploy to production
- Migration runs automatically on startup

### 3. Verify Deployment
```
/admin_system_status
```

## Monitoring

### Daily Checks
1. Check system status: `/admin_system_status`
2. Verify OpenRouter balance matches allocated
3. Review top users by balance

### Weekly Checks
1. Review allocation logs
2. Check usage patterns
3. Identify any anomalies

### Monthly Checks
1. Review balance snapshots
2. Calculate revenue vs costs
3. Adjust pricing if needed

## Troubleshooting

### "Over-allocated" Warning
**Cause:** Total user credits > OpenRouter balance
**Solution:** Top-up OpenRouter immediately

### User Can't Send Messages
**Cause:** Insufficient credits
**Solution:** User needs to top-up via /subscribe

### Credits Not Deducting
**Cause:** Database connection issue
**Solution:** Check logs, restart bot if needed

## Files Modified

1. `migrations/013_openclaw_per_user_credits.sql` - Database schema
2. `app/openclaw_user_credits.py` - Credit operations module
3. `app/handlers_openclaw_admin_credits.py` - Admin commands
4. `app/openclaw_message_handler.py` - Credit deduction logic
5. `app/handlers_openclaw_deposit.py` - Balance command
6. `run_per_user_credits_migration.py` - Migration runner

## Testing

### Test Admin Allocation
```
/admin_add_credits YOUR_USER_ID 10 Test allocation
```

### Test User Balance
```
/openclaw_balance
```

### Test Message Deduction
1. Send message to OpenClaw
2. Check balance before and after
3. Verify cost shown in response

### Test Over-Allocation Prevention
1. Check OpenRouter balance: `/admin_openclaw_balance`
2. Try to allocate more than available
3. Should get error message

## Summary

✅ Per-user credit tracking implemented
✅ Admin allocation with safety checks
✅ Automatic credit deduction per message
✅ Comprehensive logging and auditing
✅ Over-allocation prevention
✅ User balance commands
✅ Admin monitoring commands

The system ensures that:
- Credits allocated to users = Real OpenRouter balance
- No over-allocation possible
- Full transparency and audit trail
- Simple workflow for admin and users

