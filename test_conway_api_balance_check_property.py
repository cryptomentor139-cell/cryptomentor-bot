"""
Property-Based Test: Conway API Balance Check

Feature: automaton-integration
Property 34: Conway API Balance Check

For any agent balance query, the Conway Cloud API /credits/balance endpoint 
should be called with the agent_wallet as a query parameter.

Validates: Requirements 13.2

This test validates that:
1. Balance check calls the correct endpoint
2. Agent wallet is passed as query parameter
3. Response contains balance field
4. Balance is a valid numeric value
5. API authentication is included in request
"""

import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from hypothesis import given, strategies as st, settings
from app.conway_integration import ConwayIntegration

# Load environment variables
load_dotenv()

# Ethereum address pattern for agent wallets
eth_address_strategy = st.builds(
    lambda hex_str: f"0x{hex_str}",
    st.text(alphabet='0123456789abcdef', min_size=40, max_size=40)
)

# Balance strategy (0 to 1 million credits)
balance_strategy = st.floats(min_value=0.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)


@given(
    agent_wallet=eth_address_strategy,
    balance=balance_strategy
)
@settings(max_examples=100, deadline=None)
def test_balance_check_endpoint_called(agent_wallet, balance):
    """
    Property 34: Conway API Balance Check (Endpoint)
    
    For any agent wallet address, checking the balance should call
    the GET /api/v1/agents/balance endpoint with the wallet address
    as a query parameter.
    
    This validates the correct API endpoint is used.
    """
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        # Mock successful balance response
        mock_request.return_value = {
            'success': True,
            'balance': balance
        }
        
        # Create Conway client
        conway = ConwayIntegration()
        
        # Get balance
        result = conway.get_credit_balance(agent_wallet)
        
        # Property 1: API should be called exactly once
        assert mock_request.call_count == 1, \
            f"Expected 1 API call, got {mock_request.call_count}"
        
        # Property 2: Should use GET method
        call_args = mock_request.call_args
        assert call_args[0][0] == 'GET', \
            f"Expected GET method, got {call_args[0][0]}"
        
        # Property 3: Should call /api/v1/agents/balance endpoint
        assert call_args[0][1] == '/api/v1/agents/balance', \
            f"Expected /api/v1/agents/balance endpoint, got {call_args[0][1]}"
        
        # Property 4: Should pass agent_wallet as query parameter
        params = call_args[1].get('params', {})
        assert 'address' in params, \
            "Query parameters should include 'address'"
        assert params['address'] == agent_wallet, \
            f"Expected address={agent_wallet}, got {params['address']}"
        
        # Property 5: Result should match mocked balance
        assert result == balance, \
            f"Expected balance {balance}, got {result}"
        
        print(f"✅ Balance check for {agent_wallet[:10]}...: {balance:.2f} credits")


@given(agent_wallet=eth_address_strategy)
@settings(max_examples=100, deadline=None)
def test_balance_check_authentication(agent_wallet):
    """
    Property 34: Conway API Balance Check (Authentication)
    
    For any balance check request, the Authorization header should
    contain the Bearer token with the Conway API key.
    
    This validates that authentication is properly included.
    """
    with patch('requests.request') as mock_request:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'balance': 1000.0
        }
        mock_request.return_value = mock_response
        
        # Create Conway client
        conway = ConwayIntegration()
        
        # Get balance
        conway.get_credit_balance(agent_wallet)
        
        # Property: Authorization header should be present
        call_kwargs = mock_request.call_args[1]
        headers = call_kwargs.get('headers', {})
        
        assert 'Authorization' in headers, \
            "Authorization header should be present"
        
        # Property: Should use Bearer token format
        auth_header = headers['Authorization']
        assert auth_header.startswith('Bearer '), \
            f"Authorization should start with 'Bearer ', got {auth_header}"
        
        # Property: Should include API key
        api_key = os.getenv('CONWAY_API_KEY')
        if api_key:
            assert api_key in auth_header, \
                "Authorization header should include API key"
        
        print(f"✅ Authentication verified for balance check: {agent_wallet[:10]}...")


@given(
    agent_wallet=eth_address_strategy,
    balance=balance_strategy
)
@settings(max_examples=100, deadline=None)
def test_balance_check_response_format(agent_wallet, balance):
    """
    Property 34: Conway API Balance Check (Response Format)
    
    For any balance check, the response should contain a 'balance'
    field with a valid numeric value.
    
    This validates the response format is correct.
    """
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        # Mock response with balance
        mock_request.return_value = {
            'success': True,
            'balance': balance
        }
        
        conway = ConwayIntegration()
        result = conway.get_credit_balance(agent_wallet)
        
        # Property 1: Result should not be None
        assert result is not None, \
            "Balance check should return a value"
        
        # Property 2: Result should be numeric
        assert isinstance(result, (int, float)), \
            f"Balance should be numeric, got {type(result)}"
        
        # Property 3: Result should be non-negative
        assert result >= 0, \
            f"Balance should be non-negative, got {result}"
        
        # Property 4: Result should match mocked balance
        assert abs(result - balance) < 0.01, \
            f"Expected balance {balance}, got {result}"
        
        print(f"✅ Valid balance format: {result:.2f} credits")


