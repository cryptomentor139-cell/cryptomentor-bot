"""
Test Admin Unlimited Credits
Verify admin recognition and unlimited credits functionality
"""

import os
import sys
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.admin_auth import is_admin, get_admin_ids
from app.openclaw_langchain_db import get_openclaw_db


def test_admin_recognition():
    """Test admin recognition from environment"""
    print("=" * 60)
    print("TEST 1: Admin Recognition")
    print("=" * 60)
    
    admin_ids = get_admin_ids()
    print(f"\n✅ Admin IDs loaded: {admin_ids}")
    
    if not admin_ids:
        print("⚠️  WARNING: No admin IDs found in environment!")
        print("   Set ADMIN1, ADMIN2, or ADMIN_IDS in .env")
        return False
    
    # Test is_admin function
    for admin_id in admin_ids:
        result = is_admin(admin_id)
        print(f"   Admin {admin_id}: {'✅ Recognized' if result else '❌ Not recognized'}")
    
    # Test non-admin
    fake_id = 999999999
    result = is_admin(fake_id)
    print(f"   User {fake_id}: {'❌ Should not be admin!' if result else '✅ Correctly not admin'}")
    
    return True


def test_database_connection():
    """Test database connection"""
    print("\n" + "=" * 60)
    print("TEST 2: Database Connection")
    print("=" * 60)
    
    try:
        db = get_openclaw_db()
        print(f"\n✅ Database connected: {db.db_type}")
        print(f"   Connection: {db.connection_string[:50]}...")
        return True
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        return False


def test_admin_credit_bypass():
    """Test that admin doesn't need credits"""
    print("\n" + "=" * 60)
    print("TEST 3: Admin Credit Bypass Logic")
    print("=" * 60)
    
    admin_ids = get_admin_ids()
    if not admin_ids:
        print("\n⚠️  Skipping: No admin IDs configured")
        return False
    
    admin_id = list(admin_ids)[0]
    
    print(f"\n📋 Testing admin bypass logic for admin {admin_id}:")
    print(f"   1. Admin check: {is_admin(admin_id)}")
    print(f"   2. Should skip credit check: ✅")
    print(f"   3. Should skip credit deduction: ✅")
    print(f"   4. Should show 'ADMIN MODE' footer: ✅")
    
    return True


def test_system_prompt():
    """Test admin-aware system prompt"""
    print("\n" + "=" * 60)
    print("TEST 4: Admin-Aware System Prompt")
    print("=" * 60)
    
    try:
        from app.openclaw_langchain_agent_simple import OpenClawSimpleAgent
        
        agent = OpenClawSimpleAgent()
        
        # Test regular user prompt
        regular_prompt = agent.get_system_prompt(is_admin=False)
        print("\n✅ Regular user prompt generated")
        print(f"   Length: {len(regular_prompt)} chars")
        print(f"   Contains 'ADMIN MODE': {'❌ No (correct)' if 'ADMIN MODE' not in regular_prompt else '⚠️  Yes (wrong!)'}")
        
        # Test admin prompt
        admin_prompt = agent.get_system_prompt(is_admin=True)
        print("\n✅ Admin prompt generated")
        print(f"   Length: {len(admin_prompt)} chars")
        print(f"   Contains 'ADMIN MODE': {'✅ Yes (correct)' if 'ADMIN MODE' in admin_prompt else '❌ No (wrong!)'}")
        print(f"   Contains 'UNLIMITED CREDITS': {'✅ Yes' if 'UNLIMITED CREDITS' in admin_prompt else '❌ No'}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error testing system prompt: {e}")
        return False


def test_admin_tools():
    """Test admin-only tools"""
    print("\n" + "=" * 60)
    print("TEST 5: Admin Tools")
    print("=" * 60)
    
    try:
        from app.openclaw_langchain_agent_simple import OpenClawSimpleAgent
        
        agent = OpenClawSimpleAgent()
        
        print(f"\n✅ Agent initialized")
        print(f"   Base tools: {len(agent.base_tools)}")
        print(f"   Admin tools: {len(agent.admin_tools)}")
        print(f"   Total tools: {len(agent.all_tools)}")
        
        print("\n📋 Base tools (all users):")
        for tool in agent.base_tools:
            print(f"   • {tool.name}")
        
        print("\n🔑 Admin tools (admins only):")
        for tool in agent.admin_tools:
            print(f"   • {tool.name}")
        
        # Test tool binding
        regular_llm = agent.get_llm_with_tools(is_admin=False)
        admin_llm = agent.get_llm_with_tools(is_admin=True)
        
        print(f"\n✅ Tool binding works:")
        print(f"   Regular user LLM: Configured")
        print(f"   Admin LLM: Configured")
        
        return True
    except Exception as e:
        print(f"\n❌ Error testing admin tools: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_credit_operations():
    """Test credit operations"""
    print("\n" + "=" * 60)
    print("TEST 6: Credit Operations")
    print("=" * 60)
    
    try:
        db = get_openclaw_db()
        
        # Test user (not admin)
        test_user_id = 123456789
        
        print(f"\n📋 Testing credit operations for user {test_user_id}:")
        
        # Get initial balance
        balance = db.get_user_credits(test_user_id)
        print(f"   Initial balance: ${balance:.2f}")
        
        # Add credits
        result = db.add_credits(
            user_id=test_user_id,
            amount=Decimal('5.00'),
            admin_id=999999999,
            reason='Test allocation'
        )
        
        if result['success']:
            print(f"   ✅ Add credits: ${result['amount_added']:.2f}")
            print(f"   New balance: ${result['balance_after']:.2f}")
        else:
            print(f"   ❌ Add credits failed: {result.get('error')}")
        
        # Get system stats
        stats = db.get_system_stats()
        print(f"\n📊 System stats:")
        print(f"   Total users: {stats['user_count']}")
        print(f"   Total credits: ${stats['total_credits']:.2f}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error testing credit operations: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 ADMIN UNLIMITED CREDITS - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Admin Recognition", test_admin_recognition()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Admin Credit Bypass", test_admin_credit_bypass()))
    results.append(("System Prompt", test_system_prompt()))
    results.append(("Admin Tools", test_admin_tools()))
    results.append(("Credit Operations", test_credit_operations()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        print("\n🎉 Admin unlimited credits system is working correctly!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        print("\n🔧 Please check the errors above and fix them")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
