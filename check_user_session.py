from supabase import create_client

url = "https://xrbqnocovfymdikngaza.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTMyMTE5OSwiZXhwIjoyMDcwODk3MTk5fQ.QGIlCWKqy8fe0bKJbx6CAqeSr7fq17NBXqNeC8nUu5Y"
supabase = create_client(url, key)

tg_id = 7675185179
res = supabase.table("autotrade_sessions").select("*").eq("telegram_id", tg_id).execute()
print(res.data)
