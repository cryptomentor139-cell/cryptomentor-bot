# 📚 Signal Tracking System - Documentation Index

## 🎯 Start Here

### Untuk Pemula
1. **[QUICK_START_TRACKING.md](QUICK_START_TRACKING.md)** ⚡
   - Setup 10 menit
   - 3 langkah sederhana
   - Langsung jalan

### Untuk Yang Ingin Detail
2. **[SIGNAL_TRACKING_README.md](SIGNAL_TRACKING_README.md)** 📖
   - Overview lengkap
   - Semua fitur
   - Benefits & use cases

## 📋 Documentation Files

### Setup & Installation
| File | Deskripsi | Waktu Baca |
|------|-----------|------------|
| [QUICK_START_TRACKING.md](QUICK_START_TRACKING.md) | Quick start guide | 5 min |
| [SIGNAL_TRACKING_SETUP.md](SIGNAL_TRACKING_SETUP.md) | Setup lengkap Google Drive | 15 min |
| [setup_signal_tracking.py](setup_signal_tracking.py) | Setup script | - |

### Implementation
| File | Deskripsi | Waktu Baca |
|------|-----------|------------|
| [TRACKING_INTEGRATION_EXAMPLE.md](TRACKING_INTEGRATION_EXAMPLE.md) | Contoh integrasi code | 10 min |
| [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) | Checklist lengkap | 5 min |
| [integrate_signal_tracking.py](integrate_signal_tracking.py) | Integration helper | - |

### Understanding System
| File | Deskripsi | Waktu Baca |
|------|-----------|------------|
| [SIGNAL_TRACKING_SUMMARY.md](SIGNAL_TRACKING_SUMMARY.md) | Ringkasan sistem | 10 min |
| [TRACKING_FLOW_DIAGRAM.md](TRACKING_FLOW_DIAGRAM.md) | Visual flow diagram | 10 min |

### Configuration
| File | Deskripsi | Waktu Baca |
|------|-----------|------------|
| [.env.tracking.example](.env.tracking.example) | Environment variables | 5 min |

## 🗂️ Core System Files

### Main Components
```
app/
├── signal_logger.py              # Core logging system
├── gdrive_uploader.py            # Google Drive integration
├── weekly_report.py              # Report generator
├── scheduler.py                  # Auto tasks scheduler
├── signal_tracker_integration.py # Helper functions
└── handlers_signal_tracking.py   # Admin commands
```

### Data Files
```
signal_logs/
├── prompts_YYYY-MM-DD.jsonl      # Daily user prompts
├── active_signals.jsonl           # Active signals
└── completed_signals.jsonl        # Closed signals (WIN/LOSS)
```

## 🎓 Learning Path

### Level 1: Beginner (30 minutes)
1. Read [QUICK_START_TRACKING.md](QUICK_START_TRACKING.md)
2. Run `python setup_signal_tracking.py`
3. Test admin commands: `/winrate`, `/signal_stats`

### Level 2: Intermediate (1 hour)
1. Read [SIGNAL_TRACKING_README.md](SIGNAL_TRACKING_README.md)
2. Read [TRACKING_INTEGRATION_EXAMPLE.md](TRACKING_INTEGRATION_EXAMPLE.md)
3. Integrate tracking ke 1-2 commands
4. Test tracking working

### Level 3: Advanced (2 hours)
1. Read [SIGNAL_TRACKING_SETUP.md](SIGNAL_TRACKING_SETUP.md)
2. Setup Google Drive API
3. Read [TRACKING_FLOW_DIAGRAM.md](TRACKING_FLOW_DIAGRAM.md)
4. Integrate tracking ke semua commands
5. Setup scheduler
6. Complete [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)

## 🔍 Quick Reference

### Setup Commands
```bash
# Install dependencies
pip install PyDrive2

# Run setup
python setup_signal_tracking.py

# Test integration
python integrate_signal_tracking.py
```

### Admin Commands
```bash
/winrate              # Winrate 7 hari
/winrate 30           # Winrate 30 hari
/weekly_report        # Generate laporan
/upload_logs          # Upload manual
/signal_stats         # Statistik
```

