"""
Analyze database overlap - kenapa hanya sedikit unique users dari Supabase
"""
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

def analyze_databases():
    """Analyze both databases in detail"""
    print("=" * 70)
    print("🔍 DETAILED DATABASE ANALYSIS")
    print("=" * 70)
    print()
    
    # Get local database users
    print("📊 Step 1: Analyzing Local Database...")
    print("-" * 70)
    
    conn = sqlite3.connect("cryptomentor.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT telegram_id FROM users 
        WHERE telegram_id IS NOT NULL 
        AND telegram_id != 0
        AND telegram_id != ''
        AND (banned IS NULL OR banned = 0)
    """)
    
    local_ids = set()
    for row in cursor.fetchall():
        try:
            local_ids.add(int(row[0]))
        except:
            pass
    
    conn.close()
    
    print(f"✅ Local Database: {len(local_ids)} valid users")
    print()
    
    # Get Supabase users
    print("📊 Step 2: Analyzing Supabase Database...")
    print("-" * 70)
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        client = create_client(supabase_url, supabase_key)
        
        result = client.table('users')\
            .select('telegram_id')\
            .not_.is_('telegram_id', 'null')\
            .neq('telegram_id', 0)\
            .execute()
        
        supabase_ids = set()
        invalid_ids = []
        
        for user in result.data:
            tid = user.get('telegram_id')
            if tid:
                try:
                    supabase_ids.add(int(tid))
                except:
                    invalid_ids.append(tid)
        
        print(f"✅ Supabase Database: {len(supabase_ids)} valid users")
        if invalid_ids:
            print(f"⚠️  Invalid IDs found: {len(invalid_ids)}")
            print(f"   Examples: {invalid_ids[:5]}")
        print()
        
        # Analyze overlap
        print("📊 Step 3: Analyzing Overlap...")
        print("-" * 70)
        
        # Users in both databases
        in_both = local_ids & supabase_ids
        
        # Users only in local
        only_local = local_ids - supabase_ids
        
        # Users only in Supabase
        only_supabase = supabase_ids - local_ids
        
        print(f"🔄 In BOTH databases: {len(in_both)} users ({len(in_both)/len(local_ids)*100:.1f}% of local)")
        print(f"🗄️  ONLY in Local: {len(only_local)} users")
        print(f"☁️  ONLY in Supabase: {len(only_supabase)} users")
        print()
        
        # Total unique
        total_unique = len(local_ids | supabase_ids)
        print(f"🎯 Total Unique Users: {total_unique}")
        print()
        
        # Show sample IDs
        print("📋 Sample Analysis:")
        print("-" * 70)
        
        if only_supabase:
            print(f"\n✅ Users ONLY in Supabase (first 10):")
            for i, uid in enumerate(list(only_supabase)[:10], 1):
                print(f"   {i}. ID: {uid}")
        else:
            print("\n⚠️  No users found ONLY in Supabase!")
            print("   All Supabase users are already in Local database")
        
        if only_local:
            print(f"\n📊 Users ONLY in Local (first 10):")
            for i, uid in enumerate(list(only_local)[:10], 1):
                print(f"   {i}. ID: {uid}")
        
        print()
        
        # Detailed breakdown
        print("=" * 70)
        print("📈 DETAILED BREAKDOWN")
        print("=" * 70)
        print()
        
        print(f"Local Database:")
        print(f"  • Total users: {len(local_ids)}")
        print(f"  • Also in Supabase: {len(in_both)} ({len(in_both)/len(local_ids)*100:.1f}%)")
        print(f"  • Unique to Local: {len(only_local)} ({len(only_local)/len(local_ids)*100:.1f}%)")
        print()
        
        print(f"Supabase Database:")
        print(f"  • Total users: {len(supabase_ids)}")
        print(f"  • Also in Local: {len(in_both)} ({len(in_both)/len(supabase_ids)*100:.1f}%)")
        print(f"  • Unique to Supabase: {len(only_supabase)} ({len(only_supabase)/len(supabase_ids)*100:.1f}%)")
        print()
        
        print(f"Combined:")
        print(f"  • Total Unique: {total_unique}")
        print(f"  • Duplicates: {len(in_both)}")
        print(f"  • Duplication Rate: {len(in_both)/total_unique*100:.1f}%")
        print()
        
        # Explanation
        print("=" * 70)
        print("💡 EXPLANATION")
        print("=" * 70)
        print()
        
        if len(only_supabase) < 50:
            print("⚠️  KENAPA HANYA SEDIKIT UNIQUE USERS DARI SUPABASE?")
            print()
            print("Alasan:")
            print(f"  1. Mayoritas users Supabase ({len(in_both)}/{len(supabase_ids)}) sudah ada di Local")
            print(f"  2. Hanya {len(only_supabase)} users yang benar-benar unique di Supabase")
            print(f"  3. Duplication rate sangat tinggi: {len(in_both)/total_unique*100:.1f}%")
            print()
            print("Kemungkinan penyebab:")
            print("  • Bot sudah sync data dari Supabase ke Local sebelumnya")
            print("  • Users baru lebih banyak masuk ke Local database")
            print("  • Supabase mungkin database backup/secondary")
            print()
        else:
            print("✅ Ada banyak unique users di Supabase!")
            print(f"   {len(only_supabase)} users hanya ada di Supabase")
            print()
        
        # Recommendations
        print("=" * 70)
        print("🎯 BROADCAST REACH")
        print("=" * 70)
        print()
        
        print(f"Saat ini broadcast akan mencapai: {total_unique} unique users")
        print()
        print("Breakdown:")
        print(f"  • Dari Local: {len(local_ids)} users")
        print(f"  • Tambahan dari Supabase: {len(only_supabase)} users")
        print(f"  • Total: {total_unique} users")
        print()
        
        if len(only_supabase) < 50:
            print("💡 Untuk meningkatkan reach:")
            print("  1. Fokus menambah users baru (keduanya akan tersimpan)")
            print("  2. Pastikan bot menyimpan ke kedua database")
            print("  3. Broadcast sudah optimal untuk data yang ada")
        
        print()
        
        return {
            'local': len(local_ids),
            'supabase': len(supabase_ids),
            'both': len(in_both),
            'only_local': len(only_local),
            'only_supabase': len(only_supabase),
            'total_unique': total_unique
        }
        
    except Exception as e:
        print(f"❌ Error analyzing Supabase: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print()
    print("🔍 Database Overlap Analysis Tool")
    print()
    
    result = analyze_databases()
    
    if result:
        print("=" * 70)
        print("✅ Analysis Complete!")
        print("=" * 70)
        print()
        print(f"📊 Summary:")
        print(f"   • Broadcast akan mencapai {result['total_unique']} unique users")
        print(f"   • {result['only_supabase']} users tambahan dari Supabase")
        print(f"   • {result['both']} users duplikat (otomatis dihapus)")
        print()
    else:
        print("❌ Analysis failed. Check errors above.")
    
    print()
