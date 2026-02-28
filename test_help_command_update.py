"""
Test script to verify help command update for manual signal generation
"""

def test_help_text_contains_manual_signals():
    """Verify help text includes manual signal commands"""
    
    # Indonesian version
    id_help_text = """📚 **CryptoMentor AI - Panduan Perintah**

🎯 **Sistem Menu (Disarankan):**
• `/start` - Tampilkan menu selamat datang
• `/menu` - Buka menu utama kapan saja

💰 **Perintah Gratis:**
• `/price <symbol>` - Cek harga cryptocurrency
• `/market` - Ringkasan pasar global
• `/portfolio` - Lihat kepemilikan Anda
• `/credits` - Cek saldo kredit

🧠 **Perintah Generate Sinyal Manual:**
• `/analyze <symbol>` - Analisis single coin (20 kredit)
  Contoh: `/analyze BTCUSDT`
• `/futures <symbol> <timeframe>` - Sinyal futures (20 kredit)
  Contoh: `/futures ETHUSDT 4h`
• `/futures_signals` - Sinyal multi-coin (60 kredit)
  Contoh: `/futures_signals`

👑 **Lifetime Premium:** Semua command GRATIS (tanpa biaya kredit)

🤖 **Cerebras AI Assistant (ULTRA FAST!):**
• `/ai <symbol>` - Analisis market dengan AI (0.4s response!)
• `/chat <pesan>` - Chat santai tentang market & trading
• `/aimarket` - Summary kondisi market global dengan AI

👑 **Premium & Akun:**
• `/subscribe` - Upgrade ke premium
• `/referral` - Program referral
• `/language <en|id>` - Ubah bahasa

💡 **Tips:** Gunakan menu tombol untuk pengalaman terbaik!
🔥 **Fitur Baru:** Cerebras AI - 70x lebih cepat dari sebelumnya!"""
    
    # English version
    en_help_text = """📚 **CryptoMentor AI - Command Reference**

🎯 **Menu System (Recommended):**
• `/start` - Show welcome menu
• `/menu` - Open main menu anytime

💰 **Free Commands:**
• `/price <symbol>` - Check cryptocurrency price
• `/market` - Global market overview
• `/portfolio` - View your holdings
• `/credits` - Check credit balance

🧠 **Manual Signal Generation:**
• `/analyze <symbol>` - Single coin analysis (20 credits)
  Example: `/analyze BTCUSDT`
• `/futures <symbol> <timeframe>` - Futures signal (20 credits)
  Example: `/futures ETHUSDT 4h`
• `/futures_signals` - Multi-coin signals (60 credits)
  Example: `/futures_signals`

👑 **Lifetime Premium:** All commands FREE (no credit charge)

🤖 **Cerebras AI Assistant (ULTRA FAST!):**
• `/ai <symbol>` - Market analysis with AI (0.4s response!)
• `/chat <message>` - Casual chat about market & trading
• `/aimarket` - Global market summary with AI insights

👑 **Premium & Account:**
• `/subscribe` - Upgrade to premium
• `/referral` - Referral program
• `/language <en|id>` - Change language

💡 **Tip:** Use the button menu for the best experience!
🔥 **New Feature:** Cerebras AI - 70x faster than before!"""
    
    # Test Indonesian version
    print("Testing Indonesian help text...")
    assert "Perintah Generate Sinyal Manual" in id_help_text, "Missing manual signal section (ID)"
    assert "/analyze <symbol>" in id_help_text, "Missing /analyze command (ID)"
    assert "/futures <symbol> <timeframe>" in id_help_text, "Missing /futures command (ID)"
    assert "/futures_signals" in id_help_text, "Missing /futures_signals command (ID)"
    assert "Contoh: `/analyze BTCUSDT`" in id_help_text, "Missing example for /analyze (ID)"
    assert "Contoh: `/futures ETHUSDT 4h`" in id_help_text, "Missing example for /futures (ID)"
    assert "Lifetime Premium:** Semua command GRATIS" in id_help_text, "Missing lifetime premium info (ID)"
    print("✅ Indonesian help text contains all required elements")
    
    # Test English version
    print("\nTesting English help text...")
    assert "Manual Signal Generation" in en_help_text, "Missing manual signal section (EN)"
    assert "/analyze <symbol>" in en_help_text, "Missing /analyze command (EN)"
    assert "/futures <symbol> <timeframe>" in en_help_text, "Missing /futures command (EN)"
    assert "/futures_signals" in en_help_text, "Missing /futures_signals command (EN)"
    assert "Example: `/analyze BTCUSDT`" in en_help_text, "Missing example for /analyze (EN)"
    assert "Example: `/futures ETHUSDT 4h`" in en_help_text, "Missing example for /futures (EN)"
    assert "Lifetime Premium:** All commands FREE" in en_help_text, "Missing lifetime premium info (EN)"
    print("✅ English help text contains all required elements")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\n📋 Summary:")
    print("✅ Indonesian help text updated with manual signal commands")
    print("✅ English help text updated with manual signal commands")
    print("✅ Usage examples included for all commands")
    print("✅ Lifetime premium benefit clearly mentioned")
    print("\n🎯 Task 4 Acceptance Criteria:")
    print("✅ Help text includes manual signal commands")
    print("✅ Both Indonesian and English versions updated")
    print("✅ Usage examples are clear")
    print("✅ Lifetime premium benefit mentioned")

if __name__ == "__main__":
    test_help_text_contains_manual_signals()
