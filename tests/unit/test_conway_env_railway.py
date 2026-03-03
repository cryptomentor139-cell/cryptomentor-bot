#!/usr/bin/env python3
"""
Test Conway API Environment Variables on Railway
Checks if CONWAY_API_KEY and CONWAY_API_URL are properly loaded
"""

import os
import sys

def test_conway_env():
    """Test Conway environment variables"""
    print("=" * 60)
    print("CONWAY API ENVIRONMENT TEST")
    print("=" * 60)
    
    # Check CONWAY_API_KEY
    api_key = os.getenv('CONWAY_API_KEY')
    print(f"\n1. CONWAY_API_KEY:")
    if api_key:
        # Show first 10 and last 5 characters for security
        masked_key = f"{api_key[:10]}...{api_key[-5:]}" if len(api_key) > 15 else "***"
        print(f"   ✅ Found: {masked_key}")
        print(f"   Length: {len(api_key)} characters")
    else:
        print(f"   ❌ NOT FOUND!")
        print(f"   This will cause Conway API to fail")
    
    # Check CONWAY_API_URL
    api_url = os.getenv('CONWAY_API_URL', 'https://api.conway.tech')
    print(f"\n2. CONWAY_API_URL:")
    print(f"   ✅ {api_url}")
    
    # Check CONWAY_WALLET_ADDRESS
    wallet = os.getenv('CONWAY_WALLET_ADDRESS')
    print(f"\n3. CONWAY_WALLET_ADDRESS:")
    if wallet:
        print(f"   ✅ {wallet}")
    else:
        print(f"   ⚠️  Not set (optional)")
    
    # Test Conway API initialization
    print(f"\n4. Testing Conway API Initialization:")
    try:
        from app.conway_integration import ConwayIntegration
        
        if not api_key:
            print(f"   ❌ Cannot initialize - CONWAY_API_KEY missing")
            return False
        
        conway = ConwayIntegration()
        print(f"   ✅ Conway API client initialized successfully")
        print(f"   API URL: {conway.api_url}")
        
        # Test health check
        print(f"\n5. Testing Conway API Health Check:")
        is_healthy = conway.health_check()
        if is_healthy:
            print(f"   ✅ Conway API is accessible")
        else:
            print(f"   ❌ Conway API is not accessible")
            print(f"   Check your API key and network connection")
        
        return is_healthy
        
    except ValueError as e:
        print(f"   ❌ Initialization failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🔍 Testing Conway API Environment on Railway...\n")
    
    success = test_conway_env()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - Conway API is ready!")
    else:
        print("❌ TESTS FAILED - Fix environment variables in Railway")
        print("\nTo fix:")
        print("1. Go to Railway dashboard")
        print("2. Select your project")
        print("3. Go to Variables tab")
        print("4. Add/Update: CONWAY_API_KEY=cnwy_k_DNll3zray_o4ccEpRmW0G6pK68BENY73")
        print("5. Add/Update: CONWAY_API_URL=https://api.conway.tech")
        print("6. Redeploy the service")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
