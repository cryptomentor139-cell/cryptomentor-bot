# Admin AUTOMATON Credit Management Guide

**⚠️ IMPORTANT**: These commands are for **AUTOMATON credits** (AI Agent only), NOT regular bot credits!

## Quick Reference

### Add AUTOMATON Credits to User
```
/admin_add_automaton_credits <user_id> <amount> <note>
```

### Check User AUTOMATON Credits
```
/admin_check_automaton_credits <user_id>
```

## Detailed Instructions

### 1. When User Sends Deposit Proof

**User will send you:**
- Screenshot of transaction
- Their Telegram User ID
- Amount deposited

**What to do:**

1. **Verify Transaction on Blockchain**
   - Go to Base blockchain explorer: https://basescan.org/
   - Search for transaction hash
   - Verify:
     - ✅ Destination address matches centralized wallet
     - ✅ Network is Base
     - ✅ Token is USDC (not USDT)
     - ✅ Amount matches what user claims
     - ✅ Transaction is confirmed (12+ confirmations)

2. **Calculate Credits**
   - 1 USDC = 100 credits
   - $30 USDC = 3,000 credits
   - $50 USDC = 5,000 credits
   - $100 USDC = 10,000 credits

3. **Add AUTOMATON Credits**
   ```
   /admin_add_automaton_credits <user_id> <credits> Deposit $<amount> USDC verified
   ```
   
   **Example:**
   ```
   /admin_add_automaton_credits 123456789 3000 Deposit $30 USDC verified
   ```

4. **Confirm with User**
   - Bot will automatically notify user
   - User will receive message with:
     - AUTOMATON credits added
     - New balance
     - Confirmation message

### 2. Check User AUTOMATON Credits Before Adding

**Always check first to avoid duplicates:**

```
/admin_check_automaton_credits 123456789
```

**This shows:**
- Current available credits
- Total credits ever received
- Whether user has enough for spawn ($30 minimum)

### 3. Common Scenarios

#### Scenario A: First Deposit ($30)
```
User: "I deposited $30 USDC, my ID is 123456789"
Admin: /admin_check_automaton_credits 123456789
       (Shows 0 credits)
Admin: (Verify transaction on blockchain)
Admin: /admin_add_automaton_credits 123456789 3000 Deposit $30 USDC verified
Bot:   ✅ AUTOMATON Credits added! User notified.
```

#### Scenario B: Additional Deposit ($50)
```
User: "I deposited another $50 USDC"
Admin: /admin_check_automaton_credits 123456789
       (Shows 3000 credits from previous deposit)
Admin: (Verify transaction on blockchain)
Admin: /admin_add_automaton_credits 123456789 5000 Additional deposit $50 USDC verified
Bot:   ✅ AUTOMATON Credits added! User now has 8000 credits.
```

#### Scenario C: Wrong Network
```
User: "I sent $30 but credits not received"
Admin: (Check blockchain - sees transaction on Polygon, not Base)
Admin: "Sorry, you sent to wrong network. We only support Base Network.
        Funds sent to other networks cannot be recovered."
```

#### Scenario D: Wrong Token (USDT instead of USDC)
```
User: "I sent $30 USDT"
Admin: "We only support USDC, not USDT. Please send USDC on Base Network."
```

### 4. Verification Checklist

Before adding credits, verify:

- [ ] Transaction exists on Base blockchain
- [ ] Destination address is correct
- [ ] Token is USDC (not USDT)
- [ ] Network is Base (not Polygon, Arbitrum, etc)
- [ ] Amount matches user's claim
- [ ] Transaction has 12+ confirmations
- [ ] User hasn't already been credited for this transaction

### 5. Conversion Table

| USDC Amount | Credits | Use Case |
|-------------|---------|----------|
| $5 | 500 | Minimum deposit |
| $10 | 1,000 | Small deposit |
| $30 | 3,000 | Minimum for spawn agent |
| $50 | 5,000 | Medium deposit |
| $100 | 10,000 | Large deposit |
| $500 | 50,000 | Very large deposit |
| $1,000 | 100,000 | Spawn fee equivalent |

### 6. Error Messages

#### "User not found"
- User hasn't used /start yet
- Ask user to /start the bot first
- Then try again

#### "Database not available"
- Supabase connection issue
- Check Railway logs
- Try again in a few minutes

#### "Command only for admin"
- You're not in ADMIN_IDS
- Check environment variables
- Contact system admin

### 7. Best Practices

**DO:**
- ✅ Always verify transaction on blockchain
- ✅ Use descriptive notes when adding credits
- ✅ Respond to deposit proofs within 1 hour
- ✅ Keep transaction hashes for records
- ✅ Double-check user ID before adding credits

**DON'T:**
- ❌ Add credits without verifying transaction
- ❌ Add credits for wrong network transactions
- ❌ Add credits for USDT (only USDC supported)
- ❌ Add credits twice for same transaction
- ❌ Forget to check existing balance first

### 8. Transaction Logging

Every credit addition is logged with:
- User ID
- Amount added
- Your admin ID
- Timestamp
- Description/note

This creates an audit trail for all credit additions.

### 9. User Notification

When you add credits, user automatically receives:

```
✅ Deposit Berhasil Diverifikasi!

💰 Credits telah ditambahkan ke akun Anda:
• Jumlah: +3,000 credits
• Balance baru: 3,000 credits

📝 Note: Deposit $30 USDC verified

Terima kasih! Anda sekarang bisa spawn agent dengan /spawn_agent
```

### 10. Troubleshooting

**User says "I didn't receive notification"**
- Check if user blocked the bot
- Check if bot can send messages
- Credits are still added even if notification fails
- User can check with /balance

**User says "Credits not showing"**
- Ask user to use /balance command
- Check with /admin_check_credits
- Verify transaction was logged in database

**Multiple admins adding credits**
- Always check balance first with /admin_check_credits
- Avoid duplicate additions
- Transaction log shows which admin added credits

### 11. Quick Commands Reference

```bash
# Add AUTOMATON credits
/admin_add_automaton_credits 123456789 3000 Deposit $30 USDC verified

# Check AUTOMATON credits
/admin_check_automaton_credits 123456789

# Search user (from admin menu)
/admin
# Then click "Search User" and enter user ID
```

**⚠️ REMEMBER**: These are for AUTOMATON credits (AI Agent), NOT regular bot credits!

### 12. Support Responses

**Template for "Deposit not received":**
```
Please send me:
1. Transaction hash
2. Your Telegram User ID (type /id to get it)
3. Amount you deposited

I'll verify and add credits within 1 hour.
```

**Template for "Wrong network":**
```
Sorry, you sent to [network name]. We only support Base Network.

Funds sent to other networks cannot be recovered.

Please send USDC on Base Network to:
[centralized wallet address]
```

**Template for "Wrong token":**
```
Sorry, you sent USDT. We only support USDC.

Please send USDC (not USDT) on Base Network to:
[centralized wallet address]
```

---

## Summary

1. User sends deposit proof
2. Verify transaction on Base blockchain
3. Calculate credits (1 USDC = 100 credits)
4. Check existing balance: `/admin_check_automaton_credits <user_id>`
5. Add credits: `/admin_add_automaton_credits <user_id> <amount> <note>`
6. User receives automatic notification
7. Done!

**Remember**: 
- Always verify on blockchain before adding credits!
- These are AUTOMATON credits for AI Agent, NOT regular bot credits!

---

**Last Updated**: 2026-02-22
**Commands**: `/admin_add_automaton_credits`, `/admin_check_automaton_credits`
