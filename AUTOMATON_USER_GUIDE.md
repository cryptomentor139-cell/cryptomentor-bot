# Panduan Pengguna: AI Agent (Automaton)

## Apa itu AI Agent?

AI Agent adalah agen trading otomatis yang dapat melakukan trading cryptocurrency secara mandiri 24/7. Agent Anda akan:

- 🤖 Trading otomatis tanpa perlu Anda online
- 📊 Menganalisis market secara real-time
- 💰 Menghasilkan profit dari trading
- ⚡ Menggunakan Conway Credits sebagai "bensin"

## Persyaratan

Untuk menggunakan fitur AI Agent, Anda memerlukan:

1. ✅ **Automaton Access** - Biaya satu kali Rp2.000.000
2. ✅ **Premium Subscription** - Langganan premium aktif
3. ✅ **100.000 Credits** - Untuk spawn agent pertama kali

## Cara Spawn Agent

### Langkah 1: Cek Persyaratan

Pastikan Anda memiliki:
- Automaton access (gunakan `/subscribe` untuk upgrade)
- Premium subscription aktif
- Minimal 100.000 credits

### Langkah 2: Spawn Agent

Kirim command:
```
/spawn_agent NamaAgent
```

Contoh:
```
/spawn_agent TradingBot1
```

### Langkah 3: Terima Deposit Address

Bot akan memberikan:
- ✅ Nama agent Anda
- ✅ Wallet address agent
- ✅ Deposit address untuk funding
- ✅ Biaya spawn: 100.000 credits

⚠️ **Penting:** Agent belum aktif sampai Anda deposit USDC!

## Cara Fund Agent (Deposit)

### Langkah 1: Lihat Deposit Address

Kirim command:
```
/deposit
```

Bot akan menampilkan:
- 📍 Deposit address Anda
- 📱 QR code untuk scan
- 🌐 Network yang didukung
- 💱 Conversion rate

### Langkah 2: Kirim USDC

**Network yang Didukung:**
- ✅ **Base** (Recommended - biaya gas rendah)
- ✅ Polygon
- ✅ Arbitrum

**Minimum Deposit:** 5 USDC

**Conversion Rate:**
- 1 USDC = 100 Conway Credits
- Platform fee: 2%
- Net: 1 USDC = 98 Conway Credits

### Langkah 3: Tunggu Konfirmasi

- ⏳ Deposit akan diproses setelah 12 block confirmations
- 📱 Anda akan menerima notifikasi Telegram
- ⚡ Credits akan ditambahkan otomatis

### Contoh Deposit

Jika Anda deposit **50 USDC**:
- Platform fee (2%): 1 USDC
- Net amount: 49 USDC
- Conway Credits: **4.900 credits**
- Runtime estimate: ~24 hari

## Cara Cek Status Agent

### Command: /agent_status

Menampilkan:
- 🤖 Nama agent
- 💰 Conway Credits balance
- 🟢 Survival tier (Normal/Low/Critical/Dead)
- ⏱️ Runtime estimate (hari)
- 📊 Total earnings
- 📊 Total expenses
- 📈 Net P&L (profit/loss)

### Survival Tiers

**🟢 Normal** (>= 10.000 credits)
- Full compute resources
- Optimal trading performance
- ~50 hari runtime

**🟡 Low Compute** (5.000 - 9.999 credits)
- Reduced compute resources
- Slower trading
- ~25 hari runtime

**🔴 Critical** (1.000 - 4.999 credits)
- Minimal resources
- Limited trading
- ~5 hari runtime

**⚫ Dead** (< 1.000 credits)
- Agent stopped
- No trading
- Perlu deposit untuk restart

## Cara Lihat Transaction History

### Command: /agent_logs

Menampilkan 20 transaksi terakhir:
- 💚 **EARN** - Profit dari trading
- ❤️ **SPEND** - Loss atau consumption
- 💙 **FUND** - Deposit yang Anda lakukan
- 💛 **PERFORMANCE_FEE** - Fee 20% dari profit

## Cara Cek Balance

### Command: /balance

Menampilkan:
- 💰 Conway Credits balance
- 🟢 Survival tier
- ⏱️ Runtime estimate
- 📍 Deposit address

## Notifikasi Otomatis

Anda akan menerima notifikasi untuk:

### ✅ Deposit Berhasil
```
✅ Deposit Berhasil!
💰 Jumlah: 50.00 USDC
⚡ Conway Credits: +4,900
```

### ⚠️ Saldo Rendah (< 5.000 credits)
```
⚠️ Peringatan: Saldo Rendah
🤖 Agent: TradingBot1
💰 Saldo: 4,500 credits
⏰ Runtime Tersisa: ~4.5 hari
```

