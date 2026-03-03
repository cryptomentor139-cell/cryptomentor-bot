# ⚡ Quick Commands - Copy & Paste

## 🎯 Panduan Cepat Deploy CryptoMentor Bot

File ini berisi semua commands yang perlu Anda jalankan, tinggal copy-paste!

---

## Step 1: Configure Git (2 menit)

**⚠️ GANTI `YOUR_GITHUB_USERNAME` dan `YOUR_EMAIL` dengan info GitHub Anda!**

```powershell
# Set username (ganti dengan username GitHub Anda)
git config --global user.name "YOUR_GITHUB_USERNAME"

# Set email (ganti dengan email GitHub Anda)
git config --global user.email "YOUR_EMAIL@example.com"

# Verify config
git config --global --list
```

**Contoh**:
```powershell
git config --global user.name "nabilfarrel"
git config --global user.email "nabil@example.com"
git config --global --list
```

---

## Step 2: Create GitHub Repository (5 menit)

1. Buka: https://github.com/new
2. Repository name: `cryptomentor-bot`
3. Visibility: **Private** (recommended)
4. **JANGAN centang** "Initialize this repository"
5. Klik **"Create repository"**
6. **Copy URL** yang muncul (format: `https://github.com/YOUR_USERNAME/cryptomentor-bot.git`)

---

## Step 3: Push Code ke GitHub (5 menit)

**⚠️ GANTI `YOUR_USERNAME` dengan username GitHub Anda!**

```powershell
# Masuk ke folder Bismillah
cd C:\V3-Final-Version\Bismillah

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - CryptoMentor Bot with StepFun AI"

# Rename branch
git branch -M main

# Add remote (GANTI YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/cryptomentor-bot.git

# Push to GitHub
git push -u origin main
```

**Saat diminta credentials**:
- **Username**: GitHub username Anda
- **Password**: Personal Access Token (bukan password GitHub!)

### Cara Buat Personal Access Token:

1. Buka: https://github.com/settings/tokens
2. Klik **"Generate new token (classic)"**
3. Note: `CryptoMentor Bot`
4. Expiration: `90 days`
5. Centang: ✅ **`repo`**
6. Klik **"Generate token"**
7. **COPY TOKEN** (format: `ghp_xxxxx...`)
8. Paste sebagai password saat git push

---

## Step 4: Deploy ke Railway (10 menit)

### A. Login Railway

1. Buka: https://railway.app
2. Klik **"Login with GitHub"**
3. Authorize Railway

### B. Create Project

1. Klik **"New Project"**
2. Pilih **"Deploy from GitHub repo"**
3. Pilih **`cryptomentor-bot`**
4. Klik **"Deploy Now"**

### C. Add Environment Variables

1. Klik project → Tab **"Variables"**
2. Klik **"Raw Editor"**
3. Copy-paste ini:

```env
TELEGRAM_BOT_TOKEN=8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4
TOKEN=8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4
ADMIN1=1187119989
ADMIN2=7079544380
DEEPSEEK_API_KEY=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
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=stepfun/step-3.5-flash
HELIUS_API_KEY=3b32e914-4a27-417d-8dab-a70a1a9d1e8c
CRYPTOCOMPARE_API_KEY=44d575a1b1df76144a11214917bd37649345ffc2f8a88aee907671850dd662a9
SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUzMjExOTksImV4cCI6MjA3MDg5NzE5OX0.placeholder
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTMyMTE5OSwiZXhwIjoyMDcwODk3MTk5fQ.QGIlCWKqy8fe0bKJbx6CAqeSr7fq17NBXqNeC8nUu5Y
WELCOME_CREDITS=100
SESSION_SECRET=FZ+1sD4r0TLgs7r7vs1bZtPNerUjVDwtdgFM0DQ8TAJcKbs6wwGd6rSSZFdtIYGjsCoG4ANGf6+rdW+0tz6/XA==
USE_LEGACY_FUTURES_SIGNALS=true
CRYPTONEWS_API_KEY=2iqmgpfhhlcvrq9sqxhppabo8pxppg5pv1ue37x8
```

4. Klik **"Save"** (Ctrl+S)

### D. Verify Deployment

1. Tab **"Deployments"** → Klik deployment
2. Lihat **Logs**

Expected:
```
✅ CryptoMentor AI initialized
✅ Bot started successfully
✅ Polling started
```

### E. Test Bot

Di Telegram:
```
/start
/ai btc
/price eth
```

---

## 🎊 Done!

**Bot online 24/7 di Railway!** 🚀

---

## 🔄 Update Bot (Future)

```powershell
cd C:\V3-Final-Version\Bismillah

# Make changes...

git add .
git commit -m "Update: deskripsi perubahan"
git push

# Railway auto-deploy! 🚀
```

---

## 🐛 Troubleshooting

### Git push error?

```powershell
# Check remote
git remote -v

# Fix if wrong
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/cryptomentor-bot.git
git push -u origin main
```

### Lupa Personal Access Token?

1. https://github.com/settings/tokens
2. Generate new token (classic)
3. Select `repo` scope
4. Copy & save token

### Bot tidak start di Railway?

1. Railway Dashboard → Deployments → Logs
2. Check error messages
3. Verify environment variables

---

## 📋 Checklist

- [ ] Git configured dengan info GitHub saya
- [ ] Repository `cryptomentor-bot` dibuat di GitHub
- [ ] Personal Access Token sudah dibuat dan disimpan
- [ ] Code di-push ke GitHub
- [ ] Project dibuat di Railway
- [ ] Environment variables ditambahkan
- [ ] Bot berhasil deploy dan online
- [ ] Test bot di Telegram berhasil

---

## 🎯 Quick Links

- GitHub New Repo: https://github.com/new
- GitHub Tokens: https://github.com/settings/tokens
- Railway Dashboard: https://railway.app
- Bot Telegram: @Subridujdirdsjbot

---

**Total Time: 20-30 menit**
**Result: Bot online 24/7! 🚀**

**Selamat Deploy!** 🎉
