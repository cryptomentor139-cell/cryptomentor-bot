# 🤖 CryptoMentor Bot - Telegram Trading Bot

> **⚠️ FOLDER BARU SAJA DIRAPIKAN!** Lihat [CLEANUP_REPORT.md](CLEANUP_REPORT.md) untuk detail.

Telegram bot untuk crypto trading signals dengan AI-powered analysis, autonomous trading, dan signal tracking.

---

## 🎯 Quick Start

### 📚 Navigation
- **[INDEX.md](INDEX.md)** - 🗺️ Main navigation hub
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - ⚡ Quick reference cheat sheet
- **[FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md)** - 📁 Detailed folder structure
- **[UNFINISHED_SPECS.md](UNFINISHED_SPECS.md)** - 📋 Unfinished specs to complete

### 🚀 Getting Started
1. Read [START_HERE_AKSES_BOT.md](docs/guides/START_HERE_AKSES_BOT.md)
2. Setup environment: [CARA_MENJALANKAN_BOT.md](docs/guides/CARA_MENJALANKAN_BOT.md)
3. Deploy to Railway: [RAILWAY_QUICK_START.md](docs/deployment/RAILWAY_QUICK_START.md)

---

## ✨ Features

### 🤖 Automaton AI Trading
- Autonomous trading with AI
- Conway API integration
- Real-time market analysis
- [Documentation](docs/features/AUTOMATON_COMPLETE_INDEX.md)

### 📊 Signal Generation
- Manual signal generation
- Auto signal generation
- SMC (Smart Money Concepts) analysis
- Multi-coin support
- [Documentation](docs/features/AUTOSIGNAL_ANALYSIS.md)

### 💰 Wallet & Deposit System
- Centralized wallet management
- USDC deposits on Base network
- Automated credit system
- [Documentation](docs/features/CENTRALIZED_WALLET_ARCHITECTURE.md)

### 📈 Signal Tracking
- Real-time signal tracking
- Performance analytics
- Weekly reports
- [Documentation](docs/features/SIGNAL_TRACKING_INDEX.md)

### 👥 User Management
- Referral/lineage system
- Premium subscriptions
- Credit management
- Admin controls

---

## 📁 Project Structure

```
Bismillah/
├── 📱 app/              # Application code
├── 📚 docs/             # Documentation (444 files)
│   ├── deployment/     # Deployment guides
│   ├── features/       # Feature documentation
│   ├── guides/         # User guides
│   └── archive/        # Old docs & fixes
├── 🧪 tests/            # Testing suite (170 files)
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── property/       # Property-based tests
├── 🔧 scripts/          # Utility scripts (115 files)
│   ├── migration/      # Database migrations
│   ├── setup/          # Setup & verification
│   └── maintenance/    # Maintenance utilities
├── 🗄️ migrations/       # SQL migrations
└── 🤖 automaton/        # Automaton AI system
```

See [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) for details.

---

## 🚀 Running the Bot

### Local Development
```bash
# Windows
start_bot.bat

# Linux/Mac
./scripts/maintenance/start_bot.sh
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Required: TELEGRAM_BOT_TOKEN, SUPABASE_URL, SUPABASE_KEY
```

### Database Migration
```bash
python scripts/migration/run_migration_009.py
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/property/

# Run specific test file
pytest tests/unit/test_automaton_manager.py
```

---

## 🚀 Deployment

### Railway Deployment
1. Check [DEPLOYMENT_CHECKLIST.md](docs/deployment/DEPLOYMENT_CHECKLIST.md)
2. Follow [RAILWAY_DEPLOYMENT_GUIDE.md](docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md)
3. Verify with [VERIFY_DEPLOYMENT.md](docs/deployment/VERIFY_DEPLOYMENT.md)

### Environment Variables
Required environment variables:
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase API key
- `CONWAY_API_KEY` - Conway API key (for Automaton)
- `ENCRYPTION_KEY` - Encryption key for wallet

See `.env.example` for complete list.

---

## 📚 Documentation

### For Users
- [Getting Started](docs/guides/START_HERE_AKSES_BOT.md)
- [How to Use Bot](docs/guides/CARA_MENJALANKAN_BOT.md)
- [Deposit Guide](docs/guides/CARA_DEPOSIT_USDC.md)
- [Automaton Guide](docs/guides/CARA_PAKAI_AUTOMATON_AI.md)

### For Developers
- [Folder Structure](FOLDER_STRUCTURE.md)
- [Quick Reference](QUICK_REFERENCE.md)
- [Unfinished Specs](UNFINISHED_SPECS.md)
- [API Documentation](docs/features/)

### For Deployment
- [Railway Quick Start](docs/deployment/RAILWAY_QUICK_START.md)
- [Deployment Checklist](docs/deployment/DEPLOYMENT_CHECKLIST.md)
- [Migration Guide](docs/deployment/MIGRATION_QUICK_START.md)

---

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Framework**: python-telegram-bot
- **Database**: Supabase (PostgreSQL)
- **AI**: DeepSeek, Cerebras, OpenAI
- **Blockchain**: Base Network (USDC)
- **Trading**: Conway API
- **Deployment**: Railway
- **Testing**: pytest, hypothesis

---

## 📊 Statistics

- **Total Files**: 729 files organized
- **Documentation**: 444 files
- **Tests**: 170 files
- **Scripts**: 115 files
- **Lines of Code**: ~50,000+ lines

See [CLEANUP_REPORT.md](CLEANUP_REPORT.md) for details.

---

## 🔧 Maintenance

### Health Checks
```bash
python scripts/setup/check_all_env.py
python scripts/setup/check_automaton_health.py
python scripts/setup/verify_deployment.py
```

### Backup
```bash
python scripts/maintenance/backup_supabase_users.py
```

### File Organization
```bash
# Preview organization
python organize_files.py

# Execute organization
python organize_files.py --execute
```

---

## 📋 Unfinished Specs

Ada beberapa specs yang belum selesai:
1. **manual-signal-generation-fix** - Bug fix untuk manual signals
2. **dual-mode-offline-online** - Dual mode implementation
3. **ai-agent-deposit-flow** - AI agent deposit flow
4. **automaton-integration** - Automaton integration

See [UNFINISHED_SPECS.md](UNFINISHED_SPECS.md) for details.

---

## 🤝 Contributing

1. Read [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) untuk struktur
2. Check [UNFINISHED_SPECS.md](UNFINISHED_SPECS.md) untuk tasks
3. Write tests untuk new features
4. Update documentation
5. Run tests before commit

---

## 📝 License

Proprietary - All rights reserved

---

## 📞 Support

- Documentation: [INDEX.md](INDEX.md)
- Quick Reference: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- Troubleshooting: [docs/archive/TROUBLESHOOT_*.md](docs/archive/)

---

**Last Updated**: March 3, 2026  
**Status**: ✅ Folder Organized & Ready  
**Version**: 3.0
