# Railway Python Deployment Fix ✅

## Problem: Bot Crash on Railway

### Error Logs
```
/bin/bash: line 1: python3: command not found
```

Bot tidak bisa start karena Railway tidak menemukan `python3` command.

## Root Cause

Railway menggunakan **Nixpacks** builder yang membutuhkan konfigurasi eksplisit untuk Python environment.

### Issues Found:
1. ❌ `railway.json` tidak specify build command
2. ❌ `Procfile` menggunakan `python3` (tidak tersedia di Nixpacks)
3. ❌ Tidak ada `nixpacks.toml` untuk konfigurasi Nixpacks

## Solution Applied

### 1. Created `nixpacks.toml`

File baru untuk konfigurasi Nixpacks builder:

```toml
[phases.setup]
nixPkgs = ["python311", "pip"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "python bot.py"
```

**Penjelasan:**
- `nixPkgs`: Specify Python 3.11 dan pip
- `phases.install`: Install dependencies dari requirements.txt
- `start.cmd`: Command untuk start bot (gunakan `python` bukan `python3`)

### 2. Updated `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python bot.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Changes:**
- ✅ Added `buildCommand` untuk install dependencies
- ✅ Changed `python3` → `python` di startCommand

### 3. Updated `Procfile`

```
web: python bot.py
```

**Changes:**
- ✅ Changed `python3` → `python`

## Files Modified

1. ✅ `nixpacks.toml` - CREATED (new file)
2. ✅ `railway.json` - UPDATED (added buildCommand, changed python3 → python)
3. ✅ `Procfile` - UPDATED (changed python3 → python)

## Deployment

```bash
# Commit changes
git add -A
git commit -m "Fix Railway deployment - add nixpacks.toml and fix Python command"

# Push to Railway (auto-deploy)
git push origin main
```

## Expected Result

Railway akan:
1. ✅ Detect nixpacks.toml
2. ✅ Setup Python 3.11 environment
3. ✅ Install dependencies dari requirements.txt
4. ✅ Start bot dengan `python bot.py`
5. ✅ Bot online dalam 2-3 menit

## Verification

Setelah deployment selesai:

1. **Check Railway Logs:**
   - Harus muncul: "✅ Bot initialized"
   - Harus muncul: "✅ Application handlers registered"
   - Tidak ada error "command not found"

2. **Test Bot di Telegram:**
   - `/start` - Harus muncul menu
   - Klik "🤖 AI Agent" - Harus muncul submenu
   - Semua button harus functional

## Troubleshooting

### Jika masih error "command not found":

1. **Check nixpacks.toml syntax:**
   ```bash
   cat nixpacks.toml
   ```

2. **Verify Railway builder:**
   - Railway Dashboard → Settings → Builder
   - Harus: "Nixpacks"

3. **Manual redeploy:**
   - Railway Dashboard → Deployments
   - Click "Redeploy" pada deployment terakhir

### Jika build success tapi bot crash:

1. **Check environment variables:**
   - Railway Dashboard → Variables
   - Verify semua env vars ada (TELEGRAM_BOT_TOKEN, dll)

2. **Check bot.py syntax:**
   ```bash
   python bot.py
   ```
   - Harus tidak ada syntax error

3. **Check dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   - Semua dependencies harus terinstall

## Why Nixpacks?

Railway menggunakan Nixpacks sebagai default builder untuk Python projects karena:

✅ **Reproducible builds** - Consistent environment
✅ **Fast builds** - Cached dependencies
✅ **Automatic detection** - Detects Python version dari runtime.txt
✅ **Flexible** - Bisa customize dengan nixpacks.toml

## Alternative: Dockerfile

Jika Nixpacks masih bermasalah, bisa gunakan Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

Tapi untuk sekarang, **Nixpacks sudah cukup** dengan konfigurasi yang sudah dibuat.

## Status

✅ **FIXED & DEPLOYED**
- Commit: 1dcf352
- Time: 2025-02-28
- Status: Pushed to Railway, waiting for auto-deploy

---

**Next:** Monitor Railway logs untuk memastikan bot start dengan sukses.
