# Admin Guide: Grant Automaton Access

## When to Use This

When a Regular Premium user (Monthly/2 Bulan/1 Tahun) pays Rp2,000,000 for Automaton access.

**Note:** Lifetime users get automatic access - no need to grant manually.

## Step-by-Step Process

### 1. User Pays Rp2,000,000
User sends payment proof to @BillFarr with:
- Payment proof
- Telegram UID
- "Automaton Access" package

### 2. Verify Payment
Check that payment is received (Rp2,000,000)

### 3. Grant Access via Python

#### Option A: Using Python Script
```python
# Create file: grant_automaton_access.py
from database import Database

def grant_access(user_id):
    db = Database()
    
    # Check current status
    print(f"Current access: {db.has_automaton_access(user_id)}")
    
    # Grant access
    success = db.grant_automaton_access(user_id)
    
    if success:
        print(f"✅ Access granted to user {user_id}")
        print(f"New access: {db.has_automaton_access(user_id)}")
    else:
        print(f"❌ Failed to grant access")
    
    return success

# Usage
user_id = 123456789  # Replace with actual Telegram ID
grant_access(user_id)
```

Run:
```bash
python grant_automaton_access.py
```

#### Option B: Using Python Console
```bash
python
```

Then:
```python
from database import Database
db = Database()

# Replace with actual user ID
user_id = 123456789

# Grant access
db.grant_automaton_access(user_id)

# Verify
print(f"Access granted: {db.has_automaton_access(user_id)}")
```

### 4. Notify User
Send message to user:
```
✅ Automaton Access Activated!

Your Rp2,000,000 payment has been confirmed.
You can now spawn autonomous trading agents.

Try it: /automaton or use the 🤖 AI Agent menu
```

## Check User Access Status

### Check Single User
```python
from database import Database
db = Database()

user_id = 123456789
has_access = db.has_automaton_access(user_id)
is_premium = db.is_user_premium(user_id)

print(f"User {user_id}:")
print(f"  Premium: {is_premium}")
print(f"  Automaton Access: {has_access}")
```

### Check All Users Without Access
```python
from database import Database
db = Database()

# Get premium users without Automaton access
db.cursor.execute("""
    SELECT telegram_id, first_name, username, subscription_end
    FROM users 
    WHERE is_premium = 1 AND automaton_access = 0
""")

users = db.cursor.fetchall()
print(f"Premium users without Automaton access: {len(users)}")
for user in users:
    user_id, name, username, sub_end = user
    print(f"  - {user_id} (@{username}) - {name}")
```

## Revenue Tracking

### Check Total Revenue Potential
```python
from database import Database
db = Database()

# Count premium users without access
db.cursor.execute("""
    SELECT COUNT(*) FROM users 
    WHERE is_premium = 1 AND automaton_access = 0
""")
count = db.cursor.fetchone()[0]

potential_revenue = count * 2_000_000
print(f"Premium users without access: {count}")
print(f"Potential revenue: Rp{potential_revenue:,}")
```

### Check Total Users with Access
```python
from database import Database
db = Database()

db.cursor.execute("SELECT COUNT(*) FROM users WHERE automaton_access = 1")
total = db.cursor.fetchone()[0]

db.cursor.execute("""
    SELECT COUNT(*) FROM users 
    WHERE automaton_access = 1 AND subscription_end IS NULL
""")
lifetime = db.cursor.fetchone()[0]

paid = total - lifetime
revenue = paid * 2_000_000

print(f"Total with access: {total}")
print(f"  - Lifetime (free): {lifetime}")
print(f"  - Paid: {paid}")
print(f"Revenue from Automaton access: Rp{revenue:,}")
```

## Troubleshooting

### User Says They Paid But Can't Spawn
1. Check if user is premium:
   ```python
   db.is_user_premium(user_id)  # Should be True
   ```

2. Check if user has Automaton access:
   ```python
   db.has_automaton_access(user_id)  # Should be True
   ```

3. Check if user has enough credits:
   ```python
   user = db.get_user(user_id)
   print(f"Credits: {user['credits']}")  # Should be >= 100,000
   ```

### Access Not Working After Grant
1. Verify in database:
   ```python
   db.cursor.execute("""
       SELECT automaton_access FROM users WHERE telegram_id = ?
   """, (user_id,))
   print(db.cursor.fetchone())  # Should be (1,)
   ```

2. If still 0, grant again:
   ```python
   db.grant_automaton_access(user_id)
   ```

## Important Notes

- ✅ Lifetime users get FREE access automatically
- ✅ Regular Premium users must pay Rp2,000,000
- ✅ Free users must first buy Premium, then pay for Automaton access
- ✅ Access is one-time payment (not recurring)
- ✅ All grants are logged in user_activity table

## Quick Reference

| User Type | Premium | Automaton Access | Action |
|-----------|---------|------------------|--------|
| Lifetime | ✅ | ✅ FREE | Automatic |
| Monthly/2M/1Y | ✅ | ❌ Need to pay | Grant after payment |
| Free | ❌ | ❌ Need Premium first | Buy Premium first |

## Contact

If you need help, check:
- `AUTOMATON_ACCESS_FEE_COMPLETE.md` - Full documentation
- `test_automaton_access.py` - Test suite
- `migrations/003_add_automaton_access.sql` - Database schema
