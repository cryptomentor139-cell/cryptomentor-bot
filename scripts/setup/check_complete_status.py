#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Status Check
Cek semua status: Supabase credits, Conway API, dan existing agents
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_supabase_credits():
    """Check user credits in Supabase"""
    print("=" * 60)
    print("1. SUPABASE USER CREDITS")
    print("=" * 60)
    
    try:
        from supabase_client import supabase
        
        user_id = 1187119989
        result = supabase.table('user_credits_balance')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if result.data:
            data = result.data[0]
            available = float(data.get('available_credits', 0))
            total = float(data.get('total_conway_credits', 0))
            
            print(f"✅ User {user_id} Credits:")
            print(f"   • Available: {available:,.2f} Conway Credits")
            print(f"   • Total: {total:,.2f} Conway Credits")
            print(f"   • USDC Equivalent: ${available/100:,.2f}")
            return available
        else:
            print(f"⚠️  No credits found for user {user_id}")
            return 0
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

def check_existing_agents():
    """Check if user has any spawned agents"""
    print("\n" + "=" * 60)
    print("2. EXISTING AGENTS IN DATABASE")
    print("=" * 60)
    
    try:
        from supabase_client import supabase
        
        user_id = 1187119989
        result = supabase.table('user_automatons')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if result.data:
            print(f"✅ Found {len(result.data)} agent(s):")
            for agent in result.data:
                print(f"\n   Agent ID: {agent.get('id')}")
                print(f"   Name: {agent.get('agent_name')}")
                print(f"   Status: {agent.get('status')}")
                print(f"   Wallet: {agent.get('agent_wallet', 'N/A')}")
                print(f"   Deposit Address: {agent.get('conway_deposit_address', 'N/A')}")
                print(f"   Credits: {agent.get('conway_credits', 0):,.2f}")
                print(f"   Tier: {agent.get('survival_tier', 'N/A')}")
                print(f"   Created: {agent.get('created_at')}")
            return result.data
        else:
            print("⚠️  No agents found")
            print("   💡 User hasn't spawned any agents yet")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_conway_api_spawn():
    """Test Conway API to see spawn agent cost"""
    print("\n" + "=" * 60)
    print("3. CONWAY API - SPAWN AGENT INFO")
    print("=" * 60)
    
    api_url = os.getenv('CONWAY_API_URL', 'https://api.conway.tech')
    api_key = os.getenv('CONWAY_API_KEY')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Try to get pricing info
    print("Checking Conway API pricing...")
    
    try:
        # Test 1: Check if there's a pricing endpoint
        response = requests.get(f"{api_url}/api/v1/pricing", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pricing Info:")
            print(f"   {data}")
        else:
            print(f"⚠️  No pricing endpoint (Status: {response.status_code})")
    except Exception as e:
        print(f"⚠️  Pricing endpoint not available: {e}")
    
    # Test 2: Try to get agent creation cost
    print("\nChecking agent spawn requirements...")
    try:
        user_id = 1187119989
        
        # Try to create agent (dry run to see requirements)
        data = {
            'user_id': user_id,
            'agent_name': 'Test Agent',
            'genesis_prompt': 'Test prompt',
            'dry_run': True  # If supported
        }
        
        response = requests.post(
            f"{api_url}/api/v1/agents",
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Agent Creation Info:")
            print(f"   {result}")
            
            # Look for cost information
            if 'cost' in result:
                print(f"\n💰 Spawn Cost: {result['cost']} credits")
            elif 'required_credits' in result:
                print(f"\n💰 Required Credits: {result['required_credits']}")
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"⚠️  Could not determine spawn cost: {e}")
    
    print("\n💡 Note: Actual cost depends on Conway API pricing")
    print("   Check Conway dashboard for current rates")

def check_conway_wallet_balance(agents):
    """Check Conway API balance for existing agents"""
    if not agents:
        return
    
    print("\n" + "=" * 60)
    print("4. CONWAY API - AGENT BALANCES")
    print("=" * 60)
    
    api_url = os.getenv('CONWAY_API_URL', 'https://api.conway.tech')
    api_key = os.getenv('CONWAY_API_KEY')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    for agent in agents:
        agent_wallet = agent.get('agent_wallet')
        if not agent_wallet:
            continue
        
        print(f"\nChecking agent: {agent.get('agent_name')}")
        print(f"Wallet: {agent_wallet}")
        
        try:
            response = requests.get(
                f"{api_url}/api/v1/wallets/{agent_wallet}/balance",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                balance = data.get('balance', 0)
                print(f"✅ Conway Balance: {balance:,.2f} credits")
            else:
                print(f"⚠️  Could not get balance (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("\n" + "🔍" * 30)
    print("COMPLETE STATUS CHECK")
    print("🔍" * 30 + "\n")
    
    # Check Supabase credits
    user_credits = check_supabase_credits()
    
    # Check existing agents
    agents = check_existing_agents()
    
    # Test Conway API spawn info
    test_conway_api_spawn()
    
    # Check Conway balances for existing agents
    check_conway_wallet_balance(agents)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print(f"\n💰 User Credits (Supabase): {user_credits:,.2f}")
    print(f"🤖 Spawned Agents: {len(agents)}")
    
    if user_credits > 0 and len(agents) == 0:
        print("\n✅ STATUS: Ready to spawn agent")
        print("   • User has credits in Supabase")
        print("   • No agents spawned yet")
        print("   • Can proceed with agent spawning")
    elif len(agents) > 0:
        print("\n✅ STATUS: Agents already running")
        print("   • Check agent balances above")
        print("   • Monitor agent performance")
    else:
        print("\n⚠️  STATUS: Need to deposit")
        print("   • User needs to deposit USDC first")
        print("   • Minimum: 5 USDC")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
