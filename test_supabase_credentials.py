#!/usr/bin/env python3
"""
Test Supabase Credentials
Check if Supabase API keys are valid
"""
import os
import sys
from dotenv import load_dotenv

# Load .env
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection with current credentials"""
    print("="*60)
    print("🧪 TESTING SUPABASE CREDENTIALS")
    print("="*60)
    
    # Get credentials
    url = os.getenv('SUPABASE_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    print("\n📋 CREDENTIALS CHECK:")
    print(f"SUPABASE_URL: {url[:30]}..." if url else "❌ NOT SET")
    print(f"SUPABASE_ANON_KEY: {anon_key[:30]}..." if anon_key else "❌ NOT SET")
    print(f"SUPABASE_SERVICE_KEY: {service_key[:30]}..." if service_key else "❌ NOT SET")
    
    if not url or not service_key:
        print("\n❌ Missing required credentials!")
        return False
    
    # Check for placeholder
    if 'placeholder' in anon_key.lower():
        print("\n⚠️  WARNING: SUPABASE_ANON_KEY contains 'placeholder'")
        print("   This is likely an invalid key!")
    
    # Try to connect
    print("\n🔌 TESTING CONNECTION...")
    
    try:
        from supabase import create_client, Client
        
        print("✅ Supabase library imported")
        
        # Try with service key (more permissions)
        print("\n📊 Testing with SERVICE_KEY...")
        supabase: Client = create_client(url, service_key)
        
        # Test query
        print("   Querying users table...")
        result = supabase.table('users')\
            .select('telegram_id', count='exact')\
            .limit(1)\
            .execute()
        
        total_count = result.count if hasattr(result, 'count') else 0
        
        print(f"✅ CONNECTION SUCCESSFUL!")
        print(f"   Total users in Supabase: {total_count}")
        
        # Test pagination
        print("\n📄 Testing pagination (fetch 10 users)...")
        result = supabase.table('users')\
            .select('telegram_id, first_name')\
            .not_.is_('telegram_id', 'null')\
            .neq('telegram_id', 0)\
            .range(0, 9)\
            .execute()
        
        if result.data:
            print(f"✅ Fetched {len(result.data)} users")
            print(f"   Sample IDs: {[u.get('telegram_id') for u in result.data[:3]]}")
        else:
            print("⚠️  No users found")
        
        return True
        
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED!")
        print(f"   Error: {e}")
        
        error_str = str(e).lower()
        
        if 'invalid api key' in error_str or 'unauthorized' in error_str:
            print("\n🔑 ISSUE: Invalid API Key")
            print("   Your SUPABASE_SERVICE_KEY is incorrect or expired")
            print("\n   How to fix:")
            print("   1. Go to Supabase Dashboard")
            print("   2. Project Settings → API")
            print("   3. Copy 'service_role' key (NOT anon key)")
            print("   4. Update SUPABASE_SERVICE_KEY in .env")
            
        elif 'not found' in error_str or '404' in error_str:
            print("\n🔍 ISSUE: Table not found")
            print("   The 'users' table doesn't exist in your Supabase project")
            
        elif 'network' in error_str or 'timeout' in error_str:
            print("\n🌐 ISSUE: Network error")
            print("   Cannot reach Supabase server")
            print("   Check your internet connection")
        
        else:
            print("\n❓ UNKNOWN ERROR")
            print("   Check the error message above")
        
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()
        
        return False

def check_supabase_keys_format():
    """Check if Supabase keys have correct format"""
    print("\n" + "="*60)
    print("🔍 CHECKING KEY FORMATS")
    print("="*60)
    
    anon_key = os.getenv('SUPABASE_ANON_KEY', '')
    service_key = os.getenv('SUPABASE_SERVICE_KEY', '')
    
    issues = []
    
    # Check anon key
    if 'placeholder' in anon_key.lower():
        issues.append("❌ SUPABASE_ANON_KEY contains 'placeholder' - this is invalid!")
    elif not anon_key.startswith('eyJ'):
        issues.append("⚠️  SUPABASE_ANON_KEY doesn't start with 'eyJ' (JWT format)")
    else:
        print("✅ SUPABASE_ANON_KEY format looks valid")
    
    # Check service key
    if not service_key.startswith('eyJ'):
        issues.append("❌ SUPABASE_SERVICE_KEY doesn't start with 'eyJ' (JWT format)")
    else:
        print("✅ SUPABASE_SERVICE_KEY format looks valid")
    
    if issues:
        print("\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        return False
    
    print("\n✅ All keys have valid JWT format")
    return True

def get_correct_keys_instructions():
    """Show instructions to get correct keys"""
    print("\n" + "="*60)
    print("📖 HOW TO GET CORRECT SUPABASE KEYS")
    print("="*60)
    
    print("""
1. Go to: https://supabase.com/dashboard
2. Select your project: "CryptoMentor Bot"
3. Click "Settings" (gear icon) in left sidebar
4. Click "API" in settings menu
5. You'll see two keys:

   📌 anon / public key:
   - Starts with: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6...
   - Copy this to: SUPABASE_ANON_KEY
   
   🔑 service_role / secret key:
   - Starts with: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6...
   - Copy this to: SUPABASE_SERVICE_KEY
   - ⚠️  IMPORTANT: Use service_role key, NOT anon key!

6. Update your .env file:
   SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
   SUPABASE_ANON_KEY=eyJ... (paste anon key here)
   SUPABASE_SERVICE_KEY=eyJ... (paste service_role key here)

7. Restart bot

8. Test again: python test_supabase_credentials.py
""")

if __name__ == "__main__":
    print("\n🚀 Starting Supabase Credentials Test\n")
    
    # Check format
    format_ok = check_supabase_keys_format()
    
    # Test connection
    connection_ok = test_supabase_connection()
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Key format check: {'✅ PASS' if format_ok else '❌ FAIL'}")
    print(f"Connection test: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print("="*60)
    
    if not format_ok or not connection_ok:
        get_correct_keys_instructions()
        print("\n❌ SUPABASE NOT WORKING")
        print("   Fix the issues above and test again")
    else:
        print("\n✅ SUPABASE WORKING PERFECTLY!")
        print("   Your credentials are valid")
        print("   Broadcast should work with all users")
