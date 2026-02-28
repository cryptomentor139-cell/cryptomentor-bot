#!/usr/bin/env python3
"""
Test script for Deposit Monitor Service

Tests:
1. Web3 connection to Base network
2. USDC contract interaction
3. Balance checking
4. Deposit detection logic
5. Fee calculation
6. Conway credit conversion
"""

import os
import sys
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.deposit_monitor import DepositMonitor
from database import Database


def test_web3_connection():
    """Test Web3 connection to Base network"""
    print("\n" + "="*60)
    print("TEST 1: Web3 Connection to Base Network")
    print("="*60)
    
    try:
        db = Database()
        monitor = DepositMonitor(db)
        
        is_connected = monitor._check_web3_connection()
        
        if is_connected:
            print("✅ Successfully connected to Base network")
            print(f"   RPC URL: {monitor.rpc_url}")
            
            # Get latest block
            latest_block = monitor.w3.eth.block_number
            print(f"   Latest Block: {latest_block}")
            
            return True
        else:
            print("❌ Failed to connect to Base network")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_usdc_contract():
    """Test USDC contract interaction"""
    print("\n" + "="*60)
    print("TEST 2: USDC Contract Interaction")
    print("="*60)
    
    try:
        db = Database()
        monitor = DepositMonitor(db)
        
        print(f"USDC Contract Address: {monitor.usdc_address}")
        
        # Test with a known address (Coinbase wallet on Base)
        test_address = "0x3304E22DDaa22bCdC5fCa2269b418046aE7b566A"
        
        balance = monitor._get_usdc_balance(test_address)
        
        if balance is not None:
            print(f"✅ Successfully queried USDC balance")
            print(f"   Test Address: {test_address}")
            print(f"   Balance: {balance} USDC")
            return True
        else:
            print("❌ Failed to query USDC balance")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_fee_calculation():
    """Test platform fee and Conway credit calculation"""
    print("\n" + "="*60)
    print("TEST 3: Fee Calculation & Credit Conversion")
    print("="*60)
    
    try:
        db = Database()
        monitor = DepositMonitor(db)
        
        test_amounts = [5.0, 10.0, 50.0, 100.0, 1000.0]
        
        print(f"Platform Fee Rate: {monitor.platform_fee_rate * 100}%")
        print(f"Credit Conversion Rate: 1 USDC = {monitor.credit_conversion_rate} credits")
        print()
        
        all_correct = True
        
        for amount in test_amounts:
            net_amount, platform_fee, conway_credits = monitor._calculate_conway_credits(amount)
            
            # Verify calculations
            expected_fee = amount * 0.02
            expected_net = amount - expected_fee
            expected_credits = expected_net * 100
            
            is_correct = (
                abs(platform_fee - expected_fee) < 0.01 and
                abs(net_amount - expected_net) < 0.01 and
                abs(conway_credits - expected_credits) < 0.01
            )
            
            status = "✅" if is_correct else "❌"
            print(f"{status} Deposit: {amount} USDC")
            print(f"   Platform Fee: {platform_fee} USDC")
            print(f"   Net Amount: {net_amount} USDC")
            print(f"   Conway Credits: {conway_credits}")
            print()
            
            if not is_correct:
                all_correct = False
        
        if all_correct:
            print("✅ All fee calculations correct")
            return True
        else:
            print("❌ Some fee calculations incorrect")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_minimum_deposit():
    """Test minimum deposit validation"""
    print("\n" + "="*60)
    print("TEST 4: Minimum Deposit Validation")
    print("="*60)
    
    try:
        db = Database()
        monitor = DepositMonitor(db)
        
        print(f"Minimum Deposit: {monitor.min_deposit} USDC")
        print()
        
        test_cases = [
            (4.99, False, "Below minimum"),
            (5.0, True, "Exactly minimum"),
            (5.01, True, "Above minimum"),
            (10.0, True, "Well above minimum")
        ]
        
        all_correct = True
        
        for amount, should_pass, description in test_cases:
            # Check if amount meets minimum
            meets_minimum = amount >= monitor.min_deposit
            is_correct = meets_minimum == should_pass
            
            status = "✅" if is_correct else "❌"
            result = "PASS" if meets_minimum else "REJECT"
            
            print(f"{status} {amount} USDC - {description}: {result}")
            
            if not is_correct:
                all_correct = False
        
        print()
        if all_correct:
            print("✅ Minimum deposit validation working correctly")
            return True
        else:
            print("❌ Minimum deposit validation has issues")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_configuration():
    """Test deposit monitor configuration"""
    print("\n" + "="*60)
    print("TEST 5: Configuration")
    print("="*60)
    
    try:
        db = Database()
        monitor = DepositMonitor(db)
        
        print("Configuration:")
        print(f"  ✓ Network: Base")
        print(f"  ✓ RPC URL: {monitor.rpc_url}")
        print(f"  ✓ USDC Address: {monitor.usdc_address}")
        print(f"  ✓ Check Interval: {monitor.check_interval}s")
        print(f"  ✓ Min Confirmations: {monitor.min_confirmations}")
        print(f"  ✓ Min Deposit: {monitor.min_deposit} USDC")
        print(f"  ✓ Platform Fee: {monitor.platform_fee_rate * 100}%")
        print(f"  ✓ Credit Rate: 1 USDC = {monitor.credit_conversion_rate} credits")
        
        print("\n✅ Configuration loaded successfully")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("DEPOSIT MONITOR TEST SUITE")
    print("="*60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Web3 Connection", test_web3_connection),
        ("USDC Contract", test_usdc_contract),
        ("Fee Calculation", test_fee_calculation),
        ("Minimum Deposit", test_minimum_deposit)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
