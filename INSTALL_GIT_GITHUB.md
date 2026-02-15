# 📦 Install Git & Setup GitHub - Panduan Lengkap

## ✅ Status: Git BELUM Terinstall

Saya sudah cek, Git belum terinstall di sistem Anda. Mari kita install!

---

## 🚀 Step 1: Install Git (5 Menit)

### Download Git untuk Windows

1. **Buka browser** dan kunjungi:
   ```
   https://git-scm.com/download/win
   ```

2. **Download** akan otomatis start
   - File: `Git-2.43.0-64-bit.exe` (atau versi terbaru)
   - Size: ~50MB

3. **Run installer** yang sudah didownload

4. **Installation Steps**:
   
   **Screen 1: License**
   - Klik "Next"
   
   **Screen 2: Select Destination**
   - Default: `C:\Program Files\Git`
   - Klik "Next"
   
   **Screen 3: Select Components**
   - ✅ Windows Explorer integration
   - ✅ Git Bash Here
   - ✅ Git GUI Here
   - Klik "Next"
   
   **Screen 4: Select Start Menu Folder**
   - Default: "Git"
   - Klik "Next"
   
   **Screen 5: Choosing the default editor**
   - Pilih: "Use Visual Studio Code as Git's default editor" (jika punya VS Code)
   - Atau: "Use Notepad as Git's default editor"
   - Klik "Next"
   
   **Screen 6: Adjusting your PATH environment**
   - Pilih: "Git from the command line and also from 3rd-party software" (RECOMMENDED)
   - Klik "Next"
   
   **Screen 7-10: Other settings**
   - Semua default OK
   - Klik "Next" terus sampai "Install"
   
   **Screen 11: Installing**
   - Wait 1-2 menit
   
   **Screen 12: Completing**
   - ✅ Launch Git Bash (optional)
   - Klik "Finish"

5. **Verify Installation**:
   
   Buka **PowerShell** atau **Command Prompt** baru, lalu:
   ```bash
   git --version
   ```
   
   Expected output:
   ```
   git version 2.43.0.windows.1
   ```
   
   ✅ Jika muncul version, Git sudah terinstall!

---

## 🔧 Step 2: Configure Git (2 Menit)

Setelah Git terinstall, configure dengan info Anda:

```bash
# Set nama Anda
git config --global user.name "Your Name"

# Set email Anda
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

## 🌐 Step 3: Create GitHub Account (3 Menit)

### A. Sign Up

1. **Buka**: https://github.com/signup
2. **Enter email**: your.email@example.com
3. **Create password**: Strong password
4. **Choose username**: your-username (lowercase, no spaces)
5. **Verify account**: Solve puzzle
6. **Click**: "Create account"

### B. Verify Email

1. Check email inbox
2. Click verification link dari GitHub
3. Account activated! ✅

### C. Complete Profile (Optional)

1. Go to: https://github.com/settings/profile
2. Add:
   - Profile picture
   - Bio
   - Location
3. Save

---

## 🔑 Step 4: Setup GitHub Authentication (5 Menit)

Ada 2 cara: **HTTPS** (mudah) atau **SSH** (lebih aman).

### Option A: HTTPS dengan Personal Access Token (RECOMMENDED)

#### 1. Generate Token

1. Login ke GitHub
2. Klik profile picture (kanan atas) → **Settings**
3. Scroll ke bawah → **Developer settings** (paling bawah)
4. Klik **Personal access tokens** → **Tokens (classic)**
5. Klik **Generate new token** → **Generate new token (classic)**
6. **Note**: "Railway Deployment Token"
7. **Expiration**: 90 days (atau No expiration)
8. **Select scopes**:
   - ✅ `repo` (full control of private repositories)
   - ✅ `workflow` (update GitHub Action workflows)
9. Klik **Generate token**
10. **COPY TOKEN** dan simpan di tempat aman!
    ```
    ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```
    ⚠️ Token hanya muncul sekali! Save sekarang!

#### 2. Use Token

Saat push ke GitHub nanti, gunakan token sebagai password:
```bash
Username: your-github-username
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (token)
```

### Option B: SSH Key (Advanced)

Jika prefer SSH:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Press Enter 3x (default location, no passphrase)

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub:
# Settings → SSH and GPG keys → New SSH key
# Paste key → Add SSH key
```

---

## 📝 Step 5: Test Git & GitHub (2 Menit)

### Test Git Locally

```bash
# Navigate to project
cd C:\V3-Final-Version\Bismillah

# Initialize git
git init

# Check status
git status
```

Expected:
```
Initialized empty Git repository in C:/V3-Final-Version/Bismillah/.git/
```

✅ Git working!

### Test GitHub Connection

```bash
# Test HTTPS
git ls-remote https://github.com/yourusername/test.git

# Or test SSH (if using SSH)
ssh -T git@github.com
```

---

## 🎯 Step 6: Create First Repository (3 Menit)

### A. Create Repo on GitHub

