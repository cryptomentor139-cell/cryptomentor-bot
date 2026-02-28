#!/usr/bin/env python3
"""
Find a lifetime premium user for testing
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.supabase_conn import get_supabase_client

def find_lifetime_premium_users():
    """Find users with lifetime premium status"""
    try:
        supabase = get_supabase_client()
        
        # Query for lifetime premium users
        result = supabase.table("users").select(
            "telegram_id, username, is_premium, premium_until, credits"
        ).eq(
            "is_premium", True
        ).is_(
            "premium_until", "null"
        ).limit(10).execute()
        
        if result.data:
            print(f"\n✅ Found {len(result.data)} lifetime premium users:\n")
            for user in result.data:
                print(f"User ID: {user['telegram_id']}")
                print(f"  Username: {user.get('username', 'N/A')}")
                print(f"  Credits: {user.get('credits', 0)}")
                print(f"  Premium: {user['is_premium']}")
                print(f"  Premium Until: {user['premium_until']}")
                print()
            
            return result.data[0]['telegram_id']
        else:
            print("\n❌ No lifetime premium users found")
            print("\nSearching for any premium users...")
            
            # Try to find any premium user
            result = supabase.table("users").select(
                "telegram_id, username, is_premium, premium_until, credits"
            ).eq(
                "is_premium", True
            ).limit(5).execute()
            
            if result.data:
                print(f"\n✅ Found {len(result.data)} premium users:\n")
                for user in result.data:
                    print(f"User ID: {user['telegram_id']}")
                    print(f"  Username: {user.get('username', 'N/A')}")
                    print(f"  Premium Until: {user['premium_until']}")
                    print()
            
            return None
            
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        return None


if __name__ == "__main__":
    print("="*60)
    print("Finding Lifetime Premium Users")
    print("="*60)
    
    user_id = find_lifetime_premium_users()
    
    if user_id:
        print(f"\n✅ Use this user ID for testing: {user_id}")
    else:
        print("\n⚠️  No lifetime premium users found")
        print("You may need to manually set a user to lifetime premium in Supabase")
