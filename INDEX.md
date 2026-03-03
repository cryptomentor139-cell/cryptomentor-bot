# 🎯 CryptoMentor Bot - Quick Navigation Index

> **Folder telah dirapikan!** Lihat [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) untuk detail struktur folder.

## 🚀 Quick Links

### 📖 Documentation Hub
1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - ⚡ Cheat sheet untuk navigasi cepat
2. **[FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md)** - 📁 Struktur folder lengkap
3. **[CLEANUP_REPORT.md](CLEANUP_REPORT.md)** - 📊 Laporan cleanup & statistik
4. **[UNFINISHED_SPECS.md](UNFINISHED_SPECS.md)** - 📋 Specs yang belum selesai

### 📖 Untuk Pengguna Baru
1. [START HERE - Akses Bot](docs/guides/START_HERE_AKSES_BOT.md)
2. [Cara Menjalankan Bot](docs/guides/CARA_MENJALANKAN_BOT.md)
3. [Quick Start Guide](docs/guides/QUICK_START_GUIDE.md)
4. [Panduan Deployment](docs/guides/PANDUAN_DEPLOYMENT.md)

### 🔧 Untuk Developer
1. [Folder Structure](FOLDER_STRUCTURE.md) - Struktur folder lengkap
2. [App Directory](app/) - Kode aplikasi utama
3. [Tests Directory](tests/) - Testing suite
4. [Scripts Directory](scripts/) - Utility scripts
5. [Unfinished Specs](UNFINISHED_SPECS.md) - Specs yang perlu diselesaikan

### 🚀 Deployment
1. [Railway Quick Start](docs/deployment/RAILWAY_QUICK_START.md)
2. [Deployment Checklist](docs/deployment/DEPLOYMENT_CHECKLIST.md)
3. [Railway Deployment Guide](docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md)
4. [Migration Guide](docs/deployment/MIGRATION_QUICK_START.md)

### ⚡ Fitur Utama

#### 🤖 Automaton AI
- [Automaton Quick Start](docs/features/AUTOMATON_QUICK_START.md)
- [Automaton User Guide](docs/features/AUTOMATON_USER_GUIDE.md)
- [Cara Pakai Automaton AI](docs/guides/CARA_PAKAI_AUTOMATON_AI.md)
- [Automaton Complete Index](docs/features/AUTOMATON_COMPLETE_INDEX.md)

#### 💰 Wallet & Deposit
- [Centralized Wallet Architecture](docs/features/CENTRALIZED_WALLET_ARCHITECTURE.md)
- [Cara Deposit USDC](docs/guides/CARA_DEPOSIT_USDC.md)
- [Deposit Flow Diagram](docs/features/DEPOSIT_FLOW_DIAGRAM.md)

#### 📊 Signal Tracking
- [Signal Tracking Setup](docs/features/SIGNAL_TRACKING_SETUP.md)
- [Cara Test Signal Tracking](docs/guides/CARA_TEST_SIGNAL_TRACKING.md)
- [Signal Tracking Index](docs/features/SIGNAL_TRACKING_INDEX.md)

#### 🎯 Auto Signals
- [Autosignal Analysis](docs/features/AUTOSIGNAL_ANALYSIS.md)
- [Autosignal SMC Integration](docs/features/AUTOSIGNAL_SMC_INTEGRATION.md)
- [Autosignal Fix Quick Guide](docs/features/AUTOSIGNAL_FIX_QUICK_GUIDE.md)

#### 👥 Admin Features
- [Admin Quick Reference](docs/features/ADMIN_QUICK_REFERENCE.md)
- [Admin Credit Guide](docs/features/ADMIN_CREDIT_GUIDE.md)
- [Broadcast Admin Guide](docs/features/BROADCAST_ADMIN_GUIDE.md)

## 📁 Struktur Folder

