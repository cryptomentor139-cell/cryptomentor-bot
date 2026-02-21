# Admin Quick Reference Card

## 🚨 PENTING: 2 Jenis Credits!

Bot ini punya **2 sistem credits berbeda**. Jangan sampai salah!

---

## 1. Regular Bot Credits

**Untuk:** `/analyze`, `/futures`, `/ai`, multi-coin signals

**Command:**
```bash
/grant_credits <user_id> <amount>
```

**Atau via menu:**
```bash
/admin → Manage Credits
```

---

## 2. AUTOMATON Credits (AI Agent)

**Untuk:** AI Agent, spawn agent, autonomous trading

**Commands:**
```bash
/admin_add_automaton_credits <user_id> <amount> <note>
/admin_check_automaton_credits <user_id>
```

---

## Quick Decision Tree

**User bilang:**
- "Deposit USDC" → `/admin_add_automaton_credits`
- "Spawn agent" → `/admin_add_automaton_credits`
- "AI Agent" → `/admin_add_automaton_credits`
- "Autonomous trading" → `/admin_add_automaton_credits`

**User bilang:**
- "/analyze habis" → `/grant_credits`
- "/futures habis" → `/grant_credits`
- "Credits bot habis" → `/grant_credits`
- "Mau analisis" → `/grant_credits`

---

## Deposit Verification Flow

### User Deposit USDC untuk AI Agent:

1. **User kirim bukti transfer**
   - Screenshot transaction
   - User ID
   - Amount

2. **Verify di blockchain**
   - Go to: https://basescan.org/
   - Check: address, network (Base), token (USDC), amount

3. **Check existing balance**
   ```bash
   /admin_check_automaton_credits <user_id>
   ```

4. **Add credits**
   ```bash
   /admin_add_automaton_credits <user_id> <amount> Deposit $<amount> USDC verified
   ```
   
   **Example:**
   ```bash
   /admin_add_automaton_credits 123456789 3000 Deposit $30 USDC verified
   ```

5. **Done!**
   - User receives automatic notification
   - Credits added to database

---

## Conversion Table

| USDC | AUTOMATON Credits | Use Case |
|------|------------------|----------|
| $5 | 500 | Minimum deposit |
| $30 | 3,000 | Minimum for spawn |
| $50 | 5,000 | Medium deposit |
| $100 | 10,000 | Large deposit |

**Formula:** 1 USDC = 100 AUTOMATON credits

---

## Common Scenarios

### ✅ Scenario 1: First Deposit
```
User: "Saya deposit $30 USDC untuk AI Agent, ID: 123456789"
Admin: /admin_check_automaton_credits 123456789
Admin: (Verify on blockchain)
Admin: /admin_add_automaton_credits 123456789 3000 Deposit $30 USDC verified
```

### ✅ Scenario 2: Additional Deposit
```
User: "Deposit lagi $50 USDC"
Admin: /admin_check_automaton_credits 123456789
Admin: (Shows 3000 existing)
Admin: /admin_add_automaton_credits 123456789 5000 Additional deposit $50 USDC
```

### ❌ Scenario 3: Wrong Network
```
User: "Deposit $30 tapi belum masuk"
Admin: (Check blockchain - sees Polygon, not Base)
Admin: "Sorry, you sent to wrong network. We only support Base Network."
```

### ❌ Scenario 4: Wrong Token
```
User: "Saya kirim $30 USDT"
Admin: "We only support USDC, not USDT. Please send USDC on Base Network."
```

---

## Verification Checklist

Before adding credits:

- [ ] Transaction exists on Base blockchain
- [ ] Destination address correct
- [ ] Token is USDC (not USDT)
- [ ] Network is Base (not Polygon/Arbitrum/etc)
- [ ] Amount matches user's claim
- [ ] Transaction has 12+ confirmations
- [ ] User not already credited for this transaction

---

## Error Messages

**"User not found"**
→ User hasn't used /start yet

**"Database not available"**
→ Supabase connection issue, try again

**"Command only for admin"**
→ You're not in ADMIN_IDS

---

## Support Responses

**Template: Deposit not received**
```
Please send me:
1. Transaction hash
2. Your Telegram User ID (type /id)
3. Amount deposited

I'll verify and add credits within 1 hour.
```

**Template: Wrong network**
```
Sorry, you sent to [network]. We only support Base Network.
Funds sent to other networks cannot be recovered.
Please send USDC on Base Network.
```

**Template: Wrong token**
```
Sorry, you sent USDT. We only support USDC.
Please send USDC (not USDT) on Base Network.
```

---

## DO's and DON'Ts

### ✅ DO:
- Always verify on blockchain first
- Check existing balance before adding
- Use descriptive notes
- Respond within 1 hour
- Keep transaction records

### ❌ DON'T:
- Add credits without verification
- Add credits for wrong network
- Add credits for USDT (only USDC)
- Add credits twice for same transaction
- Forget to check existing balance

---

## Quick Commands

```bash
# Add AUTOMATON credits (AI Agent)
/admin_add_automaton_credits 123456789 3000 Deposit $30 USDC verified

# Check AUTOMATON credits
/admin_check_automaton_credits 123456789

# Add regular bot credits
/grant_credits 123456789 100

# Search user
/admin → Search User
```

---

## Remember

🤖 **AUTOMATON credits** = AI Agent only
📊 **Regular credits** = Bot features
⚠️ **Jangan sampai tertukar!**

---

**Last Updated**: 2026-02-22
**Quick Access**: Keep this card handy for fast reference!
