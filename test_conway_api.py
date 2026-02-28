#!/usr/bin/env python3
"""
Test Conway API Integration

Tests all Conway API endpoints to ensure proper connectivity and functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from conway_integration import get_conway_client

def test_health_check():
    """Test API health check"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    client = get_conway_client()
    is_healthy = client.health_check()
    
    if is_healthy:
        print("✅ Conway API is healthy")
        return True
    else:
        print("❌ Conway API health check failed")
        return False

def test_generate_deposit_address():
    """Test deposit address generation"""
    print("\n" + "="*60)
    print("TEST 2: Generate Deposit Address")
    print("="*60)
    
    client = get_conway_client()
    
    # Test with sample user
    test_user_id = 1187119989
    test_agent_name = "Test Agent Alpha"
    
    print(f"Generating address for user {test_user_id}...")
    address = client.generate_deposit_address(test_user_id, test_agent_name)
    
    if address:
        print(f"✅ Deposit address generated: {address}")
        print(f"   Network: Base")
        print(f"   Token: USDC only")
        return address
    else:
        print("❌ Failed to generate deposit address")
        return None

def test_get_credit_balance(deposit_address):
    """Test credit balance retrieval"""
    print("\n" + "="*60)
    print("TEST 3: Get Credit Balance")
    print("="*60)
    
    if not deposit_address:
        print("⚠️ Skipping (no deposit address)")
        return None
    
    client = get_conway_client()
    
    print(f"Checking balance for {deposit_address}...")
    balance = client.get_credit_balance(deposit_address)
    
    if balance is not None:
        print(f"✅ Current balance: {balance:,.2f} credits")
        return balance
    else:
        print("❌ Failed to get credit balance")
        return None

def test_spawn_agent(deposit_address):
    """Test agent spawning"""
    print("\n" + "="*60)
    print("TEST 4: Spawn Agent")
    print("="*60)
    
    if not deposit_address:
        print("⚠️ Skipping (no deposit address)")
        return None
    
    client = get_conway_client()
    
    print(f"Spawning agent for {deposit_address}...")
    result = client.spawn_agent(
        deposit_address=deposit_address,
        agent_name="Test Trading Bot",
        genesis_prompt="You are a test trading agent. Focus on learning and small trades."
    )
    
    if result['success']:
        print(f"✅ Agent spawned successfully!")
        print(f"   Agent ID: {result['agent_id']}")
        print(f"   Message: {result['message']}")
        return result['agent_id']
    else:
        print(f"❌ Failed to spawn agent: {result['message']}")
        return None

def test_get_agent_status(deposit_address):
    """Test agent status retrieval"""
    print("\n" + "="*60)
    print("TEST 5: Get Agent Status")
    print("="*60)
    
    if not deposit_address:
        print("⚠️ Skipping (no deposit address)")
        return None
    
    client = get_conway_client()
    
    print(f"Getting status for {deposit_address}...")
    status = client.get_agent_status(deposit_address)
    
    if status:
        print(f"✅ Agent status retrieved:")
        print(f"   Active: {status['is_active']}")
        print(f"   Balance: {status['balance']:,.2f} credits")
        print(f"   Last Active: {status['last_active']}")
        print(f"   Total Trades: {status['total_trades']}")
        print(f"   Total Profit: ${status['total_profit']:.2f}")
        print(f"   Total Loss: ${status['total_loss']:.2f}")
        return status
    else:
        print("❌ Failed to get agent status")
        return None

def test_get_transactions(deposit_address):
    """Test transaction history retrieval"""
    print("\n" + "="*60)
    print("TEST 6: Get Transaction History")
    print("="*60)
    
    if not deposit_address:
        print("⚠️ Skipping (no deposit address)")
        return None
    
    client = get_conway_client()
    
    print(f"Getting transactions for {deposit_address}...")
    transactions = client.get_agent_transactions(deposit_address, limit=10)
    
    if transactions is not None:
        print(f"✅ Retrieved {len(transactions)} transactions")
        
        if transactions:
            print("\nRecent transactions:")
            for i, tx in enumerate(transactions[:5], 1):
                print(f"   {i}. {tx.get('type')} - {tx.get('amount')} - {tx.get('timestamp')}")
        else:
            print("   No transactions yet")
        
        return transactions
    else:
        print("❌ Failed to get transactions")
        return None

def run_all_tests():
    """Run all Conway API tests"""
    print("\n" + "="*60)
    print("CONWAY API INTEGRATION TEST SUITE")
    print("="*60)
    
    # Check environment variables
    print("\n📋 Checking environment variables...")
    api_url = os.getenv('CONWAY_API_URL')
    api_key = os.getenv('CONWAY_API_KEY')
    
    if not api_url:
        print("❌ CONWAY_API_URL not set")
        return False
    
    if not api_key:
        print("❌ CONWAY_API_KEY not set")
        return False
    
    print(f"✅ CONWAY_API_URL: {api_url}")
    print(f"✅ CONWAY_API_KEY: {api_key[:8]}...{api_key[-4:]}")
    
    # Run tests
    results = {}
    
    # Test 1: Health check
    results['health'] = test_health_check()
    if not results['health']:
        print("\n❌ Health check failed - stopping tests")
        return False
    
    # Test 2: Generate deposit address
    deposit_address = test_generate_deposit_address()
    results['address'] = deposit_address is not None
    
    # Test 3: Get balance
    balance = test_get_credit_balance(deposit_address)
    results['balance'] = balance is not None
    
    # Test 4: Spawn agent (optional - may fail if already spawned)
    agent_id = test_spawn_agent(deposit_address)
    results['spawn'] = agent_id is not None
    
    # Test 5: Get status
    status = test_get_agent_status(deposit_address)
    results['status'] = status is not None
    
    # Test 6: Get transactions
    transactions = test_get_transactions(deposit_address)
    results['transactions'] = transactions is not None
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Conway API integration is working.")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the logs above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
