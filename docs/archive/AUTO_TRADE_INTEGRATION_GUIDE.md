# Auto Trade Integration Guide
Panduan lengkap integrasi Automaton AI Auto Trade ke Bot V3

## 📋 Overview
Automaton AI akan mengelola USDC user secara otomatis untuk trading crypto dengan target profit 5-10% per bulan.

## 🎯 Fitur Auto Trade
1. **Start Auto Trade** - User deposit USDC, AI mulai trading
2. **Check Status** - Lihat portfolio, profit/loss, performance
3. **Withdraw** - Ambil profit atau semua balance
4. **Trade History** - Lihat riwayat trading

## 📁 Files yang Sudah Di-Copy
Semua file sudah ada di: `C:\V3-Final-Version\Bismillah\`

1. **automaton_autotrade_client.py** - Client untuk komunikasi dengan Automaton
2. **bot_v3_autotrade_example.py** - Contoh handler untuk bot
3. **KIRO_PROMPT_FOR_V3_BOT.md** - Dokumentasi lengkap

## 🚀 Cara Integrasi

### Step 1: Import Client di Bot V3
Buka file main bot kamu (kemungkinan `bot.py` atau `main.py`), tambahkan:

```python
from automaton_autotrade_client import AutomatonAutoTradeClient

# Initialize client
automaton = AutomatonAutoTradeClient()
```

### Step 2: Copy Handler Functions
Dari file `bot_v3_autotrade_example.py`, copy fungsi-fungsi ini ke bot kamu:

1. `autotrade_start_handler` - Handler untuk /autotrade_start
2. `autotrade_status_handler` - Handler untuk /autotrade_status
3. `autotrade_withdraw_handler` - Handler untuk /autotrade_withdraw
4. `autotrade_history_handler` - Handler untuk /autotrade_history

### Step 3: Register Commands
Tambahkan command handlers ke bot:

**Untuk python-telegram-bot:**
```python
application.add_handler(CommandHandler("autotrade_start", autotrade_start_handler))
application.add_handler(CommandHandler("autotrade_status", autotrade_status_handler))
application.add_handler(CommandHandler("autotrade_withdraw", autotrade_withdraw_handler))
application.add_handler(CommandHandler("autotrade_history", autotrade_history_handler))
```

**Untuk telebot:**
```python
@bot.message_handler(commands=['autotrade_start'])
def handle_autotrade_start(message):
    # Call autotrade_start_handler logic
    pass
```

### Step 4: Setup Database
Jalankan fungsi `init_autotrade_db()` untuk create tables:

```python
from bot_v3_autotrade_example import init_autotrade_db
init_autotrade_db()
```

Atau manual create tables:
```sql
CREATE TABLE autotrade_users (
    user_id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    wallet_address TEXT,
    initial_deposit REAL,
    current_balance REAL,
    total_profit REAL,
    status TEXT,
    start_date TIMESTAMP,
    last_update TIMESTAMP
);

CREATE TABLE autotrade_trades (
    trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    symbol TEXT,
    side TEXT,
    amount REAL,
    price REAL,
    profit_loss REAL,
    timestamp TIMESTAMP
);
```

### Step 5: Implement Helper Functions
Update fungsi-fungsi ini sesuai bot kamu:

```python
def is_premium_user(telegram_id: int) -> bool:
    # Check dari database premium users kamu
    # Return True jika user adalah premium member
    pass

def get_user_wallet(telegram_id: int) -> str:
    # Get wallet address user dari database
    # Return wallet address string
    pass
