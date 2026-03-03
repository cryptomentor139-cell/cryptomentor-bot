# OpenClaw Railway Deployment Guide

## ⚠️ Important Note

OpenClaw CLI **tidak bisa berjalan langsung di Railway** karena:
- Memerlukan Node.js + npm global packages
- Butuh persistent storage untuk workspace
- Gateway perlu port dedicated
- Resource intensive

## 🎯 Deployment Strategy: Hybrid Approach

### Option 1: Payment System Only (Recommended)
Deploy payment system & monitoring ke Railway, OpenClaw CLI tetap local/separate server.

### Option 2: Full Cloud (Advanced)
Deploy OpenClaw di VPS terpisah, Railway hanya untuk bot.

---

## ✅ Option 1: Payment System Deployment

Deploy ke Railway dengan fitur:
- ✅ Credit management
- ✅ Payment processing
- ✅ Admin monitoring
- ✅ User balance tracking
- ❌ OpenClaw CLI (run separately)

### Step 1: Update bot.py

Tambahkan handler registrations:

```python
# In bot.py, di method setup_application()

# Register OpenClaw deposit handlers
try:
    from app.handlers_openclaw_deposit import register_openclaw_deposit_handlers
    register_openclaw_deposit_handlers(self.application)
    print("✅ OpenClaw deposit handlers registered")
except Exception as e:
    print(f"⚠️ OpenClaw deposit handlers failed: {e}")

# Register OpenClaw admin handlers
try:
    from app.handlers_openclaw_admin import register_openclaw_admin_handlers
    register_openclaw_admin_handlers(self.application)
    print("✅ OpenClaw admin handlers registered")
except Exception as e:
    print(f"⚠️ OpenClaw admin handlers failed: {e}")
```

### Step 2: Run Migration

```bash
# Connect to Railway database
railway run psql $DATABASE_URL

# Run migration
\i migrations/012_openclaw_payment_system.sql

# Verify tables
\dt openclaw*

# Should show:
# - openclaw_credits
# - openclaw_transactions
# - openclaw_usage_log
# - openclaw_pending_deposits
# - openclaw_platform_revenue
# - openclaw_chat_monitor
```

### Step 3: Set Environment Variables

Di Railway dashboard, tambahkan:

```env
# Admin wallet (same as /subscribe)
ADMIN_WALLET_ADDRESS=0xed7342ac9c22b1495af4d63f15a7c9768a028ea8

# OpenRouter API (for credits)
OPENROUTER_API_KEY=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

# Anthropic API (for OpenClaw)
ANTHROPIC_API_KEY=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
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
```

### Step 4: Deploy

```bash
cd Bismillah

# Commit changes
git add .
git commit -m "Add OpenClaw payment system & monitoring"

# Push to Railway
git push origin main

# Railway will auto-deploy
```

### Step 5: Verify Deployment

Test commands di Telegram:
```
/openclaw_deposit → Should show deposit options
/openclaw_balance → Should show $0.00
/openclaw_status → Should show OpenClaw info
/openclaw_monitor → Admin dashboard (admin only)
```

---

## 🚀 Option 2: Full Cloud Deployment

### Architecture:

```
Railway (Bot)
    ↓ API calls
VPS/Cloud Server (OpenClaw CLI)
    ↓
OpenRouter API
```

### Requirements:

1. **VPS Server** (DigitalOcean, Linode, AWS EC2)
   - Ubuntu 22.04
   - 2GB RAM minimum
   - Node.js 18+
   - Python 3.11+

2. **OpenClaw Gateway**
   - Running on VPS
   - Exposed via HTTPS
   - Secured with API key

### VPS Setup:

```bash
# 1. Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 2. Install OpenClaw
npm install -g openclaw

# 3. Configure OpenClaw
export ANTHROPIC_API_KEY=sk-or-v1-...
openclaw configure

# 4. Start Gateway
openclaw gateway --port 18789

# 5. Setup systemd service (keep running)
sudo nano /etc/systemd/system/openclaw.service
```

### Systemd Service:

```ini
[Unit]
Description=OpenClaw Gateway
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
Environment="ANTHROPIC_API_KEY=sk-or-v1-..."
ExecStart=/usr/bin/openclaw gateway --port 18789
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable openclaw
sudo systemctl start openclaw
sudo systemctl status openclaw
```

### Railway Configuration:

```env
# Point to VPS gateway
OPENCLAW_GATEWAY_URL=https://your-vps-ip:18789
OPENCLAW_GATEWAY_TOKEN=your-secure-token
```

---

## 📋 Deployment Checklist

### Pre-Deployment:

