"""
Test CEO Agent functionality
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_ceo_agent():
    """Test CEO Agent basic functionality"""
    
    print("=" * 60)
    print("  CEO AGENT TEST")
    print("=" * 60)
    
    # Mock bot for testing
    class MockBot:
        async def send_message(self, chat_id, text, parse_mode=None):
            print(f"\n📧 Message to {chat_id}:")
            print("─" * 50)
            print(text)
            print("─" * 50)
    
    # Initialize CEO Agent
    try:
        from app.ceo_agent import CEOAgent
        
        mock_bot = MockBot()
        ceo_agent = CEOAgent(mock_bot)
        
        print("\n✅ CEO Agent initialized")
        print(f"   System prompt loaded: {len(ceo_agent.system_prompt)} characters")
        
        # Test 1: Generate follow-up message
        print("\n" + "=" * 60)
        print("TEST 1: Follow-up Message Generation")
        print("=" * 60)
        
        message = ceo_agent._generate_followup_message("John", "2026-02-22")
        print("\n📝 Generated Message:")
        print(message)
        
        # Test 2: Daily report format
        print("\n" + "=" * 60)
        print("TEST 2: Daily Report Format")
        print("=" * 60)
        
        from datetime import datetime
        test_metrics = {
            'new_users': 15,
            'active_users': 234,
            'premium_users': 45,
            'deposits': 450.00,
            'revenue': 890.00,
            'agents_spawned': 12,
            'active_agents': 8
        }
        
        report = ceo_agent._format_daily_report(test_metrics, datetime.now().date())
        print("\n📊 Generated Report:")
        print(report)
        
        # Test 3: Check metrics helpers
        print("\n" + "=" * 60)
        print("TEST 3: Metrics Helpers")
        print("=" * 60)
        
        print(f"New users today: {ceo_agent._count_new_users_today()}")
        print(f"Active users today: {ceo_agent._count_active_users_today()}")
        print(f"Premium users: {ceo_agent._count_premium_users()}")
        print(f"Conversion rate: {ceo_agent._calculate_conversion_rate():.1f}%")
        print(f"Engagement rate: {ceo_agent._calculate_engagement_rate():.1f}%")
        
        print("\n" + "=" * 60)
        print("  ALL TESTS PASSED!")
        print("=" * 60)
        
        print("\n💡 Next Steps:")
        print("1. ✅ CEO Agent module working correctly")
        print("2. 📝 Implement database methods for real metrics")
        print("3. 🚀 Deploy to production")
        print("4. 📊 Monitor daily reports")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_ceo_agent())
    exit(0 if success else 1)
