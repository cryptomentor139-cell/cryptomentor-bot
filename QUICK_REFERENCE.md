# ⚡ Quick Reference - CryptoMentor Bot

> Cheat sheet untuk navigasi cepat folder Bismillah yang sudah rapi

---

## 📁 Folder Structure (One-Liner)

```
app/ docs/ tests/ scripts/ migrations/ automaton/ data/ signal_logs/
```

---

## 🎯 Common Tasks

### 🚀 Running the Bot
```bash
# Windows
start_bot.bat

# Linux/Mac
./scripts/maintenance/start_bot.sh
```

### 🧪 Running Tests
```bash
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest tests/property/          # Property tests
pytest                          # All tests
```

### 🗄️ Database Migration
```bash
python scripts/migration/run_migration_009.py
```

### 🔍 Health Checks
```bash
python scripts/setup/check_all_env.py
python scripts/setup/check_automaton_health.py
python scripts/setup/verify_deployment.py
```

---

## 📚 Documentation Quick Links

| Need | Location |
|------|----------|
| Getting Started | `docs/guides/START_HERE_AKSES_BOT.md` |
| Deployment | `docs/deployment/RAILWAY_QUICK_START.md` |
| Automaton | `docs/features/AUTOMATON_QUICK_START.md` |
| Deposit | `docs/guides/CARA_DEPOSIT_USDC.md` |
| Signal Tracking | `docs/features/SIGNAL_TRACKING_SETUP.md` |
| Admin Guide | `docs/features/ADMIN_QUICK_REFERENCE.md` |
| Troubleshooting | `docs/archive/TROUBLESHOOT_*.md` |

---

## 🔍 Finding Files

### By Pattern
```bash
# Deployment docs
docs/deployment/RAILWAY_*.md
docs/deployment/DEPLOYMENT_*.md

# Feature docs
docs/features/AUTOMATON_*.md
docs/features/DEPOSIT_*.md
docs/features/SIGNAL_TRACKING_*.md

# User guides
docs/guides/START_HERE_*.md
docs/guides/CARA_*.md

# Tests
tests/unit/test_*.py
tests/integration/test_*.py
tests/property/test_property_*.py

# Scripts
scripts/migration/run_migration_*.py
scripts/setup/check_*.py
scripts/maintenance/*.py
```

### By Topic
```bash
# Automaton
docs/features/AUTOMATON_*.md
app/automaton_*.py
tests/unit/test_automaton_*.py

# Deposit
docs/features/DEPOSIT_*.md
app/deposit_*.py
tests/unit/test_deposit_*.py

# Signal Tracking
docs/features/SIGNAL_TRACKING_*.md
app/signal_*.py
tests/unit/test_signal_*.py
```

---

## 🛠️ Useful Scripts

### Setup & Verification
```bash
scripts/setup/check_all_env.py              # Check environment
scripts/setup/verify_deployment.py          # Verify deployment
scripts/setup/check_automaton_health.py     # Check Automaton
scripts/setup/generate_encryption_key.py    # Generate key
```

### Migration
```bash
scripts/migration/run_migration_009.py      # Latest migration
scripts/migration/migrate_local_to_supabase.py
```

### Maintenance
```bash
scripts/maintenance/start_bot.sh            # Start bot
scripts/maintenance/stop_bot.sh             # Stop bot
scripts/maintenance/restart_bot.sh          # Restart bot
scripts/maintenance/backup_supabase_users.py
```

---

## 📊 Folder Stats

```
docs/
  ├── deployment/    69 files
  ├── features/     119 files
  ├── guides/        42 files
  └── archive/      214 files

tests/
  ├── unit/         129 files
  ├── integration/   20 files
  └── property/      21 files

scripts/
  ├── migration/     16 files
  ├── setup/         28 files
  └── maintenance/   71 files
```

---

## 🎓 File Naming Conventions

