# ⚡ Quick Access Checklist - CryptoMentor Bot

## 🎯 Ringkasan Cepat

Dokumen ini adalah versi ringkas dari `AKSES_LENGKAP_BOT_CRYPTOMENTOR.md` untuk referensi cepat.

---

## ✅ Checklist: Apa yang Perlu Diberikan

### 1. Repository Access
```
□ Invite ke GitHub repository
□ Set permission: Write/Admin
□ Share repository URL
```

### 2. Railway Deployment
```
□ Invite ke Railway project (Bot)
□ Invite ke Railway project (Automaton API)
□ Share Railway project URLs
```

### 3. Database Access
```
□ Invite ke Supabase project
□ Invite ke Neon database
□ Share connection strings
```

### 4. Credentials (via secure channel)
```
□ Bot Token
□ All API Keys
□ Database passwords
□ Encryption keys
```

### 5. Documentation
```
□ Share AKSES_LENGKAP_BOT_CRYPTOMENTOR.md
□ Share RAILWAY_DEPLOYMENT_GUIDE.md
□ Share README.md
```

---

## 🔑 Credentials Quick Reference

### Bot Token
```
8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4
```

### Admin IDs
```
Admin 1: 1187119989
Admin 2: 7079544380
```

### Railway URLs
```
Bot: [Your Railway project URL]
Automaton API: https://automaton-production-a899.up.railway.app
```

### Database
```
Supabase: https://xrbqnocovfymdikngaza.supabase.co
Neon: ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech
```

### Conway API
```
URL: https://automaton-production-a899.up.railway.app
Key: cnwy_k_HeT-F6vsVC_z6pmhYbBOyo1UJHtFhXyr
```

---

## 📋 Step-by-Step: Cara Memberikan Akses

### Step 1: GitHub Repository
```bash
# Option A: Invite collaborator
1. Go to: https://github.com/[username]/[repo]/settings/access
2. Click "Invite a collaborator"
3. Enter email
4. Set permission: Write

# Option B: Share ZIP
1. Compress folder Bismillah/
2. Upload ke Google Drive
3. Share link
```

### Step 2: Railway Access
```bash
# Via Railway Dashboard
1. Login: https://railway.app/dashboard
2. Select project
3. Settings → Members
4. Invite member
5. Set role: Admin

# Via Railway CLI
railway login
railway link
railway tokens create  # Share token
```

### Step 3: Database Access
```bash
# Supabase
1. Login: https://supabase.com/dashboard
2. Select project: xrbqnocovfymdikngaza
3. Settings → Team
4. Invite member

# Neon
1. Login: https://console.neon.tech
2. Select project
3. Settings → Members
4. Invite member
```

### Step 4: Share Credentials
```bash
# RECOMMENDED: Use password manager
1. Create shared vault in 1Password/Bitwarden
2. Add all credentials
3. Invite collaborator

# ALTERNATIVE: Encrypted file
7z a -p credentials.7z AKSES_LENGKAP_BOT_CRYPTOMENTOR.md
# Share file + password separately
```

---

## 🧪 Verification Tests

### Test 1: Repository Access
```bash
git clone [repo-url]
cd [repo-name]
ls -la  # Should see all files
```

### Test 2: Railway Access
```bash
railway login
railway link
railway status  # Should show project
railway logs    # Should show logs
```

### Test 3: Database Access
```bash
# Supabase: Login to dashboard
# Neon: Test connection
psql "postgresql://neondb_owner:npg_PXo7pTdgJ4ny@ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech:5432/neondb"
```

### Test 4: Bot Functionality
```
1. Open Telegram
2. Search bot
3. Send /start
4. Should receive welcome message
```

---

## 🔒 Security Reminders

### DO ✅
- Use secure channels (1Password, Signal, encrypted files)
- Share credentials separately from files
- Set expiration on shared access
- Monitor access logs
- Rotate keys after collaboration ends

### DON'T ❌
- Commit .env to git
- Share credentials via email/SMS
- Post credentials in public forums
- Leave access open indefinitely
- Use same keys for dev/prod

---

## 📧 Email Template

```
Subject: Bot CryptoMentor Access

Hi [Name],

Akses bot sudah saya berikan:

✅ GitHub: [link]
✅ Railway: [link]
✅ Supabase: [link]
✅ Credentials: [via 1Password/encrypted file]

Dokumentasi:
- AKSES_LENGKAP_BOT_CRYPTOMENTOR.md (full details)
- QUICK_ACCESS_CHECKLIST.md (quick reference)
- RAILWAY_DEPLOYMENT_GUIDE.md (deployment)

Contact me jika ada pertanyaan.

[Your Name]
```

---

## 🆘 Quick Troubleshooting

### Bot tidak jalan?
```bash
railway logs  # Check errors
railway variables  # Verify env vars
```

### Database connection failed?
```bash
# Check Supabase status
curl https://xrbqnocovfymdikngaza.supabase.co

# Check Neon status
psql "postgresql://..." -c "SELECT 1"
```

### API errors?
```bash
# Test Conway API
curl https://automaton-production-a899.up.railway.app

# Check API key
railway variables | grep CONWAY_API_KEY
```

---

## 📞 Emergency Contacts

**Your Contact:**
- Telegram: @[your_telegram]
- Email: [your_email]

**Platform Support:**
- Railway: https://railway.app/help
- Supabase: https://supabase.com/support
- Telegram: https://telegram.org/support

---

## 📚 Full Documentation

Untuk detail lengkap, lihat:
- `AKSES_LENGKAP_BOT_CRYPTOMENTOR.md` - Complete access guide
- `RAILWAY_DEPLOYMENT_GUIDE.md` - Deployment instructions
- `README.md` - Project overview

---

**Last Updated**: 2026-03-02
**Version**: 1.0.0
