# OpenClaw Per-User Credit System - Implementation Summary

## What Was Built

A complete per-user credit tracking system for OpenClaw where:
- Each user has their own credit balance in the database
- Admin allocates credits from OpenRouter balance to specific users
- Credits are automatically deducted per message based on actual usage
- System prevents over-allocation (total user credits cannot exceed OpenRouter balance)

## Problem Solved

**Before:** Shared OpenRouter balance across all users - no way to track individual usage or allocate specific amounts to users.

**After:** Each user has their own balance, admin can allocate specific amounts, and the system ensures total allocated never exceeds OpenRouter balance.

## Key Features

### 1. Per-User Credit Balances
- Individual balance for each user
- Tracked in `openclaw_user_credits` table
- Real-time updates on allocation and usage

### 2. Admin Credit Allocation
- Command: `/admin_add_credits <user_id> <amount> [reason]`
- Validates against OpenRouter balance before allocation
- Auto-notifies user when credits added
- Logs every allocation with admin ID and reason

### 3. Automatic Credit Deduction
- Credits deducted after each AI message
- Based on actual token usage (input + output)
- Formula: `(input_tokens * $0.0000025) + (output_tokens * $0.00001)`
- Logged in `openclaw_credit_usage` table

### 4. Safety Checks
- **Over-allocation prevention:** Total allocated ≤ OpenRouter balance
- **Insufficient balance check:** User must have enough credits before sending message
- **Transaction logging:** Every allocation and usage logged for audit

### 5. Admin Monitoring
- `/admin_system_status` - View OpenRouter vs allocated balance
- `/admin_openclaw_balance` - Check OpenRouter API balance
- `/admin_openclaw_help` - Show all admin commands

### 6. User Commands
- `/openclaw_balance` - Check personal credit balance
- `/subscribe` - View payment options and top-up

## Database Schema

### New Tables

1. **openclaw_user_credits**
   - Stores per-user credit balances
   - Tracks total allocated and total used

2. **openclaw_credit_allocations**
   - Logs every admin allocation
   - Records OpenRouter balance before/after
   - Stores reason for allocation

3. **openclaw_credit_usage**
   - Logs every message sent
   - Tracks tokens used and cost
   - Records balance before/after

4. **openclaw_balance_snapshots**
   - Periodic system status snapshots
   - Tracks OpenRouter vs allocated over time

## Workflow

### For Admin

1. User sends payment proof (Rp 100k = ~$7)
2. Admin verifies payment
3. Admin tops up OpenRouter if needed
4. Admin runs: `/admin_add_credits 123456789 7 Payment Rp 100k`
5. System validates and allocates credits
6. User auto-notified

### For User

1. User checks balance: `/openclaw_balance`
2. User tops up via `/subscribe`
3. User sends payment and proof to admin
4. Credits added automatically
5. User chats with OpenClaw
6. Credits deducted per message
7. Cost shown after each response

## Files Created

1. `migrations/013_openclaw_per_user_credits.sql` - Database schema
2. `app/openclaw_user_credits.py` - Credit operations module
3. `run_per_user_credits_migration.py` - Migration runner
4. `test_per_user_credits.py` - Test script
5. `OPENCLAW_PER_USER_CREDITS.md` - Full documentation
6. `DEPLOY_PER_USER_CREDITS.md` - Deployment guide
7. `PER_USER_CREDITS_SUMMARY.md` - This file

## Files Modified

1. `app/handlers_openclaw_admin_credits.py` - New admin commands
2. `app/openclaw_message_handler.py` - Credit deduction logic
3. `app/handlers_openclaw_deposit.py` - Updated balance command

## Commands Reference

### Admin Commands

```bash
# Allocate credits to user
/admin_add_credits 123456789 7 Payment Rp 100k

# Check system status
/admin_system_status

# Check OpenRouter balance
/admin_openclaw_balance

# Show help
/admin_openclaw_help
```

### User Commands

```bash
# Check personal balance
/openclaw_balance

# View payment options
/subscribe
```