### 🚨 Saldo Kritis (< 1.000 credits)
```
🚨 PERINGATAN KRITIS!
🤖 Agent: TradingBot1
💰 Saldo: 800 credits
⏰ Runtime: < 1 hari
⚠️ Agent Anda hampir mati!
```

### 💀 Agent Mati (0 credits)
```
💀 Agent Mati!
🤖 Agent: TradingBot1
💰 Saldo: 0 credits
📊 Status: DEAD
```

## Performance Fees

Platform mengambil **20% performance fee** dari profit trading Anda.

**Contoh:**
- Agent profit: 100 USDC
- Performance fee (20%): 20 USDC
- Your net profit: 80 USDC

**Catatan:**
- Fee hanya diambil dari **realized profit** (posisi yang sudah ditutup dengan profit)
- Tidak ada fee untuk loss
- Fee otomatis dikurangi dari Conway Credits agent

## Tips & Best Practices

### 💡 Deposit Strategy

**Untuk Runtime Optimal:**
- Deposit 50-100 USDC untuk 1-2 bulan runtime
- Jangan biarkan balance < 5.000 credits
- Set reminder untuk top-up sebelum critical

**Untuk Testing:**
- Mulai dengan 10-20 USDC
- Monitor performance selama 1 minggu
- Scale up jika profitable

### 📊 Monitoring

**Daily:**
- Cek `/agent_status` setiap hari
- Monitor net P&L
- Perhatikan survival tier

**Weekly:**
- Review `/agent_logs` untuk pattern
- Hitung ROI (Return on Investment)
- Adjust strategy jika perlu

### ⚠️ Risk Management

**Jangan:**
- ❌ Deposit lebih dari yang Anda mampu kehilangan
- ❌ Biarkan agent mati (0 credits)
- ❌ Ignore notifikasi low balance

**Lakukan:**
- ✅ Start small dan scale gradually
- ✅ Monitor performance regularly
- ✅ Top-up sebelum balance critical
- ✅ Diversify dengan multiple agents (jika profitable)

## FAQ

### Q: Berapa minimum deposit?
**A:** 5 USDC

### Q: Network mana yang paling murah?
**A:** Base network (biaya gas paling rendah)

### Q: Berapa lama deposit diproses?
**A:** ~5-10 menit (setelah 12 block confirmations)

### Q: Apakah agent bisa loss?
**A:** Ya, trading selalu ada risk. Monitor performance dan adjust strategy.

### Q: Bagaimana cara stop agent?
**A:** Biarkan balance habis (0 credits) atau contact admin.

### Q: Apakah bisa withdraw profit?
**A:** Fitur withdrawal akan tersedia soon. Saat ini profit tetap di agent untuk compound trading.

### Q: Berapa performance fee?
**A:** 20% dari realized profit (posisi yang sudah ditutup dengan profit)

### Q: Apakah bisa spawn multiple agents?
**A:** Ya, setiap spawn membutuhkan 100.000 credits.

### Q: Bagaimana cara refund jika agent tidak profitable?
**A:** Tidak ada refund. Trading adalah high-risk activity. Start small dan monitor performance.

### Q: Apakah agent trading 24/7?
**A:** Ya, selama balance > 0 credits.

## Troubleshooting

### Deposit Tidak Masuk

**Cek:**
1. Apakah Anda kirim ke address yang benar?
2. Apakah Anda kirim USDC (bukan token lain)?
3. Apakah Anda kirim di network yang benar (Base/Polygon/Arbitrum)?
4. Apakah amount >= 5 USDC?
5. Tunggu 12 block confirmations (~5-10 menit)

**Jika masih belum masuk:**
- Kirim transaction hash ke admin
- Admin akan investigate

### Agent Tidak Trading

**Cek:**
1. Apakah balance > 0 credits?
2. Apakah survival tier bukan "Dead"?
3. Cek `/agent_status` untuk detail

**Jika masih tidak trading:**
- Contact admin dengan agent ID

### Notifikasi Tidak Diterima

**Cek:**
1. Apakah Anda block bot?
2. Apakah Telegram notifications enabled?
3. Cek spam folder (jika ada)

## Support

Jika Anda mengalami masalah:

1. 📖 Baca FAQ di atas
2. 🔍 Cek `/agent_status` dan `/agent_logs`
3. 💬 Contact admin dengan detail:
   - User ID (gunakan `/id`)
   - Agent name
   - Screenshot error (jika ada)
   - Transaction hash (untuk deposit issues)

## Kesimpulan

AI Agent adalah fitur powerful untuk automated trading. Gunakan dengan bijak:

- ✅ Start small
- ✅ Monitor regularly
- ✅ Manage risk
- ✅ Top-up before critical
- ✅ Learn from performance

Selamat trading! 🚀

---

**Last Updated:** 2024
**Version:** 1.0
