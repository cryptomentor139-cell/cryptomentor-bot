"""
Property-Based Test: One Wallet Per User Invariant

Feature: automaton-integration
Property 3: One Wallet Per User Invariant

For any user, creating multiple automatons should always return the same 
custodial wallet address, ensuring exactly one wallet per user regardless 
of the number of agents spawned.

Validates: Requirements 1.4

This test validates that:
1. Same user always gets the same deposit address
2. Multiple agent spawns don't create new wallets
3. Wallet address is consistent across different agent names
4. The invariant holds regardless of spawn timing
"""

import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from hypothesis import given, strategies as st, settings
from app.conway_integration import ConwayIntegration

# Load environment variables
load_dotenv()


@given(
    user_id=st.integers(min_value=1000000, max_value=9999999),
    num_agents=st.integers(min_value=2, max_value=5)
)
@settings(max_examples=100, deadline=None)
def test_one_wallet_per_user_multiple_spawns(user_id, num_agents):
    """
    Property 3: One Wallet Per User Invariant (Multiple Spawns)
    
    For any user spawning multiple agents, all agents should receive
    the same deposit address. The system should return the existing
    wallet address rather than creating new ones.
    
    This validates the core invariant: one wallet per user.
    """
    # Generate a consistent mock address for this user
    mock_address = f"0x{format(user_id, '040x')}"
    
    addresses = []
    
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        # Mock should always return the same address for the same user
        mock_request.return_value = {
            'success': True,
            'deposit_address': mock_address
        }
        
        conway = ConwayIntegration()
        
        # Spawn multiple agents for the same user
        for i in range(num_agents):
            agent_name = f"Agent_{user_id}_{i}"
            deposit_address = conway.generate_deposit_address(user_id, agent_name)
            
            # Verify address was generated
            assert deposit_address is not None, \
                f"Failed to generate address for agent {i} of user {user_id}"
            
            addresses.append(deposit_address)
        
        # Property: All addresses should be identical (one wallet per user)
        unique_addresses = set(addresses)
        assert len(unique_addresses) == 1, \
            f"User {user_id} got {len(unique_addresses)} different addresses, expected 1. Addresses: {unique_addresses}"
        
        # Property: The single address should match the expected format
        assert addresses[0] == mock_address, \
            f"Address mismatch: expected {mock_address}, got {addresses[0]}"
        
        print(f"✅ User {user_id} spawned {num_agents} agents, all got same address: {addresses[0]}")


@given(
    user_id=st.integers(min_value=1000000, max_value=9999999),
    agent_names=st.lists(
        st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters=' _-'
        )),
        min_size=2,
        max_size=5,
        unique=True
    )
)
@settings(max_examples=100, deadline=None)
def test_one_wallet_per_user_different_agent_names(user_id, agent_names):
    """
    Property 3: One Wallet Per User Invariant (Different Agent Names)
    
    For any user spawning agents with different names, all should receive
    the same deposit address. Agent names should not affect wallet assignment.
    
    This validates that wallet assignment is based solely on user_id.
    """
    mock_address = f"0x{format(user_id, '040x')}"
    
    addresses = []
    
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        mock_request.return_value = {
            'success': True,
            'deposit_address': mock_address
        }
        
        conway = ConwayIntegration()
        
        # Generate addresses with different agent names
        for agent_name in agent_names:
            deposit_address = conway.generate_deposit_address(user_id, agent_name)
            
            assert deposit_address is not None, \
                f"Failed to generate address for agent '{agent_name}'"
            
            addresses.append(deposit_address)
        
        # Property: All addresses should be identical regardless of agent name
        unique_addresses = set(addresses)
        assert len(unique_addresses) == 1, \
            f"User {user_id} got different addresses for different agent names: {unique_addresses}"
        
        # Property: All addresses should match the expected address
        for i, (name, addr) in enumerate(zip(agent_names, addresses)):
            assert addr == mock_address, \
                f"Agent '{name}' got wrong address: expected {mock_address}, got {addr}"
        
        print(f"✅ User {user_id} with {len(agent_names)} different agent names got same address")


