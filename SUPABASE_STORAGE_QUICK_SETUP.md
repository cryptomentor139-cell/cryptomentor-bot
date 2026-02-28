# 🗄️ Supabase Storage Setup - Quick Guide

## ✅ Gunakan Supabase yang Sudah Ada!

**Good news**: Tidak perlu Supabase baru! Pakai yang sudah ada di `.env` kamu.

## 📋 Current Supabase

Dari `.env` kamu:
```bash
SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ini sudah cukup!** Tinggal tambah Storage Bucket.

## 🚀 Setup (2 Menit)

### Step 1: Login ke Supabase

1. Buka: https://app.supabase.com
2. Login dengan akun kamu
3. Pilih project: `xrbqnocovfymdikngaza`

### Step 2: Create Storage Bucket

1. Di sidebar, klik **Storage**
2. Klik **New Bucket**
3. Settings:
   - **Name**: `cryptobot-signals`
   - **Public**: ❌ No (keep private)
   - **File size limit**: 50 MB
   - **Allowed MIME types**: Leave empty (allow all)
4. Klik **Create Bucket**

### Step 3: Verify

Bucket `cryptobot-signals` sekarang muncul di Storage list.

## ✅ Done!

Tidak perlu update `.env` - credentials sudah ada!

## 🎯 What You Get

### Same Supabase Project:

```
Supabase Project: xrbqnocovfymdikngaza
├── Database (existing)
│   ├── users table
│   ├── credits table
│   └── ... (tables lainnya)
│
└── Storage (new!)
    └── cryptobot-signals bucket
        ├── prompts_2026-02-16.jsonl
        ├── active_signals.jsonl
        └── completed_signals.jsonl
```

### Benefits:

- ✅ **Satu Project** - Semua data di satu tempat
- ✅ **Satu Dashboard** - Easy monitoring
- ✅ **Satu Billing** - Free tier cukup untuk semua
- ✅ **No Extra Setup** - Credentials sudah ada

## 📊 Free Tier Limits

Supabase Free Tier includes:

| Resource | Limit | Your Usage |
|----------|-------|------------|
| Database | 500 MB | ~50 MB (users, credits) |
| Storage | 1 GB | ~10 MB (signal logs) |
| Bandwidth | 2 GB | ~100 MB/month |

**Conclusion**: Free tier **lebih dari cukup**! 🎉

## 🔧 Railway Configuration

Di Railway, environment variables **tetap sama**:

```bash
# Supabase (already in Railway)
SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Enable storage (add this)
USE_SUPABASE_STORAGE=true
USE_GDRIVE=false
```

## 🧪 Test Storage

### Via Python:

```python
from app.supabase_storage import supabase_storage

# Check status
status = supabase_storage.get_status()
print(status)
# Output: {'enabled': True, 'bucket': 'cryptobot-signals', ...}

# Upload test file
from pathlib import Path
test_file = Path("signal_logs/prompts_2026-02-16.jsonl")
supabase_storage.upload_file(test_file)
# Output: ✅ Uploaded: prompts_2026-02-16.jsonl
```

### Via Telegram:

```bash
# After bot deployed
/signal_stats
```

Expected:
```
☁️ STORAGE:
• Type: Supabase Storage (Cloud)
• Status: ✅ Enabled
• Bucket: cryptobot-signals
• Files: 0
```

## 📁 File Structure in Supabase

After running for a week:

```
Storage → cryptobot-signals/
├── prompts_2026-02-16.jsonl (2 KB)
├── prompts_2026-02-17.jsonl (3 KB)
├── prompts_2026-02-18.jsonl (2 KB)
├── prompts_2026-02-19.jsonl (4 KB)
├── prompts_2026-02-20.jsonl (3 KB)
├── prompts_2026-02-21.jsonl (2 KB)
├── prompts_2026-02-22.jsonl (3 KB)
├── active_signals.jsonl (5 KB)
└── completed_signals.jsonl (15 KB)

Total: ~40 KB (plenty of space left!)
```

## 🔐 Security

### Bucket is Private:

- ✅ Only accessible via Service Key
- ✅ Not publicly accessible
- ✅ Secure by default

### Access Control:

```sql
-- Supabase automatically creates policies
-- Only authenticated requests can access
```

## 💡 Best Practices

### 1. Monitor Storage Usage

Check Supabase Dashboard:
- Storage → cryptobot-signals
- View file sizes
- Monitor total usage

### 2. Cleanup Old Files (Optional)

If storage gets full (unlikely):
```python
# Delete files older than 90 days
from app.supabase_storage import supabase_storage
# ... cleanup logic
```

### 3. Backup Important Data

Weekly reports already sent to admin via Telegram - that's your backup!

## ⚠️ Troubleshooting

### Issue: Bucket Creation Failed

**Error**: "Bucket name already exists"

**Solution**: 
- Bucket already created! ✅
- Just use it

### Issue: Upload Failed

**Error**: "Authentication failed"

**Check**:
1. `SUPABASE_SERVICE_KEY` correct in Railway
2. Bucket exists
3. Bucket is not public

**Solution**:
```bash
# In Railway, verify:
railway variables get SUPABASE_SERVICE_KEY
```

### Issue: Files Not Showing

**Check**:
1. Bot running on Railway
2. `/signal_stats` shows storage enabled
3. Commands being used (to generate logs)

**Solution**:
```bash
# Test with command
/analyze btc

# Then check
/signal_stats
# Should show: Total Prompts: 1
```

## ✅ Verification Checklist

- [ ] Logged into Supabase Dashboard
- [ ] Navigated to Storage
- [ ] Created bucket: `cryptobot-signals`
- [ ] Bucket is private (not public)
- [ ] Verified bucket appears in list
- [ ] No changes needed to `.env`
- [ ] Ready to deploy to Railway!

## 🎉 Summary

**What you need to do:**
1. Create bucket `cryptobot-signals` in existing Supabase ✅
2. That's it! ✅

**What you DON'T need:**
- ❌ New Supabase project
- ❌ New credentials
- ❌ Update `.env`
- ❌ Extra configuration

**Result:**
- ✅ Same Supabase for everything
- ✅ Database + Storage in one place
- ✅ Free tier more than enough
- ✅ Easy to manage

---

**Setup Time**: 2 minutes  
**Cost**: $0 (Free tier)  
**Complexity**: Minimal  
**Status**: Ready to use!
