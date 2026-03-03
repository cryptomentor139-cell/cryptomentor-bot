"""
Property Test: Error Handling with Retry Logic

Feature: dual-mode-offline-online
Property 12: For any AI agent failure, the system should retry up to 3 times
with exponential backoff, and if all retries fail, display an informative
error message without deducting credits.

Validates: Requirements 12.2, 12.3
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import Mock, patch, MagicMock
import requests
import time

from app.dual_mode.automaton_bridge import AutomatonBridge, AutomatonResponse
from app.dual_mode.credit_manager import CreditManager
from app.dual_mode.online_mode_handler import OnlineModeHandler


@given(
    user_id=st.integers(min_value=1, max_value=999999),
    failure_count=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=10, deadline=None)
def test_retry_logic_with_exponential_backoff(user_id, failure_count):
    """
    Feature: dual-mode-offline-online, Property 12:
    For any AI agent failure, the system should retry up to 3 times
    with exponential backoff, and if all retries fail, display an
    informative error message without deducting credits.
    """
    # Setup
    credit_manager = CreditManager()
    automaton_bridge = AutomatonBridge()
    
    initial_credits = 10000
    credit_manager.add_credits(user_id, initial_credits, "test setup")
    
    # Mock the session.post to simulate failures
    with patch.object(automaton_bridge.session, 'post') as mock_post:
        # Simulate failures followed by success
        if failure_count <= 3:
            # Should succeed after retries
            mock_responses = [Mock(side_effect=requests.exceptions.Timeout())] * failure_count
            mock_responses.append(Mock(
                status_code=200,
                json=lambda: {"response": "success", "credits_used": 1}
            ))
            mock_post.side_effect = mock_responses
        else:
            # Should fail after 3 retries
            mock_post.side_effect = [Mock(side_effect=requests.exceptions.Timeout())] * 5
        
        # Execute
        start_time = time.time()
        result = automaton_bridge.send_message(f"agent_{user_id}", "test message")
        elapsed_time = time.time() - start_time
        
        # Verify retry behavior
        if failure_count <= 3:
            # Should succeed after retries
            assert result.success, f"Expected success after {failure_count} failures"
            assert mock_post.call_count == failure_count + 1, \
                f"Expected {failure_count + 1} calls, got {mock_post.call_count}"
            
            # Verify exponential backoff timing (approximate)
            # Expected wait time: 2^0 + 2^1 + ... + 2^(failure_count-1)
            expected_min_wait = sum(2**i for i in range(failure_count))
            assert elapsed_time >= expected_min_wait * 0.8, \
                f"Expected at least {expected_min_wait}s wait, got {elapsed_time}s"
        
        else:
            # Should fail after 3 retries
            assert not result.success, "Expected failure after max retries"
            assert mock_post.call_count == 3, \
                f"Expected exactly 3 retry attempts, got {mock_post.call_count}"
            assert "timed out" in result.error.lower() or "try again" in result.error.lower(), \
                f"Expected informative error message, got: {result.error}"
            
            # Verify credits not deducted on failure
            final_credits = credit_manager.get_user_credits(user_id)
            assert final_credits == initial_credits, \
                f"Credits should not be deducted on failure. Initial: {initial_credits}, Final: {final_credits}"


@given(
    user_id=st.integers(min_value=1, max_value=999999),
    agent_id=st.text(min_size=5, max_size=50)
)
@settings(max_examples=10, deadline=None)
def test_connection_error_retry_behavior(user_id, agent_id):
    """
    Test that connection errors trigger retry logic
    """
    automaton_bridge = AutomatonBridge()
    
    with patch.object(automaton_bridge.session, 'post') as mock_post:
        # Simulate 2 connection errors, then success
        mock_post.side_effect = [
            Mock(side_effect=requests.exceptions.ConnectionError()),
            Mock(side_effect=requests.exceptions.ConnectionError()),
            Mock(
                status_code=200,
                json=lambda: {"response": "success", "credits_used": 1}
            )
        ]
        
        result = automaton_bridge.send_message(agent_id, "test")
        
        # Should succeed after retries
        assert result.success
        assert mock_post.call_count == 3


@given(
    user_id=st.integers(min_value=1, max_value=999999)
)
@settings(max_examples=10, deadline=None)
def test_http_error_no_retry(user_id):
    """
    Test that HTTP errors (4xx, 5xx) don't trigger retries
    """
    automaton_bridge = AutomatonBridge()
    
    with patch.object(automaton_bridge.session, 'post') as mock_post:
        # Simulate HTTP 500 error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        result = automaton_bridge.send_message(f"agent_{user_id}", "test")
        
        # Should fail immediately without retries
        assert not result.success
        assert mock_post.call_count == 1  # No retries for HTTP errors


@given(
    user_id=st.integers(min_value=1, max_value=999999),
    message=st.text(min_size=1, max_size=500)
)
@settings(max_examples=10, deadline=None)
def test_successful_first_attempt_no_retry(user_id, message):
    """
    Test that successful operations don't trigger retries
    """
    automaton_bridge = AutomatonBridge()
    
    with patch.object(automaton_bridge.session, 'post') as mock_post:
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"response": "success", "credits_used": 1}
        )
        
        result = automaton_bridge.send_message(f"agent_{user_id}", message)
        
        # Should succeed on first attempt
        assert result.success
        assert mock_post.call_count == 1  # No retries needed


def test_retry_with_backoff_generic_operation():
    """
    Test the generic retry_with_backoff method
    """
    automaton_bridge = AutomatonBridge()
    
    # Test successful operation after 2 failures
    call_count = 0
    
    def flaky_operation():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise requests.exceptions.Timeout()
        return "success"
    
    result = automaton_bridge.retry_with_backoff(flaky_operation, max_retries=3)
    
    assert result == "success"
    assert call_count == 3


def test_retry_with_backoff_all_failures():
    """
    Test retry_with_backoff when all attempts fail
    """
    automaton_bridge = AutomatonBridge()
    
    def always_fail():
        raise requests.exceptions.Timeout()
    
    with pytest.raises(requests.exceptions.Timeout):
        automaton_bridge.retry_with_backoff(always_fail, max_retries=3)


def test_retry_with_backoff_non_retryable_error():
    """
    Test that non-retryable errors are not retried
    """
    automaton_bridge = AutomatonBridge()
    
    call_count = 0
    
    def non_retryable_error():
        nonlocal call_count
        call_count += 1
        raise ValueError("Non-retryable error")
    
    with pytest.raises(ValueError):
        automaton_bridge.retry_with_backoff(non_retryable_error, max_retries=3)
    
    # Should fail immediately without retries
    assert call_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
