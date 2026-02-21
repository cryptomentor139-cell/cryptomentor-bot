# 🤖 Cara Pakai Automaton AI - Panduan Lengkap

## 📌 Apa itu Automaton AI?

Automaton AI adalah fitur premium yang memberikan trading signals yang dianalisis oleh AI. Fitur ini terintegrasi dengan Automaton dashboard dan memberikan rekomendasi entry, stop loss, dan take profit.

## ✅ Syarat Menggunakan

### 1. Premium Subscription
- Harus berlangganan premium
- Gunakan `/subscribe` untuk upgrade

### 2. Automaton Access
- Biaya one-time: Rp2.000.000
- Akses seumur hidup
- Gunakan `/subscribe` untuk beli

### 3. Automaton Dashboard Running
- Dashboard harus running di server
- Admin yang handle ini

## 🎯 Command yang Tersedia

### 1. `/ai_signal` - Dapatkan AI Signal

**Format:**
```
/ai_signal <symbol> [timeframe]
```

**Contoh:**
```
/ai_signal BTCUSDT
/ai_signal ETHUSDT 4h
/ai_signal BNBUSDT 1d
```

**Timeframe yang didukung:**
- `1m` - 1 menit
- `5m` - 5 menit
- `15m` - 15 menit
- `1h` - 1 jam (default)
- `4h` - 4 jam
- `1d` - 1 hari

**Response yang didapat:**
```
🤖 AI Trading Signal

📊 Symbol: BTCUSDT
⏰ Timeframe: 1h

🟢 Trend: BULLISH
💰 Entry: 45,250
🛑 Stop Loss: 44,800
🎯 Take Profit:
   TP1: 45,800
   TP2: 46,200
   TP3: 46,800
📈 Risk/Reward: 1:3.2
🎲 Confidence: 85%

📝 Analysis:
Bitcoin menunjukkan momentum bullish yang kuat...

⚠️ Disclaimer: AI signal adalah referensi. DYOR!
```

### 2. `/ai_status` - Cek Status AI

**Format:**
```
/ai_status
```

**Response:**
```
🟢 Automaton AI Status

Status: ONLINE
Total Turns: 1,234
Last Activity: 2026-02-22 10:30:00

✅ AI ready untuk memberikan trading signals!
```

## 📊 Rate Limit

### Batasan Penggunaan

- **10 AI signals per jam**
- Setelah 10 request, harus tunggu 1 jam
- Rate limit reset otomatis setiap jam

**Contoh:**
```
Request 1-10: ✅ Berhasil
Request 11: ❌ Rate limit exceeded!

⏱️ Rate limit exceeded!

You can only request 10 AI signals per hour.
Please wait 45 minutes before requesting another signal.
```

## 🚀 Cara Menggunakan (Step by Step)

### Step 1: Pastikan Premium & Automaton Access

```
/subscribe
```

Pilih paket yang sesuai:
- Premium: Rp50.000/bulan
- Automaton Access: Rp2.000.000 (one-time)

### Step 2: Cek Status AI

```
/ai_status
```

Pastikan status: `ONLINE`

### Step 3: Request AI Signal

```
/ai_signal BTCUSDT
```

Tunggu 30-60 detik untuk response.

### Step 4: Analisis Signal

Perhatikan:
- **Trend:** Arah market (bullish/bearish/neutral)
- **Entry:** Harga masuk yang disarankan
- **Stop Loss:** Batas kerugian
- **Take Profit:** Target profit (3 level)
- **Risk/Reward:** Rasio risk vs reward
- **Confidence:** Tingkat keyakinan AI (0-100%)

### Step 5: Ambil Keputusan

⚠️ **PENTING:**
- AI signal adalah REFERENSI, bukan perintah
- Selalu lakukan riset sendiri (DYOR)
- Gunakan risk management yang baik
- Jangan invest lebih dari yang bisa Anda rugikan

## 💡 Tips Menggunakan AI Signal

### 1. Kombinasikan dengan Analisis Sendiri

Jangan hanya bergantung pada AI:
- Cek chart sendiri
- Lihat news & fundamental
- Perhatikan volume trading
- Cek support & resistance

### 2. Gunakan Multiple Timeframes

Request signal di berbagai timeframe:
```
/ai_signal BTCUSDT 1h   # Short term
/ai_signal BTCUSDT 4h   # Medium term
/ai_signal BTCUSDT 1d   # Long term
```

### 3. Perhatikan Confidence Level

- **80-100%:** High confidence, signal kuat
- **60-79%:** Medium confidence, hati-hati
- **0-59%:** Low confidence, skip atau tunggu

### 4. Gunakan Stop Loss

SELALU pasang stop loss sesuai rekomendasi AI:
- Proteksi dari kerugian besar
- Disiplin trading
- Risk management

### 5. Take Profit Bertahap

Gunakan 3 level TP:
- TP1: Ambil 30% profit
- TP2: Ambil 40% profit
- TP3: Ambil 30% profit (atau trailing stop)

## 🎯 Contoh Penggunaan Real

### Scenario 1: Scalping (1m - 5m)

```
/ai_signal BTCUSDT 1m
```

**Use case:**
- Quick trades (5-15 menit)
- Small profit targets (0.5-1%)
- Tight stop loss

### Scenario 2: Day Trading (15m - 1h)

```
/ai_signal ETHUSDT 1h
```

**Use case:**
- Intraday trades (beberapa jam)
- Medium profit targets (2-5%)
- Moderate stop loss

