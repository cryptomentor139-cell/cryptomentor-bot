"""
Property-Based Test: Conway API Credit Transfer

Feature: automaton-integration
Property 33: Conway API Credit Transfer

For any agent funding operation, the Conway Cloud API /credits/transfer endpoint 
should be called with the correct agent_wallet and credit amount in the request body.

Validates: Requirements 13.1

This test validates that:
1. The fund_agent method calls the correct API endpoint (/credits/transfer)
2. The request body contains the agent_wallet parameter
3. The request body contains the amount parameter
4. The Authorization header is correctly set
5. The method handles various credit amounts correctly
"""

from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch, call
import requests
from app.conway_integration import ConwayIntegration


# Strategy for generating valid Ethereum addresses
def ethereum_address_strategy():
    """Generate valid Ethereum addresses (0x + 40 hex chars)"""
    return st.text(
        alphabet='0123456789abcdef',
        min_size=40,
        max_size=40
    ).map(lambda x: f"0x{x}")


@given(
    agent_wallet=ethereum_address_strategy(),
    credit_amount=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_conway_api_credit_transfer_endpoint(agent_wallet, credit_amount):
    """
    **Validates: Requirements 13.1**
    
    Property 33: Conway API Credit Transfer
    
    For any agent funding operation with a valid wallet address and credit amount,
    the Conway Cloud API /credits/transfer endpoint should be called with the
    correct agent_wallet and amount in the request body.
    
    This validates the core API integration for funding agents.
    """
    # Mock the requests.request method
    with patch('requests.request') as mock_request:
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'new_balance': credit_amount + 1000,
            'message': 'Credits transferred successfully'
        }
        mock_request.return_value = mock_response
        
        # Create Conway client with mocked API key
        with patch.dict('os.environ', {'CONWAY_API_KEY': 'test_api_key_12345'}):
            client = ConwayIntegration()
            
            # Call fund_agent
            result = client.fund_agent(agent_wallet, credit_amount)
            
            # Property 1: The method should call requests.request
            assert mock_request.called, "requests.request should be called"
            
            # Property 2: The endpoint should be /credits/transfer
            call_args = mock_request.call_args
            url = call_args.kwargs.get('url') or call_args[1].get('url')
            assert '/credits/transfer' in url, \
                f"Endpoint should be /credits/transfer, got {url}"
            
            # Property 3: The request body should contain agent_wallet
            request_data = call_args.kwargs.get('json') or call_args[1].get('json')
            assert request_data is not None, "Request should have JSON body"
            assert 'agent_wallet' in request_data, \
                f"Request body should contain 'agent_wallet', got {request_data.keys()}"
            assert request_data['agent_wallet'] == agent_wallet, \
                f"agent_wallet should be {agent_wallet}, got {request_data['agent_wallet']}"
            
            # Property 4: The request body should contain amount
            assert 'amount' in request_data, \
                f"Request body should contain 'amount', got {request_data.keys()}"
            assert abs(request_data['amount'] - credit_amount) < 0.01, \
                f"amount should be {credit_amount}, got {request_data['amount']}"
            
            # Property 5: The Authorization header should be set
            headers = call_args.kwargs.get('headers') or call_args[1].get('headers')
            assert headers is not None, "Request should have headers"
            assert 'Authorization' in headers, \
                f"Headers should contain 'Authorization', got {headers.keys()}"
            assert headers['Authorization'].startswith('Bearer '), \
                f"Authorization should start with 'Bearer ', got {headers['Authorization']}"
            
            # Property 6: The method should use POST
            method = call_args.kwargs.get('method') or call_args[0][0]
            assert method == 'POST', \
                f"HTTP method should be POST, got {method}"
            
            # Property 7: The result should indicate success
            assert result['success'] is True, \
                f"Result should indicate success, got {result}"
            
            print(f"✅ API call validated: {agent_wallet} funded with {credit_amount:.2f} credits")


