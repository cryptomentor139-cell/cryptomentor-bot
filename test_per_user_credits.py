#!/usr/bin/env python3
"""
Test Per-User Credit System
Verifies the implementation works correctly
"""

import os
import sys
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services import get_database
from app.openclaw_user_credits import (
    get_user_credits,
    add_credits,
    deduct_credits,
    get_total_allocated,
    check_allocation_limit
)


def test_credit_system():
    """Test the per-user credit system"""
    print("🧪 Testing Per-User Credit System\n")
    
    try:
        db = get_database()
        
        # Test user IDs
        test_user_id = 999999999  # Fake user for testing
        test_admin_id = 123456789  # Fake admin
        
        print("1️⃣ Testing get_user_credits...")
        credits = get_user_credits(db, test_user_id)
        print(f"   ✅ User {test_user_id} has ${float(credits):.2f}")
        
        print("\n2️⃣ Testing add_credits...")
        success, new_balance, msg = add_credits(
            db=db,
            user_id=test_user_id,
            amount=Decimal('10.00'),
            admin_id=test_admin_id,
            reason="Test allocation"
        )
        if success:
            print(f"   ✅ Added $10.00. New balance: ${float(new_balance):.2f}")
        else:
            print(f"   ❌ Failed: {msg}")
            return False
        
        print("\n3️⃣ Testing deduct_credits...")
        success, new_balance, msg = deduct_credits(
            db=db,
            user_id=test_user_id,
            amount=Decimal('0.05'),
            assistant_id="test-assistant",
            conversation_id="test-conv",
            input_tokens=100,
            output_tokens=200,
            model_used="openai/gpt-4.1"
        )
        if success:
            print(f"   ✅ Deducted $0.05. New balance: ${float(new_balance):.2f}")
        else:
            print(f"   ❌ Failed: {msg}")
            return False
        
        print("\n4️⃣ Testing get_total_allocated...")
        total = get_total_allocated(db)
        print(f"   ✅ Total allocated to all users: ${float(total):.2f}")
        
        print("\n5️⃣ Testing check_allocation_limit...")
        can_allocate, msg = check_allocation_limit(
            db=db,
            amount=Decimal('5.00'),
            openrouter_balance=Decimal('100.00')
        )
        if can_allocate:
            print(f"   ✅ Can allocate $5.00: {msg}")
        else:
            print(f"   ⚠️ Cannot allocate: {msg}")
        
        print("\n6️⃣ Testing over-allocation prevention...")
        can_allocate, msg = check_allocation_limit(
            db=db,
            amount=Decimal('1000.00'),
            openrouter_balance=Decimal('100.00')
        )
        if not can_allocate:
            print(f"   ✅ Correctly prevented over-allocation: {msg}")
        else:
            print(f"   ❌ Should have prevented over-allocation!")
            return False
        
        print("\n7️⃣ Testing insufficient balance...")
        success, new_balance, msg = deduct_credits(
            db=db,
            user_id=test_user_id,
            amount=Decimal('1000.00'),  # More than user has
            assistant_id="test-assistant",
            input_tokens=100,
            output_tokens=200
        )
        if not success:
            print(f"   ✅ Correctly prevented deduction: {msg}")
        else:
            print(f"   ❌ Should have prevented deduction!")
            return False
        
        print("\n8️⃣ Cleaning up test data...")
        cursor = db.cursor()
        cursor.execute("DELETE FROM openclaw_credit_usage WHERE user_id = %s", (test_user_id,))
        cursor.execute("DELETE FROM openclaw_credit_allocations WHERE user_id = %s", (test_user_id,))
        cursor.execute("DELETE FROM openclaw_user_credits WHERE user_id = %s", (test_user_id,))
        db.commit()
        cursor.close()
        print("   ✅ Test data cleaned up")
        
        print("\n✅ All tests passed!")
        print("\n📋 Summary:")
        print("  • Per-user credit tracking: ✅")
        print("  • Credit allocation: ✅")
        print("  • Credit deduction: ✅")
        print("  • Over-allocation prevention: ✅")
        print("  • Insufficient balance check: ✅")
        print("  • Total allocated calculation: ✅")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_credit_system()
    sys.exit(0 if success else 1)

