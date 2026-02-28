# Panduan Backup Database Supabase

## PENTING: Backup SEBELUM Migration! ⚠️

Sebelum menjalankan migration 003 (Automaton Access), WAJIB backup database terlebih dahulu untuk mencegah kehilangan data.

## Metode 1: Backup via Python Script (RECOMMENDED) ✅

### Langkah 1: Jalankan Script Backup
```bash
cd Bismillah
python backup_supabase_users.py
```

### Output yang Diharapkan:
```
🚀 Starting Supabase Users Backup
============================================================
🔄 Connecting to Supabase...
📥 Fetching all users from Supabase...
✅ Fetched 1234 users
📊 Premium users: 50
📊 Lifetime users: 41
💾 Saving backup to backup_users_before_automaton_20260220_143000.json...
✅ Backup saved: backup_users_before_automaton_20260220_143000.json (245,678 bytes)

============================================================
📋 BACKUP SUMMARY
============================================================
Backup file: backup_users_before_automaton_20260220_143000.json
Total users: 1234
Premium users: 50
Lifetime users: 41
File size: 245,678 bytes
Backup date: 2026-02-20T14:30:00.123456
============================================================
✅ Backup completed successfully!

⚠️ IMPORTANT: Keep this backup file safe!
   You can use it to restore data if migration fails.
```

### Langkah 2: Verifikasi File Backup
```bash
# Check file exists
dir backup_users_before_automaton_*.json

# Check file size (should be > 100KB for 1000+ users)
```

### Langkah 3: Simpan Backup di Tempat Aman
1. Copy file backup ke folder lain (bukan di project)
2. Upload ke Google Drive / Dropbox
3. Atau kirim ke email sendiri

## Metode 2: Backup via Supabase Dashboard

### Langkah 1: Buka Supabase Dashboard
1. Login ke https://supabase.com
2. Pilih project CryptoMentor AI
3. Klik "Database" di sidebar

### Langkah 2: Create Backup
1. Klik tab "Backups"
2. Klik tombol "Create backup"
3. Tunggu proses backup selesai (biasanya 1-5 menit)
4. Backup akan muncul di list dengan timestamp

### Langkah 3: Verifikasi Backup
- Status harus "Completed"
- Size harus > 0 MB
- Timestamp harus sesuai dengan waktu sekarang

## Metode 3: Export Manual via SQL Editor

### Langkah 1: Buka SQL Editor
1. Di Supabase Dashboard, klik "SQL Editor"
2. Klik "New query"

### Langkah 2: Export Users Table
```sql
-- Export all users to CSV
COPY (
    SELECT * FROM users
) TO STDOUT WITH CSV HEADER;
```

### Langkah 3: Save Output
1. Copy semua output
2. Paste ke file `users_backup_20260220.csv`
3. Save file di tempat aman

## Verifikasi Backup Berhasil

### Cek Jumlah Users
```python
import json

# Load backup file
with open('backup_users_before_automaton_20260220_143000.json', 'r') as f:
    backup = json.load(f)

print(f"Total users: {backup['total_users']}")
print(f"Premium users: {backup['premium_users']}")
print(f"Lifetime users: {backup['lifetime_users']}")

# Check sample user
if backup['users']:
    sample = backup['users'][0]
    print(f"\nSample user:")
    print(f"  ID: {sample.get('telegram_id')}")
    print(f"  Name: {sample.get('first_name')}")
    print(f"  Premium: {sample.get('is_premium')}")
```

### Expected Output:
```
Total users: 1234
Premium users: 50
Lifetime users: 41

Sample user:
  ID: 1187119989
  Name: Bil
  Premium: True
```

## Restore dari Backup (Jika Diperlukan)

### Jika Migration Gagal:

#### Option 1: Restore via Python Script
```python
import json
from supabase_client import supabase_service

# Load backup
with open('backup_users_before_automaton_20260220_143000.json', 'r') as f:
    backup = json.load(f)

# Restore users (CAUTION: This will overwrite current data)
for user in backup['users']:
    # Remove automaton_access field if exists
    if 'automaton_access' in user:
        del user['automaton_access']
    
    # Upsert user
    supabase_service.table('users').upsert(user).execute()

print(f"✅ Restored {len(backup['users'])} users")
```

#### Option 2: Restore via Supabase Dashboard
1. Go to Database > Backups
2. Find the backup you created
3. Click "Restore"
4. Confirm restoration
5. Wait for process to complete

#### Option 3: Restore via SQL
```sql
-- Remove automaton_access column
ALTER TABLE users DROP COLUMN IF EXISTS automaton_access;

-- Then restore from backup file manually
```

## Checklist Sebelum Migration

- [ ] ✅ Backup created via Python script
- [ ] ✅ Backup file saved (> 100KB)
- [ ] ✅ Backup copied to safe location
- [ ] ✅ Backup verified (can open and read)
- [ ] ✅ Total users count matches production
- [ ] ✅ Premium users count matches production
- [ ] ✅ Lifetime users count matches production

## Setelah Backup Selesai

Lanjut ke deployment:
1. ✅ Backup completed
2. ⏳ Run Supabase migration (next step)
3. ⏳ Deploy code to Railway
4. ⏳ Test in production
5. ⏳ Announce to users

## Troubleshooting

### Error: "Module 'supabase_client' not found"
```bash
# Check if supabase_client.py exists
dir supabase_client.py

# If not, check .env for Supabase credentials
type .env | findstr SUPABASE
```

### Error: "Connection timeout"
- Check internet connection
- Check Supabase project status
- Try again in a few minutes

### Error: "No users found"
- Check if connected to correct project
- Check if users table exists
- Check Supabase credentials in .env

### Backup File Too Small (< 10KB)
- Something went wrong
- Check error messages
- Try backup again
- Don't proceed with migration

## Important Notes

⚠️ **CRITICAL**: NEVER skip backup before migration!

✅ **BEST PRACTICE**: Create multiple backups:
- Python script backup (JSON)
- Supabase dashboard backup
- Manual SQL export (CSV)

💾 **STORAGE**: Keep backups for at least 30 days

🔒 **SECURITY**: Backup files contain sensitive data:
- Don't commit to Git
- Don't share publicly
- Store securely

## Contact

Jika ada masalah dengan backup:
1. Check error messages carefully
2. Try different backup method
3. Contact development team
4. DO NOT proceed with migration until backup succeeds

---

**Ready to backup?** Run the Python script now:
```bash
python backup_supabase_users.py
```

**After backup succeeds**, proceed to:
- `AUTOMATON_ACCESS_DEPLOYMENT.md` - Deployment steps
