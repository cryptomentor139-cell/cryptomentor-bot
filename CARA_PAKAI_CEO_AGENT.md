# 🚀 CARA PAKAI CEO AGENT - PANDUAN LENGKAP

## 📋 APA ITU CEO AGENT?

CEO Agent adalah AUTOMATON Induk yang berfungsi sebagai Chief Executive Officer untuk CryptoMentor AI. Agent ini fokus pada:

- 👥 Follow-up user baru
- 📈 Mengembangkan bisnis
- 💰 Meningkatkan revenue
- 🎯 Marketing & growth
- 📊 Analytics & reporting
- 🤝 Customer relationship management

## 🆚 PERBEDAAN INDUK vs CHILD

### AUTOMATON Induk (CEO Agent)
- **Pemilik**: CryptoMentor AI (bukan user)
- **Tugas**: Mengelola bisnis & follow-up user
- **Bahasa**: Bahasa Indonesia
- **Fokus**: Semua user platform

### Child Agent (User's Agent)
- **Pemilik**: User individual
- **Tugas**: Trading otomatis untuk owner
- **Bahasa**: Sesuai preferensi user
- **Fokus**: Portfolio owner saja

## 📁 FILE YANG TERSEDIA

### 1. AUTOMATON_INDUK_PROMPT.md
Prompt lengkap untuk CEO Agent (~15,000 kata)
- Identitas & peran
- Tugas harian
- KPIs & metrics
- Communication templates
- Growth strategies
- Crisis management

### 2. CEO_AGENT_QUICK_REFERENCE.md
Referensi cepat (~2,000 kata)
- Checklist harian
- Key metrics
- Templates
- Protocols

### 3. CEO_AGENT_IMPLEMENTATION.md
Panduan teknis implementasi
- Cara spawn agent
- Integrasi dengan bot
- Testing & monitoring
- Troubleshooting

### 4. CEO_AGENT_COMPLETE_SUMMARY.md
Summary lengkap semua dokumentasi

## 🚀 CARA SPAWN CEO AGENT

### Option 1: Via Python Script (Recommended)

```python
# 1. Buat file spawn_ceo_agent.py
import requests
import os

CONWAY_API_KEY = os.getenv('CONWAY_API_KEY')
CONWAY_WALLET_ADDRESS = os.getenv('CONWAY_WALLET_ADDRESS')

def spawn_ceo_agent():
    url = "https://api.conway.so/v1/agents"
    
    # Load prompt
    with open('AUTOMATON_INDUK_PROMPT.md', 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    
    payload = {
        "name": "CryptoMentor CEO Agent",
        "description": "AI Agent CEO untuk CryptoMentor AI",
        "system_prompt": system_prompt,
        "model": "gpt-4-turbo",
        "temperature": 0.7,
        "max_tokens": 2000,
        "owner_wallet": CONWAY_WALLET_ADDRESS,
        "is_public": False,
        "metadata": {
            "type": "induk",
            "role": "ceo",
            "language": "id"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {CONWAY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        agent_data = response.json()
        agent_id = agent_data['agent_id']
        print(f"✅ CEO Agent spawned!")
        print(f"   Agent ID: {agent_id}")
        
        # Save to .env
        with open('.env', 'a') as f:
            f.write(f"\nCEO_AGENT_ID={agent_id}\n")
        
        return agent_id
    else:
        print(f"❌ Failed: {response.text}")
        return None

if __name__ == "__main__":
    spawn_ceo_agent()
```

```bash
# 2. Jalankan script
python spawn_ceo_agent.py
```

### Option 2: Via Bot Command (Admin Only)

```bash
# Di Telegram bot, kirim command:
/spawn_ceo_agent
```

## ⚙️ KONFIGURASI

### 1. Environment Variables

Tambahkan ke `.env`:
```bash
# Conway API
CONWAY_API_KEY=your_api_key_here
CONWAY_WALLET_ADDRESS=your_wallet_address_here

# CEO Agent (akan di-set otomatis setelah spawn)
CEO_AGENT_ID=will_be_set_after_spawn
```

