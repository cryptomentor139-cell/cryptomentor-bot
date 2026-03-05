"""
Test OpenClaw LangChain Implementation
"""

import os
import sys
import asyncio
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.openclaw_langchain_db import get_openclaw_db
from app.openclaw_langchain_agent_simple import get_openclaw_agent


async def test_database():
    """Test database operations"""
    print("=" * 60)
    print("TEST 1: Database Operations")
    print("=" * 60)
    
    try:
        db = get_openclaw_db()
        print(f"✅ Database initialized: {db.db_type}")
        
        # Test user 123456789
        test_user_id = 123456789
        
        # Get credits
        credits = db.get_user_credits(test_user_id)
        print(f"✅ User {test_user_id} credits: ${credits:.2f}")
        
        # Add credits
        result = db.add_credits(
            user_id=test_user_id,
            amount=Decimal('0.5'),
            admin_id=1087836223,
            reason='Test allocation'
        )
        
        if result['success']:
            print(f"✅ Added credits: ${result['amount_added']:.2f}")
            print(f"   Balance: ${result['balance_before']:.2f} → ${result['balance_after']:.2f}")
        else:
            print(f"❌ Failed to add credits: {result.get('error')}")
        
        # Get system stats
        stats = db.get_system_stats()
        print(f"✅ System stats:")
        print(f"   Users: {stats['user_count']}")
        print(f"   Total credits: ${stats['total_credits']:.2f}")
        print(f"   Total allocated: ${stats['total_allocated']:.2f}")
        print(f"   Total used: ${stats['total_used']:.2f}")
        
        print("\n✅ Database tests passed!\n")
        return True
    
    except Exception as e:
        print(f"\n❌ Database test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_agent():
    """Test agent operations"""
    print("=" * 60)
    print("TEST 2: Agent Operations")
    print("=" * 60)
    
    try:
        agent = get_openclaw_agent()
        print("✅ Agent initialized")
        
        # Test user
        test_user_id = 123456789
        
        # Test chat
        print("\n📝 Testing chat: 'What is Bitcoin?'")
        result = await agent.chat(
            user_id=test_user_id,
            message="What is Bitcoin?",
            deduct_credits=False  # Don't deduct for test
        )
        
        if result['success']:
            print(f"✅ Agent response:")
            print(f"   {result['response'][:200]}...")
            print(f"   Credits would be used: ${result['credits_used']:.4f}")
        else:
            print(f"❌ Agent failed: {result.get('error')}")
        
        print("\n✅ Agent tests passed!\n")
        return True
    
    except Exception as e:
        print(f"\n❌ Agent test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_tools():
    """Test agent tools"""
    print("=" * 60)
    print("TEST 3: Agent Tools")
    print("=" * 60)
    
    try:
        agent = get_openclaw_agent()
        
        # Test crypto price
        print("\n📝 Testing tool: get_crypto_price")
        result = agent.get_crypto_price("bitcoin")
        print(f"✅ Result: {result}")
        
        # Test crypto price with symbol
        print("\n📝 Testing tool: get_crypto_price (eth)")
        result = agent.get_crypto_price("eth")
        print(f"✅ Result: {result}")
        
        print("\n✅ Tool tests passed!\n")
        return True
    
    except Exception as e:
        print(f"\n❌ Tool test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("OpenClaw LangChain Implementation Tests")
    print("=" * 60 + "\n")
    
    # Check environment
    if not os.getenv('OPENCLAW_API_KEY'):
        print("❌ OPENCLAW_API_KEY not found in environment")
        print("   Please set it in .env file")
        return
    
    print(f"✅ OPENCLAW_API_KEY found")
    print(f"✅ Database path: {os.getenv('DATABASE_PATH', 'cryptomentor.db')}\n")
    
    # Run tests
    results = []
    
    results.append(await test_database())
    results.append(await test_agent())
    results.append(await test_tools())
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED! 🎉")
        print("\nNext steps:")
        print("1. Update bot.py to use LangChain handlers")
        print("2. Deploy to Railway")
        print("3. Test with real users")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease fix errors before deploying")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
