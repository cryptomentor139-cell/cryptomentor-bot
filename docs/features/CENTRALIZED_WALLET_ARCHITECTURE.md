# 🏦 Centralized Wallet Architecture - Conway Integration

## 📊 Perubahan Arsitektur

### ❌ Arsitektur Lama (Custodial Wallet Per-User):
```
User 1 → Wallet A (0x1234...) → Monitor deposit → Convert to credits
User 2 → Wallet B (0x5678...) → Monitor deposit → Convert to credits
User 3 → Wallet C (0x9abc...) → Monitor deposit → Convert to credits
```

**Masalah:**
- Perlu manage banyak wallet
- Perlu encryption key untuk private keys
- Kompleks untuk tracking
- Tidak terintegrasi dengan Conway Dashboard

### ✅ Arsitektur Baru (Centralized Wallet):
```
User 1 ┐
User 2 ├→ SATU WALLET (0x63116672bef9f26fd906cd2a57550f7a13925822)
User 3 ┘     ↓
         Conway Dashboard
              ↓
         Auto-convert ke Conway Credits
```

**Keuntungan:**
- ✅ Satu wallet untuk semua user
- ✅ Terintegrasi langsung dengan Conway Dashboard
- ✅ Auto-convert USDT/USDC → Conway Credits
- ✅ Tidak perlu encryption key
- ✅ Lebih mudah di-manage
- ✅ Tracking lebih simple

## 🔄 Cara Kerja Baru

### 1. User Deposit Flow:
```
1. User klik "💰 Deposit Now"
2. Bot tampilkan wallet address: 0x63116672bef9f26fd906cd2a57550f7a13925822
3. User kirim USDT/USDC ke address tersebut
4. User input transaction hash di bot
5. Bot verify transaction on-chain
6. Bot update balance user di database
7. Conway Dashboard auto-convert ke credits
```

### 2. Tracking System:
```
Database Table: user_deposits
- user_id (Telegram ID)
- tx_hash (Transaction hash)
- amount_usdt (Jumlah USDT)
- amount_usdc (Jumlah USDC)
- conway_credits (Credits yang didapat)
- status (pending/confirmed/credited)
- created_at
- confirmed_at
```

### 3. Credit Conversion:
```
Conway Dashboard akan otomatis:
1. Detect deposit ke wallet 0x6311...5822
2. Convert USDT/USDC → Conway Credits
3. Credits masuk ke pool
4. Bot query Conway API untuk get balance
5. Bot assign credits ke user yang deposit
```

## 🛠️ Implementasi

### File yang Perlu Diubah:

1. **menu_handlers.py**
   - Ubah `handle_automaton_first_deposit()`
   - Tidak perlu generate wallet lagi
   - Tampilkan centralized wallet address
   - Minta user input tx hash setelah deposit

2. **database schema**
   - Buat table baru: `user_deposits`
   - Hapus/deprecate: `custodial_wallets` table

3. **deposit_monitor.py**
   - Monitor deposits ke centralized wallet
   - Match deposit dengan user berdasarkan tx hash
   - Update user balance

4. **conway_integration.py**
   - Query Conway API untuk total credits
   - Distribute credits ke user

### Environment Variables:

```env
# Centralized Wallet (Conway Dashboard)
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822

# Conway API (untuk query credits)
CONWAY_API_KEY=cnwy_k_DNll3zray_o4ccEpRmW0G6pK68BENY73
CONWAY_API_URL=https://api.conway.tech

# Blockchain RPC (untuk verify transactions)
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/your_api_key
BASE_RPC_URL=https://mainnet.base.org
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc

# Tidak perlu lagi:
# ENCRYPTION_KEY (tidak perlu karena tidak ada private keys)
```

## 📝 Migration Plan

