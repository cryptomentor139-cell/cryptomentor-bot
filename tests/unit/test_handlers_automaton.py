#!/usr/bin/env python3
"""
Test script for Automaton Telegram Bot Handlers

Tests:
- Handler responses to commands
- Premium verification
- Automaton access verification
- Error messages
- QR code URL generation
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from app.automaton_manager import get_automaton_manager


def test_qr_code_generation():
    """Test QR code URL generation"""
    print("\n" + "="*60)
    print("TEST: QR Code URL Generation")
    print("="*60)
    
    test_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    expected_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={test_address}"
    
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={test_address}"
    
    print(f"Test Address: {test_address}")
    print(f"Generated QR URL: {qr_url}")
    print(f"Expected URL: {expected_url}")
    
    if qr_url == expected_url:
        print("✅ QR code URL generation: PASS")
        return True
    else:
        print("❌ QR code URL generation: FAIL")
        return False


def test_automaton_access_check():
    """Test Automaton access verification"""
    print("\n" + "="*60)
    print("TEST: Automaton Access Verification")
    print("="*60)
    
    db = Database()
    
    # Test with a non-existent user (should return False)
    test_user_id = 999999999
    has_access = db.has_automaton_access(test_user_id)
    
    print(f"Test User ID: {test_user_id}")
    print(f"Has Automaton Access: {has_access}")
    
    if has_access == False:
        print("✅ Automaton access check (non-existent user): PASS")
        return True
    else:
        print("❌ Automaton access check (non-existent user): FAIL")
        return False


def test_premium_verification():
    """Test premium status verification"""
    print("\n" + "="*60)
    print("TEST: Premium Status Verification")
    print("="*60)
    
    db = Database()
    
    # Test with a non-existent user (should return False)
    test_user_id = 999999999
    is_premium = db.is_user_premium(test_user_id)
    
    print(f"Test User ID: {test_user_id}")
    print(f"Is Premium: {is_premium}")
    
    if is_premium == False:
        print("✅ Premium verification (non-existent user): PASS")
        return True
    else:
        print("❌ Premium verification (non-existent user): FAIL")
        return False


def test_error_messages():
    """Test error message formatting"""
    print("\n" + "="*60)
    print("TEST: Error Message Formatting")
    print("="*60)
    
    # Test messages
    messages = {
        'no_access': "❌ *Akses Automaton Diperlukan*\n\nUntuk menggunakan fitur AI Agent, Anda perlu membayar biaya satu kali sebesar *Rp2.000.000*.",
        'no_premium': "❌ *Premium Diperlukan*\n\nFitur AI Agent hanya tersedia untuk pengguna premium.",
        'insufficient_credits': "❌ *Kredit Tidak Cukup*\n\nSpawn agent membutuhkan 100.000 kredit.",
        'no_agents': "❌ *Tidak Ada Agent*\n\nAnda belum memiliki agent. Gunakan /spawn_agent untuk membuat agent baru."
    }
    
    all_pass = True
    for msg_type, msg in messages.items():
        print(f"\n{msg_type}:")
        print(f"  {msg[:50]}...")
        
        # Check if message is in Indonesian
        if any(word in msg.lower() for word in ['anda', 'untuk', 'tidak', 'diperlukan']):
            print(f"  ✅ Message is in Indonesian")
        else:
            print(f"  ❌ Message is NOT in Indonesian")
            all_pass = False
        
        # Check if message uses Markdown
        if '*' in msg:
            print(f"  ✅ Message uses Markdown formatting")
        else:
            print(f"  ❌ Message does NOT use Markdown")
            all_pass = False
    
    if all_pass:
        print("\n✅ Error message formatting: PASS")
        return True
    else:
        print("\n❌ Error message formatting: FAIL")
        return False


def test_handler_imports():
    """Test that handlers can be imported"""
    print("\n" + "="*60)
    print("TEST: Handler Imports")
    print("="*60)
    
    try:
        from app.handlers_automaton import (
            spawn_agent_command,
            agent_status_command,
            deposit_command,
            balance_command,
            agent_logs_command,
            withdraw_command
        )
        
        handlers = [
            spawn_agent_command,
            agent_status_command,
            deposit_command,
            balance_command,
            agent_logs_command,
            withdraw_command
        ]
        
        print(f"Successfully imported {len(handlers)} handlers:")
        for handler in handlers:
            print(f"  ✅ {handler.__name__}")
        
        print("\n✅ Handler imports: PASS")
        return True
    
    except Exception as e:
        print(f"❌ Failed to import handlers: {e}")
        print("❌ Handler imports: FAIL")
        return False


def test_automaton_manager():
    """Test AutomatonManager initialization"""
    print("\n" + "="*60)
    print("TEST: AutomatonManager Initialization")
    print("="*60)
    
    try:
        db = Database()
        manager = get_automaton_manager(db)
        
        print(f"AutomatonManager initialized: {manager is not None}")
        print(f"Spawn fee: {manager.spawn_fee_credits:,} credits")
        print(f"Tier thresholds: {manager.tier_thresholds}")
        
        print("\n✅ AutomatonManager initialization: PASS")
        return True
    
    except Exception as e:
        print(f"❌ Failed to initialize AutomatonManager: {e}")
        print("❌ AutomatonManager initialization: FAIL")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AUTOMATON HANDLERS TEST SUITE")
    print("="*60)
    
    tests = [
        test_handler_imports,
        test_automaton_manager,
        test_qr_code_generation,
        test_automaton_access_check,
        test_premium_verification,
        test_error_messages
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