### 2. Bot Integration

Tambahkan ke `bot.py`:
```python
# Import CEO Agent tasks
from app.ceo_agent_tasks import start_ceo_agent_tasks

# Di main() function
async def main():
    # ... existing code ...
    
    # Start CEO Agent automation
    ceo_agent_id = os.getenv('CEO_AGENT_ID')
    if ceo_agent_id:
        asyncio.create_task(start_ceo_agent_tasks(bot))
        print("✅ CEO Agent tasks started")
    else:
        print("⚠️ CEO Agent not configured")
```

## 🎯 FITUR UTAMA

### 1. Auto Follow-Up User Baru

CEO Agent otomatis follow-up user yang:
- Baru signup dalam 24 jam
- Belum deposit minimum $30
- Sudah deposit tapi belum spawn agent
- Inactive >7 hari

**Contoh Message**:
```
Halo John! 👋

Selamat datang di CryptoMentor AI! Saya CEO Agent yang akan membantu Anda.

Saya lihat Anda baru bergabung. Ada yang bisa saya bantu?

✅ Cara deposit USDC untuk AUTOMATON
✅ Cara spawn AI trading agent
✅ Tips optimasi performa

Jangan ragu bertanya! 🚀
```

### 2. Daily Business Report

Setiap hari jam 21:00, CEO Agent generate report:
```
📊 LAPORAN HARIAN CRYPTOMENTOR AI

Tanggal: 22 Feb 2026

👥 USER METRICS:
• Total Users: 1,234
• New Users: 45
• Active Users: 567
• Premium Users: 123

💰 REVENUE:
• Premium: $4,567
• AUTOMATON: $2,345
• Total: $6,912

🤖 AI AGENT:
• Agents Spawned: 89
• Active Agents: 67
• Total Trades: 1,234

📈 GROWTH:
• User Growth: +15%
• Revenue Growth: +22%

🎯 ACTION ITEMS:
1. Follow-up 12 users belum deposit
2. Launch weekend promo
3. Fix reported bug in /analyze
```

### 3. User Inquiry Handler

CEO Agent bisa handle pertanyaan user:
```
User: "Gimana cara deposit USDC?"

CEO Agent:
"Halo! Senang bisa membantu 😊

Cara deposit USDC untuk AUTOMATON:

1️⃣ Klik tombol 🤖 AI Agent di menu
2️⃣ Pilih "💰 Deposit USDC"
3️⃣ Copy alamat wallet (Base Network)
4️⃣ Kirim min $30 USDC
5️⃣ Kirim bukti transfer ke admin

⚠️ PENTING:
• Network: Base ONLY
• Token: USDC ONLY
• Minimum: $30 USDC

Ada yang masih kurang jelas?"
```

### 4. Marketing Campaigns

CEO Agent jalankan campaign otomatis:
- Weekend special offers
- Referral program reminders
- Loyalty rewards
- Seasonal promotions
- Re-engagement campaigns

### 5. Analytics & Insights

CEO Agent track dan analyze:
- User behavior patterns
- Conversion funnels
- Revenue trends
- Feature adoption
- Churn indicators

## 📊 MONITORING

### Dashboard Metrics

Akses via API endpoint:
```bash
GET /api/ceo/dashboard
```

Response:
```json
{
  "users": {
    "total": 1234,
    "active_today": 567,
    "new_today": 45,
    "premium": 123
  },
  "revenue": {
    "today": 6912,
    "this_week": 45678,
    "this_month": 123456,
    "mrr": 50000
  },
  "agents": {
    "total_spawned": 89,
    "active": 67,
    "total_trades": 1234
  },
  "health": {
    "churn_rate": 4.5,
    "conversion_rate": 12.3,
    "retention_rate": 85.7,
    "nps": 52
  }
}
```

## 🧪 TESTING

### Test CEO Agent Response

