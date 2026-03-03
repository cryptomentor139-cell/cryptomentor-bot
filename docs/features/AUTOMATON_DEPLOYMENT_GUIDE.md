# Automaton Integration - Deployment Guide

## Overview

This guide covers deploying the Automaton Integration feature to production on Railway. The Automaton system enables users to spawn and manage autonomous AI trading agents that consume Conway credits as fuel.

## Prerequisites

- Railway account with active project
- Supabase account with database configured
- Conway Cloud API access
- Base network RPC URL
- Telegram Bot Token

## Environment Variables

### Required Variables

Add these to your Railway environment:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=<your_bot_token>

# Database (Supabase)
SUPABASE_URL=<your_supabase_url>
SUPABASE_KEY=<your_supabase_anon_key>
SUPABASE_SERVICE_KEY=<your_supabase_service_role_key>

# Blockchain (Base Network)
BASE_RPC_URL=https://mainnet.base.org
BASE_USDC_ADDRESS=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

# Conway Cloud API
CONWAY_API_URL=https://api.conway.tech
CONWAY_API_KEY=<your_conway_api_key>

# Admin
ADMIN_IDS=<comma_separated_admin_telegram_ids>
ADMIN1=<primary_admin_id>
ADMIN2=<secondary_admin_id>

# Background Services (Optional - defaults provided)
DEPOSIT_CHECK_INTERVAL=30          # seconds (default: 30)
BALANCE_CHECK_INTERVAL=3600        # seconds (default: 3600 = 1 hour)
FEE_COLLECTOR_INTERVAL=300         # seconds (default: 300 = 5 minutes)
MIN_DEPOSIT_USDC=5.0               # minimum deposit (default: 5.0)
MIN_CONFIRMATIONS=12               # block confirmations (default: 12)
```

### Optional Variables

```bash
# Wallet Encryption (if using custodial wallets)
WALLET_ENCRYPTION_KEY=<fernet_key_base64>

# Monitoring
SENTRY_DSN=<sentry_dsn>
LOG_LEVEL=INFO
```

## Database Migration

### Step 1: Run Migration Scripts

The database tables are already created in Supabase. Verify they exist:

```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'custodial_wallets',
    'wallet_deposits',
    'wallet_withdrawals',
    'user_automatons',
    'automaton_transactions',
    'platform_revenue'
);
```

### Step 2: Verify Table Structure

Run this query to verify the `user_automatons` table:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user_automatons';
```

Expected columns:
- id (uuid)
- user_id (bigint)
- agent_wallet (text)
- agent_name (text)
- conway_deposit_address (text)
- genesis_prompt (text)
- conway_credits (numeric)
- survival_tier (text)
- status (text)
- created_at (timestamp)
- last_active (timestamp)
- total_earnings (numeric)
- total_expenses (numeric)

### Step 3: Create Indexes (if not exist)

```sql
-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_automaton_user_id ON user_automatons(user_id);
CREATE INDEX IF NOT EXISTS idx_automaton_status ON user_automatons(status);
CREATE INDEX IF NOT EXISTS idx_transaction_automaton_id ON automaton_transactions(automaton_id);
CREATE INDEX IF NOT EXISTS idx_transaction_type ON automaton_transactions(type);
CREATE INDEX IF NOT EXISTS idx_revenue_timestamp ON platform_revenue(timestamp);
```

## Railway Deployment

### Step 1: Update Railway Environment

1. Go to Railway dashboard
2. Select your project
3. Click on "Variables" tab
4. Add all required environment variables listed above
5. Click "Deploy" to apply changes

### Step 2: Verify Deployment

After deployment, check the logs:

```bash
# Look for these success messages:
✅ Automaton Manager initialized
✅ Deposit Monitor initialized
✅ Balance Monitor initialized
✅ Revenue Manager initialized
✅ Automaton handlers registered
✅ Admin automaton handlers registered
✅ Background Services initialized
🤖 Automaton Background Services started
```

### Step 3: Test Basic Functionality

1. **Test Conway API Connection:**
   ```bash
   # In Railway logs, look for:
   ✅ Conway API health check passed
   ```

2. **Test Database Connection:**
   ```bash
   # Should see:
   ✅ Supabase connection established
   ```

3. **Test Bot Commands:**
   - Send `/spawn_agent TestAgent` to bot
   - Should receive response about Automaton access requirement

## Conway Cloud API Setup

### Step 1: Get API Key

1. Sign up at https://conway.tech
2. Navigate to API settings
3. Generate new API key
4. Copy key to `CONWAY_API_KEY` environment variable

### Step 2: Verify API Access

Test the API connection:

```python
# Run this in Railway console or locally:
python test_conway_env.py
```

Expected output:
```
✅ Conway API health check passed
✅ Deposit address generation works
✅ Credit balance retrieval works
```

## Base Network Configuration

### RPC Endpoints

Primary (recommended):
```
https://mainnet.base.org
```

Alternatives (if primary fails):
```
https://base.llamarpc.com
https://base-mainnet.public.blastapi.io
```

### USDC Contract

Base USDC address:
```
0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
```

Verify on BaseScan:
https://basescan.org/token/0x833589fcd6edb6e08f4c7c32d4f71b54bda02913

## Background Services

### Service Overview

Three background services run continuously:

1. **Deposit Monitor** (30s interval)
   - Monitors custodial wallets for USDC deposits
   - Processes deposits and credits Conway credits
   - Sends deposit confirmation notifications

2. **Balance Monitor** (1h interval)
   - Checks all active agents for low balances
   - Sends warning alerts (< 5000 credits)
   - Sends critical alerts (< 1000 credits)

3. **Performance Fee Collector** (5m interval)
   - Collects 20% performance fees from profitable agents
   - Records fees in platform_revenue table
   - Updates agent balances

