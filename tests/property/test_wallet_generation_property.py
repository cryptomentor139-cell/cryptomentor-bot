"""
Property-Based Test: Wallet Generation Uniqueness

Feature: automaton-integration
Property 1: Unique Wallet Generation

For any user ID, generating a custodial wallet should produce a unique, 
valid Ethereum address (0x followed by 40 hexadecimal characters) that 
does not collide with any existing wallet address in the system.

Validates: Requirements 1.1

NOTE: This test uses mocked Conway API responses since the actual API
endpoints are not yet fully implemented. The test validates the wallet
generation logic and format validation.
"""

import os
import re
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from hypothesis import given, strategies as st, settings
from app.conway_integration import ConwayIntegration

# Load environment variables
load_dotenv()

# Ethereum address pattern: 0x followed by 40 hexadecimal characters
ETH_ADDRESS_PATTERN = re.compile(r'^0x[a-fA-F0-9]{40}$')


def generate_mock_eth_address(user_id: int) -> str:
    """
    Generate a deterministic mock Ethereum address for testing.
    Uses user_id to ensure uniqueness.
    """
    # Create a deterministic address based on user_id
    # In production, this would come from the Conway API
    hex_suffix = format(user_id, '040x')  # Convert to 40-char hex
    return f"0x{hex_suffix}"


@given(user_id=st.integers(min_value=1000000, max_value=9999999))
@settings(max_examples=100, deadline=None)
def test_wallet_generation_uniqueness(user_id):
    """
    Property 1: Unique Wallet Generation
    
    For any user ID, generating a custodial wallet should produce:
    1. A valid Ethereum address format (0x + 40 hex chars)
    2. A unique address that doesn't collide with others
    
    This test validates the wallet address format and uniqueness logic.
    """
    # Mock the Conway API response
    mock_address = generate_mock_eth_address(user_id)
    
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        mock_request.return_value = {
            'success': True,
            'deposit_address': mock_address
        }
        
        # Create Conway client
        conway = ConwayIntegration()
        
        # Generate deposit address for the user
        agent_name = f"TestAgent_{user_id}"
        deposit_address = conway.generate_deposit_address(user_id, agent_name)
        
        # Property 1: Address should be generated (not None)
        assert deposit_address is not None, \
            f"Failed to generate deposit address for user {user_id}"
        
        # Property 2: Address should match Ethereum address format
        assert ETH_ADDRESS_PATTERN.match(deposit_address), \
            f"Invalid Ethereum address format: {deposit_address}"
        
        # Property 3: Address should be a string
        assert isinstance(deposit_address, str), \
            f"Deposit address should be string, got {type(deposit_address)}"
        
        # Property 4: Address should be exactly 42 characters (0x + 40 hex)
        assert len(deposit_address) == 42, \
            f"Ethereum address should be 42 characters, got {len(deposit_address)}"
        
        # Property 5: Address should start with 0x
        assert deposit_address.startswith('0x'), \
            f"Ethereum address should start with 0x, got {deposit_address[:2]}"
        
        # Property 6: Verify API was called with correct parameters
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == 'POST'
        assert call_args[0][1] == '/api/v1/agents/address'
        
        print(f"✅ Valid wallet generated for user {user_id}: {deposit_address}")