```python
# test_ceo_agent.py
import asyncio
from app.conway_integration import chat_with_agent

async def test():
    ceo_agent_id = os.getenv('CEO_AGENT_ID')
    
    # Test follow-up message
    response = await chat_with_agent(
        ceo_agent_id,
        "Generate follow-up message untuk user baru bernama John yang signup 2 jam lalu tapi belum deposit."
    )
    
    print(f"Response:\n{response}")

asyncio.run(test())
```

```bash
# Run test
python test_ceo_agent.py
```

## 📈 EXPECTED RESULTS

### Week 1
- ✅ CEO Agent spawned & configured
- ✅ Auto follow-up working
- ✅ Daily reports generated
- ✅ User inquiries handled

### Month 1
- ✅ Conversion rate improved 10%+
- ✅ User engagement increased
- ✅ Churn rate decreased
- ✅ Positive user feedback

### Quarter 1
- ✅ User base doubled
- ✅ MRR increased 50%+
- ✅ Strong community built
- ✅ Market leadership established

## ⚠️ TROUBLESHOOTING

### CEO Agent Not Responding

**Problem**: Agent tidak respond ke queries

**Solution**:
1. Check Conway API status
2. Verify `CEO_AGENT_ID` in `.env`
3. Check API credits balance
4. Review error logs
5. Test with simple prompt

### Follow-Up Not Sending

**Problem**: Auto follow-up tidak terkirim

**Solution**:
1. Check bot permissions
2. Verify user IDs valid
3. Review rate limiting
4. Check database queries
5. Test manually first

### Reports Not Generated

**Problem**: Daily report tidak generate

**Solution**:
1. Check scheduled task running
2. Verify database connections
3. Review metric calculations
4. Check admin IDs configured
5. Test report generation manually

## 💡 TIPS & BEST PRACTICES

### 1. Personalization
- Gunakan nama user di setiap message
- Reference history user (signup date, activity)
- Adjust tone based on user segment

### 2. Timing
- Follow-up dalam 24 jam signup
- Send reports di waktu yang konsisten
- Respect user timezone jika memungkinkan

### 3. Value First
- Setiap message harus provide value
- Jangan spam dengan promo terus
- Balance antara selling dan helping

### 4. Data-Driven
- Review metrics setiap hari
- Adjust strategy based on data
- A/B test different approaches

### 5. Human Touch
- CEO Agent assist, not replace human
- Escalate complex issues to admin
- Always option to talk to human

## 📞 SUPPORT

### Need Help?

**Technical Issues**:
- Check `CEO_AGENT_IMPLEMENTATION.md`
- Review error logs
- Contact admin team

**Strategy Questions**:
- Review `AUTOMATON_INDUK_PROMPT.md`
- Check `CEO_AGENT_QUICK_REFERENCE.md`
- Discuss with business team

**Prompt Updates**:
- Edit `AUTOMATON_INDUK_PROMPT.md`
- Re-spawn agent with new prompt
- Test thoroughly before production

## 🎯 NEXT STEPS

1. ✅ Review all documentation
2. ✅ Configure environment variables
3. ✅ Spawn CEO Agent
4. ✅ Test basic functions
5. ✅ Integrate with bot
6. ✅ Monitor performance
7. ✅ Optimize based on results
8. ✅ Scale automation

## 🎉 CONCLUSION

CEO Agent (AUTOMATON Induk) siap membantu mengembangkan CryptoMentor AI! Dengan automation yang tepat, personalized communication, dan data-driven decisions, platform akan tumbuh lebih cepat dan sustainable.

**Remember**: CEO Agent adalah tool untuk membantu, bukan menggantikan human judgment. Selalu review dan adjust berdasarkan real-world results.

---

**Status**: ✅ READY TO USE
**Language**: Bahasa Indonesia
**Version**: 1.0.0
**Last Updated**: 2026-02-22

**"Your Success is Our Success"** 🚀

**Questions?** Baca dokumentasi lengkap di:
- `AUTOMATON_INDUK_PROMPT.md` - System prompt
- `CEO_AGENT_QUICK_REFERENCE.md` - Quick reference
- `CEO_AGENT_IMPLEMENTATION.md` - Technical guide
- `CEO_AGENT_COMPLETE_SUMMARY.md` - Complete summary
