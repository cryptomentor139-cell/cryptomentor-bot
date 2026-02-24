"""
AI Agent Education Handler
Memberikan edukasi transparan kepada user tentang fitur AI Agent
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from app.database import get_user_data, update_user_data


async def show_ai_agent_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Tampilkan edukasi AI Agent kepada user pertama kali
    Full transparansi tentang sistem, cara kerja, dan manfaat
    """
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    # Cek apakah user sudah pernah melihat edukasi
    has_seen_education = user_data.get('has_seen_ai_agent_education', False)
    
    # Teks edukasi yang transparan dan informatif
    education_text = """
🤖 <b>Selamat Datang di AI Agent!</b>

<b>🎯 Apa itu AI Agent?</b>
AI Agent adalah asisten trading otomatis yang bekerja 24/7 untuk Anda. Seperti memiliki trader profesional pribadi yang tidak pernah tidur!

<b>⚙️ Cara Kerja (Full Transparansi):</b>

1⃣ <b>Isolated AI Instance</b>
   🔒 Setiap user mendapat AI pribadi
   🖥️ Berjalan di server terpisah (Conway)
   🚫 Data trading Anda TIDAK tercampur dengan user lain
   ✅ Privacy & keamanan terjaga

2⃣ <b>Sistem Deposit & Credits</b>
   💰 Deposit USDC ke wallet Anda
   💵 1 USDC = 100 credits
   📊 Credits digunakan untuk:
     • Spawn AI Agent (100 credits)
     • Biaya operasional AI ("bensin")
     • Eksekusi trading

3⃣ <b>Autonomous Trading</b>
   📈 AI menganalisis market real-time
   🎯 Menggunakan Smart Money Concepts (SMC)
   ⚡ Eksekusi otomatis saat ada peluang
   👀 Anda bisa monitor kapan saja

4⃣ <b>Revenue Sharing Otomatis</b>
   💸 Setiap profit trading → 10% ke parent (jika ada)
   🤖 OTOMATIS terpotong, tidak perlu manual
   🔄 Recursive: parent share ke grandparent
   💰 Passive income dari children agents!

5⃣ <b>Spawn Child System</b>
   👶 Agent bisa "melahirkan" child agent (otomatis)
   🔒 Child trading sendiri (isolated)
   💵 10% profit child → Parent Anda
   🌳 Build lineage tree untuk passive income!

<b>✨ Manfaat untuk Anda:</b>

✅ <b>Trading 24/7</b> - AI tidak pernah lelah
🧠 <b>Emotion-Free</b> - Keputusan berdasarkan data
📊 <b>Multi-Timeframe</b> - Analisis lengkap
🛡️ <b>Risk Management</b> - Stop loss otomatis
🔍 <b>Transparent</b> - Semua log bisa dilihat
📈 <b>Scalable</b> - Spawn multiple agents
💰 <b>Passive Income</b> - 10% dari children profits
🌳 <b>Lineage System</b> - Build agent family tree

<b>💵 Biaya & Pricing:</b>

🤖 <b>Spawn Agent:</b> 100,000 credits (1,000 USDC)
💰 <b>Minimum Deposit:</b> 5 USDC (technical minimum)
✅ <b>Recommended Deposit:</b> 1,030+ USDC (untuk spawn + operations)
🏦 <b>Platform Fee:</b> 2% dari deposit (untuk pengembangan)
⛽ <b>Operasional AI:</b> Credits untuk "bensin" automaton
💵 <b>Trading Capital:</b> Sisanya untuk trading
💸 <b>Withdrawal:</b> Kapan saja (min 5 USDC)

⚠️ <b>Penting - Spawn Fee:</b>
• Spawn 1 agent: 100,000 credits = $1,000 USDC
• Kenapa mahal? Agent berjalan 24/7, konsumsi resources
• One-time fee per agent
• Tercatat di transaction log

💰 <b>Minimum Deposit Options:</b>
• $5 USDC: Technical minimum (testing only, CANNOT spawn)
• $30 USDC: Small operations (monitoring, analysis, CANNOT spawn)
• $1,030 USDC: Spawn 1 agent + operations
• $2,000+ USDC: Spawn + trading capital

📊 <b>Contoh Deposit $1,030 USDC:</b>
• Platform fee: 2% ($20.60) → CryptoMentor AI
• Net received: $1,009.40 = 100,940 credits
• Spawn agent: 100,000 credits ($1,000)
• Remaining: 940 credits ($9.40) untuk operasional
• Trading capital: Perlu deposit tambahan

❓ <b>Kenapa ada Platform Fee 2%?</b>
• Pengembangan fitur baru
• Maintenance server & infrastructure
• Support & customer service
• Keamanan & audit sistem
• Continuous improvement

🔍 <b>Transparansi Platform Fee:</b>
• 2% fixed rate (tidak berubah)
• Dipotong saat deposit
• Tercatat di transaction log
• Digunakan untuk pengembangan platform

<b>🔒 Keamanan:</b>

✅ Wallet custodial (kami kelola)
🔐 Private key terenkripsi
📝 Audit log semua transaksi
🛡️ Rate limiting untuk proteksi
👮 Admin approval untuk withdrawal

<b>⚙️ Teknologi:</b>

🤖 <b>AI Model:</b> DeepSeek R1 (reasoning)
📊 <b>Data Source:</b> Binance Futures API
⛓️ <b>Blockchain:</b> Base Network (USDC)
🖥️ <b>Infrastructure:</b> Conway + Railway

<b>🚀 Siap Memulai?</b>

Klik tombol di bawah untuk:
1. Deposit USDC pertama Anda
2. Spawn AI Agent pertama
3. Mulai autonomous trading!

<i>❓ Ada pertanyaan? Hubungi admin atau baca dokumentasi lengkap.</i>
"""
    
    # Keyboard dengan opsi
    keyboard = [
        [InlineKeyboardButton("💰 Deposit Sekarang", callback_data="automaton_deposit")],
        [InlineKeyboardButton("🤖 Spawn AI Agent", callback_data="automaton_spawn")],
        [InlineKeyboardButton("📚 Baca Dokumentasi", callback_data="ai_agent_docs")],
        [InlineKeyboardButton("❓ FAQ", callback_data="ai_agent_faq")],
        [InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="ai_agent_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Update flag bahwa user sudah melihat edukasi
    if not has_seen_education:
        update_user_data(user_id, {'has_seen_ai_agent_education': True})
    
    await query.edit_message_text(
        text=education_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )


async def show_ai_agent_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Tampilkan FAQ tentang AI Agent
    """
    query = update.callback_query
    await query.answer()
    
    faq_text = """
 <b>FAQ - AI Agent</b>

<b>Q: Apakah AI Agent bisa rugi?</b>
A: Ya, seperti trading manual. AI menggunakan risk management, tapi market tetap unpredictable. Jangan invest lebih dari yang Anda mampu.

<b>Q: Berapa lama AI Agent berjalan?</b>
A: Tergantung aktivitas trading. AI butuh "bensin" (credits) untuk operasional. Semakin aktif trading, semakin cepat credits terpakai. Estimasi: 100-500 credits per hari untuk operasional.

<b>Q: Bisa spawn berapa AI Agent?</b>
A: Unlimited! Setiap agent butuh 100 credits (1 USDC) untuk spawn. Plus credits untuk operasional masing-masing agent. Anda bisa punya multiple agents dengan strategi berbeda.

<b>Q: Bagaimana cara withdraw profit?</b>
A: Gunakan command /withdraw. Minimum 5 USDC. Admin akan approve dalam 24 jam.

<b>Q: Apakah data saya aman?</b>
A: Ya! Setiap user punya isolated instance. Data tidak tercampur. Private key terenkripsi dengan AES-256.

<b>Q: Bisa ganti strategi AI?</b>
A: Saat ini menggunakan SMC (Smart Money Concepts). Update strategi akan ditambahkan di versi mendatang.

<b>Q: Kalau AI Agent error?</b>
A: Sistem auto-restart. Jika masalah berlanjut, hubungi admin. Credits tidak akan hangus.

<b>Q: Minimum deposit berapa?</b>
A: 
 Technical minimum: 5 USDC
 Untuk spawn agent: 1,030+ USDC
 Recommended: 2,000+ USDC

Breakdown untuk spawn:
 Spawn 1 agent: 100,000 credits (1,000 USDC)
 Operasional AI beberapa hari: 100-500 credits
 Trading capital: Sisanya

Note: $30 USDC TIDAK CUKUP untuk spawn agent!

<b>Q: Bisa refund?</b>
A: Deposit bisa di-withdraw kapan saja (min 5 USDC). Tapi credits yang sudah digunakan tidak bisa refund.

<b>Q: Profit sharing?</b>
A: Tidak ada profit sharing dengan platform! Semua profit 100% milik Anda. Kami hanya charge:
 2% platform fee saat deposit (untuk pengembangan)
 Credits untuk operasional AI (bensin)

<b>Q: Apa itu Platform Fee 2%?</b>
A: Biaya untuk pengembangan dan maintenance platform:
 Pengembangan fitur baru
 Server & infrastructure costs
 Support & customer service
 Keamanan & audit sistem
 Continuous improvement

Contoh: Deposit $100 USDC
 Platform fee: $2 (2%)
 You receive: $98 = 9,800 credits

<b>Q: Apakah ada biaya lain?</b>
A: Hanya 3 biaya yang transparan:
1. Platform fee: 2% saat deposit
2. Spawn agent: 100,000 credits (1,000 USDC)
3. Operasional AI: Credits untuk bensin

Tidak ada:
 Hidden fees
 Monthly subscription
 Profit sharing
 Withdrawal fees (min 5 USDC)

<b>Q: Apa itu "bensin" automaton?</b>
A: Credits yang digunakan untuk menjalankan AI Agent:
 Analisis market real-time
 Eksekusi trading
 Monitoring posisi
 Risk management
Semakin aktif AI, semakin banyak bensin terpakai.

<b>Q: Apa itu Revenue Sharing Otomatis?</b>
A: Sistem otomatis yang membagi profit trading:
 Setiap kali agent Anda profit dari trading
 10% otomatis terpotong untuk parent agent (jika ada)
 Ini OTOMATIS, tidak perlu manual
 Recursive: parent juga share ke grandparent (10% dari 10%)

Contoh: Agent Anda profit 100 credits
 10 credits → Parent agent (otomatis)
 90 credits → Tetap di agent Anda
 Jika parent punya parent, 1 credit → Grandparent (10% dari 10)

<b>Q: Apa itu Spawn Child?</b>
A: Agent Anda bisa "melahirkan" agent baru (child) secara OTOMATIS:
 Ketika agent Anda sudah profit (bukan habis karena bensin)
 Agent bisa spawn child dengan 100 credits
 Child agent trading sendiri (isolated)
 10% profit child → Parent Anda (passive income!)

<b>Q: Keuntungan Spawn Child?</b>
A: Passive income yang terus bertambah:
 Child trading 24/7 → Anda dapat 10% profit mereka
 Child bisa spawn grandchild → Anda dapat 1% profit grandchild
 Semakin banyak descendants, semakin banyak passive income
 Seperti MLM tapi untuk AI trading!

Contoh Lineage Tree:
```
Your Agent (Parent)
   Child 1 → profit 1000 credits → Anda dapat 100
   Child 2 → profit 500 credits → Anda dapat 50
   Child 3
       Grandchild → profit 200 credits → Anda dapat 2
Total passive income: 152 credits!
```

<b>Q: Kerugian Spawn Child?</b>
A: Ada biaya dan risk:
 Spawn cost: 100 credits dari parent
 Child bisa rugi → Parent tidak dapat apa-apa
 Child konsumsi bensin → Bisa habis sebelum profit
 Tidak semua child profitable

<b>Q: Kapan Agent Spawn Child?</b>
A: OTOMATIS berdasarkan kondisi:
 Agent sudah profit (balance > initial deposit)
 Agent punya cukup credits (min 200 credits)
 Agent dalam status "active"
 Survival tier "thriving" atau "stable"

<b>Q: Bisa kontrol spawn child?</b>
A: Ya, ada settings:
 Enable/disable auto-spawn
 Set minimum profit sebelum spawn
 Set maximum children per agent
 Manual spawn juga bisa

<b>Q: Berapa maksimal children?</b>
A: Tidak ada limit hard, tapi:
 Recommended: 3-5 children per agent
 Terlalu banyak children → Parent kehabisan credits
 Quality over quantity!

<b>Q: Bagaimana tracking lineage?</b>
A: Gunakan command:
 <code>/agent_lineage</code> - Lihat tree lengkap
 Tampilkan parent, children, grandchildren
 Total revenue dari lineage
 Statistics per agent
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Kembali", callback_data="ai_agent_education")],
        [InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=faq_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )


async def show_ai_agent_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Tampilkan dokumentasi teknis AI Agent
    """
    query = update.callback_query
    await query.answer()
    
    docs_text = """
 <b>Dokumentasi Teknis AI Agent</b>

<b> Arsitektur Sistem:</b>

<code>
User (Telegram Bot)
    ↓
Main Server (Railway)
    ↓
Conway Server (AI Instances)
    ↓
Binance API (Market Data)
</code>

<b> Flow Deposit → Trading:</b>

1. User deposit USDC ke wallet
2. Sistem detect deposit otomatis
3. Credits di-credit ke akun (1 USDC = 100 credits)
4. User spawn AI Agent (100 credits = 1 USDC)
5. AI mulai analisis market (konsumsi bensin)
6. Eksekusi trade saat ada signal (konsumsi bensin)
7. Profit/loss masuk ke balance
8. <b>OTOMATIS: 10% profit → Parent agent (jika ada)</b>
9. User bisa withdraw kapan saja

 <b>Catatan Bensin:</b>
 Setiap aktivitas AI konsumsi credits
 Monitoring: ~1-5 credits/jam
 Trading: ~10-50 credits/trade
 Total: ~100-500 credits/hari (tergantung aktivitas)

 <b>Lineage System (Spawn Child):</b>

<b>Kapan Agent Spawn Child?</b>
 Agent sudah profit (balance > initial)
 Punya min 200 credits
 Status "active" & tier "thriving"
 Auto-spawn enabled

<b>Revenue Sharing Otomatis:</b>
```
Child profit 100 credits
  ↓
10 credits → Parent (OTOMATIS)
90 credits → Child tetap
  ↓
1 credit → Grandparent (10% dari 10%)
```

<b>Contoh Lineage Tree:</b>
```
Your Agent (1000 credits)
   Child 1 (500 credits) → profit 200 → Anda +20
   Child 2 (300 credits) → profit 100 → Anda +10
   Child 3 (400 credits)
       Grandchild (200 credits) → profit 50 → Anda +0.5
      
Total passive income: 30.5 credits!
```

<b>Keuntungan Lineage:</b>
 Passive income 24/7
 Semakin banyak descendants, semakin banyak income
 Children trading independently
 Recursive revenue sharing

<b>Kerugian Lineage:</b>
 Spawn cost: 100 credits per child
 Child bisa rugi → No income
 Child konsumsi bensin
 Management complexity

<b> AI Decision Making:</b>

 <b>Data Input:</b>
  - Price action (OHLCV)
  - Volume profile
  - Order flow
  - Market structure

 <b>Analysis:</b>
  - Smart Money Concepts
  - Supply/Demand zones
  - Liquidity mapping
  - Trend identification

 <b>Execution:</b>
  - Entry: Break of structure
  - Stop Loss: Below/above zone
  - Take Profit: Next liquidity level
  - Position Size: Risk-based

<b> Database Schema:</b>

 <b>users:</b> User data & credits
 <b>wallets:</b> Custodial wallets
 <b>deposits:</b> Deposit history
 <b>withdrawals:</b> Withdrawal requests
 <b>ai_agents:</b> Agent instances
 <b>trades:</b> Trading history
 <b>audit_logs:</b> All activities

<b> Security Measures:</b>

 AES-256 encryption untuk private keys
 Rate limiting (10 req/min)
 Admin approval untuk withdrawal
 Audit logging semua transaksi
 Isolated AI instances per user
 Environment variables untuk secrets

<b> Monitoring:</b>

Commands untuk monitoring:
 <code>/agent_status</code> - Status AI Agent
 <code>/balance</code> - Check balance & credits
 <code>/agent_logs</code> - View AI logs
 <code>/agent_lineage</code> - Agent hierarchy & passive income

<b>Lineage Command Output:</b>
```
 Agent Lineage Tree

Your Agent: "Alpha Trader"
 Credits: 1,500
 Total Children Revenue: 250 credits
 Direct Children: 3
 Total Descendants: 5

Children:
   Child 1: "Beta Bot" (500 credits)
      Grandchild: "Gamma AI" (200 credits)
   Child 2: "Delta Trader" (300 credits)
   Child 3: "Epsilon Bot" (400 credits)

 Passive Income Stats:
 Total earned from lineage: 250 credits
 Average per child: 83.3 credits
 Lineage depth: 2 levels
```

<b> Roadmap:</b>

 Phase 1: Basic AI Agent (Done)
 Phase 2: Deposit System (Done)
 Phase 3: Autonomous Trading (Done)
 Phase 4: Multiple Strategies (In Progress)
 Phase 5: Portfolio Management
 Phase 6: Social Trading
 Phase 7: Mobile App

<i> Sistem ini terus berkembang. Feedback Anda sangat berharga!</i>
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Kembali", callback_data="ai_agent_education")],
        [InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=docs_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    