1. Login ke GitHub
2. Klik **+** (kanan atas) → **New repository**
3. **Repository name**: `cryptomentor-bot`
4. **Description**: "CryptoMentor AI Telegram Bot"
5. **Visibility**: 
   - ✅ Private (recommended untuk bot dengan API keys)
   - atau Public (jika mau share)
6. **DON'T** initialize with README (kita sudah punya)
7. Klik **Create repository**

### B. Connect Local to GitHub

GitHub akan show commands, tapi ini versi lengkapnya:

```bash
# Navigate to project
cd C:\V3-Final-Version\Bismillah

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - CryptoMentor Bot ready for Railway"

# Add remote (ganti YOUR_USERNAME dengan username GitHub Anda)
git remote add origin https://github.com/YOUR_USERNAME/cryptomentor-bot.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

Saat diminta credentials:
```
Username: your-github-username
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (token dari Step 4)
```

✅ Code uploaded ke GitHub!

---

## 🎉 Verification

### Check GitHub

1. Buka: https://github.com/YOUR_USERNAME/cryptomentor-bot
2. Harus ada semua files:
   - ✅ `main.py`
   - ✅ `bot.py`
   - ✅ `requirements.txt`
   - ✅ `Procfile`
   - ✅ `railway.json`
   - ✅ dll

### Check Git Status

```bash
cd C:\V3-Final-Version\Bismillah
git status
```

Expected:
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

✅ Everything synced!

---

## 🔄 Daily Git Workflow

### Make Changes

```bash
# Edit files
# ...

# Check what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "Update: description of changes"

# Push to GitHub
git push
```

### Pull Changes (if working from multiple computers)

```bash
git pull
```

---

## 🐛 Troubleshooting

### "git: command not found"

**Solution**: 
1. Close dan reopen PowerShell/CMD
2. Atau restart computer
3. Verify: `git --version`

### "Permission denied (publickey)"

**Solution**: Use HTTPS instead of SSH, atau setup SSH key properly.

### "Authentication failed"

**Solution**: 
1. Make sure using Personal Access Token, bukan password
2. Token harus punya `repo` scope
3. Generate new token jika perlu

### "fatal: remote origin already exists"

**Solution**:
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/cryptomentor-bot.git
```

### ".env file uploaded to GitHub!"

**Solution**: 
```bash
# Remove from GitHub
git rm --cached .env
git commit -m "Remove .env from tracking"
git push

# .gitignore already configured, so won't happen again
```

---

## 📚 Git Commands Cheat Sheet

### Basic Commands

```bash
# Initialize repository
git init

# Check status
git status

# Add files
git add .                    # Add all
git add filename.py          # Add specific file

# Commit
git commit -m "Message"

# Push to GitHub
git push

# Pull from GitHub
git pull

# View history
git log

# View remote
git remote -v
```

### Branch Commands

```bash
# Create branch
git branch feature-name

# Switch branch
git checkout feature-name

# Create and switch
git checkout -b feature-name

# Merge branch
git checkout main
git merge feature-name

# Delete branch
git branch -d feature-name
```

---

## 🎯 Next Steps

### After Git & GitHub Setup:

1. ✅ Git installed
2. ✅ GitHub account created
3. ✅ Repository created
4. ✅ Code pushed to GitHub

### Ready for Railway!

Now you can:
1. Login ke Railway dengan GitHub
2. Deploy from GitHub repo
3. Auto-deploy on push

Follow: `RAILWAY_QUICK_START.md`

---

## 💡 Pro Tips

### 1. Use .gitignore
```bash
# Already configured!
# .env will NOT be uploaded
```

### 2. Commit Often
```bash
# Small, frequent commits better than big ones
git commit -m "Add feature X"
git commit -m "Fix bug Y"
```

### 3. Write Good Commit Messages
```bash
# Good
git commit -m "Add AI analysis feature"
git commit -m "Fix timeout error in SnD detector"

# Bad
git commit -m "update"
git commit -m "fix"
```

### 4. Check Before Push
```bash
git status          # What changed?
git diff            # Show changes
git log --oneline   # Recent commits
```

### 5. Backup Important Branches
```bash
git push origin main
git push origin development
```

---

## 📖 Learning Resources

### Official Docs
- Git: https://git-scm.com/doc
- GitHub: https://docs.github.com

### Interactive Tutorials
- GitHub Skills: https://skills.github.com
- Learn Git Branching: https://learngitbranching.js.org

### Video Tutorials
- YouTube: "Git and GitHub for Beginners"
- YouTube: "Git Tutorial for Beginners"

---

## ✅ Summary

**What We Did**:
1. ✅ Installed Git for Windows
2. ✅ Configured Git with name & email
3. ✅ Created GitHub account
4. ✅ Setup authentication (Personal Access Token)
5. ✅ Created first repository
6. ✅ Pushed code to GitHub

**Time Taken**: ~20 menit

**Result**: Ready to deploy to Railway! 🚀

---

**Date**: 2026-02-15
**Status**: ✅ READY FOR GITHUB & RAILWAY
**Next**: Follow `RAILWAY_QUICK_START.md`

**Happy Coding! 🚀**
