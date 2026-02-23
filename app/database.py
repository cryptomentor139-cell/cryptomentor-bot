"""
Database helper functions for AI Agent education and user data
"""

from database import Database

def get_user_data(user_id: int) -> dict:
    """
    Get user data including education flags
    """
    db = Database()
    
    # Try to get from Supabase first
    if db.supabase_enabled:
        try:
            from supabase_client import supabase
            if supabase:
                result = supabase.table('users')\
                    .select('user_data')\
                    .eq('user_id', user_id)\
                    .execute()
                
                if result.data and result.data[0].get('user_data'):
                    return result.data[0]['user_data']
        except Exception as e:
            print(f"⚠️ Error getting user data from Supabase: {e}")
    
    # Fallback to empty dict
    return {}


def update_user_data(user_id: int, data: dict):
    """
    Update user data (merge with existing data)
    """
    db = Database()
    
    # Get existing data
    existing_data = get_user_data(user_id)
    
    # Merge with new data
    existing_data.update(data)
    
    # Update in Supabase
    if db.supabase_enabled:
        try:
            from supabase_client import supabase
            if supabase:
                supabase.table('users')\
                    .update({'user_data': existing_data})\
                    .eq('user_id', user_id)\
                    .execute()
                
                print(f"✅ User data updated for {user_id}: {data}")
        except Exception as e:
            print(f"⚠️ Error updating user data in Supabase: {e}")
