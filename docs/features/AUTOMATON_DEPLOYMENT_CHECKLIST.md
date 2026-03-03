# Automaton Integration - Deployment Checklist

## Overview
This checklist ensures all components are properly configured before deploying the Automaton integration feature to production.

## Pre-Deployment Checklist

### Phase 1: Database Setup ✅ (Task 1)

- [ ] **1.1 Run Database Migration**
  ```bash
  # In Supabase SQL Editor, run:
  Bismillah/migrations/001_automaton_tables.sql
  ```
  - [ ] Verify all 6 tables created successfully
  - [ ] Verify all indexes created
  - [ ] Check table constraints are active

- [ ] **1.2 Verify Table Creation**
  ```sql
  -- Run this query in Supabase SQL Editor
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
  )
  ORDER BY table_name;
  ```
  - [ ] Should return 6 rows
  - [ ] All table names present

- [ ] **1.3 Verify Index Creation**
  ```sql
  -- Run this query in Supabase SQL Editor
  SELECT tablename, indexname 
  FROM pg_indexes 
  WHERE schemaname = 'public' 
  AND tablename IN (
    'custodial_wallets',
    'wallet_deposits',
    'wallet_withdrawals', 
    'user_automatons',
    'automaton_transactions',
    'platform_revenue'
  )
  ORDER BY tablename, indexname;
  ```
  - [ ] Should return 20+ indexes
  - [ ] All critical indexes present

### Phase 2: Environment Variables Setup

- [ ] **2.1 Generate Encryption Key**
  ```bash
  python generate_encryption_key.py
  ```
  - [ ] Key generated successfully
  - [ ] Key backed up securely (password manager)
  - [ ] Rotation reminder set (90 days)

- [ ] **2.2 Configure Railway Variables**
  - [ ] TELEGRAM_BOT_TOKEN
  - [ ] SUPABASE_URL
  - [ ] SUPABASE_KEY
  - [ ] SUPABASE_SERVICE_KEY
  - [ ] POLYGON_RPC_URL
  - [ ] WALLET_ENCRYPTION_KEY
  - [ ] CONWAY_API_URL
  - [ ] CONWAY_API_KEY
  - [ ] ADMIN_IDS
  - [ ] ADMIN_USER_ID
  - [ ] POLYGON_USDT_CONTRACT
  - [ ] POLYGON_USDC_CONTRACT

- [ ] **2.3 Test Environment Variables**
  ```bash
  python test_env.py
  ```
  - [ ] All required variables present
  - [ ] Encryption key test passed
  - [ ] Admin IDs valid
  - [ ] Polygon RPC connection working
  - [ ] Supabase connection working

### Phase 3: Polygon RPC Setup

- [ ] **3.1 Choose RPC Provider**
  - [ ] Option A: Alchemy (Recommended)
  - [ ] Option B: Infura
  - [ ] Option C: QuickNode
  - [ ] Option D: Public RPC (Not recommended)

- [ ] **3.2 Configure RPC Endpoint**
  - [ ] API key obtained
  - [ ] Polygon network selected
  - [ ] HTTPS endpoint configured
  - [ ] Rate limits understood

- [ ] **3.3 Test RPC Connection**
  ```python
  from web3 import Web3
  w3 = Web3(Web3.HTTPProvider(os.getenv('POLYGON_RPC_URL')))
  print(f"Connected: {w3.is_connected()}")
  print(f"Latest block: {w3.eth.block_number}")
  print(f"Chain ID: {w3.eth.chain_id}")  # Should be 137
  ```
  - [ ] Connection successful
  - [ ] Chain ID is 137 (Polygon Mainnet)
  - [ ] Can fetch latest block

### Phase 4: Conway Cloud API Setup

- [ ] **4.1 Get Conway API Key**
  - [ ] Account created on Conway Cloud
  - [ ] API key generated
  - [ ] API key added to Railway variables

- [ ] **4.2 Test Conway API**
  ```python
  import requests
  headers = {'Authorization': f'Bearer {os.getenv("CONWAY_API_KEY")}'}
  response = requests.get(f'{os.getenv("CONWAY_API_URL")}/health', headers=headers)
  print(f"Status: {response.status_code}")
  ```
  - [ ] Authentication successful
  - [ ] API responding correctly
  - [ ] Rate limits understood

### Phase 5: Security Verification

- [ ] **5.1 Encryption Security**
  - [ ] Master key stored only in Railway (not in code)
  - [ ] Master key backed up securely
  - [ ] Encryption test passed
  - [ ] Decryption test passed

- [ ] **5.2 Access Control**
  - [ ] Admin IDs configured correctly
  - [ ] Only trusted admins added
  - [ ] Admin commands tested

- [ ] **5.3 API Security**
  - [ ] All API keys are valid
  - [ ] No API keys in git repository
  - [ ] Rate limiting configured
  - [ ] Error handling in place

