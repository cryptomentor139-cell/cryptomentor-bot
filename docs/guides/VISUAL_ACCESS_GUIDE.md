# 🎨 Visual Access Guide - CryptoMentor Bot

## 📊 Diagram & Visual Guides

Dokumen ini berisi diagram visual untuk memudahkan pemahaman struktur akses dan flow.

---

## 🗺️ 1. Dokumentasi Navigation Map

```
┌─────────────────────────────────────────────────────────────┐
│                    START_HERE_AKSES_BOT.md                   │
│                    (📍 YOU START HERE)                       │
│                                                              │
│  "Saya ingin..."                                            │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ Memberikan akses │  │ Setup development│               │
│  │ ke orang lain    │  │ environment      │               │
│  └────────┬─────────┘  └────────┬─────────┘               │
│           │                      │                          │
│           ▼                      ▼                          │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ AKSES_LENGKAP_   │  │ CREDENTIALS_     │               │
│  │ BOT_CRYPTOMENTOR │  │ EXPORT.txt       │               │
│  │ .md              │  │                  │               │
│  └────────┬─────────┘  └──────────────────┘               │
│           │                                                 │
│           ▼                                                 │
│  ┌──────────────────┐                                      │
│  │ INVITATION_      │                                      │
│  │ TEMPLATES.md     │                                      │
│  └──────────────────┘                                      │
│                                                              │
│  Need quick reference?                                      │
│           │                                                 │
│           ▼                                                 │
│  ┌──────────────────┐                                      │
│  │ QUICK_ACCESS_    │                                      │
│  │ CHECKLIST.md     │                                      │
│  └──────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 2. Access Granting Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    ACCESS GRANTING FLOW                      │
└─────────────────────────────────────────────────────────────┘

Step 1: PREPARATION
┌──────────────────────────────────────────┐
│ 1. Review documentation                  │
│ 2. Verify credentials valid              │
│ 3. Setup password manager                │
│ 4. Prepare invitation email              │
└──────────────┬───────────────────────────┘
               │
               ▼
Step 2: PLATFORM ACCESS
┌──────────────────────────────────────────┐
│ Invite to:                               │
│ ✅ GitHub Repository                     │
│ ✅ Railway Projects (Bot + Automaton)   │
│ ✅ Supabase Database                     │
│ ✅ Neon Database                         │
└──────────────┬───────────────────────────┘
               │
               ▼
Step 3: CREDENTIALS SHARING
┌──────────────────────────────────────────┐
│ Share via secure channel:                │
│ • 1Password shared vault (RECOMMENDED)   │
│ • Encrypted file (7-Zip)                 │
│ • Signal/Telegram secret chat            │
│                                          │
│ Share:                                   │
│ • CREDENTIALS_EXPORT.txt                 │
│ • All documentation files                │
└──────────────┬───────────────────────────┘
               │
               ▼
Step 4: SEND INVITATION
┌──────────────────────────────────────────┐
│ Use template from:                       │
│ INVITATION_TEMPLATES.md                  │
│                                          │
│ Include:                                 │
│ • Access details                         │
│ • Documentation links                    │
│ • Quick start guide                      │
│ • Contact information                    │
└──────────────┬───────────────────────────┘
               │
               ▼
Step 5: VERIFICATION
┌──────────────────────────────────────────┐
│ Verify collaborator can:                 │
│ ✅ Access GitHub                         │
│ ✅ Access Railway                        │
│ ✅ Access databases                      │
│ ✅ Run bot locally                       │
│ ✅ Deploy to Railway                     │
└──────────────┬───────────────────────────┘
               │
               ▼
Step 6: MONITORING
┌──────────────────────────────────────────┐
│ Monitor:                                 │
│ • Railway logs                           │
│ • Database access logs                   │
│ • GitHub commits                         │
│ • Unusual activity                       │
└──────────────────────────────────────────┘
```

---

