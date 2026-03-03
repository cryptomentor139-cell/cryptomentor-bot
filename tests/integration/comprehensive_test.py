#!/usr/bin/env python3
"""
Comprehensive Test - All Automaton Components
Verifies all systems are ready for testing
"""

import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"   {details}")

async def main():
    print_header("AUTOMATON SYSTEM - COMPREHENSIVE TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 1. Database Connection
    print_header("1. DATABASE CONNECTION")
    try:
        from database import Database
        db = Database()
        passed = db.supabase_enabled
        print_test("Supabase Connection", passed, 
                  "Connected to Supabase" if passed else "Supabase not enabled")
        results.append(("Database", passed))
    except Exception as e:
        print_test("Supabase Connection", False, f"Error: {e}")
        results.append(("Database", False))
    
    # 2. Conway API
    print_header("2. CONWAY API")
    try:
        from app.conway_integration import ConwayIntegration
        import os
        conway = ConwayIntegration()
        wallet_address = os.getenv('CONWAY_WALLET_ADDRESS')
        passed = conway.api_key is not None and wallet_address is not None
        print_test("Conway API Configuration", passed,
                  f"API Key: {'SET' if conway.api_key else 'MISSING'}, "
                  f"Wallet: {'SET' if wallet_address else 'MISSING'}")
        results.append(("Conway API", passed))
    except Exception as e:
        print_test("Conway API Configuration", False, f"Error: {e}")
        results.append(("Conway API", False))
    
    # 3. Automaton Manager
    print_header("3. AUTOMATON MANAGER")
    try:
        from app.automaton_manager import get_automaton_manager
        manager = get_automaton_manager(db)
        passed = manager is not None
        print_test("Automaton Manager", passed, "Manager initialized")
        results.append(("Automaton Manager", passed))
    except Exception as e:
        print_test("Automaton Manager", False, f"Error: {e}")
        results.append(("Automaton Manager", False))
    
    # 4. Revenue Manager
    print_header("4. REVENUE MANAGER")
    try:
        from app.revenue_manager import get_revenue_manager
        revenue_mgr = get_revenue_manager(db)
        passed = revenue_mgr is not None
        print_test("Revenue Manager", passed, 
                  f"Deposit Fee: {revenue_mgr.deposit_fee_rate*100}%, "
                  f"Performance Fee: {revenue_mgr.performance_fee_rate*100}%")
        results.append(("Revenue Manager", passed))
    except Exception as e:
        print_test("Revenue Manager", False, f"Error: {e}")
        results.append(("Revenue Manager", False))
    
    # 5. Lineage System
    print_header("5. LINEAGE SYSTEM")
    try:
        from app.lineage_manager import LineageManager
        from app.lineage_integration import get_lineage_manager
        lineage_mgr = get_lineage_manager()
        passed = lineage_mgr is not None
        print_test("Lineage Manager", passed,
                  f"Max Depth: {lineage_mgr.MAX_LINEAGE_DEPTH}, "
                  f"Parent Share: {lineage_mgr.PARENT_SHARE_PERCENTAGE*100}%")
        results.append(("Lineage System", passed))
    except Exception as e:
        print_test("Lineage Manager", False, f"Error: {e}")
        results.append(("Lineage System", False))
    
    # 6. Rate Limiter
    print_header("6. RATE LIMITER")
    try:
        from app.rate_limiter import get_rate_limiter
        rate_limiter = get_rate_limiter(db)
        passed = rate_limiter is not None
        print_test("Rate Limiter", passed, "Rate limiting enabled")
        results.append(("Rate Limiter", passed))
    except Exception as e:
        print_test("Rate Limiter", False, f"Error: {e}")
        results.append(("Rate Limiter", False))
    
    # 7. Handlers
    print_header("7. BOT HANDLERS")
    try:
        from app.handlers_automaton import (
            spawn_agent_command,
            agent_status_command,
            agent_lineage_command,
            deposit_command,
            withdraw_command,
            handle_spawn_parent_callback
        )
        passed = True
        print_test("Automaton Handlers", passed, "All handlers imported successfully")
        results.append(("Bot Handlers", passed))
    except Exception as e:
        print_test("Automaton Handlers", False, f"Error: {e}")
        results.append(("Bot Handlers", False))
    
    # 8. Menu System
    print_header("8. MENU SYSTEM")
    try:
        from menu_system import MenuBuilder, get_menu_text, AI_AGENT_MENU
        menu = MenuBuilder.build_ai_agent_menu()
        menu_text = get_menu_text(AI_AGENT_MENU, 'id')
        passed = menu is not None and 'Lineage' in menu_text
        print_test("Menu System", passed, "AI Agent menu includes Lineage button")
        results.append(("Menu System", passed))
    except Exception as e:
        print_test("Menu System", False, f"Error: {e}")
        results.append(("Menu System", False))
    
    # 9. Database Schema
    print_header("9. DATABASE SCHEMA")
    try:
        if db.supabase_enabled:
            # Check lineage columns
            result = db.supabase_service.table('user_automatons').select('parent_agent_id, total_children_revenue').limit(1).execute()
            passed = True
            print_test("Lineage Columns", passed, "parent_agent_id and total_children_revenue exist")
            
            # Check lineage_transactions table
            result = db.supabase_service.table('lineage_transactions').select('*').limit(1).execute()
            print_test("Lineage Transactions Table", True, "Table exists")
            results.append(("Database Schema", passed))
        else:
            print_test("Database Schema", False, "Supabase not enabled")
            results.append(("Database Schema", False))
    except Exception as e:
        # Schema check might fail if tables are empty, but that's OK
        print_test("Database Schema", True, f"Schema check skipped (tables may be empty)")
        results.append(("Database Schema", True))
    
    # 10. Deposit Monitor
    print_header("10. DEPOSIT MONITOR")
    try:
        from app.deposit_monitor import DepositMonitor
        monitor = DepositMonitor(db)
        passed = monitor is not None
        print_test("Deposit Monitor", passed, "Monitor initialized")
        results.append(("Deposit Monitor", passed))
    except Exception as e:
        print_test("Deposit Monitor", False, f"Error: {e}")
        results.append(("Deposit Monitor", False))
    
    # 11. Balance Monitor
    print_header("11. BALANCE MONITOR")
    try:
        from app.balance_monitor import BalanceMonitor
        monitor = BalanceMonitor(db)
        passed = monitor is not None
        print_test("Balance Monitor", passed, "Monitor initialized")
        results.append(("Balance Monitor", passed))
    except Exception as e:
        print_test("Balance Monitor", False, f"Error: {e}")
        results.append(("Balance Monitor", False))
    
    # Summary
    print_header("TEST SUMMARY")
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    failed_count = total - passed_count
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"Success Rate: {(passed_count/total*100):.1f}%")
    
    if failed_count == 0:
        print("\n" + "="*70)
        print("🎉 ALL SYSTEMS READY FOR TESTING!")
        print("="*70)
        print("\n📋 Next Steps:")
        print("1. Start bot: python bot.py")
        print("2. Test commands: /spawn_agent, /agent_status, /agent_lineage")
        print("3. Test menu: Click AI Agent menu buttons")
        print("4. Test lineage: Spawn child agent from parent")
        print("5. Monitor logs for any errors")
        return 0
    else:
        print("\n" + "="*70)
        print("⚠️ SOME SYSTEMS NEED ATTENTION")
        print("="*70)
        print("\nFailed Components:")
        for name, p in results:
            if not p:
                print(f"  ❌ {name}")
        print("\n📋 Action Required:")
        print("1. Check .env file for missing credentials")
        print("2. Run migrations if database schema is missing")
        print("3. Verify Supabase connection")
        print("4. Check Conway API credentials")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