- [ ] Migration file ready (`012_openclaw_payment_system.sql`)
- [ ] Handlers registered in `bot.py`
- [ ] Environment variables configured
- [ ] Admin wallet address set
- [ ] OpenRouter API key set

### Railway Deployment:

- [ ] Run database migration
- [ ] Set environment variables
- [ ] Push code to Railway
- [ ] Verify deployment logs
- [ ] Test commands in Telegram

### Post-Deployment:

- [ ] Test `/openclaw_deposit`
- [ ] Test `/openclaw_balance`
- [ ] Test `/openclaw_status`
- [ ] Test admin commands
- [ ] Monitor logs for errors

---

## 🔧 Troubleshooting

### Issue: "openclaw_credits table not found"
**Solution:** Run migration
```bash
railway run psql $DATABASE_URL < migrations/012_openclaw_payment_system.sql
```

### Issue: "ADMIN_WALLET_ADDRESS not set"
**Solution:** Add to Railway environment variables
```
ADMIN_WALLET_ADDRESS=0xed7342ac9c22b1495af4d63f15a7c9768a028ea8
```

### Issue: "OpenClaw CLI not accessible"
**Solution:** This is expected on Railway. OpenClaw CLI features will show "Setup Required" message. Payment system still works!

### Issue: Import errors
**Solution:** Check all files are committed:
```bash
git status
git add app/openclaw_payment_system.py
git add app/handlers_openclaw_deposit.py
git add app/handlers_openclaw_admin.py
git add app/openclaw_chat_monitor.py
git commit -m "Add OpenClaw files"
git push
```

---

## 🎯 What Works on Railway

### ✅ Working Features:

1. **Payment System**
   - Deposit flow
   - Credit management
   - Balance tracking
   - Transaction history

2. **Admin Tools**
   - Add credits manually
   - Check user balance
   - Monitor activity
   - View statistics

3. **Monitoring**
   - Log all attempts
   - Track users without credits
   - Revenue tracking
   - Platform fees

### ❌ Not Working (Needs Separate Server):

1. **OpenClaw CLI**
   - Gateway
   - Agent spawning
   - Tool execution
   - Workspace management

---

## 💡 Recommended Approach

### Phase 1: Deploy Payment System (Now)
```
Railway: Bot + Payment System
Users: Can deposit, get credits
Admin: Can manage credits
OpenClaw: Shows "coming soon" message
```

### Phase 2: Add VPS (Later)
```
Railway: Bot + Payment System
VPS: OpenClaw Gateway
Users: Full OpenClaw features
Admin: Full monitoring
```

### Phase 3: Scale (Future)
```
Railway: Bot + Payment
VPS Cluster: Multiple OpenClaw instances
Load Balancer: Distribute requests
Users: Fast & reliable service
```

---

## 🚀 Quick Deploy Commands

```bash
# 1. Commit all changes
cd Bismillah
git add .
git commit -m "Add OpenClaw payment system"

# 2. Push to Railway
git push origin main

# 3. Run migration (in Railway dashboard)
railway run psql $DATABASE_URL < migrations/012_openclaw_payment_system.sql

# 4. Set environment variables (in Railway dashboard)
# Add: ADMIN_WALLET_ADDRESS, OPENROUTER_API_KEY, ANTHROPIC_API_KEY

# 5. Restart service
railway restart

# 6. Test in Telegram
# /openclaw_deposit
# /openclaw_balance
# /openclaw_status
```

---

## 📊 Expected Results

After deployment, users will see:

```
/openclaw_deposit
→ ✅ Shows deposit options
→ ✅ Shows wallet address
→ ✅ Shows 80/20 split

/openclaw_balance
→ ✅ Shows $0.00 (or actual balance)
→ ✅ Shows statistics

/openclaw_ask "question"
→ ⚠️ Shows "insufficient credits" if no balance
→ ⚠️ Shows "setup required" if has balance (CLI not on Railway)

Admin commands:
→ ✅ /openclaw_add_credits works
→ ✅ /openclaw_monitor works
→ ✅ /openclaw_check_user works
```

---

## ✅ Summary

**Deploy Now:**
- Payment system ✅
- Credit management ✅
- Admin monitoring ✅
- User balance tracking ✅

**Deploy Later (Optional):**
- OpenClaw CLI on VPS
- Full AI agent features
- Gateway integration

**Status:** Ready to deploy payment system to Railway!

---

**Last Updated:** 2026-03-03
**Deployment:** Railway (Payment System)
**OpenClaw CLI:** Separate server (optional)
**Status:** ✅ READY TO DEPLOY
