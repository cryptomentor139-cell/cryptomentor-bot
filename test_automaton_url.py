#!/usr/bin/env python3
"""
Test Automaton URL Connection
Check if CONWAY_API_URL is set and accessible
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_automaton_url():
    """Test if Automaton URL is accessible"""
    
    print("🔍 Testing Automaton URL Connection\n")
    print("=" * 60)
    
    # Check if CONWAY_API_URL is set
    automaton_url = os.getenv('CONWAY_API_URL')
    
    if not automaton_url:
        print("❌ CONWAY_API_URL not set in environment variables!")
        print("\nExpected variable:")
        print("  CONWAY_API_URL=https://automaton-production-a899.up.railway.app")
        return False
    
    print(f"✅ CONWAY_API_URL found: {automaton_url}")
    print()
    
    # Test 1: Health endpoint
    print("Test 1: Health Check")
    print("-" * 60)
    
    health_url = f"{automaton_url}/health"
    print(f"Testing: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Health check PASSED")
            print()
            return True
        else:
            print(f"❌ Health check FAILED (status {response.status_code})")
            print()
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: Cannot connect to {automaton_url}")
        print(f"   Error: {e}")
        print()
        print("Possible causes:")
        print("  1. Automaton service is down")
        print("  2. URL is incorrect")
        print("  3. Network issue")
        return False
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: No response from {automaton_url} after 10 seconds")
        print()
        print("Possible causes:")
        print("  1. Automaton service is slow to respond")
        print("  2. Network latency")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_from_railway_env():
    """Test using Railway environment variable format"""
    
    print("\n" + "=" * 60)
    print("🔍 Testing Railway Automaton URL\n")
    
    # Expected Railway URL
    railway_url = "https://automaton-production-a899.up.railway.app"
    
    print(f"Testing Railway URL: {railway_url}")
    print()
    
    try:
        response = requests.get(f"{railway_url}/health", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Railway Automaton is ONLINE and accessible!")
            print()
            print("✅ URL to use in Railway Bot Variables:")
            print(f"   CONWAY_API_URL={railway_url}")
            return True
        else:
            print(f"❌ Railway Automaton responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Railway Automaton")
        print()
        print("Possible causes:")
        print("  1. Automaton service is not deployed")
        print("  2. Automaton service is stopped")
        print("  3. URL is incorrect")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    
    print("\n" + "🤖 AUTOMATON URL CONNECTION TEST" + "\n")
    
    # Test 1: Check local .env
    local_test = test_automaton_url()
    
    # Test 2: Check Railway URL directly
    railway_test = test_from_railway_env()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if local_test:
        print("✅ Local .env CONWAY_API_URL: WORKING")
    else:
        print("❌ Local .env CONWAY_API_URL: NOT SET or NOT WORKING")
    
    if railway_test:
        print("✅ Railway Automaton URL: ONLINE")
    else:
        print("❌ Railway Automaton URL: OFFLINE or UNREACHABLE")
    
    print()
    
    if railway_test and not local_test:
        print("⚠️  ACTION REQUIRED:")
        print("   Railway Automaton is online, but local .env needs update!")
        print()
        print("   Add to Bismillah/.env:")
        print("   CONWAY_API_URL=https://automaton-production-a899.up.railway.app")
        print()
        print("   Add to Railway Bot Variables:")
        print("   Variable: CONWAY_API_URL")
        print("   Value: https://automaton-production-a899.up.railway.app")
    
    elif not railway_test:
        print("⚠️  ACTION REQUIRED:")
        print("   Railway Automaton is NOT accessible!")
        print()
        print("   Check:")
        print("   1. Railway Dashboard → Automaton Service → Status")
        print("   2. Railway Dashboard → Automaton Service → Logs")
        print("   3. Railway Dashboard → Automaton Service → Settings → Domains")
    
    elif local_test and railway_test:
        print("✅ ALL TESTS PASSED!")
        print("   Bot should be able to connect to Automaton")
    
    print()

if __name__ == "__main__":
    main()