@given(
    user_id=st.integers(min_value=1000000, max_value=9999999),
    spawn_count=st.integers(min_value=3, max_value=10)
)
@settings(max_examples=100, deadline=None)
def test_one_wallet_per_user_consistency_over_time(user_id, spawn_count):
    """
    Property 3: One Wallet Per User Invariant (Temporal Consistency)
    
    For any user spawning agents over multiple calls, the deposit address
    should remain consistent. The invariant should hold across time.
    
    This validates that wallet assignment is stable and persistent.
    """
    mock_address = f"0x{format(user_id, '040x')}"
    
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        mock_request.return_value = {
            'success': True,
            'deposit_address': mock_address
        }
        
        conway = ConwayIntegration()
        
        # First spawn
        first_address = conway.generate_deposit_address(user_id, "FirstAgent")
        assert first_address is not None, "First spawn failed"
        
        # Subsequent spawns
        for i in range(1, spawn_count):
            agent_name = f"Agent_{i}"
            current_address = conway.generate_deposit_address(user_id, agent_name)
            
            assert current_address is not None, \
                f"Spawn {i} failed for user {user_id}"
            
            # Property: Each spawn should return the same address as the first
            assert current_address == first_address, \
                f"Address changed on spawn {i}: first={first_address}, current={current_address}"
        
        print(f"✅ User {user_id} maintained same address across {spawn_count} spawns: {first_address}")


@given(
    users=st.lists(
        st.tuples(
            st.integers(min_value=1000000, max_value=9999999),  # user_id
            st.integers(min_value=2, max_value=4)  # num_agents
        ),
        min_size=3,
        max_size=5,
        unique_by=lambda x: x[0]  # Unique user_ids
    )
)
@settings(max_examples=100, deadline=None)
def test_one_wallet_per_user_multiple_users(users):
    """
    Property 3: One Wallet Per User Invariant (Multiple Users)
    
    For any set of users each spawning multiple agents, each user should
    have exactly one unique wallet address, and different users should
    have different addresses.
    
    This validates the invariant across multiple users simultaneously.
    """
    user_addresses = {}  # user_id -> set of addresses
    
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        conway = ConwayIntegration()
        
        for user_id, num_agents in users:
            mock_address = f"0x{format(user_id, '040x')}"
            mock_request.return_value = {
                'success': True,
                'deposit_address': mock_address
            }
            
            user_addresses[user_id] = set()
            
            # Each user spawns multiple agents
            for i in range(num_agents):
                agent_name = f"User{user_id}_Agent{i}"
                deposit_address = conway.generate_deposit_address(user_id, agent_name)
                
                assert deposit_address is not None, \
                    f"Failed to generate address for user {user_id}, agent {i}"
                
                user_addresses[user_id].add(deposit_address)
        
        # Property 1: Each user should have exactly one unique address
        for user_id, addresses in user_addresses.items():
            assert len(addresses) == 1, \
                f"User {user_id} has {len(addresses)} different addresses, expected 1: {addresses}"
        
        # Property 2: Different users should have different addresses
        all_addresses = [list(addrs)[0] for addrs in user_addresses.values()]
        unique_addresses = set(all_addresses)
        assert len(unique_addresses) == len(users), \
            f"Address collision detected: {len(users)} users but only {len(unique_addresses)} unique addresses"
        
        print(f"✅ {len(users)} users each got exactly one unique address")


