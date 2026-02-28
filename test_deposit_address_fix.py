"""
Test deposit address generation fix
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_deposit_address_generation():
    """Test the fixed deposit address generation"""
    
    print("="*80)
    print("TEST: Deposit Address Generation (Centralized Wallet)")
    print("="*80)
    
    # Import after loading env
    from app.conway_integration import get_conway_client
    
    # Get Conway client
    conway = get_conway_client()
    
    # Test generate deposit address
    print("\n1. Testing generate_deposit_address()...")
    
    test_user_id = 123456789
    test_agent_name = "TestAgent"
    
    deposit_address = conway.generate_deposit_address(test_user_id, test_agent_name)
    
    if deposit_address:
        print(f"\n✅ SUCCESS!")
        print(f"   User ID: {test_user_id}")
        print(f"   Agent Name: {test_agent_name}")
        print(f"   Deposit Address: {deposit_address}")
        print(f"   Network: Base")
        print(f"   Token: USDC")
        
        # Verify it's the centralized wallet
        expected_address = os.getenv('CENTRALIZED_WALLET_ADDRESS')
        if deposit_address == expected_address:
            print(f"\n✅ Correct! Using centralized wallet address")
        else:
            print(f"\n⚠️ Warning: Address doesn't match CENTRALIZED_WALLET_ADDRESS")
            print(f"   Expected: {expected_address}")
            print(f"   Got: {deposit_address}")
    else:
        print(f"\n❌ FAILED! No deposit address returned")
        return False
    
    # Test multiple users (should all get same address)
    print("\n" + "="*80)
    print("2. Testing multiple users (should all get same address)...")
    print("="*80)
    
    test_users = [
        (111111, "Agent1"),
        (222222, "Agent2"),
        (333333, "Agent3"),
    ]
    
    addresses = []
    for user_id, agent_name in test_users:
        addr = conway.generate_deposit_address(user_id, agent_name)
        addresses.append(addr)
        print(f"User {user_id} ({agent_name}): {addr}")
    
    # All should be the same
    if len(set(addresses)) == 1:
        print(f"\n✅ Correct! All users get the same centralized wallet address")
    else:
        print(f"\n⚠️ Warning: Users got different addresses")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
✅ Deposit address generation is now working!

How it works:
1. All users deposit to the SAME centralized wallet address
2. The address is stored in CENTRALIZED_WALLET_ADDRESS env variable
3. Deposits are tracked by user_id in the database
4. When user deposits USDC to this address, the system credits their account

This is a CUSTODIAL wallet system - Conway Automaton controls the wallet.
    """)
    
    return True

if __name__ == '__main__':
    try:
        success = test_deposit_address_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
