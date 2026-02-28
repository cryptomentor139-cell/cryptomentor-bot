#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk manually credit deposit yang sudah masuk ke centralized wallet
Digunakan ketika user deposit langsung via MetaMask tanpa melalui bot
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def manual_credit_deposit(
    user_id: int,
    amount_usdc: float,
    tx_hash: str = None,
    from_address: str = None
):
    """
    Manually credit a deposit to user's account
    
    Args:
        user_id: Telegram user ID
        amount_usdc: Amount of USDC deposited
        tx_hash: Transaction hash (optional)
        from_address: Sender's wallet address (optional)
    """
    print("=" * 60)
    print("MANUAL DEPOSIT CREDIT")
    print("=" * 60)
    
    try:
        from database import Database
        
        db = Database()
        
        if not db.supabase_enabled:
            print("❌ Supabase not enabled")
            return False
        
        # Calculate Conway credits (1 USDC = 100 credits)
        conway_credits = amount_usdc * 100
        
        print(f"\n📋 Deposit Details:")
        print(f"   • User ID: {user_id}")
        print(f"   • Amount: ${amount_usdc:,.2f} USDC")
        print(f"   • Conway Credits: {conway_credits:,.2f}")
        print(f"   • TX Hash: {tx_hash or 'Not provided'}")
        print(f"   • From Address: {from_address or 'Not provided'}")
        
        # Confirm
        print(f"\n⚠️  WARNING: This will credit {conway_credits:,.2f} credits to user {user_id}")
        confirm = input("Type 'YES' to confirm: ")
        
        if confirm != 'YES':
            print("❌ Cancelled")
            return False
        
        # Get centralized wallet address
        centralized_wallet = os.getenv('CENTRALIZED_WALLET_ADDRESS', '0x63116672bef9f26fd906cd2a57550f7a13925822')
        
        # Create deposit transaction record
        print("\n1. Creating deposit transaction record...")
        try:
            tx_data = {
                'tx_hash': tx_hash or f'manual_{user_id}_{int(datetime.now().timestamp())}',
                'from_address': from_address or 'manual_deposit',
                'to_address': centralized_wallet,
                'network': 'base',
                'token': 'USDC',
                'amount': amount_usdc,
                'conway_credits': conway_credits,
                'user_id': user_id,
                'status': 'credited',
                'confirmations': 12,
                'webhook_received_at': datetime.now().isoformat(),
                'credited_at': datetime.now().isoformat()
            }
            
            result = db.supabase_service.table('deposit_transactions').insert(tx_data).execute()
            
            if result.data:
                print("✅ Deposit transaction created")
                tx_id = result.data[0]['id']
                print(f"   • Transaction ID: {tx_id}")
            else:
                print("❌ Failed to create transaction")
                return False
                
        except Exception as e:
            print(f"❌ Error creating transaction: {e}")
            return False
        
        # Check if user_credits_balance exists
        print("\n2. Updating user credits balance...")
        try:
            # Check existing balance
            existing = db.supabase_service.table('user_credits_balance')\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()
            
            if existing.data:
                # Update existing balance
                current = existing.data[0]
                new_data = {
                    'total_deposits_count': current.get('total_deposits_count', 0) + 1,
                    'total_deposited_usdc': float(current.get('total_deposited_usdc', 0)) + amount_usdc,
                    'total_conway_credits': float(current.get('total_conway_credits', 0)) + conway_credits,
                    'available_credits': float(current.get('available_credits', 0)) + conway_credits,
                    'last_deposit_at': datetime.now().isoformat()
                }
                
                result = db.supabase_service.table('user_credits_balance')\
                    .update(new_data)\
                    .eq('user_id', user_id)\
                    .execute()
                
                print("✅ Updated existing balance")
            else:
                # Create new balance record
                new_data = {
                    'user_id': user_id,
                    'total_deposits_count': 1,
                    'total_deposited_usdc': amount_usdc,
                    'total_conway_credits': conway_credits,
                    'available_credits': conway_credits,
                    'spent_credits': 0,
                    'first_deposit_at': datetime.now().isoformat(),
                    'last_deposit_at': datetime.now().isoformat()
                }
                
                result = db.supabase_service.table('user_credits_balance')\
                    .insert(new_data)\
                    .execute()
                
                print("✅ Created new balance record")
            
            if result.data:
                balance = result.data[0]
                print(f"   • Total Credits: {balance.get('total_conway_credits', 0):,.2f}")
                print(f"   • Available: {balance.get('available_credits', 0):,.2f}")
                print(f"   • Spent: {balance.get('spent_credits', 0):,.2f}")
            
        except Exception as e:
            print(f"❌ Error updating balance: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Create credit transaction log
        print("\n3. Creating credit transaction log...")
        try:
            log_data = {
                'user_id': user_id,
                'transaction_type': 'deposit',
                'amount': conway_credits,
                'balance_before': float(current.get('available_credits', 0)) if existing.data else 0,
                'balance_after': float(current.get('available_credits', 0)) + conway_credits if existing.data else conway_credits,
                'description': f'Manual deposit credit: ${amount_usdc:,.2f} USDC',
                'reference_id': tx_id
            }
            
            result = db.supabase_service.table('credit_transactions').insert(log_data).execute()
            
            if result.data:
                print("✅ Credit transaction logged")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not create log: {e}")
            # Not critical, continue
        
        # Success summary
        print("\n" + "=" * 60)
        print("✅ DEPOSIT CREDITED SUCCESSFULLY!")
        print("=" * 60)
        print(f"💰 User {user_id} now has {conway_credits:,.2f} Conway Credits")
        print(f"💵 Equivalent to ${amount_usdc:,.2f} USDC")
        print(f"🤖 Can spawn {int(conway_credits / 100)} agent(s)")
        print("\n💡 User can now:")
        print("   1. Open Telegram bot")
        print("   2. Click '🤖 AI Agent' menu")
        print("   3. Click '🚀 Spawn Agent'")
        print("   4. Start trading!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("\n" + "🏦" * 30)
    print("MANUAL DEPOSIT CREDIT TOOL")
    print("🏦" * 30 + "\n")
    
    print("This tool manually credits a deposit to a user's account")
    print("Use this when user deposits directly via MetaMask\n")
    
    # Get user input
    try:
        user_id = int(input("Enter Telegram User ID: "))
        amount_usdc = float(input("Enter USDC amount deposited: "))
        tx_hash = input("Enter transaction hash (optional, press Enter to skip): ").strip()
        from_address = input("Enter sender wallet address (optional, press Enter to skip): ").strip()
        
        if not tx_hash:
            tx_hash = None
        if not from_address:
            from_address = None
        
        # Validate
        if amount_usdc < 5:
            print(f"❌ Minimum deposit is 5 USDC (you entered {amount_usdc})")
            return
        
        # Execute
        success = manual_credit_deposit(user_id, amount_usdc, tx_hash, from_address)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
