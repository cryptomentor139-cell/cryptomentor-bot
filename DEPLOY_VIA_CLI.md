# 🚀 Deploy via Railway CLI - Solusi Pasti!

## Masalah
Railway tidak auto-deploy setelah GitHub connected dan push.

## Solusi: Railway CLI
Deploy langsung dari komputer Anda menggunakan Railway CLI.

## Langkah 1: Install Railway CLI (1 menit)

### Windows (PowerShell):
```powershell
npm install -g @railway/cli
```

Atau jika npm belum ada, download installer:
https://docs.railway.app/guides/cli#installation

## Langkah 2: Login ke Railway (30 detik)

```bash
railway login
```

Ini akan buka browser untuk login. Login dengan akun Railway Anda.

## Langkah 3: Link ke Project (30 detik)

```bash
cd Bismillah
railway link
```

Pilih:
- Project: **industrious-dream**
- Environment: **production**

## Langkah 4: Deploy! (2 menit)

```bash
railway up
```

Railway akan:
1. Upload code dari folder lokal
2. Build aplikasi
3. Deploy ke production
4. Show logs real-time

## Langkah 5: Cek Logs

Setelah deploy selesai:
```bash
railway logs
```

Harus muncul:
```
🚀 Starting CryptoMentor AI Bot...
✅ Bot initialized with 2 admin(s)
...
🚀 CryptoMentor AI Bot is running...
🔄 Polling for updates...
```

## Langkah 6: Test Bot

Telegram → `/start`

## Commands Berguna

```bash
# Cek status
railway status

# Cek logs (follow mode)
railway logs --follow

# Cek environment variables
railway variables

# Redeploy
railway up

# Open dashboard
railway open
```

## Troubleshooting

### Error: "npm not found"
Install Node.js dulu: https://nodejs.org/

### Error: "railway not found"
Restart terminal setelah install.

### Error: "Not linked to project"
Run `railway link` lagi.

## Keuntungan Railway CLI

- ✅ Deploy langsung dari komputer
- ✅ Tidak perlu tunggu GitHub webhook
- ✅ Lihat logs real-time
- ✅ Lebih cepat (skip GitHub)
- ✅ Lebih reliable

## Estimasi Waktu

- Install CLI: 1 menit
- Login & Link: 1 menit
- Deploy: 2 menit
- **Total: 4 menit**

---

**MULAI SEKARANG:**
```bash
npm install -g @railway/cli
railway login
cd Bismillah
railway link
railway up
```
