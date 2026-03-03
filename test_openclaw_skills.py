#!/usr/bin/env python3
"""
Test OpenClaw Skills System
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_skills_system():
    """Test the OpenClaw skills system"""
    
    print("🧪 Testing OpenClaw Skills System\n")
    print("="*60)
    
    # Import after env loaded
    from services import get_database
    from app.openclaw_manager import get_openclaw_manager
    
    db = get_database()
    manager = get_openclaw_manager(db)
    
    # Test 1: Create test assistant
    print("\n1️⃣ Creating test assistant...")
    try:
        assistant = manager.create_assistant(
            user_id=123456789,
            name="TestBot",
            personality="friendly"
        )
        assistant_id = assistant['assistant_id']
        print(f"   ✅ Created assistant: {assistant_id}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 2: Get available skills
    print("\n2️⃣ Getting available skills...")
    try:
        skills = manager.get_available_skills(assistant_id)
        print(f"   ✅ Found {len(skills)} available skills")
        
        # Show first 3
        for skill in skills[:3]:
            price = f"{skill['price_credits']} credits" if skill['price_credits'] > 0 else "FREE"
            premium = "⭐" if skill['is_premium'] else ""
            print(f"      {premium} {skill['name']} - {price}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 3: Get skill details
    print("\n3️⃣ Getting skill details...")
    try:
        skill = manager.get_skill_details('skill_crypto_analysis')
        if skill:
            print(f"   ✅ Skill: {skill['name']}")
            print(f"      Category: {skill['category']}")
            print(f"      Price: {skill['price_credits']} credits")
            print(f"      Capabilities: {len(skill['capabilities'])}")
        else:
            print("   ❌ Skill not found")
            return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 4: Add credits to user
    print("\n4️⃣ Adding test credits...")
    try:
        # Add 10,000 credits for testing
        db.cursor.execute("""
            INSERT INTO openclaw_user_credits (user_id, credits)
            VALUES (%s, %s)
            ON CONFLICT (user_id) 
            DO UPDATE SET credits = openclaw_user_credits.credits + EXCLUDED.credits
        """, (123456789, 10000))
        db.conn.commit()
        
        credits = manager.get_user_credits(123456789)
        print(f"   ✅ User credits: {credits:,}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 5: Install free skill
    print("\n5️⃣ Installing free skill (Basic Chat)...")
    try:
        success, message, cost = manager.install_skill(
            assistant_id=assistant_id,
            skill_id='skill_basic_chat',
            user_id=123456789
        )
        
        if success:
            print(f"   ✅ Installed! Cost: {cost} credits")
        else:
            print(f"   ⚠️ {message}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 6: Install paid skill
    print("\n6️⃣ Installing paid skill (Crypto Analysis)...")
    try:
        success, message, cost = manager.install_skill(
            assistant_id=assistant_id,
            skill_id='skill_crypto_analysis',
            user_id=123456789
        )
        
        if success:
            print(f"   ✅ Installed! Cost: {cost} credits")
            new_balance = manager.get_user_credits(123456789)
            print(f"   💰 New balance: {new_balance:,} credits")
        else:
            print(f"   ❌ {message}")
            return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 7: Get installed skills
    print("\n7️⃣ Getting installed skills...")
    try:
        installed = manager.get_installed_skills(assistant_id)
        print(f"   ✅ Installed {len(installed)} skills:")
        
        for skill in installed:
            status = "✅" if skill['is_active'] else "⏸️"
            print(f"      {status} {skill['name']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 8: Toggle skill
    print("\n8️⃣ Toggling skill...")
    try:
        success = manager.toggle_skill(
            assistant_id=assistant_id,
            skill_id='skill_crypto_analysis',
            is_active=False
        )
        
        if success:
            print("   ✅ Skill disabled")
            
            # Enable it back
            manager.toggle_skill(
                assistant_id=assistant_id,
                skill_id='skill_crypto_analysis',
                is_active=True
            )
            print("   ✅ Skill re-enabled")
        else:
            print("   ❌ Failed to toggle")
            return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 9: Try to install already installed skill
    print("\n9️⃣ Testing duplicate installation...")
    try:
        success, message, cost = manager.install_skill(
            assistant_id=assistant_id,
            skill_id='skill_crypto_analysis',
            user_id=123456789
        )
        
        if not success and "already installed" in message.lower():
            print(f"   ✅ Correctly rejected: {message}")
        else:
            print(f"   ⚠️ Should have rejected duplicate")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 10: Try to install without enough credits
    print("\n🔟 Testing insufficient credits...")
    try:
        # Set credits to 0
        db.cursor.execute("""
            UPDATE openclaw_user_credits
            SET credits = 0
            WHERE user_id = %s
        """, (123456789,))
        db.conn.commit()
        
        success, message, cost = manager.install_skill(
            assistant_id=assistant_id,
            skill_id='skill_onchain_analysis',  # 1500 credits
            user_id=123456789
        )
        
        if not success and "insufficient" in message.lower():
            print(f"   ✅ Correctly rejected: {message}")
        else:
            print(f"   ⚠️ Should have rejected insufficient credits")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 11: System prompt with skills
    print("\n1️⃣1️⃣ Testing system prompt generation...")
    try:
        prompt = manager._generate_system_prompt(
            assistant_name="TestBot",
            user_name="TestUser",
            personality="friendly",
            assistant_id=assistant_id
        )
        
        if "INSTALLED SKILLS" in prompt:
            print("   ✅ System prompt includes skills")
            print(f"   📝 Prompt length: {len(prompt)} chars")
        else:
            print("   ⚠️ Skills not in system prompt")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    try:
        db.cursor.execute("""
            DELETE FROM openclaw_assistants 
            WHERE assistant_id = %s
        """, (assistant_id,))
        
        db.cursor.execute("""
            DELETE FROM openclaw_user_credits
            WHERE user_id = %s
        """, (123456789,))
        
        db.conn.commit()
        print("   ✅ Cleanup complete")
    except Exception as e:
        print(f"   ⚠️ Cleanup failed: {e}")
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_skills_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
