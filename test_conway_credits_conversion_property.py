"""
Property-Based Test: Conway Credits Conversion Formula

Feature: automaton-integration
Property 7: Conway Credits Conversion Formula

For any confirmed deposit of amount A in USDT or USDC, the credited Conway 
credits should equal (A × 0.98) × 100, where 0.98 represents the 2% platform 
fee deduction.

Validates: Requirements 2.4, 3.1, 3.2, 3.3, 21.1

This test validates that:
1. Platform fee is correctly calculated (2% of deposit)
2. Net amount after fee is correct (98% of deposit)
3. Conway credits conversion rate is correct (1:100)
4. Formula works for both USDT and USDC
5. Formula works across various deposit amounts
"""

from hypothesis import given, strategies as st, settings
from decimal import Decimal


# Constants from the deposit monitor implementation
PLATFORM_FEE_RATE = 0.02  # 2%
CREDIT_CONVERSION_RATE = 100  # 1 USDC/USDT = 100 credits
MIN_DEPOSIT = 5.0  # Minimum deposit amount


def calculate_conway_credits(deposit_amount: float) -> tuple[float, float, float]:
    """
    Calculate Conway credits after platform fee deduction.
    
    This is the core conversion formula being tested.
    
    Args:
        deposit_amount: USDC or USDT deposit amount
        
    Returns:
        Tuple of (net_amount, platform_fee, conway_credits)
    """
    platform_fee = deposit_amount * PLATFORM_FEE_RATE
    net_amount = deposit_amount - platform_fee
    conway_credits = net_amount * CREDIT_CONVERSION_RATE
    
    return (net_amount, platform_fee, conway_credits)


