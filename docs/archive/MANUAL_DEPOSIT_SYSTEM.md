# Manual Deposit System - Quick Reference

## Overview
The AI Agent deposit system now uses **manual verification by admin** instead of automatic detection. This ensures maximum security and prevents issues with blockchain monitoring.

**IMPORTANT**: These commands are for **AUTOMATON credits** (AI Agent only), NOT regular bot credits!

## How It Works

### For Users:
1. User clicks "💰 Deposit Sekarang" in AI Agent menu
2. System shows centralized wallet address (Base Network only)
3. User sends USDC to the address
4. User screenshots transaction proof
5. User clicks "📤 Kirim Bukti Transfer" button
6. User sends screenshot to admin with their User ID
7. Admin verifies and adds credits manually
8. User receives notification when credits are added

### For Admin:
1. User sends transfer proof via Telegram
2. Admin verifies transaction on Base blockchain explorer
3. Admin uses `/admin_add_automaton_credits <user_id> <amount> <note>`
4. System adds credits to user's account
5. User receives automatic notification
6. Admin can check user credits with `/admin_check_automaton_credits <user_id>`

## Admin Commands

### Add AUTOMATON Credits
```
/admin_add_automaton_credits <user_id> <amount> <note>
```

**Example:**
```
/admin_add_automaton_credits 123456789 3000 Deposit $30 USDC verified
```

**Parameters:**
- `user_id`: Telegram user ID (required)
- `amount`: AUTOMATON credits to add (required, 1 USDC = 100 credits)
- `note`: Reason for adding credits (optional, can be multiple words)

**⚠️ IMPORTANT**: This adds AUTOMATON credits for AI Agent, NOT regular bot credits!

### Check AUTOMATON Credits
```
/admin_check_automaton_credits <user_id>
```

**Example:**
```
/admin_check_automaton_credits 123456789
```

**Shows:**
- User info (ID, username, name, premium tier)
- Available credits
- Total credits
- Whether user has enough for spawn ($30 minimum)

## Deposit Requirements

### Minimum Deposit
- **$30 USDC** (3,000 credits) required to spawn agent
- This applies to EVERYONE including admin and lifetime premium users

### Network
- **Base Network ONLY**
- Other networks NOT supported (funds will be lost)

### Token
- **USDC ONLY**
- USDT and other tokens NOT supported

### Conversion Rate
- 1 USDC = 100 Conway Credits
- $30 USDC = 3,000 Credits

## User Flow

### Step 1: Access AI Agent Menu
- User clicks "🤖 AI Agent" in main menu
- If no deposit: Shows deposit-required message
- If has deposit: Shows full AI Agent menu

### Step 2: Deposit
1. Click "💰 Deposit Sekarang"
2. Copy wallet address or scan QR code
3. Send USDC (Base Network) to address
4. Screenshot transaction proof

### Step 3: Send Proof to Admin
1. Click "📤 Kirim Bukti Transfer ke Admin"
2. Opens chat with admin
3. Send screenshot with User ID
4. Wait for admin verification (< 1 hour)

### Step 4: Verification
1. Admin checks transaction on blockchain
2. Admin adds credits with `/admin_add_credits`
3. User receives notification
4. User can now spawn agent

## Database Tables

### user_credits_balance
Stores user credit balances:
- `user_id`: Telegram user ID
- `available_credits`: Credits available for use
- `total_conway_credits`: Total credits ever received

### credit_transactions
Logs all credit transactions:
- `user_id`: Telegram user ID
- `amount`: Credits added/removed
- `type`: Transaction type (admin_deposit, spawn, etc)
- `description`: Transaction description
- `admin_id`: Admin who performed action

## Security Features

1. **Manual Verification**: Admin verifies each deposit on blockchain
2. **Transaction Logging**: All credit additions are logged with admin ID
3. **User Notifications**: Users receive confirmation when credits are added
4. **Audit Trail**: Complete history of all credit transactions

## Troubleshooting

### User Says "Deposit Not Received"
1. Ask for transaction hash
2. Check Base blockchain explorer
3. Verify: correct address, correct network, correct token
4. If valid, add credits manually with `/admin_add_credits`

### User Sent to Wrong Network
- Funds are lost if sent to wrong network
- Cannot recover funds from other networks
- Educate user to use Base Network only

### User Sent Wrong Token (USDT instead of USDC)
- USDT is not supported
- Cannot convert USDT to credits
- User must send USDC

## Best Practices

### For Admin:
1. Always verify transaction on blockchain before adding credits
2. Use descriptive notes when adding credits
3. Respond to deposit proofs within 1 hour
4. Keep transaction hashes for records

### For Users:
1. Always use Base Network
2. Only send USDC
3. Include User ID when sending proof
4. Save transaction hash for tracking
5. Wait for admin verification before contacting support

## Files Modified

1. `bot.py`: Registered admin credit commands
2. `menu_handlers.py`: Updated deposit flow with manual verification
3. `app/handlers_admin_credits.py`: Admin commands for credit management

## Testing

### Test Add Credits
```bash
# As admin in Telegram:
/admin_add_automaton_credits YOUR_USER_ID 3000 Test deposit $30
```

### Test Check Credits
```bash
# As admin in Telegram:
/admin_check_automaton_credits YOUR_USER_ID
```

### Test User Flow
1. As regular user, go to AI Agent menu
2. Click "💰 Deposit Sekarang"
3. Note the wallet address
4. Click "📤 Kirim Bukti Transfer"
5. Send test message to admin
6. Admin adds credits
7. Check if notification received

## Deployment

### Railway Environment Variables
No new environment variables needed. Uses existing:
- `ADMIN_IDS`: Admin user IDs (comma-separated)
- `CENTRALIZED_WALLET_ADDRESS`: Deposit address

### Database Migration
No migration needed. Uses existing tables:
- `user_credits_balance`
- `credit_transactions`

## Next Steps

1. ✅ Register admin commands in bot.py
2. ✅ Update deposit flow in menu_handlers.py
3. ✅ Add "Kirim Bukti Transfer" button
4. ✅ Update deposit guide
5. ⏳ Test manual credit addition
6. ⏳ Deploy to Railway

## Support

If issues arise:
1. Check admin commands are registered: Look for "✅ Admin credits handlers registered" in logs
2. Check database connection: Verify Supabase is enabled
3. Check user exists: User must have used /start before
4. Check admin permissions: Only admins can add credits

---

**Status**: Implementation complete, ready for testing
**Last Updated**: 2026-02-22
