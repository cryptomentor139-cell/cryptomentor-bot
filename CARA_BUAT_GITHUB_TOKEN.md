# 🔐 Cara Membuat GitHub Personal Access Token

## 🎯 Apa itu Personal Access Token (PAT)?

Personal Access Token adalah "password khusus" yang digunakan untuk akses GitHub dari command line (Git).

**⚠️ PENTING**: 
- **JANGAN gunakan password GitHub** saat git push!
- Gunakan **Personal Access Token** sebagai password
- Token lebih aman dan bisa di-revoke kapan saja

---

## 📋 Step-by-Step Membuat Token (5 Menit)

### Step 1: Buka GitHub Settings

1. Login ke GitHub: https://github.com
2. Klik foto profil Anda (pojok kanan atas)
3. Klik **"Settings"**

### Step 2: Masuk ke Developer Settings

1. Scroll ke bawah di sidebar kiri
2. Klik **"Developer settings"** (paling bawah)
3. Klik **"Personal access tokens"**
4. Klik **"Tokens (classic)"**

**Direct link**: https://github.com/settings/tokens

### Step 3: Generate New Token

1. Klik tombol **"Generate new token"**
2. Pilih **"Generate new token (classic)"**

### Step 4: Configure Token

#### A. Note (Nama Token)
```
CryptoMentor Bot Deploy
```
Atau nama lain yang mudah diingat.

#### B. Expiration (Masa Berlaku)
Pilih salah satu:
- **30 days** - Token berlaku 30 hari
- **60 days** - Token berlaku 60 hari
- **90 days** - Token berlaku 90 hari (recommended)
- **No expiration** - Token tidak pernah expire (tidak recommended)

**Recommended**: `90 days`

#### C. Select Scopes (Permissions)

**PENTING**: Centang ✅ **`repo`** (full control of private repositories)

Ini akan otomatis centang semua sub-permissions:
- ✅ repo:status
- ✅ repo_deployment
- ✅ public_repo
- ✅ repo:invite
- ✅ security_events

**Jangan centang yang lain**, cukup `repo` saja!

### Step 5: Generate Token

1. Scroll ke bawah
2. Klik tombol hijau **"Generate token"**

### Step 6: Copy Token

**⚠️ SANGAT PENTING!**

Setelah token dibuat, Anda akan melihat token seperti ini:

```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**COPY TOKEN INI SEKARANG!**

Token format:
- Dimulai dengan `ghp_`
- Panjang ~40 karakter
- Contoh: `ghp_1A2b3C4d5E6f7G8h9I0jK1L2M3N4O5P6Q7R8S9T0`

**⚠️ Token hanya muncul SEKALI!**
- Setelah Anda close halaman ini, token tidak akan muncul lagi
- Jika lupa, harus buat token baru

### Step 7: Simpan Token

**Simpan token di tempat yang aman**:

1. **Notepad** (sementara)
2. **Password Manager** (recommended)
3. **File .txt** di komputer (jangan share!)

**JANGAN**:
- ❌ Share token ke orang lain
- ❌ Commit token ke GitHub
- ❌ Post token di forum/chat

---

## 🔧 Cara Menggunakan Token

### Saat Git Push

Ketika Anda jalankan:
```powershell
git push -u origin main
```

Git akan minta credentials:

```
Username for 'https://github.com': 
```
**Ketik**: GitHub username Anda (contoh: `nabilfarrel`)

```
Password for 'https://nabilfarrel@github.com':
```
**Paste**: Personal Access Token Anda (bukan password GitHub!)

**Contoh**:
```
Username: nabilfarrel
Password: ghp_1A2b3C4d5E6f7G8h9I0jK1L2M3N4O5P6Q7R8S9T0
```

✅ Push berhasil!

---

## 💾 Simpan Credentials (Optional)

Agar tidak perlu input token setiap kali push:

```powershell
# Enable credential helper
git config --global credential.helper wincred
```

Setelah ini, Git akan menyimpan token Anda di Windows Credential Manager.

**Next push**: Tidak perlu input token lagi! 🎉

---

## 🔄 Token Expired? Buat Token Baru

Jika token sudah expired (90 hari):

### Option 1: Regenerate Token

1. https://github.com/settings/tokens
2. Cari token lama Anda
3. Klik **"Regenerate token"**
4. Copy token baru
5. Update di Git credential

### Option 2: Buat Token Baru

1. https://github.com/settings/tokens
2. Klik **"Generate new token (classic)"**
3. Ulangi Step 4-7 di atas

---

## 🗑️ Revoke Token (Jika Perlu)

Jika token ter-leak atau tidak digunakan lagi:

1. https://github.com/settings/tokens
2. Cari token yang ingin di-revoke
3. Klik **"Delete"** atau **"Revoke"**
4. Confirm

Token langsung tidak bisa digunakan lagi.

---

## 🐛 Troubleshooting

### Error: "Authentication failed"

**Penyebab**:
- Token salah
- Token expired
- Token tidak punya permission `repo`

**Solusi**:
1. Buat token baru dengan permission `repo`
2. Copy token dengan benar (jangan ada spasi)
3. Paste saat diminta password

### Error: "remote: Permission denied"

**Penyebab**:
- Token tidak punya permission `repo`
- Repository URL salah

**Solusi**:
1. Buat token baru dengan centang ✅ `repo`
2. Verify repository URL:
   ```powershell
   git remote -v
   ```

### Lupa Token

**Solusi**:
- Buat token baru (token lama tidak bisa dilihat lagi)
- Ikuti Step 1-7 di atas

---

## 📋 Checklist

- [ ] Buka https://github.com/settings/tokens
- [ ] Generate new token (classic)
- [ ] Note: `CryptoMentor Bot Deploy`
- [ ] Expiration: `90 days`
- [ ] Centang ✅ `repo`
- [ ] Generate token
- [ ] Copy token (format: `ghp_xxxxx...`)
- [ ] Simpan token di tempat aman
- [ ] Gunakan token sebagai password saat git push

---

## 🎯 Quick Reference

### Generate Token:
```
https://github.com/settings/tokens
→ Generate new token (classic)
→ Note: CryptoMentor Bot Deploy
→ Expiration: 90 days
→ Select: ✅ repo
→ Generate token
→ Copy token
```

### Use Token:
```powershell
git push -u origin main

Username: YOUR_GITHUB_USERNAME
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Save Credentials:
```powershell
git config --global credential.helper wincred
```

---

## 🔐 Security Tips

1. **Jangan share token** ke siapa pun
2. **Jangan commit token** ke repository
3. **Gunakan expiration** (90 days recommended)
4. **Revoke token** jika tidak digunakan lagi
5. **Simpan token** di password manager

---

## ✅ Summary

**Personal Access Token** adalah password khusus untuk Git:
- Lebih aman dari password GitHub
- Bisa di-revoke kapan saja
- Punya expiration date
- Digunakan sebagai password saat git push

**Format**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Permission**: ✅ `repo` (full control of private repositories)

---

**Date**: 2026-02-15
**Status**: ✅ READY TO USE

**Selamat Membuat Token!** 🔐
