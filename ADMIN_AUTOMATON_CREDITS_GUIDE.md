# 🤖 Admin Guide: AUTOMATON Credits Management

## 🎯 Quick Reference

### Add AUTOMATON Credits
```bash
/admin_add_automaton_credits <user_id> <amount> <note>
```

### Check AUTOMATON Credits
```bash
/admin_check_automaton_credits <user_id>
```

## 📊 Credit Conversion

| USDC | Credits | Purpose |
|------|---------|---------|
| $5 | 500 | Minimum deposit |
| $30 | 3,000 | Minimum to spawn agent |
| $50 | 5,000 | Recommended starting balance |
| $100 | 10,000 | Good for multiple agents |

## 🔄 Complete Flow

### 1. User Sends Proof of Transfer
User clicks "📤 Kirim Bukti Transfer ke Admin" and sends:
- Screenshot of transaction
- Transaction hash
- Amount sent

### 2. Admin Verifies Deposit
Check transaction on Base Network:
- Network: Base
- Token: USDC
- Minimum: $5 USDC
- For spawn: $30 USDC

### 3. Admin Adds Credits
```bash
/admin_add_automaton_credits 123456789 3000 "Deposit $30 USDC verified - TxHash: 0x..."
```

### 4. User Receives Notification
User automatically receives:
```
✅ Deposit AUTOMATON Berhasil Diverifikasi!

💰 AUTOMATON Credits telah ditambahkan ke akun Anda:
• Jumlah: +3,000 credits
• Balance baru: 3,000 credits

📝 Note: Deposit $30 USDC verified - TxHash: 0x...

🤖 Credits ini khusus untuk AI Agent (autonomous trading)

🎯 Langkah Selanjutnya:
Klik tombol 🤖 AI Agent di menu utama untuk spawn agent Anda!
```

### 5. User Clicks AI Agent Button
- User clicks "🤖 AI Agent" in main menu
- Menu automatically detects credits >= 3,000
- Full spawn agent menu is displayed
- User can now spawn agent!

## 💡 Important Notes

### Two Credit Systems
1. **Regular Bot Credits** (for /analyze, /futures, /ai)
   - Command: `/grant_credits`
   - Table: `user_credits`
   - Purpose: Bot features

2. **AUTOMATON Credits** (for AI Agent)
   - Command: `/admin_add_automaton_credits`
   - Table: `user_credits_balance`
   - Purpose: Autonomous trading

### Minimum Requirements
- **Any deposit**: $5 USDC minimum
- **Spawn agent**: $30 USDC minimum (3,000 credits)
- **Applies to**: Everyone (including admin & lifetime premium)

### Network & Token
- **Network**: Base Network ONLY
- **Token**: USDC ONLY
- **No other networks or tokens supported**

## 🎯 Admin Menu Access

You can also manage credits via menu:
1. Send `/admin`
2. Click "👑 Premium Control"
3. Click "🤖 Manage AUTOMATON Credits"
4. Choose:
   - ➕ Add AUTOMATON Credits
   - 🔍 Check AUTOMATON Credits
   - 📖 View Guide

## 📝 Examples

### Example 1: First Time Deposit
```bash
# User deposits $30 USDC
/admin_add_automaton_credits 123456789 3000 "First deposit $30 USDC - TxHash: 0xabc123"

# Result:
# - User gets 3,000 credits
# - Can spawn agent immediately
# - Receives notification with instructions
```

### Example 2: Top Up
```bash
# User already has 2,000 credits, deposits $10 more
/admin_add_automaton_credits 123456789 1000 "Top up $10 USDC - TxHash: 0xdef456"

# Result:
# - User now has 3,000 credits total
# - Can now spawn agent
# - Receives notification
```

### Example 3: Large Deposit
```bash
# User deposits $100 USDC
/admin_add_automaton_credits 123456789 10000 "Deposit $100 USDC - TxHash: 0xghi789"

# Result:
# - User gets 10,000 credits
# - Can spawn multiple agents
# - Good balance for extended trading
```

## 🔍 Checking User Status

### Check Credits
```bash
/admin_check_automaton_credits 123456789
```

Output:
```
👤 User Info:
• ID: 123456789
• Username: @username
• Name: John Doe
• Premium: lifetime

💰 AUTOMATON Credits Balance:
• Available: 3,000 credits
• Total: 3,000 credits

📊 Status:
• Minimum untuk spawn: 3,000 credits
• Status: ✅ Cukup

⚠️ Ini adalah AUTOMATON credits untuk AI Agent
```

## ⚠️ Common Mistakes to Avoid

### ❌ Wrong Command
```bash
# DON'T use regular credits command
/grant_credits 123456789 3000

# DO use AUTOMATON credits command
/admin_add_automaton_credits 123456789 3000 "Deposit verified"
```

### ❌ Wrong Network
```
User: "I sent USDC on Ethereum"
Admin: ❌ Only Base Network supported
```

### ❌ Wrong Token
```
User: "I sent USDT"
Admin: ❌ Only USDC supported
```

### ❌ Below Minimum for Spawn
```bash
# User deposits $20 (2,000 credits)
/admin_add_automaton_credits 123456789 2000 "Deposit $20"

# Result: Credits added but can't spawn yet
# User needs $10 more to reach $30 minimum
```

## 🎉 Success Indicators

After adding credits, user should:
1. ✅ Receive notification message
2. ✅ See "Langkah Selanjutnya" instruction
3. ✅ Click "🤖 AI Agent" button
4. ✅ See full spawn agent menu (not deposit menu)
5. ✅ Be able to spawn agent

If user still sees deposit menu:
- Check credits balance: `/admin_check_automaton_credits <user_id>`
- Verify credits >= 3,000
- Ask user to click AI Agent button again

## 📞 Support

If issues occur:
1. Check user credits balance
2. Verify transaction on Base Network
3. Confirm USDC token (not USDT)
4. Ensure minimum $30 for spawn
5. Ask user to click AI Agent button

---

**Remember**: AUTOMATON credits are separate from regular bot credits. Always use the correct command!
