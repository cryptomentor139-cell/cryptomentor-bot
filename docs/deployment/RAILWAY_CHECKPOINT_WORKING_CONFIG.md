# 🎯 RAILWAY CHECKPOINT - WORKING CONFIGURATION

## ⚠️ PENTING: JANGAN UBAH KONFIGURASI INI!

**Status:** ✅ BOT ONLINE & RUNNING  
**Date:** 28 Februari 2026  
**Railway Deployment:** eebdb5f (Active & Online)  
**GitHub Commit:** Checkpoint yang di-rollback dari Railway

---

## 📋 WORKING CONFIGURATION

### 1. Railway Settings

**Builder:** Nixpacks (Auto-detect)  
**Region:** us-west2  
**Start Command:** `python main.py`  
**Restart Policy:** ON_FAILURE (max 10 retries)

### 2. File Structure (YANG BEKERJA)

```
Bismillah/
├── bot.py                    # Main bot class
├── main.py                   # Entry point (PENTING!)
├── Procfile                  # Railway process file
├── railway.json              # Railway config
├── runtime.txt               # Python version
├── requirements.txt          # Dependencies
├── menu_system.py            # Menu structure
├── menu_handler.py           # Menu handlers
├── menu_handlers.py          # Menu callback handlers
└── app/
    ├── handlers_ai_agent_education.py
    ├── handlers_automaton.py
    └── ... (other handlers)
```

### 3. Critical Files Content

#### `Procfile`
```
web: python main.py
```

#### `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### `runtime.txt`
```
python-3.11.9
```

