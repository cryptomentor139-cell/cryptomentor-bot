# Admin Guide: OpenClaw Credits Management 🔧

## Overview

Sebagai admin, kamu bisa:
1. ✅ Cek sisa credits OpenRouter secara real-time
2. ✅ Kirim notifikasi ke user setelah menambah credits
3. ✅ Monitor usage dan balance

---

## Admin Commands

### 1. Check OpenRouter Balance (Real-Time)

```
/admin_openclaw_balance
```

**Response:**
```
🔑 OpenRouter API Status

Account: My OpenRouter Account
Tier: Paid

💰 Balance:
• Available: $45.23
• Total Limit: $100.00
• Used: $54.77 (54.8%)

📊 Rate Limits:
• Requests: 200
• Interval: per minute

✅ Balance is healthy.

🔗 Quick Links:
• Manage Keys
• Add Credits
• View Activity

[🔄 Refresh] [💰 Add Credits (Web)]
```

**Features:**
- Real-time balance from OpenRouter API
- Shows usage percentage
- Warning if balance low
- Quick links to OpenRouter dashboard

---

### 2. Notify User (After Adding Credits)

```
/admin_notify_credits <user_id> <amount>
```

**Example:**
```
/admin_notify_credits 123456789 10
```

**What It Does:**
1. Fetches current OpenRouter balance
2. Sends notification to user
3. Confirms to admin

**User Receives:**
```
✅ Credits Added!

💰 Amount Added: $10.00
💳 Current Balance: $45.23

Your OpenClaw credits have been successfully added!

You can now use OpenClaw AI Agent.
Check your balance: /openclaw_balance

Thank you for your payment! 🎉
```

**Admin Receives:**
```
✅ Notification Sent!

User ID: 123456789
Amount: $10.00
Current Balance: $45.23

User has been notified.
```

---

### 3. Admin Help

```
/admin_openclaw_help
```

Shows all admin commands and workflow.

---

## Complete Workflow

### When User Wants to Deposit:

**Step 1: User Initiates Deposit**
```
User: /deposit
Bot: [Shows amount buttons]
User: [Clicks $10]
Bot: [Shows wallet address and payment instructions]
```

**Step 2: User Sends Payment**
- User sends USDT/USDC/BNB to wallet address
- User contacts @BillFarr with proof

**Step 3: Admin Verifies Payment**
```
1. Check BSCScan for transaction
2. Verify amount and wallet address
3. Confirm payment received
```

**Step 4: Admin Adds Credits to OpenRouter**
```
1. Go to https://openrouter.ai/settings/billing
2. Click "Add Credits"
3. Add amount (e.g., $10)
4. Confirm payment
```

**Step 5: Admin Notifies User**
```
/admin_notify_credits 123456789 10
```

**Step 6: User Checks Balance**
```
User: /openclaw_balance
Bot: Shows updated balance from OpenRouter
```

---

## Quick Reference

### Check Balance
```bash
/admin_openclaw_balance
```

### Notify User
```bash
/admin_notify_credits <user_id> <amount>

# Examples:
/admin_notify_credits 123456789 10
/admin_notify_credits 987654321 25.50
```

### Get Help
```bash
/admin_openclaw_help
```

---

## Important Links

### OpenRouter Dashboard
- **Add Credits:** https://openrouter.ai/settings/billing
- **View Activity:** https://openrouter.ai/activity
- **Manage Keys:** https://openrouter.ai/settings/keys

### Verify Payments
- **BSCScan:** https://bscscan.com/
- Search by transaction hash
- Verify wallet address and amount

---

## Tips for Admin

### 1. Monitor Balance Regularly
```
Run /admin_openclaw_balance daily
Set alert when balance < $10
```

### 2. Quick Response
```
Respond to user payment proofs within 24 hours
Use /admin_notify_credits immediately after adding
```

### 3. Keep Records
```
Log all deposits in spreadsheet:
- Date
- User ID
- Amount
- Transaction Hash
- Status
```

### 4. Handle Errors
```
If notification fails:
- User may have blocked bot
- Contact user directly
- Verify user ID is correct
```

---

## Troubleshooting

### Balance Not Showing?

**Check:**
1. OPENCLAW_API_KEY is set in Railway
2. API key is valid on OpenRouter
3. Network connection is stable

**Fix:**
```bash
# Test API key locally
python test_openrouter_key.py
```

### Notification Failed?

**Reasons:**
- User blocked the bot
- User deleted Telegram account
- Invalid user ID

**Solution:**
- Contact user via other means
- Ask user to unblock bot
- Verify user ID is correct

### Balance Not Updating?

**Remember:**
- Balance is shared across all users
- Updates are real-time from OpenRouter
- User sees same balance as admin

---

## Security Notes

### Protect Admin Commands
- Only admin IDs in ADMIN_IDS can use these commands
- Never share admin credentials
- Monitor admin activity logs

### Verify Payments
- Always check BSCScan before adding credits
- Verify transaction is confirmed (not pending)
- Match amount exactly

### OpenRouter API Key
- Keep OPENCLAW_API_KEY secret
- Rotate key if compromised
- Monitor usage for anomalies

---

## Example Session

```
Admin: /admin_openclaw_balance
Bot: Available: $45.23, Used: $54.77

[User sends payment proof: $10 USDT]

Admin: [Verifies on BSCScan]
Admin: [Adds $10 to OpenRouter]
Admin: /admin_notify_credits 123456789 10
Bot: ✅ Notification Sent!

User: /openclaw_balance
Bot: Available Credits: $55.23
```

---

## Files

**Handler:** `app/handlers_openclaw_admin_credits.py`
**Registration:** `bot.py` (line ~360)
**Documentation:** This file

---

## Testing

### Test Balance Check
```
/admin_openclaw_balance
Expected: Show OpenRouter balance
```

### Test Notification
```
/admin_notify_credits YOUR_USER_ID 0.01
Expected: You receive notification
```

### Test Help
```
/admin_openclaw_help
Expected: Show all commands
```

---

## Status

✅ Admin balance check (real-time)
✅ User notification system
✅ OpenRouter API integration
✅ Error handling
✅ Security checks

**Ready to use!**

---

**Created:** 2026-03-04
**For:** Admin Credit Management
**System:** OpenClaw (OpenRouter Balance)
