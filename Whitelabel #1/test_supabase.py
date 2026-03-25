"""Test koneksi Supabase WL#1"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

import config as wl_config

print(f"SUPABASE_URL: {wl_config.SUPABASE_URL}")
print(f"SERVICE_KEY: {'SET' if wl_config.SUPABASE_SERVICE_KEY else 'MISSING'}")

try:
    from supabase import create_client
    client = create_client(wl_config.SUPABASE_URL, wl_config.SUPABASE_SERVICE_KEY)
    # Coba query tabel users
    res = client.table("users").select("count", count="exact").execute()
    print(f"✅ Supabase connected! users table count: {res.count}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
