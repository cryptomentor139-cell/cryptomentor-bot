# 🧪 Cara Test CryptoMentor AI

## 🚀 Quick Start

### 1. Start Bot
```bash
cd Bismillah
python main.py
```

### 2. Test di Telegram

Buka bot di Telegram: @Subridujdirdsjbot

#### Test 1: Analisis Market
```
/ai BTC
```
**Expected Result**:
- Bot akan reply "🤖 CryptoMentor AI sedang menganalisis BTC..."
- Tunggu 5-10 detik
- Akan muncul analisis lengkap dengan header:
  ```
  🤖 CRYPTOMENTOR AI ANALYSIS - BTC
  📊 Market Data: $95,000.50 (+3.50%)
  🕐 Analysis Time: 14:30:25 WIB
  ---
  [Analisis lengkap dari AI]
  ```

#### Test 2: Chat dengan AI
```
/chat gimana kondisi market hari ini?
```
**Expected Result**:
- Bot akan reply dengan analisis dari CryptoMentor AI
- Response dimulai dengan "🤖 **CryptoMentor AI**:"
- Berisi jawaban lengkap tentang kondisi market

#### Test 3: Market Summary
```
/aimarket
```
**Expected Result**:
- Bot akan analyze top 10 coins
- Memberikan overview kondisi market global
- Branded sebagai CryptoMentor AI

#### Test 4: Via Menu
1. Klik tombol "🤖 Ask AI"
2. Akan muncul 4 pilihan:
   - 💬 Chat dengan AI
   - 📊 Analisis Market AI
   - 🌍 Market Summary AI
   - 📖 Panduan AI

3. Klik "📊 Analisis Market AI"
4. Bot akan minta symbol: "Masukkan symbol crypto (contoh: BTC, ETH, SOL)"
5. Ketik: `BTC`
6. Akan muncul analisis lengkap

## ✅ Checklist Verification

Saat testing, pastikan:

- [ ] Tidak ada error "Insufficient data: 0 candles"
- [ ] Tidak ada mention "DeepSeek" ke user
- [ ] Semua response branded "CryptoMentor AI"
- [ ] AI memberikan analisis lengkap (bukan placeholder)
- [ ] Response time 5-10 detik (reasonable)
- [ ] Menu "Ask AI" menampilkan 4 pilihan
- [ ] Semua command (/ai, /chat, /aimarket) berfungsi

## 🐛 Troubleshooting

### Error: "CryptoMentor AI tidak tersedia"
**Cause**: API key tidak terdeteksi
**Fix**: 
```bash
# Check .env file
cat .env | grep DEEPSEEK_API_KEY

# Should show:
# DEEPSEEK_API_KEY=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
```

### Error: "Failed to get market data"
**Cause**: Binance API connection issue
**Fix**:
```bash
# Test Binance connection
python test_binance_api.py
```

### Error: "Insufficient data: 0 candles"
**Cause**: Old code masih dipanggil
**Fix**: 
- Restart bot (Ctrl+C, then `python main.py`)
- Pastikan `analyze_market_simple()` dipanggil, bukan `analyze_market_with_reasoning()`

### Bot tidak merespon
**Cause**: Bot sudah running di server
**Fix**: 
- Hanya bisa 1 instance bot dengan token yang sama
- Stop bot di server dulu, atau test di server langsung

## 📊 Expected Behavior

### Successful AI Analysis Response:
```
🤖 CRYPTOMENTOR AI ANALYSIS - BTC
📊 Market Data: $95,234.50 (+2.35%)
🕐 Analysis Time: 14:30:25 WIB

---

Berdasarkan data market saat ini, Bitcoin (BTC) menunjukkan 
kondisi BULLISH dengan pergerakan positif 2.35% dalam 24 jam 
terakhir...

[Analisis lengkap dengan reasoning, level support/resistance,
risk/opportunity, dan rekomendasi trading]

⚠️ Disclaimer: Trading cryptocurrency memiliki risiko tinggi...
```

### Successful Chat Response:
```
🤖 **CryptoMentor AI**:

Kondisi market crypto hari ini cukup positif! Bitcoin dan 
Ethereum menunjukkan pergerakan bullish dengan volume yang 
sehat...

[Analisis lengkap dengan insight dan rekomendasi]
```

## 🎯 Success Criteria

AI dianggap berfungsi dengan baik jika:

1. ✅ Response time < 15 detik
2. ✅ Tidak ada error message
3. ✅ Analisis lengkap dan relevan
4. ✅ Branded sebagai "CryptoMentor AI"
5. ✅ Tidak mention "DeepSeek" sama sekali
6. ✅ Memberikan reasoning yang jelas
7. ✅ Include risk management advice

## 📞 Support

Jika masih ada masalah:

1. Check logs di terminal
2. Run test scripts:
   ```bash
   python quick_test_ai.py
   python test_binance_api.py
   ```
3. Verify .env configuration
4. Restart bot

---

**Last Updated**: 2026-02-15
**Status**: Ready for Testing
