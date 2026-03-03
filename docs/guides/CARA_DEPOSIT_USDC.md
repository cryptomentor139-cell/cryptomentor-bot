# 💰 Cara Deposit USDC ke Conway Automaton

## Quick Start

### 1. Spawn Agent
```
/spawn_agent NamaAgentAnda
```

Bot akan memberikan deposit address.

### 2. Deposit Address
```
0x63116672bef9f26fd906cd2a57550f7a13925822
```

**PENTING:**
- ✅ Network: **Base** (WAJIB!)
- ✅ Token: **USDC** (bukan USDT!)
- ✅ Minimum: **$30 USDC**

### 3. Kirim USDC

Dari wallet Anda (MetaMask, Trust Wallet, dll):

1. Pilih network: **Base**
2. Pilih token: **USDC**
3. Paste address: `0x63116672bef9f26fd906cd2a57550f7a13925822`
4. Amount: Minimal $30 USDC
5. Kirim!

### 4. Tunggu Konfirmasi

- ⏱️ 12 konfirmasi (~5-10 menit)
- 💳 Credits otomatis masuk ke account Anda
- 📱 Bot akan notify Anda

## Conversion Rate

```
1 USDC = 100 Conway Credits

$5 USDC   = 500 credits
$10 USDC  = 1,000 credits
$30 USDC  = 3,000 credits (minimum untuk spawn)
$100 USDC = 10,000 credits
```

## Biaya

### Spawn Agent
- **100,000 credits** (~$1,000 USDC)
- One-time fee per agent

### Minimum Deposit
- **$30 USDC** (3,000 credits)
- Untuk memenuhi requirement spawn agent

### Total untuk Spawn Agent Pertama
```
Deposit minimum: $30 USDC (3,000 credits)
Spawn fee: 100,000 credits (~$1,000 USDC)
─────────────────────────────────────────
Total: ~$1,030 USDC
```

## Network Details

### Base Network
- **Chain ID:** 8453
- **RPC URL:** https://mainnet.base.org
- **Explorer:** https://basescan.org
- **Gas Token:** ETH
- **Gas Fee:** ~$0.01 per transaction

### Tambah Base Network ke MetaMask

1. Buka MetaMask
2. Click network dropdown
3. "Add Network"
4. Pilih "Base" atau manual:
   - Network Name: Base
   - RPC URL: https://mainnet.base.org
   - Chain ID: 8453
   - Currency Symbol: ETH
   - Block Explorer: https://basescan.org

## Cara Deposit dari Exchange

### Coinbase
1. Buy USDC
2. Withdraw USDC
3. Network: **Base**
4. Address: `0x63116672bef9f26fd906cd2a57550f7a13925822`

### Binance
1. Buy USDC
2. Withdraw USDC
3. Network: **Base** (jika tersedia)
4. Address: `0x63116672bef9f26fd906cd2a57550f7a13925822`

⚠️ **PENTING:** Pastikan exchange support Base network!

## Cara Deposit dari Wallet

### MetaMask
1. Buka MetaMask
2. Switch ke Base network
3. Select USDC token
4. Click "Send"
5. Paste address: `0x63116672bef9f26fd906cd2a57550f7a13925822`
6. Enter amount (min $30)
7. Confirm transaction

### Trust Wallet
1. Buka Trust Wallet
2. Select USDC (Base)
3. Click "Send"
4. Paste address: `0x63116672bef9f26fd906cd2a57550f7a13925822`
5. Enter amount (min $30)
6. Confirm transaction

## Verifikasi Deposit

### Check di Bot
```
/balance
```

Bot akan show:
- Conway credits balance
- Agent balance
- Recent transactions

### Check di Blockchain
1. Buka https://basescan.org
2. Paste address: `0x63116672bef9f26fd906cd2a57550f7a13925822`
3. Check "Token Transfers"
4. Find your transaction

## Troubleshooting

### ❌ Deposit tidak masuk

**Cek:**
1. Network benar? (Base, bukan Ethereum/Polygon)
2. Token benar? (USDC, bukan USDT)
3. Address benar? (`0x63116672bef9f26fd906cd2a57550f7a13925822`)
4. Konfirmasi cukup? (12 konfirmasi)

**Solusi:**
1. Check transaction di basescan.org
2. Copy transaction hash
3. Contact admin dengan transaction hash
4. Admin akan manual credit

### ❌ Salah network

Jika kirim ke network lain (Ethereum, Polygon, dll):
- ⚠️ Dana mungkin hilang
- 💡 Contact admin dengan transaction hash
- 🔧 Admin akan coba recover (tidak guaranteed)

### ❌ Salah token

Jika kirim token lain (USDT, ETH, dll):
- ⚠️ Token tidak akan di-credit
- 💡 Contact admin dengan transaction hash
- 🔧 Admin bisa return token (minus gas fee)

## FAQ

### Q: Apakah address ini aman?
A: Ya, ini adalah custodial wallet milik Conway Automaton. Semua user deposit ke address yang sama.

### Q: Kenapa semua user pakai address yang sama?
A: Sistem menggunakan centralized custodial wallet. Deposits di-track berdasarkan user ID di database.

### Q: Apakah saya control private key?
A: Tidak, ini custodial wallet. Conway Automaton yang control private key.

### Q: Bagaimana kalau saya mau withdraw?
A: Gunakan command `/withdraw` di bot. Admin akan process withdrawal request.

### Q: Berapa lama deposit masuk?
A: ~5-10 menit (12 konfirmasi di Base network).

### Q: Apakah ada fee deposit?
A: Tidak ada fee deposit. Hanya gas fee di Base network (~$0.01).

### Q: Minimum deposit berapa?
A: $30 USDC (3,000 credits) untuk spawn agent.

### Q: Bisa deposit lebih dari $30?
A: Ya! Tidak ada maximum. Semakin banyak deposit, semakin banyak credits.

## Support

Jika ada masalah:
1. Check dokumentasi ini
2. Check transaction di basescan.org
3. Contact admin di bot dengan:
   - Transaction hash
   - Amount
   - Timestamp
   - Screenshot

Admin akan bantu resolve issue Anda.

## Summary

✅ **Deposit Address:** `0x63116672bef9f26fd906cd2a57550f7a13925822`
✅ **Network:** Base
✅ **Token:** USDC
✅ **Minimum:** $30 USDC
✅ **Conversion:** 1 USDC = 100 credits
✅ **Konfirmasi:** 12 blocks (~5-10 menit)

Happy trading! 🚀
