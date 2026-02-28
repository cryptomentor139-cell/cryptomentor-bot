# 🚀 RUN MIGRATION SEKARANG - 3 LANGKAH

## ✅ Backup Selesai! Lanjut Migration

---

## 📋 LANGKAH 1: COPY SQL INI

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS automaton_access BOOLEAN DEFAULT FALSE;

UPDATE users SET automaton_access = TRUE WHERE is_premium = TRUE AND subscription_end IS NULL;

CREATE INDEX IF NOT EXISTS idx_users_automaton_access ON users(automaton_access);

SELECT COUNT(*) as total_users, SUM(CASE WHEN automaton_access = TRUE THEN 1 ELSE 0 END) as users_with_access FROM users;
```

---

## ▶️ LANGKAH 2: PASTE & RUN

1. **Buka SQL Editor** Supabase (masih terbuka kan?)
2. **Ctrl+A** (select all)
3. **Ctrl+V** (paste SQL di atas)
4. **F5** (run)

---

## ✅ LANGKAH 3: CEK HASIL

Hasil akan muncul dengan 2 angka:
- `total_users`: Total users Anda (1000+)
- `users_with_access`: Lifetime users yang dapat akses gratis (40-50)

**Screenshot hasil** dan kirim ke saya!

---

## 🆘 JIKA ERROR

### Error: "subscription_end does not exist"

**Gunakan SQL ini** (tanpa subscription_end check):

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS automaton_access BOOLEAN DEFAULT FALSE;

UPDATE users SET automaton_access = TRUE WHERE is_premium = TRUE;

CREATE INDEX IF NOT EXISTS idx_users_automaton_access ON users(automaton_access);

SELECT COUNT(*) as total_users, SUM(CASE WHEN automaton_access = TRUE THEN 1 ELSE 0 END) as users_with_access FROM users;
```

**Note:** Ini akan grant akses ke SEMUA premium users.

### Error: "column already exists"

**Artinya:** Migration sudah pernah dijalankan.

**Solusi:** Skip migration, langsung deploy code (Step 3).

---

**COBA SEKARANG!** Copy SQL di atas dan run di Supabase.