### Phase 6: Code Deployment

- [ ] **6.1 Install Dependencies**
  ```bash
  pip install web3 cryptography supabase
  ```
  - [ ] web3 installed (blockchain interaction)
  - [ ] cryptography installed (wallet encryption)
  - [ ] supabase installed (database)

- [ ] **6.2 Deploy to Railway**
  ```bash
  git add .
  git commit -m "Add Automaton integration - Task 1 complete"
  git push origin main
  ```
  - [ ] Code pushed to repository
  - [ ] Railway auto-deploy triggered
  - [ ] Deployment successful

- [ ] **6.3 Verify Deployment**
  - [ ] Bot started without errors
  - [ ] All services running
  - [ ] Logs show no critical errors
  - [ ] Health check passing

### Phase 7: Functional Testing

- [ ] **7.1 Test Database Connection**
  - [ ] Bot can connect to Supabase
  - [ ] Can query existing users table
  - [ ] Can query new automaton tables

- [ ] **7.2 Test Encryption**
  - [ ] Can encrypt test data
  - [ ] Can decrypt test data
  - [ ] Round-trip encryption works

- [ ] **7.3 Test Polygon Connection**
  - [ ] Can connect to Polygon RPC
  - [ ] Can query USDT contract
  - [ ] Can query USDC contract
  - [ ] Can check wallet balances

- [ ] **7.4 Test Conway API**
  - [ ] Can authenticate with API
  - [ ] Can make test API calls
  - [ ] Error handling works

### Phase 8: Monitoring Setup

- [ ] **8.1 Configure Logging**
  - [ ] Structured logging enabled
  - [ ] Log levels configured
  - [ ] Sensitive data not logged

- [ ] **8.2 Set Up Alerts**
  - [ ] Critical error alerts to admin
  - [ ] RPC connection failure alerts
  - [ ] Conway API failure alerts
  - [ ] Database connection alerts

- [ ] **8.3 Monitor Resources**
  - [ ] CPU usage normal
  - [ ] Memory usage normal
  - [ ] Network usage normal
  - [ ] Database connections normal

## Post-Deployment Verification

### Immediate Checks (First 5 minutes)

- [ ] Bot responds to /start command
- [ ] No critical errors in logs
- [ ] Database queries working
- [ ] All services connected

### Short-term Checks (First hour)

- [ ] No memory leaks
- [ ] No connection drops
- [ ] Error rate acceptable
- [ ] Response times normal

### Medium-term Checks (First 24 hours)

- [ ] All background services stable
- [ ] No unexpected errors
- [ ] Performance metrics normal
- [ ] User experience good

## Rollback Plan

If critical issues are discovered:

1. **Immediate Actions**
   - [ ] Stop bot deployment
   - [ ] Notify all admins
   - [ ] Document the issue

2. **Rollback Steps**
   - [ ] Revert to previous Railway deployment
   - [ ] Verify bot is working
   - [ ] Notify users of maintenance

3. **Investigation**
   - [ ] Review error logs
   - [ ] Identify root cause
   - [ ] Fix issues in development
   - [ ] Test thoroughly

4. **Re-deployment**
   - [ ] Fix verified in staging
   - [ ] All tests passing
   - [ ] Deploy to production
   - [ ] Monitor closely

## Success Criteria

Task 1 is complete when:

- [x] All 6 database tables created in Supabase
- [x] All indexes created successfully
- [x] All environment variables configured in Railway
- [x] Encryption key generated and tested
- [x] Polygon RPC connection working
- [x] Conway API authentication working
- [x] Bot deployed to Railway successfully
- [x] All tests passing
- [x] No critical errors in logs
- [x] Ready for Task 2 (Wallet Manager Implementation)

## Next Steps

After Task 1 is complete:

1. ✅ Proceed to Task 2: Wallet Manager Implementation
2. ✅ Implement wallet generation with encryption
3. ✅ Implement database persistence
4. ✅ Write property-based tests
5. ✅ Test end-to-end wallet creation

## Documentation

- [x] Database migration script created
- [x] Environment setup guide created
- [x] Encryption key generator created
- [x] Environment test script created
- [x] Deployment checklist created

## Support Contacts

If you encounter issues:

- **Database Issues:** Check Supabase dashboard and logs
- **RPC Issues:** Contact your RPC provider support
- **Conway API Issues:** Contact Conway Cloud support
- **Bot Issues:** Check Railway logs and error messages

## Notes

- Keep this checklist updated as you progress
- Mark items as complete with [x]
- Document any issues encountered
- Update rollback plan if needed

---

**Task Status:** ✅ Task 1 Complete - Database Schema and Infrastructure Setup
**Next Task:** Task 2 - Wallet Manager Implementation
**Last Updated:** 2026-02-20
**Version:** 1.0.0
