"""
AI Agent Education Handler - Transparent explanation for users
Shows how the isolated AI trading system works
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


async def show_ai_agent_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show educational message about AI Agent system
    Full transparency about how it works
    """
    
    user_id = update.effective_user.id
    
    # Educational message - transparent and honest
    message = """
🤖 <b>AI Agent Trading - Cara Kerjanya</b>

Kami ingin <b>100% transparan</b> tentang bagaimana sistem AI Agent kami bekerja:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 Apa itu AI Agent?</b>

AI Agent adalah sistem trading otomatis yang:
• Trade 24/7 untuk Anda
• Analisis market secara real-time
• Eksekusi strategi trading otomatis
• Kelola risk management

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💰 Sistem Deposit & Balance</b>

<b>PENTING - Baca ini dengan teliti:</b>

1️⃣ <b>Wallet Terpusat (Centralized)</b>
   • Semua user deposit ke 1 wallet yang sama
   • Address: <code>0x6311...5822</code> (Base Network)
   • Ini untuk efisiensi dan keamanan

2️⃣ <b>AI Instance Terpisah (Isolated)</b>
   • Setiap user dapat AI sendiri
   • Balance tracked terpisah di database
   • AI Anda HANYA trade dengan uang Anda

<b>Contoh:</b>
• User A deposit 100 USDC → AI A balance: 100
• User B deposit 1000 USDC → AI B balance: 1000
• User C deposit 50 USDC → AI C balance: 50

Meskipun deposit ke wallet yang sama, sistem kami track balance masing-masing user secara terpisah.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 Pembagian Profit - FAIR!</b>

Profit dibagi secara <b>proporsional</b>:

Jika semua AI earn 5% profit:
• User A: 100 → 105 (+5 USDC)
• User B: 1000 → 1050 (+50 USDC)
• User C: 50 → 52.5 (+2.5 USDC)

✅ Percentage sama (5%)
✅ Amount berbeda (sesuai deposit)
✅ FAIR untuk semua!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🌳 Child AI Spawning</b>

Ketika AI Anda earn cukup banyak, AI bisa "spawn" child agent:

<b>Cara Kerjanya:</b>
• AI utama Anda (Generation 1) trade
• Ketika profit mencapai threshold tertentu
• AI founder (Automaton) decide untuk spawn child
• Child agent (Generation 2) dibuat dari earnings Anda
• Child juga trade untuk Anda

<b>Contoh Hierarchy:</b>
```
Your Main AI (Gen 1)
├─ Balance: 100 USDC
├─ Earned: 60 USDC
│
├─ Child AI 1 (Gen 2)
│  └─ Balance: 12 USDC (dari earnings)
│
└─ Child AI 2 (Gen 2)
   └─ Balance: 10 USDC (dari earnings)

Total Portfolio: 182 USDC
```

<b>PENTING:</b>
• Child spawning INDEPENDENT per user
• User dengan deposit lebih besar → lebih banyak child
• Tidak ada biaya tambahan untuk spawn
• Semua child tetap milik Anda

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💵 Fee Structure</b>

<b>1. Deposit Fee: 5%</b>
   Contoh: Deposit 100 USDC
   • Platform fee: 5 USDC
   • AI balance: 95 USDC

<b>2. Performance Fee: 20% dari profit</b>
   Contoh: AI earn 10 USDC profit
   • Performance fee: 2 USDC
   • Your profit: 8 USDC

<b>3. Tidak ada biaya lain!</b>
   • Tidak ada monthly fee
   • Tidak ada withdrawal fee
   • Tidak ada spawn fee

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🔒 Keamanan & Transparansi</b>

<b>Wallet Terpusat:</b>
✅ 1 private key untuk manage (lebih aman)
✅ Professional custody solution
✅ Reduced attack surface

<b>Database Tracking:</b>
✅ Balance tracked per user
✅ Complete audit trail
✅ Real-time monitoring
✅ Transparent reporting

<b>Anda bisa cek:</b>
• Balance AI Anda kapan saja
• History semua transaksi
• Profit/loss detail
• Child agents Anda

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>❓ FAQ</b>

<b>Q: Apakah uang saya aman?</b>
A: Ya! Meskipun deposit ke wallet terpusat, balance Anda tracked terpisah. Anda bisa withdraw kapan saja.

<b>Q: Bagaimana saya tahu profit saya real?</b>
A: Sistem kami fully transparent. Anda bisa cek balance, history, dan performance AI Anda kapan saja.

<b>Q: Apakah AI saya bisa rugi?</b>
A: Ya, trading selalu ada risk. Tapi AI kami punya risk management untuk minimize loss.

<b>Q: Berapa minimum deposit?</b>
A: Minimum 10 USDC untuk activate AI Agent.

<b>Q: Bisa withdraw kapan saja?</b>
A: Ya! Tidak ada lock period. Withdraw kapan saja Anda mau.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 Kesimpulan</b>

Sistem kami dirancang untuk:
✅ Fair profit distribution
✅ Transparent tracking
✅ Secure custody
✅ Scalable untuk semua user

Kami percaya <b>transparansi</b> adalah kunci kepercayaan. Jika ada pertanyaan, jangan ragu untuk tanya!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Siap untuk mulai?</b>
"""
    
    # Keyboard with options
    keyboard = [
        [
            InlineKeyboardButton("✅ Saya Mengerti, Aktifkan AI", callback_data="activate_ai_agent"),
            InlineKeyboardButton("📊 Lihat Contoh Portfolio", callback_data="show_ai_example")
        ],
        [
            InlineKeyboardButton("❓ Tanya Lebih Lanjut", callback_data="ai_agent_faq"),
            InlineKeyboardButton("🔙 Kembali", callback_data="back_to_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send or edit message
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )


async def show_ai_example_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show example portfolio to help users understand"""
    
    message = """
📊 <b>Contoh Portfolio AI Agent</b>

Mari lihat contoh real bagaimana sistem bekerja:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>👤 User: Alice</b>
<b>Deposit Awal: 100 USDC</b>

<b>Setelah 1 Bulan Trading:</b>

🤖 <b>Main AI Agent (Gen 1)</b>
├─ Balance: 148 USDC
├─ Total Earned: 60 USDC
├─ ROI: +60%
└─ Status: Active

   ├─ 🤖 <b>Child AI 1 (Gen 2)</b>
   │  ├─ Balance: 12 USDC
   │  ├─ Earned: 2 USDC
   │  └─ Spawned from parent earnings
   │
   └─ 🤖 <b>Child AI 2 (Gen 2)</b>
      ├─ Balance: 10 USDC
      ├─ Earned: 1.5 USDC
      └─ Spawned from parent earnings

<b>📈 Total Portfolio:</b>
• Total Balance: 170 USDC
• Total Profit: 70 USDC
• ROI: +70%
• Active Agents: 3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>👤 User: Bob</b>
<b>Deposit Awal: 1000 USDC</b>

<b>Setelah 1 Bulan Trading:</b>

🤖 <b>Main AI Agent (Gen 1)</b>
├─ Balance: 1280 USDC
├─ Total Earned: 600 USDC
├─ ROI: +60%
└─ Status: Active

   ├─ 🤖 <b>Child AI 1 (Gen 2)</b>
   │  ├─ Balance: 120 USDC
   │  └─ Earned: 20 USDC
   │
   ├─ 🤖 <b>Child AI 2 (Gen 2)</b>
   │  ├─ Balance: 100 USDC
   │  └─ Earned: 15 USDC
   │
   └─ 🤖 <b>Child AI 3 (Gen 2)</b>
      ├─ Balance: 100 USDC
      └─ Earned: 12 USDC

<b>📈 Total Portfolio:</b>
• Total Balance: 1600 USDC
• Total Profit: 600 USDC
• ROI: +60%
• Active Agents: 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 Perhatikan:</b>

1️⃣ <b>ROI Percentage Sama</b>
   • Alice: +60%
   • Bob: +60%
   • Fair untuk semua!

2️⃣ <b>Profit Amount Berbeda</b>
   • Alice: +70 USDC
   • Bob: +600 USDC
   • Proporsional ke deposit

3️⃣ <b>Child Spawning Independent</b>
   • Alice: 2 child agents
   • Bob: 3 child agents
   • Lebih banyak deposit → lebih banyak child

4️⃣ <b>Semua Transparent</b>
   • Bisa cek balance kapan saja
   • History lengkap
   • Real-time updates

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 Kesimpulan:</b>

Sistem kami memastikan:
✅ Fair distribution (percentage sama)
✅ Proportional profit (amount sesuai deposit)
✅ Independent growth (child spawning per user)
✅ Full transparency (track semua detail)

<b>Siap untuk mulai?</b>
"""
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Aktifkan AI Agent Saya", callback_data="activate_ai_agent"),
        ],
        [
            InlineKeyboardButton("🔙 Kembali ke Penjelasan", callback_data="show_ai_education"),
            InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def show_ai_agent_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed FAQ"""
    
    message = """
❓ <b>AI Agent - Frequently Asked Questions</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Q1: Kenapa semua deposit ke 1 wallet?</b>

A: Untuk efisiensi dan keamanan:
• Lebih mudah manage 1 private key
• Lower gas fees (consolidated funds)
• Professional custody solution
• Easier liquidity management

Tapi jangan khawatir! Balance Anda tracked terpisah di database. Uang Anda tetap aman dan bisa withdraw kapan saja.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Q2: Bagaimana saya yakin balance saya benar?</b>

A: Full transparency:
• Real-time balance tracking
• Complete transaction history
• Audit trail lengkap
• Bisa cek kapan saja via bot

Kami juga melakukan balance reconciliation regular untuk memastikan database match dengan on-chain balance.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Q3: Apakah AI saya bisa rugi?</b>

A: Ya, trading selalu ada risk. Tapi:
• AI punya risk management
• Stop loss otomatis
• Position sizing yang proper
• Diversifikasi strategi

<b>PENTING:</b> Jangan invest lebih dari yang Anda mampu untuk lose.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Q4: Berapa lama untuk profit?</b>

A: Tidak ada jaminan profit. Tapi:
• AI trade 24/7
• Analisis market real-time
• Eksekusi cepat
• Biasanya mulai terlihat hasil dalam 1-2 minggu

Performance bisa vary tergantung market conditions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Q5: Bisa withdraw kapan saja?</b>

A: Ya! Tidak ada lock period.
• Withdraw kapan saja
• Proses dalam 24 jam
• Tidak ada penalty
• Tidak ada minimum holding period

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Q6: Bagaimana dengan child AI spawning?</b>

A: Child AI spawn otomatis ketika:
• Main AI earn cukup profit
• Automaton founder AI decide
• Tidak ada biaya tambahan
• Child tetap milik Anda

Anda tidak perlu lakukan apa-apa, semua otomatis!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Q7: Apakah ada hidden fees?</b>

A: TIDAK! Fee structure kami transparent:
• Deposit fee: 5% (one-time)
• Performance fee: 20% dari profit
• Tidak ada monthly fee
• Tidak ada withdrawal fee
• Tidak ada hidden charges

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Q8: Bagaimana jika platform tutup?</b>

A: Funds Anda aman karena:
• Stored di blockchain (Base Network)
• Anda bisa withdraw kapan saja
• Tidak ada lock-in
• Transparent on-chain

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Q9: Bisa lihat performance AI saya?</b>

A: Ya! Anda bisa cek:
• Balance real-time
• Profit/loss history
• Trade history
• Child agents status
• ROI percentage

Semua via bot, kapan saja!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Q10: Minimum deposit berapa?</b>

A: Minimum 10 USDC untuk activate AI Agent.

Tapi kami recommend start dengan amount yang Anda comfortable untuk risk.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Masih ada pertanyaan?</b>

Jangan ragu untuk tanya! Kami siap bantu.
"""
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Saya Siap, Aktifkan AI", callback_data="activate_ai_agent"),
        ],
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="show_ai_education"),
            InlineKeyboardButton("💬 Chat Admin", url="https://t.me/your_admin")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )
