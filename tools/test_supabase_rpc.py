
import os
import sys
from supabase import create_client, Client

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not URL or not KEY:
    print("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in environment.")
    sys.exit(1)

supabase: Client = create_client(URL, KEY)

DUMMY_TG = 999999999  # ganti kalau mau

def ensure_user():
    data = {
        "telegram_id": DUMMY_TG,
        "username": "dummyuser",
        "first_name": "Dummy",
        "last_name": "Tester",
    }
    res = supabase.table("users").upsert(data, on_conflict="telegram_id").select("*").execute()
    return res.data[0]

def call_set_premium_lifetime():
    res = supabase.rpc("set_premium", {
        "p_telegram_id": DUMMY_TG,
        "p_duration_value": 0,
        "p_duration_type": "lifetime"
    }).execute()
    print("set_premium(lifetime) OK", res.data)

def call_debit_credits(amount: int):
    res = supabase.rpc("debit_credits", {
        "p_telegram_id": DUMMY_TG,
        "p_amount": amount
    }).execute()
    print(f"debit_credits({amount}) remaining =", res.data)

def show_user():
    res = supabase.table("users").select("*").eq("telegram_id", DUMMY_TG).limit(1).execute()
    print("User row =", res.data[0] if res.data else None)

if __name__ == "__main__":
    print("== Supabase RPC Smoke Test ==")
    u = ensure_user()
    show_user()
    call_set_premium_lifetime()
    show_user()
    # seed credits dulu biar debit terlihat
    supabase.table("users").update({"credits": 10}).eq("telegram_id", DUMMY_TG).execute()
    call_debit_credits(3)
    show_user()
    print("Done.")
