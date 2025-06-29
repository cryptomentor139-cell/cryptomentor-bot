
#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime
from database import Database

def check_database_health():
    """Comprehensive database health check for CryptoMentor"""
    print("🔍 CryptoMentor Database Health Check")
    print("=" * 50)
    
    try:
        # Initialize database connection
        db = Database()
        print("✅ Database connection successful")
        
        # Check database file
        db_path = "cryptomentor.db"
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            print(f"📁 Database file: {db_path} ({file_size} bytes)")
        else:
            print("❌ Database file not found!")
            return
        
        print("\n📊 Table Structure Analysis:")
        
        # Check users table
        try:
            db.cursor.execute("PRAGMA table_info(users)")
            users_columns = db.cursor.fetchall()
            print(f"👥 Users table: {len(users_columns)} columns")
            
            # Check for required columns
            required_columns = ['telegram_id', 'is_premium', 'credits', 'subscription_end']
            existing_columns = [col[1] for col in users_columns]
            
            missing_columns = []
            for col in required_columns:
                if col in existing_columns:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ {col} - MISSING")
                    missing_columns.append(col)
            
            if missing_columns:
                print(f"⚠️  Missing columns detected: {missing_columns}")
            
        except Exception as e:
            print(f"❌ Error checking users table: {e}")
        
        # Check user data integrity
        print("\n🔍 User Data Integrity Check:")
        
        try:
            # Count total users
            db.cursor.execute("SELECT COUNT(*) FROM users")
            total_users = db.cursor.fetchone()[0]
            print(f"👥 Total users: {total_users}")
            
            # Check users with NULL telegram_id
            db.cursor.execute("SELECT COUNT(*) FROM users WHERE telegram_id IS NULL")
            null_telegram_id = db.cursor.fetchone()[0]
            if null_telegram_id > 0:
                print(f"❌ Users with NULL telegram_id: {null_telegram_id}")
            else:
                print("✅ All users have valid telegram_id")
            
            # Check premium users
            db.cursor.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
            premium_users = db.cursor.fetchone()[0]
            print(f"⭐ Premium users: {premium_users}")
            
            # Check users with zero or negative credits
            db.cursor.execute("SELECT COUNT(*) FROM users WHERE credits <= 0")
            zero_credits = db.cursor.fetchone()[0]
            print(f"💳 Users with 0 or negative credits: {zero_credits}")
            
            # Check users with NULL credits
            db.cursor.execute("SELECT COUNT(*) FROM users WHERE credits IS NULL")
            null_credits = db.cursor.fetchone()[0]
            if null_credits > 0:
                print(f"❌ Users with NULL credits: {null_credits}")
            else:
                print("✅ All users have valid credits")
            
            # Sample users data
            print("\n📋 Sample User Data:")
            db.cursor.execute("SELECT telegram_id, first_name, is_premium, credits, subscription_end FROM users LIMIT 5")
            sample_users = db.cursor.fetchall()
            
            for user in sample_users:
                telegram_id, first_name, is_premium, credits, sub_end = user
                status = "Premium" if is_premium else "Free"
                print(f"   • {telegram_id} ({first_name}): {status}, {credits} credits")
                
                # Check premium users without subscription_end
                if is_premium and sub_end is None:
                    print(f"     ℹ️  Permanent premium user")
                elif is_premium and sub_end:
                    try:
                        end_date = datetime.fromisoformat(sub_end)
                        if datetime.now() > end_date:
                            print(f"     ⚠️  Premium expired: {sub_end}")
                        else:
                            print(f"     ✅ Premium valid until: {sub_end}")
                    except ValueError:
                        print(f"     ❌ Invalid subscription_end format: {sub_end}")
            
        except Exception as e:
            print(f"❌ Error checking user data: {e}")
        
        # Check other tables
        print("\n📊 Other Tables:")
        
        tables = ['subscriptions', 'portfolio', 'user_activity']
        for table in tables:
            try:
                db.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = db.cursor.fetchone()[0]
                print(f"📋 {table}: {count} records")
            except Exception as e:
                print(f"❌ Table {table}: {e}")
        
        # Check for database corruption
        print("\n🔍 Database Integrity Check:")
        try:
            db.cursor.execute("PRAGMA integrity_check")
            integrity_result = db.cursor.fetchone()[0]
            if integrity_result == "ok":
                print("✅ Database integrity: OK")
            else:
                print(f"❌ Database integrity issue: {integrity_result}")
        except Exception as e:
            print(f"❌ Error checking integrity: {e}")
        
        # Test critical database operations
        print("\n🧪 Database Operations Test:")
        
        try:
            # Test user lookup
            test_user = db.get_user(123456789)  # Non-existent user
            print("✅ User lookup: Working")
            
            # Test credit operations
            test_credits = db.get_user_credits(123456789)
            print("✅ Credit operations: Working")
            
            # Test premium check
            test_premium = db.is_user_premium(123456789)
            print("✅ Premium check: Working")
            
        except Exception as e:
            print(f"❌ Database operations error: {e}")
        
        # Memory usage check
        print("\n💾 Database Performance:")
        try:
            db.cursor.execute("PRAGMA page_count")
            page_count = db.cursor.fetchone()[0]
            
            db.cursor.execute("PRAGMA page_size")
            page_size = db.cursor.fetchone()[0]
            
            total_size = page_count * page_size
            print(f"📊 Database size: {total_size:,} bytes ({page_count:,} pages)")
            
            # Check for unused space
            db.cursor.execute("PRAGMA freelist_count")
            free_pages = db.cursor.fetchone()[0]
            if free_pages > page_count * 0.1:  # More than 10% free space
                print(f"⚠️  High fragmentation: {free_pages} free pages")
                print("💡 Consider running VACUUM to optimize")
            else:
                print("✅ Database fragmentation: Normal")
                
        except Exception as e:
            print(f"❌ Error checking performance: {e}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        
        if null_telegram_id > 0:
            print("• Fix users with NULL telegram_id")
        
        if null_credits > 0:
            print("• Fix users with NULL credits")
        
        if zero_credits > total_users * 0.8:  # More than 80% users have 0 credits
            print("• Consider running credit fix for existing users")
        
        print("• Regular database backups recommended")
        print("• Monitor premium user expiration dates")
        
        db.conn.close()
        print("\n✅ Database health check completed!")
        
    except Exception as e:
        print(f"❌ Critical database error: {e}")
        print("🔧 Database may need repair or recreation")

def fix_common_issues():
    """Fix common database issues"""
    print("\n🔧 Auto-fixing common issues...")
    
    try:
        db = Database()
        
        # Fix NULL credits
        db.cursor.execute("UPDATE users SET credits = 10 WHERE credits IS NULL")
        null_credits_fixed = db.cursor.rowcount
        
        # Fix users with negative credits
        db.cursor.execute("UPDATE users SET credits = 0 WHERE credits < 0")
        negative_credits_fixed = db.cursor.rowcount
        
        # Fix expired premium users
        db.cursor.execute("""
            UPDATE users SET is_premium = 0 
            WHERE is_premium = 1 
            AND subscription_end IS NOT NULL 
            AND datetime(subscription_end) < datetime('now')
        """)
        expired_premium_fixed = db.cursor.rowcount
        
        db.conn.commit()
        
        print(f"✅ Fixed NULL credits: {null_credits_fixed} users")
        print(f"✅ Fixed negative credits: {negative_credits_fixed} users") 
        print(f"✅ Fixed expired premium: {expired_premium_fixed} users")
        
        db.conn.close()
        
    except Exception as e:
        print(f"❌ Error during auto-fix: {e}")

if __name__ == "__main__":
    check_database_health()
    
    # Ask if user wants to fix issues
    print("\n" + "="*50)
    fix_issues = input("🔧 Run auto-fix for common issues? (y/n): ").lower().strip()
    
    if fix_issues == 'y':
        fix_common_issues()
        print("\n🔄 Re-running health check after fixes...")
        check_database_health()
