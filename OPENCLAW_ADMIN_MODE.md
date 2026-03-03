# 👑 OpenClaw Admin Mode - System Management via AI

## 🎯 Overview

Admin dapat langsung chat dengan OpenClaw tanpa perlu command `/openclaw_start`. OpenClaw akan auto-activate dan memberikan full system access untuk mengelola bot.

## ✨ Key Features

### 1. Auto-Activation
```
Admin: "Show me bot statistics"
Bot: 👑 Admin Mode Auto-Activated
     [Shows statistics]
```

**No commands needed!** Admin langsung bisa chat.

### 2. System Management
- ✅ Update prices (premium, credits)
- ✅ View bot statistics
- ✅ Check git status
- ✅ Commit & push changes
- ✅ Deploy to Railway
- ✅ Execute SQL queries
- ✅ Add/remove admins

### 3. Git Integration
- Check status
- Commit changes
- Push to GitHub
- Auto-deploy via Railway

## 💡 Admin Capabilities

### Price Management

**View Current Prices:**
```
Admin: "Show me current prices"
Bot: 📊 Current Prices:
     • Premium Monthly: $10
     • Premium Yearly: $100
     • Credits Rate: 100 credits per USDC
     • Platform Fee: 20%
```

**Update Price:**
```
Admin: "Change monthly premium to $15"
Bot: 🔄 Updating price...
     ✅ Updated premium_monthly to $15
     📝 Committing to git...
     ✅ Changes committed and pushed
     🚂 Railway will auto-deploy in ~2-3 minutes
```

### Bot Statistics

```
Admin: "Show bot statistics"
Bot: 📊 Bot Statistics:
     
     👥 Total Users: 1,234
     ⭐ Premium Users: 156
     🤖 OpenClaw Users: 89
     💰 Total Revenue: $2,450
     📈 Active Today: 234 conversations
```

### Git Operations

**Check Status:**
```
Admin: "What's the git status?"
Bot: 📝 Changes:
     M app/openclaw_manager.py
     M .env
```

**Commit & Push:**
```
Admin: "Commit and push these changes"
Bot: 📝 Committing changes...
     ✅ Changes committed and pushed to GitHub
     🚂 Railway will auto-deploy automatically
```

### System Information

```
Admin: "Show system info"
Bot: 🖥️ System Information:
     
     Python: 3.11.5
     Git Branch: main
     Git Commit: abc123f
     Working Dir: /app
     .env File: ✅ Exists
```

### Database Queries

```
Admin: "Show me top 10 users by credits"
Bot: 🔍 Executing query...
     
     Results:
     (user_id: 123, credits: 50000)
     (user_id: 456, credits: 35000)
     ...
```

**Safety:** DROP and DELETE queries are blocked!

### Admin Management

**Add Admin:**
```
Admin: "Add user 789012345 as admin"
Bot: ✅ Added user 789012345 as admin
     Updated .env file
```

**Remove Admin:**
```
Admin: "Remove user 789012345 from admin"
Bot: ✅ Removed user 789012345 from admin
     Updated .env file
```

## 🔧 How It Works

### Auto-Activation Flow

```
1. Admin sends message
   ↓
2. Bot detects admin user_id
   ↓
3. Auto-creates/gets admin assistant
   ↓
4. Auto-activates OpenClaw session
   ↓
5. Shows welcome message (first time)
   ↓
6. Processes message with admin capabilities
```

### System Prompt Enhancement

Admin gets special system prompt with:
- Full system access
- Price management tools
- Git operations
- Deployment capabilities
- Database access
- Admin management

### Tool Integration

OpenClaw can call these admin tools:
- `get_current_prices()` - View prices
- `update_price()` - Change prices
- `get_bot_stats()` - View statistics
- `git_status()` - Check git
- `git_commit_and_push()` - Deploy changes
- `railway_deploy()` - Trigger deployment
- `get_system_info()` - System details
- `add_admin_user()` - Add admin
- `remove_admin_user()` - Remove admin
- `execute_sql()` - Run queries

## 📁 Files Created

### 1. app/openclaw_admin_tools.py
**Admin tools for system management:**
- Price management
- Statistics
- Git operations
- Deployment
- Database queries
- Admin management

### 2. app/openclaw_admin_handler.py
**Auto-activation handler:**
- Detect admin users
- Auto-create assistant
- Auto-activate session
- Welcome message

### 3. app/openclaw_manager.py (Updated)
**Enhanced system prompt:**
- Admin mode detection
- Special capabilities
- Tool descriptions
- Workflow examples

### 4. bot.py (Updated)
**Message handler priority:**
- PRIORITY 0: Admin auto-activation
- PRIORITY 1: OpenClaw message handling
- PRIORITY 2: Normal bot flow

## 🚀 Deployment Workflow

### Example: Change Premium Price

```
Admin: "I want to change monthly premium to $12"

Bot: 🤔 Understood. Let me update the monthly premium price to $12.
     
     Step 1: Updating price...
     ✅ Updated premium_monthly to $12 in .env
     
     Step 2: Committing to git...
     📝 git add .
     📝 git commit -m "Updated premium monthly price to $12"
     📝 git push
     ✅ Changes pushed to GitHub
     
     Step 3: Deployment...
     🚂 Railway detected changes
     🚂 Auto-deployment started
     ⏱️ ETA: 2-3 minutes
     
     ✅ Done! The new price will be live after deployment.
     
     Summary:
     • Old Price: $10
     • New Price: $12
     • Status: Deploying
     • Monitor: https://railway.app
```

