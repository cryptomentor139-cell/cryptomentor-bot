# OpenClaw Quick Reference

## ⚡ Quick Commands

### Test Integration
```bash
cd Bismillah
python quick_test_openclaw.py
```

### Start Bot
```bash
cd Bismillah
python bot.py
```

### Test in Telegram
```
/openclaw_status  → Check availability
/openclaw_help    → Show features
/openclaw_ask     → Ask AI (needs gateway)
/openclaw_test    → Admin test
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `app/openclaw_cli_bridge.py` | Python wrapper for CLI |
| `app/handlers_openclaw_simple.py` | Telegram handlers |
| `quick_test_openclaw.py` | Quick test script |
| `test_bot_openclaw.py` | Full integration test |
| `OPENCLAW_INTEGRATION_COMPLETE.md` | Full documentation |

## 🔧 CLI Commands

```bash
# Version
openclaw --version

# Help
openclaw --help

# Status
openclaw status

# Gateway (optional)
openclaw gateway

# Doctor check
openclaw doctor
```

## 🐍 Python Usage

```python
from app.openclaw_cli_bridge import get_openclaw_cli_bridge

bridge = get_openclaw_cli_bridge()

# Health check
bridge.check_health()  # True/False

# Version
bridge.get_version()  # "2026.3.2"

# Status
bridge.get_status()  # Dict
```

## ✅ Status

- **CLI:** ✅ Installed (2026.3.2)
- **Bridge:** ✅ Working
- **Handlers:** ✅ Registered
- **Bot:** ✅ Integrated
- **Tests:** ✅ Passed

## 🚀 Ready to Use!

Bot sudah siap dengan OpenClaw integration. Test dengan `/openclaw_status` di Telegram!
