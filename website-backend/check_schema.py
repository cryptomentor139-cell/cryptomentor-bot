from app.db.supabase import _client
s = _client()

# Cek kolom autotrade_sessions
res = s.table("autotrade_sessions").select("*").limit(1).execute()
if res.data:
    print("autotrade_sessions columns:", list(res.data[0].keys()))
else:
    print("autotrade_sessions: no data, insert dummy to check schema")
    # Coba insert minimal untuk lihat error
    try:
        s.table("autotrade_sessions").select("telegram_id").limit(1).execute()
        print("table exists but empty")
    except Exception as e:
        print("error:", e)

# Cek kolom autotrade_trades
res2 = s.table("autotrade_trades").select("*").limit(1).execute()
if res2.data:
    print("autotrade_trades columns:", list(res2.data[0].keys()))
else:
    print("autotrade_trades: empty")
