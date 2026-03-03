# 🔧 Troubleshooting: Binance API Connection

## 🐛 Gejala Masalah

Bot tidak bisa mengambil data dari Binance:
- Command `/price` tidak menampilkan harga
- Command `/analyze` error
- Command `/ai` tidak dapat data market
- Error message: "Failed to fetch data"

---

## 🔍 Diagnosis

### Quick Test:
```bash
cd Bismillah
python quick_test_binance.py
```

### Full Diagnostic:
```bash
cd Bismillah
python fix_binance_connection.py
```

---

## ✅ Solusi Berdasarkan Error

### 1. Connection Timeout / Network Error

**Gejala:**
```
❌ Error: HTTPConnectionPool timeout
❌ Error: Connection refused
❌ Error: timed out
```

**Penyebab:**
- Internet connection bermasalah
- Firewall memblokir Binance
- Binance API down (jarang terjadi)

**Solusi:**
```bash
# Test koneksi internet
ping api.binance.com

# Jika blocked, coba:
# 1. Matikan firewall sementara
# 2. Gunakan VPN
# 3. Coba network lain
```

---

### 2. Rate Limiting (429 Error)

**Gejala:**
```
❌ Error: Rate limit exceeded
❌ Status code: 429
```

**Penyebab:**
- Terlalu banyak request dalam waktu singkat
- Bot melakukan scan terlalu cepat

**Solusi:**
Sudah diperbaiki dengan:
- Rate limiting (9 RPS)
- Exponential backoff
- Request throttling

**Jika masih terjadi:**
```python
# Edit di binance_provider.py
_rps = _RPS(rps=5.0)  # Kurangi dari 9.0 ke 5.0
```

---

### 3. Invalid Symbol (400 Error)

**Gejala:**
```
❌ Error: Symbol not found
❌ Status code: 400
❌ Error code: -1121
```

**Penyebab:**
- Symbol tidak ada di Binance
- Typo dalam symbol name

**Solusi:**
- Pastikan symbol benar (BTC, ETH, SOL, dll)
- Gunakan symbol yang ada di Binance
- Bot sudah auto-cache invalid symbols

---

### 4. Missing Dependencies

**Gejala:**
```
❌ ModuleNotFoundError: No module named 'httpx'
❌ ModuleNotFoundError: No module named 'requests'
```

**Solusi:**
```bash
pip install httpx requests
# atau
pip install -r requirements.txt
```

---

### 5. HTTP/2 Connection Error

**Gejala:**
```
❌ HTTP/2 connection failed
❌ ConnectError
```

**Solusi:**
Bot sudah auto-fallback ke HTTP/1.1

**Jika masih error:**
```python
# Edit di binance_provider.py
# Disable HTTP/2
http2_config = {
    "http2": False,  # Ubah dari True ke False
    ...
}
```

---

## 🚀 Optimasi yang Sudah Diterapkan

### 1. Multi-Protocol Support
- ✅ HTTP/2 (primary)
- ✅ HTTP/1.1 (fallback)
- ✅ Auto-switch on error

### 2. Rate Limiting
- ✅ 9 requests per second
- ✅ Token bucket algorithm
- ✅ Automatic throttling

### 3. Retry Mechanism
- ✅ 3 retries with exponential backoff
- ✅ Smart error detection
- ✅ Circuit breaker for invalid symbols

### 4. Header Rotation
- ✅ User-Agent rotation every 3-5 requests
- ✅ Multiple User-Agent variants
- ✅ Prevents 400 errors

### 5. Caching
- ✅ 5-minute cache for price data
- ✅ Invalid symbol cache
- ✅ Reduces API calls

### 6. Validation
- ✅ Price range validation
- ✅ NaN/Infinity checks
- ✅ Cross-validation with ticker data

---

## 🧪 Testing

### Test 1: Direct API
```bash
curl "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
```

**Expected:**
```json
{
  "symbol": "BTCUSDT",
  "lastPrice": "43250.00",
  "priceChangePercent": "2.50"
}
```

### Test 2: Python Script
```bash
python quick_test_binance.py
```

**Expected:**
```
✅ BTC Price: $43,250.00
✅ 24h Change: +2.50%
✅ Binance API is working!
```

### Test 3: Bot Command
```
/price BTC
```

**Expected:**
```
📊 Harga BTC (Binance)

💰 Saat ini: $43,250.00
📈 Perubahan 24j: +2.50% 📈
📊 Volume 24j: $28.5B
```

---

## 🔧 Manual Fixes

### Fix 1: Update Dependencies
```bash
pip install --upgrade httpx requests
```

### Fix 2: Clear Cache
```python
# Dalam bot, jalankan:
from crypto_api import CryptoAPI
api = CryptoAPI()
api._cache.clear()
```

### Fix 3: Reset HTTP Client
```python
# Restart bot untuk reset HTTP client
# Atau edit binance_provider.py:
_http = _HTTP()  # Recreate client
```

### Fix 4: Change Binance Endpoint
```python
# Edit .env file:
BINANCE_BASE_URL=https://api1.binance.com
# atau
BINANCE_BASE_URL=https://api2.binance.com
```

---

## 📊 Monitoring

### Check API Status:
```bash
# Binance API status
curl https://api.binance.com/api/v3/ping

# Expected: {}
```

### Check Bot Logs:
```bash
# Look for these messages:
✅ HTTP/2 + HTTP/1.1 ENABLED
✅ CryptoAPI initialized with Binance provider
```

### Check Error Logs:
```bash
# Look for:
❌ HTTP error after 3 retries
❌ Rate limit exceeded
❌ Symbol not found
```

---

## 🆘 Emergency Fallback

Jika Binance API benar-benar tidak bisa diakses:

### Option 1: Use VPN
```bash
# Install VPN
# Connect to server di negara yang tidak block Binance
# Restart bot
```

### Option 2: Use Proxy
```python
# Edit binance_provider.py
http2_config = {
    ...
    "proxies": {
        "http://": "http://proxy-server:port",
        "https://": "http://proxy-server:port"
    }
}
```

### Option 3: Alternative API
```python
# Bisa switch ke CoinGecko atau CoinMarketCap
# (Perlu modifikasi code)
```

---

## 📝 Checklist Troubleshooting

- [ ] Internet connection OK
- [ ] Binance API accessible (curl test)
- [ ] Dependencies installed (httpx, requests)
- [ ] No firewall blocking
- [ ] Bot logs show no errors
- [ ] Test script passes
- [ ] Bot commands work

---

## 💡 Tips

1. **Selalu test dengan script dulu** sebelum jalankan bot
2. **Monitor logs** untuk error patterns
3. **Jangan spam requests** - respect rate limits
4. **Use cache** - jangan force_refresh terlalu sering
5. **Keep dependencies updated**

---

## 🎯 Expected Behavior

### Normal Operation:
```
✅ HTTP/2 + HTTP/1.1 ENABLED
✅ CryptoAPI initialized
✅ BTC Price: $43,250.00
✅ Request successful (200)
```

### With Errors (Auto-Recovery):
```
⚠️  HTTP/2 failed, switching to HTTP/1.1
✅ Retry successful
✅ BTC Price: $43,250.00
```

---

## 📞 Support

Jika masih bermasalah setelah semua solusi dicoba:

1. Jalankan `python fix_binance_connection.py`
2. Screenshot error message
3. Check Binance status: https://www.binance.com/en/support/announcement
4. Coba dari network/device lain

---

**Bot sudah dioptimasi untuk handle berbagai error Binance API!** 🚀
