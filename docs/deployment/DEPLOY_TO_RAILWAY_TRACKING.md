# 🚂 Deploy Signal Tracking to Railway - Complete Guide

## 🎯 Overview

Signal Tracking V2.0 supports **dual environment**:
- **Local**: Uses G: drive for fast development
- **Railway**: Uses Supabase Storage for cloud persistence

## 📋 Pre-Deployment Checklist

- [ ] Code tested locally
- [ ] G: drive working on local
- [ ] Supabase project created
- [ ] GitHub repository ready
- [ ] Railway project connected

## 🔧 Step 1: Setup Supabase Storage

### 1.1 Create Bucket

1. Go to Supabase Dashboard: https://app.supabase.com
2. Select your project
3. Navigate to **Storage**
4. Click **Create Bucket**
5. Settings:
   - Name: `cryptobot-signals`
   - Public: **No** (keep private)
   - File size limit: 50MB
6. Click **Create**

### 1.2 Get Credentials

Already in your `.env`:
```bash
SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
```

## 🚀 Step 2: Configure Railway

### 2.1 Environment Variables

Add these to Railway:

```bash
# Disable G: drive (not available on Railway)
USE_GDRIVE=false

# Enable Supabase Storage
USE_SUPABASE_STORAGE=true

# Supabase credentials
SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Admin IDs (for weekly reports)
ADMIN1=1187119989
ADMIN2=7079544380

# Telegram Bot Token
TELEGRAM_BOT_TOKEN=your_bot_token
```

### 2.2 How to Add Variables

**Via Railway Dashboard:**
1. Go to your project
2. Click **Variables** tab
3. Add each variable
4. Click **Deploy** to apply

**Via Railway CLI:**
```bash
railway variables set USE_GDRIVE=false
railway variables set USE_SUPABASE_STORAGE=true
railway variables set SUPABASE_URL=your_url
railway variables set SUPABASE_SERVICE_KEY=your_key
```

## 📦 Step 3: Deploy Code

### 3.1 Commit Changes

```bash
git add .
git commit -m "Add signal tracking V2.0 with Supabase support"
git push origin main
```

### 3.2 Railway Auto-Deploy

Railway will automatically:
1. Detect push to GitHub
2. Build new image
3. Deploy updated bot
4. Restart service

### 3.3 Monitor Deployment

Watch logs in Railway dashboard:
```
Building...
✅ Build successful
Deploying...
✅ Deployment successful
Starting bot...
✅ Signal logger initialized
📁 Log directory: signal_logs
☁️ Using Supabase Storage: True
✅ Bot started successfully
```

## ✅ Step 4: Verify Deployment

### 4.1 Check Bot Status

In Telegram:
```bash
/signal_stats
```

Expected output:
```
📊 STATISTIK SIGNAL TRACKING

📝 DATA TERSIMPAN:
• Total Prompts: 0
• Active Signals: 0
• Completed Signals: 0

☁️ STORAGE:
• Type: Supabase Storage (Cloud)
• Status: ✅ Enabled
• Bucket: cryptobot-signals
• Files: 0
```

### 4.2 Test Tracking

```bash
# Test any command
/analyze btc

# Check stats again
/signal_stats
```

Should show:
```
• Total Prompts: 1
```

### 4.3 Test Upload

```bash
/upload_logs
```

Expected:
```
✅ Supabase Upload complete!
📊 Uploaded: 1 files
❌ Failed: 0 files
```

### 4.4 Verify in Supabase

1. Go to Supabase Dashboard
2. Storage → cryptobot-signals
3. Should see files:
   - `prompts_2026-02-16.jsonl`
   - `active_signals.jsonl`
   - etc.

## 📊 Step 5: Weekly Report Setup

### 5.1 Scheduler Auto-Start

Scheduler starts automatically when bot starts:
```
✅ Scheduler started
Next daily sync in 8.5 hours
Next weekly report in 42.3 hours
```

### 5.2 Schedule

- **Daily Backup**: 23:00 UTC → Upload to Supabase
- **Weekly Report**: Monday 09:00 WIB → Send to admins

### 5.3 Test Weekly Report

Manual trigger:
```bash
/weekly_report
```