@given(
    agent_wallet=ethereum_address_strategy(),
    credit_amount=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_conway_api_credit_transfer_request_structure(agent_wallet, credit_amount):
    """
    **Validates: Requirements 13.1**
    
    Property 33: Conway API Credit Transfer (Request Structure)
    
    For any agent funding operation, the request to /credits/transfer should
    have the correct structure with exactly two parameters: agent_wallet and amount.
    
    This validates the API contract is correctly implemented.
    """
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'new_balance': credit_amount,
            'message': 'Success'
        }
        mock_request.return_value = mock_response
        
        with patch.dict('os.environ', {'CONWAY_API_KEY': 'test_key'}):
            client = ConwayIntegration()
            client.fund_agent(agent_wallet, credit_amount)
            
            # Get the request data
            call_args = mock_request.call_args
            request_data = call_args.kwargs.get('json') or call_args[1].get('json')
            
            # Property 1: Request should have exactly 2 keys
            assert len(request_data) == 2, \
                f"Request should have exactly 2 keys, got {len(request_data)}: {request_data.keys()}"
            
            # Property 2: Keys should be agent_wallet and amount
            expected_keys = {'agent_wallet', 'amount'}
            actual_keys = set(request_data.keys())
            assert actual_keys == expected_keys, \
                f"Request keys should be {expected_keys}, got {actual_keys}"
            
            # Property 3: agent_wallet should be a string
            assert isinstance(request_data['agent_wallet'], str), \
                f"agent_wallet should be string, got {type(request_data['agent_wallet'])}"
            
            # Property 4: amount should be numeric
            assert isinstance(request_data['amount'], (int, float)), \
                f"amount should be numeric, got {type(request_data['amount'])}"
            
            # Property 5: amount should be positive
            assert request_data['amount'] > 0, \
                f"amount should be positive, got {request_data['amount']}"
            
            print(f"✅ Request structure validated: {request_data}")


@given(
    agent_wallet=ethereum_address_strategy(),
    amounts=st.lists(
        st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=5
    )
)
@settings(max_examples=100, deadline=None)
def test_conway_api_credit_transfer_multiple_calls(agent_wallet, amounts):
    """
    **Validates: Requirements 13.1**
    
    Property 33: Conway API Credit Transfer (Multiple Calls)
    
    For any sequence of funding operations to the same agent, each call
    should independently call the /credits/transfer endpoint with the
    correct parameters.
    
    This validates that multiple funding operations work correctly.
    """
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'new_balance': 10000,
            'message': 'Success'
        }
        mock_request.return_value = mock_response
        
        with patch.dict('os.environ', {'CONWAY_API_KEY': 'test_key'}):
            client = ConwayIntegration()
            
            # Make multiple funding calls
            for amount in amounts:
                result = client.fund_agent(agent_wallet, amount)
                assert result['success'] is True
            
            # Property 1: Should have called the API once per amount
            assert mock_request.call_count == len(amounts), \
                f"Should have called API {len(amounts)} times, got {mock_request.call_count}"
            
            # Property 2: Each call should have the correct agent_wallet
            for call_obj in mock_request.call_args_list:
                request_data = call_obj.kwargs.get('json') or call_obj[1].get('json')
                assert request_data['agent_wallet'] == agent_wallet, \
                    f"Each call should use same agent_wallet {agent_wallet}"
            
            # Property 3: Each call should have the correct amount
            for i, call_obj in enumerate(mock_request.call_args_list):
                request_data = call_obj.kwargs.get('json') or call_obj[1].get('json')
                expected_amount = amounts[i]
                assert abs(request_data['amount'] - expected_amount) < 0.01, \
                    f"Call {i} should have amount {expected_amount}, got {request_data['amount']}"
            
            print(f"✅ Multiple calls validated: {len(amounts)} funding operations to {agent_wallet}")


@given(
    agent_wallet=ethereum_address_strategy(),
    credit_amount=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_conway_api_credit_transfer_authentication(agent_wallet, credit_amount):
    """
    **Validates: Requirements 13.1, 13.3**
    
    Property 33: Conway API Credit Transfer (Authentication)
    
    For any agent funding operation, the request should include proper
    authentication via the Authorization header with Bearer token.
    
    This validates that API authentication is correctly implemented.
    """
    test_api_key = 'test_secret_key_abc123'
    
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'new_balance': 1000}
        mock_request.return_value = mock_response
        
        with patch.dict('os.environ', {'CONWAY_API_KEY': test_api_key}):
            client = ConwayIntegration()
            client.fund_agent(agent_wallet, credit_amount)
            
            # Get the headers
            call_args = mock_request.call_args
            headers = call_args.kwargs.get('headers') or call_args[1].get('headers')
            
            # Property 1: Authorization header should exist
            assert 'Authorization' in headers, \
                "Authorization header should be present"
            
            # Property 2: Authorization should use Bearer scheme
            auth_header = headers['Authorization']
            assert auth_header.startswith('Bearer '), \
                f"Authorization should start with 'Bearer ', got {auth_header}"
            
            # Property 3: Authorization should contain the API key
            assert test_api_key in auth_header, \
                f"Authorization should contain API key {test_api_key}"
            
            # Property 4: Authorization format should be "Bearer <key>"
            expected_auth = f"Bearer {test_api_key}"
            assert auth_header == expected_auth, \
                f"Authorization should be '{expected_auth}', got '{auth_header}'"
            
            print(f"✅ Authentication validated: Bearer token present")


