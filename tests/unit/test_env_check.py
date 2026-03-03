from dotenv import load_dotenv
load_dotenv()

import os

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print(f"SUPABASE_URL: {SUPABASE_URL[:20] if SUPABASE_URL else 'NOT SET'}")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:20] if SUPABASE_KEY else 'NOT SET'}")
print(f"SUPABASE_URL bool: {bool(SUPABASE_URL)}")
print(f"SUPABASE_KEY bool: {bool(SUPABASE_KEY)}")
print(f"Check result: {not SUPABASE_URL or not SUPABASE_KEY}")