## 🏗️ 3. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CRYPTOMENTOR BOT SYSTEM                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                         USERS                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ User A   │  │ User B   │  │ User N   │                 │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                 │
└───────┼─────────────┼─────────────┼────────────────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    TELEGRAM API                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              CRYPTOMENTOR BOT (Railway)                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  bot.py                                            │    │
│  │  ├── Command Handlers                              │    │
│  │  ├── Dual Mode (Offline/Online)                    │    │
│  │  ├── AI Agent Manager                              │    │
│  │  └── Error Handler                                 │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Environment Variables:                                     │
│  • TELEGRAM_BOT_TOKEN                                       │
│  • DEEPSEEK_API_KEY                                         │
│  • SUPABASE_URL                                             │
│  • CONWAY_API_KEY                                           │
│  • etc.                                                     │
└──────────┬───────────────────────┬──────────────────────────┘
           │                       │
           ▼                       ▼
┌──────────────────────┐  ┌──────────────────────┐
│   DATABASES          │  │   EXTERNAL APIs      │
│                      │  │                      │
│  ┌────────────────┐ │  │  ┌────────────────┐ │
│  │ Supabase       │ │  │  │ Conway API     │ │
│  │ (User data)    │ │  │  │ (Automaton)    │ │
│  └────────────────┘ │  │  └────────────────┘ │
│                      │  │                      │
│  ┌────────────────┐ │  │  ┌────────────────┐ │
│  │ Neon           │ │  │  │ DeepSeek AI    │ │
│  │ (PostgreSQL)   │ │  │  │ (OpenRouter)   │ │
│  └────────────────┘ │  │  └────────────────┘ │
│                      │  │                      │
│  ┌────────────────┐ │  │  ┌────────────────┐ │
│  │ Google Drive   │ │  │  │ CryptoNews     │ │
│  │ (Signals)      │ │  │  │ API            │ │
│  └────────────────┘ │  │  └────────────────┘ │
└──────────────────────┘  └──────────────────────┘
```

---

## 🔐 4. Access Levels Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      ACCESS LEVELS                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  LEVEL 1: OWNER (YOU)                                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ✅ Full access to everything                       │    │
│  │ ✅ Can grant/revoke access                         │    │
│  │ ✅ Can modify all platforms                        │    │
│  │ ✅ Has all credentials                             │    │
│  │ ✅ Can transfer ownership                          │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 2: ADMIN (Full Access)                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ✅ GitHub: Write/Admin                             │    │
│  │ ✅ Railway: Admin                                  │    │
│  │ ✅ Database: Developer                             │    │
│  │ ✅ All credentials                                 │    │
│  │ ✅ Can deploy & modify                             │    │
│  │ ❌ Cannot transfer ownership                       │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 3: DEVELOPER (Write Access)                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ✅ GitHub: Write                                   │    │
│  │ ✅ Railway: Developer                              │    │
│  │ ✅ Database: Read/Write                            │    │
│  │ ✅ Most credentials                                │    │
│  │ ✅ Can deploy                                      │    │
│  │ ❌ Cannot modify settings                          │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 4: VIEWER (Read-Only)                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ✅ GitHub: Read                                    │    │
│  │ ✅ Railway: Viewer                                 │    │
│  │ ✅ Database: Read-Only                             │    │
│  │ ❌ No credentials                                  │    │
│  │ ❌ Cannot deploy                                   │    │
│  │ ❌ Cannot modify                                   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 5: TEMPORARY (Time-Limited)                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ⏰ Access expires: [Date]                          │    │
│  │ ✅ Task-specific access                            │    │
│  │ ✅ Limited credentials                             │    │
│  │ ✅ Monitored activity                              │    │
│  │ ❌ Auto-revoked after expiration                   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 5. Credentials Organization

```
┌─────────────────────────────────────────────────────────────┐
│                    CREDENTIALS STRUCTURE                     │
└─────────────────────────────────────────────────────────────┘

