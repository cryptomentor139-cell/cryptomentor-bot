#!/usr/bin/env python3
"""
Test Admin Verification for OpenClaw
Verify that UID 1187119989 is recognized as admin
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_admin_auth():
    """Test centralized admin_auth module"""
    print("\n" + "="*60)
    print("TEST 1: Admin Auth Module")
    print("="*60)
    
    try:
        from app.admin_auth import is_admin, get_admin_ids, ADMIN_IDS
        
        # Get admin IDs
        admin_ids = get_admin_ids()
        print(f"✅ Admin IDs loaded: {admin_ids}")
        print(f"✅ ADMIN_IDS constant: {ADMIN_IDS}")
        
        # Test admin check
        test_uid = 1187119989
        result = is_admin(test_uid)
        
        if result:
            print(f"✅ UID {test_uid} is recognized as ADMIN")
        else:
            print(f"❌ UID {test_uid} is NOT recognized as admin")
            return False
        
        # Test non-admin
        non_admin = 999999999
        result = is_admin(non_admin)
        
        if not result:
            print(f"✅ UID {non_admin} correctly identified as NON-ADMIN")
        else:
            print(f"❌ UID {non_admin} incorrectly identified as admin")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_openclaw_manager():
    """Test OpenClaw Manager admin check"""
    print("\n" + "="*60)
    print("TEST 2: OpenClaw Manager Admin Check")
    print("="*60)
    
    try:
        # Mock database
        class MockDB:
            def __init__(self):
                self.conn = None
                self.cursor = None
        
        from app.openclaw_manager import OpenClawManager
        
        db = MockDB()
        manager = OpenClawManager(db)
        
        # Test admin check
        test_uid = 1187119989
        result = manager._is_admin(test_uid)
        
        if result:
            print(f"✅ OpenClawManager recognizes UID {test_uid} as ADMIN")
        else:
            print(f"❌ OpenClawManager does NOT recognize UID {test_uid} as admin")
            return False
        
        # Test non-admin
        non_admin = 999999999
        result = manager._is_admin(non_admin)
        
        if not result:
            print(f"✅ OpenClawManager correctly identifies UID {non_admin} as NON-ADMIN")
        else:
            print(f"❌ OpenClawManager incorrectly identifies UID {non_admin} as admin")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_env_variables():
    """Test environment variables"""
    print("\n" + "="*60)
    print("TEST 3: Environment Variables")
    print("="*60)
    
    admin1 = os.getenv('ADMIN1')
    admin2 = os.getenv('ADMIN2')
    admin_ids = os.getenv('ADMIN_IDS')
    
    print(f"ADMIN1: {admin1}")
    print(f"ADMIN2: {admin2}")
    print(f"ADMIN_IDS: {admin_ids}")
    
    if admin1 == '1187119989':
        print("✅ ADMIN1 is set correctly")
    else:
        print("❌ ADMIN1 is not set correctly")
        return False
    
    if admin_ids and '1187119989' in admin_ids:
        print("✅ ADMIN_IDS contains 1187119989")
    else:
        print("❌ ADMIN_IDS does not contain 1187119989")
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🔍 OpenClaw Admin Verification Test")
    print("="*60)
    print(f"Testing UID: 1187119989")
    print("="*60)
    
    results = []
    
    # Test 1: Environment Variables
    results.append(("Environment Variables", test_env_variables()))
    
    # Test 2: Admin Auth Module
    results.append(("Admin Auth Module", test_admin_auth()))
    
    # Test 3: OpenClaw Manager
    results.append(("OpenClaw Manager", test_openclaw_manager()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ UID 1187119989 is fully recognized as admin")
        print("\n📋 Next Steps:")
        print("1. Deploy to Railway: git push")
        print("2. Test on Telegram bot")
        print("3. Verify admin commands work")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please check the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
