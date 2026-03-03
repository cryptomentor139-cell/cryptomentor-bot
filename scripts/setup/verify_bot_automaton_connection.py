#!/usr/bin/env python3
"""
Comprehensive Connection Test: Bot ↔ Automaton
Verify if Railway Bot can connect to Railway Automaton
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(test_name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    if details:
        print(f"   {details}")

def test_1_environment_variables():
    """Test 1: Check if environment variables are set"""
    print_header("TEST 1: Environment Variables")
    
    conway_url = os.getenv('CONWAY_API_URL')
    conway_key = os.getenv('CONWAY_API_KEY')
    
    print(f"\nCONWAY_API_URL: {conway_url if conway_url else '❌ NOT SET'}")
    print(f"CONWAY_API_KEY: {'✅ SET' if conway_key else '❌ NOT SET'}")
    
    if conway_url:
        print(f"\n📍 Automaton URL: {conway_url}")
    
    return bool(conway_url)

def test_2_automaton_health():
    """Test 2: Check if Automaton service is online"""
    print_header("TEST 2: Automaton Health Check")
    
    automaton_url = os.getenv('CONWAY_API_URL')
    if not automaton_url:
        print_result("Automaton Health", False, "CONWAY_API_URL not set")
        return False
    
    health_url = f"{automaton_url}/health"
    print(f"\nTesting: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Automaton Status:")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Uptime: {data.get('uptime', 0)} seconds")
            if 'agent' in data:
                print(f"   Agent State: {data['agent'].get('state', 'unknown')}")
            
            print_result("Automaton Health", True, "Service is ONLINE")
            return True
        else:
            print_result("Automaton Health", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print_result("Automaton Health", False, f"Connection failed: {e}")
        return False
    except Exception as e:
        print_result("Automaton Health", False, f"Error: {e}")
        return False

def test_3_conway_integration_import():
    """Test 3: Check if ConwayIntegration can be imported"""
    print_header("TEST 3: Conway Integration Import")
    
    try:
        from app.conway_integration import ConwayIntegration, get_conway_client
        print_result("Import ConwayIntegration", True, "Module imported successfully")
        return True
    except ImportError as e:
        print_result("Import ConwayIntegration", False, f"Import error: {e}")
        return False
    except Exception as e:
        print_result("Import ConwayIntegration", False, f"Error: {e}")
        return False

def test_4_conway_client_initialization():
    """Test 4: Initialize Conway client"""
    print_header("TEST 4: Conway Client Initialization")
    
    try:
        from app.conway_integration import get_conway_client
        
        # Check if CONWAY_API_URL is set
        if not os.getenv('CONWAY_API_URL'):
            print_result("Client Init", False, "CONWAY_API_URL not set")
            return False
        
        # Try to initialize client
        client = get_conway_client()
        
        print(f"\n📍 Client API URL: {client.api_url}")
        print(f"🔑 API Key: {'SET' if client.api_key else 'NOT SET'}")
        
        print_result("Client Init", True, "Client initialized successfully")
        return True
        
    except ValueError as e:
        print_result("Client Init", False, f"ValueError: {e}")
        return False
    except Exception as e:
        print_result("Client Init", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_health_check_via_client():
    """Test 5: Health check via Conway client"""
    print_header("TEST 5: Health Check via Conway Client")
    
    try:
        from app.conway_integration import get_conway_client
        
        client = get_conway_client()
        
        print(f"\nCalling: client.health_check()")
        result = client.health_check()
        
        print(f"Result: {result}")
        
        if result:
            print_result("Health Check", True, "Automaton is reachable via client")
            return True
        else:
            print_result("Health Check", False, "Automaton not reachable")
            return False
            
    except Exception as e:
        print_result("Health Check", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_6_handler_import():
    """Test 6: Check if new API handlers can be imported"""
    print_header("TEST 6: API Handlers Import")
    
    try:
        from app.handlers_automaton_api import (
            automaton_status_api,
            automaton_spawn_api,
            automaton_balance_api,
            automaton_deposit_info
        )
        
        print("\n✅ Imported handlers:")
        print("   - automaton_status_api")
        print("   - automaton_spawn_api")
        print("   - automaton_balance_api")
        print("   - automaton_deposit_info")
        
        print_result("Handler Import", True, "All handlers imported successfully")
        return True
        
    except ImportError as e:
        print_result("Handler Import", False, f"Import error: {e}")
        return False
    except Exception as e:
        print_result("Handler Import", False, f"Error: {e}")
        return False

def test_7_database_connection():
    """Test 7: Check database connection"""
    print_header("TEST 7: Database Connection")
    
    try:
        from database import Database
        
        db = Database()
        
        # Try a simple query
        result = db.supabase_service.table('users').select('user_id').limit(1).execute()
        
        print(f"\n✅ Database connected")
        print(f"   Query successful: {len(result.data) if result.data else 0} rows")
        
        print_result("Database Connection", True, "Supabase is accessible")
        return True
        
    except Exception as e:
        print_result("Database Connection", False, f"Error: {e}")
        return False

def test_8_end_to_end_simulation():
    """Test 8: Simulate /automaton status flow"""
    print_header("TEST 8: End-to-End Flow Simulation")
    
    try:
        from app.conway_integration import get_conway_client
        from database import Database
        
        print("\n📝 Simulating /automaton status flow:")
        print("   1. Get Conway client")
        client = get_conway_client()
        print("      ✅ Client initialized")
        
        print("   2. Health check")
        if not client.health_check():
            print("      ❌ Health check failed")
            print_result("E2E Simulation", False, "Automaton not reachable")
            return False
        print("      ✅ Automaton is online")
        
        print("   3. Database connection")
        db = Database()
        print("      ✅ Database connected")
        
        print("   4. Query user agents (example)")
        # This will fail if no agents, but that's OK
        result = db.supabase_service.table('user_automatons')\
            .select('deposit_address')\
            .limit(1)\
            .execute()
        print(f"      ✅ Query executed ({len(result.data) if result.data else 0} agents found)")
        
        print("\n✅ All components working!")
        print_result("E2E Simulation", True, "Full flow successful")
        return True
        
    except Exception as e:
        print_result("E2E Simulation", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "🔍 BOT ↔ AUTOMATON CONNECTION VERIFICATION" + "\n")
    print("This script will verify if Railway Bot can connect to Railway Automaton")
    
    results = {}
    
    # Run all tests
    results['env_vars'] = test_1_environment_variables()
    results['automaton_health'] = test_2_automaton_health()
    results['import_integration'] = test_3_conway_integration_import()
    results['client_init'] = test_4_conway_client_initialization()
    results['health_via_client'] = test_5_health_check_via_client()
    results['handler_import'] = test_6_handler_import()
    results['database'] = test_7_database_connection()
    results['e2e'] = test_8_end_to_end_simulation()
    
    # Summary
    print_header("SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    print()
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"   {status} {test_name.replace('_', ' ').title()}")
    
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("   Bot and Automaton are properly connected.")
        print()
        print("✅ You can now use:")
        print("   /automaton status")
        print("   /automaton spawn")
        print("   /automaton balance")
        print()
    else:
        print("⚠️  SOME TESTS FAILED")
        print()
        print("🔧 Troubleshooting:")
        
        if not results['env_vars']:
            print("   1. Set CONWAY_API_URL in Railway Bot Variables")
            print("      Value: https://automaton-production-a899.up.railway.app")
        
        if not results['automaton_health']:
            print("   2. Check if Automaton service is running")
            print("      Railway Dashboard → Automaton Service → Status")
        
        if not results['import_integration'] or not results['handler_import']:
            print("   3. Ensure latest code is deployed")
            print("      Check Railway Dashboard → Bot Service → Deployments")
            print("      Latest commit should be: 85b5fa9")
        
        if not results['client_init']:
            print("   4. Check if CONWAY_API_KEY is set (if required)")
            print("      Note: Bot should NOT need CONWAY_API_KEY")
            print("      Only Automaton service needs it")
        
        print()
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