CREDENTIALS_EXPORT.txt
│
├── 1. TELEGRAM BOT
│   ├── Bot Token
│   └── Admin IDs
│
├── 2. AI PROVIDERS
│   ├── DeepSeek (OpenRouter)
│   └── Cerebras
│
├── 3. DATA PROVIDERS
│   ├── CryptoNews API
│   ├── Helius RPC
│   └── CryptoCompare
│
├── 4. DATABASES
│   ├── Supabase
│   │   ├── URL
│   │   ├── Anon Key
│   │   └── Service Key
│   │
│   └── Neon PostgreSQL
│       ├── Host
│       ├── Database
│       ├── User
│       ├── Password
│       └── Connection String
│
├── 5. CONWAY API
│   ├── API URL
│   ├── API Key
│   └── Wallet Address
│
├── 6. SECURITY
│   ├── Encryption Key
│   └── Session Secret
│
└── 7. COMPLETE .ENV FILE
    └── (Ready to copy-paste)
```

---

## 🔄 6. Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT FLOW                           │
└─────────────────────────────────────────────────────────────┘

LOCAL DEVELOPMENT
┌──────────────────────────────────────────┐
│ 1. Clone repository                      │
│    git clone [repo-url]                  │
│                                          │
│ 2. Setup environment                     │
│    Copy .env from CREDENTIALS_EXPORT.txt │
│                                          │
│ 3. Install dependencies                  │
│    pip install -r requirements.txt       │
│                                          │
│ 4. Run locally                           │
│    python bot.py                         │
└──────────────┬───────────────────────────┘
               │
               │ (Test locally first)
               │
               ▼
RAILWAY DEPLOYMENT
┌──────────────────────────────────────────┐
│ 1. Login to Railway                      │
│    railway login                         │
│                                          │
│ 2. Link to project                       │
│    railway link                          │
│                                          │
│ 3. Set environment variables             │
│    railway variables set KEY="value"     │
│    (Copy commands from                   │
│     CREDENTIALS_EXPORT.txt)              │
│                                          │
│ 4. Deploy                                │
│    railway up                            │
└──────────────┬───────────────────────────┘
               │
               ▼
VERIFICATION
┌──────────────────────────────────────────┐
│ 1. Check logs                            │
│    railway logs                          │
│                                          │
│ 2. Test bot                              │
│    Open Telegram → Send /start           │
│                                          │
│ 3. Monitor                               │
│    railway logs --tail                   │
└──────────────────────────────────────────┘
```

---

## 🛡️ 7. Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                           │
└─────────────────────────────────────────────────────────────┘

Layer 1: CREDENTIAL PROTECTION
┌──────────────────────────────────────────┐
│ • Never commit .env to git               │
│ • Use .gitignore                         │
│ • Encrypt files before sharing           │
│ • Use password managers                  │
└──────────────┬───────────────────────────┘
               │
               ▼
Layer 2: ACCESS CONTROL
┌──────────────────────────────────────────┐
│ • Different access levels                │
│ • Temporary access with expiration       │
│ • Read-only for reviewers                │
│ • Monitor access logs                    │
└──────────────┬───────────────────────────┘
               │
               ▼
Layer 3: SECURE SHARING
┌──────────────────────────────────────────┐
│ • 1Password shared vault                 │
│ • Encrypted files (7-Zip)                │
│ • Signal/Telegram secret chat            │
│ • Separate channels for file & password  │
└──────────────┬───────────────────────────┘
               │
               ▼
Layer 4: KEY ROTATION
┌──────────────────────────────────────────┐
│ • Rotate after collaboration ends        │
│ • Rotate every 3-6 months                │
│ • Rotate if compromised                  │
│ • Document rotation schedule             │
└──────────────┬───────────────────────────┘
               │
               ▼
