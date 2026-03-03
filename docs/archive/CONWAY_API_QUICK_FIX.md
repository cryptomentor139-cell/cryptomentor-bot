# Conway API Quick Fix - Langkah Cepat

## 🎯 Masalah
Error: `CONWAY_APKEY environment variable not set`

## ⚡ Solusi Cepat (5 Menit)

### 1. Buka Railway Dashboard
https://railway.app/dashboard

### 2. Pilih Project Anda
Klik project `cryptomentor-bot`

### 3. Klik Tab "Variables"
Di sidebar kiri, klik "Variables"

### 4. Tambahkan 2 Variables Ini:

**Variable 1:**
```
Name: CONWAY_API_KEY
Value: cnwy_k_DNll3zray_o4ccEpRmW0G6pK68BENY73
```
Klik tombol "Add" ✅

**Variable 2:**
```
Name: CONWAY_API_URL
Value: https://api.conway.tech
```
Klik tombol "Add" ✅

### 5. Redeploy Service

**Option A: Manual Redeploy**
- Klik tab "Deployments"
- Klik "Redeploy" pada deployment terakhir
- Tunggu 2-3 menit

**Option B: Auto Deploy (sudah dilakukan)**
- Code sudah di-push ke GitHub
- Railway akan auto-deploy
- Tunggu 2-3 menit

### 6. Verify

Cek deployment logs, harus ada:
```
✅ Conway API client initialized: https://api.conway.tech
```

Jika masih error:
```
❌ CONWAY_API_KEY environment variable not set
```

Berarti variables belum ter-save. Ulangi step 4 dan pastikan klik "Add"!

---

## 🧪 Test Setelah Fix

1. Buka bot di Telegram
2. Klik "AI Agent"
3. Klik "Spawn Agent"
4. Ketik nama agent

**Harus berhasil tanpa error!**

---

## 📋 Checklist

- [ ] CONWAY_API_KEY ditambahkan di Railway
- [ ] CONWAY_API_URL ditambahkan di Railway
- [ ] Klik "Add" untuk setiap variable
- [ ] Service di-redeploy
- [ ] Logs menunjukkan "Conway API client initialized"
- [ ] Bot bisa spawn agent tanpa error

---

## 🆘 Masih Error?

Baca panduan lengkap: `FIX_CONWAY_API_NOT_FOUND.md`

Atau jalankan test script:
```bash
cd Bismillah
python test_conway_env_railway.py
```
