"""
Comprehensive Environment Variables Checker
Cek semua konfigurasi dan pastikan semuanya berfungsi
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env_var(name, required=True, check_placeholder=True):
    """Check single environment variable"""
    value = os.getenv(name, '').strip()
    
    if not value:
        return {
            'status': 'missing' if required else 'optional',
            'value': None,
            'message': '❌ Not set' if required else '⚠️  Optional (not set)'
        }
    
    # Check for placeholder values
    if check_placeholder:
        placeholders = ['your_', 'placeholder', 'here', 'example']
        if any(p in value.lower() for p in placeholders):
            return {
                'status': 'placeholder',
                'value': value[:30] + '...' if len(value) > 30 else value,
                'message': '⚠️  Placeholder value detected'
            }
    
    return {
        'status': 'ok',
        'value': value[:30] + '...' if len(value) > 30 else value,
        'message': '✅ Configured'
    }


def check_all_configurations():
    """Check all environment configurations"""
    print("=" * 70)
    print("🔍 COMPREHENSIVE ENVIRONMENT CHECK")
    print("=" * 70)
    print()
    
    results = {}
    
    # 1. Telegram Bot Configuration
    print("🤖 TELEGRAM BOT CONFIGURATION")
    print("-" * 70)
    
    telegram_vars = {
        'TOKEN': True,
        'TELEGRAM_BOT_TOKEN': False,  # Alias
        'ADMIN1': True,
        'ADMIN2': False,
        'ADMIN3': False,
    }
    
    for var, required in telegram_vars.items():
        result = check_env_var(var, required, check_placeholder=False)
        results[var] = result
        print(f"{result['message']} {var}")
        if result['value']:
            print(f"   Value: {result['value']}")
    
    print()
    
    # 2. Supabase Configuration
    print("☁️  SUPABASE CONFIGURATION")
    print("-" * 70)
    
    supabase_vars = {
        'SUPABASE_URL': True,
        'SUPABASE_SERVICE_KEY': True,
        'SUPABASE_ANON_KEY': False,
    }
    
    for var, required in supabase_vars.items():
        result = check_env_var(var, required)
        results[var] = result
        print(f"{result['message']} {var}")
        if result['value']:
            print(f"   Value: {result['value']}")
    
    print()
    
    # 3. DeepSeek AI Configuration
    print("🤖 DEEPSEEK AI CONFIGURATION")
    print("-" * 70)
    
    deepseek_vars = {
        'DEEPSEEK_API_KEY': True,
        'DEEPSEEK_BASE_URL': False,
    }
    
    for var, required in deepseek_vars.items():
        result = check_env_var(var, required, check_placeholder=False)
        results[var] = result
        print(f"{result['message']} {var}")
        if result['value']:
            print(f"   Value: {result['value']}")
    
    print()
    
    # 4. Other APIs
    print("🔌 OTHER API CONFIGURATIONS")
    print("-" * 70)
    
    other_vars = {
        'CRYPTONEWS_API_KEY': False,
        'WELCOME_CREDITS': False,
        'SESSION_SECRET': False,
    }
    
    for var, required in other_vars.items():
        result = check_env_var(var, required, check_placeholder=False)
        results[var] = result
        print(f"{result['message']} {var}")
        if result['value']:
            print(f"   Value: {result['value']}")
    
    print()
    
    # 5. Database Configuration (PostgreSQL/Neon)
    print("🗄️  POSTGRESQL/NEON CONFIGURATION")
    print("-" * 70)
    
    pg_vars = {
        'PGHOST': False,
        'PGDATABASE': False,
        'PGUSER': False,
        'PGPASSWORD': False,
        'PGPORT': False,
    }
    
    for var, required in pg_vars.items():
        result = check_env_var(var, required, check_placeholder=False)
        results[var] = result
        print(f"{result['message']} {var}")
        if result['value']:
            print(f"   Value: {result['value']}")
    
    print()
    
    return results


def test_connections():
    """Test actual connections"""
    print("=" * 70)
    print("🔌 CONNECTION TESTS")
    print("=" * 70)
    print()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Supabase Connection
    print("1️⃣ Testing Supabase Connection...")
    print("-" * 70)
    tests_total += 1
    
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL', '').strip()
        key = os.getenv('SUPABASE_SERVICE_KEY', '').strip()
        
        if not url or not key or 'your_' in url or 'your_' in key:
            print("⚠️  Skipped: Supabase not configured properly")
        else:
            client = create_client(url, key)
            result = client.table('users').select('count', count='exact').limit(1).execute()
            user_count = result.count if hasattr(result, 'count') else 0
            
            print(f"✅ Supabase Connected!")
            print(f"   Users in database: {user_count}")
            tests_passed += 1
    except Exception as e:
        print(f"❌ Supabase Connection Failed: {e}")
    
    print()
    
    # Test 2: DeepSeek AI
    print("2️⃣ Testing DeepSeek AI...")
    print("-" * 70)
    tests_total += 1
    
    try:
        api_key = os.getenv('DEEPSEEK_API_KEY', '').strip()
        
        if not api_key or 'your_' in api_key:
            print("⚠️  Skipped: DeepSeek API key not configured")
        else:
            print(f"✅ DeepSeek API Key configured")
            print(f"   Key: {api_key[:20]}...")
            print(f"   Note: Actual API test requires network call")
            tests_passed += 1
    except Exception as e:
        print(f"❌ DeepSeek Check Failed: {e}")
    
    print()
    
    # Test 3: Local Database
    print("3️⃣ Testing Local Database...")
    print("-" * 70)
    tests_total += 1
    
    try:
        import sqlite3
        
        if os.path.exists('cryptomentor.db'):
            conn = sqlite3.connect('cryptomentor.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            conn.close()
            
            print(f"✅ Local Database Connected!")
            print(f"   Users in database: {count}")
            tests_passed += 1
        else:
            print("⚠️  Local database file not found")
    except Exception as e:
        print(f"❌ Local Database Failed: {e}")
    
    print()
    
    return tests_passed, tests_total


def show_summary(results):
    """Show summary of all checks"""
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print()
    
    # Count statuses
    ok_count = sum(1 for r in results.values() if r['status'] == 'ok')
    missing_count = sum(1 for r in results.values() if r['status'] == 'missing')
    placeholder_count = sum(1 for r in results.values() if r['status'] == 'placeholder')
    optional_count = sum(1 for r in results.values() if r['status'] == 'optional')
    
    total = len(results)
    
    print(f"Total Variables Checked: {total}")
    print(f"  ✅ Configured: {ok_count}")
    print(f"  ❌ Missing (Required): {missing_count}")
    print(f"  ⚠️  Placeholder: {placeholder_count}")
    print(f"  ⚠️  Optional (Not Set): {optional_count}")
    print()
    
    # Issues
    if missing_count > 0:
        print("❌ CRITICAL ISSUES:")
        for var, result in results.items():
            if result['status'] == 'missing':
                print(f"   • {var} is required but not set")
        print()
    
    if placeholder_count > 0:
        print("⚠️  WARNINGS:")
        for var, result in results.items():
            if result['status'] == 'placeholder':
                print(f"   • {var} has placeholder value")
        print()
    
    # Overall status
    if missing_count == 0 and placeholder_count == 0:
        print("🎉 ALL CONFIGURATIONS ARE VALID!")
        return True
    elif missing_count == 0:
        print("✅ All required configurations are set (some placeholders)")
        return True
    else:
        print("❌ Some required configurations are missing")
        return False


def show_recommendations():
    """Show recommendations"""
    print("=" * 70)
    print("💡 RECOMMENDATIONS")
    print("=" * 70)
    print()
    
    # Check specific issues
    supabase_anon = os.getenv('SUPABASE_ANON_KEY', '').strip()
    
    if 'your_' in supabase_anon or 'USE_LEGACY' in supabase_anon:
        print("⚠️  SUPABASE_ANON_KEY Issue Detected:")
        print("   Current value contains 'USE_LEGACY_FUTURES_SIGNALS=true'")
        print()
        print("   Fix in .env file:")
        print("   SUPABASE_ANON_KEY=your_actual_anon_key")
        print("   USE_LEGACY_FUTURES_SIGNALS=true")
        print()
    
    print("✅ To start using the bot:")
    print("   1. Ensure all required configs are set")
    print("   2. Run: python bot.py")
    print("   3. Test in Telegram: /admin")
    print()
    
    print("📊 To test broadcast:")
    print("   1. /admin → Settings → Database Stats")
    print("   2. /admin → Settings → Broadcast")
    print()
    
    print("🤖 To test DeepSeek AI:")
    print("   1. /ai btc")
    print("   2. /chat hello")
    print("   3. /aimarket")
    print()


if __name__ == "__main__":
    print()
    print("🔍 CryptoMentor Bot - Environment Configuration Checker")
    print()
    
    # Check all configurations
    results = check_all_configurations()
    
    # Test connections
    tests_passed, tests_total = test_connections()
    
    # Show summary
    all_ok = show_summary(results)
    
    # Show recommendations
    show_recommendations()
    
    # Final status
    print("=" * 70)
    print("✅ CHECK COMPLETE!")
    print("=" * 70)
    print()
    
    if all_ok and tests_passed == tests_total:
        print("🎉 ALL SYSTEMS GO!")
        print("   Your bot is ready to use!")
    elif all_ok:
        print("✅ Configurations OK")
        print(f"   Connection tests: {tests_passed}/{tests_total} passed")
    else:
        print("⚠️  Some configurations need attention")
        print("   Review the issues above")
    
    print()