## Example Usage

### Admin Allocates Credits

```
Admin: /admin_add_credits 123456789 7 Payment Rp 100k

Bot: ✅ Credits Allocated Successfully!

User: 123456789
Amount: $7.00
Reason: Payment Rp 100k

User Balance:
• Before: $0.00
• After: $7.00

System Status:
💰 OpenRouter Balance: $100.00
📊 Total Allocated: $7.00
✅ Available: $93.00

✅ Notification sent
```

### User Checks Balance

```
User: /openclaw_balance

Bot: 💳 Your OpenClaw Balance

👤 User ID: 123456789
💰 Available Credits: $7.00

📊 Usage Stats:
• Total Used: $0.00
• Messages Sent: 0
• Avg Cost/Message: $0.0000

✅ Balance is healthy.

💰 Top-Up Credits:
Use /subscribe to see payment options

📞 Need Help?
Contact admin: @BillFarr
```

### User Sends Message

```
User: Analyze BTC trend

Bot: [AI Response about BTC]

💰 Cost: $0.0234 • 💳 Balance: $6.98
```

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
- Every allocation logged with admin ID
- Every usage logged with token counts
- Full audit trail for disputes

## Testing

### Run Tests Locally
```bash
cd Bismillah
python test_per_user_credits.py
```

### Test Coverage
- ✅ Get user credits
- ✅ Add credits
- ✅ Deduct credits
- ✅ Get total allocated
- ✅ Check allocation limit
- ✅ Over-allocation prevention
- ✅ Insufficient balance check

## Deployment

### Steps
1. Run migration: `python run_per_user_credits_migration.py`
2. Test locally: `python test_per_user_credits.py`
3. Commit and push to GitHub
4. Railway auto-deploys
5. Verify with `/admin_system_status`

### Verification
```bash
# Check system status
/admin_system_status

# Test allocation
/admin_add_credits YOUR_USER_ID 10 Test

# Check balance
/openclaw_balance

# Send message and verify deduction
```

## Benefits

### For Admin
- ✅ Full control over credit allocation
- ✅ Prevents over-allocation automatically
- ✅ Complete audit trail
- ✅ Real-time monitoring

### For Users
- ✅ Transparent credit balance
- ✅ Pay only for what they use
- ✅ Clear cost per message
- ✅ Easy top-up process

### For System
- ✅ Sustainable revenue model
- ✅ Accurate usage tracking
- ✅ Prevents abuse
- ✅ Scalable architecture

## Monitoring

### Daily
- Check `/admin_system_status`
- Verify no over-allocation
- Monitor top users

### Weekly
- Review allocation logs
- Check usage patterns
- Identify anomalies

### Monthly
- Review balance snapshots
- Calculate revenue vs costs
- Adjust pricing if needed

## Troubleshooting

### "Over-allocated" Warning
**Solution:** Top-up OpenRouter at https://openrouter.ai/settings/billing

### User Can't Send Messages
**Solution:** User needs to top-up via `/subscribe`

### Credits Not Deducting
**Solution:** Check logs, restart bot if needed

## Success Metrics

✅ Per-user credit tracking implemented
✅ Admin allocation with safety checks
✅ Automatic credit deduction per message
✅ Comprehensive logging and auditing
✅ Over-allocation prevention working
✅ User balance commands functional
✅ Admin monitoring commands working

## Next Steps

1. Deploy to production
2. Test with real users
3. Monitor for 24 hours
4. Announce to users
5. Document edge cases

## Conclusion

The per-user credit system is production-ready and provides:
- **Transparency:** Users see exactly what they're paying for
- **Safety:** System prevents over-allocation automatically
- **Sustainability:** Ensures credits allocated = OpenRouter balance
- **Scalability:** Can handle unlimited users

The implementation ensures that "credits yang ku beri ke dia adalah credits real yang dari openrouter tersedia, jadi pemakaiannya jelas tidak ada yang kurang dan lebih" - exactly as requested.

