#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk cek kesehatan sistem AI Agent Automaton
Memeriksa semua komponen yang diperlukan untuk menjalankan agent
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("=" * 60)
    print("1. CHECKING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    required_vars = {
        'CONWAY_API_KEY': 'Conway API Key',
        'CONWAY_API_URL': 'Conway API URL',
        'SUPABASE_URL': 'Supabase URL',
        'SUPABASE_SERVICE_KEY': 'Supabase Service Key',
        'CENTRALIZED_WALLET_ADDRESS': 'Centralized Wallet Address'
    }
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var:
                display_value = value[:10] + '...' + value[-4:] if len(value) > 14 else '***'
            else:
                display_value = value
            print(f"✅ {description}: {display_value}")
        else:
            print(f"❌ {description}: NOT SET")
            all_set = False
    
    print()
    return all_set

def check_conway_api():
    """Check Conway API connection"""
    print("=" * 60)
    print("2. CHECKING CONWAY API CONNECTION")
    print("=" * 60)
    
    try:
        from app.conway_integration import ConwayIntegration
        
        conway = ConwayIntegration()
        
        # Test API connection
        print("Testing Conway API connection...")
        wallet_address = os.getenv('CENTRALIZED_WALLET_ADDRESS', '0x63116672bef9f26fd906cd2a57550f7a13925822')
        
        balance = conway.get_credit_balance(wallet_address)
        
        if balance is not None:
            print(f"✅ Conway API Connected!")
            print(f"💰 Wallet Balance: {balance:,.2f} Conway Credits")
            print(f"📍 Wallet Address: {wallet_address}")
            
            # Convert to USDC equivalent
            usdc_equivalent = balance / 100
            print(f"💵 USDC Equivalent: ${usdc_equivalent:,.2f}")
            
            return True, balance
        else:
            print("❌ Failed to get balance from Conway API")
            return False, 0
            
    except Exception as e:
        print(f"❌ Error connecting to Conway API: {e}")
        import traceback
        traceback.print_exc()
        return False, 0

def check_database_connection():
    """Check Supabase database connection"""
    print("\n" + "=" * 60)
    print("3. CHECKING DATABASE CONNECTION")
    print("=" * 60)
    
    try:
        from database import Database
        
        db = Database()
        
        if not db.supabase_enabled:
            print("❌ Supabase is not enabled")
            return False
        
        print("✅ Supabase connection established")
        
        # Check required tables
        required_tables = [
            'user_automatons',
            'automaton_transactions',
            'user_credits_balance',
            'deposit_transactions',
            'pending_deposits'
        ]
        
        print("\nChecking required tables:")
        for table in required_tables:
            try:
                result = db.supabase_service.table(table).select('*').limit(1).execute()
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                print(f"❌ Table '{table}' error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_automaton_manager():
    """Check Automaton Manager functionality"""
    print("\n" + "=" * 60)
    print("4. CHECKING AUTOMATON MANAGER")
    print("=" * 60)
    
    try:
        from app.automaton_manager import AutomatonManager
        from database import Database
        
        db = Database()
        manager = AutomatonManager(db)
        
        print("✅ AutomatonManager initialized successfully")
        
        # Check if we can query automatons
        test_user_id = 1187119989  # Your admin user ID
        
        try:
            automatons = manager.get_user_automatons(test_user_id)
            print(f"✅ Can query user automatons (found {len(automatons)} agents)")
            
            if automatons:
                print("\n📊 Your Active Agents:")
                for agent in automatons:
                    print(f"  • Agent ID: {agent.get('id')}")
                    print(f"    Status: {agent.get('status')}")
                    print(f"    Balance: {agent.get('balance_conway_credits', 0):,.2f} credits")
                    print(f"    Created: {agent.get('created_at')}")
                    print()
        except Exception as e:
            print(f"⚠️  Could not query automatons: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ AutomatonManager error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_background_services():
    """Check if background services can be initialized"""
    print("\n" + "=" * 60)
    print("5. CHECKING BACKGROUND SERVICES")
    print("=" * 60)
    
    try:
        from app.background_services import BackgroundServices
        from database import Database
        
        db = Database()
        
        # Just check if we can initialize (don't start services)
        services = BackgroundServices(db, None)  # None for bot instance
        
        print("✅ BackgroundServices can be initialized")
        print("   • Balance Monitor: Ready")
        print("   • Revenue Manager: Ready")
        print("   • Deposit Monitor: Ready")
        
        return True
        
    except Exception as e:
        print(f"❌ BackgroundServices error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_spawn_capability(conway_balance):
    """Check if user can spawn agents"""
    print("\n" + "=" * 60)
    print("6. CHECKING SPAWN CAPABILITY")
    print("=" * 60)
    
    # Minimum credits needed to spawn an agent
    MIN_SPAWN_CREDITS = 100  # 1 USDC = 100 credits
    
    print(f"💰 Available Credits: {conway_balance:,.2f}")
    print(f"🎯 Minimum Required: {MIN_SPAWN_CREDITS:,.2f} credits")
    
    if conway_balance >= MIN_SPAWN_CREDITS:
        max_agents = int(conway_balance / MIN_SPAWN_CREDITS)
        print(f"✅ You can spawn up to {max_agents} agent(s)")
        print(f"💡 Each agent costs {MIN_SPAWN_CREDITS} credits to spawn")
        return True
    else:
        needed = MIN_SPAWN_CREDITS - conway_balance
        print(f"❌ Insufficient credits")
        print(f"💡 You need {needed:,.2f} more credits to spawn an agent")
        return False

def main():
    """Main health check function"""
    print("\n" + "🤖" * 30)
    print("AI AGENT AUTOMATON - HEALTH CHECK")
    print("🤖" * 30 + "\n")
    
    results = {
        'env_vars': False,
        'conway_api': False,
        'database': False,
        'automaton_manager': False,
        'background_services': False,
        'can_spawn': False
    }
    
    conway_balance = 0
    
    # Run all checks
    results['env_vars'] = check_environment_variables()
    results['conway_api'], conway_balance = check_conway_api()
    results['database'] = check_database_connection()
    results['automaton_manager'] = check_automaton_manager()
    results['background_services'] = check_background_services()
    results['can_spawn'] = check_spawn_capability(conway_balance)
    
    # Summary
    print("\n" + "=" * 60)
    print("HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    for check, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check.replace('_', ' ').title()}")
    
    print(f"\n📊 Score: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("✅ Your AI Agent Automaton is ready to run!")
        print("\n💡 Next Steps:")
        print("   1. Go to Telegram bot")
        print("   2. Click '🤖 AI Agent' menu")
        print("   3. Click '🚀 Spawn Agent'")
        print("   4. Your agent will start trading!")
    elif passed_checks >= total_checks - 1:
        print("\n⚠️  MOSTLY OPERATIONAL")
        print("System can run but some features may be limited")
    else:
        print("\n❌ SYSTEM NOT READY")
        print("Please fix the failed checks before spawning agents")
    
    print("\n" + "=" * 60)
    
    return passed_checks == total_checks

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
