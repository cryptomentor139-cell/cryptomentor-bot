#!/usr/bin/env python3
"""
Test script to verify autosignal fix for lifetime premium users
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chat_store():
    """Test that chat_store functions work correctly"""
    print("=" * 60)
    print("TEST 1: Chat Store Functions")
    print("=" * 60)
    
    from app.chat_store import remember_chat, get_private_chat_id
    
    # Test storing and retrieving chat_id
    test_user_id = 123456789
    test_chat_id = 987654321
    
    print(f"\n1. Storing chat_id for user {test_user_id}...")
    remember_chat(test_user_id, test_chat_id)
    print("   ✅ Chat ID stored")
    
    print(f"\n2. Retrieving chat_id for user {test_user_id}...")
    retrieved_chat_id = get_private_chat_id(test_user_id)
    
    if retrieved_chat_id == test_chat_id:
        print(f"   ✅ Retrieved correct chat_id: {retrieved_chat_id}")
    else:
        print(f"   ❌ ERROR: Expected {test_chat_id}, got {retrieved_chat_id}")
        return False
    
    print("\n✅ Chat store test PASSED")
    return True


def test_list_recipients():
    """Test that list_recipients correctly identifies lifetime premium users"""
    print("\n" + "=" * 60)
    print("TEST 2: List Recipients (Lifetime Premium Users)")
    print("=" * 60)
    
    from app.autosignal_fast import list_recipients
    from app.chat_store import remember_chat
    
    # Get admin IDs from environment
    admin_ids = []
    for key in ['ADMIN_USER_ID', 'ADMIN2_USER_ID']:
        val = os.getenv(key)
        if val and val.isdigit():
            admin_ids.append(int(val))
    
    print(f"\n1. Admin IDs from environment: {admin_ids}")
    
    # Store chat_ids for admins (simulate /start command)
    for admin_id in admin_ids:
        remember_chat(admin_id, admin_id)  # Use same ID for testing
        print(f"   Stored chat_id for admin {admin_id}")
    
    print("\n2. Fetching lifetime premium users from Supabase...")
    try:
        recipients = list_recipients()
        print(f"   ✅ Found {len(recipients)} recipients")
        print(f"   Recipients: {recipients}")
        
        if len(recipients) > 0:
            print("\n✅ List recipients test PASSED")
            return True
        else:
            print("\n⚠️ WARNING: No recipients found")
            print("   This could mean:")
            print("   - No lifetime premium users in database")
            print("   - Users haven't used /start command yet")
            print("   - Supabase connection issue")
            return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_autosignal_enabled():
    """Test that autosignal is enabled"""
    print("\n" + "=" * 60)
    print("TEST 3: AutoSignal Status")
    print("=" * 60)
    
    from app.autosignal_fast import autosignal_enabled
    
    enabled = autosignal_enabled()
    print(f"\nAutoSignal enabled: {enabled}")
    
    if enabled:
        print("✅ AutoSignal is ENABLED")
        return True
    else:
        print("❌ AutoSignal is DISABLED")
        print("   Run /signal_on command to enable")
        return False


def test_signal_generation():
    """Test that signal generation works"""
    print("\n" + "=" * 60)
    print("TEST 4: Signal Generation (Fast Mode)")
    print("=" * 60)
    
    from app.autosignal_fast import compute_signal_fast
    
    # Test with BTC
    print("\n1. Testing signal generation for BTC...")
    try:
        signal = compute_signal_fast("BTC")
        
        if signal:
            print("   ✅ Signal generated successfully")
            print(f"   Symbol: {signal.get('symbol')}")
            print(f"   Side: {signal.get('side')}")
            print(f"   Confidence: {signal.get('confidence')}%")
            print(f"   Reasons: {signal.get('reasons')}")
            return True
        else:
            print("   ⚠️ No signal generated (market conditions not met)")
            print("   This is normal - not all coins have signals at all times")
            return True
    
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AUTOSIGNAL FIX VERIFICATION TEST")
    print("=" * 60)
    print("\nThis test verifies that:")
    print("1. Chat IDs are stored correctly")
    print("2. Lifetime premium users are identified")
    print("3. AutoSignal is enabled")
    print("4. Signal generation works")
    
    results = []
    
    # Run tests
    results.append(("Chat Store", test_chat_store()))
    results.append(("List Recipients", test_list_recipients()))
    results.append(("AutoSignal Status", test_autosignal_enabled()))
    results.append(("Signal Generation", test_signal_generation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Deploy to Railway")
        print("2. Users need to use /start command to register their chat_id")
        print("3. AutoSignal will send signals to lifetime premium users")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Please review the errors above")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
