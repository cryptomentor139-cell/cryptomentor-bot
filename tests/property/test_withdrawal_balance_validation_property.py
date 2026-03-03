"""
Property-Based Test: Withdrawal Balance Validation (Task 16.3)

Property 28: Withdrawal Balance Validation
**Validates: Requirements 12.1**

For any user with balance_usdt < withdrawal amount, attempting to withdraw 
should be rejected with an error message.

This property test uses hypothesis to generate random test cases and verify
that the withdrawal validation logic correctly rejects withdrawals when the
user has insufficient balance.
"""

import os
import sys
from hypothesis import given, strategies as st, settings
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname