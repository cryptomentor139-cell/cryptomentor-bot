# 🔧 Automaton AI - Troubleshooting Guide

## 🚨 Common Issues & Solutions

### Issue 1: "Automaton AI Offline"

**Error Message:**
```
❌ Automaton AI Offline

Automaton AI sedang tidak tersedia.
Pastikan Automaton dashboard running:
`cd C:\Users\dragon\automaton`
`node dist/index.js --run`
```

**Possible Causes:**
1. Automaton dashboard not running
2. Dashboard crashed
3. Wrong path configuration

**Solutions:**

#### Solution 1A: Start Automaton Dashboard
```bash
# Open new terminal
cd C:\Users\dragon\automaton
node dist/index.js --run
```

Keep this terminal open!

#### Solution 1B: Check if Already Running
```bash
# Windows
tasklist | findstr node

# Should see: node.exe
```

If running but still offline, restart:
```bash
# Kill node processes
taskkill /F /IM node.exe

# Start again
cd C:\Users\dragon\automaton
node dist/index.js --run
```

#### Solution 1C: Check Path Configuration
Edit `app/automaton_ai_integration.py`:
```python
# Line ~15
def __init__(self, automaton_dir="C:/Users/dragon/automaton"):
```

Verify path is correct for your system.

---

### Issue 2: "send-task.js not found"

**Error Message:**
```
❌ Failed to initialize AI client: 
send-task.js not found at C:/Users/dragon/automaton/send-task.js
```

**Possible Causes:**
1. File doesn't exist
2. Wrong path
3. File permissions

**Solutions:**

#### Solution 2A: Verify File Exists
```bash
dir C:\Users\dragon\automaton\send-task.js
```

If not found, check Automaton installation.

#### Solution 2B: Check File Permissions
```bash
# Right-click send-task.js
# Properties → Security
# Ensure you have Read & Execute permissions
```

#### Solution 2C: Update Path
If file is in different location, update:
```python
# app/automaton_ai_integration.py
self.send_task_script = self.automaton_dir / "send-task.js"
```

---

### Issue 3: Timeout / No Response

**Error Message:**
```
❌ Error

Gagal mendapatkan AI signal: No response from Automaton AI

Pastikan Automaton dashboard running.
```

**Possible Causes:**
1. AI processing taking too long
2. Database connection issue
3. Task not being processed
4. Database locked

**Solutions:**

#### Solution 3A: Increase Timeout
Edit `app/handlers_automaton_ai.py`:
```python
# Line ~90
result = ai_client.get_ai_signal(symbol, timeframe, timeout=120)  # Increase to 120s
```

#### Solution 3B: Check Database
```python
# Test database connection
import sqlite3
conn = sqlite3.connect("C:/root/.automaton/state.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM turns")
print(cursor.fetchone())
conn.close()
```

#### Solution 3C: Check Automaton Logs
Look at Automaton dashboard terminal for errors:
- Task received?
- Processing started?
- Any error messages?

#### Solution 3D: Restart Everything
```bash
# 1. Stop bot (Ctrl+C)
# 2. Stop Automaton (Ctrl+C)
# 3. Start Automaton
cd C:\Users\dragon\automaton
node dist/index.js --run

# 4. Wait 10 seconds
# 5. Start bot
cd C:\V3-Final-Version\Bismillah
python bot.py
```

---

### Issue 4: Import Errors

**Error Message:**
```
ModuleNotFoundError: No module named 'app.automaton_ai_integration'
```

**Possible Causes:**
1. Files not in correct location
2. Python path issue
3. Typo in import

**Solutions:**

#### Solution 4A: Verify Files Exist
```bash
dir Bismillah\app\automaton_ai_integration.py
dir Bismillah\app\handlers_automaton_ai.py
```

Both should exist.

#### Solution 4B: Check Python Path
```python
import sys
print(sys.path)
```

Should include bot directory.

#### Solution 4C: Restart Bot
```bash
# Stop bot (Ctrl+C)
# Start again
python bot.py
```

---

### Issue 5: Rate Limit Not Working

**Symptoms:**
- Can send > 10 requests/hour
- No rate limit error shown

**Possible Causes:**
1. Rate limiter not initialized
2. Bot restarted (in-memory reset)
3. Code not updated

**Solutions:**

#### Solution 5A: Verify Rate Limiter Updated
Check `app/rate_limiter.py` contains:
```python
'ai_signal': {
    'max_requests': 10,
    'window_seconds': 3600,
    'description': 'AI signal requests'
}
```

#### Solution 5B: Check Handler Calls Rate Limiter
In `app/handlers_automaton_ai.py`:
```python
# Should have this check
allowed, error_msg = rate_limiter.check_ai_signal_limit(user_id)
if not allowed:
    await update.message.reply_text(error_msg, ...)
    return
```

#### Solution 5C: Restart Bot
Rate limits are in-memory, restart resets them:
```bash
# Stop and start bot
python bot.py
```

---

### Issue 6: Premium/Access Check Not Working

**Symptoms:**
- Non-premium users can access
- Users without Automaton access can use

**Possible Causes:**
1. Database issue
2. Check logic bypassed
3. Test mode enabled

**Solutions:**

#### Solution 6A: Verify Database
```python
# Test premium check
from database import Database
db = Database()
print(db.is_user_premium(USER_ID))
print(db.has_automaton_access(USER_ID))
```

#### Solution 6B: Check Handler Logic
In `app/handlers_automaton_ai.py`:
```python
# Should have these checks
if not db.is_user_premium(user_id):
    # Return error
    
if not db.has_automaton_access(user_id):
    # Return error
```

#### Solution 6C: Grant Access for Testing
```python
# Grant premium
/set_premium USER_ID 30

# Grant Automaton access (run script)
python grant_automaton_access.py USER_ID
```

---

### Issue 7: Response Parsing Errors

**Symptoms:**
- Signal shows "N/A" for all fields
- Confidence is 0%
- Analysis is truncated

**Possible Causes:**
1. AI response not in JSON format
2. JSON parsing failed
3. Response structure different

**Solutions:**

#### Solution 7A: Check Raw Response
Add debug logging in `app/automaton_ai_integration.py`:
```python
# After getting response
print(f"RAW RESPONSE: {response_text}")
```

#### Solution 7B: Improve JSON Extraction
Update `_parse_ai_response()` method:
```python
def _parse_ai_response(self, response_text: str, symbol: str):
    # Try multiple JSON extraction methods
    # 1. Look for ```json blocks
    # 2. Look for { } blocks
    # 3. Use regex
    # 4. Fallback to raw text
```

#### Solution 7C: Update AI Prompt
Make prompt more explicit:
```python
task_content = f"""Analyze {symbol} on {timeframe} timeframe.

IMPORTANT: Respond ONLY with valid JSON in this exact format:
{{
  "trend": "bullish|bearish|neutral",
  "entry_price": "number",
  "stop_loss": "number",
  "take_profit": ["tp1", "tp2", "tp3"],
  "risk_reward": "ratio",
  "confidence": number,
  "analysis": "text"
}}

No additional text before or after JSON."""
```

---

### Issue 8: Bot Crashes on AI Request

**Symptoms:**
- Bot stops responding
- Terminal shows error
- Need to restart bot

**Possible Causes:**
1. Unhandled exception
2. Memory issue
3. Subprocess error

**Solutions:**

#### Solution 8A: Add More Error Handling
Wrap everything in try-except:
```python
async def ai_signal_command(update, context):
    try:
        # All code here
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            "❌ Terjadi kesalahan. Silakan coba lagi."
        )
```

#### Solution 8B: Check Memory Usage
```bash
# Windows Task Manager
# Check Python memory usage
# If > 500MB, might be memory leak
```

#### Solution 8C: Add Subprocess Timeout
In `_send_task()`:
```python
result = subprocess.run(
    ['node', 'send-task.js', task_content],
    cwd=str(self.automaton_dir),
    capture_output=True,
    text=True,
    timeout=15  # Increase if needed
)
```

---

### Issue 9: Slow Response Time

**Symptoms:**
- Takes > 90 seconds
- Users complaining about wait time

**Possible Causes:**
1. AI processing slow
2. Database polling inefficient
3. Network latency

**Solutions:**

#### Solution 9A: Optimize Polling Interval
In `_wait_for_response()`:
```python
# Change from 3s to 2s
time.sleep(2)  # Check every 2 seconds
```

#### Solution 9B: Add Progress Updates
```python
# In handler, update message every 15s
for i in range(6):  # 90s / 15s
    await asyncio.sleep(15)
    await processing_msg.edit_text(
        f"⏳ Still processing... ({(i+1)*15}s)"
    )
