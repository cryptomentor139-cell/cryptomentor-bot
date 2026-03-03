# Railway Environment Variables Setup - Automaton Integration

## Overview
This document lists all required environment variables for the Automaton integration feature. These variables must be configured in Railway before deploying the bot.

## Required Environment Variables

### 1. Telegram Bot Configuration
```bash
# Your Telegram bot token from @BotFather
TELEGRAM_BOT_TOKEN=<your_bot_token>
```

### 2. Supabase Database Configuration
```bash
# Supabase project URL
SUPABASE_URL=https://your-project.supabase.co

# Supabase anon/public key (for client-side operations)
SUPABASE_KEY=<your_anon_key>

# Supabase service role key (for admin operations - KEEP SECRET!)
SUPABASE_SERVICE_KEY=<your_service_role_key>
```

### 3. Blockchain Configuration (Polygon Network)
```bash
# Polygon RPC URL - Use one of these providers:
# Option 1: Alchemy (Recommended)
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/<your_api_key>

# Option 2: Infura
# POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/<your_project_id>

# Option 3: QuickNode
# POLYGON_RPC_URL=https://your-endpoint.matic.quiknode.pro/<your_api_key>

# Option 4: Public RPC (Not recommended for production)
# POLYGON_RPC_URL=https://polygon-rpc.com
```

### 4. Wallet Encryption Configuration
```bash
# Master encryption key for private keys (Fernet key format)
# Generate using: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
WALLET_ENCRYPTION_KEY=<your_fernet_key_base64>

# CRITICAL: This key encrypts all user wallet private keys
# - NEVER commit this to git
# - NEVER share this key
# - Store backup in secure location (password manager)
# - Rotate every 90 days
```

### 5. Conway Cloud API Configuration
```bash
# Conway Cloud API base URL
CONWAY_API_URL=https://api.conway.tech

# Conway Cloud API key (get from Conway dashboard)
CONWAY_API_KEY=<your_conway_api_key>
```

### 6. Admin Configuration
```bash
# Admin Telegram IDs (comma-separated for multiple admins)
ADMIN_IDS=1187119989,7255533151

# Primary admin ID (for critical notifications)
ADMIN_USER_ID=1187119989
```

### 7. Polygon Contract Addresses (Pre-configured)
```bash
# USDT contract on Polygon
POLYGON_USDT_CONTRACT=0xc2132D05D31c914a87C6611C10748AEb04B58e8F

# USDC contract on Polygon
POLYGON_USDC_CONTRACT=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
```

## How to Set Environment Variables in Railway

### Method 1: Railway Dashboard (Recommended)
1. Go to your Railway project dashboard
2. Click on your service (bot)
3. Navigate to "Variables" tab
4. Click "New Variable"
5. Add each variable name and value
6. Click "Add" to save

### Method 2: Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Set variables one by one
railway variables set TELEGRAM_BOT_TOKEN=<your_token>
railway variables set SUPABASE_URL=<your_url>
# ... repeat for all variables
```

### Method 3: Bulk Import (JSON)
Create a file `railway-vars.json`:
```json
{
  "TELEGRAM_BOT_TOKEN": "your_token",
  "SUPABASE_URL": "your_url",
  "SUPABASE_KEY": "your_key",
  "SUPABASE_SERVICE_KEY": "your_service_key",
  "POLYGON_RPC_URL": "your_rpc_url",
  "WALLET_ENCRYPTION_KEY": "your_encryption_key",
  "CONWAY_API_URL": "https://api.conway.tech",
  "CONWAY_API_KEY": "your_conway_key",
  "ADMIN_IDS": "1187119989,7255533151",
  "ADMIN_USER_ID": "1187119989",
  "POLYGON_USDT_CONTRACT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
  "POLYGON_USDC_CONTRACT": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
}
```

Then import:
```bash
railway variables set --from-file railway-vars.json
```

## Generating Required Keys

### 1. Generate Wallet Encryption Key
```python
# Run this Python script to generate a Fernet encryption key
from cryptography.fernet import Fernet

# Generate key
key = Fernet.generate_key()
print(f"WALLET_ENCRYPTION_KEY={key.decode()}")

