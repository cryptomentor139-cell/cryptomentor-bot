# 📚 Panduan GitHub untuk Pemula - Step by Step

## 🎯 Goal
Push project CryptoMentor Bot ke GitHub dalam 10 menit!

---

## 📋 Persiapan (5 menit)

### Step 1: Install Git (Jika Belum Ada)

#### Cek apakah Git sudah terinstall:
```bash
git --version
```

**Jika muncul versi** (contoh: `git version 2.40.0`):
- ✅ Git sudah terinstall, lanjut ke Step 2

**Jika muncul error** (`'git' is not recognized`):
- ❌ Git belum terinstall, install dulu:

#### Install Git di Windows:
1. Download dari: https://git-scm.com/download/win
2. Jalankan installer
3. Klik "Next" terus sampai selesai
4. Restart Command Prompt
5. Test lagi: `git --version`

### Step 2: Buat Akun GitHub (Jika Belum Ada)

1. Buka: https://github.com/signup
2. Isi:
   - Email: email Anda
   - Password: password yang kuat
   - Username: pilih username (contoh: `nabildeveloper`)
3. Verify email
4. Login ke GitHub

### Step 3: Setup Git Config (Sekali Saja)

Buka Command Prompt dan jalankan:

```bash
# Set nama Anda
git config --global user.name "Nama Anda"

# Set email Anda (sama dengan email GitHub)
git config --global user.email "email@anda.com"

# Verify
git config --global user.name
git config --global user.email
```

**Contoh**:
```bash
git config --global user.name "Nabil Developer"
git config --global user.email "nabil@example.com"
```

---

## 🚀 Push ke GitHub (5 menit)

### Step 1: Buat Repository di GitHub

1. **Login** ke https://github.com
2. **Klik** tombol hijau "New" (atau ikon + di kanan atas → "New repository")
3. **Isi form**:
   - Repository name: `cryptomentor-bot`
   - Description: `AI-powered Telegram bot for crypto analysis`
   - Private atau Public: **Private** (recommended untuk bot dengan API keys)
   - ❌ **JANGAN** centang "Add a README file"
   - ❌ **JANGAN** centang "Add .gitignore"
   - ❌ **JANGAN** centang "Choose a license"
4. **Klik** "Create repository"

**Screenshot yang akan muncul**:
```
Quick setup — if you've done this kind of thing before
...or create a