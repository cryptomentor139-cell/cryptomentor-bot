"""
Discover available Conway API endpoints
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def discover_endpoints():
    """Try to discover available endpoints"""
    
    api_url = os.getenv('CONWAY_API_URL', 'https://automaton-production-a899.up.railway.app')
    api_key = os.getenv('CONWAY_API_KEY')
    
    print(f"🔍 Discovering Conway API endpoints: {api_url}")
    
    # Common API endpoint patterns
    endpoints_to_try = [
        # Root paths
        ('GET', '/'),
        ('GET', '/api'),
        ('GET', '/api/v1'),
        
        # Documentation
        ('GET', '/docs'),
        ('GET', '/api/docs'),
        ('GET', '/api/v1/docs'),
        ('GET', '/swagger'),
        ('GET', '/openapi.json'),
        
        # Agent endpoints
        ('GET', '/api/v1/agents'),
        ('POST', '/api/v1/agents'),
        ('GET', '/api/v1/agent'),
        ('POST', '/api/v1/agent'),
        
        # Wallet endpoints
        ('GET', '/api/v1/wallet'),
        ('POST', '/api/v1/wallet'),
        ('GET', '/api/v1/wallets'),
        
        # Credit endpoints
        ('GET', '/api/v1/credits'),
        ('POST', '/api/v1/credits'),
        ('GET', '/api/v1/balance'),
        
        # Deposit endpoints
        ('GET', '/api/v1/deposits'),
        ('POST', '/api/v1/deposits'),
        
        # Status endpoints
        ('GET', '/health'),
        ('GET', '/status'),
        ('GET', '/api/v1/status'),
    ]
    
    print("\n" + "="*80)
    print("TESTING ENDPOINTS")
    print("="*80)
    
    found_endpoints = []
    
    for method, endpoint in endpoints_to_try:
        try:
            if method == 'GET':
                response = requests.get(
                    f"{api_url}{endpoint}",
                    headers={'Authorization': f'Bearer {api_key}'},
                    timeout=5
                )
            else:
                response = requests.post(
                    f"{api_url}{endpoint}",
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={},
                    timeout=5
                )
            
            status = response.status_code
            
            # Only show non-404 responses
            if status != 404:
                print(f"\n{method} {endpoint}")
                print(f"  Status: {status}")
                
                # Try to parse JSON
                try:
                    data = response.json()
                    print(f"  Response: {str(data)[:200]}")
                except:
                    print(f"  Response: {response.text[:200]}")
                
                found_endpoints.append((method, endpoint, status))
        
        except requests.exceptions.Timeout:
            print(f"{method} {endpoint}: ⏱️ Timeout")
        except Exception as e:
            pass  # Skip errors
    
    print("\n" + "="*80)
    print("SUMMARY - FOUND ENDPOINTS")
    print("="*80)
    
    if found_endpoints:
        for method, endpoint, status in found_endpoints:
            print(f"✅ {method} {endpoint} -> {status}")
    else:
        print("❌ No endpoints found (all returned 404)")
    
    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    print("""
Conway Automaton API yang di-deploy di Railway sepertinya tidak memiliki
endpoint untuk generate deposit address.

Solusi:
1. Gunakan CENTRALIZED_WALLET_ADDRESS yang sudah ada di .env
2. Semua user deposit ke wallet yang sama
3. Track deposit berdasarkan amount dan timestamp
4. Atau tambahkan endpoint baru ke Conway API
    """)

if __name__ == '__main__':
    discover_endpoints()
