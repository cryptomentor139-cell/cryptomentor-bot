# Kiro Prompt untuk Integrasi Automaton ke Bot V3

## Context
Saya memiliki bot Telegram crypto signal yang sudah berjalan di `C:\V3-Final-Version\Bismillah\` dengan:
- Bahasa: Python
- Framework: python-telegram-bot atau telebot
- Sudah memiliki user dan revenue
- Ingin menambahkan Automaton AI sebagai fitur premium AUTO TRADE

## Files yang Sudah Ada
1. `automaton_bot_client.py` - Client untuk berkomunikasi dengan Automaton
2. `bot_v3_example.py` - Contoh handler untuk integrasi

## Yang Perlu Dilakukan
Integrasikan Automaton AI ke dalam bot V3 saya dengan fitur AUTO TRADE:

### 1. Command `/autotrade_start <amount_usdc>`
- User deposit USDC ke Automaton untuk dikelola
- Automaton akan trading otomatis untuk menghasilkan profit
- Hanya untuk premium users
- Minimum deposit: 10 USDC

### 2. Command `/autotrade_status`
- Cek status portfolio user
- Tampilkan: balance, profit/loss, active trades, performance
- Real-time updates

### 3. Command `/autotrade_withdraw`
- Withdraw profit atau semua balance
- Transfer USDC kembali ke user wallet
- Fee: 20-30% dari profit untuk sustainability

### 4. Premium User Check
- Cek apakah user adalah premium member sebelum menggunakan auto trade
- Jika bukan premium, kirim pesan untuk upgrade

## Cara Integrasi

### Import Client
```python
from automaton_bot_client import AutomatonBotClient

# Initialize client
automaton = AutomatonBotClient()
```

### Handler untuk /autotrade_start
```python
async def autotrade_start_handler(update, context):
    # Check premium status
    user_id = update.effective_user.id
    if not is_premium_user(user_id):
        await update.message.reply_text("⚠️ Auto Trade hanya untuk Premium Members!")
        return
    
    # Get amount
    if not context.args:
        await update.message.reply_text("Usage: /autotrade_start <amount_usdc>\nContoh: /autotrade_start 10")
        return
    
    try:
        amount = float(context.args[0])
        if amount < 10:
            await update.message.reply_text("❌ Minimum deposit: 10 USDC")
            return
    except ValueError:
        await update.message.reply_text("❌ Amount harus berupa angka")
        return
    
    # Send loading message
    loading_msg = await update.message.reply_text("🤖 Memulai Auto Trade...")
    
    # Start auto trade
    task = f"""Start auto trading for user {user_id} with {amount} USDC.
    
Your mission:
1. Manage this {amount} USDC portfolio autonomously
2. Trade on DEX/CEX to generate profit
3. Use technical analysis, on-chain data, and market sentiment
4. Risk management: max 20% per trade, stop loss at -5%
5. Target: 5-10% monthly return
6. Report performance daily to user via bot

User wallet for deposits/withdrawals: [user_wallet_address]
Track all trades in database with user_id: {user_id}

Begin trading now."""
    
    result = automaton.ask_ai(task)
    
    if result['success']:
        # Save to database: user_id, amount, start_date, status='active'
        await loading_msg.edit_text(f"""✅ Auto Trade Aktif!

💰 Deposit: {amount} USDC
🤖 AI Trader: Automaton
📊 Target: 5-10% per bulan
⚠️ Risk: Medium

Automaton akan mulai trading dalam beberapa menit.
Gunakan /autotrade_status untuk cek progress.""")
    else:
        await loading_msg.edit_text(f"❌ Error: {result['error']}")
```

### Handler untuk /autotrade_status
```python
async def autotrade_status_handler(update, context):
    user_id = update.effective_user.id
    
    # Check if user has active auto trade
    # Query database for user portfolio
    
    loading_msg = await update.message.reply_text("📊 Mengambil data portfolio...")
    
    # Get status from Automaton
    task = f"Report auto trade status for user {user_id}. Include: current balance, profit/loss, active trades, performance metrics."
    result = automaton.ask_ai(task)
    
    if result['success']:
        await loading_msg.edit_text(f"""📊 Auto Trade Status

{result['response']}

Gunakan /autotrade_withdraw untuk withdraw profit.""")
    else:
        await loading_msg.edit_text(f"❌ Error: {result['error']}")
