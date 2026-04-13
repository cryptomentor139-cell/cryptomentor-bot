import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), "Bismillah"))
load_dotenv(os.path.join(os.getcwd(), "Bismillah", ".env"))

from app.supabase_repo import _client

def check_columns():
    try:
        c = _client()
        res = c.table("autotrade_trades").select("*").limit(1).execute()
        if res.data:
            print(f"Columns: {list(res.data[0].keys())}")
        else:
            print("No data in autotrade_trades")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_columns()
