# 🤖 Bot Management Guide - Terminal Scripts

## 📁 Available Scripts

### Windows (.bat files):
1. ✅ `run_bot.bat` - Start bot
2. ✅ `restart_bot.bat` - Restart bot (stop + start)
3. ✅ `stop_bot.bat` - Stop bot
4. ✅ `status_bot.bat` - Check bot status

### Linux/Mac (.sh files):
1. ✅ `run_bot.sh` - Start bot
2. ✅ `restart_bot.sh` - Restart bot (stop + start)
3. ✅ `stop_bot.sh` - Stop bot
4. ✅ `status_bot.sh` - Check bot status

## 🚀 Quick Start

### Windows:

#### Start Bot:
```cmd
cd Bismillah
run_bot.bat
```

#### Restart Bot:
```cmd
cd Bismillah
restart_bot.bat
```

#### Stop Bot:
```cmd
cd Bismillah
stop_bot.bat
```

#### Check Status:
```cmd
cd Bismillah
status_bot.bat
```

### Linux/Mac:

#### First Time Setup (make scripts executable):
```bash
cd Bismillah
chmod +x *.sh
```

#### Start Bot:
```bash
cd Bismillah
./run_bot.sh
```

#### Restart Bot:
```bash
cd Bismillah
./restart_bot.sh
```

#### Stop Bot:
```bash
cd Bismillah
./stop_bot.sh
```

#### Check Status:
```bash
cd Bismillah
./status_bot.sh
```

## 📊 Script Details

### 1. run_bot.bat / run_bot.sh

**Purpose**: Start the bot

**What it does**:
- ✅ Check if Python is installed
- ✅ Check if main.py exists
- ✅ Check if .env exists (warning if missing)
- ✅ Start bot with `python main.py`
- ✅ Show error if bot crashes

**When to use**:
- First time starting bot
- After stopping bot manually
- When you know bot is not running

**Example Output**:
```
========================================
  CryptoMentor Bot - Starting...
========================================

[INFO] Starting CryptoMentor Bot...
[INFO] Press Ctrl+C to stop

========================================

✅ Bot initialized with 2 admin(s)
✅ Application handlers registered successfully
🔄 Bot restarted - All user command states will be reset
   Users will need to start new commands
✅ Bot started successfully!
📱 Bot is now polling for updates...
```

---

### 2. restart_bot.bat / restart_bot.sh

**Purpose**: Restart the bot (stop existing + start new)

**What it does**:
- ✅ Find all running bot processes
- ✅ Kill existing processes
- ✅ Wait 2 seconds
- ✅ Clear Python cache (__pycache__)
- ✅ Start bot fresh

**When to use**:
- After code changes
- After .env changes
- When bot is stuck
- Regular maintenance restart

**Example Output**:
```
========================================
  CryptoMentor Bot - Restart Script
========================================

[1/4] Mencari proses bot yang sedang berjalan...

Menghentikan proses Python (PID: 12345)...

[2/4] Proses bot dihentikan

[3/4] Membersihkan cache...
Cache dibersihkan

[4/4] Memulai bot...

========================================
  Bot Starting...
  Press Ctrl+C to stop
========================================

✅ Bot started successfully!
```

---

### 3. stop_bot.bat / stop_bot.sh

**Purpose**: Stop the bot

**What it does**:
- ✅ Find all running bot processes
- ✅ Kill processes forcefully
- ✅ Confirm if stopped or not running

**When to use**:
- Before making code changes
- Before server maintenance
- When bot needs to be stopped
- Emergency stop

**Example Output**:
```
========================================
  CryptoMentor Bot - Stop Script
========================================

[INFO] Mencari proses bot yang sedang berjalan...

[INFO] Menghentikan proses bot (PIDs: 12345)...

[SUCCESS] Bot berhasil dihentikan!

========================================
```

---

### 4. status_bot.bat / status_bot.sh

**Purpose**: Check if bot is running

**What it does**:
- ✅ Check if Python is installed
- ✅ Check if bot process is running
- ✅ Check if configuration files exist
- ✅ Show status summary

**When to use**:
- Check if bot is running
- Verify configuration
- Troubleshooting
- Before starting/stopping

**Example Output**:
```
========================================
  CryptoMentor Bot - Status Check
========================================

[INFO] Checking bot status...

[RUNNING] Bot process found (PID: 12345)

[STATUS] Bot is RUNNING ✓

========================================

[CONFIG] .env file: EXISTS ✓
[CONFIG] main.py: EXISTS ✓
[CONFIG] bot.py: EXISTS ✓

========================================
```

## 🔄 Common Workflows