### Documentation
- `START_HERE_*.md` - Getting started guides
- `CARA_*.md` - How-to guides (Indonesian)
- `QUICK_START_*.md` - Quick start guides
- `*_COMPLETE.md` - Completion summaries
- `FIX_*.md` - Bug fix documentation
- `TROUBLESHOOT_*.md` - Troubleshooting guides

### Tests
- `test_*.py` - Python tests
- `test-*.js` - JavaScript tests
- `test_property_*.py` - Property-based tests
- `test_task_*.py` - Task-based integration tests

### Scripts
- `run_migration_*.py` - Migration runners
- `check_*.py` - Health checks
- `verify_*.py` - Verification scripts
- `setup_*.py` - Setup scripts
- `*_bot.*` - Bot management scripts

---

## 🔗 Important Files

### Root
```
bot.py                  # Main bot
.env                    # Environment (don't commit!)
requirements.txt        # Dependencies
Procfile                # Railway config
INDEX.md                # Navigation index
FOLDER_STRUCTURE.md     # Folder structure
UNFINISHED_SPECS.md     # Unfinished specs
```

### App
```
app/bot.py              # Bot logic
app/handlers_*.py       # Feature handlers
app/dual_mode/          # Dual mode system
app/providers/          # Data providers
```

### Migrations
```
migrations/009_dual_mode_offline_online.sql
scripts/migration/run_migration_009.py
```

---

## 🚨 Emergency Commands

### Bot Not Responding
```bash
# Check status
python scripts/setup/verify_bot_running.py

# Restart
./scripts/maintenance/restart_bot.sh

# Check logs
# (Railway dashboard)
```

### Database Issues
```bash
# Check connection
python scripts/setup/check_supabase_status.py

# Run migration
python scripts/migration/run_migration_009.py
```

### Automaton Issues
```bash
# Check health
python scripts/setup/check_automaton_health.py

# Check connection
python scripts/setup/check_connection_status.py
```

---

## 📝 Specs Status

| Spec | Status | Location |
|------|--------|----------|
| cryptomentor-telegram-bot | ✅ | `.kiro/specs/cryptomentor-telegram-bot/` |
| manual-signal-generation-fix | ⚠️ | `.kiro/specs/manual-signal-generation-fix/` |
| dual-mode-offline-online | ⚠️ | `.kiro/specs/dual-mode-offline-online/` |
| ai-agent-deposit-flow | ⚠️ | `.kiro/specs/ai-agent-deposit-flow/` |
| automaton-integration | ⚠️ | `.kiro/specs/automaton-integration/` |

See [UNFINISHED_SPECS.md](UNFINISHED_SPECS.md) for details.

---

## 🎯 Next Steps

### New User?
1. Read `INDEX.md`
2. Follow `docs/guides/START_HERE_AKSES_BOT.md`
3. Setup with `docs/guides/CARA_MENJALANKAN_BOT.md`

### Want to Deploy?
1. Check `docs/deployment/DEPLOYMENT_CHECKLIST.md`
2. Follow `docs/deployment/RAILWAY_QUICK_START.md`
3. Verify with `scripts/setup/verify_deployment.py`

### Want to Develop?
1. Read `FOLDER_STRUCTURE.md`
2. Explore `app/` folder
3. Run tests in `tests/`
4. Use scripts in `scripts/`

### Want to Continue Specs?
1. Read `UNFINISHED_SPECS.md`
2. Open spec in `.kiro/specs/[spec-name]/`
3. Check `tasks.md` for remaining tasks
4. Implement and test

---

## 💡 Tips

- Use `INDEX.md` as your main navigation hub
- Check `FOLDER_STRUCTURE.md` for detailed structure
- Read `CLEANUP_REPORT.md` for organization details
- Use `organize_files.py` to reorganize new files
- Keep root folder clean - move files to appropriate folders

---

**Quick Access**: [INDEX.md](INDEX.md) | [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) | [UNFINISHED_SPECS.md](UNFINISHED_SPECS.md) | [CLEANUP_REPORT.md](CLEANUP_REPORT.md)
