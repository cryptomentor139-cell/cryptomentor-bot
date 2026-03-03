"""
Debug Automaton Connection
Check if Automaton dashboard is running and accessible
"""

import subprocess
import sqlite3
import os
from pathlib import Path

def check_automaton_dashboard():
    """Check if Automaton dashboard is running"""
    print("\n" + "="*60)
    print("1. CHECKING AUTOMATON DASHBOARD")
    print("="*60)
    
    try:
        # Check if node process is running
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq node.exe'],
            capture_output=True,
            text=True
        )
        
        if 'node.exe' in result.stdout:
            print("✅ Node.js process is running")
            print(f"   Processes found:")
            for line in result.stdout.split('\n'):
                if 'node.exe' in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ Node.js process NOT running")
            print("\n   To start Automaton dashboard:")
            print("   cd C:\\Users\\dragon\\automaton")
            print("   node dist/index.js --run")
            return False
    except Exception as e:
        print(f"❌ Error checking process: {e}")
        return False
    
    return True


def check_automaton_files():
    """Check if required Automaton files exist"""
    print("\n" + "="*60)
    print("2. CHECKING AUTOMATON FILES")
    print("="*60)
    
    automaton_dir = Path("C:/Users/dragon/automaton")
    send_task = automaton_dir / "send-task.js"
    dist_index = automaton_dir / "dist/index.js"
    
    all_exist = True
    
    # Check send-task.js
    if send_task.exists():
        print(f"✅ send-task.js exists")
        print(f"   Path: {send_task}")
    else:
        print(f"❌ send-task.js NOT FOUND")
        print(f"   Expected: {send_task}")
        all_exist = False
    
    # Check dist/index.js
    if dist_index.exists():
        print(f"✅ dist/index.js exists")
        print(f"   Path: {dist_index}")
    else:
        print(f"❌ dist/index.js NOT FOUND")
        print(f"   Expected: {dist_index}")
        all_exist = False
    
    return all_exist


def check_automaton_database():
    """Check if Automaton database is accessible"""
    print("\n" + "="*60)
    print("3. CHECKING AUTOMATON DATABASE")
    print("="*60)
    
    db_path = "C:/root/.automaton/state.db"
    
    # Check if file exists
    if not os.path.exists(db_path):
        print(f"❌ Database NOT FOUND")
        print(f"   Expected: {db_path}")
        return False
    
    print(f"✅ Database file exists")
    print(f"   Path: {db_path}")
    print(f"   Size: {os.path.getsize(db_path):,} bytes")
    
    # Try to connect and query
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n   Tables found: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check inbox_messages
        cursor.execute("SELECT COUNT(*) FROM inbox_messages")
        inbox_count = cursor.fetchone()[0]
        print(f"\n   Inbox messages: {inbox_count}")
        
        # Check turns
        cursor.execute("SELECT COUNT(*) FROM turns")
        turns_count = cursor.fetchone()[0]
        print(f"   Turns: {turns_count}")
        
        # Check last activity
        cursor.execute("SELECT timestamp FROM turns ORDER BY timestamp DESC LIMIT 1")
        last_turn = cursor.fetchone()
        if last_turn:
            print(f"   Last activity: {last_turn[0]}")
        else:
            print(f"   Last activity: None")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def test_send_task():
    """Test sending a simple task"""
    print("\n" + "="*60)
    print("4. TESTING SEND-TASK.JS")
    print("="*60)
    
    automaton_dir = "C:/Users/dragon/automaton"
    
    try:
        print("⏳ Sending test task...")
        result = subprocess.run(
            ['node', 'send-task.js', 'Hello from debug script'],
            cwd=automaton_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ send-task.js executed successfully")
            print(f"\n   Output:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"   {line}")
            
            # Extract task ID
            for line in result.stdout.split('\n'):
                if 'Task ID:' in line:
                    task_id = line.split('Task ID:')[1].strip()
                    print(f"\n   Task ID: {task_id}")
                    return task_id
        else:
            print(f"❌ send-task.js failed")
            print(f"   Error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ send-task.js timeout (> 10 seconds)")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def check_task_processing(task_id):
    """Check if task is being processed"""
    print("\n" + "="*60)
    print("5. CHECKING TASK PROCESSING")
    print("="*60)
    
    if not task_id:
        print("⚠️  No task ID to check")
        return
    
    db_path = "C:/root/.automaton/state.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if task exists in inbox
        cursor.execute("""
            SELECT id, content, received_at, processed_at 
            FROM inbox_messages 
            WHERE id = ?
        """, (task_id,))
        
        task = cursor.fetchone()
        
        if task:
            print(f"✅ Task found in inbox")
            print(f"   ID: {task[0]}")
            print(f"   Content: {task[1][:50]}...")
            print(f"   Received: {task[2]}")
            print(f"   Processed: {task[3] or 'Not yet'}")
            
            if task[3]:
                print("\n   ✅ Task has been processed!")
                
                # Get response
                cursor.execute("""
                    SELECT thinking FROM turns 
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC LIMIT 1
                """, (task[2],))
                
                response = cursor.fetchone()
                if response:
                    print(f"\n   Response (first 200 chars):")
                    print(f"   {response[0][:200]}...")
            else:
                print("\n   ⏳ Task not processed yet")
                print("   This means Automaton dashboard is NOT processing tasks")
                print("\n   Possible reasons:")
                print("   1. Dashboard not running")
                print("   2. Dashboard crashed")
                print("   3. Dashboard stuck")
        else:
            print(f"❌ Task NOT found in inbox")
            print(f"   Task ID: {task_id}")
            print("   This means send-task.js didn't insert the task")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all diagnostic checks"""
    print("\n" + "="*60)
    print("AUTOMATON CONNECTION DIAGNOSTIC")
    print("="*60)
    
    # Run checks
    dashboard_ok = check_automaton_dashboard()
    files_ok = check_automaton_files()
    db_ok = check_automaton_database()
    
    # Test send-task if everything looks good
    if files_ok and db_ok:
        task_id = test_send_task()
        
        if task_id:
            print("\n⏳ Waiting 10 seconds for processing...")
            import time
            time.sleep(10)
            check_task_processing(task_id)
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    
    print(f"Dashboard Running: {'✅' if dashboard_ok else '❌'}")
    print(f"Files Exist: {'✅' if files_ok else '❌'}")
    print(f"Database OK: {'✅' if db_ok else '❌'}")
    
    if not dashboard_ok:
        print("\n🔧 ACTION REQUIRED:")
        print("   Start Automaton dashboard:")
        print("   1. Open new terminal")
        print("   2. cd C:\\Users\\dragon\\automaton")
        print("   3. node dist/index.js --run")
        print("   4. Keep terminal open")
        print("   5. Run this diagnostic again")
    elif not files_ok:
        print("\n🔧 ACTION REQUIRED:")
        print("   Check Automaton installation")
        print("   Ensure send-task.js and dist/index.js exist")
    elif not db_ok:
        print("\n🔧 ACTION REQUIRED:")
        print("   Check database at C:/root/.automaton/state.db")
        print("   May need to initialize Automaton")
    else:
        print("\n✅ All checks passed!")
        print("   If AI signal still fails, check Automaton dashboard logs")
    
    print("="*60)


if __name__ == "__main__":
    main()
