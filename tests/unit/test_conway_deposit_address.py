"""
Test Conway API - Generate Deposit Address Endpoint
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_conway_deposit_address():
    """Test generate deposit address endpoint"""
    
    api_url = os.getenv('CONWAY_API_URL', 'https://automaton-production-a899.up.railway.app')
    api_key = os.getenv('CONWAY_API_KEY')
    
    print(f"🔍 Testing Conway API: {api_url}")
    print(f"🔑 API Key: {api_key[:20]}...")
    
    # Test 1: Health check
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(
            f"{api_url}/health",
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: List available endpoints
    print("\n" + "="*60)
    print("TEST 2: Check API Documentation")
    print("="*60)
    
    try:
        response = requests.get(
            f"{api_url}/api/v1/docs",
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.text[:500]}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Try to generate deposit address
    print("\n" + "="*60)
    print("TEST 3: Generate Deposit Address")
    print("="*60)
    
    test_data = {
        'user_id': 123456789,
        'agent_name': 'TestAgent',
        'network': 'base',
        'token': 'USDC'
    }
    
    print(f"Request data: {test_data}")
    
    try:
        response = requests.post(
            f"{api_url}/api/v1/agents/address",
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json=test_data,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'deposit_address' in data:
                print(f"\n✅ SUCCESS! Deposit address: {data['deposit_address']}")
            else:
                print(f"\n⚠️ No deposit_address in response")
        else:
            print(f"\n❌ Failed with status {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Try alternative endpoint paths
    print("\n" + "="*60)
    print("TEST 4: Try Alternative Endpoints")
    print("="*60)
    
    alternative_endpoints = [
        '/api/v1/wallet/generate',
        '/api/v1/deposit/address',
        '/api/v1/agents/wallet',
        '/api/v1/custodial/address',
        '/api/agents/address',
        '/agents/address'
    ]
    
    for endpoint in alternative_endpoints:
        try:
            response = requests.post(
                f"{api_url}{endpoint}",
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json=test_data,
                timeout=5
            )
            print(f"{endpoint}: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"  ✅ Found! Response: {response.text[:200]}")
        except Exception as e:
            print(f"{endpoint}: ❌ {str(e)[:50]}")

if __name__ == '__main__':
    test_conway_deposit_address()
