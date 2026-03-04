# 🔧 OpenClaw Commands Fix - Database Issues

## 🐛 Masalah Yang Ditemukan

Dari screenshot Telegram, semua command OpenClaw error dengan 2 masalah utama:

### 1. Database Connection Error
```
Error: invalid integer value 'npg_PXo7pTdgJ4ny' for connection option 'port'
```

**Root Cause:** Environment variable `PGPASSWORD` terbaca sebagai `PGPORT`
- `.env` file memiliki: `PGPASSWORD=npg_PXo7pTdgJ4ny`
- System mencoba parse sebagai port number
- Port harus integer, bukan string

**Solution:** Periksa urutan environment variables di `.env`

### 2. SQLite Cursor Error
```
Error: sqlite3.Cursor' object is not callable
```

**Root Cause:** Code menyimpan `db.cursor` sebagai property, bukan method
```python
# WRONG:
self.cursor = db.cursor  # Stores method reference
self.cursor.execute()    # Tries to call property

# CORRECT:
cursor = db.cursor()     # Calls method to get cursor
cursor.execute()         # Uses cursor object
```

### 3. PostgreSQL vs SQLite Syntax
Code menggunakan PostgreSQL placeholder `%s` tapi database adalah SQLite yang butuh `?`

```python
# WRONG (PostgreSQL):
cursor.execute("SELECT * FROM table WHERE id = %s", (id,))

# CORRECT (SQLite):
cursor.execute("SELECT * FROM table WHERE id = ?", (id,))
```

## ✅ Perbaikan Yang Dilakukan

### File: `app/handlers_openclaw_admin_credits.py`
- ✅ Fixed: Changed all `%s` to `?` for SQLite compatibility
- ✅ Fixed: Lines 189, 195, 201, 207, 257, 260

### File: `app/openclaw_manager.py`
- ✅ Fixed: Removed `self.cursor = db.cursor` (line 48)
- ✅ Added: `_get_cursor()` helper method
- ✅ Fixed: `create_assistant()` method to use local cursor
- ⚠️ TODO: Fix remaining methods (see below)

## 🔄 Methods Yang Perlu Diperbaiki

Semua method di `openclaw_manager.py` yang menggunakan `self.cursor` perlu diubah:

### Pattern Yang Harus Diikuti:
```python
def some_method(self, ...):
    """Method description"""
    try:
        cursor = self._get_cursor()  # Get new cursor
        
        # Do database operations
        cursor.execute("SELECT ...", (...))
        result = cursor.fetchone()
        
        # Commit if needed
        self.conn.commit()
        cursor.close()  # Always close cursor
        
        return result
        
    except Exception as e:
        logger.error(f"Error: {e}")
        cursor.close()  # Close on error too
        raise
```

### Methods Yang Perlu Update:
1. ✅ `create_assistant()` - FIXED
2. ⚠️ `chat()` - Needs fix
3. ⚠️ `purchase_credits()` - Needs fix
4. ⚠️ `get_assistant_info()` - Needs fix
5. ⚠️ `get_user_assistants()` - Needs fix
6. ⚠️ `get_user_conversations()` - Needs fix
7. ⚠️ `_create_conversation()` - Needs fix
8. ⚠️ `_get_conversation_history()` - Needs fix
9. ⚠️ `_save_message()` - Needs fix
10. ⚠️ `_get_user_credits()` - Needs fix
11. ⚠️ `_deduct_credits()` - Needs fix
12. ⚠️ `_update_conversation_stats()` - Needs fix
13. ⚠️ `_update_assistant_stats()` - Needs fix
14. ⚠️ `get_available_skills()` - Needs fix (also has `%s`)
15. ⚠️ `get_installed_skills()` - Needs fix (also has `%s`)
16. ⚠️ `install_skill()` - Needs fix (also has `%s`)
17. ⚠️ `toggle_skill()` - Needs fix (also has `%s`)
18. ⚠️ `get_skill_details()` - Needs fix (also has `%s`)
19. ⚠️ `_generate_system_prompt()` - Has nested query with `%s`

## 🚀 Quick Fix Script

Saya sudah membuat `fix_openclaw_cursor.py` tapi perlu review manual karena:
- Setiap method perlu `cursor = self._get_cursor()` di awal
- Setiap method perlu `cursor.close()` sebelum return
- Error handling perlu close cursor juga

## 📋 Recommended Action Plan

### Option 1: Manual Fix (Safest)
1. Fix each method one by one
2. Test after each fix
3. Time: ~2-3 hours

### Option 2: Automated Fix + Review
1. Run fix script to replace all
2. Manual review and add cursor management
3. Test all commands
4. Time: ~1 hour

### Option 3: Temporary Workaround
1. Keep `self.cursor = db.cursor()` (call method)
2. Just fix PostgreSQL `%s` → SQLite `?`
3. Test if it works
4. Time: ~15 minutes

## 💡 Recommendation

**Start with Option 3** (quick workaround):
- Change line 48 to: `self.cursor = db.cursor()`  (add `()`)
- Fix all `%s` to `?` in skill methods
- Test commands
- If works → deploy
- If not → proceed with Option 1 or 2

## 🎯 Expected Result After Fix

All these commands should work:
- ✅ `/openclaw_start` - Start AI Assistant
- ✅ `/openclaw_create` - Create assistant
- ✅ `/openclaw_help` - Show help
- ✅ `/openclaw_balance` - Check credits
- ✅ `/openclaw_monitor` - Admin monitoring
- ✅ `/admin_system_status` - System status
- ✅ `/admin_add_credits` - Add credits to user

## 📝 Testing Checklist

After fix, test these commands:
- [ ] `/openclaw_help` - Should show help text
- [ ] `/openclaw_balance` - Should show balance
- [ ] `/admin_system_status` - Should show OpenRouter balance
- [ ] `/admin_add_credits 1187119989 10 test` - Should add credits
- [ ] `/openclaw_monitor` - Should show monitoring dashboard
- [ ] Send message to bot - Should get AI response

---

**Status:** 🔄 In Progress
**Priority:** 🔴 High (All OpenClaw commands broken)
**Impact:** All users cannot use OpenClaw features
**ETA:** 15-60 minutes depending on approach chosen