# IMPORTANT: Save this key securely!
# You cannot decrypt wallets without this key
```

Or use this one-liner:
```bash
python -c "from cryptography.fernet import Fernet; print(f'WALLET_ENCRYPTION_KEY={Fernet.generate_key().decode()}')"
```

### 2. Get Polygon RPC URL

#### Option A: Alchemy (Recommended)
1. Go to https://www.alchemy.com/
2. Sign up for free account
3. Create new app
4. Select "Polygon" network
5. Copy the HTTPS URL

#### Option B: Infura
1. Go to https://infura.io/
2. Sign up for free account
3. Create new project
4. Select "Polygon PoS" network
5. Copy the HTTPS endpoint

#### Option C: QuickNode
1. Go to https://www.quicknode.com/
2. Sign up for free trial
3. Create Polygon endpoint
4. Copy the HTTPS URL

### 3. Get Conway Cloud API Key
1. Go to Conway Cloud dashboard
2. Navigate to API settings
3. Generate new API key
4. Copy the key (starts with `ck_` or similar)

## Security Best Practices

### Critical Security Rules
1. **NEVER commit environment variables to git**
   - Add `.env` to `.gitignore`
   - Use Railway's secure variable storage

2. **Rotate sensitive keys regularly**
   - Wallet encryption key: Every 90 days
   - API keys: Every 180 days
   - Bot token: If compromised

3. **Backup encryption key securely**
   - Store in password manager (1Password, Bitwarden)
   - Keep offline backup in safe location
   - Document key rotation procedure

4. **Limit admin access**
   - Only add trusted admin IDs
   - Review admin list regularly
   - Log all admin operations

5. **Monitor API usage**
   - Set up alerts for unusual activity
   - Review RPC node usage monthly
   - Check Conway API quota

## Verification Checklist

After setting all variables, verify:

- [ ] Bot starts without errors
- [ ] Database connection successful
- [ ] Polygon RPC connection working
- [ ] Conway API authentication successful
- [ ] Wallet encryption/decryption working
- [ ] Admin commands accessible
- [ ] All environment variables loaded

## Testing Environment Variables

Create a test script `test_env.py`:
```python
import os
from cryptography.fernet import Fernet

# Test all required variables
required_vars = [
    'TELEGRAM_BOT_TOKEN',
    'SUPABASE_URL',
    'SUPABASE_KEY',
    'SUPABASE_SERVICE_KEY',
    'POLYGON_RPC_URL',
    'WALLET_ENCRYPTION_KEY',
    'CONWAY_API_URL',
    'CONWAY_API_KEY',
    'ADMIN_IDS'
]

print("🔍 Checking environment variables...\n")

missing = []
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if 'KEY' in var or 'TOKEN' in var:
            display = value[:8] + '...' + value[-4:]
        else:
            display = value
        print(f"✅ {var}: {display}")
    else:
        print(f"❌ {var}: MISSING")
        missing.append(var)

if missing:
    print(f"\n❌ Missing {len(missing)} required variables:")
    for var in missing:
        print(f"   - {var}")
else:
    print("\n✅ All required variables are set!")

# Test encryption key
print("\n🔐 Testing wallet encryption key...")
try:
    key = os.getenv('WALLET_ENCRYPTION_KEY')
    if key:
        cipher = Fernet(key.encode())
        test_data = b"test_private_key"
        encrypted = cipher.encrypt(test_data)
        decrypted = cipher.decrypt(encrypted)
        if decrypted == test_data:
            print("✅ Encryption key is valid!")
        else:
            print("❌ Encryption key test failed!")
    else:
        print("❌ Encryption key not set!")
except Exception as e:
    print(f"❌ Encryption key error: {e}")
```

Run the test:
```bash
python test_env.py
```

## Troubleshooting

### Issue: "Encryption key invalid"
**Solution:** Regenerate key using the Python script above

### Issue: "RPC connection failed"
**Solution:** 
- Check RPC URL is correct
- Verify API key is valid
- Try alternative RPC provider

### Issue: "Conway API authentication failed"
**Solution:**
- Verify API key is correct
- Check API key hasn't expired
- Contact Conway support

### Issue: "Database connection failed"
**Solution:**
- Verify Supabase URL is correct
- Check service role key is valid
- Ensure database is not paused

## Next Steps

After setting up all environment variables:

1. ✅ Run database migration script (`001_automaton_tables.sql`)
2. ✅ Test environment variables (`python test_env.py`)
3. ✅ Deploy bot to Railway
4. ✅ Verify all services running
5. ✅ Test wallet generation
6. ✅ Test deposit detection (testnet first)
7. ✅ Enable production features

## Support

If you encounter issues:
1. Check Railway logs for error messages
2. Verify all environment variables are set correctly
3. Test each component individually
4. Contact support with error logs

---

**Last Updated:** 2026-02-20
**Version:** 1.0.0
**Status:** Ready for deployment