```

#### Solution 9C: Optimize AI Prompt
Make prompt shorter and more specific:
```python
task_content = f"Quick analysis for {symbol} {timeframe}: trend, entry, SL, 3 TPs, R:R, confidence. JSON only."
```

---

### Issue 10: Database Locked

**Error Message:**
```
sqlite3.OperationalError: database is locked
```

**Possible Causes:**
1. Multiple processes accessing DB
2. Long-running transaction
3. Database corruption

**Solutions:**

#### Solution 10A: Add Retry Logic
```python
def _wait_for_response(self, task_id, timeout):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            # ... rest of code
        except sqlite3.OperationalError as e:
            if "locked" in str(e) and attempt < max_retries - 1:
                time.sleep(1)
                continue
            raise
```

#### Solution 10B: Use WAL Mode
```python
conn = sqlite3.connect(self.db_path)
conn.execute("PRAGMA journal_mode=WAL")
```

#### Solution 10C: Close Connections Properly
Always use context manager:
```python
with sqlite3.connect(self.db_path) as conn:
    cursor = conn.cursor()
    # ... queries
# Auto-closes
```

---

## 🧪 Debugging Tools

### 1. Test Script
```bash
cd Bismillah
python test_automaton_ai.py
```

### 2. Manual Database Check
```python
import sqlite3
conn = sqlite3.connect("C:/root/.automaton/state.db")
cursor = conn.cursor()

# Check inbox
cursor.execute("SELECT * FROM inbox_messages ORDER BY received_at DESC LIMIT 5")
print(cursor.fetchall())

# Check turns
cursor.execute("SELECT * FROM turns ORDER BY timestamp DESC LIMIT 5")
print(cursor.fetchall())

conn.close()
```

### 3. Enable Debug Logging
Add to bot.py:
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 4. Check Automaton Status
```python
from app.automaton_ai_integration import get_automaton_ai_client

client = get_automaton_ai_client()
status = client.get_status()
print(status)
```

---

## 📊 Monitoring Checklist

Daily checks:
- [ ] Automaton dashboard running
- [ ] Bot responding to commands
- [ ] AI signals working
- [ ] Rate limits enforced
- [ ] No error spikes in logs
- [ ] Response time < 60s average

Weekly checks:
- [ ] Review error logs
- [ ] Check database size
- [ ] Verify premium checks working
- [ ] Test with multiple users
- [ ] Update documentation if needed

---

## 🆘 Emergency Procedures

### If Bot Completely Down

1. **Stop everything:**
   ```bash
   # Ctrl+C on both terminals
   ```

2. **Check logs:**
   ```bash
   # Look for last error message
   ```

3. **Restart Automaton:**
   ```bash
   cd C:\Users\dragon\automaton
   node dist/index.js --run
   ```

4. **Wait 30 seconds**

5. **Restart Bot:**
   ```bash
   cd C:\V3-Final-Version\Bismillah
   python bot.py
   ```

6. **Test:**
   ```
   /ai_status
   ```

### If Database Corrupted

1. **Backup database:**
   ```bash
   copy C:\root\.automaton\state.db C:\root\.automaton\state.db.backup
   ```

2. **Try to repair:**
   ```python
   import sqlite3
   conn = sqlite3.connect("C:/root/.automaton/state.db")
   conn.execute("PRAGMA integrity_check")
   ```

3. **If repair fails, restore from backup**

### If Users Reporting Issues

1. **Verify issue:**
   - Test yourself
   - Check logs
   - Ask for screenshot

2. **Quick fix:**
   - Restart services
   - Clear rate limits
   - Grant temporary access

3. **Permanent fix:**
   - Identify root cause
   - Update code
   - Deploy fix
   - Test thoroughly

---

## 📞 Getting Help

### Self-Help Resources
1. Read this troubleshooting guide
2. Check `AUTOMATON_AI_INTEGRATION_GUIDE.md`
3. Review `CARA_PAKAI_AUTOMATON_AI.md`
4. Run test suite

### Contact Support
If issue persists:
1. Collect error messages
2. Note steps to reproduce
3. Check if others have same issue
4. Contact admin with details

### Report Bug
Include:
- Error message (full text)
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Bot version
- Automaton version

---

**Last Updated:** 2026-02-22
**Version:** 1.0.0
