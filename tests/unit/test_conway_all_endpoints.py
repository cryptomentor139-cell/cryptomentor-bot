#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test All Conway API Endpoints
Mencoba berbagai endpoint untuk menemukan yang benar
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_all_endpoints():
    """Test berbagai endpoint Conway API"""
    
    api_url = os.getenv('CONWAY_API_URL', 'https://api.conway.tech')
    api_key = os.getenv('CONWAY_API_KEY')
    user_id = 1187119989
    wallet_address = os.getenv('CENTRALIZED_WALLET_ADDRESS', '0x63116672bef9f26fd906cd2a57550f7a13925822')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("=" * 60)
    print("🔍 TESTING ALL CONWAY API ENDPOINTS")
    print("=" * 60)
    print(f"\nAPI URL: {api_url}")
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"User ID: {user_id}")
    print(f"Wallet: {wallet_address}")
    
    # List of endpoints to test
    endpoints = [
        # Account/User endpoints
        ('GET', '/api/v1/account', None, 'Get account info'),
        ('GET', '/api/v1/account/balance', None, 'Get account balance'),
        ('GET', '/api/v1/account/credits', None, 'Get account credits'),
        ('GET', f'/api/v1/users/{user_id}', None, 'Get user info'),
        ('GET', f'/api/v1/users/{user_id}/balance', None, 'Get user balance'),
        ('GET', f'/api/v1/users/{user_id}/credits', None, 'Get user credits'),
        
        # Wallet endpoints
        ('GET', '/api/v1/wallets', None, 'List all wallets'),
        ('GET', f'/api/v1/wallets/{wallet_address}', None, 'Get wallet info'),
        ('GET', f'/api/v1/wallets/{wallet_address}/balance', None, 'Get wallet balance'),
        ('GET', f'/api/v1/wallets/{user_id}/deposit-address', None, 'Get deposit address'),
        
        # Credits endpoints
        ('GET', '/api/v1/credits', None, 'Get credits info'),
        ('GET', '/api/v1/credits/balance', None, 'Get credits balance'),
        
        # Agent endpoints
        ('GET', '/api/v1/agents', None, 'List agents'),
        ('GET', f'/api/v1/agents?user_id={user_id}', None, 'List user agents'),
        
        # Dashboard/Stats
        ('GET', '/api/v1/dashboard', None, 'Get dashboard'),
        ('GET', '/api/v1/stats', None, 'Get stats'),
        ('GET', '/api/v1/me', None, 'Get current user'),
    ]
    
    successful_endpoints = []
    
    for method, endpoint, data, description in endpoints:
        print(f"\n{'=' * 60}")
        print(f"Testing: {description}")
        print(f"Endpoint: {method} {endpoint}")
        print("-" * 60)
        
        try:
            url = f"{api_url}{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS!")
                try:
                    json_data = response.json()
                    print(f"Response: {json_data}")
                    successful_endpoints.append((endpoint, description, json_data))
                except:
                    print(f"Response (text): {response.text[:200]}")
                    successful_endpoints.append((endpoint, description, response.text))
            elif response.status_code == 404:
                print(f"❌ Not Found")
            elif response.status_code == 401:
                print(f"❌ Unauthorized - Check API key")
            elif response.status_code == 403:
                print(f"❌ Forbidden - No permission")
            else:
                print(f"⚠️  Status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"⏳ Timeout")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if successful_endpoints:
        print(f"\n✅ Found {len(successful_endpoints)} working endpoint(s):\n")
        for endpoint, description, data in successful_endpoints:
            print(f"• {endpoint}")
            print(f"  {description}")
            print(f"  Data: {str(data)[:100]}...")
            print()
    else:
        print("\n❌ No working endpoints found")
        print("\n💡 Possible reasons:")
        print("   1. API key tidak valid atau expired")
        print("   2. Wallet/user belum terdaftar di Conway")
        print("   3. Endpoint structure berbeda dari dokumentasi")
        print("   4. Perlu registrasi/setup awal di Conway dashboard")
        
        print("\n🔧 Next steps:")
        print("   1. Login ke Conway dashboard: https://conway.tech")
        print("   2. Cek API key masih valid")
        print("   3. Cek apakah ada wallet/agent yang sudah terdaftar")
        print("   4. Lihat dokumentasi API di dashboard")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_all_endpoints()
