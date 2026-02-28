#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Conway Credits for User
Quick script to check current Conway credits balance
"""

import os
from dotenv import load_dotenv

load_dotenv()

def check_credits(user_id=1187119989):
    """Check Conway credits for a user"""
    try:
        from supabase_client import supabase
        
        if not supabase:
            print("❌ Supabase client not initialized")
            return
        
        print("=" * 60)
        print("💰 CONWAY CREDITS CHECK")
        print("=" * 60)
        
        # Query user_credits_balance
        result = supabase.table('user_credits_balance')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if result.data:
            data = result.data[0]
            available = float(data.get('available_credits', 0))
            total = float(data.get('total_conway_credits', 0))
            created = data.get('created_at', 'N/A')
            updated = data.get('updated_at', 'N/A')
            
            print(f"\n✅ Credits Found for User {user_id}")
            print(f"\n📊 Balance:")
            print(f"   • Available Credits: {available:,.2f}")
            print(f"   • Total Conway Credits: {total:,.2f}")
            
            print(f"\n📅 Timestamps:")
            print(f"   • Created: {created}")
            print(f"   • Updated: {updated}")
            
            print(f"\n🎯 Status:")
            if available > 0:
                print(f"   ✅ User has credits - Can spawn agents")
                print(f"   ✅ Menu will show: FULL AI Agent Menu")
                
                # Calculate how many agents can be spawned
                agents_can_spawn = int(available / 100)  # 100 credits per agent
                print(f"\n🤖 Agent Capacity:")
                print(f"   • Can spawn: {agents_can_spawn} agents")
                print(f"   • Cost per agent: 100 credits")
            else:
                print(f"   ⚠️  No credits available")
                print(f"   ⚠️  Menu will show: Deposit-First Menu")
                print(f"   💡 Need to deposit USDC to get credits")
            
        else:
            print(f"\n⚠️  No credits record found for user {user_id}")
            print(f"\n📝 This means:")
            print(f"   • User hasn't deposited yet")
            print(f"   • Menu will show: Deposit-First Menu")
            print(f"   • Need to deposit minimum 5 USDC")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_credits()