### Integration Code
```python
# Track command
from app.signal_tracker_integration import track_user_command
track_user_command(user.id, user.username, "/analyze", "BTC", "1h")

# Track signal
from app.signal_tracker_integration import track_signal_given
signal_id = track_signal_given(user.id, "BTCUSDT", "1h", 50000, 51000, 52000, 49500)

# Update result
from app.signal_tracker_integration import update_signal_outcome
update_signal_outcome(signal_id, hit_tp=True, pnl_percent=2.5)
```

## 📊 Use Cases

### 1. Dokumentasi Signal
**File**: [SIGNAL_TRACKING_README.md](SIGNAL_TRACKING_README.md) → Section "Logging System"
- Semua prompt user tersimpan
- Bisa review history
- Analisis pattern user

### 2. Tracking Winrate
**File**: [TRACKING_FLOW_DIAGRAM.md](TRACKING_FLOW_DIAGRAM.md) → Section "Winrate Calculation"
- Hitung winrate otomatis
- Track WIN/LOSS
- Avg PnL calculation

### 3. Backup ke Google Drive
**File**: [SIGNAL_TRACKING_SETUP.md](SIGNAL_TRACKING_SETUP.md) → Section "Setup Google Drive API"
- Auto upload daily
- Safe backup
- Easy access

### 4. Laporan Mingguan
**File**: [SIGNAL_TRACKING_README.md](SIGNAL_TRACKING_README.md) → Section "Laporan Mingguan Format"
- Auto send ke admin
- Analisis performa
- Rekomendasi improvement

## 🎯 Common Tasks

### Task: Setup dari awal
1. [QUICK_START_TRACKING.md](QUICK_START_TRACKING.md)
2. [SIGNAL_TRACKING_SETUP.md](SIGNAL_TRACKING_SETUP.md)
3. [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)

### Task: Integrate ke bot
1. [TRACKING_INTEGRATION_EXAMPLE.md](TRACKING_INTEGRATION_EXAMPLE.md)
2. [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) → Section "Integration Phase"

### Task: Troubleshooting
1. [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) → Section "Troubleshooting"
2. [SIGNAL_TRACKING_SETUP.md](SIGNAL_TRACKING_SETUP.md) → Section "Troubleshooting"

### Task: Understand system
1. [SIGNAL_TRACKING_SUMMARY.md](SIGNAL_TRACKING_SUMMARY.md)
2. [TRACKING_FLOW_DIAGRAM.md](TRACKING_FLOW_DIAGRAM.md)

## 📞 Support

### Issues & Questions
1. Check [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) → Troubleshooting
2. Review [TRACKING_FLOW_DIAGRAM.md](TRACKING_FLOW_DIAGRAM.md)
3. Re-read [SIGNAL_TRACKING_SETUP.md](SIGNAL_TRACKING_SETUP.md)

### Common Problems
- **Google Drive not working**: [SIGNAL_TRACKING_SETUP.md](SIGNAL_TRACKING_SETUP.md) → Section "Troubleshooting"
- **Tracking not saving**: [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) → "If tracking not working"
- **Scheduler not running**: [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) → "If scheduler not running"
- **Winrate incorrect**: [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) → "If winrate incorrect"

## 🎓 Best Practices

1. **Start Simple**
   - Setup basic tracking first
   - Test dengan 1-2 commands
   - Expand gradually

2. **Test Thoroughly**
   - Follow [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)
   - Verify each step
   - Check logs regularly

3. **Monitor Regularly**
   - Use `/signal_stats` daily
   - Check Google Drive weekly
   - Review reports monthly

4. **Backup Important**
   - Keep `signal_logs/` backed up
   - Save Google Drive credentials
   - Document custom changes

## 📈 Next Steps

After implementation:
1. Monitor first week
2. Review first weekly report
3. Analyze winrate trends
4. Optimize signal parameters
5. Scale to more commands

## 🎉 Success Checklist

- [ ] Read documentation
- [ ] Setup completed
- [ ] Integration done
- [ ] Testing passed
- [ ] First upload successful
- [ ] First report received
- [ ] System running stable

---

**Total Documentation**: 11 files
**Total Setup Time**: ~2 hours
**Maintenance**: Minimal (automated)

**Version**: 1.0.0
**Last Updated**: 2026-02-16