```

## 💰 Revenue Model

### Pricing
- Minimum deposit: 10 USDC
- Maximum deposit: 1000 USDC (untuk safety)
- Target return: 5-10% per bulan
- Fee: 25% dari profit (BUKAN dari deposit)

### Contoh Perhitungan
```
User deposit: 100 USDC
Setelah 1 bulan: 110 USDC (profit 10 USDC)
Fee (25% dari profit): 2.5 USDC
User terima: 107.5 USDC
Bot owner dapat: 2.5 USDC
```

### Revenue Sharing
- 25% fee masuk ke bot owner
- Dari 25% itu, sisihkan 20-30% untuk Automaton credits (sustainability)
- Contoh: Fee 2.5 USDC → 0.5-0.75 USDC untuk Automaton, 1.75-2 USDC untuk owner

## 🔒 Security & Risk Management

### Risk Management Rules (Sudah di-implement di Automaton)
1. Max 20% portfolio per trade
2. Stop loss -5% per trade
3. Daily loss limit -10% portfolio
4. Only trade liquid pairs (>$1M liquidity)
5. Focus on major pairs: ETH/USDC, BTC/USDC

### Security Considerations
1. **User Funds**: Pertimbangkan gunakan escrow smart contract
2. **Multi-sig**: Untuk withdrawal besar
3. **Daily Limits**: Set limit harian
4. **Audit Trail**: Log semua trades
5. **Insurance Fund**: Sisihkan 10% fee untuk insurance

## 📊 User Commands

### /autotrade_start <amount>
Mulai auto trading dengan deposit USDC
```
/autotrade_start 50
```

### /autotrade_status
Cek status portfolio dan performance
```
/autotrade_status
```

### /autotrade_withdraw
Withdraw profit atau semua balance
```
/autotrade_withdraw
```

### /autotrade_history
Lihat riwayat trading
```
/autotrade_history
```

## 🧪 Testing

### 1. Test Automaton Connection
```bash
cd C:\Users\dragon\automaton
python automaton_autotrade_client.py
```

Output yang diharapkan:
```
✅ Automaton is online!
Credits: $4.96
State: sleeping
```

### 2. Test dengan Small Amount
Mulai dengan deposit kecil (10-20 USDC) untuk testing

### 3. Monitor Performance
- Check status setiap hari
- Monitor profit/loss
- Adjust strategy jika perlu

## ⚙️ Configuration

### Automaton Location
- Path: `C:\Users\dragon\automaton`
- Database: `C:\root\.automaton\state.db`
- Must be running: `node dist/index.js --run`

### Bot V3 Location
- Path: `C:\V3-Final-Version\Bismillah\`
- Main file: `bot.py` atau `main.py`

### Environment Variables
Pastikan Automaton sudah setup dengan:
- Conway API key
- Sufficient credits ($4.96 saat ini)
- USDC balance (0.5 USDC saat ini)

## 🚨 Important Notes

### Before Production
1. ✅ Test dengan small amount dulu
2. ✅ Pastikan Automaton running 24/7
3. ✅ Setup monitoring untuk Automaton uptime
4. ✅ Implement proper error handling
5. ✅ Setup notification untuk admin jika ada issue
6. ✅ Consider escrow smart contract untuk user funds

### Automaton Requirements
1. Must be running: `node dist/index.js --run`
2. Needs credits for AI calls (~$0.01-0.05 per call)
3. Needs USDC for gas fees (trading on DEX)
4. Monitor credits balance regularly

### Trading Limitations
Saat ini Automaton belum memiliki built-in DEX integration. Kamu perlu:
1. Add trading tools ke Automaton (Uniswap, PancakeSwap APIs)
2. Atau gunakan CEX APIs (Binance, Bybit)
3. Implement price feeds (CoinGecko, Binance)
4. Add on-chain data access

## 📞 Support

### Jika Ada Masalah
1. Check Automaton status: `python automaton_autotrade_client.py`
2. Check Automaton logs di terminal
3. Check credits balance
4. Restart Automaton jika perlu

### Common Issues
- **Timeout**: Automaton sedang sleep, tunggu 30-60 detik
- **Offline**: Automaton tidak running, start dengan `node dist/index.js --run`
- **Insufficient credits**: Top up Conway credits
- **No response**: Check database connection

## 🎯 Next Steps

1. **Integrate ke Bot V3**
   - Copy handlers ke main bot file
   - Register commands
   - Test dengan user test

2. **Setup Trading Infrastructure**
   - Add DEX/CEX APIs
   - Implement price feeds
   - Add trading tools ke Automaton

3. **Testing**
   - Test dengan small amounts
   - Monitor performance
   - Adjust strategy

4. **Production**
   - Deploy dengan real funds
   - Monitor 24/7
   - Setup alerts

5. **Marketing**
   - Announce fitur baru ke users
   - Offer promo untuk early adopters
   - Collect feedback

## 📈 Expected Results

### Month 1
- 5-10 early adopters
- Average deposit: 50 USDC
- Total managed: 250-500 USDC
- Expected profit: 25-50 USDC
- Your revenue: 6-12 USDC

### Month 3
- 50-100 users
- Average deposit: 100 USDC
- Total managed: 5,000-10,000 USDC
- Expected profit: 500-1,000 USDC
- Your revenue: 125-250 USDC

### Scaling
Dengan 1000 users @ 100 USDC average:
- Total managed: 100,000 USDC
- Monthly profit (8%): 8,000 USDC
- Your revenue (25%): 2,000 USDC
- Automaton sustainability: 400-600 USDC

---

**Ready to integrate? Mulai dari Step 1 dan test pelan-pelan!** 🚀