Expected output:
```
📊 LAPORAN MINGGUAN SIGNAL
🗓️ Periode: 10/02/2026 - 17/02/2026

📈 PERFORMA SIGNAL:
• Total Signal: 0
• Win: 0 ✅
• Loss: 0 ❌
• Winrate: 0% 🎯
• Avg PnL: 0%

👥 AKTIVITAS USER:
• Total Prompts: 1
• Rata-rata per hari: 0

📊 ANALISIS:
⏳ Belum ada data signal untuk analisis

🎯 REKOMENDASI:
• Mulai track signal untuk mendapatkan insights
```

## 🔄 Step 6: Iteration Process

### 6.1 Data Collection (Automatic)

Every signal is tracked:
```python
# In your command handlers
track_user_command(user.id, user.username, "/analyze", "BTC", "1h")
track_signal_given(user.id, "BTCUSDT", "1h", 50000, 51000, 52000, 49500)
```

### 6.2 Weekly Analysis (Automatic)

Every Monday 09:00 WIB:
1. Calculate winrate
2. Analyze patterns
3. Generate recommendations
4. Send to all admins

### 6.3 Manual Review (You)

When you receive weekly report:
1. Review winrate percentage
2. Check WIN/LOSS ratio
3. Identify losing patterns
4. Plan improvements

### 6.4 Implement Changes (Development)

On your local machine:
1. Update signal parameters
2. Test with G: drive
3. Verify improvements
4. Push to Railway

### 6.5 Monitor Results (Next Week)

Compare reports:
```
Week 1: Winrate 65%
Week 2: Winrate 70% ✅ Improved!
Week 3: Winrate 75% ✅ Keep going!
```

## 📈 Continuous Improvement Cycle

```
Week 1: Collect Data
    ↓
Week 2: Analyze Report
    ↓
Week 3: Identify Issues
    ↓
Week 4: Implement Fixes
    ↓
Week 5: Monitor Results
    ↓
Repeat...
```

## 🎯 Key Metrics to Track

### Signal Quality
- Winrate percentage
- Average PnL
- WIN/LOSS ratio

### User Engagement
- Total prompts per week
- Active users
- Command usage

### System Health
- Upload success rate
- Storage usage
- Error rate

## 🔍 Monitoring & Debugging

### Check Railway Logs

```bash
# Via CLI
railway logs --tail

# Look for:
✅ Signal tracked
✅ Uploaded to Supabase
✅ Weekly report sent
```

### Check Supabase Storage

Dashboard → Storage → cryptobot-signals:
- Files should update daily
- Check file sizes
- Verify timestamps

### Check Telegram

Admin should receive:
- Weekly reports (Monday 09:00)
- No error messages
- `/signal_stats` works

## ⚠️ Troubleshooting

### Issue: Supabase Upload Fails

**Check:**
```bash
# In Railway logs
❌ Upload failed: Authentication error
```

**Solution:**
1. Verify `SUPABASE_SERVICE_KEY` in Railway
2. Check bucket permissions
3. Ensure bucket exists

### Issue: Weekly Report Not Sent

**Check:**
```bash
# In Railway logs
⏰ Next weekly report in X hours
```

**Solution:**
1. Verify scheduler started
2. Check admin IDs in environment
3. Wait for scheduled time

### Issue: No Data in Reports

**Check:**
```bash
/signal_stats
# Should show prompts > 0
```

**Solution:**
1. Ensure tracking integrated in commands
2. Test with `/analyze btc`
3. Verify files created

## ✅ Success Criteria

After deployment, you should have:

- [x] Bot running on Railway
- [x] Supabase Storage connected
- [x] Files uploading successfully
- [x] `/signal_stats` shows correct data
- [x] Weekly report scheduled
- [x] Admin receives reports
- [x] Iteration cycle working

## 🎉 Result

You now have:

- ✅ **Production Bot**: Running 24/7 on Railway
- ✅ **Cloud Storage**: All data in Supabase
- ✅ **Weekly Reports**: Automatic to admin
- ✅ **Iteration Loop**: Data-driven improvements
- ✅ **Scalable**: Works at any scale

## 📚 Next Steps

1. **Week 1**: Let it collect data
2. **Week 2**: Review first report
3. **Week 3**: Identify patterns
4. **Week 4**: Implement improvements
5. **Week 5**: Monitor results
6. **Repeat**: Continuous improvement!

---

**Deployment Time**: ~15 minutes  
**Maintenance**: Minimal (automated)  
**Iteration Cycle**: Weekly  
**Expected Improvement**: 5-10% winrate per month
