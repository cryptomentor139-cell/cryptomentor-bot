# ❓ FAQ - Deployment CryptoMentor Bot

## 🎯 Frequently Asked Questions

Jawaban untuk pertanyaan yang sering ditanyakan tentang deployment bot.

---

## 📋 Table of Contents

1. [Git & GitHub](#git--github)
2. [Personal Access Token](#personal-access-token)
3. [Railway Deployment](#railway-deployment)
4. [Bot Issues](#bot-issues)
5. [Cost & Billing](#cost--billing)
6. [Updates & Maintenance](#updates--maintenance)

---

## 🔧 Git & GitHub

### Q: Apakah saya harus punya akun GitHub?
**A**: Ya, Anda perlu akun GitHub untuk:
- Backup code
- Version control
- Deploy ke Railway (Railway connect via GitHub)

**Buat akun gratis**: https://github.com/signup

---

### Q: Apakah repository harus Private atau Public?
**A**: **Recommended: Private**

**Private**:
- ✅ Code tidak terlihat publik
- ✅ API keys aman (jika ter-commit)
- ✅ Gratis untuk unlimited private repos

**Public**:
- ✅ Open source
- ❌ Code terlihat semua orang
- ❌ Harus hati-hati dengan API keys

**Pilihan**: Private (lebih aman)

---

### Q: Bagaimana jika saya salah commit API key?
**A**: Jangan panik!

**Langkah**:
1. **Revoke API key** yang ter-commit
2. **Generate API key baru**
3. **Update** di Railway environment variables
4. **Remove** dari Git history (optional)

**Prevention**:
- Gunakan `.gitignore` (sudah ada)
- Jangan commit file `.env`
- Gunakan environment variables di Railway

---

### Q: Git command error "not recognized"?
**A**: Git sudah terinstall, tapi PowerShell belum refresh PATH.

**Solution**:
1. **Restart PowerShell**
2. Test: `git --version`
3. Should show: `git version 2.53.0.windows.1`

✅ Fixed!

---

## 🔐 Personal Access Token

### Q: Apa itu Personal Access Token (PAT)?
**A**: PAT adalah "password khusus" untuk Git command line.

**Kenapa perlu PAT?**
- ✅ Lebih aman dari password GitHub
- ✅ Bisa di-revoke kapan saja
- ✅ Punya expiration date
- ✅ Bisa limit permissions

**Format**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

### Q: Dimana saya bisa buat Personal Access Token?
**A**: https://github.com/settings/tokens

**Steps**:
1. Generate new token (classic)
2. Note: `CryptoMentor Bot Deploy`
3. Expiration: `90 days`
4. Select: ✅ `repo`
5. Generate token
6. Copy token (format: `ghp_xxxxx...`)

**File Panduan**: `CARA_BUAT_GITHUB_TOKEN.md`

---

### Q: Token saya expired, apa yang harus dilakukan?
**A**: Buat token baru.

**Steps**:
1. https://github.com/settings/tokens
2. Regenerate token atau Generate new token
3. Copy token baru
4. Update di Git credential (akan diminta saat git push)

**Tip**: Set expiration `90 days` atau `No expiration` (tidak recommended)

---

### Q: Saya lupa token, bagaimana?
**A**: Token tidak bisa dilihat lagi setelah dibuat.

**Solution**:
1. Buat token baru
2. Revoke token lama (optional)
3. Simpan token baru di password manager

**Prevention**: Simpan token di tempat aman!

---

### Q: Error "Authentication failed" saat git push?
**A**: Token salah atau expired.

**Solution**:
1. Buat token baru dengan permission `repo`
2. Copy token dengan benar (jangan ada spasi)
3. Paste sebagai password saat git push

**Check**:
- Token format: `ghp_xxxxx...`
- Token punya permission ✅ `repo`
- Token belum expired

---

## ☁️ Railway Deployment

### Q: Apakah Railway gratis?
**A**: Ada free tier!

**Free Tier**:
- $5 credit per bulan (gratis)
- ~500 hours runtime

**Estimated Cost**:
- Bot 24/7: ~$14/month
- Dengan $5 free: **~$9/month**

**Worth it untuk bot yang reliable!**

---

### Q: Kenapa harus deploy ke Railway?
**A**: Beberapa alasan:

**Advantages**:
- ✅ Bot online 24/7 (tidak perlu komputer nyala)
- ✅ Network issue solved (Railway bisa akses crypto APIs)
- ✅ Auto-deploy on git push
- ✅ Monitoring & logs
- ✅ Scalable
- ✅ Reliable infrastructure

**Alternative**: VPS, Heroku, AWS, dll (lebih ribet)

---

### Q: Bagaimana cara update bot setelah deploy?
**A**: Sangat mudah!

**Steps**:
```powershell
cd C:\V3-Final-Version\Bismillah

# Make changes to your code...

git add .
git commit -m "Update: deskripsi perubahan"
git push

# Railway auto-deploy! 🚀
```

**Time**: 2-3 menit auto-deploy

---

### Q: Bot tidak start di Railway, apa yang harus dilakukan?
**A**: Check logs!

**Steps**:
1. Railway Dashboard
2. Click project
3. Tab **"Deployments"**
4. Click deployment
5. View **Logs**

**Common Issues**:
- Missing environment variables
- Wrong `Procfile` command
- Python version mismatch
- Missing dependencies

**Solution**: Check logs untuk error message

---

### Q: Bagaimana cara melihat logs bot?
**A**: Railway Dashboard → Deployments → Logs

**Real-time logs**:
- Bot startup messages
- Command executions
- Errors
- API calls

**Useful untuk debugging!**

---

### Q: Apakah Railway bisa akses Binance API?
**A**: Ya! ✅

**Current Issue**:
- Local server: ❌ Network blocked
- Railway: ✅ Can access all crypto APIs

**Railway Infrastructure**:
- Google Cloud Platform
- No firewall restrictions
- Can access: Binance, CoinGecko, CryptoCompare, OpenRouter

**This is why we deploy to Railway!**

---

## 🤖 Bot Issues

### Q: Bot tidak respond di Telegram?
**A**: Check beberapa hal:

**1. Bot Status**:
- Railway Dashboard → Check if running
- Logs → Check for errors

**2. Bot Token**:
- Verify `TELEGRAM_BOT_TOKEN` di Railway variables
- Test token: https://api.telegram.org/bot<TOKEN>/getMe

**3. Network**:
- Railway should have no network issues
- Check logs untuk connection errors

---

### Q: AI analysis tidak bekerja?
**A**: Check AI configuration.

**Verify**:
1. `DEEPSEEK_API_KEY` ada di Railway variables
2. `DEEPSEEK_BASE_URL` = `https://openrouter.ai/api/v1`
3. `AI_MODEL` = `stepfun/step-3.5-flash`

**Test**:
```
/ai btc
```

**Expected**: AI analysis dalam 5-10 detik

**If error**: Check Railway logs

---

### Q: Price data tidak muncul?
**A**: Network issue atau API issue.

**On Railway**: Should work! ✅
**On Local**: Might be blocked ❌

**Verify**:
- Railway deployment
- Check logs untuk API errors
- Test: `/price btc`

---

### Q: Database error?
**A**: Check Supabase configuration.

**Verify**:
1. `SUPABASE_URL` correct
2. `SUPABASE_ANON_KEY` correct
3. `SUPABASE_SERVICE_KEY` correct

**Fallback**: Bot uses SQLite if Supabase not available

---

## 💰 Cost & Billing

### Q: Berapa biaya deploy bot?
**A**: ~$9/month (setelah free credit)

**Breakdown**:
- Railway Free Tier: $5/month (gratis)
- Bot 24/7 usage: ~$14/month
- **Net Cost**: ~$9/month

**Comparison**:
- VPS: $5-10/month (tapi harus setup sendiri)
- Heroku: $7/month (limited)
- AWS: $10-20/month (ribet)

**Railway**: Worth it! Easy & reliable

---

### Q: Apakah ada biaya tersembunyi?
**A**: Tidak!

**Railway Pricing**:
- Transparent
- Pay-as-you-go
- No hidden fees
- Free $5 credit per month

**Monitor**: Railway Dashboard → Usage

---

### Q: Bagaimana cara upgrade plan?
**A**: Railway Dashboard → Settings → Plan

**Plans**:
- **Hobby**: $5 credit/month (current)
- **Pro**: $20/month (more resources)
- **Team**: Custom pricing

**Recommendation**: Start with Hobby plan

---

## 🔄 Updates & Maintenance

### Q: Bagaimana cara update bot?
**A**: Git push!

**Steps**:
```powershell
# Make changes
git add .
git commit -m "Update: description"
git push

# Railway auto-deploy!
```

**Time**: 2-3 menit

---

### Q: Apakah bot perlu maintenance?
**A**: Minimal maintenance!

**Regular Tasks**:
- Monitor logs (weekly)
- Check bot statistics (daily)
- Update dependencies (monthly)
- Renew API keys (if expired)

**Railway handles**:
- Server maintenance
- Uptime
- Scaling
- Backups

---

### Q: Bagaimana cara backup bot?
**A**: Already backed up!

**Backups**:
- ✅ Code: GitHub repository
- ✅ Database: Supabase (auto-backup)
- ✅ Logs: Railway (7 days retention)

**Manual Backup**:
```powershell
# Clone repository
git clone https://github.com/YOUR_USERNAME/cryptomentor-bot.git
```

---

### Q: Bot down, bagaimana cara restart?
**A**: Railway auto-restart!

**Manual Restart**:
1. Railway Dashboard
2. Click project
3. Tab "Deployments"
4. Click "Redeploy"

**Auto-restart**: Railway restarts on crash

---

## 🐛 Troubleshooting

### Q: Error "Permission denied" saat git push?
**A**: Token tidak punya permission `repo`.

**Solution**:
1. Buat token baru
2. Centang ✅ `repo`
3. Copy token
4. Use sebagai password

---

### Q: Error "remote: Repository not found"?
**A**: Repository URL salah.

**Check**:
```powershell
git remote -v
```

**Fix**:
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/cryptomentor-bot.git
git push -u origin main
```

---

### Q: Railway deployment failed?
**A**: Check logs untuk error.

**Common Issues**:
- Missing `requirements.txt`
- Wrong `Procfile` command
- Missing environment variables
- Python version mismatch

**Solution**: Fix error dan git push lagi

---

### Q: Bot lambat respond?
**A**: Check beberapa hal:

**1. AI Model**:
- StepFun: 2-5 detik (FAST) ✅
- DeepSeek: 10-15 detik (SLOW) ❌

**Current**: StepFun (FREE & FAST)

**2. Network**:
- Railway: Fast ✅
- Local: Might be slow ❌

**3. API Rate Limits**:
- Check logs untuk rate limit errors

---

## 📚 Additional Resources

### File Panduan:
- `MULAI_DISINI.md` - Start here
- `LANGKAH_SELANJUTNYA.md` - Step-by-step guide
- `QUICK_COMMANDS.md` - Copy-paste commands
- `CARA_BUAT_GITHUB_TOKEN.md` - Token guide
- `DEPLOYMENT_CHECKLIST_VISUAL.md` - Progress tracker
- `DEPLOYMENT_FLOW.md` - Visual flow diagram

### External Links:
- GitHub: https://github.com
- GitHub Tokens: https://github.com/settings/tokens
- Railway: https://railway.app
- Railway Docs: https://docs.railway.app

---

## 🎯 Quick Help

### Stuck on Git?
**Read**: `CARA_BUAT_GITHUB_TOKEN.md`

### Stuck on Railway?
**Read**: `RAILWAY_QUICK_START.md`

### Need Commands?
**Read**: `QUICK_COMMANDS.md`

### Want Step-by-Step?
**Read**: `LANGKAH_SELANJUTNYA.md`

---

## ✅ Still Have Questions?

### Check These Files:
1. `PANDUAN_DEPLOYMENT.md` - Overview
2. `LANGKAH_SELANJUTNYA.md` - Detailed guide
3. `DEPLOYMENT_FLOW.md` - Visual flow
4. `FAQ_DEPLOYMENT.md` - This file

### Common Issues:
- Git: `CARA_BUAT_GITHUB_TOKEN.md`
- Railway: `RAILWAY_DEPLOYMENT_GUIDE.md`
- Bot: Check Railway logs

---

## 🎊 Summary

**Most Common Questions**:
1. ✅ Personal Access Token - `CARA_BUAT_GITHUB_TOKEN.md`
2. ✅ Railway Cost - ~$9/month
3. ✅ Update Bot - `git push` (auto-deploy)
4. ✅ Bot Issues - Check Railway logs
5. ✅ Network Issue - Solved on Railway

**Start Deployment**: `MULAI_DISINI.md` 👈

---

**Date**: 2026-02-15
**Status**: ✅ READY TO DEPLOY

**Happy Deploying!** 🚀🎉
