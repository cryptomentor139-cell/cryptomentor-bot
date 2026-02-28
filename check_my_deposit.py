#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk cek deposit dan credits Anda
"""

import os
from dotenv import load_dotenv

load_dotenv()

def check_my_credits():
    """Check credits for admin user"""
    print("=" * 60)
    print("CHECKING YOUR DEPOSIT & CREDITS")
    print("=" * 60)
    
    try:
        from database import Database
        
        db = Database()
        
        if not db.supabase_enabled:
            print("❌ Supabase not enabled")
            return
        
        # Your admin user ID
        admin_user_id = 1187119989
        
        print(f"\n👤 Checking user ID: {admin_user_id}")
        
        # Check user_credits_balance table
        print("\n1. Checking user_credits_balance table...")
        try:
            result = db.supabase_service.table('user_credits_balance')\
                .select('*')\
                .eq('user_id', admin_user_id)\
                .execute()
            
            if result.data:
                balance = result.data[0]
                print("✅ Found balance record:")
                print(f"   • Total Deposits: {balance.get('total_deposits_count', 0)}")
                print(f"   • Total USDT: ${balance.get('total_deposited_usdt', 0):,.2f}")
                print(f"   • Total USDC: ${balance.get('total_deposited_usdc', 0):,.2f}")
                print(f"   • Total Conway Credits: {balance.get('total_conway_credits', 0):,.2f}")
                print(f"   • Available Credits: {balance.get('available_credits', 0):,.2f}")
                print(f"   • Spent Credits: {balance.get('spent_credits', 0):,.2f}")
                print(f"   • First Deposit: {balance.get('first_deposit_at', 'N/A')}")
                print(f"   • Last Deposit: {balance.get('last_deposit_at', 'N/A')}")
            else:
                print("❌ No balance record found")
                print("   This means no deposits have been credited yet")
        except Exception as e:
            print(f"❌ Error checking balance: {e}")
        
        # Check deposit_transactions table
        print("\n2. Checking deposit_transactions table...")
        try:
            result = db.supabase_service.table('deposit_transactions')\
                .select('*')\
                .eq('user_id', admin_user_id)\
                .order('created_at', desc=True)\
                .execute()
            
            if result.data:
                print(f"✅ Found {len(result.data)} deposit transaction(s):")
                for i, tx in enumerate(result.data, 1):
                    print(f"\n   Transaction #{i}:")
                    print(f"   • TX Hash: {tx.get('tx_hash', 'N/A')}")
                    print(f"   • From: {tx.get('from_address', 'N/A')}")
                    print(f"   • Network: {tx.get('network', 'N/A')}")
                    print(f"   • Token: {tx.get('token', 'N/A')}")
                    print(f"   • Amount: ${tx.get('amount', 0):,.2f}")
                    print(f"   • Conway Credits: {tx.get('conway_credits', 0):,.2f}")
                    print(f"   • Status: {tx.get('status', 'N/A')}")
                    print(f"   • Created: {tx.get('created_at', 'N/A')}")
                    print(f"   • Credited: {tx.get('credited_at', 'N/A')}")
            else:
                print("❌ No deposit transactions found")
                print("   This means your deposit hasn't been detected yet")
        except Exception as e:
            print(f"❌ Error checking transactions: {e}")
        
        # Check pending_deposits table
        print("\n3. Checking pending_deposits table...")
        try:
            result = db.supabase_service.table('pending_deposits')\
                .select('*')\
                .eq('user_id', admin_user_id)\
                .execute()
            
            if result.data:
                pending = result.data[0]
                print("✅ Found pending deposit record:")
                print(f"   • Status: {pending.get('status', 'N/A')}")
                print(f"   • Created: {pending.get('created_at', 'N/A')}")
                print(f"   • Expires: {pending.get('expires_at', 'N/A')}")
            else:
                print("ℹ️  No pending deposit record")
        except Exception as e:
            print(f"❌ Error checking pending: {e}")
        
        # Check centralized wallet address
        print("\n4. Centralized Wallet Info:")
        wallet_address = os.getenv('CENTRALIZED_WALLET_ADDRESS', '0x63116672bef9f26fd906cd2a57550f7a13925822')
        print(f"   • Address: {wallet_address}")
        print(f"   • Network: Base")
        print(f"   • Token: USDC")
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        try:
            result = db.supabase_service.table('user_credits_balance')\
                .select('available_credits')\
                .eq('user_id', admin_user_id)\
                .execute()
            
            if result.data:
                available = float(result.data[0].get('available_credits', 0))
                if available > 0:
                    print(f"✅ You have {available:,.2f} Conway Credits available")
                    print(f"💵 Equivalent to ${available/100:,.2f} USDC")
                    
                    # Check if can spawn
                    if available >= 100:
                        max_agents = int(available / 100)
                        print(f"🤖 You can spawn up to {max_agents} agent(s)")
                    else:
                        print(f"⚠️  Need {100-available:,.2f} more credits to spawn an agent")
                else:
                    print("❌ No credits available")
                    print("\n💡 Possible reasons:")
                    print("   1. Deposit hasn't been detected yet (wait for 12 confirmations)")
                    print("   2. Deposit was to wrong address")
                    print("   3. Deposit was on wrong network (must be Base)")
                    print("   4. Deposit was wrong token (must be USDC)")
            else:
                print("❌ No balance record found")
                print("\n💡 Your deposit hasn't been processed yet")
                print("   Please wait for:")
                print("   • 12 blockchain confirmations (~5-10 minutes)")
                print("   • Conway Dashboard to detect deposit")
                print("   • Webhook to credit your account")
        except Exception as e:
            print(f"❌ Error getting summary: {e}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_my_credits()