### Development Workflow:

```bash
# 1. Check status
./status_bot.sh

# 2. Make code changes
# ... edit files ...

# 3. Restart bot to apply changes
./restart_bot.sh

# 4. Monitor logs
# Bot will show logs in terminal
```

### Production Workflow:

```bash
# 1. Start bot
./run_bot.sh

# 2. Check if running
./status_bot.sh

# 3. If need to restart
./restart_bot.sh

# 4. If need to stop
./stop_bot.sh
```

### Troubleshooting Workflow:

```bash
# 1. Check status
./status_bot.sh

# 2. If running but not responding
./restart_bot.sh

# 3. If still not working
./stop_bot.sh
# Check logs, fix issues
./run_bot.sh

# 4. Verify working
./status_bot.sh
```

## 🐛 Troubleshooting

### Issue: "Python tidak ditemukan"

**Cause**: Python not installed or not in PATH

**Solution**:
```bash
# Check Python installation
python --version  # Windows
python3 --version # Linux/Mac

# If not installed, install Python
# Windows: Download from python.org
# Linux: sudo apt install python3
# Mac: brew install python3
```

### Issue: "main.py tidak ditemukan"

**Cause**: Not in correct directory

**Solution**:
```bash
# Navigate to Bismillah folder
cd path/to/Bismillah

# Verify you're in correct folder
ls main.py  # Linux/Mac
dir main.py # Windows
```

### Issue: "Bot stopped with error"

**Cause**: Configuration error or missing dependencies

**Solution**:
```bash
# Check .env file exists
cat .env  # Linux/Mac
type .env # Windows

# Install dependencies
pip install -r requirements.txt

# Check logs for specific error
```

### Issue: Script won't run (Linux/Mac)

**Cause**: Script not executable

**Solution**:
```bash
# Make scripts executable
chmod +x *.sh

# Then run
./run_bot.sh
```

### Issue: Multiple bot instances running

**Cause**: Bot started multiple times

**Solution**:
```bash
# Stop all instances
./stop_bot.sh

# Wait a moment
sleep 2

# Start fresh
./run_bot.sh
```

## 💡 Tips & Best Practices

### 1. Always Check Status First
```bash
./status_bot.sh
```
Before starting or restarting, check if bot is already running.

### 2. Use Restart for Code Changes
```bash
./restart_bot.sh
```
Restart automatically stops old instance and starts new one.

### 3. Monitor Logs
When running bot, keep terminal open to see logs:
- User interactions
- Errors
- API calls
- State changes

### 4. Regular Restarts
For production, restart bot regularly (e.g., daily) to:
- Clear memory
- Apply any updates
- Reset states
- Maintain performance

### 5. Background Running (Linux/Mac)
To run bot in background:
```bash
# Start in background
nohup ./run_bot.sh > bot.log 2>&1 &

# Check if running
./status_bot.sh

# View logs
tail -f bot.log

# Stop
./stop_bot.sh
```

### 6. Auto-restart on Crash (Linux/Mac)
Use systemd or supervisor for auto-restart:
```bash
# Example with systemd
sudo nano /etc/systemd/system/cryptomentor.service

# Add service configuration
# Then enable
sudo systemctl enable cryptomentor
sudo systemctl start cryptomentor
```

## 📋 Checklist

### Before Starting Bot:
- [ ] Python installed
- [ ] In Bismillah directory
- [ ] .env file configured
- [ ] Dependencies installed
- [ ] No other instance running

### After Starting Bot:
- [ ] Check status (should show RUNNING)
- [ ] Test in Telegram (/start)
- [ ] Monitor logs for errors
- [ ] Verify all features working

### Before Stopping Bot:
- [ ] Inform users (if production)
- [ ] Check if any critical operations running
- [ ] Note the reason for stopping

### After Stopping Bot:
- [ ] Verify stopped (status check)
- [ ] Make necessary changes
- [ ] Test changes if needed
- [ ] Restart when ready

## 🎯 Quick Reference

| Task | Windows | Linux/Mac |
|------|---------|-----------|
| Start | `run_bot.bat` | `./run_bot.sh` |
| Restart | `restart_bot.bat` | `./restart_bot.sh` |
| Stop | `stop_bot.bat` | `./stop_bot.sh` |
| Status | `status_bot.bat` | `./status_bot.sh` |

## 📞 Support

If scripts don't work:
1. Check Python installation
2. Verify you're in Bismillah folder
3. Check file permissions (Linux/Mac)
4. Review error messages
5. Check bot logs

---

**Created**: 2026-02-15
**Status**: ✅ READY TO USE
**Platform**: Windows, Linux, Mac
