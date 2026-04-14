import sys
sys.path.append('D:/cryptomentorAI/Bismillah')
from app.supabase_repo import SupabaseRepo
import asyncio

async def test():
    repo = SupabaseRepo()
    session = await repo.get_autotrade_session('7972497694')
    print("Session:", session)
    
if __name__ == '__main__':
    asyncio.run(test())