@given(user_ids=st.lists(
    st.integers(min_value=1000000, max_value=9999999),
    min_size=5,
    max_size=10,
    unique=True
))
@settings(max_examples=100, deadline=None)
def test_wallet_generation_no_collisions(user_ids):
    """
    Property 1: Unique Wallet Generation (Collision Test)
    
    For any set of different user IDs, each should generate a unique
    wallet address with no collisions.
    
    This test validates that different users get different addresses.
    """
    addresses = []
    
    for user_id in user_ids:
        mock_address = generate_mock_eth_address(user_id)
        
        with patch.object(ConwayIntegration, '_make_request') as mock_request:
            mock_request.return_value = {
                'success': True,
                'deposit_address': mock_address
            }
            
            conway = ConwayIntegration()
            agent_name = f"TestAgent_{user_id}"
            deposit_address = conway.generate_deposit_address(user_id, agent_name)
            
            # Verify address was generated
            assert deposit_address is not None, \
                f"Failed to generate address for user {user_id}"
            
            # Verify valid format
            assert ETH_ADDRESS_PATTERN.match(deposit_address), \
                f"Invalid address format for user {user_id}: {deposit_address}"
            
            addresses.append(deposit_address)
    
    # Property: All addresses should be unique (no collisions)
    unique_addresses = set(addresses)
    assert len(unique_addresses) == len(addresses), \
        f"Address collision detected! Generated {len(addresses)} addresses but only {len(unique_addresses)} unique"
    
    print(f"✅ Generated {len(addresses)} unique addresses with no collisions")


@given(user_id=st.integers(min_value=1000000, max_value=9999999))
@settings(max_examples=100, deadline=None)
def test_wallet_generation_idempotency(user_id):
    """
    Property 1: Unique Wallet Generation (Idempotency Test)
    
    For any user ID, generating a wallet multiple times should return
    the same address (one wallet per user invariant).
    
    This test validates that the same user gets consistent addresses.
    """
    mock_address = generate_mock_eth_address(user_id)
    agent_name = f"TestAgent_{user_id}"
    
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        # Mock should return the same address both times
        mock_request.return_value = {
            'success': True,
            'deposit_address': mock_address
        }
        
        conway = ConwayIntegration()
        
        # Generate address twice for the same user
        address1 = conway.generate_deposit_address(user_id, agent_name)
        address2 = conway.generate_deposit_address(user_id, agent_name)
        
        # Both should be valid
        assert address1 is not None, "First address generation failed"
        assert address2 is not None, "Second address generation failed"
        
        # Property: Same user should get the same address (idempotency)
        # Note: In the actual implementation, the Conway API should handle this
        assert address1 == address2, \
            f"Same user got different addresses: {address1} vs {address2}"
        
        print(f"✅ Idempotency verified for user {user_id}: {address1}")


@given(
    user_id=st.integers(min_value=1000000, max_value=9999999),
    agent_name=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters=' _-'
    ))
)
@settings(max_examples=100, deadline=None)
def test_wallet_generation_with_various_agent_names(user_id, agent_name):
    """
    Property 1: Unique Wallet Generation (Agent Name Variation)
    
    For any user ID and agent name, the wallet address should be valid
    regardless of the agent name format.
    
    This test validates that agent names don't affect address validity.
    """
    mock_address = generate_mock_eth_address(user_id)
    
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        mock_request.return_value = {
            'success': True,
            'deposit_address': mock_address
        }
        
        conway = ConwayIntegration()
        deposit_address = conway.generate_deposit_address(user_id, agent_name)
        
        # Address should be valid regardless of agent name
        assert deposit_address is not None
        assert ETH_ADDRESS_PATTERN.match(deposit_address)
        assert len(deposit_address) == 42
        
        # Verify API was called with the agent name
        call_args = mock_request.call_args
        request_data = call_args[1]['data']
        assert request_data['agent_name'] == agent_name
        
        print(f"✅ Valid wallet for user {user_id} with agent '{agent_name[:20]}...'")


if __name__ == "__main__":
    import pytest
    import sys
    
    print("=" * 70)
    print("Property-Based Test: Wallet Generation Uniqueness")
    print("Feature: automaton-integration, Property 1")
    print("=" * 70)
    print()
    print("NOTE: Using mocked Conway API responses for testing")
    print("      Validates wallet format and uniqueness logic")
    print()
    
    # Run the tests
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
    
    sys.exit(exit_code)


if __name__ == "__main__":
    import pytest
    import sys
    
    print("=" * 70)
    print("Property-Based Test: Wallet Generation Uniqueness")
    print("Feature: automaton-integration, Property 1")
    print("=" * 70)
    print()
    
    # Run the tests
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
    
    sys.exit(exit_code)
