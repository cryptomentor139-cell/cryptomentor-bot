# ✅ Setup Git dengan Akun GitHub Anda

## 🎯 Status: Config Di-Reset, Siap Setup dengan Akun Anda!

Git config yang tadi sudah di-reset. Sekarang Anda bisa setup dengan info GitHub Anda sendiri.

---

## 🔧 Setup Git Config (2 Menit)

### Step 1: Set Nama Anda

Gunakan **nama yang sama** dengan akun GitHub Anda:

```bash
git config --global user.name "Your GitHub Username"
```

**Example**:
```bash
git config --global user.name "nabilfarrel"
```

### Step 2: Set Email Anda

Gunakan **email yang sama** dengan akun GitHub Anda:

```bash
git config --global user.email "your.email@example.com"
```

**Example**:
```bash
git config --global user.email "nabil@example.com"
```

### Step 3: Verify Config

```bash
git config --global --list
```

Expected output:
```
user.name=Your GitHub Username
user.email=your.email@example.com
```

✅ Config ready!

---

## 📋 Info yang Dibutuhkan

Untuk setup Git, Anda perlu:

### 1. GitHub Username
- Buka: https://github.com/YOUR_USERNAME
- Username ada di URL
- Example: `nabilfarrel`

### 2. GitHub Email
- Buka: https://github.com/settings/emails
- Gunakan primary email
- Example: `nabil@example.com`

---

## 🚀 Quick Setup Commands

Copy dan edit dengan info Anda:

```bash
# Ganti dengan info Anda
git config --global user.name "YOUR_GITHUB_USERNAME"
git config --global user.email "YOUR_GITHUB_EMAIL"

# Verify
git config --global --list
```

---

## 💡 Tips

### 1. Gunakan Info yang Sama dengan GitHub

**PENTING**: Gunakan nama dan email yang **sama persis** dengan akun GitHub Anda agar commits ter-link dengan akun Anda.

### 2. Check GitHub Settings

Jika lupa info GitHub:
- Username: https://github.com/settings/profile
- Email: https://github.com/settings/emails

### 3. Multiple Emails?

Jika punya multiple emails di GitHub, gunakan **primary email**.

---

## 🧪 Test Setup

Setelah config, test dengan:

```bash
# Check config
git config --global user.name
git config --global user.email

# Test git commands
cd C:\V3-Final-Version\Bismillah
git init
git status
```

✅ All should work!

---

## 🎯 Next Steps

Setelah Git config ready:

### Step 1: Initialize Repository
```bash
cd C:\V3-Final-Version\Bismillah
git init
git add .
git commit -m "Initial commit - CryptoMentor Bot"
```

### Step 2: Connect to GitHub
```bash
# Ganti YOUR_USERNAME dengan username GitHub Anda
git remote add origin https://github.com/YOUR_USERNAME/cryptomentor-bot.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Railway
Follow: `RAILWAY_QUICK_START.md`

---

## 🔐 GitHub Authentication

Saat push ke GitHub, Anda akan diminta credentials:

### Username
```
Your GitHub username
```

### Password
**JANGAN gunakan password GitHub!**

Gunakan **Personal Access Token**:

1. GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. Select: `repo` scope
5. Generate & copy token
6. Use token sebagai password

Token format:
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ✅ Summary

**Status**: Git config di-reset ✅
**Next**: Setup dengan info GitHub Anda
**Commands**:
```bash
git config --global user.name "YOUR_GITHUB_USERNAME"
git config --global user.email "YOUR_GITHUB_EMAIL"
```

**Ready to deploy!** 🚀

---

**Date**: 2026-02-15
**Status**: ✅ READY FOR YOUR GITHUB ACCOUNT
