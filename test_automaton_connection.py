#!/usr/bin/env python3
"""
Test Automaton Connection
Diagnose why "Automaton service offline" appears
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_environment_variables():
    """Test 1: Check environment variables"""
    print("=" * 60)
    print("TEST 1: Environment Variables")
    print("=" * 60)
    
    conway_url = os.getenv('CONWAY_API_URL')
    conway_key = os.getenv('CONWAY_API_KEY')
    
    print(f"\nCONWAY_API_URL: {conway_url}")
    print(f"CONWAY_API_KEY: {'*' * 20 if conway_key else 'NOT SET'}")
    
    if not conway_url:
        print("❌ CONWAY_API_URL not set!")
        return False
    
    if not conway_key:
        print("❌ CONWAY_API_KEY not set!")
        return False
    
    print("✅ Environment variables are set")
    return True


def test_api_connectivity():
    """Test 2: Test raw API connectivity"""
    print("\n" + "=" * 60)
    print("TEST 2: API Connectivity")
    print("=" * 60)
    
    conway_url = os.getenv('CONWAY_API_URL')
    conway_key = os.getenv('CONWAY_API_KEY')
    
    if not conway_url or not conway_key:
        print("❌ Skipping - environment variables not set")
        return False
    
    headers = {
        'Authorization': f'Bearer {conway_key}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Base URL
    print(f"\n1. Testing base URL: {conway_url}")
    try:
        response = requests.get(conway_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   ✅ Base URL is accessible")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Health check endpoint (dummy request)
    print(f"\n2. Testing health check endpoint...")
    try:
        test_url = f"{conway_url}/api/v1/wallets/0/deposit-address"
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 404]:
            print(f"   ✅ API is responding (status {response.status_code} is expected)")
            return True
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout - API not responding")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error - Cannot reach API")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_conway_integration():
    """Test 3: Test Conway Integration class"""
    print("\n" + "=" * 60)
    print("TEST 3: Conway Integration Class")
    print("=" * 60)
    
    try:
        from app.conway_integration import get_conway_client
        
        print("\n1. Initializing Conway client...")
        conway = get_conway_client()
        print(f"   ✅ Client initialized")
        print(f"   API URL: {conway.api_url}")
        
        print("\n2. Running health check...")
        health = conway.health_check()
        
        print(f"   Healthy: {health['healthy']}")
        print(f"   Status Code: {health['status_code']}")
        print(f"   Message: {health['message']}")
        
        if health['healthy']:
            print(f"   ✅ Health check PASSED")
            return True
        else:
            print(f"   ❌ Health check FAILED")
            
            # Provide specific guidance based on status code
            if health['status_code'] == 502:
                print(f"\n   🔴 502 Bad Gateway - Automaton application CRASHED")
                print(f"   → Check Railway Automaton logs for errors")
                print(f"   → Restart Automaton service in Railway")
                print(f"   → Verify all dependencies are installed")
            elif health['status_code'] == 503:
                print(f"\n   ⚠️ 503 Service Unavailable - Service restarting")
                print(f"   → Wait 1-2 minutes and try again")
            
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specific_endpoints():
    """Test 4: Test specific API endpoints"""
    print("\n" + "=" * 60)
    print("TEST 4: Specific API Endpoints")
    print("=" * 60)
    
    conway_url = os.getenv('CONWAY_API_URL')
    conway_key = os.getenv('CONWAY_API_KEY')
    
    if not conway_url or not conway_key:
        print("❌ Skipping - environment variables not set")
        return False
    
    headers = {
        'Authorization': f'Bearer {conway_key}',
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        '/api/v1/agents/balance?address=0x0000000000000000000000000000000000000000',
        '/api/v1/agents/status?address=0x0000000000000000000000000000000000000000',
        '/api/v1/wallets/0/deposit-address',
    ]
    
    results = []
    for endpoint in endpoints:
        url = f"{conway_url}{endpoint}"
        print(f"\nTesting: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 404]:
                print(f"   ✅ Endpoint accessible")
                results.append(True)
            else:
                print(f"   ⚠️ Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                results.append(False)
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(False)
    
    return all(results)


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AUTOMATON CONNECTION DIAGNOSTIC")
    print("=" * 60)
    print("\nThis will test:")
    print("1. Environment variables")
    print("2. API connectivity")
    print("3. Conway Integration class")
    print("4. Specific API endpoints")
    
    results = []
    
    # Run tests
    results.append(("Environment Variables", test_environment_variables()))
    results.append(("API Connectivity", test_api_connectivity()))
    results.append(("Conway Integration", test_conway_integration()))
    results.append(("Specific Endpoints", test_specific_endpoints()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nAutomaton API is accessible and working correctly.")
        print("If bot still shows 'offline', check Railway logs for errors.")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("\nPossible issues:")
        print("1. CONWAY_API_URL or CONWAY_API_KEY not set in Railway")
        print("2. Automaton Railway service is down")
        print("3. API endpoint has changed")
        print("4. Network/firewall blocking connection")
        print("\nNext steps:")
        print("- Check Railway environment variables")
        print("- Check Automaton Railway deployment status")
        print("- Check Railway logs for errors")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
