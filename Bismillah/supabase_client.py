import os
from supabase import create_client, Client
from datetime import datetime, timedelta, timezone

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def validate_supabase_connection():
    """Validate Supabase connection and tables"""
    try:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment variables")
            print("💡 Please add them to Replit Secrets")
            return False

        # Test connection with service role key
        test_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        # Try to access users table
        result = test_client.table('users').select('count', count='exact').limit(1).execute()

        print("✅ Supabase connection validated successfully")
        print(f"📊 Users table accessible with {result.count or 0} records")
        return True

    except Exception as e:
        error_msg = str(e)
        if "PGRST205" in error_msg:
            print("❌ Table 'users' not found in Supabase database")
            print("💡 Run: python setup_supabase_tables.py to create tables")
        elif "PGRST301" in error_msg:
            print("❌ Authentication failed - check SUPABASE_SERVICE_ROLE_KEY")
        elif "PGRST000" in error_msg:
            print("❌ Connection failed - check SUPABASE_URL")
        else:
            print(f"❌ Supabase validation failed: {error_msg}")

        return False

# Validate that required environment variables are present
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment variables")
    print("💡 Please add them to Replit Secrets:")
    print("   - SUPABASE_URL: Your Supabase project URL")
    print("   - SUPABASE_SERVICE_ROLE_KEY: Your Supabase service role key")
    # Don't raise exception, let bot continue with limited functionality
    supabase = None
    print("⚠️ Bot will continue with limited functionality (no Supabase)")
else:
    # Create Supabase client using service role key only
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    print("✅ Supabase client initialized successfully")
    print(f"🔗 URL: {SUPABASE_URL}")
    print(f"🔑 Service Role Client: ✅ Ready")

# CRUD Functions for User Management
def add_user(user_id, username=None, is_premium=False, expired_date=None, first_name=None, last_name=None):
    """Add a new user to Supabase users table"""
    if not supabase:
        print("⚠️ Supabase not available")
        return {"success": False, "error": "Supabase not configured"}

    try:
        # Ensure telegram_id is properly typed as int8
        telegram_id = int(user_id) if user_id else None
        if not telegram_id:
            error_msg = f"Invalid telegram_id: {user_id}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        user_data = {
            'telegram_id': telegram_id,
            'username': username or 'no_username',
            'first_name': first_name or 'Unknown',
            'last_name': last_name,
            'is_premium': bool(is_premium),
            'credits': 100,  # Default credits
            'language_code': 'id'  # Default Indonesian
        }

        if expired_date:
            user_data['subscription_end'] = expired_date

        print(f"📝 Inserting user payload: {user_data}")

        result = supabase.table('users').upsert(user_data, on_conflict='telegram_id').execute()

        print(f"📤 Supabase response: {result}")

        if result.data:
            print(f"✅ User {user_id} added/updated successfully")

            # Immediately verify user count
            count_result = supabase.table('users').select('count', count='exact').execute()
            total_users = count_result.count if hasattr(count_result, 'count') else 0
            print(f"📊 Total users after insert: {total_users}")

            return {"success": True, "data": result.data[0]}
        else:
            error_msg = f"No data returned from Supabase for user {user_id}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    except Exception as e:
        error_msg = f"Error adding user {user_id}: {str(e)}"
        print(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}

def get_user(user_id):
    """Get user data from Supabase"""
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}

    try:
        result = supabase.table('users').select('*').eq('telegram_id', int(user_id)).execute()

        if result.data:
            print(f"✅ User {user_id} found")
            return {"success": True, "data": result.data[0]}
        else:
            print(f"⚠️ User {user_id} not found")
            return {"success": False, "error": "User not found"}

    except Exception as e:
        print(f"❌ Error getting user {user_id}: {e}")
        return {"success": False, "error": str(e)}

def update_user(user_id, data_dict):
    """Update user data in Supabase"""
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}

    try:
        # Ensure we don't update telegram_id accidentally
        update_data = {k: v for k, v in data_dict.items() if k != 'telegram_id'}

        print(f"📝 Updating user {user_id} with payload: {update_data}")

        result = supabase.table('users').update(update_data).eq('telegram_id', int(user_id)).execute()

        print(f"📤 Supabase update response: {result}")

        if result.data:
            print(f"✅ User {user_id} updated successfully")
            return {"success": True, "data": result.data[0]}
        else:
            error_msg = f"No data updated for user {user_id}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    except Exception as e:
        error_msg = f"Error updating user {user_id}: {str(e)}"
        print(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}

def delete_user(user_id):
    """Delete user from Supabase"""
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}

    try:
        print(f"🗑️ Deleting user {user_id}")

        result = supabase.table('users').delete().eq('telegram_id', int(user_id)).execute()

        print(f"📤 Supabase delete response: {result}")

        if result.data:
            print(f"✅ User {user_id} deleted successfully")
            return {"success": True, "data": result.data[0]}
        else:
            error_msg = f"User {user_id} not found or already deleted"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    except Exception as e:
        error_msg = f"Error deleting user {user_id}: {str(e)}"
        print(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}

def add_premium(user_id, duration_days=None):
    """Add premium status to user"""
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}

    try:
        if duration_days == "lifetime":
            # Lifetime premium
            premium_until = "9999-12-31T23:59:59+00:00"
        elif duration_days:
            # Calculate expiry date
            try:
                days = int(duration_days)
                premium_until = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
            except ValueError:
                return {"success": False, "error": "Invalid duration format"}
        else:
            # Default 30 days
            premium_until = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

        update_data = {
            "is_premium": True,
            "subscription_end": premium_until
        }

        return update_user(user_id, update_data)

    except Exception as e:
        return {"success": False, "error": str(e)}

def revoke_premium(user_id):
    """Revoke premium status from user"""
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}

    try:
        update_data = {
            "is_premium": False,
            "subscription_end": None
        }

        return update_user(user_id, update_data)

    except Exception as e:
        return {"success": False, "error": str(e)}

def get_live_user_count():
    """Get live user count directly from Supabase"""
    if not supabase:
        return 0

    try:
        result = supabase.table('users').select('count', count='exact').execute()
        count = result.count if hasattr(result, 'count') else 0
        print(f"📊 Live user count from Supabase: {count}")
        return count
    except Exception as e:
        print(f"❌ Error getting live user count: {e}")
        return 0

# Validate connection on import
if supabase and not validate_supabase_connection():
    print("⚠️ Supabase validation failed - bot will continue with limited functionality")
    print("🔧 To fix: Add SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to Replit Secrets")
elif supabase:
    print("✅ Supabase fully operational")
    print(f"📊 Current user count: {get_live_user_count()}")