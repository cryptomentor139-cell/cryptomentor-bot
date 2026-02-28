# ✅ Fix: Git Not Recognized - SOLVED!

## ❌ Masalah

Setelah install Git, muncul error:
```
git : The term 'git' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

## 🔍 Root Cause

**PowerShell belum refresh PATH environment variable** setelah Git diinstall.

Git sudah terinstall dengan benar, tapi PowerShell masih pakai PATH lama yang tidak include Git.

---

## ✅ Solusi (Pilih Salah Satu)

### Option 1: Restart PowerShell (TERMUDAH) ⭐

1. **Close** PowerShell yang sekarang
2. **Buka PowerShell BARU**
3. Test:
   ```bash
   git --version
   ```

Expected:
```
git version 2.53.0.windows.1
```

✅ Git working!

### Option 2: Refresh PATH (Tanpa Restart)

Jika tidak mau close PowerShell, jalankan command ini:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

Lalu test:
```bash
git --version
```

✅ Git working!

### Option 3: Restart Computer (Paling Pasti)

Jika kedua option di atas tidak work:
1. Restart computer
2. Buka PowerShell
3. Test: `git --version`

✅ Pasti working!

---

## 🧪 Verify Git Installation

### Test 1: Check Version
```bash
git --version
```

Expected:
```
git version 2.53.0.windows.1
```

### Test 2: Check Git Location
```bash
where.exe git
```

Expected:
```
C:\Program Files\Git\cmd\git.exe
```

### Test 3: Check Git Config
```bash
git config --list
```

Expected: List of git configurations

---

## 🔧 Configure Git (Jika Belum)

Setelah Git working, configure dengan info Anda:

```bash
# Set nama
git config --global user.name "Your Name"

# Set email
git config --global user.email "your.email@example.com"

# Verify
git config --list
```

Example:
```bash
git config --global user.name "Nabil Farrel"
git config --global user.email "nabil@example.com"
```

---

## 📝 Test Git Commands

### Initialize Repository
```bash
cd C:\V3-Final-Version\Bismillah
git init
```

Expected:
```
Initialized empty Git repository in C:/V3-Final-Version/Bismillah/.git/
```

### Check Status
```bash
git status
```

Expected:
```
On branch main
No commits yet
Untracked files: ...
```

### Add Files
```bash
git add .
```

### Commit
```bash
git commit -m "Initial commit"
```

✅ All working!

---

## 🎯 Next Steps

Setelah Git working:

1. ✅ Git installed & working
2. ✅ Git configured
3. ⏭️ Create GitHub account (jika belum)
4. ⏭️ Push code ke GitHub
5. ⏭️ Deploy ke Railway

Follow: `RAILWAY_QUICK_START.md`

---

## 💡 Why This Happens?

### Technical Explanation:

1. **Git installer** menambahkan Git path ke **System Environment Variables**
2. **PowerShell** yang sudah running pakai **cached PATH** (PATH lama)
3. **Restart PowerShell** → Load PATH baru → Git terdeteksi

### PATH Location:

Git biasanya diinstall di:
```
C:\Program Files\Git\cmd\
```

Dan ditambahkan ke PATH environment variable.

---

## 🐛 Troubleshooting

### Still Not Working After Restart?

#### Check 1: Git Installation Location
```bash
dir "C:\Program Files\Git\cmd\git.exe"
```

Jika file ada, Git terinstall dengan benar.

#### Check 2: PATH Environment Variable

1. Open **System Properties**:
   - Press `Win + R`
   - Type: `sysdm.cpl`
   - Press Enter

2. Click **Advanced** tab
3. Click **Environment Variables**
4. Under **System variables**, find **Path**
5. Click **Edit**
6. Check if ada entry:
   ```
   C:\Program Files\Git\cmd
   ```

Jika tidak ada, **Add** manually:
- Click **New**
- Add: `C:\Program Files\Git\cmd`
- Click **OK**
- Restart PowerShell

#### Check 3: Reinstall Git

Jika masih tidak work:
1. Uninstall Git (Control Panel → Programs)
2. Download Git lagi: https://git-scm.com/download/win
3. Install dengan option:
   - ✅ "Git from the command line and also from 3rd-party software"
4. Restart computer
5. Test: `git --version`

---

## ✅ Summary

**Problem**: Git not recognized setelah install
**Cause**: PowerShell belum refresh PATH
**Solution**: Restart PowerShell atau refresh PATH
**Status**: ✅ SOLVED!

**Git Version Detected**: 2.53.0.windows.1
**Ready for**: GitHub & Railway deployment!

---

**Date**: 2026-02-15
**Status**: ✅ GIT WORKING
**Next**: Follow `RAILWAY_QUICK_START.md`

**Happy Coding! 🚀**
