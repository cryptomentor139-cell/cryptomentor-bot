#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Conway API Connection
Cek koneksi ke Conway API dan balance Automaton
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_conway_api():
    """Test Conway API connection and get balance"""
    
    api_url = os.getenv('CONWAY_API_URL', 'https://api.conway.tech')
    api_key = os.getenv('CONWAY_API_KEY')
    wallet_address = os.getenv('CENTRALIZED_WALLET_ADDRESS', '0x63116672bef9f26fd906cd2a57550f7a13925822')
    
    print("=" * 60)
    print("🔌 CONWAY API CONNECTION TEST")
    print("=" * 60)
    
    print(f"\n📍 API URL: {api_url}")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"💼 Wallet: {wallet_address}")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Health check
    print("\n" + "=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{api_url}/health", headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: Get wallet balance (correct endpoint)
    print("\n" + "=" * 60)
    print("TEST 2: Get Wallet Balance")
    print("=" * 60)
    
    try:
        endpoint = f"/api/v1/wallets/{wallet_address}/balance"
        url = f"{api_url}{endpoint}"
        print(f"Endpoint: {endpoint}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data}")
            
            balance = data.get('balance', 0)
            print(f"\n💰 Conway Credits Balance: {balance:,.2f}")
            
            # Calculate USDC equivalent
            usdc_equivalent = balance / 100
            print(f"💵 USDC Equivalent: ${usdc_equivalent:,.2f}")
            
            # Calculate agent capacity
            if balance >= 100:
                # Note: Actual cost depends on Automaton API pricing
                print(f"\n🤖 Agent Spawn Capability:")
                print(f"   ⚠️  Cost per agent depends on Automaton API")
                print(f"   💡 Check Conway dashboard for current pricing")
            else:
                print(f"\n⚠️  Insufficient balance to spawn agents")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Balance check failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Get deposit address
    print("\n" + "=" * 60)
    print("TEST 3: Get Deposit Address")
    print("=" * 60)
    
    try:
        user_id = 1187119989  # Your admin user ID
        endpoint = f"/api/v1/wallets/{user_id}/deposit-address"
        url = f"{api_url}{endpoint}"
        print(f"Endpoint: {endpoint}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data}")
            
            deposit_address = data.get('deposit_address')
            if deposit_address:
                print(f"\n📥 Deposit Address: {deposit_address}")
                print(f"🌐 Network: Base")
                print(f"💵 Token: USDC")
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Deposit address check failed: {e}")
    
    # Test 4: List available endpoints
    print("\n" + "=" * 60)
    print("TEST 4: API Documentation")
    print("=" * 60)
    
    try:
        response = requests.get(f"{api_url}/api/v1/docs", headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ API docs available at: {api_url}/api/v1/docs")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Note: {e}")
    
    print("\n" + "=" * 60)
    print("✅ CONNECTION TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_conway_api()