### Monitoring Services

Check service health:

```bash
# In Railway logs, look for:
🚀 Deposit Monitor service started
🚀 Balance Monitor service started
🚀 Performance Fee Collector service started
```

### Troubleshooting Services

If a service fails:

1. Check Railway logs for error messages
2. Verify environment variables are set
3. Check database connectivity
4. Verify Conway API access
5. Restart the deployment

## User Documentation

### For Users

#### How to Spawn an Agent

1. Ensure you have Automaton access (Rp2,000,000 one-time fee)
2. Ensure you have premium subscription
3. Ensure you have >= 100,000 credits
4. Send `/spawn_agent <name>` to bot
5. Bot will create agent and provide deposit address

#### How to Fund an Agent

1. Send `/deposit` to see your deposit address
2. Send USDC to the address (Base network recommended)
3. Minimum deposit: 5 USDC
4. Credits will be added automatically after 12 confirmations
5. Conversion rate: 1 USDC = 98 Conway Credits (after 2% fee)

#### How to Check Agent Status

1. Send `/agent_status` to bot
2. View agent balance, survival tier, and runtime estimate
3. View total earnings and expenses

#### How to View Transaction History

1. Send `/agent_logs` to bot
2. View last 20 transactions
3. See deposits, earnings, expenses, and fees

### For Admins

#### Admin Commands

- `/admin_wallets` - View wallet summary and platform stats
- `/admin_wallet_details <user_id>` - View specific user wallet
- `/admin_revenue [period]` - View revenue report (daily/weekly/monthly/all)
- `/admin_agents` - View agent statistics and top performers

#### Monitoring Platform Health

1. Check `/admin_wallets` for overall stats
2. Check `/admin_agents` for agent survival rate
3. Check `/admin_revenue daily` for daily revenue
4. Monitor Railway logs for errors

## Security Considerations

### API Keys

- Never commit API keys to git
- Use Railway environment variables
- Rotate keys every 90 days
- Use separate keys for staging/production

### Database Access

- Use Supabase service role key for admin operations
- Use anon key for user operations
- Enable Row Level Security (RLS) on sensitive tables
- Regularly backup database

### Admin Access

- Limit admin IDs to trusted users
- Use multiple admin IDs for redundancy
- Monitor admin command usage
- Implement audit logging

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Agent Metrics:**
   - Total active agents
   - Survival rate (%)
   - Average balance
   - Dead agents count

2. **Revenue Metrics:**
   - Daily revenue
   - Revenue by source (deposit fees, performance fees, spawn fees)
   - Top revenue-generating agents

3. **System Metrics:**
   - Deposit processing time
   - Conway API response time
   - Background service uptime
   - Error rates

### Setting Up Alerts

1. **Critical Alerts:**
   - Conway API failures (after 3 retries)
   - Database connection failures
   - Deposit processing failures
   - Agent spawn failures

2. **Warning Alerts:**
   - High error rates (> 5% of requests)
   - Slow API responses (> 5s)
   - Low agent survival rate (< 80%)

3. **Info Alerts:**
   - Daily revenue summary
   - New agent spawns
   - Large deposits (> 100 USDC)

## Troubleshooting

### Common Issues

#### 1. Conway API Connection Failed

**Symptoms:**
```
❌ Conway API health check failed
```

**Solutions:**
- Verify `CONWAY_API_KEY` is set correctly
- Check `CONWAY_API_URL` is correct
- Test API manually with curl
- Check Conway Cloud status page

#### 2. Deposit Not Detected

**Symptoms:**
- User deposited USDC but credits not added

**Solutions:**
- Verify deposit on BaseScan
- Check if deposit is >= 5 USDC
- Verify correct network (Base)
- Check deposit monitor logs
- Verify RPC connection

#### 3. Background Services Not Running

**Symptoms:**
```
⚠️ Automaton Background Services failed to start
```

**Solutions:**
- Check Railway logs for error details
- Verify all environment variables set
- Restart deployment
- Check database connectivity

#### 4. Agent Spawn Failed

**Symptoms:**
- User gets error when spawning agent

**Solutions:**
- Verify user has Automaton access
- Verify user is premium
- Verify user has >= 100,000 credits
- Check Conway API connectivity
- Check database for errors

## Rollback Plan

If critical issues occur:

1. **Disable Spawn Functionality:**
   - Set environment variable: `AUTOMATON_ENABLED=false`
   - Redeploy

2. **Stop Background Services:**
   - Comment out background service startup in bot.py
   - Redeploy

3. **Notify Users:**
   - Use `/broadcast` to inform users of maintenance
   - Provide ETA for fix

4. **Fix Issues:**
   - Test fixes in staging environment
   - Run all tests
   - Verify with property-based tests

5. **Re-enable Features:**
   - Remove `AUTOMATON_ENABLED=false`
   - Uncomment background services
   - Redeploy
   - Monitor closely for 24 hours

## Support

### Getting Help

- Check Railway logs first
- Review this documentation
- Check Conway Cloud documentation
- Contact Conway support for API issues
- Check Supabase status for database issues

### Reporting Issues

When reporting issues, include:
- Error message from logs
- Steps to reproduce
- Environment (production/staging)
- Timestamp of issue
- User ID (if applicable)

## Next Steps

After successful deployment:

1. ✅ Test spawn workflow end-to-end
2. ✅ Test deposit workflow with small amount
3. ✅ Verify notifications work
4. ✅ Test admin commands
5. ✅ Monitor for 24 hours
6. ✅ Announce feature to users

## Conclusion

The Automaton Integration is now deployed and ready for production use. Monitor the system closely for the first few days and be prepared to address any issues quickly.

For questions or issues, contact the development team.

---

**Last Updated:** 2024
**Version:** 1.0
**Status:** Production Ready
