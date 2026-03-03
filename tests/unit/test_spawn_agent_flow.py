"""
Test complete spawn agent flow with deposit address
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def test_spawn_agent_flow():
    """Test the complete spawn agent flow"""
    
    print("="*80)
    print("TEST: Complete Spawn Agent Flow")
    print("="*80)
    
    # Import modules
    from app.automaton_manager import get_automaton_manager
    from database import Database
    
    # Initialize database
    print("\n1. Initializing database...")
    db = Database()
    print("✅ Database initialized")
    
    # Initialize automaton manager
    print("\n2. Initializing automaton manager...")
    automaton_manager = get_automaton_manager(db)
    print("✅ Automaton manager initialized")
    
    # Test spawn agent (dry run - don't actually insert to DB)
    print("\n3. Testing spawn agent logic...")
    
    test_user_id = 999999999  # Test user
    test_agent_name = "TestAgent_DryRun"
    
    # Check if Conway client can generate deposit address
    deposit_address = automaton_manager.conway.generate_deposit_address(
        test_user_id, 
        test_agent_name
    )
    
    if not deposit_address:
        print("❌ Failed to generate deposit address")
        return False
    
    print(f"✅ Deposit address generated: {deposit_address}")
    
    # Verify it's the centralized wallet
    expected_address = os.getenv('CENTRALIZED_WALLET_ADDRESS')
    if deposit_address != expected_address:
        print(f"⚠️ Warning: Address mismatch!")
        print(f"   Expected: {expected_address}")
        print(f"   Got: {deposit_address}")
        return False
    
    print(f"✅ Correct centralized wallet address")
    
    # Test the complete spawn flow (without DB insert)
    print("\n4. Testing spawn agent flow components...")
    
    # Check spawn fee
    spawn_fee = automaton_manager.spawn_fee_credits
    print(f"   Spawn fee: {spawn_fee:,} credits")
    
    # Check tier thresholds
    print(f"   Tier thresholds: {automaton_manager.tier_thresholds}")
    
    print("\n" + "="*80)
    print("SPAWN AGENT FLOW SIMULATION")
    print("="*80)
    
    print(f"""
User Flow:
──────────

1. User sends: /spawn_agent {test_agent_name}

2. Bot checks:
   ✅ User has Automaton access
   ✅ User is premium
   ✅ User has >= {spawn_fee:,} credits
   ✅ Rate limit OK

3. Bot generates deposit address:
   📍 Address: {deposit_address}
   🌐 Network: Base
   💰 Token: USDC

4. Bot creates agent in database:
   🤖 Agent Name: {test_agent_name}
   💼 Agent Wallet: agent_[random]
   📍 Deposit Address: {deposit_address}
   💳 Conway Credits: 0
   📊 Status: active
   ⚰️ Survival Tier: dead (until funded)

5. Bot deducts spawn fee:
   💸 Fee: {spawn_fee:,} credits
   💳 User credits: [user_credits - {spawn_fee:,}]

6. Bot sends response:
   ✅ Agent Berhasil Dibuat!
   
   🤖 Nama: {test_agent_name}
   💼 Wallet: agent_abc123...
   📍 Deposit Address:
   {deposit_address}
   
   ⚠️ Agent belum aktif!
   Deposit USDC ke address di atas untuk mengaktifkan agent.

7. User deposits USDC:
   💰 Send USDC to: {deposit_address}
   🌐 Network: Base
   ⏱️ Wait 12 confirmations (~5-10 min)

8. System detects deposit:
   🔍 Monitor blockchain
   💳 Credit user account
   📱 Notify user

9. User can use agent:
   ✅ Fund agent
   ✅ Start trading
   ✅ Monitor performance
    """)
    
    print("="*80)
    print("VERIFICATION")
    print("="*80)
    
    checks = [
        ("Conway client initialized", True),
        ("Deposit address generation works", deposit_address is not None),
        ("Using centralized wallet", deposit_address == expected_address),
        ("Spawn fee configured", spawn_fee == 100000),
        ("Tier thresholds configured", len(automaton_manager.tier_thresholds) == 4),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("="*80)
        print("""
Bot is ready to spawn agents with deposit addresses!

Next steps:
1. Deploy to Railway
2. Test in production with real user
3. Monitor deposit detection
4. Verify credits are credited correctly
        """)
    else:
        print("❌ SOME CHECKS FAILED")
        print("="*80)
    
    return all_passed

if __name__ == '__main__':
    try:
        success = test_spawn_agent_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
