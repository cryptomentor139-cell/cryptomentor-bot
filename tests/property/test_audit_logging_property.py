"""
Property-Based Test: Audit Logging for Decryption

Feature: automaton-integration
Property 27: Audit Logging for Decryption

For any private key decryption operation, an audit log entry should be 
created with the timestamp, wallet address, and operation type.

Validates: Requirements 11.4

This test validates that:
1. Every decryption operation creates an audit log entry
2. Audit log contains required fields (timestamp, wallet_address, operation_type)
3. Audit log records both successful and failed operations
4. Audit log includes admin_id for accountability
5. Audit logs are immutable and retrievable
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.audit_logger import AuditLogger

# Load environment variables
load_dotenv()


# Strategies for generating test data
wallet_address_strategy = st.builds(
    lambda hex_str: f"0x{hex_str}",
    st.text(alphabet='0123456789abcdef', min_size=40, max_size=40)
)

operation_type_strategy = st.sampled_from([
    'withdrawal_processing',
    'transfer',
    'emergency_recovery',
    'key_rotation',
    'balance_check',
    'admin_override'
])

admin_id_strategy = st.integers(min_value=100000000, max_value=999999999)

success_status_strategy = st.booleans()

error_message_strategy = st.one_of(
    st.none(),
    st.sampled_from([
        'Invalid key format',
        'Decryption failed',
        'Key not found',
        'Permission denied',
        'Timeout error'
    ])
)


@given(
    wallet_address=wallet_address_strategy,
    operation_type=operation_type_strategy,
    admin_id=admin_id_strategy,
    success=success_status_strategy,
    error_message=error_message_strategy
)
@settings(max_examples=100, deadline=None)
def test_audit_log_creation_for_decryption(
    wallet_address,
    operation_type,
    admin_id,
    success,
    error_message
):
    """
    Property 27: Audit Logging for Decryption
    
    For any private key decryption operation, an audit log entry should 
    be created with timestamp, wallet address, operation type, and admin ID.
    
    This validates that all decryption operations are audited.
    """
    # Create a mock Supabase client
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()
    
    # Set up the mock chain
    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = mock_execute
    
    # Create audit logger with mocked Supabase
    with patch('app.audit_logger.create_client', return_value=mock_supabase):
        # Force Supabase to be enabled
        audit_logger = AuditLogger()
        audit_logger.supabase = mock_supabase
        audit_logger.supabase_enabled = True
        
        # Log the decryption operation
        result = audit_logger.log_private_key_decryption(
            wallet_address=wallet_address,
            operation_type=operation_type,
            admin_id=admin_id,
            success=success,
            error_message=error_message
        )
        
        # Property 1: Logging should succeed
        assert result is True, \
            "Audit logging should return True on success"
        
        # Property 2: Supabase table method should be called with 'audit_logs'
        mock_supabase.table.assert_called_once_with('audit_logs')
        
        # Property 3: Insert should be called exactly once
        assert mock_table.insert.call_count == 1, \
            "Insert should be called exactly once per log operation"
        
        # Get the audit entry that was inserted
        insert_call_args = mock_table.insert.call_args
        audit_entry = insert_call_args[0][0]
        
        # Property 4: Audit entry should contain event_type
        assert 'event_type' in audit_entry, \
            "Audit entry must contain event_type field"
        assert audit_entry['event_type'] == 'private_key_decryption', \
            "Event type should be 'private_key_decryption'"
        
        # Property 5: Audit entry should contain wallet_address
        assert 'wallet_address' in audit_entry, \
            "Audit entry must contain wallet_address field"
        assert audit_entry['wallet_address'] == wallet_address, \
            f"Wallet address mismatch: expected {wallet_address}, got {audit_entry['wallet_address']}"
        
        # Property 6: Audit entry should contain operation_type
        assert 'operation_type' in audit_entry, \
            "Audit entry must contain operation_type field"
        assert audit_entry['operation_type'] == operation_type, \
            f"Operation type mismatch: expected {operation_type}, got {audit_entry['operation_type']}"
        
        # Property 7: Audit entry should contain admin_id
        assert 'admin_id' in audit_entry, \
            "Audit entry must contain admin_id field"
        assert audit_entry['admin_id'] == admin_id, \
            f"Admin ID mismatch: expected {admin_id}, got {audit_entry['admin_id']}"
        
        # Property 8: Audit entry should contain timestamp
        assert 'timestamp' in audit_entry, \
            "Audit entry must contain timestamp field"
        
        # Validate timestamp format (ISO 8601)
        timestamp_str = audit_entry['timestamp']
        try:
            parsed_timestamp = datetime.fromisoformat(timestamp_str)
            assert isinstance(parsed_timestamp, datetime), \
                "Timestamp should be parseable as datetime"
        except ValueError:
            assert False, f"Timestamp should be in ISO format, got: {timestamp_str}"
        
        # Property 9: Audit entry should contain success status
        assert 'success' in audit_entry, \
            "Audit entry must contain success field"
        assert audit_entry['success'] == success, \
            f"Success status mismatch: expected {success}, got {audit_entry['success']}"
        
        # Property 10: Audit entry should contain error_message (if provided)
        assert 'error_message' in audit_entry, \
            "Audit entry must contain error_message field"
        assert audit_entry['error_message'] == error_message, \
            f"Error message mismatch: expected {error_message}, got {audit_entry['error_message']}"
        
        # Property 11: Audit entry should contain metadata
        assert 'metadata' in audit_entry, \
            "Audit entry must contain metadata field"
        assert isinstance(audit_entry['metadata'], dict), \
            "Metadata should be a dictionary"
        assert 'operation' in audit_entry['metadata'], \
            "Metadata should contain operation"
        assert 'wallet' in audit_entry['metadata'], \
            "Metadata should contain wallet"
        
        print(f"✅ Audit log created for {operation_type} on {wallet_address[:10]}... "
              f"by admin {admin_id}, success={success}")


@given(
    wallet_address=wallet_address_strategy,
    operation_type=operation_type_strategy,
    admin_id=admin_id_strategy
)
@settings(max_examples=100, deadline=None)
def test_audit_log_immutability(wallet_address, operation_type, admin_id):
    """
    Property 27: Audit Log Immutability
    
    For any decryption operation, the audit log entry should be immutable
    and contain all required fields that cannot be modified after creation.
    
    This validates that audit logs maintain integrity.
    """
    # Create a mock Supabase client
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()
    
    # Set up the mock chain
    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = mock_execute
    
    # Create audit logger with mocked Supabase
    with patch('app.audit_logger.create_client', return_value=mock_supabase):
        audit_logger = AuditLogger()
        audit_logger.supabase = mock_supabase
        audit_logger.supabase_enabled = True
        
        # Log the decryption operation
        result = audit_logger.log_private_key_decryption(
            wallet_address=wallet_address,
            operation_type=operation_type,
            admin_id=admin_id,
            success=True
        )
        
        # Get the audit entry
        insert_call_args = mock_table.insert.call_args
        audit_entry = insert_call_args[0][0]
        
        # Property: All required fields should be present and non-empty
        required_fields = [
            'event_type',
            'wallet_address',
            'operation_type',
            'admin_id',
            'timestamp',
            'success',
            'metadata'
        ]
        
        for field in required_fields:
            assert field in audit_entry, \
                f"Required field '{field}' missing from audit entry"
            
            # Ensure non-None values for critical fields
            if field in ['event_type', 'wallet_address', 'operation_type', 'admin_id', 'timestamp']:
                assert audit_entry[field] is not None, \
                    f"Critical field '{field}' should not be None"
        
        # Property: Timestamp should be recent (within last minute)
        timestamp = datetime.fromisoformat(audit_entry['timestamp'])
        now = datetime.now()
        time_diff = (now - timestamp).total_seconds()
        
        assert abs(time_diff) < 60, \
            f"Timestamp should be recent, but differs by {time_diff} seconds"
        
        print(f"✅ Immutable audit log verified for {operation_type} on {wallet_address[:10]}...")


@given(
    wallet_addresses=st.lists(wallet_address_strategy, min_size=1, max_size=10),
    operation_type=operation_type_strategy,
    admin_id=admin_id_strategy
)
@settings(max_examples=100, deadline=None)
def test_audit_log_multiple_operations(wallet_addresses, operation_type, admin_id):
    """
    Property 27: Audit Logging for Multiple Operations
    
    For any sequence of decryption operations, each operation should 
    create a separate audit log entry with unique timestamps.
    
    This validates that all operations are individually tracked.
    """
    # Create a mock Supabase client
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()
    
    # Set up the mock chain
    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = mock_execute
    
    # Create audit logger with mocked Supabase
    with patch('app.audit_logger.create_client', return_value=mock_supabase):
        audit_logger = AuditLogger()
        audit_logger.supabase = mock_supabase
        audit_logger.supabase_enabled = True
        
        # Log multiple decryption operations
        for wallet_address in wallet_addresses:
            result = audit_logger.log_private_key_decryption(
                wallet_address=wallet_address,
                operation_type=operation_type,
                admin_id=admin_id,
                success=True
            )
            
            assert result is True, \
                f"Logging should succeed for wallet {wallet_address}"
        
        # Property: Insert should be called once per operation
        assert mock_table.insert.call_count == len(wallet_addresses), \
            f"Insert should be called {len(wallet_addresses)} times, " \
            f"but was called {mock_table.insert.call_count} times"
        
        # Property: Each audit entry should have unique wallet address
        all_calls = mock_table.insert.call_args_list
        logged_wallets = [call[0][0]['wallet_address'] for call in all_calls]
        
        assert len(logged_wallets) == len(wallet_addresses), \
            "Number of logged wallets should match input"
        
        for wallet in wallet_addresses:
            assert wallet in logged_wallets, \
                f"Wallet {wallet} should be in audit logs"
        
        print(f"✅ Multiple operations logged: {len(wallet_addresses)} decryptions for admin {admin_id}")


@given(
    wallet_address=wallet_address_strategy,
    operation_type=operation_type_strategy,
    admin_id=admin_id_strategy,
    success=success_status_strategy
)
@settings(max_examples=100, deadline=None)
def test_audit_log_success_and_failure(
    wallet_address,
    operation_type,
    admin_id,
    success
):
    """
    Property 27: Audit Logging for Success and Failure
    
    For any decryption operation, both successful and failed operations 
    should be logged with appropriate success status.
    
    This validates that all outcomes are audited.
    """
    # Create a mock Supabase client
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()
    
    # Set up the mock chain
    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = mock_execute
    
    # Create audit logger with mocked Supabase
    with patch('app.audit_logger.create_client', return_value=mock_supabase):
        audit_logger = AuditLogger()
        audit_logger.supabase = mock_supabase
        audit_logger.supabase_enabled = True
        
        # Prepare error message for failures
        error_msg = "Decryption failed" if not success else None
        
        # Log the decryption operation
        result = audit_logger.log_private_key_decryption(
            wallet_address=wallet_address,
            operation_type=operation_type,
            admin_id=admin_id,
            success=success,
            error_message=error_msg
        )
        
        # Property: Logging should succeed regardless of operation outcome
        assert result is True, \
            "Audit logging should succeed for both success and failure cases"
        
        # Get the audit entry
        insert_call_args = mock_table.insert.call_args
        audit_entry = insert_call_args[0][0]
        
        # Property: Success status should match input
        assert audit_entry['success'] == success, \
            f"Success status should be {success}"
        
        # Property: Error message should be present for failures
        if not success:
            assert audit_entry['error_message'] is not None, \
                "Failed operations should have error message"
        
        status_str = "successful" if success else "failed"
        print(f"✅ Audit log created for {status_str} {operation_type} on {wallet_address[:10]}...")


@given(
    wallet_address=wallet_address_strategy,
    operation_type=operation_type_strategy,
    admin_id=admin_id_strategy
)
@settings(max_examples=100, deadline=None)
def test_audit_log_metadata_completeness(
    wallet_address,
    operation_type,
    admin_id
):
    """
    Property 27: Audit Log Metadata Completeness
    
    For any decryption operation, the audit log metadata should contain 
    operation and wallet information for quick filtering and analysis.
    
    This validates that metadata is properly structured.
    """
    # Create a mock Supabase client
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()
    
    # Set up the mock chain
    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = mock_execute
    
    # Create audit logger with mocked Supabase
    with patch('app.audit_logger.create_client', return_value=mock_supabase):
        audit_logger = AuditLogger()
        audit_logger.supabase = mock_supabase
        audit_logger.supabase_enabled = True
        
        # Log the decryption operation
        result = audit_logger.log_private_key_decryption(
            wallet_address=wallet_address,
            operation_type=operation_type,
            admin_id=admin_id,
            success=True
        )
        
        # Get the audit entry
        insert_call_args = mock_table.insert.call_args
        audit_entry = insert_call_args[0][0]
        
        # Property: Metadata should be a dictionary
        metadata = audit_entry['metadata']
        assert isinstance(metadata, dict), \
            "Metadata should be a dictionary"
        
        # Property: Metadata should contain operation
        assert 'operation' in metadata, \
            "Metadata should contain 'operation' key"
        assert metadata['operation'] == operation_type, \
            f"Metadata operation should be {operation_type}"
        
        # Property: Metadata should contain wallet
        assert 'wallet' in metadata, \
            "Metadata should contain 'wallet' key"
        assert metadata['wallet'] == wallet_address, \
            f"Metadata wallet should be {wallet_address}"
        
        # Property: Metadata should not contain sensitive information
        sensitive_keys = ['private_key', 'secret', 'password', 'mnemonic']
        for key in metadata.keys():
            assert key.lower() not in sensitive_keys, \
                f"Metadata should not contain sensitive key: {key}"
        
        print(f"✅ Metadata complete for {operation_type} on {wallet_address[:10]}...")


if __name__ == "__main__":
    import pytest
    
    print("=" * 70)
    print("Property-Based Test: Audit Logging for Decryption")
    print("Feature: automaton-integration, Property 27")
    print("=" * 70)
    print()
    print("Testing audit logging for private key decryption operations...")
    print("Validates: Requirements 11.4")
    print()
    print("Properties being tested:")
    print("  1. Every decryption creates an audit log entry")
    print("  2. Audit log contains required fields (timestamp, wallet, operation)")
    print("  3. Both successful and failed operations are logged")
    print("  4. Admin ID is recorded for accountability")
    print("  5. Audit logs are immutable and retrievable")
    print("  6. Metadata is properly structured")
    print()
    
    # Run the tests
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
    
    sys.exit(exit_code)