## 💰 Price Types

### Available Price Settings

1. **premium_monthly**
   - Monthly premium subscription
   - Default: $10
   - Env: `PREMIUM_MONTHLY_PRICE`

2. **premium_yearly**
   - Yearly premium subscription
   - Default: $100
   - Env: `PREMIUM_YEARLY_PRICE`

3. **openclaw_credits**
   - USDC to credits conversion
   - Default: 100 (1 USDC = 100 credits)
   - Env: `OPENCLAW_USDC_TO_CREDITS`

4. **platform_fee**
   - Platform fee percentage
   - Default: 0.20 (20%)
   - Env: `OPENCLAW_PLATFORM_FEE`

## 🎯 Example Conversations

### Scenario 1: Quick Price Update

```
Admin: "Change yearly premium to $90"

Bot: 🔄 Updating yearly premium price...
     
     ✅ Updated premium_yearly to $90
     📝 Committing: "Updated premium yearly price to $90"
     ✅ Pushed to GitHub
     🚂 Railway auto-deploying
     
     Done! New price will be live in ~2 minutes.
```

### Scenario 2: Check Before Update

```
Admin: "What are the current prices?"

Bot: 📊 Current Prices:
     
     Premium:
     • Monthly: $10
     • Yearly: $100
     
     OpenClaw:
     • Credits Rate: 100 per USDC
     • Platform Fee: 20%

Admin: "Increase monthly to $12"

Bot: 🔄 Updating...
     ✅ Done! Monthly premium now $12
     🚂 Deploying to Railway...
```

### Scenario 3: View Statistics

```
Admin: "How's the bot doing?"

Bot: 📊 Bot Performance:
     
     Users:
     • Total: 1,234 users
     • Premium: 156 (12.6%)
     • OpenClaw: 89 (7.2%)
     
     Revenue:
     • Total: $2,450
     • This Month: $450
     
     Activity:
     • Active Today: 234 conversations
     • Messages Today: 1,567
     
     Looking good! 📈
```

### Scenario 4: Deploy Changes

```
Admin: "What changes are pending?"

Bot: 📝 Git Status:
     
     Modified:
     • app/openclaw_manager.py
     • .env
     
     2 files changed

Admin: "Deploy these changes"

Bot: 🚀 Deploying...
     
     📝 git add .
     📝 git commit -m "Admin updates via OpenClaw"
     📝 git push
     ✅ Pushed to GitHub
     
     🚂 Railway auto-deployment triggered
     ⏱️ ETA: 2-3 minutes
     
     ✅ Deployment in progress!
```

## 🔒 Security

### Admin Detection
```python
def _is_admin(user_id):
    admin_ids = os.getenv('ADMIN_IDS', '').split(',')
    return str(user_id) in admin_ids
```

### SQL Safety
- Only SELECT, UPDATE, INSERT allowed
- DROP and DELETE blocked
- All queries logged
- Rollback on error

### Git Safety
- All commits logged
- Push requires authentication
- Railway deployment monitored

## ⚠️ Important Notes

### 1. Admin Identification
Admin IDs must be in `.env`:
```
ADMIN_IDS=123456789,987654321
```

### 2. Git Configuration
Ensure git is configured:
```bash
git config user.name "Bot Admin"
git config user.email "admin@bot.com"
```

### 3. Railway Connection
Railway must be connected to GitHub repo for auto-deployment.

### 4. Environment Variables
Changes to `.env` require deployment to take effect in production.

## 🧪 Testing

### Test Admin Auto-Activation

```
1. Set your user_id in ADMIN_IDS
2. Send any message to bot
3. Should see: "👑 Admin Mode Auto-Activated"
4. Try: "Show me bot statistics"
```

### Test Price Update

```
1. "Show current prices"
2. "Change monthly premium to $15"
3. Check .env file updated
4. Check git commit created
5. Check Railway deployment
```

### Test Git Operations

```
1. Make a change to code
2. "What's the git status?"
3. "Commit and push changes"
4. Verify on GitHub
5. Check Railway deployment
```

## 📊 Admin Commands Reference

### Prices
- "Show current prices"
- "Change [price_type] to [value]"
- "Update monthly premium to $15"

### Statistics
- "Show bot statistics"
- "How many users do we have?"
- "What's the revenue?"

### Git
- "What's the git status?"
- "Show pending changes"
- "Commit and push"
- "Deploy changes"

### System
- "Show system info"
- "What's the current version?"
- "Check deployment status"

### Database
- "Show top users"
- "Count premium users"
- "Get user statistics"

### Admin Management
- "Add user [id] as admin"
- "Remove user [id] from admin"
- "List all admins"

## 🎉 Benefits

### For Admin
- ✅ No commands needed
- ✅ Natural language interface
- ✅ Quick price updates
- ✅ Easy deployment
- ✅ Real-time statistics

### For System
- ✅ Git version control
- ✅ Automated deployment
- ✅ Audit trail
- ✅ Safe operations
- ✅ Rollback capability

## 🚀 Ready to Use

Admin mode is ready! Just:

1. ✅ Set ADMIN_IDS in .env
2. ✅ Restart bot
3. ✅ Send any message as admin
4. ✅ Start managing the system!

**No /openclaw_start needed for admins!** 👑