### Step 1: Database Migration
```sql
-- Create new table for deposits
CREATE TABLE user_deposits (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    tx_hash VARCHAR(66) NOT NULL UNIQUE,
    network VARCHAR(20) NOT NULL, -- 'polygon', 'base', 'arbitrum'
    token VARCHAR(10) NOT NULL, -- 'USDT', 'USDC'
    amount DECIMAL(18, 6) NOT NULL,
    conway_credits DECIMAL(18, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'confirmed', 'credited'
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP,
    credited_at TIMESTAMP
);

-- Index for faster queries
CREATE INDEX idx_user_deposits_user_id ON user_deposits(user_id);
CREATE INDEX idx_user_deposits_tx_hash ON user_deposits(tx_hash);
CREATE INDEX idx_user_deposits_status ON user_deposits(status);

-- User credits balance (aggregate)
CREATE TABLE user_credits (
    user_id BIGINT PRIMARY KEY,
    total_deposited_usdt DECIMAL(18, 6) DEFAULT 0,
    total_deposited_usdc DECIMAL(18, 6) DEFAULT 0,
    total_conway_credits DECIMAL(18, 2) DEFAULT 0,
    available_credits DECIMAL(18, 2) DEFAULT 0,
    spent_credits DECIMAL(18, 2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Step 2: Update Code
1. Update `menu_handlers.py` - new deposit flow
2. Create `tx_verifier.py` - verify transactions on-chain
3. Update `deposit_monitor.py` - monitor centralized wallet
4. Update `conway_integration.py` - credit distribution

### Step 3: Testing
1. Test deposit flow dengan testnet
2. Verify transaction verification
3. Test credit distribution
4. Test Conway API integration

### Step 4: Deployment
1. Run database migration
2. Deploy updated code
3. Update environment variables
4. Monitor first deposits

## 🔐 Security Considerations

### Keamanan Wallet:
- ⚠️ Wallet 0x6311...5822 harus di-manage dengan aman
- Private key harus disimpan di Conway Dashboard
- Tidak perlu expose private key ke bot
- Bot hanya perlu wallet address untuk display

### Keamanan Transaction:
- Verify transaction on-chain sebelum credit
- Check transaction confirmation (min 12 blocks)
- Validate amount dan token contract
- Prevent double-spending dengan tx_hash unique constraint

### Keamanan Credits:
- Track semua deposit di database
- Audit log untuk credit distribution
- Rate limiting untuk prevent abuse
- Admin dashboard untuk monitoring

## 📊 Monitoring & Analytics

### Metrics to Track:
1. Total deposits (USDT + USDC)
2. Total Conway credits distributed
3. Average deposit per user
4. Deposit success rate
5. Transaction confirmation time
6. Conway API response time

### Alerts:
- Large deposits (> $1000)
- Failed transaction verifications
- Conway API errors
- Unusual deposit patterns

## 🚀 Advantages

### For Users:
- ✅ Simpler deposit process
- ✅ Faster credit conversion
- ✅ One wallet address to remember
- ✅ Better UX

### For Admin:
- ✅ Easier to manage
- ✅ Better tracking
- ✅ Integrated with Conway Dashboard
- ✅ Less complexity
- ✅ No encryption key management

### For System:
- ✅ Reduced database complexity
- ✅ Better scalability
- ✅ Easier to audit
- ✅ Lower maintenance cost

## ⚠️ Considerations

### Potential Issues:
1. **Attribution**: Bagaimana tahu deposit dari user mana?
   - **Solution**: User input tx hash setelah deposit
   
2. **Timing**: Delay antara deposit dan credit
   - **Solution**: Monitor blockchain real-time
   
3. **Conway API**: Dependency pada external service
   - **Solution**: Implement retry logic dan fallback

4. **Multiple Networks**: Support Polygon, Base, Arbitrum
   - **Solution**: Multi-chain monitoring

## 📞 Next Steps

1. Review arsitektur ini
2. Confirm dengan Conway Dashboard integration
3. Implement database migration
4. Update code
5. Test thoroughly
6. Deploy to production

---

**Ready to implement?** Saya bisa mulai dengan:
1. Database migration script
2. Updated menu_handlers.py
3. Transaction verifier
4. Deposit monitor