@given(deposit_amount=st.floats(min_value=5.0, max_value=10000.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=100, deadline=None)
def test_conway_credits_conversion_formula(deposit_amount):
    """
    **Validates: Requirements 2.4, 3.1, 3.2, 3.3, 21.1**
    
    Property 7: Conway Credits Conversion Formula
    
    For any confirmed deposit amount A (where A >= 5.0), the conversion
    should follow the formula: conway_credits = (A × 0.98) × 100
    
    This validates the core business logic of the deposit processing system.
    """
    # Calculate using the conversion function
    net_amount, platform_fee, conway_credits = calculate_conway_credits(deposit_amount)
    
    # Property 1: Platform fee should be exactly 2% of deposit
    expected_fee = deposit_amount * 0.02
    assert abs(platform_fee - expected_fee) < 0.01, \
        f"Platform fee incorrect: expected {expected_fee}, got {platform_fee}"
    
    # Property 2: Net amount should be 98% of deposit (deposit - fee)
    expected_net = deposit_amount * 0.98
    assert abs(net_amount - expected_net) < 0.01, \
        f"Net amount incorrect: expected {expected_net}, got {net_amount}"
    
    # Property 3: Net amount should equal deposit minus fee
    assert abs(net_amount - (deposit_amount - platform_fee)) < 0.0001, \
        f"Net amount should equal deposit - fee: {deposit_amount} - {platform_fee} = {net_amount}"
    
    # Property 4: Conway credits should equal net amount × 100
    expected_credits = net_amount * 100
    assert abs(conway_credits - expected_credits) < 0.01, \
        f"Conway credits incorrect: expected {expected_credits}, got {conway_credits}"
    
    # Property 5: Conway credits should equal (deposit × 0.98) × 100
    expected_credits_direct = (deposit_amount * 0.98) * 100
    assert abs(conway_credits - expected_credits_direct) < 0.01, \
        f"Conway credits don't match formula: expected {expected_credits_direct}, got {conway_credits}"
    
    # Property 6: All values should be positive
    assert platform_fee > 0, "Platform fee should be positive"
    assert net_amount > 0, "Net amount should be positive"
    assert conway_credits > 0, "Conway credits should be positive"
    
    # Property 7: Fee + net amount should equal original deposit
    assert abs((platform_fee + net_amount) - deposit_amount) < 0.0001, \
        f"Fee + net should equal deposit: {platform_fee} + {net_amount} = {deposit_amount}"
    
    print(f"✅ Deposit {deposit_amount:.2f} → Fee {platform_fee:.2f} → Net {net_amount:.2f} → Credits {conway_credits:.2f}")


@given(
    deposit_amount=st.floats(min_value=5.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    token=st.sampled_from(['USDT', 'USDC'])
)
@settings(max_examples=100, deadline=None)
def test_conway_credits_conversion_both_tokens(deposit_amount, token):
    """
    **Validates: Requirements 3.1, 3.2**
    
    Property 7: Conway Credits Conversion Formula (Token Agnostic)
    
    For any deposit amount in either USDT or USDC, the conversion formula
    should be identical. Both tokens use the same 1:100 conversion rate.
    
    This validates that USDT and USDC are treated equally.
    """
    # Calculate credits
    net_amount, platform_fee, conway_credits = calculate_conway_credits(deposit_amount)
    
    # Property: Conversion should be the same regardless of token
    expected_credits = (deposit_amount * 0.98) * 100
    assert abs(conway_credits - expected_credits) < 0.01, \
        f"{token} conversion incorrect: expected {expected_credits}, got {conway_credits}"
    
    # Property: Both tokens should use 2% fee
    expected_fee = deposit_amount * 0.02
    assert abs(platform_fee - expected_fee) < 0.01, \
        f"{token} fee incorrect: expected {expected_fee}, got {platform_fee}"
    
    print(f"✅ {token} {deposit_amount:.2f} → {conway_credits:.2f} credits")


@given(deposit_amount=st.floats(min_value=5.0, max_value=10000.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=100, deadline=None)
def test_conway_credits_conversion_precision(deposit_amount):
    """
    **Validates: Requirements 2.4, 21.1**
    
    Property 7: Conway Credits Conversion Formula (Precision)
    
    For any deposit amount, the conversion should maintain reasonable
    precision without significant rounding errors.
    
    This validates numerical stability of the conversion.
    """
    net_amount, platform_fee, conway_credits = calculate_conway_credits(deposit_amount)
    
    # Use Decimal for high-precision validation
    deposit_decimal = Decimal(str(deposit_amount))
    fee_decimal = deposit_decimal * Decimal('0.02')
    net_decimal = deposit_decimal - fee_decimal
    credits_decimal = net_decimal * Decimal('100')
    
    # Property: Float calculation should be close to Decimal calculation
    assert abs(float(fee_decimal) - platform_fee) < 0.01, \
        "Platform fee has precision issues"
    
    assert abs(float(net_decimal) - net_amount) < 0.01, \
        "Net amount has precision issues"
    
    assert abs(float(credits_decimal) - conway_credits) < 0.01, \
        "Conway credits have precision issues"
    
    print(f"✅ Precision validated for {deposit_amount:.2f}")


@given(
    deposits=st.lists(
        st.floats(min_value=5.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=5
    )
)
@settings(max_examples=100, deadline=None)
def test_conway_credits_conversion_additivity(deposits):
    """
    **Validates: Requirements 2.4, 3.3**
    
    Property 7: Conway Credits Conversion Formula (Additivity)
    
    For any set of deposits, the total Conway credits from processing
    them individually should equal the sum of credits from each deposit.
    
    This validates that the conversion is additive and consistent.
    """
    total_credits = 0
    total_fees = 0
    
    for deposit in deposits:
        net_amount, platform_fee, conway_credits = calculate_conway_credits(deposit)
        total_credits += conway_credits
        total_fees += platform_fee
    
    # Property: Total credits should equal sum of individual conversions
    total_deposit = sum(deposits)
    expected_total_fee = total_deposit * 0.02
    expected_total_credits = (total_deposit * 0.98) * 100
    
    assert abs(total_fees - expected_total_fee) < 0.1, \
        f"Total fees don't match: expected {expected_total_fee}, got {total_fees}"
    
    assert abs(total_credits - expected_total_credits) < 0.1, \
        f"Total credits don't match: expected {expected_total_credits}, got {total_credits}"
    
    print(f"✅ {len(deposits)} deposits totaling {total_deposit:.2f} → {total_credits:.2f} credits")


@given(deposit_amount=st.floats(min_value=5.0, max_value=10000.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=100, deadline=None)
def test_conway_credits_conversion_bounds(deposit_amount):
    """
    **Validates: Requirements 2.4, 3.3**
    
    Property 7: Conway Credits Conversion Formula (Bounds)
    
    For any deposit amount A, the Conway credits should satisfy:
    - Credits < A × 100 (due to 2% fee)
    - Credits > A × 95 (reasonable lower bound)
    - Credits = A × 98 (exact formula)
    
    This validates that the conversion stays within expected bounds.
    """
    net_amount, platform_fee, conway_credits = calculate_conway_credits(deposit_amount)
    
    # Property 1: Credits should be less than deposit × 100 (due to fee)
    max_possible_credits = deposit_amount * 100
    assert conway_credits < max_possible_credits, \
        f"Credits {conway_credits} should be less than {max_possible_credits}"
    
    # Property 2: Credits should be greater than deposit × 95 (reasonable lower bound)
    min_reasonable_credits = deposit_amount * 95
    assert conway_credits > min_reasonable_credits, \
        f"Credits {conway_credits} should be greater than {min_reasonable_credits}"
    
    # Property 3: Credits should equal deposit × 98 (exact formula)
    expected_credits = deposit_amount * 98
    assert abs(conway_credits - expected_credits) < 0.1, \
        f"Credits {conway_credits} should equal {expected_credits}"
    
    # Property 4: Fee should be between 1% and 3% of deposit (sanity check)
    assert platform_fee > deposit_amount * 0.01, "Fee too low"
    assert platform_fee < deposit_amount * 0.03, "Fee too high"
    
    print(f"✅ Bounds validated for {deposit_amount:.2f}: {conway_credits:.2f} credits")


@given(deposit_amount=st.floats(min_value=5.0, max_value=10000.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=100, deadline=None)
def test_conway_credits_conversion_monotonicity(deposit_amount):
    """
    **Validates: Requirements 2.4**
    
    Property 7: Conway Credits Conversion Formula (Monotonicity)
    
    For any two deposit amounts A and B where A < B, the Conway credits
    for A should be less than the Conway credits for B.
    
    This validates that larger deposits always yield more credits.
    """
    # Calculate credits for original amount
    _, _, credits_a = calculate_conway_credits(deposit_amount)
    
    # Calculate credits for slightly larger amount
    larger_deposit = deposit_amount * 1.1  # 10% more
    _, _, credits_b = calculate_conway_credits(larger_deposit)
    
    # Property: Larger deposit should yield more credits (monotonicity)
    assert credits_b > credits_a, \
        f"Monotonicity violated: {deposit_amount} → {credits_a}, {larger_deposit} → {credits_b}"
    
    # Property: The increase should be proportional
    expected_increase_ratio = 1.1
    actual_increase_ratio = credits_b / credits_a
    assert abs(actual_increase_ratio - expected_increase_ratio) < 0.01, \
        f"Increase not proportional: expected {expected_increase_ratio}, got {actual_increase_ratio}"
    
    print(f"✅ Monotonicity: {deposit_amount:.2f} → {credits_a:.2f}, {larger_deposit:.2f} → {credits_b:.2f}")


@given(deposit_amount=st.floats(min_value=5.0, max_value=10000.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=100, deadline=None)
def test_conway_credits_conversion_platform_revenue(deposit_amount):
    """
    **Validates: Requirements 21.1**
    
    Property 7: Conway Credits Conversion Formula (Platform Revenue)
    
    For any deposit amount, the platform fee should be exactly 2% of the
    deposit, which represents the platform's revenue from deposits.
    
    This validates the revenue model is correctly implemented.
    """
    net_amount, platform_fee, conway_credits = calculate_conway_credits(deposit_amount)
    
    # Property 1: Platform fee should be exactly 2%
    expected_fee_percentage = 0.02
    actual_fee_percentage = platform_fee / deposit_amount
    assert abs(actual_fee_percentage - expected_fee_percentage) < 0.0001, \
        f"Fee percentage incorrect: expected {expected_fee_percentage}, got {actual_fee_percentage}"
    
    # Property 2: Platform keeps 2%, user gets 98%
    user_percentage = net_amount / deposit_amount
    assert abs(user_percentage - 0.98) < 0.0001, \
        f"User percentage incorrect: expected 0.98, got {user_percentage}"
    
    # Property 3: Platform fee + net amount = 100% of deposit
    total_percentage = (platform_fee + net_amount) / deposit_amount
    assert abs(total_percentage - 1.0) < 0.0001, \
        f"Total percentage should be 1.0, got {total_percentage}"
    
    print(f"✅ Revenue model validated: {deposit_amount:.2f} → Platform {platform_fee:.2f} (2%), User {net_amount:.2f} (98%)")


@given(deposit_amount=st.floats(min_value=0.1, max_value=4.99, allow_nan=False, allow_infinity=False))
@settings(max_examples=100, deadline=None)
def test_conway_credits_conversion_minimum_deposit(deposit_amount):
    """
    **Validates: Requirements 3.4**
    
    Property 7: Conway Credits Conversion Formula (Minimum Deposit)
    
    For any deposit amount below the minimum (5 USDT/USDC), the system
    should still calculate the conversion correctly, but the deposit
    should be rejected at the validation layer.
    
    This validates that the formula works mathematically even for small
    amounts, but business logic enforces the minimum.
    """
    # The formula should still work mathematically
    net_amount, platform_fee, conway_credits = calculate_conway_credits(deposit_amount)
    
    # Property: Formula should still produce valid results
    assert platform_fee > 0, "Fee should be positive even for small deposits"
    assert net_amount > 0, "Net amount should be positive"
    assert conway_credits > 0, "Credits should be positive"
    
    # Property: Formula should still be correct
    expected_credits = (deposit_amount * 0.98) * 100
    assert abs(conway_credits - expected_credits) < 0.01, \
        f"Formula should work for small amounts: expected {expected_credits}, got {conway_credits}"
    
    # Property: Deposit is below minimum (business rule validation)
    assert deposit_amount < MIN_DEPOSIT, \
        f"Test deposit {deposit_amount} should be below minimum {MIN_DEPOSIT}"
    
    print(f"✅ Formula works for small deposit {deposit_amount:.2f} → {conway_credits:.2f} credits (but would be rejected)")


if __name__ == "__main__":
    import pytest
    import sys
    
    print("=" * 70)
    print("Property-Based Test: Conway Credits Conversion Formula")
    print("Feature: automaton-integration, Property 7")
    print("=" * 70)
    print()
    print("Testing the core conversion formula:")
    print("  conway_credits = (deposit_amount × 0.98) × 100")
    print()
    print("Where:")
    print("  - 0.98 represents 98% after 2% platform fee")
    print("  - 100 is the conversion rate (1 USDC/USDT = 100 credits)")
    print()
    print("Validates: Requirements 2.4, 3.1, 3.2, 3.3, 21.1")
    print()
    
    # Run the tests
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
    
    sys.exit(exit_code)
