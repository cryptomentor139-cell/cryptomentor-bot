"""
Test /analyze BTCUSDT Command for Lifetime Premium Users
Task 5.1: Manual Signal Generation Fix

This test verifies:
1. Signal is generated successfully for lifetime premium users
2. No credit deduction occurs for lifetime premium users
3. Signal format matches CryptoMentor AI 3.0 format
4. No errors are thrown
"""

import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes
from app.handlers_manual_signals import cmd_analyze
from app.premium_checker import is_lifetime_premium, get_user_credit_balance


class TestAnalyzeCommand:
    """Test suite for /analyze command"""
    
    def __init__(self):
        self.test_results = []
        self.lifetime_premium_user_id = None
        
    async def setup_mock_update(self, user_id: int, command_args: list):
        """Create mock Update object for testing"""
        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        mock_user.first_name = "Test User"
        
        # Create mock chat
        mock_chat = Mock(spec=Chat)
        mock_chat.id = user_id
        
        # Create mock message
        mock_message = Mock(spec=Message)
        mock_message.reply_text = AsyncMock()
        mock_message.delete = AsyncMock()
        mock_message.chat = mock_chat
        
        # Create mock update
        mock_update = Mock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.message = mock_message
        
        # Create mock context
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.args = command_args
        
        return mock_update, mock_context
    
    def find_lifetime_premium_user(self):
        """Find a lifetime premium user from database for testing"""
        print("\n🔍 Searching for lifetime premium user in database...")
        
        try:
            from app.supabase_conn import get_supabase_client
            
            supabase = get_supabase_client()
            result = supabase.table("users").select(
                "telegram_id, username, is_premium, premium_until, credits"
            ).eq(
                "is_premium", True
            ).is_(
                "premium_until", "null"
            ).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                user = result.data[0]
                self.lifetime_premium_user_id = user['telegram_id']
                print(f"✅ Found lifetime premium user: {user['telegram_id']}")
                print(f"   Username: {user.get('username', 'N/A')}")
                print(f"   Credits: {user.get('credits', 0)}")
                return True
            else:
                print("❌ No lifetime premium users found in database")
                print("   Please create a test user with:")
                print("   - is_premium = true")
                print("   - premium_until = NULL")
                return False
                
        except Exception as e:
            print(f"❌ Error finding lifetime premium user: {e}")
            return False
    
    async def test_lifetime_premium_no_credit_deduction(self):
        """Test 1: Verify no credit deduction for lifetime premium users"""
        print("\n" + "="*70)
        print("TEST 1: Lifetime Premium - No Credit Deduction")
        print("="*70)
        
        if not self.lifetime_premium_user_id:
            print("⚠️ Skipping test - no lifetime premium user available")
            self.test_results.append(("Test 1", "SKIPPED", "No lifetime premium user"))
            return False
        
        user_id = self.lifetime_premium_user_id
        
        try:
            # Get initial credit balance
            initial_credits = get_user_credit_balance(user_id)
            print(f"\n📊 Initial credit balance: {initial_credits}")
            
            # Verify user is lifetime premium
            is_premium = is_lifetime_premium(user_id)
            print(f"👑 Is lifetime premium: {is_premium}")
            
            if not is_premium:
                print("❌ User is not lifetime premium!")
                self.test_results.append(("Test 1", "FAILED", "User not lifetime premium"))
                return False
            
            # Create mock update and context
            mock_update, mock_context = await self.setup_mock_update(user_id, ["BTCUSDT"])
            
            # Execute /analyze command
            print(f"\n🚀 Executing: /analyze BTCUSDT")
            await cmd_analyze(mock_update, mock_context)
            
            # Get final credit balance
            final_credits = get_user_credit_balance(user_id)
            print(f"📊 Final credit balance: {final_credits}")
            
            # Verify no credit deduction
            if initial_credits == final_credits:
                print("✅ PASS: No credits deducted (as expected for lifetime premium)")
                self.test_results.append(("Test 1", "PASSED", "No credit deduction"))
                return True
            else:
                print(f"❌ FAIL: Credits changed from {initial_credits} to {final_credits}")
                self.test_results.append(("Test 1", "FAILED", f"Credits deducted: {initial_credits - final_credits}"))
  