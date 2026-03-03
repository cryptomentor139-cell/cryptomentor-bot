# 📁 Struktur Folder Bismillah - CryptoMentor Bot

Folder ini telah dirapikan dan diorganisir untuk memudahkan navigasi dan maintenance.

## 🗂️ Struktur Utama

```
Bismillah/
├── 📱 app/                    # Kode aplikasi utama
│   ├── handlers_*.py         # Handler untuk berbagai fitur
│   ├── dual_mode/            # Sistem dual mode (online/offline)
│   └── providers/            # Data providers (Binance, dll)
│
├── 📚 docs/                   # Dokumentasi lengkap
│   ├── deployment/           # Panduan deployment & Railway
│   ├── features/             # Dokumentasi fitur-fitur
│   ├── guides/               # Panduan pengguna
│   └── archive/              # Dokumentasi lama/deprecated
│
├── 🧪 tests/                  # Testing suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── property/             # Property-based tests
│
├── 🔧 scripts/                # Utility scripts
│   ├── migration/            # Database migration scripts
│   ├── setup/                # Setup & verification scripts
│   └── maintenance/          # Maintenance & utility scripts
│
├── 🗄️ migrations/             # Database migrations (SQL)
├── 🤖 automaton/              # Automaton AI system
├── 📊 data/                   # Data files
├── 📝 signal_logs/            # Signal tracking logs
│
└── 📄 [Root Files]            # File konfigurasi utama
    ├── bot.py                # Main bot file
    ├── .env                  # Environment variables
    ├── requirements.txt      # Python dependencies
    ├── Procfile              # Railway deployment
    └── README.md             # Project documentation
```

## 📚 Dokumentasi (docs/)

### 🚀 deployment/
Semua yang berhubungan dengan deployment ke Railway:
- `RAILWAY_*.md` - Panduan Railway
- `DEPLOYMENT_*.md` - Checklist & status deployment
- `MIGRATION_*.md` - Database migration guides
- `BACKUP_*.md` - Backup procedures

### ⚡ features/
Dokumentasi fitur-fitur bot:
- `AUTOMATON_*.md` - Automaton AI trading system
- `AI_AGENT_*.md` - AI Agent features
- `AUTOSIGNAL_*.md` - Auto signal generation
- `CENTRALIZED_WALLET_*.md` - Wallet system
- `DEPOSIT_*.md` - Deposit system
- `LINEAGE_*.md` - Referral/lineage system
- `SIGNAL_TRACKING_*.md` - Signal tracking
- `BROADCAST_*.md` - Broadcast features
- `ADMIN_*.md` - Admin features

### 📖 guides/
Panduan untuk pengguna:
- `START_HERE_*.md` - Getting started guides
- `CARA_*.md` - How-to guides (Bahasa Indonesia)
- `PANDUAN_*.md` - User manuals
- `QUICK_START_*.md` - Quick start guides
- `README*.md` - Project documentation

### 🗃️ archive/
Dokumentasi lama, fixes, dan historical records:
- `FIX_*.md` - Bug fixes documentation
- `TASK_*.md` - Completed task records
- `*_COMPLETE.md` - Completion summaries

## 🧪 Tests (tests/)

### Unit Tests (tests/unit/)
- Test individual components
- Python: `test_*.py`
- JavaScript: `test-*.js`

### Integration Tests (tests/integration/)
- Test feature interactions
- `test_task_*.py` - Task-based tests
- `comprehensive_test.py` - Full system test

### Property Tests (tests/property/)
- Property-based testing dengan Hypothesis
- `test_property_*.py` - Property tests
- Validation & edge case testing

## 🔧 Scripts (scripts/)

### Migration (scripts/migration/)
Database migrations:
- `run_migration_*.py` - Migration runners
- `migrate_*.py` - Migration utilities
- `create_supabase_*.sql` - Schema creation

### Setup (scripts/setup/)
Setup & verification:
- `check_*.py` - Health checks
- `verify_*.py` - Verification scripts
- `setup_*.py` - Setup utilities
- `generate_*.py` - Key generation

### Maintenance (scripts/maintenance/)
Maintenance & utilities:
- `*_bot.*` - Bot management scripts
- `backup_*.py` - Backup utilities
- `analyze_*.py` - Analysis tools
- `fix_*.py` - Fix scripts

## 🚀 Quick Start

### Menjalankan Bot
```bash
# Windows
start_bot.bat

# Linux/Mac
./start_bot.sh
```

### Running Tests
```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Property tests
pytest tests/property/
```

### Database Migration
```bash
python scripts/migration/run_migration_009.py
```

## 📝 File Penting di Root

- `bot.py` - Main bot application
- `.env` - Environment variables (jangan di-commit!)
- `requirements.txt` - Python dependencies
- `Procfile` - Railway deployment config
- `railway.json` - Railway configuration
- `config.py` - Bot configuration
- `database.py` - Database utilities

## 🔍 Mencari Dokumentasi

### Untuk Deployment:
→ Lihat `docs/deployment/`

### Untuk Fitur Tertentu:
→ Lihat `docs/features/[NAMA_FITUR]*.md`

### Untuk Panduan Pengguna:
→ Lihat `docs/guides/START_HERE_*.md`

### Untuk Troubleshooting:
→ Lihat `docs/archive/FIX_*.md` atau `docs/archive/TROUBLESHOOT_*.md`

## 📊 Statistik

- **Total Files Organized**: 729 files
- **Documentation Files**: ~400 files
- **Test Files**: ~200 files
- **Script Files**: ~100 files
- **Core Application**: app/ folder

## 🎯 Best Practices

1. **Dokumentasi baru** → Taruh di `docs/features/` atau `docs/guides/`
2. **Test baru** → Taruh di `tests/unit/`, `tests/integration/`, atau `tests/property/`
3. **Script utility** → Taruh di `scripts/setup/` atau `scripts/maintenance/`
4. **Migration** → Taruh di `migrations/` (SQL) atau `scripts/migration/` (Python)
5. **Dokumentasi lama** → Pindahkan ke `docs/archive/`

## 🔄 Maintenance

Folder ini diorganisir menggunakan `organize_files.py`. Jika ada file baru yang perlu dirapikan:

```bash
# Dry run (preview)
python organize_files.py

# Execute (actually move files)
python organize_files.py --execute
```

---

**Last Updated**: March 3, 2026
**Organized by**: Kiro AI Assistant
