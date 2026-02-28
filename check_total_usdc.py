#!/usr/bin/env python3
"""
Check Total USDC from All Users

This script queries Supabase to get total USDC balance across all custodial wallets
and displays detailed statistics.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def check_total_usdc():
    """Query and display total USDC statistics"""
    print("=" * 70)
    print("💰 TOTAL USDC BALANCE - ALL USERS")
    print("=" * 70)
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_service_key:
        print("❌ Supabase credentials not found in .env file!")
        print()
        print("Please set:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_SERVICE_KEY=your_service_role_key")
        return
    
    try:
        # Connect to Supabase
        print("🔌 Connecting to Supabase...")
        supabase: Client = create_client(supabase_url, supabase_service_key)
        print("✅ Connected!")
        print()
        
        # Query all custodial wallets
        print("📊 Fetching wallet data...")
        result = supabase.table('custodial_wallets').select('*').execute()
        
        if not result.data:
            print("⚠️  No custodial wallets found in database")
            print()
            print("This is normal if no users have deposited yet.")
            return
        
        wallets = result.data
        print(f"✅ Found {len(wallets)} custodial wallets")
        print()
        
        # Calculate statistics
        total_usdc = 0
        total_conway_credits = 0
        wallets_with_balance = 0
        wallets_with_credits = 0
        
        print("=" * 70)
        print("📋 WALLET DETAILS")
        print("=" * 70)
        print()
        
        for wallet in wallets:
            user_id = wallet.get('user_id')
            wallet_address = wallet.get('wallet_address')
            balance_usdc = float(wallet.get('balance_usdc', 0))
            conway_credits = float(wallet.get('conway_credits', 0))
            created_at = wallet.get('created_at', 'Unknown')
            
            total_usdc += balance_usdc
            total_conway_credits += conway_credits
            
            if balance_usdc > 0:
                wallets_with_balance += 1
            if conway_credits > 0:
                wallets_with_credits += 1
            
            # Display wallet info
            print(f"👤 User ID: {user_id}")
            print(f"   Wallet: {wallet_address[:10]}...{wallet_address[-8:]}")
            print(f"   USDC Balance: ${balance_usdc:.2f}")
            print(f"   Conway Credits: {conway_credits:.0f}")
            print(f"   Created: {created_at[:10]}")
            print()
        
        # Display summary statistics
        print("=" * 70)
        print("📊 SUMMARY STATISTICS")
        print("=" * 70)
        print()
        print(f"💰 Total USDC Balance: ${total_usdc:.2f}")
        print(f"🎯 Total Conway Credits: {total_conway_credits:.0f}")
        print(f"👥 Total Wallets: {len(wallets)}")
        print(f"💵 Wallets with USDC: {wallets_with_balance}")
        print(f"⚡ Wallets with Credits: {wallets_with_credits}")
        print()
        
        # Calculate averages
        if len(wallets) > 0:
            avg_usdc = total_usdc / len(wallets)
            avg_credits = total_conway_credits / len(wallets)
            print(f"📈 Average USDC per Wallet: ${avg_usdc:.2f}")
            print(f"📈 Average Credits per Wallet: {avg_credits:.0f}")
            print()
        
        # Conversion info
        expected_credits = total_usdc * 100
        credit_difference = total_conway_credits - expected_credits
        
        print("=" * 70)
        print("💱 CONVERSION ANALYSIS")
        print("=" * 70)
        print()
        print(f"Expected Credits (1 USDC = 100 Credits): {expected_credits:.0f}")
        print(f"Actual Credits: {total_conway_credits:.0f}")
        print(f"Difference: {credit_difference:+.0f}")
        print()
        
        if abs(credit_difference) > 1:
            print("⚠️  Note: Difference may be due to:")
            print("   - Manual credit adjustments")
            print("   - Bonus credits")
            print("   - Agent spending")
            print()
        
        # Top wallets
        print("=" * 70)
        print("🏆 TOP 5 WALLETS BY USDC BALANCE")
        print("=" * 70)
        print()
        
        sorted_wallets = sorted(wallets, key=lambda w: float(w.get('balance_usdc', 0)), reverse=True)
        for i, wallet in enumerate(sorted_wallets[:5], 1):
            user_id = wallet.get('user_id')
            balance_usdc = float(wallet.get('balance_usdc', 0))
            conway_credits = float(wallet.get('conway_credits', 0))
            
            print(f"{i}. User {user_id}")
            print(f"   USDC: ${balance_usdc:.2f} | Credits: {conway_credits:.0f}")
            print()
        
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    check_total_usdc()

if __name__ == "__main__":
    main()