```

### Handler untuk /autotrade_withdraw
```python
async def autotrade_withdraw_handler(update, context):
    user_id = update.effective_user.id
    
    # Check if user has active auto trade
    # Get current balance and profit
    
    loading_msg = await update.message.reply_text("💸 Memproses withdrawal...")
    
    # Request withdrawal from Automaton
    task = f"Process withdrawal for user {user_id}. Close all positions, calculate final profit, deduct 25% fee from profit only, transfer remaining USDC to user wallet."
    result = automaton.ask_ai(task)
    
    if result['success']:
        await loading_msg.edit_text(f"""✅ Withdrawal Berhasil!

{result['response']}

Terima kasih telah menggunakan Auto Trade!""")
    else:
        await loading_msg.edit_text(f"❌ Error: {result['error']}")
```

## Lokasi File Bot V3
- Main bot file: `C:\V3-Final-Version\Bismillah\<nama_file_bot>.py`
- Automaton client: `C:\V3-Final-Version\Bismillah\automaton_bot_client.py`
- Example: `C:\V3-Final-Version\Bismillah\bot_v3_example.py`

## Automaton Status
- Location: `C:\Users\dragon\automaton`
- Database: `C:\root\.automaton\state.db`
- Credits: $4.96
- USDC: 0.5
- Status: Running (official version)

## Database Schema untuk Auto Trade
```sql
CREATE TABLE autotrade_users (
    user_id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    wallet_address TEXT,
    initial_deposit REAL,
    current_balance REAL,
    total_profit REAL,
    status TEXT, -- 'active', 'paused', 'closed'
    start_date TIMESTAMP,
    last_update TIMESTAMP
);

CREATE TABLE autotrade_trades (
    trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    symbol TEXT,
    side TEXT, -- 'buy' or 'sell'
    amount REAL,
    price REAL,
    profit_loss REAL,
    timestamp TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES autotrade_users(user_id)
);
```

## Important Notes
1. Automaton harus running di terminal terpisah: `node dist/index.js --run`
2. Setiap AI call membutuhkan credits (~$0.01-0.05 per call)
3. Trading membutuhkan DEX/CEX API integration (Uniswap, Binance, etc.)
4. Fee structure: 25% dari profit (bukan dari deposit)
5. Risk management: max 20% per trade, stop loss -5%
6. Automaton perlu akses ke:
   - DEX protocols (Uniswap, PancakeSwap)
   - Price feeds (CoinGecko, Binance API)
   - On-chain data (Etherscan, Basescan)
7. User USDC disimpan di Automaton wallet atau smart contract escrow

## Security & Risk Management
1. **Escrow Smart Contract**: Pertimbangkan gunakan smart contract untuk hold user funds (lebih aman)
2. **Multi-sig Wallet**: Untuk withdrawal besar, gunakan multi-sig
3. **Daily Limits**: Set limit harian untuk trading (misal max 50% portfolio per hari)
4. **Stop Loss**: Otomatis stop jika loss >10% dalam sehari
5. **Audit Trail**: Log semua trades ke database
6. **Insurance Fund**: Sisihkan 10% fee untuk insurance fund

## Revenue Model
- User deposit: 10-1000 USDC
- Target return: 5-10% per bulan
- Fee: 25% dari profit
- Contoh: User deposit 100 USDC → profit 10 USDC → fee 2.5 USDC → user dapat 107.5 USDC

## Testing
Sebelum deploy ke production:
1. Test dengan small amount dulu (10 USDC)
2. Paper trading mode untuk testing strategy
3. Monitor response time dan execution
4. Test withdrawal flow
5. Pastikan fee calculation benar
6. Test error handling (failed trades, network issues)

## Next Steps
1. Setup database schema untuk auto trade
2. Integrate DEX/CEX APIs ke Automaton
3. Tambahkan trading tools ke Automaton (buy, sell, check_price, etc.)
4. Implementasi risk management rules
5. Create escrow system untuk user funds
6. Tambahkan handler ke bot V3
7. Test dengan paper trading
8. Deploy dengan real funds (small amount)
9. Monitor performance dan adjust strategy
