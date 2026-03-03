# 🧪 Test OpenClaw Gateway - Step by Step

## 📋 Prerequisites

1. ✅ OpenClaw installed (version 2026.3.1)
2. ✅ OpenClaw config in D:/OpenClaw
3. ✅ Python environment ready
4. ✅ Gateway bridge module created

## 🚀 Step 1: Start OpenClaw Gateway

### Option A: Using Batch File (Easiest)
```bash
# Double-click or run:
start_openclaw_gateway.bat
```

### Option B: Manual Command
```bash
cd D:/OpenClaw
openclaw gateway
```

### What to Expect:
```
OpenClaw Gateway v2026.3.1
Loading configuration from /root/.openclaw/openclaw.json
Initializing agents...
Gateway listening on port 18789
✓ Ready to accept connections
```

**IMPORTANT**: Keep this terminal open! Gateway must stay running.

## 🧪 Step 2: Quick Health Check

Open NEW terminal and run:

```bash
cd Bismillah
python quick_test_gateway.py
```

### Expected Output:
```
🧪 Testing OpenClaw Gateway...
   URL: http://localhost:18789
   ✅ Gateway is RUNNING!
   Status: 200
   Response: OK

✅ Gateway is ready!
```

### If Gateway Not Running:
```
❌ Gateway is NOT running

📋 To start gateway:
   1. Open new terminal
   2. Run: start_openclaw_gateway.bat
   3. Wait for 'Gateway listening on port 18789'
   4. Run this test again
```

## 🧪 Step 3: Full Test Suite

Once health check passes, run full test:

```bash
python test_openclaw_gateway.py
```

### Test 1: Gateway Connection
Tests basic connectivity and gateway info.

**Expected:**
```
1️⃣ Initializing gateway bridge...
   Gateway URL: http://localhost:18789
   Auth Token: deb2a3ab8a9bc891a1a4...

2️⃣ Testing gateway health...
   ✅ Gateway is healthy!

3️⃣ Getting gateway information...
   ✅ Gateway info retrieved:
      • version: 2026.3.1
      • uptime: 120s
      • agents: 0

4️⃣ Listing existing agents...
   ✅ Found 0 agents

✅ Gateway connection test PASSED!
```

### Test 2: Agent Spawn
Tests spawning autonomous agent.

**Expected:**
```
1️⃣ Spawning test agent...
   Task: 'Say hello and tell me the current time'
   ✅ Agent spawned successfully!
   Agent ID: agent_abc123xyz

2️⃣ Waiting for agent to process task...

3️⃣ Checking agent status...
   ✅ Agent status:
      • Status: active
      • Progress: processing

4️⃣ Getting agent logs...
   ✅ Retrieved 5 log entries:
      • 2026-03-03T10:30:00Z: Agent initialized
      • 2026-03-03T10:30:01Z: Processing task...
      • 2026-03-03T10:30:02Z: Calling GPT-4.1...
      • 2026-03-03T10:30:04Z: Response received
      • 2026-03-03T10:30:05Z: Task completed

✅ Agent spawn test PASSED!
```

### Test 3: Agent Chat
Tests chatting with agent.

**Expected:**
```
1️⃣ Spawning chat agent...
   ✅ Agent spawned: agent_xyz789abc

2️⃣ Sending message to agent...
   Message: 'What is 2+2?'
   ✅ Agent response:
      2+2 equals 4.

3️⃣ Sending follow-up message...
   Message: 'What about 5*5?'
   ✅ Agent response:
      5*5 equals 25.

4️⃣ Stopping agent...
   ✅ Agent stopped

✅ Chat test PASSED!
```

### Final Summary:
```
📊 TEST SUMMARY
============================================================
✅ PASS - Gateway Connection
✅ PASS - Agent Spawn
✅ PASS - Agent Chat

Results: 3/3 tests passed

✅ ALL TESTS PASSED!

🎉 OpenClaw Gateway is working perfectly!

Next steps:
1. Integrate gateway commands into bot
2. Test with Telegram bot
3. Deploy to Railway
```

## 🔧 Troubleshooting

### Issue 1: Connection Refused
```
❌ Gateway is NOT running (connection refused)
```

**Solution:**
1. Start gateway: `start_openclaw_gateway.bat`
2. Wait for "Gateway listening on port 18789"
3. Run test again

### Issue 2: Auth Failed
```
❌ Failed to spawn agent: Unauthorized
```

**Solution:**
1. Check auth token in `D:/OpenClaw/openclaw.json`
2. Update token in `.env`:
   ```
   OPENCLAW_GATEWAY_TOKEN=your_token_here
   ```
3. Restart test

### Issue 3: Timeout
```
❌ Error: Request timeout
```

**Solution:**
1. Gateway might be slow to start
2. Wait 30 seconds after starting gateway
3. Check gateway logs for errors
4. Try restarting gateway

### Issue 4: Port Already in Use
```
Error: Port 18789 already in use
```

**Solution:**
1. Check if gateway already running:
   ```bash
   netstat -ano | findstr :18789
   ```
2. Kill existing process or use different port
3. Update port in `openclaw.json`

## 📊 Test Results Interpretation

### All Tests Pass ✅
Gateway is working perfectly! Ready to integrate with bot.

### Connection Test Fails ❌
Gateway not running or not accessible. Start gateway first.

### Spawn Test Fails ❌
Gateway running but can't spawn agents. Check:
- OpenRouter API key in `auth-profiles.json`
- Model availability
- Gateway logs for errors

### Chat Test Fails ❌
Agents spawn but can't chat. Check:
- Agent initialization time (wait longer)
- Model response time
- Gateway logs

## 🎯 Next Steps After Tests Pass

### 1. Integrate with Bot
Add gateway commands to bot:
- `/openclaw_spawn <task>`
- `/openclaw_status <agent_id>`
- `/openclaw_chat <agent_id> <message>`
- `/openclaw_list`

### 2. Test with Telegram
Test commands via Telegram bot:
```
/openclaw_spawn Analyze BTC market
/openclaw_status agent_abc123
/openclaw_chat agent_abc123 What's your analysis?
```

### 3. Deploy to Railway
Deploy both:
- OpenClaw Gateway (separate service)
- Telegram Bot (with gateway bridge)

## 📝 Manual Testing Commands

### Test Health:
```bash
curl http://localhost:18789/health
```

### Test Gateway Info:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:18789/api/info
```

### Test List Agents:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:18789/api/agents
```

## 🔍 Gateway Logs

Gateway logs show:
- Agent spawns
- Tool executions
- API calls
- Errors

Watch logs in gateway terminal for debugging.

## 💡 Tips

1. **Keep Gateway Running**: Don't close gateway terminal during tests
2. **Wait for Initialization**: Give agents 3-5 seconds to initialize
3. **Check Logs**: Gateway logs show detailed execution info
4. **Test Incrementally**: Run quick test first, then full suite
5. **Use Batch File**: Easier than manual commands

## 🎉 Success Criteria

Gateway is ready when:
- ✅ Health check returns 200
- ✅ Can spawn agents
- ✅ Agents respond to chat
- ✅ Can list and stop agents
- ✅ No errors in logs

---

**Ready to Test?**
1. Start gateway: `start_openclaw_gateway.bat`
2. Quick test: `python quick_test_gateway.py`
3. Full test: `python test_openclaw_gateway.py`
4. Celebrate! 🎉
