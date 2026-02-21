# Credits System Comparison

## ⚠️ PENTING: Ada 2 Jenis Credits!

Bot ini memiliki **2 sistem credits yang berbeda**. Jangan sampai salah!

## 1. Regular Bot Credits (Credits Biasa)

### Untuk Apa?
- Fitur analisis bot: `/analyze`, `/futures`, `/ai`
- Multi-coin signals
- AI market summary
- Semua fitur bot biasa

### Command Admin:
```bash
/grant_credits <user_id> <amount>
# atau
/admin  # Lalu pilih "Manage Credits"
```

### Dimana Disimpan?
- Table: `users` (kolom `credits`)
- Ini adalah credits untuk fitur bot biasa

### Conversion:
- Gratis untuk premium users
- 20 credits per analisis untuk free users

---

## 2. AUTOMATON Credits (Credits AI Agent)

### Untuk Apa?
- **HANYA untuk AI Agent** (autonomous trading)
- Spawn agent
- Agent operations
- Autonomous trading

### Command Admin:
```bash
/admin_add_automaton_credits <user_id> <amount> <note>
/admin_check_automaton_credits <user_id>
```

### Dimana Disimpan?
- Table: `user_credits_balance` (kolom `available_credits`)
- Ini adalah credits khusus untuk AI Agent

### Conversion:
- 1 USDC = 100 AUTOMATON credits
- $30 USDC = 3,000 credits (minimum untuk spawn)

---

## Perbandingan Lengkap

| Aspek | Regular Bot Credits | AUTOMATON Credits |
|-------|-------------------|-------------------|
| **Fungsi** | Analisis bot biasa | AI Agent (autonomous trading) |
| **Command Cek** | `/credits` | `/balance` atau `/agent_status` |
| **Command Admin Add** | `/grant_credits` | `/admin_add_automaton_credits` |
| **Command Admin Check** | `/admin` → Manage Credits | `/admin_check_automaton_credits` |
| **Database Table** | `users.credits` | `user_credits_balance.available_credits` |
| **Cara Dapat** | Gratis untuk premium, atau beli | Deposit USDC (Base Network) |
| **Minimum Deposit** | N/A (gratis untuk premium) | $30 USDC (3,000 credits) |
| **Network** | N/A | Base Network ONLY |
| **Token** | N/A | USDC ONLY |
| **Verifikasi** | Otomatis | Manual oleh admin |

---

## Kapan Pakai Yang Mana?

### Pakai Regular Bot Credits (`/grant_credits`):
- User minta credits untuk `/analyze`
- User minta credits untuk `/futures`
- User minta credits untuk `/ai`
- User minta credits untuk multi-coin signals
- User komplain "credits habis" untuk fitur bot

### Pakai AUTOMATON Credits (`/admin_add_automaton_credits`):
- User deposit USDC untuk AI Agent
- User mau spawn agent
- User komplain "tidak bisa spawn agent"
- User kirim bukti transfer USDC
- User tanya tentang autonomous trading

---

## Contoh Kasus

### ❌ SALAH:
```
User: "Saya deposit $30 USDC untuk AI Agent"
Admin: /grant_credits 123456789 3000
```
**Kenapa salah?** Ini menambah regular bot credits, bukan AUTOMATON credits!

### ✅ BENAR:
```
User: "Saya deposit $30 USDC untuk AI Agent"
Admin: /admin_add_automaton_credits 123456789 3000 Deposit $30 USDC verified
```
**Kenapa benar?** Ini menambah AUTOMATON credits yang benar untuk AI Agent!

---

### ❌ SALAH:
```
User: "Credits saya habis untuk /analyze"
Admin: /admin_add_automaton_credits 123456789 100 Top up credits
```
**Kenapa salah?** User butuh regular bot credits, bukan AUTOMATON credits!

### ✅ BENAR:
```
User: "Credits saya habis untuk /analyze"
Admin: /grant_credits 123456789 100
```
**Kenapa benar?** Ini menambah regular bot credits yang benar untuk fitur bot!

---

## Cara Cek Credits User

### Cek Regular Bot Credits:
```bash
/admin
# Lalu search user dan lihat "Credits" field
```

### Cek AUTOMATON Credits:
```bash
/admin_check_automaton_credits <user_id>
```

---

## Tips untuk Admin

1. **Selalu tanya dulu**: "Credits untuk apa? Bot biasa atau AI Agent?"

2. **Lihat konteks**:
   - Kalau user mention "deposit USDC" → AUTOMATON credits
   - Kalau user mention "spawn agent" → AUTOMATON credits
   - Kalau user mention "/analyze" atau "/futures" → Regular bot credits

3. **Cek dulu sebelum add**:
   - Regular: `/admin` → Search user
   - AUTOMATON: `/admin_check_automaton_credits <user_id>`

4. **Jangan sampai salah**:
   - AUTOMATON credits TIDAK bisa dipakai untuk bot biasa
   - Regular bot credits TIDAK bisa dipakai untuk AI Agent
   - Keduanya terpisah total!

---

## Quick Reference Card

**User bilang:**
- "Deposit USDC" → `/admin_add_automaton_credits`
- "Spawn agent" → `/admin_add_automaton_credits`
- "AI Agent" → `/admin_add_automaton_credits`
- "Autonomous trading" → `/admin_add_automaton_credits`
- "/analyze habis" → `/grant_credits`
- "/futures habis" → `/grant_credits`
- "Credits bot habis" → `/grant_credits`
- "Mau analisis" → `/grant_credits`

---

## Kesimpulan

**2 sistem credits yang BERBEDA:**

1. **Regular Bot Credits** = Untuk fitur bot biasa
   - Command: `/grant_credits`
   
2. **AUTOMATON Credits** = Untuk AI Agent saja
   - Command: `/admin_add_automaton_credits`

**Jangan sampai tertukar!** 🚨

---

**Last Updated**: 2026-02-22
**Dibuat untuk**: Membantu admin membedakan 2 jenis credits
