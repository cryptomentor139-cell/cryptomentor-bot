"""
Property-based test for mode persistence.

Feature: dual-mode-offline-online
Property 14: Mode Persistence
Validates: Requirements 1.7

For any mode change, the system should persist the new mode state to the 
database and increment the transition counter.
"""

import os
import pytest
from hypothesis import given, strategies as st, assume, settings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if environment variables are set
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    pytest.skip(
        "SUPABASE_URL and SUPABASE_KEY must be set to run these tests",
        allow_module_level=True
    )

from app.dual_mode_db import (
    get_user_mode,
    set_user_mode,
    supabase
)


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    mode=st.sampled_from(['offline', 'online'])
)
def test_mode_persistence(user_id, mode):
    """
    Feature: dual-mode-offline-online, Property 14: Mode Persistence
    
    For any mode change, the system should persist the new mode state to the 
    database and increment the transition counter.
    
    **Validates: Requirements 1.7**
    """
    # Clean up any existing state for this user
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Get initial transition count (should be 0 for new user)
    initial_result = supabase.table('user_mode_states')\
        .select('transition_count')\
        .eq('user_id', user_id)\
        .execute()
    
    initial_count = 0
    if initial_result.data and len(initial_result.data) > 0:
        initial_count = initial_result.data[0]['transition_count']
    
    # Set the mode
    success = set_user_mode(user_id, mode)
    assert success, f"Failed to set mode for user {user_id}"
    
    # Verify mode was persisted
    persisted_mode = get_user_mode(user_id)
    assert persisted_mode == mode, \
        f"Mode not persisted correctly: expected {mode}, got {persisted_mode}"
    
    # Verify transition count was incremented
    result = supabase.table('user_mode_states')\
        .select('transition_count')\
        .eq('user_id', user_id)\
        .execute()
    
    assert result.data and len(result.data) > 0, \
        "No mode state record found after setting mode"
    
    new_count = result.data[0]['transition_count']
    
    # For first mode set, count should be 0 (no transition yet)
    # For subsequent sets, count should increment
    if initial_count == 0:
        assert new_count == 0, \
            f"First mode set should have transition_count=0, got {new_count}"
    else:
        assert new_count == initial_count + 1, \
            f"Transition count not incremented: expected {initial_count + 1}, got {new_count}"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    modes=st.lists(
        st.sampled_from(['offline', 'online']),
        min_size=2,
        max_size=5
    )
)
def test_multiple_mode_transitions_increment_counter(user_id, modes):
    """
    Feature: dual-mode-offline-online, Property 14: Mode Persistence
    
    For any sequence of mode changes, the transition counter should increment
    correctly with each transition.
    
    **Validates: Requirements 1.7**
    """
    # Clean up any existing state
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set initial mode
    first_mode = modes[0]
    success = set_user_mode(user_id, first_mode)
    assert success, "Failed to set initial mode"
    
    # Get initial count (should be 0)
    result = supabase.table('user_mode_states')\
        .select('transition_count')\
        .eq('user_id', user_id)\
        .execute()
    
    assert result.data and len(result.data) > 0
    initial_count = result.data[0]['transition_count']
    assert initial_count == 0, f"Initial transition count should be 0, got {initial_count}"
    
    # Perform transitions
    expected_count = 0
    for i, mode in enumerate(modes[1:], start=1):
        success = set_user_mode(user_id, mode)
        assert success, f"Failed to set mode at transition {i}"
        
        # Verify mode persisted
        persisted_mode = get_user_mode(user_id)
        assert persisted_mode == mode, \
            f"Mode not persisted at transition {i}: expected {mode}, got {persisted_mode}"
        
        # Verify counter incremented
        result = supabase.table('user_mode_states')\
            .select('transition_count')\
            .eq('user_id', user_id)\
            .execute()
        
        assert result.data and len(result.data) > 0
        current_count = result.data[0]['transition_count']
        expected_count = i
        
        assert current_count == expected_count, \
            f"Transition {i}: expected count {expected_count}, got {current_count}"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999),
    mode=st.sampled_from(['offline', 'online'])
)
def test_mode_persistence_survives_retrieval(user_id, mode):
    """
    Feature: dual-mode-offline-online, Property 14: Mode Persistence
    
    For any mode change, the persisted mode should be retrievable even after
    multiple get operations.
    
    **Validates: Requirements 1.7**
    """
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Set mode
    success = set_user_mode(user_id, mode)
    assert success, "Failed to set mode"
    
    # Retrieve mode multiple times
    for _ in range(5):
        retrieved_mode = get_user_mode(user_id)
        assert retrieved_mode == mode, \
            f"Mode not persisted correctly: expected {mode}, got {retrieved_mode}"
    
    # Clean up
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
    except:
        pass


@settings(max_examples=5, deadline=None)
@given(
    user_id=st.integers(min_value=1, max_value=999999)
)
def test_default_mode_is_offline(user_id):
    """
    Feature: dual-mode-offline-online, Property 14: Mode Persistence
    
    For any user without a mode record, the default mode should be 'offline'.
    
    **Validates: Requirements 1.7**
    """
    # Clean up to ensure no existing record
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
    except:
        pass
    
    # Get mode for user with no record
    mode = get_user_mode(user_id)
    
    # Should default to offline
    assert mode == 'offline', \
        f"Default mode should be 'offline', got '{mode}'"
    
    # Clean up (though there should be nothing to clean)
    try:
        supabase.table('user_mode_states').delete().eq('user_id', user_id).execute()
    except:
        pass


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
