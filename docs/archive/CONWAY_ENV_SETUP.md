# Conway Integration - Environment Setup (Simplified)

## Overview
Setup environment variables untuk Conway Automaton integration. Jauh lebih simple karena Conway handles semua blockchain operations.

## Required Environment Variables (Simplified)

### 1. Telegram Bot
```bash
TELEGRAM_BOT_TOKEN=<your_bot_token>
```

### 2. Supabase Database
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=<your_anon_key>
SUPABASE_SERVICE_KEY=<your_service_role_key>
```

### 3. Conway Cloud API
```bash
# Conway API base URL
CONWAY_API_URL=https://api.conway.tech

# Conway API key (get from Conway dashboard)
CONWAY_API_KEY=<your_conway_api_key>
```

### 4. Admin Configuration
```bash
ADMIN_IDS=1187119989,7255533151
ADMIN_USER_ID=1187119989
```

## What's Removed (Conway Handles These)

### ❌ No Longer Needed
```bash
# Blockchain RPC (Conway handles this)
POLYGON_RPC_URL

# Wallet encryption (Conway manages wallets)
WALLET_ENCRYPTION_KEY

# Contract addresses (Conway handles deposits)
POLYGON_USDT_CONTRACT
POLYGON_USDC_CONTRACT
BASE_USDC_CONTRACT
```

## Quick Setup (Railway)

### Method 1: Railway Dashboard
1. Go to Railway → Your Project → Variables
2. Add these 7 variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `TELEGRAM_BOT_TOKEN` | Your bot token | From @BotFather |
| `SUPABASE_URL` | Your Supabase URL | From Supabase dashboard |
| `SUPABASE_KEY` | Your anon key | From Supabase dashboard |
| `SUPABASE_SERVICE_KEY` | Your service key | From Supabase dashboard |
| `CONWAY_API_URL` | `https://api.conway.tech` | Conway API base |
| `CONWAY_API_KEY` | Your Conway key | From Conway dashboard |
| `ADMIN_IDS` | `1187119989,7255533151` | Your admin IDs |

### Method 2: Railway CLI
```bash
railway variables set TELEGRAM_BOT_TOKEN=<your_token>
railway variables set SUPABASE_URL=<your_url>
railway variables set SUPABASE_KEY=<your_key>
railway variables set SUPABASE_SERVICE_KEY=<your_service_key>
railway variables set CONWAY_API_URL=https://api.conway.tech
railway variables set CONWAY_API_KEY=<your_conway_key>
railway variables set ADMIN_IDS=1187119989,7255533151
```

## Get Conway API Key

### Step 1: Sign Up
1. Go to https://conway.tech
2. Create account
3. Verify email

### Step 2: Create API Key
1. Go to Dashboard → API Keys
2. Click "Create New Key"
3. Name: "CryptoMentor Bot"
4. Permissions: Full access
5. Copy the key (starts with `ck_` or similar)

### Step 3: Test API Key
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.conway.tech/api/v1/health
```

Should return:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

## Test Environment

Create `test_conway_env.py`:
```python
import os
import requests

# Required variables
required = [
    'TELEGRAM_BOT_TOKEN',
    'SUPABASE_URL',
    'SUPABASE_KEY',
    'SUPABASE_SERVICE_KEY',
    'CONWAY_API_URL',
    'CONWAY_API_KEY',
    'ADMIN_IDS'
]

print("🔍 Checking environment variables...\n")

missing = []
for var in required:
    value = os.getenv(var)
    if value:
        if 'KEY' in var or 'TOKEN' in var:
            display = value[:8] + '...' + value[-4:]
        else:
            display = value
        print(f"✅ {var}: {display}")
    else:
        print(f"❌ {var}: MISSING")
        missing.append(var)

if missing:
    print(f"\n❌ Missing {len(missing)} variables")
    exit(1)

print("\n✅ All variables set!")

# Test Conway API
print("\n🔗 Testing Conway API...")
try:
    headers = {'Authorization': f'Bearer {os.getenv("CONWAY_API_KEY")}'}
    response = requests.get(
        f'{os.getenv("CONWAY_API_URL")}/api/v1/health',
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ Conway API connection successful!")
    else:
        print(f"❌ Conway API error: {response.status_code}")
except Exception as e:
    print(f"❌ Conway API connection failed: {e}")

print("\n✅ Environment ready for deployment!")
```

Run test:
```bash
python test_conway_env.py
```

## Deployment Checklist

- [ ] All 7 environment variables set in Railway
- [ ] Conway API key obtained and tested
- [ ] Supabase credentials verified
- [ ] Admin IDs configured
- [ ] Test script passes
- [ ] Ready to deploy

## Troubleshooting

### Error: "Conway API authentication failed"
**Fix:** 
1. Check API key is correct
2. Verify key hasn't expired
3. Regenerate key in Conway dashboard

### Error: "Supabase connection failed"
**Fix:**
1. Verify URL is correct
2. Check service role key is valid
3. Ensure database is not paused

### Error: "Missing environment variables"
**Fix:**
1. Run test script to identify missing vars
2. Add missing variables in Railway
3. Redeploy bot

## Security Notes

### API Key Security
- ✅ Store in Railway environment only
- ✅ Never commit to git
- ✅ Rotate every 180 days
- ✅ Use separate keys for dev/prod

### Simplified Security
With Conway handling wallets:
- ✅ No private keys to manage
- ✅ No encryption keys to rotate
- ✅ No blockchain security concerns
- ✅ Fewer attack vectors
- ✅ Simpler codebase

## Next Steps

After environment setup:
1. ✅ Run database migration (`002_automaton_simplified.sql`)
2. ✅ Test Conway API integration
3. ✅ Deploy bot to Railway
4. ✅ Test agent spawning
5. ✅ Test deposit flow

## Support

- **Conway API:** support@conway.tech
- **Supabase:** support@supabase.com
- **Railway:** help@railway.app

---

**Last Updated:** 2026-02-20
**Version:** 2.0.0 (Simplified for Conway)
**Status:** Ready for deployment