### Scenario 3: Swing Trading (4h - 1d)

```
/ai_signal BNBUSDT 1d
```

**Use case:**
- Multi-day trades (beberapa hari)
- Large profit targets (5-15%)
- Wide stop loss

## ⚠️ Error Messages & Solutions

### Error 1: "Premium Required"

**Pesan:**
```
❌ Premium Required

AI Signal adalah fitur premium.

Gunakan /subscribe untuk upgrade ke premium.
```

**Solusi:**
```
/subscribe
```
Pilih paket premium.

### Error 2: "Automaton Access Required"

**Pesan:**
```
❌ Automaton Access Required

Untuk menggunakan AI Signal, Anda perlu Automaton access.

Biaya: Rp2.000.000 (one-time)
Gunakan /subscribe untuk upgrade.
```

**Solusi:**
```
/subscribe
```
Pilih Automaton Access.

### Error 3: "Rate limit exceeded"

**Pesan:**
```
⏱️ Rate limit exceeded!

You can only request 10 AI signals per hour.
Please wait 45 minutes before requesting another signal.
```

**Solusi:**
Tunggu sampai rate limit reset (1 jam dari request pertama).

### Error 4: "Automaton AI Offline"

**Pesan:**
```
❌ Automaton AI Offline

Automaton AI sedang tidak tersedia.
```

**Solusi:**
Hubungi admin. Dashboard perlu di-restart.

## 📈 Tracking Performance

### Catat Setiap Signal

Buat spreadsheet untuk tracking:

| Date | Symbol | Timeframe | Entry | SL | TP | Result | Profit/Loss |
|------|--------|-----------|-------|----|----|--------|-------------|
| 2026-02-22 | BTCUSDT | 1h | 45,250 | 44,800 | 45,800 | ✅ Hit TP1 | +1.2% |
| 2026-02-22 | ETHUSDT | 4h | 2,850 | 2,820 | 2,920 | ❌ Hit SL | -1.0% |

### Hitung Win Rate

```
Win Rate = (Winning Trades / Total Trades) × 100%

Contoh:
- Total trades: 20
- Winning trades: 14
- Win rate: 70%
```

### Evaluasi Bulanan

Setiap bulan, evaluasi:
- Total profit/loss
- Win rate
- Average risk/reward
- Best performing timeframe
- Best performing symbols

## 🔐 Security & Privacy

### Data yang Disimpan

Bot menyimpan:
- User ID
- Timestamp request
- Symbol & timeframe
- Activity log

### Data yang TIDAK Disimpan

Bot TIDAK menyimpan:
- Trading decisions Anda
- Profit/loss Anda
- Portfolio Anda
- Private keys

### Privacy

- AI signal hanya dikirim ke Anda
- Tidak ada sharing signal ke user lain
- Activity log hanya untuk admin monitoring

## 📞 Support

### Butuh Bantuan?

1. **Cek dokumentasi ini dulu**
2. **Coba `/ai_status` untuk cek AI**
3. **Hubungi admin jika masih error**

### Report Bug

Jika menemukan bug:
1. Screenshot error message
2. Catat command yang digunakan
3. Kirim ke admin

## ✅ Checklist Sebelum Trading

Sebelum execute trade berdasarkan AI signal:

- [ ] Sudah cek chart sendiri
- [ ] Sudah baca news terkait
- [ ] Sudah set stop loss
- [ ] Sudah hitung risk (max 2-5% per trade)
- [ ] Sudah siap mental jika loss
- [ ] Sudah punya exit plan

## 🎓 Learning Resources

### Recommended Reading

1. **Technical Analysis Basics**
   - Support & Resistance
   - Trend lines
   - Candlestick patterns

2. **Risk Management**
   - Position sizing
   - Stop loss placement
   - Portfolio diversification

3. **Trading Psychology**
   - Emotional control
   - Discipline
   - Patience

### Practice First

Sebelum trading real money:
1. Paper trading dulu (simulasi)
2. Test AI signals di demo account
3. Track performance minimal 1 bulan
4. Baru trading dengan uang kecil

## 🎉 Success Stories

### User Testimonial (Example)

> "Saya pakai AI signal untuk day trading. Win rate saya naik dari 55% jadi 70%. Yang penting tetap DYOR dan pakai risk management!" - User A

> "AI signal bagus untuk konfirmasi analisis saya. Kalau AI dan analisis saya sama, confidence lebih tinggi untuk execute." - User B

## 📊 Statistics (Example)

**AI Signal Performance (Last 30 Days):**
- Total signals: 500
- Win rate: 68%
- Average R:R: 1:2.5
- Best timeframe: 1h (72% win rate)
- Best symbol: BTCUSDT (75% win rate)

*Note: Past performance tidak guarantee future results*

## 🚀 Next Steps

1. **Upgrade ke Premium + Automaton Access**
   ```
   /subscribe
   ```

2. **Test AI Signal**
   ```
   /ai_signal BTCUSDT
   ```

3. **Start Small**
   - Trade dengan amount kecil dulu
   - Test 10-20 signals
   - Evaluate performance

4. **Scale Up**
   - Jika profitable, increase position size
   - Tetap maintain risk management
   - Keep learning & improving

---

**Disclaimer:** Trading crypto berisiko tinggi. AI signal adalah tools bantu, bukan jaminan profit. Selalu DYOR dan trade dengan bijak.

**Last Updated:** 2026-02-22
**Version:** 1.0.0
