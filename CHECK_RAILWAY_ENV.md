# Check Railway Environment Variables

## 🔍 DIAGNOSIS RESULT

Test script menunjukkan environment variables **TIDAK DISET** di local development.

Ini **NORMAL** untuk local development, tapi **HARUS ADA** di Railway production.

## ✅ YANG HARUS ADA DI RAILWAY BOT

### Environment Variables yang Diperlukan:

```bash
# Automaton API (Conway)
CONWAY_API_URL=https://your-automaton.railway.app
CONWAY_API_KEY=your_api_key_here

# Centralized Wallet
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822
```

## 🔧 CARA CEK DI RAILWAY

### Step 1: Buka Railway Dashboard
1. Go to: https://railway.app/dashboard
2. Pilih project bot kamu
3. Klik tab "Variables"

### Step 2: Verify Variables Ada
Cek apakah ada:
- ✅ `CONWAY_API_URL`
- ✅ `CONWAY_API_KEY`
- ✅ `CENTRALIZED_WALLET_ADDRESS`

### Step 3: Verify Format Benar

**CONWAY_API_URL:**
```
✅ BENAR: https://automaton-production.railway.app
❌ SALAH: https://automaton-production.railway.app/  (ada trailing slash)
❌ SALAH: http://automaton-production.railway.app   (http bukan https)
```

**CONWAY_API_KEY:**
```
✅ BENAR: sk_live_abc123xyz...  (API key dari Automaton)
❌ SALAH: (kosong atau typo)
```

**CENTRALIZED_WALLET_ADDRESS:**
```
✅ BENAR: 0x63116672bef9f26fd906cd2a57550f7a13925822
❌ SALAH: 63116672bef9f26fd906cd2a57550f7a13925822  (missing 0x)
❌ SALAH: 0x6311...  (terlalu pendek, harus 42 chars)
```

## 🎯 KEMUNGKINAN MASALAH

### Masalah 1: Variables Tidak Ada
**Symptom**: "Automaton service offline"
**Solution**: Tambah variables di Railway dashboard

### Masalah 2: URL Salah
**Symptom**: Connection error, timeout
**Solution**: 
- Cek URL Automaton Railway yang benar
- Copy dari Automaton Railway dashboard
- Format: `https://[service-name].railway.app`

### Masalah 3: API Key Salah
**Symptom**: 401 Unauthorized, 403 Forbidden
**Solution**:
- Generate API key baru dari Automaton
- Update di Railway bot variables

### Masalah 4: Automaton Railway Down
**Symptom**: Connection refused, 503 Service Unavailable
**Solution**:
- Cek Automaton Railway deployment status
- Restart Automaton Railway jika perlu

## 📋 ACTION ITEMS

### 1. Cek Railway Bot Variables
```
Railway Dashboard → Bot Project → Variables
```

Pastikan ada:
- CONWAY_API_URL
- CONWAY_API_KEY  
- CENTRALIZED_WALLET_ADDRESS

### 2. Cek Automaton Railway Status
```
Railway Dashboard → Automaton Project → Deployments
```

Pastikan:
- Status: ✅ Active (bukan Crashed)
- Logs: No errors
- URL: Accessible

### 3. Test Manual dari Railway Logs

Setelah variables diset, cek Railway bot logs untuk:
```
✅ Conway API client initialized: https://...
✅ Health check passed
```

Atau error:
```
❌ Conway API health check failed: [error]
```

## 🚀 QUICK FIX

### Jika Variables Belum Ada:

1. **Get Automaton URL:**
   - Buka Automaton Railway project
   - Copy URL dari "Deployments" tab
   - Format: `https://automaton-xxx.railway.app`

2. **Get API Key:**
   - Jika belum punya, generate dari Automaton
   - Atau use existing key

3. **Add to Bot Railway:**
   ```
   CONWAY_API_URL=https://automaton-xxx.railway.app
   CONWAY_API_KEY=your_key_here
   CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822
   ```

4. **Redeploy Bot:**
   - Railway akan auto-redeploy setelah variables berubah
   - Atau manual trigger redeploy

5. **Test:**
   - Ketik `/automaton status` di bot
   - Seharusnya tidak ada "service offline" lagi

## 📝 NOTES

- Local development **TIDAK PERLU** variables ini (kecuali mau test)
- Production Railway **HARUS PUNYA** variables ini
- Setelah add/update variables, Railway auto-redeploy (~2-3 menit)

---

**Next Action**: Cek Railway dashboard dan verify variables ada dengan format yang benar
