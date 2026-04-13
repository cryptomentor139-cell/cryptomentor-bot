from supabase import create_client
import os

url = 'https://xrbqnocovfymdikngaza.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTMyMTE5OSwiZXhwIjoyMDcwODk3MTk5fQ.QGIlCWKqy8fe0bKJbx6CAqeSr7fq17NBXqNeC8nUu5Y'

try:
    s = create_client(url, key)
    
    # Fetch data
    users = s.table('users').select('telegram_id').execute().data
    verifications = s.table('user_verifications').select('telegram_id, status').execute().data
    api_keys = s.table('user_api_keys').select('telegram_id').execute().data
    sessions = s.table('autotrade_sessions').select('*').execute().data
    
    # Process
    total_users = len(users)
    verified_users = len([x for x in verifications if x.get('status') in ('approved', 'uid_verified', 'active', 'verified')])
    users_with_keys = len(set([x.get('telegram_id') for x in api_keys]))
    
    active_sessions = len([x for x in sessions if x.get('status') == 'active'])
    engines_engaged = len([x for x in sessions if x.get('engine_active')])
    
    scalping_count = len([x for x in sessions if x.get('trading_mode') == 'scalping'])
    swing_count = len([x for x in sessions if x.get('trading_mode') == 'swing'])
    
    total_balance = sum([float(x.get('current_balance') or 0) for x in sessions])
    total_profit = sum([float(x.get('total_profit') or 0) for x in sessions])
    
    print("--- TRADING ENGINE USER STATS ---")
    print(f"Total Registered Users: {total_users}")
    print(f"Verified Users: {verified_users}")
    print(f"Users with API Keys: {users_with_keys}")
    print(f"Active Autotrade Sessions: {active_sessions}")
    print(f"Engines Currently Engaged: {engines_engaged}")
    print("\nMode Distribution:")
    print(f"  Scalping Mode: {scalping_count}")
    print(f"  Swing Mode: {swing_count}")
    print("\nFinancial Aggregates:")
    print(f"  Total Managed Balance: {total_balance:,.2f} USDT")
    print(f"  Total Accumulated Profit: {total_profit:,.2f} USDT")

except Exception as e:
    print(f"Error fetching stats: {e}")
