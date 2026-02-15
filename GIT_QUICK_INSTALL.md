# ⚡ Git Quick Install - 10 Menit

## ❌ Status: Git BELUM Terinstall

Git belum terinstall di sistem Anda. Mari install sekarang!

---

## 🚀 Quick Install (10 Menit)

### Step 1: Download Git (2 menit)

1. Buka: https://git-scm.com/download/win
2. Download otomatis start (~50MB)
3. Run installer `Git-2.43.0-64-bit.exe`

### Step 2: Install Git (3 menit)

1. **Klik "Next"** di semua screen
2. **PENTING**: Di screen "Adjusting PATH":
   - Pilih: "Git from the command line and also from 3rd-party software"
3. **Klik "Next"** sampai "Install"
4. Wait 1-2 menit
5. **Klik "Finish"**

### Step 3: Verify (1 menit)

Buka **PowerShell BARU**, lalu:
```bash
git --version
```

Expected:
```
git version 2.43.0.windows.1
```

✅ Git installed!

### Step 4: Configure (2 menit)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 5: GitHub Account (2 menit)

1. Buka: https://github.com/signup
2. Enter email, password, username
3. Verify email
4. Done!

---

## 🔑 GitHub Token (PENTING!)

### Generate Token:

1. GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. Select: `repo` scope
5. Generate token
6. **COPY & SAVE TOKEN!**
   ```
   ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Use Token:

Saat push ke GitHub, gunakan token sebagai password:
```
Username: your-github-username
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ✅ Test Git

```bash
cd C:\V3-Final-Version\Bismillah
git init
git status
```

Expected:
```
Initialized empty Git repository
```

✅ Ready!

---

## 🎯 Next Steps

1. ✅ Git installed
2. ✅ GitHub account created
3. ✅ Token generated

**Now**: Follow `RAILWAY_QUICK_START.md` untuk deploy!

---

**Total Time: 10 menit**
**Status: ✅ READY**

**Full Guide**: See `INSTALL_GIT_GITHUB.md`
