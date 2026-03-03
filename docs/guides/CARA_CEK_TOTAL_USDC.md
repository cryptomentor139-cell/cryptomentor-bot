# 💰 Cara Cek Total USDC dari Para User

Ada 3 cara untuk melihat total USDC dan data wallet custodial user:

## 🖥️ Cara 1: Supabase Dashboard (UI - Paling Mudah)

### Langkah-langkah:

1. **Buka Supabase Dashboard**
   - URL: https://supabase.com/dashboard
   - Login dengan akun Anda

2. **Pilih Project**
   - Klik project bot Anda
   - Dari `.env`: `SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co`
   - Project ID: `xrbqnocovfymdikngaza`

3. **Buka Table Editor**
   - Di sidebar kiri, klik "Table Editor"
   - Pilih table: `custodial_wallets`

4. **Lihat Data**
   - Anda akan melihat semua wallet dengan kolom:
     - `user_id` - ID user Telegram
     - `wallet_address` - Alamat wallet Ethereum
     - `balance_usdc` - Balance USDC user
     - `conway_credits` - Conway credits user
     - `created_at` - Tanggal wallet dibuat
     - `updated_at` - Terakhir update

5. **Filter & Sort**
   - Klik header kolom untuk sort
   - Gunakan filter untuk cari user tertentu
   - Export data ke CSV jika perlu

### Screenshot Lokasi:
```
Supabase Dashboard
├── [Your Project]
│   ├── Table Editor  ← Klik ini
│   │   ├── custodial_wallets  ← Pilih table ini
│   │   │   ├── user_id
│   │   │   ├── wallet_address
│   │   │   ├── balance_usdc  ← Total USDC ada di sini
│   │   │   ├── conway_credits
│   │   │   └── ...
```

## 🐍 Cara 2: Python Script (Otomatis dengan Statistik)

### Jalankan Script:

```bash
cd Bismillah
python check_total_usdc.py
```

### Output yang Ditampilkan:

```
💰 TOTAL USDC BALANCE - ALL USERS
======================================================================

📋 WALLET DETAILS
======================================================================

👤 User ID: 1187119989
   Wallet: 0x1234567...89abcdef
   USDC Balance: $50.00
   Conway Credits: 5000
   Created: 2026-02-21

👤 User ID: 7079544380
   Wallet: 0xabcdef12...34567890
   USDC Balance: $25.00
   Conway Credits: 2500
   Created: 2026-02-21

======================================================================
📊 SUMMARY STATISTICS
======================================================================

💰 Total USDC Balance: $75.00
🎯 Total Conway Credits: 7500
👥 Total Wallets: 2
💵 Wallets with USDC: 2
⚡ Wallets with Credits: 2

📈 Average USDC per Wallet: $37.50
📈 Average Credits per Wallet: 3750

======================================================================
💱 CONVERSION ANALYSIS
======================================================================

Expected Credits (1 USDC = 100 Credits): 7500
Actual Credits: 7500
Difference: 0

======================================================================
🏆 TOP 5 WALLETS BY USDC BALANCE
======================================================================

1. User 1187119989
   USDC: $50.00 | Credits: 5000

2. User 7079544380
   USDC: $25.00 | Credits: 2500

======================================================================
```

## 📊 Cara 3: SQL Query Langsung (Advanced)

### Di Supabase SQL Editor:

1. Buka Supabase Dashboard
2. Klik "SQL Editor" di sidebar
3. Jalankan query ini:

#### Query 1: Total USDC Semua User
```sql
SELECT 
    COUNT(*) as total_wallets,
    SUM(balance_usdc) as total_usdc,
    SUM(conway_credits) as total_credits,
    AVG(balance_usdc) as avg_usdc,
    AVG(conway_credits) as avg_credits
FROM custodial_wallets;
```

#### Query 2: Detail Per User
```sql
SELECT 
    user_id,
    wallet_address,
    balance_usdc,
    conway_credits,
    created_at,
    updated_at
FROM custodial_wallets
ORDER BY balance_usdc DESC;
```