@given(
    agent_wallet=ethereum_address_strategy(),
    credit_amount=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_conway_api_credit_transfer_content_type(agent_wallet, credit_amount):
    """
    **Validates: Requirements 13.1**
    
    Property 33: Conway API Credit Transfer (Content Type)
    
    For any agent funding operation, the request should have Content-Type
    set to application/json since we're sending JSON data.
    
    This validates proper HTTP headers for JSON API communication.
    """
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'new_balance': 1000}
        mock_request.return_value = mock_response
        
        with patch.dict('os.environ', {'CONWAY_API_KEY': 'test_key'}):
            client = ConwayIntegration()
            client.fund_agent(agent_wallet, credit_amount)
            
            # Get the headers
            call_args = mock_request.call_args
            headers = call_args.kwargs.get('headers') or call_args[1].get('headers')
            
            # Property 1: Content-Type header should exist
            assert 'Content-Type' in headers, \
                "Content-Type header should be present"
            
            # Property 2: Content-Type should be application/json
            content_type = headers['Content-Type']
            assert content_type == 'application/json', \
                f"Content-Type should be 'application/json', got '{content_type}'"
            
            print(f"✅ Content-Type validated: application/json")


@given(
    agent_wallet=ethereum_address_strategy(),
    credit_amount=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_conway_api_credit_transfer_url_construction(agent_wallet, credit_amount):
    """
    **Validates: Requirements 13.1**
    
    Property 33: Conway API Credit Transfer (URL Construction)
    
    For any agent funding operation, the full URL should be correctly
    constructed as {base_url}/credits/transfer.
    
    This validates proper URL construction for the API endpoint.
    """
    test_base_url = 'https://api.conway.tech'
    
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'new_balance': 1000}
        mock_request.return_value = mock_response
        
        with patch.dict('os.environ', {
            'CONWAY_API_KEY': 'test_key',
            'CONWAY_API_URL': test_base_url
        }):
            client = ConwayIntegration()
            client.fund_agent(agent_wallet, credit_amount)
            
            # Get the URL
            call_args = mock_request.call_args
            url = call_args.kwargs.get('url') or call_args[1].get('url')
            
            # Property 1: URL should start with base URL
            assert url.startswith(test_base_url), \
                f"URL should start with {test_base_url}, got {url}"
            
            # Property 2: URL should end with /credits/transfer
            assert url.endswith('/credits/transfer'), \
                f"URL should end with /credits/transfer, got {url}"
            
            # Property 3: URL should be exactly base_url + /credits/transfer
            expected_url = f"{test_base_url}/credits/transfer"
            assert url == expected_url, \
                f"URL should be {expected_url}, got {url}"
            
            print(f"✅ URL construction validated: {url}")


@given(
    agent_wallet=ethereum_address_strategy(),
    credit_amount=st.floats(min_value=1.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_conway_api_credit_transfer_timeout(agent_wallet, credit_amount):
    """
    **Validates: Requirements 13.1**
    
    Property 33: Conway API Credit Transfer (Timeout)
    
    For any agent funding operation, the request should have a reasonable
    timeout configured to prevent hanging indefinitely.
    
    This validates proper timeout handling for API requests.
    """
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'new_balance': 1000}
        mock_request.return_value = mock_response
        
        with patch.dict('os.environ', {'CONWAY_API_KEY': 'test_key'}):
            client = ConwayIntegration()
            client.fund_agent(agent_wallet, credit_amount)
            
            # Get the timeout parameter
            call_args = mock_request.call_args
            timeout = call_args.kwargs.get('timeout')
            
            # Property 1: Timeout should be set
            assert timeout is not None, \
                "Timeout should be configured"
            
            # Property 2: Timeout should be reasonable (between 5 and 60 seconds)
            assert 5 <= timeout <= 60, \
                f"Timeout should be between 5 and 60 seconds, got {timeout}"
            
            # Property 3: Timeout should be numeric
            assert isinstance(timeout, (int, float)), \
                f"Timeout should be numeric, got {type(timeout)}"
            
            print(f"✅ Timeout validated: {timeout} seconds")


if __name__ == "__main__":
    import pytest
    import sys
    
    print("=" * 70)
    print("Property-Based Test: Conway API Credit Transfer")
    print("Feature: automaton-integration, Property 33")
    print("=" * 70)
    print()
    print("Testing the Conway Cloud API /credits/transfer endpoint:")
    print("  - Correct endpoint path")
    print("  - Correct request body structure (agent_wallet, amount)")
    print("  - Proper authentication (Bearer token)")
    print("  - Correct HTTP method (POST)")
    print("  - Proper headers (Content-Type, Authorization)")
    print()
    print("Validates: Requirements 13.1")
    print()
    
    # Run the tests
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
    
    sys.exit(exit_code)
