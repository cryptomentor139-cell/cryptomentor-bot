# ⚡ Quick Fix Reference - Deposit Address

## Problem
```
❌ Gagal generate deposit address. Silakan coba lagi.
```

## Solution
✅ Use centralized custodial wallet

## Implementation

### Code Change
**File:** `app/conway_integration.py`

```python
def generate_deposit_address(self, user_id: int, agent_name: str) -> Optional[str]:
    centralized_wallet = os.getenv('CENTRALIZED_WALLET_ADDRESS')
    return centralized_wallet
```

### Environment Variable
```bash
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822
```

## Deployment

### 1. Code (✅ Done)
```bash
git add -A
git commit -m "Fix: Use centralized custodial wallet"
git push origin main
```

### 2. Railway (⏳ To Do)
1. Go to Railway dashboard
2. Add variable: `CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822`
3. Wait for auto-deploy (~2-5 min)

### 3. Test (⏳ To Do)
```
/spawn_agent TestBot
```

Expected:
```
✅ Agent Berhasil Dibuat!
📍 Deposit Address:
0x63116672bef9f26fd906cd2a57550f7a13925822
```

## Key Info

| Item | Value |
|------|-------|
| Address | `0x63116672bef9f26fd906cd2a57550f7a13925822` |
| Network | Base (Chain ID: 8453) |
| Token | USDC |
| Minimum | $30 USDC (3,000 credits) |
| Conversion | 1 USDC = 100 credits |

## How It Works

```
All Users → Same Address → Track by user_id in DB
```

## Files Created

1. ✅ `FIX_DEPOSIT_ADDRESS_COMPLETE.md` - Full technical details
2. ✅ `CARA_DEPOSIT_USDC.md` - User guide
3. ✅ `DEPOSIT_ADDRESS_FIX_SUMMARY.md` - Summary
4. ✅ `DEPLOY_DEPOSIT_FIX_NOW.md` - Deployment guide
5. ✅ `test_deposit_address_fix.py` - Test script
6. ✅ `test_spawn_agent_flow.py` - Integration test

## Tests

```bash
# Test deposit address generation
python test_deposit_address_fix.py

# Test complete spawn flow
python test_spawn_agent_flow.py
```

Both: ✅ PASSED

## Status

- [x] Code fixed
- [x] Tests passing
- [x] Documentation created
- [x] Code pushed to GitHub
- [ ] Environment variable added to Railway
- [ ] Deployed to production
- [ ] Tested in production

## Next Action

**Add to Railway:**
```
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822
```

Then test with `/spawn_agent` command.

---

**That's it!** Simple fix, big impact. 🚀
