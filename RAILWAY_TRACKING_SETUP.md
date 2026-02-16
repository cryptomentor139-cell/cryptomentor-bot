# 🚂 Railway Deployment - Signal Tracking Setup

## ⚠️ Important: G: Drive Not Available on Railway

Railway runs on Linux servers - **no G: drive mount available**. We need cloud storage solution.

## 🎯 Solution: Dual Environment Support

### Local Development (Your PC)
- ✅ Uses G: drive mount
- ✅ Real-time sync to Google Drive
- ✅ Easy access via File Explorer

### Railway Production (Cloud)
- ✅ Uses Supabase Storage
- ✅ Cloud-based backup
- ✅ Accessible from anywhere

## 📦 Setup for Railway

### 1. Environment Variables

Add to Railway environment variables:

```bash
# Disable G: drive (not available on Railway)
USE_GDRIVE=false

# Use Supabase for storage
USE_SUPABASE_STORAGE=true

# Supabase credentials (already in .env)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_key
SUPABASE_SERVICE_KEY=your_service_key
```

### 2. Supabase Storage Setup

Create bucket in Supabase:

1. Go to Supabase Dashboard
2. Storage → Create Bucket
3. Name: `cryptobot-signals`
4. Public: No (private)
5. Create

### 3. Code Already Supports Both!

The code automatically detects environment:

```python
# In signal_logger.py
if os.getenv('USE_GDRIVE', 'true').lower() == 'true' and os.path.exists('G:/'):
    # Use G: drive (local)
    self.log_dir = Path(gdrive_path)
else:
    # Use local/Supabase (Railway)
    self.log_dir = Path('signal_logs')
```

## 🔄 How It Works

### Local (Your PC):
```
User Command
    ↓
Save to G:/Drive Saya/CryptoBot_Signals/
    ↓
Google Drive for Desktop auto-sync
    ↓
Available in cloud
```

### Railway (Production):
```
User Command
    ↓
Save to signal_logs/ (temporary)
    ↓
Upload to Supabase Storage
    ↓
Available in cloud
```

## 📊 Weekly Report

Weekly report works on **both environments**:

- **Local**: Reads from G: drive
- **Railway**: Reads from Supabase Storage
- **Admin**: Receives report via Telegram (same)

## 🚀 Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Add signal tracking V2.0"
git push origin main
```

### 2. Railway Auto-Deploy

Railway will automatically:
- Detect changes
- Rebuild
- Deploy new version

### 3. Set Environment Variables

In Railway dashboard:
```
USE_GDRIVE=false
USE_SUPABASE_STORAGE=true
```

### 4. Verify Deployment

Check Railway logs:
```
✅ Signal logger initialized
📁 Log directory: signal_logs
☁️ Using Supabase Storage: True
```

## 💡 Best Practice

### Development Workflow:

1. **Local Testing** (Your PC)
   - Use G: drive
   - Fast iteration
   - Easy debugging

2. **Push to GitHub**
   - Commit changes
   - Railway auto-deploy

3. **Production** (Railway)
   - Uses Supabase
   - Cloud storage
   - Always available

## 🔍 Monitoring

### Check Logs on Railway:

```bash
# Via Railway CLI
railway logs

# Or via Dashboard
# Project → Deployments → View Logs
```

### Check Signal Stats:

```bash
# In Telegram
/signal_stats
```

Expected output on Railway:
```
📊 STATISTIK SIGNAL TRACKING

📝 DATA TERSIMPAN:
• Total Prompts: 156
• Active Signals: 12
• Completed Signals: 45

☁️ STORAGE:
• Type: Supabase Storage
• Status: ✅ Connected
```

## 🎯 Weekly Report Schedule

Scheduler works on Railway:

- **Daily Backup**: 23:00 UTC (upload to Supabase)
- **Weekly Report**: Monday 09:00 WIB (send to admins)

## ⚙️ Configuration

### .env (Local)
```bash
USE_GDRIVE=true
GDRIVE_PATH=G:/Drive Saya/CryptoBot_Signals
```

### Railway Environment Variables
```bash
USE_GDRIVE=false
USE_SUPABASE_STORAGE=true
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
```

## 🔄 Data Sync Strategy

### Option A: Manual Sync
- Download from Supabase periodically
- Review on local machine
- Analyze with tools

### Option B: Automated Sync
- Supabase → Google Drive sync (via script)
- Best of both worlds
- Requires additional setup

## 📈 Iteration Process

### 1. Collect Data (Automatic)
- Railway tracks all signals
- Stores in Supabase
- Weekly report to admin

### 2. Analyze (Manual)
- Review weekly report
- Check WIN/LOSS patterns
- Identify improvements

### 3. Iterate (Development)
- Update signal parameters
- Test locally with G: drive
- Push to Railway

### 4. Monitor (Automatic)
- Next week's report
- Compare results
- Continuous improvement

## ✅ Verification Checklist

### Before Deploy:
- [ ] Code pushed to GitHub
- [ ] Railway environment variables set
- [ ] Supabase bucket created
- [ ] .env updated for local

### After Deploy:
- [ ] Railway logs show success
- [ ] `/signal_stats` works
- [ ] Weekly report scheduled
- [ ] Data saving correctly

## 🎉 Result

You get:

- ✅ **Local**: Fast development with G: drive
- ✅ **Railway**: Production-ready with Supabase
- ✅ **Weekly Reports**: Automatic to admin
- ✅ **Iteration**: Data-driven improvements
- ✅ **Scalable**: Works at any scale

---

**Note**: G: drive is for local development only. Railway uses Supabase Storage for cloud persistence.