#### Query 3: User dengan Balance > 0
```sql
SELECT 
    user_id,
    wallet_address,
    balance_usdc,
    conway_credits
FROM custodial_wallets
WHERE balance_usdc > 0
ORDER BY balance_usdc DESC;
```

#### Query 4: Statistik Deposit
```sql
SELECT 
    COUNT(*) FILTER (WHERE balance_usdc > 0) as users_with_deposit,
    COUNT(*) FILTER (WHERE balance_usdc = 0) as users_without_deposit,
    MIN(balance_usdc) as min_balance,
    MAX(balance_usdc) as max_balance,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY balance_usdc) as median_balance
FROM custodial_wallets;
```

## 🔍 Monitoring Real-time

### Setup Auto-refresh Script:

Buat script untuk monitoring terus-menerus:

```bash
# Windows
while ($true) { cls; python check_total_usdc.py; Start-Sleep -Seconds 60 }

# Linux/Mac
watch -n 60 python check_total_usdc.py
```

Ini akan refresh data setiap 60 detik.

## 📱 Cara Cek dari Bot (Admin Command)

Anda juga bisa tambahkan admin command di bot untuk cek total USDC:

### Command: `/admin_wallet_stats`

Saya bisa buatkan handler untuk ini jika Anda mau. Command ini akan:
- Hanya bisa diakses admin
- Menampilkan total USDC semua user
- Menampilkan top 10 wallets
- Menampilkan statistik deposit

## 📊 Dashboard Recommendations

Untuk monitoring yang lebih baik, pertimbangkan:

### 1. Supabase Dashboard (Built-in)
- ✅ Gratis
- ✅ Real-time
- ✅ SQL query support
- ✅ Export to CSV
- ❌ Limited customization

### 2. Metabase (Open Source)
- ✅ Beautiful dashboards
- ✅ Auto-refresh
- ✅ Charts & graphs
- ✅ Connect to Supabase
- ❌ Perlu setup sendiri

### 3. Grafana (Advanced)
- ✅ Professional monitoring
- ✅ Alerts
- ✅ Multiple data sources
- ❌ Complex setup

### 4. Custom Admin Panel
- ✅ Fully customized
- ✅ Integrated dengan bot
- ❌ Perlu development time

## 🚨 Important Notes

### Security:
- ⚠️ JANGAN share screenshot yang menampilkan:
  - Wallet addresses lengkap
  - Private keys (encrypted atau tidak)
  - User IDs yang sensitive
  - Total balance yang bisa jadi target

### Privacy:
- Data wallet user adalah data sensitive
- Hanya admin yang boleh akses
- Jangan share data ke pihak ketiga
- Comply dengan privacy regulations

### Backup:
- Export data wallet secara berkala
- Simpan di tempat aman
- Encrypt backup files
- Test restore procedure

## 🎯 Quick Access Links

### Supabase Dashboard:
```
https://supabase.com/dashboard/project/xrbqnocovfymdikngaza
```

### Direct Table View:
```
https://supabase.com/dashboard/project/xrbqnocovfymdikngaza/editor/custodial_wallets
```

### SQL Editor:
```
https://supabase.com/dashboard/project/xrbqnocovfymdikngaza/sql
```

## 📞 Troubleshooting

### Error: "Connection failed"
- Check internet connection
- Verify Supabase credentials in `.env`
- Check if Supabase project is active

### Error: "Table not found"
- Run migration: `python run_migration_001.py`
- Check table name spelling
- Verify database permissions

### Data tidak update
- Check deposit monitor running
- Verify blockchain confirmations
- Check error logs

## 🔄 Next Steps

Setelah cek total USDC:

1. ✅ Monitor deposit activity
2. ✅ Track Conway credits usage
3. ✅ Analyze user behavior
4. ✅ Plan scaling strategy
5. ✅ Setup alerts for large deposits

---

**Rekomendasi**: Gunakan Supabase Dashboard untuk quick check, dan Python script untuk detailed analysis!