@given(agent_wallet=eth_address_strategy)
@settings(max_examples=100, deadline=None)
def test_balance_check_error_handling(agent_wallet):
    """
    Property 34: Conway API Balance Check (Error Handling)
    
    For any balance check that fails, the function should return None
    and handle the error gracefully.
    
    This validates error handling behavior.
    """
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        # Mock API failure
        mock_request.side_effect = Exception("API connection failed")
        
        conway = ConwayIntegration()
        result = conway.get_credit_balance(agent_wallet)
        
        # Property: Should return None on error
        assert result is None, \
            f"Expected None on error, got {result}"
        
        print(f"✅ Error handled gracefully for {agent_wallet[:10]}...")


@given(
    agent_wallet=eth_address_strategy,
    balances=st.lists(
        st.floats(min_value=0.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=5
    )
)
@settings(max_examples=100, deadline=None)
def test_balance_check_multiple_calls(agent_wallet, balances):
    """
    Property 34: Conway API Balance Check (Multiple Calls)
    
    For any agent wallet, multiple balance checks should each call
    the API independently and return the current balance.
    
    This validates that balance checks are not cached incorrectly.
    """
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        conway = ConwayIntegration()
        
        results = []
        for balance in balances:
            # Mock different balance for each call
            mock_request.return_value = {
                'success': True,
                'balance': balance
            }
            
            result = conway.get_credit_balance(agent_wallet)
            results.append(result)
        
        # Property 1: Should make one API call per balance check
        assert mock_request.call_count == len(balances), \
            f"Expected {len(balances)} API calls, got {mock_request.call_count}"
        
        # Property 2: Each result should match the corresponding balance
        for i, (expected, actual) in enumerate(zip(balances, results)):
            assert abs(actual - expected) < 0.01, \
                f"Call {i+1}: expected {expected}, got {actual}"
        
        print(f"✅ {len(balances)} balance checks completed for {agent_wallet[:10]}...")


@given(
    agent_wallet=eth_address_strategy,
    balance=balance_strategy
)
@settings(max_examples=100, deadline=None)
def test_balance_check_query_parameter_format(agent_wallet, balance):
    """
    Property 34: Conway API Balance Check (Query Parameter Format)
    
    For any balance check, the agent wallet should be passed as a
    query parameter named 'address' (not in the request body).
    
    This validates the correct parameter passing method.
    """
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        mock_request.return_value = {
            'success': True,
            'balance': balance
        }
        
        conway = ConwayIntegration()
        conway.get_credit_balance(agent_wallet)
        
        call_args = mock_request.call_args
        
        # Property 1: Should use params (query parameters), not data (body)
        params = call_args[1].get('params')
        data = call_args[1].get('data')
        
        assert params is not None, \
            "Query parameters should be used for GET request"
        
        assert data is None, \
            "Request body should not be used for GET request"
        
        # Property 2: Params should contain 'address' key
        assert 'address' in params, \
            "Query parameters should include 'address'"
        
        # Property 3: Address value should match agent wallet
        assert params['address'] == agent_wallet, \
            f"Expected address={agent_wallet}, got {params['address']}"
        
        print(f"✅ Query parameter format correct for {agent_wallet[:10]}...")


@given(agent_wallet=eth_address_strategy)
@settings(max_examples=100, deadline=None)
def test_balance_check_missing_balance_field(agent_wallet):
    """
    Property 34: Conway API Balance Check (Missing Balance Field)
    
    For any balance check where the response doesn't contain a
    'balance' field, the function should return None.
    
    This validates handling of malformed responses.
    """
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        # Mock response without balance field
        mock_request.return_value = {
            'success': True
            # Missing 'balance' field
        }
        
        conway = ConwayIntegration()
        result = conway.get_credit_balance(agent_wallet)
        
        # Property: Should return None when balance field is missing
        assert result is None, \
            f"Expected None for missing balance field, got {result}"
        
        print(f"✅ Missing balance field handled for {agent_wallet[:10]}...")


@given(
    agent_wallet=eth_address_strategy,
    balance=st.floats(min_value=-1000.0, max_value=-0.01, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_balance_check_negative_balance(agent_wallet, balance):
    """
    Property 34: Conway API Balance Check (Negative Balance)
    
    For any balance check that returns a negative balance (which
    shouldn't happen in production), the function should still
    return the value as-is for debugging purposes.
    
    This validates that the function doesn't silently modify values.
    """
    with patch.object(ConwayIntegration, '_make_request') as mock_request:
        mock_request.return_value = {
            'success': True,
            'balance': balance
        }
        
        conway = ConwayIntegration()
        result = conway.get_credit_balance(agent_wallet)
        
        # Property: Should return the actual value (even if negative)
        assert result == balance, \
            f"Expected {balance}, got {result}"
        
        # Property: Should be numeric
        assert isinstance(result, (int, float)), \
            f"Result should be numeric, got {type(result)}"
        
        print(f"✅ Negative balance handled: {result:.2f} credits")


def main():
    """Run the property-based tests"""
    import pytest
    import sys
    
    print("=" * 70)
    print("Property-Based Test: Conway API Balance Check")
    print("Feature: automaton-integration, Property 34")
    print("=" * 70)
    print()
    print("Testing Conway API balance check endpoint...")
    print("Validates: Requirements 13.2")
    print()
    print("Properties tested:")
    print("  1. Correct endpoint called (GET /api/v1/agents/balance)")
    print("  2. Agent wallet passed as query parameter")
    print("  3. Authentication header included")
    print("  4. Response format validated")
    print("  5. Error handling verified")
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
    main()
