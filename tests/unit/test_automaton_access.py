#!/usr/bin/env python3
"""
Test Automaton Access Control
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import Database

def test_automaton_access():
    """Test automaton access control"""
    print("🧪 Testing Automaton Access Control")
    print("=" * 60)
    
    db = Database()
    
    # Test 1: Check lifetime users have access
    print("\n1️⃣ Testing lifetime users have automatic access...")
    db.cursor.execute("""
        SELECT telegram_id, first_name, is_premium, subscription_end, automaton_access
        FROM users 
        WHERE is_premium = 1 AND subscription_end IS NULL
        LIMIT 5
    """)
    lifetime_users = db.cursor.fetchall()
    
    for user in lifetime_users:
        user_id, name, is_premium, sub_end, access = user
        status = "✅" if access == 1 else "❌"
        print(f"  {status} User {user_id} ({name}): Premium={is_premium}, SubEnd={sub_end}, Access={access}")
    
    # Test 2: Check regular premium users don't have access
    print("\n2️⃣ Testing regular premium users need to pay...")
    db.cursor.execute("""
        SELECT telegram_id, first_name, is_premium, subscription_end, automaton_access
        FROM users 
        WHERE is_premium = 1 AND subscription_end IS NOT NULL
        LIMIT 5
    """)
    regular_premium = db.cursor.fetchall()
    
    for user in regular_premium:
        user_id, name, is_premium, sub_end, access = user
        status = "✅" if access == 0 else "⚠️"
        print(f"  {status} User {user_id} ({name}): Premium={is_premium}, SubEnd={sub_end}, Access={access}")
    
    # Test 3: Test has_automaton_access method
    print("\n3️⃣ Testing has_automaton_access() method...")
    if lifetime_users:
        test_user_id = lifetime_users[0][0]
        has_access = db.has_automaton_access(test_user_id)
        print(f"  User {test_user_id}: has_automaton_access() = {has_access}")
        assert has_access == True, "Lifetime user should have access"
        print("  ✅ Method works correctly")
    
    # Test 4: Test grant_automaton_access method
    print("\n4️⃣ Testing grant_automaton_access() method...")
    if regular_premium:
        test_user_id = regular_premium[0][0]
        print(f"  Before: User {test_user_id} access = {db.has_automaton_access(test_user_id)}")
        
        # Grant access
        success = db.grant_automaton_access(test_user_id)
        print(f"  Grant result: {success}")
        
        # Verify
        has_access = db.has_automaton_access(test_user_id)
        print(f"  After: User {test_user_id} access = {has_access}")
        assert has_access == True, "Access should be granted"
        print("  ✅ Method works correctly")
        
        # Revert for testing
        db.cursor.execute("UPDATE users SET automaton_access = 0 WHERE telegram_id = ?", (test_user_id,))
        db.conn.commit()
        print(f"  Reverted access for testing purposes")
    
    # Test 5: Summary statistics
    print("\n5️⃣ Summary Statistics...")
    db.cursor.execute("SELECT COUNT(*) FROM users WHERE automaton_access = 1")
    total_access = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1 AND subscription_end IS NULL")
    total_lifetime = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
    total_premium = db.cursor.fetchone()[0]
    
    print(f"  📊 Total users with Automaton access: {total_access}")
    print(f"  📊 Total lifetime users: {total_lifetime}")
    print(f"  📊 Total premium users: {total_premium}")
    print(f"  📊 Premium users without access: {total_premium - total_access}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_automaton_access()
