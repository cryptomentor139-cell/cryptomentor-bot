# 🔐 Akses Lengkap Bot CryptoMentor - Checklist & Credentials

## 📋 Daftar Isi
1. [Informasi Bot & Credentials](#1-informasi-bot--credentials)
2. [Repository & Source Code](#2-repository--source-code)
3. [Railway Deployment Access](#3-railway-deployment-access)
4. [Database & Storage Access](#4-database--storage-access)
5. [API Keys & Third Party Services](#5-api-keys--third-party-services)
6. [Environment Variables Lengkap](#6-environment-variables-lengkap)
7. [Dokumentasi & Panduan](#7-dokumentasi--panduan)
8. [Cara Memberikan Akses](#8-cara-memberikan-akses)

---

## 1. Informasi Bot & Credentials

### 🤖 Telegram Bot
- **Bot Username**: @[Your_Bot_Username]
- **Bot Token**: `8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4`
- **Bot Father Link**: https://t.me/BotFather
- **Admin User IDs**:
  - Admin 1: `1187119989`
  - Admin 2: `7079544380`
  - Admin 3: `Optional` (belum diset)

### 🔑 Status Credentials
- ✅ Bot Token: **TERSEDIA**
- ✅ Admin IDs: **TERSEDIA**
- ⚠️ Bot Username: **PERLU DICEK** (tidak ada di .env)

---

## 2. Repository & Source Code

### 📂 Struktur Project

**Project Utama (Python Bot):**
```
Bismillah/
├── bot.py                          # Main bot file
├── app/                            # Core application modules
│   ├── handlers_*.py              # Command handlers
│   ├── dual_mode/                 # Dual mode (offline/online)
│   ├── isolated_ai_manager.py     # AI agent management
│   ├── conway_integration.py      # Conway API integration
│   ├── automaton_manager.py       # Automaton management
│   └── ...
├── migrations/                     # Database migrations
├── .env                           # Environment variables
└── requirements.txt               # Python dependencies
```

**Project Node.js (Telegram Bot - Alternatif):**
```
cryptomentor-bot/
├── index.js                       # Main bot file
├── error-messages.js              # Error handling
├── package.json                   # Dependencies
└── README.md                      # Documentation
```

### 🔗 Repository Access

**Untuk memberikan akses repository:**

#### Option 1: GitHub Repository (Jika sudah ada)
```bash
# Jika repository sudah di GitHub
# Invite collaborator:
# 1. Go to: https://github.com/[your-username]/[repo-name]/settings/access
# 2. Click "Invite a collaborator"
# 3. Enter email atau username
# 4. Set permission: "Write" atau "Admin"
```

#### Option 2: Upload ke GitHub (Jika belum ada)
```bash
# 1. Buat repository baru di GitHub
# 2. Initialize git di local
cd Bismillah
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/[username]/[repo-name].git
git push -u origin main

# 3. Invite collaborator (lihat Option 1)
```

#### Option 3: Share via ZIP (Temporary)
```bash
# Compress project (exclude sensitive files)
# Windows PowerShell:
Compress-Archive -Path Bismillah -DestinationPath cryptomentor-bot-source.zip

# Atau manual: Right-click folder → Send to → Compressed folder
# Upload ke Google Drive / Dropbox dan share link
```

### ⚠️ PENTING: File yang TIDAK boleh di-commit
```gitignore
.env
*.pyc
__pycache__/
node_modules/
.hypothesis/
*.log
*.db
```

---

## 3. Railway Deployment Access

### 🚂 Railway Project Information

**Bot Deployment:**
- **Platform**: Railway.app
- **Project Name**: `cryptomentor-telegram-bot` (atau sesuai nama Anda)
- **Service Type**: Python Bot (Bismillah) atau Node.js Bot (cryptomentor-bot)
- **Region**: Auto-selected by Railway

**Automaton API Deployment:**
- **URL**: `https://automaton-production-a899.up.railway.app`
- **Project**: Separate Railway project
- **API Key**: `cnwy_k_HeT-F6vsVC_z6pmhYbBOyo1UJHtFhXyr`

### 📝 Cara Memberikan Akses Railway

#### Method 1: Invite ke Team (RECOMMENDED)
1. Login ke Railway: https://railway.app/dashboard
2. Pilih project bot Anda
3. Click "Settings" → "Members"
4. Click "Invite Member"
5. Masukkan email collaborator
6. Set role: "Admin" atau "Developer"
7. Send invitation

#### Method 2: Share Login Sementara
```
⚠️ TIDAK RECOMMENDED untuk production
Hanya untuk testing/debugging sementara:

1. Buat akun Railway baru khusus untuk sharing
2. Deploy bot ke akun tersebut
3. Share credentials akun tersebut
4. Setelah selesai, transfer project ke akun utama
```

#### Method 3: Share Environment Variables & Deploy Token
```bash
# Generate Railway deploy token
railway login
railway whoami
railway tokens create

# Share token ini untuk deployment access
# Token format: railway_token_xxxxxxxxxxxxx
```

### 🔍 Monitoring & Logs

**Cara akses logs:**
```bash
# Via Railway CLI
railway login
railway link  # Link ke project
railway logs  # View logs
railway logs --tail  # Live logs

# Via Railway Dashboard
# 1. Go to project
# 2. Click "Deployments"
# 3. Click latest deployment
# 4. View logs in real-time
```

---

## 4. Database & Storage Access

### 🗄️ Supabase Database

**Connection Details:**
- **URL**: `https://xrbqnocovfymdikngaza.supabase.co`
- **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUzMjExOTksImV4cCI6MjA3MDg5NzE5OX0.placeholder`
- **Service Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTMyMTE5OSwiZXhwIjoyMDcwODk3MTk5fQ.QGIlCWKqy8fe0bKJbx6CAqeSr7fq17NBXqNeC8nUu5Y`

**Cara memberikan akses:**
1. Login ke Supabase: https://supabase.com/dashboard
2. Pilih project: `xrbqnocovfymdikngaza`
3. Go to "Settings" → "Team"
4. Click "Invite member"
5. Enter email dan set role: "Developer" atau "Admin"

### 🗄️ Neon Database (PostgreSQL)

**Connection Details:**
- **Host**: `ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech`
- **Database**: `neondb`
- **User**: `neondb_owner`
- **Password**: `npg_PXo7pTdgJ4ny`
- **Port**: `5432`

**Connection String:**
```
postgresql://neondb_owner:npg_PXo7pTdgJ4ny@ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech:5432/neondb
```

**Cara memberikan akses:**
1. Login ke Neon: https://console.neon.tech
2. Pilih project
3. Go to "Settings" → "Members"
4. Invite collaborator

### 💾 Google Drive Storage

**Path**: `G:/Drive Saya/CryptoBot_Signals`

**Cara memberikan akses:**
1. Buka Google Drive
2. Navigate ke folder `CryptoBot_Signals`
3. Right-click → Share
4. Add email collaborator
5. Set permission: "Editor" atau "Viewer"

---

## 5. API Keys & Third Party Services

### 🔑 AI & Data Provider APIs

#### 1. DeepSeek AI (via OpenRouter)
- **API Key**: `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`
- **Base URL**: `https://openrouter.ai/api/v1`
- **Model**: `google/gemini-flash-1.5` (FREE & FAST)
- **Dashboard**: https://openrouter.ai/dashboard

#### 2. Cerebras AI
- **API Key**: `csk-8ee6jd8ekjcwyhtdx6yk3r3dhkewe88t9mv54k5yce295p3n`
- **Dashboard**: https://cerebras.ai/dashboard

#### 3. CryptoNews API
- **API Key**: `2iqmgpfhhlcvrq9sqxhppabo8pxppg5pv1ue37x8`
- **Dashboard**: https://cryptonews-api.com/dashboard

#### 4. Helius RPC (Solana)
- **API Key**: `3b32e914-4a27-417d-8dab-a70a1a9d1e8c`
- **Dashboard**: https://www.helius.dev/dashboard

#### 5. CryptoCompare API
- **API Key**: `44d575a1b1df76144a11214917bd37649345ffc2f8a88aee907671850dd662a9`
- **Dashboard**: https://min-api.cryptocompare.com/

### 🔗 Conway API (Automaton)

- **API URL**: `https://automaton-production-a899.up.railway.app`
- **API Key**: `cnwy_k_HeT-F6vsVC_z6pmhYbBOyo1UJHtFhXyr`
- **Wallet Address**: `0x63116672bef9f26fd906cd2a57550f7a13925822`

### 🔐 Encryption & Security

- **Encryption Key**: `Gq-ymFPUufXwh-OvL4HM2BnrB--_WBecaUmwuEpm_KI=`
- **Session Secret**: `FZ+1sD4r0TLgs7r7vs1bZtPNerUjVDwtdgFM0DQ8TAJcKbs6wwGd6rSSZFdtIYGjsCoG4ANGf6+rdW+0tz6/XA==`

⚠️ **CRITICAL**: Jangan pernah share keys ini di public!

---

## 6. Environment Variables Lengkap

### 📄 File .env Lengkap

```env
# ============================================
# TELEGRAM BOT CONFIGURATION
# ============================================
TOKEN=8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4
TELEGRAM_BOT_TOKEN=8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4

# ============================================
# ADMIN CONFIGURATION
# ============================================
ADMIN1=1187119989
ADMIN2=7079544380
ADMIN3=Optional

# ============================================
# AI CONFIGURATION
# ============================================
# DeepSeek AI (via OpenRouter - FREE & FAST)
DEEPSEEK_API_KEY=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
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=google/gemini-flash-1.5

# Cerebras AI
CEREBRAS_API_KEY=csk-8ee6jd8ekjcwyhtdx6yk3r3dhkewe88t9mv54k5yce295p3n

# ============================================
# DATA PROVIDERS
# ============================================
# CryptoNews API
CRYPTONEWS_API_KEY=2iqmgpfhhlcvrq9sqxhppabo8pxppg5pv1ue37x8

# Helius RPC (Solana)
HELIUS_API_KEY=3b32e914-4a27-417d-8dab-a70a1a9d1e8c

# CryptoCompare API
CRYPTOCOMPARE_API_KEY=44d575a1b1df76144a11214917bd37649345ffc2f8a88aee907671850dd662a9

# ============================================
# DATABASE CONFIGURATION
# ============================================
# Supabase
SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUzMjExOTksImV4cCI6MjA3MDg5NzE5OX0.placeholder
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTMyMTE5OSwiZXhwIjoyMDcwODk3MTk5fQ.QGIlCWKqy8fe0bKJbx6CAqeSr7fq17NBXqNeC8nUu5Y
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTMyMTE5OSwiZXhwIjoyMDcwODk3MTk5fQ.QGIlCWKqy8fe0bKJbx6CAqeSr7fq17NBXqNeC8nUu5Y

# Neon PostgreSQL
PGHOST=ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech
PGDATABASE=neondb
PGUSER=neondb_owner
PGPASSWORD=npg_PXo7pTdgJ4ny
PGPORT=5432

# ============================================
# CONWAY API (AUTOMATON)
# ============================================
CONWAY_API_URL=https://automaton-production-a899.up.railway.app
CONWAY_API_KEY=cnwy_k_HeT-F6vsVC_z6pmhYbBOyo1UJHtFhXyr
CONWAY_WALLET_ADDRESS=0x0000000000000000000000000000000000000000

# ============================================
# WALLET & ENCRYPTION
# ============================================
ENCRYPTION_KEY=Gq-ymFPUufXwh-OvL4HM2BnrB--_WBecaUmwuEpm_KI=
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822
SESSION_SECRET=FZ+1sD4r0TLgs7r7vs1bZtPNerUjVDwtdgFM0DQ8TAJcKbs6wwGd6rSSZFdtIYGjsCoG4ANGf6+rdW+0tz6/XA==

# ============================================
# BOT SETTINGS
# ============================================
WELCOME_CREDITS=100
USE_LEGACY_FUTURES_SIGNALS=true

# ============================================
# STORAGE
# ============================================
GDRIVE_PATH=G:/Drive Saya/CryptoBot_Signals
```

### 📋 Cara Set di Railway

```bash
# Via Railway CLI
railway login
railway link

# Set semua variables
railway variables set TELEGRAM_BOT_TOKEN="8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4"
railway variables set ADMIN1="1187119989"
railway variables set ADMIN2="7079544380"
railway variables set DEEPSEEK_API_KEY="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"
railway variables set DEEPSEEK_BASE_URL="https://openrouter.ai/api/v1"
railway variables set AI_MODEL="google/gemini-flash-1.5"
railway variables set CEREBRAS_API_KEY="csk-8ee6jd8ekjcwyhtdx6yk3r3dhkewe88t9mv54k5yce295p3n"
railway variables set CRYPTONEWS_API_KEY="2iqmgpfhhlcvrq9sqxhppabo8pxppg5pv1ue37x8"
railway variables set HELIUS_API_KEY="3b32e914-4a27-417d-8dab-a70a1a9d1e8c"
railway variables set CRYPTOCOMPARE_API_KEY="44d575a1b1df76144a11214917bd37649345ffc2f8a88aee907671850dd662a9"
railway variables set SUPABASE_URL="https://xrbqnocovfymdikngaza.supabase.co"
railway variables set SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTMyMTE5OSwiZXhwIjoyMDcwODk3MTk5fQ.QGIlCWKqy8fe0bKJbx6CAqeSr7fq17NBXqNeC8nUu5Y"
railway variables set PGHOST="ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech"
railway variables set PGDATABASE="neondb"
railway variables set PGUSER="neondb_owner"
railway variables set PGPASSWORD="npg_PXo7pTdgJ4ny"
railway variables set PGPORT="5432"
railway variables set CONWAY_API_URL="https://automaton-production-a899.up.railway.app"
railway variables set CONWAY_API_KEY="cnwy_k_HeT-F6vsVC_z6pmhYbBOyo1UJHtFhXyr"
railway variables set ENCRYPTION_KEY="Gq-ymFPUufXwh-OvL4HM2BnrB--_WBecaUmwuEpm_KI="
railway variables set CENTRALIZED_WALLET_ADDRESS="0x63116672bef9f26fd906cd2a57550f7a13925822"
railway variables set SESSION_SECRET="FZ+1sD4r0TLgs7r7vs1bZtPNerUjVDwtdgFM0DQ8TAJcKbs6wwGd6rSSZFdtIYGjsCoG4ANGf6+rdW+0tz6/XA=="
railway variables set WELCOME_CREDITS="100"
railway variables set USE_LEGACY_FUTURES_SIGNALS="true"

# Verify
railway variables
```

---

## 7. Dokumentasi & Panduan

### 📚 Dokumentasi Tersedia

**Deployment & Setup:**
- `RAILWAY_DEPLOYMENT_GUIDE.md` - Panduan deploy ke Railway
- `RAILWAY_ENV_SETUP.md` - Setup environment variables
- `DEPLOYMENT_CHECKLIST.md` - Checklist deployment
- `QUICK_START_GUIDE.md` - Quick start guide

**Feature Documentation:**
- `AUTOMATON_INTEGRATION_COMPLETE.md` - Automaton integration
- `ISOLATED_AI_TRADING_SOLUTION.md` - Isolated AI trading
- `CENTRALIZED_WALLET_ARCHITECTURE.md` - Wallet system
- `DUAL_MODE_OFFLINE_ONLINE/` - Dual mode feature

**User Guides:**
- `CARA_PAKAI_CEO_AGENT.md` - CEO Agent usage
- `CARA_DEPOSIT_USDC.md` - Deposit guide
- `ADMIN_QUICK_REFERENCE.md` - Admin commands

**Technical Docs:**
- `ARCHITECTURE_TWO_SERVERS.md` - Architecture overview
- `AUTOMATON_ARCHITECTURE_FINAL.md` - Automaton architecture
- `REVENUE_SHARING_LINEAGE_GUIDE.md` - Revenue system

### 🔗 Link Penting

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Railway Docs**: https://docs.railway.app/
- **Supabase Docs**: https://supabase.com/docs
- **OpenRouter Docs**: https://openrouter.ai/docs

---

## 8. Cara Memberikan Akses

### ✅ Checklist Akses yang Perlu Diberikan

#### 1. Repository Access
- [ ] Invite ke GitHub repository (atau share ZIP)
- [ ] Berikan akses "Write" atau "Admin"
- [ ] Share link repository

#### 2. Railway Access
- [ ] Invite ke Railway project (bot)
- [ ] Invite ke Railway project (Automaton API)
- [ ] Set role: "Admin" atau "Developer"

#### 3. Database Access
- [ ] Invite ke Supabase project
- [ ] Invite ke Neon database
- [ ] Share connection strings

#### 4. API Keys
- [ ] Share semua API keys (via secure channel)
- [ ] Provide dashboard access jika perlu
- [ ] Document API limits & quotas

#### 5. Documentation
- [ ] Share semua dokumentasi
- [ ] Provide architecture diagrams
- [ ] Share deployment guides

### 🔒 Cara Aman Share Credentials

#### Option 1: Password Manager (RECOMMENDED)
```
1. Gunakan 1Password / Bitwarden / LastPass
2. Create shared vault
3. Add semua credentials ke vault
4. Invite collaborator ke vault
5. Set expiration jika perlu
```

#### Option 2: Encrypted File
```bash
# Encrypt file dengan password
# Windows (7-Zip):
7z a -p -mhe=on credentials.7z AKSES_LENGKAP_BOT_CRYPTOMENTOR.md

# Share file + password via different channels
# File via email/drive
# Password via WhatsApp/Telegram
```

#### Option 3: Secure Messaging
```
1. Gunakan Signal / Telegram Secret Chat
2. Enable disappearing messages
3. Share credentials satu per satu
4. Confirm receipt
5. Delete messages after confirmed
```

### 📧 Template Email untuk Invite

```
Subject: Akses Bot CryptoMentor - [Your Name]

Hi [Collaborator Name],

Saya ingin memberikan akses penuh ke bot CryptoMentor untuk [tujuan: development/debugging/maintenance].

Berikut akses yang sudah saya berikan:

✅ GitHub Repository: [link]
✅ Railway Project: [link]
✅ Supabase Database: [link]
✅ Credentials: [shared via 1Password/encrypted file]

Dokumentasi lengkap ada di repository di file:
- AKSES_LENGKAP_BOT_CRYPTOMENTOR.md
- RAILWAY_DEPLOYMENT_GUIDE.md
- README.md

Jika ada pertanyaan, silakan hubungi saya.

Best regards,
[Your Name]
```

---

## 9. Testing & Verification

### ✅ Checklist Setelah Memberikan Akses

#### Test Repository Access
```bash
# Collaborator test clone
git clone [repository-url]
cd [repository-name]

# Verify files
ls -la
cat .env.example  # Should exist
cat README.md     # Should exist
```

#### Test Railway Access
```bash
# Collaborator test Railway CLI
railway login
railway link
railway status
railway logs

# Should see project info
```

#### Test Database Access
```bash
# Test Supabase
# Go to: https://supabase.com/dashboard
# Should see project

# Test Neon
psql "postgresql://neondb_owner:npg_PXo7pTdgJ4ny@ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech:5432/neondb"
# Should connect
```

#### Test Bot
```bash
# Collaborator test bot
# 1. Open Telegram
# 2. Search bot
# 3. Send /start
# 4. Should receive welcome message
```

---

## 10. Security Best Practices

### 🔐 Keamanan Credentials

1. **NEVER commit .env to git**
   ```bash
   # Verify .gitignore
   cat .gitignore | grep .env
   # Should show: .env
   ```

2. **Rotate keys regularly**
   - Bot token: Every 6 months
   - API keys: Every 3 months
   - Database passwords: Every 3 months

3. **Use environment-specific keys**
   - Development: Separate keys
   - Staging: Separate keys
   - Production: Separate keys

4. **Monitor access logs**
   ```bash
   # Railway logs
   railway logs --tail

   # Supabase logs
   # Dashboard → Logs

   # Neon logs
   # Dashboard → Monitoring
   ```

5. **Revoke access when done**
   - Remove from GitHub
   - Remove from Railway
   - Remove from databases
   - Rotate shared keys

### ⚠️ Red Flags

Watch out for:
- Unusual API usage spikes
- Failed login attempts
- Unauthorized deployments
- Database schema changes
- Unexpected bot behavior

---

## 11. Support & Contact

### 📞 Jika Ada Masalah

**Bot Issues:**
- Check Railway logs: `railway logs`
- Check Telegram bot status: https://t.me/[your_bot]
- Verify environment variables

**Database Issues:**
- Check Supabase status: https://status.supabase.com/
- Check Neon status: https://neon.tech/status
- Verify connection strings

**API Issues:**
- Check Conway API: `curl https://automaton-production-a899.up.railway.app`
- Check OpenRouter status: https://openrouter.ai/status
- Verify API keys

### 📧 Contact Information

**Your Contact:**
- Telegram: @[your_telegram]
- Email: [your_email]
- Phone: [your_phone]

**Emergency Contacts:**
- Railway Support: https://railway.app/help
- Supabase Support: https://supabase.com/support
- Telegram Support: https://telegram.org/support

---

## 📝 Changelog

### Version 1.0.0 (2026-03-02)
- ✅ Initial documentation
- ✅ All credentials documented
- ✅ Access procedures defined
- ✅ Security guidelines added

---

## ⚠️ DISCLAIMER

**PENTING:**
- Dokumen ini berisi informasi sensitif
- Jangan share di public (GitHub, forum, dll)
- Gunakan secure channel untuk sharing
- Revoke access setelah tidak dibutuhkan
- Rotate keys secara berkala

**TANGGUNG JAWAB:**
- Anda bertanggung jawab atas keamanan credentials
- Collaborator harus sign NDA jika perlu
- Monitor semua akses dan aktivitas
- Report suspicious activity immediately

---

**Last Updated**: 2026-03-02
**Document Version**: 1.0.0
**Status**: ✅ Ready for sharing
