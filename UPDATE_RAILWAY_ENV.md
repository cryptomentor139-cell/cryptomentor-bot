# 🚀 Update Railway Environment Variable - QUICK GUIDE

## ⚠️ PENTING: Setelah code di-push, kamu HARUS update environment variable di Railway!

Railway sudah auto-deploy code baru, tapi environment variable `AI_MODEL` masih pakai nilai lama.

## 📋 Step-by-Step Instructions:

### 1️⃣ Buka Railway Dashboard
```
https://railway.app
```
- Login dengan akun kamu
- Pilih project: **cryptomentor-bot**

### 2️⃣ Masuk ke Variables Tab
- Di dashboard project, klik tab **"Variables"** (biasanya di sidebar kiri)
- Atau klik **"Settings"** → **"Variables"**

### 3️⃣ Cari Variable `AI_MODEL`
- Scroll atau search untuk variable bernama: `AI_MODEL`
- Nilai saat ini: `stepfun/step-3.5-flash`

### 4️⃣ Edit Variable
- Klik pada variable `AI_MODEL`
- Atau klik icon **pencil/edit** di sebelah kanan

### 5️⃣ Ganti Nilai
**DARI:**
```
stepfun/step-3.5-flash
```

**MENJADI:**
```
google/gemini-flash-1.5
```

### 6️⃣ Save Changes
- Klik tombol **"Save"** atau **"Update"**
- Railway akan otomatis **redeploy** bot (2-3 menit)

### 7️⃣ Tunggu Deployment Selesai
- Lihat di tab **"Deployments"**
- Status akan berubah dari "Building" → "Deploying" → "Success"
- Biasanya selesai dalam 2-3 menit

### 8️⃣ Verify
Setelah deployment selesai, cek Railway logs:
```
✅ CryptoMentor AI initialized (Provider: OpenRouter, Model: google/gemini-flash-1.5)
```

Jika muncul pesan ini, berarti Gemini Flash sudah aktif! ✅

## 🎯 Visual Reference:

```
Railway Dashboard
├── Projects
│   └── cryptomentor-bot (pilih ini)
│       ├── Deployments
│       ├── Variables ← KLIK INI
│       │   ├── TELEGRAM_BOT_TOKEN
│       │   ├── DEEPSEEK_API_KEY
│       │   ├── AI_MODEL ← EDIT INI
│       │   │   └── Value: google/gemini-flash-1.5 ← GANTI KE INI
│       │   ├── SUPABASE_URL
│       │   └── ...
│       ├── Settings
│       └── Logs
```

## 🔧 Alternative: Via Railway CLI

Jika kamu prefer command line:

```bash
# Install Railway CLI (jika belum)
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Set variable
railway variables set AI_MODEL=google/gemini-flash-1.5

# Verify
railway variables
```

## ✅ Verification Checklist:

Setelah update, test ini:

- [ ] Railway deployment status: **Success** ✅
- [ ] Railway logs menunjukkan: `Model: google/gemini-flash-1.5` ✅
- [ ] Test futures signal: Response dalam **3-5 detik** ✅
- [ ] Test spot signal: Response dalam **3-5 detik** ✅
- [ ] Test `/ai` command: Response dalam **2-4 detik** ✅

## 🐛 Troubleshooting:

### Problem: Variable tidak muncul
**Solution**: Tambah variable baru
- Klik **"Add Variable"**
- Name: `AI_MODEL`
- Value: `google/gemini-flash-1.5`
- Save

### Problem: Deployment gagal
**Solution**: Check logs
- Klik tab **"Logs"**
- Cari error message
- Biasanya karena typo di variable value

### Problem: Bot masih lambat
**Solution**: Verify variable
- Pastikan value EXACT: `google/gemini-flash-1.5`
- Tidak ada spasi di awal/akhir
- Case-sensitive (huruf kecil semua)

### Problem: AI tidak jalan
**Solution**: Check API key
- Pastikan `DEEPSEEK_API_KEY` masih valid
- Test di OpenRouter dashboard
- Regenerate key jika perlu

## 📊 Expected Results:

### Before Update:
```
⏳ Analyzing BTC 4h...
[Wait 5-10 seconds]
📊 Signal + AI Insight
```

### After Update:
```
⏳ Analyzing BTC 4h...
[Wait 3-5 seconds] ⚡
📊 Signal + AI Insight
```

**50% faster response time!**

## 💡 Pro Tips:

1. **Bookmark Railway Dashboard** untuk akses cepat
2. **Enable notifications** untuk deployment updates
3. **Check logs regularly** untuk monitor performance
4. **Set up alerts** untuk error detection

## 🔄 Rollback Instructions:

Jika ada masalah dengan Gemini Flash, rollback ke StepFun:

1. Buka Railway Variables
2. Edit `AI_MODEL`
3. Ganti ke: `stepfun/step-3.5-flash`
4. Save
5. Wait for redeploy

## 📞 Need Help?

Jika stuck, screenshot:
1. Railway Variables page
2. Railway Logs (last 50 lines)
3. Error message (if any)

Dan share untuk troubleshooting!

---

**Status**: ⏳ WAITING FOR YOUR ACTION
**Action**: Update `AI_MODEL` variable in Railway Dashboard
**Expected Time**: 2 minutes to update + 3 minutes to redeploy = **5 minutes total**
