#!/usr/bin/env python3
"""
Test script to verify admin check fix
Tests that admin IDs are loaded from ADMIN1, ADMIN2, ADMIN3 environment variables
"""

import os
import sys

# Set test environment variables
os.environ['ADMIN1'] = '1187119989'
os.environ['ADMIN2'] = '7079544380'
os.environ['ADMIN3'] = ''  # Optional, can be empty

print("🧪 Testing Admin Check Fix")
print("=" * 60)

# Import admin_status module
try:
    from app.admin_status import is_admin, ADMIN_IDS, _load_admin_ids
    print("✅ Successfully imported admin_status module")
except ImportError as e:
    print(f"❌ Failed to import admin_status: {e}")
    sys.exit(1)

print(f"\n📋 Environment Variables:")
print(f"   ADMIN1: {os.getenv('ADMIN1')}")
print(f"   ADMIN2: {os.getenv('ADMIN2')}")
print(f"   ADMIN3: {os.getenv('ADMIN3')}")
print(f"   ADMIN_IDS: {os.getenv('ADMIN_IDS', 'Not set')}")

print(f"\n🔍 Loaded Admin IDs: {ADMIN_IDS}")
print(f"   Count: {len(ADMIN_IDS)}")

print(f"\n🧪 Testing is_admin() function:")

# Test cases
test_cases = [
    (1187119989, True, "Admin 1 (should be admin)"),
    (7079544380, True, "Admin 2 (should be admin)"),
    (999999999, False, "Random user (should NOT be admin)"),
    (123456789, False, "Another random user (should NOT be admin)"),
]

all_passed = True

for user_id, expected, description in test_cases:
    result = is_admin(user_id)
    status = "✅ PASS" if result == expected else "❌ FAIL"
    
    if result != expected:
        all_passed = False
    
    print(f"   {status} | User {user_id}: {result} (expected: {expected}) - {description}")

print("\n" + "=" * 60)

if all_passed:
    print("✅ ALL TESTS PASSED!")
    print("\n🎯 Admin check fix is working correctly!")
    print("\n📝 Next Steps:")
    print("   1. Deploy to Railway (already done via git push)")
    print("   2. Wait for Railway deployment to complete (~1-2 minutes)")
    print("   3. Test in Telegram bot:")
    print("      • Send: /admin_add_automaton_credits 123456789 3000 Test")
    print("      • Should see success message, not 'Command ini hanya untuk admin'")
    sys.exit(0)
else:
    print("❌ SOME TESTS FAILED!")
    print("\n🔧 Check the following:")
    print("   1. Environment variables are set correctly")
    print("   2. Admin IDs are valid integers")
    print("   3. app/admin_status.py has the updated _load_admin_ids() function")
    sys.exit(1)