#### `main.py` (Entry Point)
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CryptoMentor AI Bot - Main Entry Point
Simple entry point for Railway deployment
"""

if __name__ == "__main__":
    import bot
    import asyncio
    
    print("🚀 Starting CryptoMentor AI Bot...")
    
    # Create bot instance
    telegram_bot = bot.TelegramBot()
    
    # Run bot
    asyncio.run(telegram_bot.run())
```

### 4. Environment Variables (Railway Dashboard)

**Required Variables:**
```
TELEGRAM_BOT_TOKEN=<your_token>
SUPABASE_URL=<your_url>
SUPABASE_KEY=<your_key>
ADMIN_IDS=<admin_user_ids>
ADMIN1=<admin_id_1>
ADMIN2=<admin_id_2>
```

**Optional but Recommended:**
```
DEEPSEEK_API_KEY=<your_key>
CEREBRAS_API_KEY=<your_key>
CONWAY_API_URL=<conway_url>
CONWAY_API_KEY=<conway_key>
```

---

## 🚫 JANGAN LAKUKAN INI!

### ❌ JANGAN Buat File Ini:
- `nixpacks.toml` - Menyebabkan derivation error
- Custom build scripts yang kompleks
- Dockerfile (kecuali benar-benar diperlukan)

### ❌ JANGAN Ubah:
- `Procfile` - Tetap gunakan `python main.py`
- `railway.json` - Tetap minimal seperti di atas
- `runtime.txt` - Tetap Python 3.11.9
- Builder setting - Tetap Nixpacks

### ❌ JANGAN Gunakan:
- `python3` command - Gunakan `python`
- `python bot.py` - Gunakan `python main.py`
- Custom buildCommand - Biarkan Nixpacks auto-detect

---

## ✅ CARA DEPLOY PERUBAHAN BARU

### Step 1: Test Lokal Dulu
```bash
cd Bismillah
python main.py
# Pastikan bot jalan tanpa error
```

### Step 2: Commit ke GitHub
```bash
git add <files_yang_diubah>
git commit -m "Deskripsi perubahan"
git push origin main
```

### Step 3: Monitor Railway
1. Buka Railway Dashboard
2. Lihat Build Logs - harus success
3. Lihat Deploy Logs - harus muncul "✅ Bot initialized"
4. Test bot di Telegram

### Step 4: Jika Gagal - ROLLBACK!
1. Railway Dashboard → Deployments
2. Cari deployment "eebdb5f" (yang sekarang online)
3. Click "Redeploy" pada deployment itu
4. Bot akan kembali ke konfigurasi yang bekerja

---

## 📊 VERIFICATION CHECKLIST

Setelah deployment, pastikan:

- [ ] Railway status: Online (hijau)
- [ ] Build logs: No errors
- [ ] Deploy logs: "✅ Bot initialized"
- [ ] Telegram `/start`: Menu muncul
- [ ] Menu "🤖 AI Agent": Submenu muncul dengan:
  - Spawn Agent
  - Agent Status
  - Agent Lineage
  - Fund Agent (Deposit)
  - Agent Logs
- [ ] Commands working: `/help`, `/price btc`

---

## 🔧 TROUBLESHOOTING

### Jika Bot Tidak Respond:

1. **Check Railway Logs:**
   ```
   Railway Dashboard → Logs tab
   Cari error messages
   ```

2. **Check Environment Variables:**
   ```
   Railway Dashboard → Variables tab
   Pastikan semua var ada dan benar
   ```

3. **Rollback ke Checkpoint:**
   ```
   Railway Dashboard → Deployments
   Redeploy: eebdb5f
   ```

### Jika Build Gagal:

1. **Check Build Logs:**
   - Cari error message
   - Biasanya masalah di dependencies atau syntax

2. **Verify Files:**
   ```bash
   # Check critical files exist
   ls Procfile railway.json runtime.txt requirements.txt main.py
   ```

3. **Rollback Changes:**
   ```bash
   git revert HEAD
   git push origin main
   ```

---

## 📝 DEPLOYMENT HISTORY

### Working Deployments:
- **eebdb5f** (Current) - ✅ ONLINE - 28 Feb 2026
  - Config: Nixpacks auto-detect
  - Entry: python main.py
  - Status: Stable & Running

### Failed Attempts (JANGAN ULANGI):
- **f367c8b** - ❌ FAILED - Added main.py but still error
- **20ccaa0** - ❌ FAILED - Removed nixpacks.toml
- **1dcf352** - ❌ FAILED - Added nixpacks.toml (derivation error)
- **fedc3f9** - ❌ FAILED - Initial menu update

---

## 🎯 GOLDEN RULES

1. **Keep It Simple** - Nixpacks sudah pintar, jangan overcomplicate
2. **Test Locally First** - Selalu test di local sebelum push
3. **Small Changes** - Deploy perubahan kecil-kecil, bukan sekaligus banyak
4. **Monitor Logs** - Selalu cek logs setelah deploy
5. **Know Your Rollback** - Selalu tahu cara rollback ke checkpoint ini

---

## 📞 EMERGENCY ROLLBACK

Jika bot crash dan Anda panik:

```bash
# Option 1: Railway Dashboard
1. Buka Railway Dashboard
2. Tab "Deployments"
3. Cari "eebdb5f" (yang hijau/online)
4. Click "Redeploy"
5. Tunggu 2-3 menit

# Option 2: Git Rollback
git log  # Cari commit yang bekerja
git reset --hard <commit_hash>
git push origin main --force
```

---

## 🎊 SUCCESS INDICATORS

Bot bekerja dengan baik jika:

✅ Railway status: Online (hijau)  
✅ No error di logs  
✅ Bot respond di Telegram  
✅ Menu buttons functional  
✅ Commands working  
✅ No restart loops  

---

## 📌 NOTES

- Checkpoint ini adalah **GOLDEN CONFIG**
- Jangan ubah tanpa backup
- Selalu test di local dulu
- Jika ragu, jangan deploy
- Simpan dokumentasi ini dengan baik

**Last Updated:** 28 Februari 2026  
**Maintained By:** CryptoMentor AI Team  
**Status:** ✅ PRODUCTION READY

---

## 🔐 BACKUP CHECKPOINT

Jika file ini hilang, cari di:
- Railway Dashboard → Deployments → eebdb5f
- GitHub Commit sebelum perubahan terakhir
- Local backup di folder Bismillah/

**INGAT: Deployment eebdb5f adalah CHECKPOINT EMAS Anda!**
