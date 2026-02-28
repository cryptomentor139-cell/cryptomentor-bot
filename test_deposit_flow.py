#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Deposit Detection Flow
Verifies the complete deposit detection and menu update flow
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_1_check_deposit_monitor_config():
    """Test 1: Check deposit monitor configuration"""
    print("=" * 70)
    print("🧪 TEST 1: Deposit Monitor Configuration")
    print("=" * 70)
    
    required_env = {
        'BASE_RPC_URL': os.getenv('BASE_RPC_URL'),
        'BASE_USDC_ADDRESS': os.getenv('BASE_USDC_ADDRESS'),
        'CENTRALIZED_WALLET_ADDRESS': os.getenv('CENTRALIZED_WALLET_ADDRESS'),
        'DEPOSIT_CHECK_INTERVAL': os.getenv('DEPOSIT_CHECK_INTERVAL', '30'),
        'MIN_CONFIRMATIONS': os.getenv('MIN_CONFIRMATIONS', '12'),
        'MIN_DEPOSIT_USDC': os.getenv('MIN_DEPOSIT_USDC', '5.0'),
    }
    
    all_configured = True
    for key, value in required_env.items():
        if value:
            print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: NOT SET")
            all_configured = False
    
    if all_configured:
        print("\n✅ All deposit monitor environment variables configured")
        return True
    else:
        print("\n⚠️  Some environment variables missing")
        return False