Layer 5: MONITORING
┌──────────────���───────────────────────────┐
│ • Railway logs                           │
│ • Database access logs                   │
│ • GitHub commit history                  │
│ • Alert on unusual activity              │
└──────────────────────────────────────────┘
```

---

## 📊 8. Documentation Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                  DOCUMENTATION HIERARCHY                     │
└─────────────────────────────────────────────────────────────┘

                    START_HERE_AKSES_BOT.md
                            │
                            │ (Navigation Hub)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ AKSES_LENGKAP │  │ QUICK_ACCESS  │  │ CREDENTIALS_  │
│ _BOT_CRYPTO   │  │ _CHECKLIST    │  │ EXPORT.txt    │
│ MENTOR.md     │  │ .md           │  │               │
│               │  │               │  │               │
│ (Complete     │  │ (Quick        │  │ (Copy-Paste   │
│  Guide)       │  │  Reference)   │  │  Ready)       │
└───────┬───────┘  └───────────────┘  └───────────────┘
        │
        │
        ▼
┌───────────────┐
│ INVITATION_   │
│ TEMPLATES.md  │
│               │
│ (Email        │
│  Templates)   │
└───────────────┘

Supporting Documents:
├── SUMMARY_DOKUMENTASI_AKSES.md (This summary)
├── VISUAL_ACCESS_GUIDE.md (Visual diagrams)
├── RAILWAY_DEPLOYMENT_GUIDE.md (Deployment)
└── README.md (Project overview)
```

---

## 🎯 9. Quick Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│              WHICH DOCUMENT SHOULD I READ?                   │
└─────────────────────────────────────────────────────────────┘

START: What do you want to do?
│
├─ Give access to someone?
│  │
│  ├─ First time? → Read AKSES_LENGKAP_BOT_CRYPTOMENTOR.md
│  │
│  ├─ Already familiar? → Use QUICK_ACCESS_CHECKLIST.md
│  │
│  └─ Need email template? → Use INVITATION_TEMPLATES.md
│
├─ Setup development environment?
│  │
│  └─ Copy from CREDENTIALS_EXPORT.txt
│
├─ Deploy to Railway?
│  │
│  ├─ First time? → Read RAILWAY_DEPLOYMENT_GUIDE.md
│  │
│  └─ Already know how? → Copy commands from CREDENTIALS_EXPORT.txt
│
├─ Need overview?
│  │
│  └─ Read START_HERE_AKSES_BOT.md
│
└─ Troubleshooting?
   │
   └─ Check QUICK_ACCESS_CHECKLIST.md → Troubleshooting section
```

---

## 📈 10. Access Timeline

```
┌─────────────────────────────────────────────────────────────┐
│                    ACCESS TIMELINE                           │
└─────────────────────────────────────────────────────────────┘

DAY 0: PREPARATION
├─ Review documentation
├─ Verify credentials
├─ Setup password manager
└─ Prepare invitation

DAY 1: GRANT ACCESS
├─ Invite to platforms
├─ Share credentials
├─ Send documentation
└─ Send invitation email

DAY 2-3: VERIFICATION
├─ Confirm access received
├─ Verify can access all platforms
├─ Test bot locally
└─ Answer questions

WEEK 1: MONITORING
├─ Check access logs
├─ Monitor activity
├─ Provide support
└─ Address issues

ONGOING: MAINTENANCE
├─ Monitor regularly
├─ Review access list
├─ Rotate keys (every 3-6 months)
└─ Revoke when done

END: REVOCATION (if temporary)
├─ Remove from platforms
├─ Rotate shared credentials
├─ Verify access removed
└─ Document completion
```

---

## ✅ Summary

Dokumen ini menyediakan **visual guides** untuk:

1. ✅ Navigation map (cara navigasi dokumentasi)
2. ✅ Access granting flow (proses memberikan akses)
3. ✅ System architecture (struktur sistem)
4. ✅ Access levels (level akses)
5. ✅ Credentials organization (organisasi credentials)
6. ✅ Deployment flow (proses deployment)
7. ✅ Security layers (lapisan keamanan)
8. ✅ Documentation hierarchy (hierarki dokumentasi)
9. ✅ Decision tree (pohon keputusan)
10. ✅ Access timeline (timeline akses)

**Gunakan diagram ini untuk**:
- Memahami struktur dokumentasi
- Memvisualisasikan proses akses
- Menjelaskan ke collaborator
- Quick reference

---

**Last Updated**: 2026-03-02
**Version**: 1.0.0