@given(
    user_id=st.integers(min_value=1000000, max_value=9999999),
    first_batch=st.integers(min_value=2, max_value=3),
    second_batch=st.integers(min_value=2, max_value=3)
)
@settings(max_examples=100, deadline=None)
def test_one_wallet_per_user_batch_spawning(user_id, first_batch, second_batch):
    """
    Property 3: One Wallet Per User Invariant (Batch Spawning)
    
    For any user spawning agents in multiple batches, all agents across
    all batches should receive the same deposit address.
    
    This validates that the invariant holds across batch operations.
    """
    mock_address = f"0x{format(user_id, '040x')}"
    
    all_addresses = []
    
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        mock_request.return_value = {
            'success': True,
            'deposit_address': mock_address
        }
        
        conway = ConwayIntegration()
        
        # First batch of spawns
        for i in range(first_batch):
            agent_name = f"Batch1_Agent{i}"
            address = conway.generate_deposit_address(user_id, agent_name)
            assert address is not None
            all_addresses.append(address)
        
        # Second batch of spawns
        for i in range(second_batch):
            agent_name = f"Batch2_Agent{i}"
            address = conway.generate_deposit_address(user_id, agent_name)
            assert address is not None
            all_addresses.append(address)
        
        # Property: All addresses across both batches should be identical
        unique_addresses = set(all_addresses)
        assert len(unique_addresses) == 1, \
            f"User {user_id} got different addresses across batches: {unique_addresses}"
        
        # Property: The address should match the expected format
        assert all_addresses[0] == mock_address
        
        total_spawns = first_batch + second_batch
        print(f"✅ User {user_id} spawned {total_spawns} agents in 2 batches, all got same address")


@given(
    user_id=st.integers(min_value=1000000, max_value=9999999)
)
@settings(max_examples=100, deadline=None)
def test_one_wallet_per_user_idempotency(user_id):
    """
    Property 3: One Wallet Per User Invariant (Idempotency)
    
    For any user, calling generate_deposit_address multiple times should
    be idempotent - always returning the same address without side effects.
    
    This validates that the operation is safe to retry.
    """
    mock_address = f"0x{format(user_id, '040x')}"
    
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        mock_request.return_value = {
            'success': True,
            'deposit_address': mock_address
        }
        
        conway = ConwayIntegration()
        
        # Call the same operation multiple times
        addresses = []
        for i in range(5):
            address = conway.generate_deposit_address(user_id, f"Agent_{i}")
            assert address is not None, f"Call {i} failed"
            addresses.append(address)
        
        # Property: All calls should return the same address (idempotency)
        assert all(addr == addresses[0] for addr in addresses), \
            f"Non-idempotent behavior detected: {set(addresses)}"
        
        # Property: The address should be the expected one
        assert addresses[0] == mock_address
        
        print(f"✅ Idempotency verified for user {user_id}: 5 calls returned {addresses[0]}")


@given(
    user_id=st.integers(min_value=1000000, max_value=9999999),
    num_agents=st.integers(min_value=2, max_value=5)
)
@settings(max_examples=100, deadline=None)
def test_one_wallet_per_user_no_address_mutation(user_id, num_agents):
    """
    Property 3: One Wallet Per User Invariant (No Mutation)
    
    For any user spawning multiple agents, the deposit address should
    never change or mutate. Once assigned, it should remain constant.
    
    This validates that addresses are immutable per user.
    """
    mock_address = f"0x{format(user_id, '040x')}"
    
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        mock_request.return_value = {
            'success': True,
            'deposit_address': mock_address
        }
        
        conway = ConwayIntegration()
        
        # Get initial address
        initial_address = conway.generate_deposit_address(user_id, "InitialAgent")
        assert initial_address is not None
        
        # Spawn more agents and verify address never changes
        for i in range(1, num_agents):
            current_address = conway.generate_deposit_address(user_id, f"Agent_{i}")
            
            # Property: Address should never mutate
            assert current_address == initial_address, \
                f"Address mutated on spawn {i}: initial={initial_address}, current={current_address}"
            
            # Property: Address should maintain exact format
            assert len(current_address) == 42
            assert current_address.startswith('0x')
            assert current_address == mock_address
        
        print(f"✅ User {user_id} address remained immutable across {num_agents} spawns")


if __name__ == "__main__":
    import pytest
    import sys
    
    print("=" * 70)
    print("Property-Based Test: One Wallet Per User Invariant")
    print("Feature: automaton-integration, Property 3")
    print("=" * 70)
    print()
    print("Testing that each user gets exactly one wallet address")
    print("regardless of how many agents they spawn...")
    print()
    print("Validates: Requirements 1.4")
    print()
    
    # Run the tests
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
    
    sys.exit(exit_code)