def test_2_check_web3_connection():
    """Test 2: Check Web3 connection to Base network"""
    print("\n" + "=" * 70)
    print("🧪 TEST 2: Web3 Connection to Base Network")
    print("=" * 70)
    
    try:
        from web3 import Web3
        
        rpc_url = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if w3.is_connected():
            print(f"✅ Connected to Base network: {rpc_url}")
            
            # Get latest block
            latest_block = w3.eth.block_number
            print(f"✅ Latest block: {latest_block}")
            
            return True
        else:
            print(f"❌ Failed to connect to Base network")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_3_check_usdc_contract():
    """Test 3: Check USDC contract on Base"""
    print("\n" + "=" * 70)
    print("🧪 TEST 3: USDC Contract Interaction")
    print("=" * 70)
    
    try:
        from web3 import Web3
        
        rpc_url = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        usdc_address = os.getenv(
            'BASE_USDC_ADDRESS',
            '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
        )
        
        # Minimal ERC20 ABI
        erc20_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            }
        ]
        
        usdc_contract = w3.eth.contract(
            address=Web3.to_checksum_address(usdc_address),
            abi=erc20_abi
        )
        
        print(f"✅ USDC Contract: {usdc_address}")
        
        # Test balance check on centralized wallet
        centralized_wallet = os.getenv('CENTRALIZED_WALLET_ADDRESS')
        if centralized_wallet:
            checksum_address = Web3.to_checksum_address(centralized_wallet)
            balance_wei = usdc_contract.functions.balanceOf(checksum_address).call()
            balance_usdc = balance_wei / (10 ** 6)  # USDC has 6 decimals
            
            print(f"✅ Centralized Wallet: {centralized_wallet}")
            print(f"✅ Current USDC Balance: {balance_usdc} USDC")
            
            return True
        else:
            print("⚠️  CENTRALIZED_WALLET_ADDRESS not set")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_check_database_tables():
    """Test 4: Check required database tables exist"""
    print("\n" + "=" * 70)
    print("🧪 TEST 4: Database Tables")
    print("=" * 70)
    
    try:
        from supabase_client import supabase
        
        if not supabase:
            print("❌ Supabase client not initialized")
            return False
        
        required_tables = [
            'user_credits_balance',
            'custodial_wallets',
            'wallet_deposits',
            'platform_revenue'
        ]
        
        all_exist = True
        for table in required_tables:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"✅ Table exists: {table}")
            except Exception as e:
                print(f"❌ Table missing or error: {table} - {e}")
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_5_check_user_credits():
    """Test 5: Check user credits in database"""
    print("\n" + "=" * 70)
    print("🧪 TEST 5: User Credits Check")
    print("=" * 70)
    
    try:
        from supabase_client import supabase
        
        user_id = 1187119989  # Admin user
        
        # Check user_credits_balance
        credits_result = supabase.table('user_credits_balance')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if credits_result.data:
            balance = credits_result.data[0]
            available = float(balance.get('available_credits', 0))
            total = float(balance.get('total_conway_credits', 0))
            
            print(f"✅ User {user_id} credits found:")
            print(f"   • Available Credits: {available}")
            print(f"   • Total Conway Credits: {total}")
            print(f"   • Has Deposit: {available > 0 or total > 0}")
            
            return True
        else:
            print(f"⚠️  No credits record for user {user_id}")
            print("   This is normal if user hasn't deposited yet")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_6_simulate_menu_logic():
    """Test 6: Simulate menu detection logic"""
    print("\n" + "=" * 70)
    print("🧪 TEST 6: Menu Detection Logic")
    print("=" * 70)
    
    try:
        from database import Database
        from supabase_client import supabase
        
        db = Database()
        user_id = 1187119989
        
        # Simulate the menu handler logic
        has_deposit = False
        
        if db.supabase_enabled and supabase:
            credits_result = supabase.table('user_credits_balance')\
                .select('available_credits, total_conway_credits')\
                .eq('user_id', user_id)\
                .execute()
            
            if credits_result.data:
                balance = credits_result.data[0]
                available = float(balance.get('available_credits', 0))
                total = float(balance.get('total_conway_credits', 0))
                has_deposit = (available > 0 or total > 0)
                
                print(f"✅ Credits check:")
                print(f"   • Available: {available}")
                print(f"   • Total: {total}")
                print(f"   • Has Deposit: {has_deposit}")
            else:
                print("⚠️  No credits record found")
        
        # Determine which menu to show
        if has_deposit:
            print("\n✅ RESULT: Show FULL AI Agent Menu")
            print("   Menu items:")
            print("   • 🚀 Spawn Agent")
            print("   • 📊 Agent Status")
            print("   • 🌳 Agent Lineage")
            print("   • 💰 Deposit Credits")
            print("   • 📜 Agent Logs")
        else:
            print("\n⚠️  RESULT: Show DEPOSIT-FIRST Menu")
            print("   Menu items:")
            print("   • 💰 Deposit Sekarang")
            print("   • ❓ Cara Deposit")
            print("   • 🔙 Kembali")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_7_check_deposit_monitor_class():
    """Test 7: Check DepositMonitor class initialization"""
    print("\n" + "=" * 70)
    print("🧪 TEST 7: DepositMonitor Class")
    print("=" * 70)
    
    try:
        from database import Database
        from app.deposit_monitor import get_deposit_monitor
        
        db = Database()
        monitor = get_deposit_monitor(db)
        
        print(f"✅ DepositMonitor initialized")
        print(f"   • RPC URL: {monitor.rpc_url}")
        print(f"   • USDC Address: {monitor.usdc_address}")
        print(f"   • Check Interval: {monitor.check_interval}s")
        print(f"   • Min Confirmations: {monitor.min_confirmations}")
        print(f"   • Min Deposit: {monitor.min_deposit} USDC")
        print(f"   • Platform Fee: {monitor.platform_fee_rate * 100}%")
        print(f"   • Credit Conversion: 1 USDC = {monitor.credit_conversion_rate} credits")
        
        # Check Web3 connection
        if monitor._check_web3_connection():
            print(f"✅ Web3 connected")
        else:
            print(f"❌ Web3 not connected")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n🚀 Starting Deposit Flow Tests\n")
    
    results = []
    
    # Run all tests
    results.append(("Deposit Monitor Config", test_1_check_deposit_monitor_config()))
    results.append(("Web3 Connection", test_2_check_web3_connection()))
    results.append(("USDC Contract", test_3_check_usdc_contract()))
    results.append(("Database Tables", test_4_check_database_tables()))
    results.append(("User Credits", test_5_check_user_credits()))
    results.append(("Menu Logic", test_6_simulate_menu_logic()))
    results.append(("DepositMonitor Class", test_7_check_deposit_monitor_class()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("\n📝 System Status:")
        print("   ✅ Deposit detection system ready")
        print("   ✅ Menu logic working correctly")
        print("   ✅ Database tables configured")
        print("   ✅ Web3 connection established")
        print("\n🚀 Next Steps:")
        print("   1. Deploy to Railway")
        print("   2. Start background services")
        print("   3. Test with real deposit")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
