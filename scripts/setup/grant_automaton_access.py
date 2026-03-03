#!/usr/bin/env python3
"""
Admin Tool: Grant Automaton Access
Usage: python grant_automaton_access.py <user_id>
"""

import sys
from database import Database

def grant_access(user_id):
    """Grant Automaton access to a user"""
    db = Database()
    
    # Get user info
    user = db.get_user(user_id)
    if not user:
        print(f"❌ User {user_id} not found")
        return False
    
    print(f"\n👤 User Information:")
    print(f"   ID: {user_id}")
    print(f"   Name: {user.get('first_name', 'Unknown')}")
    print(f"   Username: @{user.get('username', 'none')}")
    print(f"   Premium: {'✅ Yes' if user.get('is_premium') else '❌ No'}")
    print(f"   Subscription End: {user.get('subscription_end', 'Lifetime')}")
    
    # Check current access
    current_access = db.has_automaton_access(user_id)
    print(f"   Current Automaton Access: {'✅ Yes' if current_access else '❌ No'}")
    
    if current_access:
        print(f"\n⚠️  User already has Automaton access!")
        return True
    
    # Check if premium
    if not db.is_user_premium(user_id):
        print(f"\n❌ User is not premium! They must buy premium first.")
        return False
    
    # Grant access
    print(f"\n🔄 Granting Automaton access...")
    success = db.grant_automaton_access(user_id)
    
    if success:
        print(f"✅ Access granted successfully!")
        print(f"✅ User {user_id} can now spawn agents")
        
        # Verify
        new_access = db.has_automaton_access(user_id)
        print(f"✅ Verified: Access = {new_access}")
        return True
    else:
        print(f"❌ Failed to grant access")
        return False

def check_access(user_id):
    """Check user's Automaton access status"""
    db = Database()
    
    user = db.get_user(user_id)
    if not user:
        print(f"❌ User {user_id} not found")
        return
    
    has_access = db.has_automaton_access(user_id)
    is_premium = db.is_user_premium(user_id)
    
    print(f"\n👤 User {user_id} ({user.get('first_name', 'Unknown')})")
    print(f"   Premium: {'✅' if is_premium else '❌'}")
    print(f"   Automaton Access: {'✅' if has_access else '❌'}")
    print(f"   Credits: {user.get('credits', 0):,}")

def list_without_access():
    """List premium users without Automaton access"""
    db = Database()
    
    db.cursor.execute("""
        SELECT telegram_id, first_name, username, credits
        FROM users 
        WHERE is_premium = 1 AND automaton_access = 0
        ORDER BY first_name
    """)
    
    users = db.cursor.fetchall()
    
    if not users:
        print("✅ All premium users have Automaton access!")
        return
    
    print(f"\n📊 Premium users without Automaton access: {len(users)}")
    print(f"💰 Potential revenue: Rp{len(users) * 2_000_000:,}\n")
    
    for user in users:
        user_id, name, username, credits = user
        print(f"  • {user_id} - {name} (@{username or 'none'}) - {credits:,} credits")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python grant_automaton_access.py <user_id>     # Grant access")
        print("  python grant_automaton_access.py check <user_id>  # Check status")
        print("  python grant_automaton_access.py list          # List users without access")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_without_access()
    elif command == "check":
        if len(sys.argv) < 3:
            print("❌ Please provide user_id")
            sys.exit(1)
        user_id = int(sys.argv[2])
        check_access(user_id)
    else:
        user_id = int(command)
        grant_access(user_id)
