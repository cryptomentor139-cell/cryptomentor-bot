# 🚀 Deploy Update: USDC on Base Only

## ✅ Perubahan yang Sudah Dilakukan

### 1. Update Deposit Messaging
File yang diubah: `menu_handlers.py`

**Perubahan di `handle_automaton_first_deposit()`:**
- ❌ Dulu: "Deposit USDT/USDC" dengan network Polygon, Base, Arbitrum
- ✅ Sekarang: "Deposit USDC" dengan Base Network ONLY

**Perubahan di `show_ai_agent_menu()`:**
- ❌ Dulu: Welcome message menyebutkan USDT/USDC dan multiple networks
- ✅ Sekarang: Welcome message hanya menyebutkan USDC dan Base Network

### 2. Detail Perubahan

**Token:**
- Hanya USDC (tidak ada USDT lagi)

**Network:**
- Hanya Base Network (tidak ada Polygon atau Arbitrum)

**Conversion Rate:**
- 1 USDC = 100 Conway Credits

**Minimum Deposit:**
- 5 USDC

**Centralized Wallet:**
- `0x63116672bef9f26fd906cd2a57550f7a13925822`

## 📋 Langkah Deploy ke Railway

### Step 1: Push ke GitHub

```bash
cd Bismillah
git add menu_handlers.py
git commit -m "Update: Focus on USDC Base network only for deposits"
git push origin main
```

### Step 2: Cek Environment Variable di Railway

Pastikan Railway sudah punya environment variable ini:

```
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822
```

**Cara cek:**
1. Buka Railway dashboard
2. Pilih project Anda
3. Klik tab "Variables"
4. Cari `CENTRALIZED_WALLET_ADDRESS`
5. Jika belum ada, tambahkan dengan value di atas

### Step 3: Wait for Auto-Deploy

Railway akan otomatis deploy setelah push ke GitHub:
1. Tunggu 2-3 menit
2. Cek deployment logs di Railway
3. Pastikan tidak ada error

### Step 4: Test di Telegram

1. Buka bot Telegram Anda
2. Klik menu "🤖 AI Agent"
3. Klik "💰 Deposit Sekarang"
4. Verifikasi pesan yang muncul:
   - ✅ Hanya menyebutkan USDC (bukan USDT/USDC)
   - ✅ Hanya menyebutkan Base Network (bukan Polygon/Base/Arbitrum)
   - ✅ Conversion rate: 1 USDC = 100 Conway Credits
   - ✅ Minimum deposit: 5 USDC

## 🎯 Apa yang Berubah untuk User?

### Sebelum:
```
💰 Deposit USDT/USDC

🌐 Network yang Didukung:
• Polygon (Direkomendasikan - Biaya rendah)
• Base
• Arbitrum

💱 Conversion Rate:
• 1 USDT = 100 Conway Credits
• 1 USDC = 100 Conway Credits
```

### Sesudah:
```
💰 Deposit USDC

🌐 Network:
• Base Network (WAJIB)

💱 Conversion Rate:
• 1 USDC = 100 Conway Credits
```

## ⚠️ Penting!

1. **Conway Dashboard harus dikonfigurasi untuk Base Network**
   - Pastikan webhook Conway Dashboard sudah set untuk monitor Base Network
   - Pastikan hanya USDC yang diproses

2. **User yang sudah deposit di network lain**
   - Jika ada user yang sudah deposit USDT atau di Polygon/Arbitrum sebelumnya
   - Credits mereka tetap aman di database
   - Tapi deposit baru hanya bisa USDC di Base

3. **Testing**
   - Test dengan deposit kecil dulu (5 USDC)
   - Pastikan Conway Dashboard detect deposit
   - Pastikan credits masuk ke user

## 🔄 Rollback Plan

Jika ada masalah, rollback dengan:

```bash
git revert HEAD
git push origin main
```

Railway akan auto-deploy versi sebelumnya.

## 📞 Support

Jika ada masalah:
1. Cek Railway logs
2. Cek Conway Dashboard logs
3. Cek Supabase `pending_deposits` table
4. Cek Supabase `deposit_transactions` table

---

**Status:** ✅ Ready to Deploy
**Next Step:** Push ke GitHub dan test di Telegram