```
Bismillah/
├── 📱 app/              → Kode aplikasi
├── 📚 docs/             → Dokumentasi
│   ├── deployment/     → Deployment guides
│   ├── features/       → Feature docs
│   ├── guides/         → User guides
│   └── archive/        → Old docs
├── 🧪 tests/            → Testing
│   ├── unit/           → Unit tests
│   ├── integration/    → Integration tests
│   └── property/       → Property tests
├── 🔧 scripts/          → Utilities
│   ├── migration/      → DB migrations
│   ├── setup/          → Setup scripts
│   └── maintenance/    → Maintenance
├── 🗄️ migrations/       → SQL migrations
└── 🤖 automaton/        → Automaton system
```

## 🔍 Cara Mencari Dokumentasi

### Mencari berdasarkan topik:

**Deployment & Railway**
```
docs/deployment/RAILWAY_*.md
docs/deployment/DEPLOYMENT_*.md
```

**Fitur Automaton**
```
docs/features/AUTOMATON_*.md
docs/guides/CARA_PAKAI_AUTOMATON_AI.md
```

**Wallet & Deposit**
```
docs/features/CENTRALIZED_WALLET_*.md
docs/features/DEPOSIT_*.md
docs/guides/CARA_DEPOSIT_USDC.md
```

**Signal Tracking**
```
docs/features/SIGNAL_TRACKING_*.md
docs/guides/CARA_TEST_SIGNAL_TRACKING.md
```

**Admin Features**
```
docs/features/ADMIN_*.md
docs/features/BROADCAST_*.md
```

**Troubleshooting**
```
docs/archive/FIX_*.md
docs/archive/TROUBLESHOOT_*.md
```

## 🛠️ Command Reference

### Menjalankan Bot
```bash
# Windows
start_bot.bat

# Linux/Mac
./start_bot.sh
```

### Testing
```bash
# All tests
pytest

# Specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/property/
```

### Database Migration
```bash
# Run latest migration
python scripts/migration/run_migration_009.py

# Check migration status
python scripts/setup/check_supabase_status.py
```

### Health Checks
```bash
# Check all environment variables
python scripts/setup/check_all_env.py

# Check Automaton health
python scripts/setup/check_automaton_health.py

# Verify deployment
python scripts/setup/verify_deployment.py
```

## 📊 Specs (Kiro Specs)

Specs yang belum selesai ada di `.kiro/specs/`:

1. **cryptomentor-telegram-bot** - Main bot spec
2. **manual-signal-generation-fix** - Manual signal bugfix
3. **dual-mode-offline-online** - Dual mode implementation
4. **ai-agent-deposit-flow** - AI agent deposit flow
5. **automaton-integration** - Automaton integration

Untuk melanjutkan spec, buka di Kiro IDE.

## 🎯 Next Steps

### Jika Anda Baru:
1. Baca [START_HERE_AKSES_BOT.md](docs/guides/START_HERE_AKSES_BOT.md)
2. Setup environment dengan [CARA_MENJALANKAN_BOT.md](docs/guides/CARA_MENJALANKAN_BOT.md)
3. Deploy ke Railway dengan [RAILWAY_QUICK_START.md](docs/deployment/RAILWAY_QUICK_START.md)

### Jika Ingin Deploy:
1. Cek [DEPLOYMENT_CHECKLIST.md](docs/deployment/DEPLOYMENT_CHECKLIST.md)
2. Ikuti [RAILWAY_DEPLOYMENT_GUIDE.md](docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md)
3. Verify dengan [VERIFY_DEPLOYMENT.md](docs/deployment/VERIFY_DEPLOYMENT.md)

### Jika Ingin Develop:
1. Lihat struktur di [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md)
2. Explore [app/](app/) untuk kode aplikasi
3. Run tests di [tests/](tests/)
4. Gunakan scripts di [scripts/](scripts/)

## 📞 Support

Jika ada pertanyaan atau masalah:
1. Cek dokumentasi di `docs/guides/`
2. Lihat troubleshooting di `docs/archive/TROUBLESHOOT_*.md`
3. Cek fix history di `docs/archive/FIX_*.md`

---

**Last Updated**: March 3, 2026  
**Total Files Organized**: 729 files  
**Status**: ✅ Folder Structure Cleaned & Organized
