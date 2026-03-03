#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick script to credit your own deposit
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# YOUR DETAILS
ADMIN_USER_ID = 1187119989
DEPOSIT_AMOUNT_USDC = 10.0

def credit_deposit():
    """Credit deposit to admin account"""
    print("=" * 60)
    print("CREDITING YOUR DEPOSIT")
    print("=" * 60)
    
    try:
        from supabase_client import supabase
        
        if not supabase:
            print("❌ Supabase not initialized")
            return False
        
        conway_credits = DEPOSIT_AMOUNT_USDC * 100
        centralized_wallet = os.getenv('CENTRALIZED_WALLET_ADDRESS', '0x63116672bef9f26fd906cd2a57550f7a13925822')
        
        print(f"\n💰 Crediting ${DEPOSIT_AMOUNT_USDC:,.2f} USDC = {conway_credits:,.2f} credits")
        print(f"👤 To user: {ADMIN_USER_ID}")
        
        # 1. Create deposit transaction
        print("\n1. Creating deposit transaction...")
        tx_data = {
            'tx_hash': f'manual_admin_{int(datetime.now().timestamp())}',
            'from_address': 'admin_metamask',
            'to_address': centralized_wallet,
            'network': 'base',
            'token': 'USDC',
            'amount': DEPOSIT_AMOUNT_USDC,
            'conway_credits': conway_credits,
            'user_id': ADMIN_USER_ID,
            'status': 'credited',
            'confirmations': 12,
            'webhook_received_at': datetime.now().isoformat(),
            'credited_at': datetime.now().isoformat()
        }
        
        result = supabase.table('deposit_transactions').insert(tx_data).execute()
        
        if result.data:
            print("✅ Transaction created")
            tx_id = result.data[0]['id']
        else:
            print("❌ Failed to create transaction")
            return False
        
        # 2. Update balance
        print("\n2. Updating balance...")
        
        # Check existing
        existing = supabase.table('user_credits_balance')\
            .select('*')\
            .eq('user_id', ADMIN_USER_ID)\
            .execute()
        
        if existing.data:
            # Update
            current = existing.data[0]
            new_data = {
                'total_deposits_count': current.get('total_deposits_count', 0) + 1,
                'total_deposited_usdc': float(current.get('total_deposited_usdc', 0)) + DEPOSIT_AMOUNT_USDC,
                'total_conway_credits': float(current.get('total_conway_credits', 0)) + conway_credits,
                'available_credits': float(current.get('available_credits', 0)) + conway_credits,
                'last_deposit_at': datetime.now().isoformat()
            }
            
            result = supabase.table('user_credits_balance')\
                .update(new_data)\
                .eq('user_id', ADMIN_USER_ID)\
                .execute()
            
            print("✅ Balance updated")
        else:
            # Create new
            new_data = {
                'user_id': ADMIN_USER_ID,
                'total_deposits_count': 1,
                'total_deposited_usdc': DEPOSIT_AMOUNT_USDC,
                'total_conway_credits': conway_credits,
                'available_credits': conway_credits,
                'spent_credits': 0,
                'first_deposit_at': datetime.now().isoformat(),
                'last_deposit_at': datetime.now().isoformat()
            }
            
            result = supabase.table('user_credits_balance')\
                .insert(new_data)\
                .execute()
            
            print("✅ Balance created")
        
        if result.data:
            balance = result.data[0]
            available = balance.get('available_credits', 0)
            
            print(f"\n💰 New Balance: {available:,.2f} Conway Credits")
            print(f"💵 Equivalent: ${available/100:,.2f} USDC")
            print(f"🤖 Can spawn: {int(available/100)} agent(s)")
        
        # 3. Log transaction
        print("\n3. Logging transaction...")
        try:
            log_data = {
                'user_id': ADMIN_USER_ID,
                'transaction_type': 'deposit',
                'amount': conway_credits,
                'balance_before': float(current.get('available_credits', 0)) if existing.data else 0,
                'balance_after': available,
                'description': f'Manual deposit: ${DEPOSIT_AMOUNT_USDC:,.2f} USDC via MetaMask',
                'reference_id': tx_id
            }
            
            supabase.table('credit_transactions').insert(log_data).execute()
            print("✅ Transaction logged")
        except Exception as e:
            print(f"⚠️  Log warning: {e}")
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"🎉 Your deposit has been credited!")
        print(f"💰 You now have {available:,.2f} Conway Credits")
        print(f"\n📱 Next steps:")
        print("   1. Open your Telegram bot")
        print("   2. Click '🤖 AI Agent' menu")
        print("   3. Click '📊 Agent Status' to verify balance")
        print("   4. Click '🚀 Spawn Agent' to create your first agent!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    credit_deposit()
