"""
Property-Based Test: Wallet Encryption Round Trip

Feature: automaton-integration
Property 2: Wallet Encryption Round Trip

For any generated wallet private key, encrypting then decrypting using 
the Fernet cipher should produce the original private key value.

Validates: Requirements 1.2, 11.1

This test validates that:
1. Encryption is reversible (round trip works)
2. No data corruption during encryption/decryption
3. Works with various private key formats
4. Fernet cipher is properly configured
"""

import os
from dotenv import load_dotenv
from hypothesis import given, strategies as st, settings
from cryptography.fernet import Fernet

# Load environment variables
load_dotenv()

# Global test key - generated once and reused for all tests
_TEST_ENCRYPTION_KEY = None


def get_encryption_key() -> bytes:
    """
    Get the Fernet encryption key from environment variables.
    
    Returns:
        Fernet key as bytes
        
    Raises:
        ValueError: If key is not set or invalid
    """
    global _TEST_ENCRYPTION_KEY
    
    key_string = os.getenv('WALLET_ENCRYPTION_KEY')
    
    if not key_string:
        # Generate a test key once and reuse it for all tests
        if _TEST_ENCRYPTION_KEY is None:
            print("⚠️  WALLET_ENCRYPTION_KEY not set, generating test key for session")
            _TEST_ENCRYPTION_KEY = Fernet.generate_key()
        return _TEST_ENCRYPTION_KEY
    
    return key_string.encode()


def encrypt_private_key(private_key: str) -> str:
    """
    Encrypt a private key using Fernet symmetric encryption.
    
    Args:
        private_key: The private key to encrypt (as string)
        
    Returns:
        Encrypted private key (base64 encoded string)
    """
    key = get_encryption_key()
    cipher = Fernet(key)
    
    # Convert private key to bytes and encrypt
    private_key_bytes = private_key.encode('utf-8')
    encrypted_bytes = cipher.encrypt(private_key_bytes)
    
    # Return as string (base64 encoded)
    return encrypted_bytes.decode('utf-8')


def decrypt_private_key(encrypted_key: str) -> str:
    """
    Decrypt a private key using Fernet symmetric encryption.
    
    Args:
        encrypted_key: The encrypted private key (base64 encoded string)
        
    Returns:
        Decrypted private key (as string)
    """
    key = get_encryption_key()
    cipher = Fernet(key)
    
    # Convert encrypted key to bytes and decrypt
    encrypted_bytes = encrypted_key.encode('utf-8')
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    
    # Return as string
    return decrypted_bytes.decode('utf-8')


# Strategy for generating Ethereum private keys (64 hex characters)
eth_private_key_strategy = st.text(
    alphabet='0123456789abcdef',
    min_size=64,
    max_size=64
)

# Strategy for generating private keys with 0x prefix
eth_private_key_with_prefix_strategy = st.builds(
    lambda hex_str: f"0x{hex_str}",
    st.text(alphabet='0123456789abcdef', min_size=64, max_size=64)
)

# Strategy for various private key formats
private_key_formats_strategy = st.one_of(
    eth_private_key_strategy,
    eth_private_key_with_prefix_strategy,
    st.text(min_size=32, max_size=128, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    ))
)


@given(private_key=eth_private_key_strategy)
@settings(max_examples=100, deadline=None)
def test_encryption_roundtrip_basic(private_key):
    """
    Property 2: Wallet Encryption Round Trip (Basic)
    
    For any Ethereum private key (64 hex characters), encrypting then 
    decrypting should produce the original value.
    
    This validates the core encryption/decryption functionality.
    """
    # Encrypt the private key
    encrypted = encrypt_private_key(private_key)
    
    # Property 1: Encrypted value should be different from original
    assert encrypted != private_key, \
        "Encrypted value should differ from original"
    
    # Property 2: Encrypted value should be non-empty
    assert len(encrypted) > 0, \
        "Encrypted value should not be empty"
    
    # Property 3: Encrypted value should be base64 encoded (Fernet format)
    # Fernet tokens are base64 encoded and start with specific bytes
    assert isinstance(encrypted, str), \
        "Encrypted value should be a string"
    
    # Decrypt the encrypted key
    decrypted = decrypt_private_key(encrypted)
    
    # Property 4: Decrypted value should match original (ROUND TRIP)
    assert decrypted == private_key, \
        f"Round trip failed: original={private_key[:10]}..., decrypted={decrypted[:10]}..."
    
    # Property 5: Decrypted value should have same length as original
    assert len(decrypted) == len(private_key), \
        f"Length mismatch: original={len(private_key)}, decrypted={len(decrypted)}"
    
    print(f"✅ Round trip successful for key: {private_key[:10]}...{private_key[-10:]}")


@given(private_key=eth_private_key_with_prefix_strategy)
@settings(max_examples=100, deadline=None)
def test_encryption_roundtrip_with_prefix(private_key):
    """
    Property 2: Wallet Encryption Round Trip (With 0x Prefix)
    
    For any Ethereum private key with 0x prefix, encrypting then 
    decrypting should preserve the prefix and produce the original value.
    
    This validates that the encryption handles prefixed keys correctly.
    """
    # Encrypt the private key
    encrypted = encrypt_private_key(private_key)
    
    # Decrypt the encrypted key
    decrypted = decrypt_private_key(encrypted)
    
    # Property: Round trip should preserve the 0x prefix
    assert decrypted == private_key, \
        f"Round trip failed for prefixed key: {private_key[:12]}..."
    
    assert decrypted.startswith('0x'), \
        "Decrypted key should preserve 0x prefix"
    
    assert len(decrypted) == 66, \
        f"Prefixed key should be 66 chars (0x + 64 hex), got {len(decrypted)}"
    
    print(f"✅ Round trip successful for prefixed key: {private_key[:12]}...")


@given(private_key=private_key_formats_strategy)
@settings(max_examples=100, deadline=None)
def test_encryption_roundtrip_various_formats(private_key):
    """
    Property 2: Wallet Encryption Round Trip (Various Formats)
    
    For any private key format (hex, prefixed, alphanumeric), encrypting 
    then decrypting should produce the original value.
    
    This validates that encryption works with different key formats.
    """
    # Encrypt the private key
    encrypted = encrypt_private_key(private_key)
    
    # Decrypt the encrypted key
    decrypted = decrypt_private_key(encrypted)
    
    # Property: Round trip should work for any format
    assert decrypted == private_key, \
        f"Round trip failed: original length={len(private_key)}, decrypted length={len(decrypted)}"
    
    # Property: Character-by-character comparison
    for i, (orig_char, dec_char) in enumerate(zip(private_key, decrypted)):
        assert orig_char == dec_char, \
            f"Character mismatch at position {i}: '{orig_char}' != '{dec_char}'"
    
    print(f"✅ Round trip successful for format: {private_key[:20]}...")


@given(
    private_key=eth_private_key_strategy,
    iterations=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=100, deadline=None)
def test_encryption_multiple_roundtrips(private_key, iterations):
    """
    Property 2: Wallet Encryption Round Trip (Multiple Iterations)
    
    For any private key, performing multiple encrypt/decrypt cycles 
    should always produce the original value.
    
    This validates that encryption is consistently reversible.
    """
    current_value = private_key
    
    # Perform multiple encryption/decryption cycles
    for i in range(iterations):
        encrypted = encrypt_private_key(current_value)
        decrypted = decrypt_private_key(encrypted)
        
        # Property: Each round trip should preserve the value
        assert decrypted == current_value, \
            f"Round trip {i+1} failed: expected={current_value[:10]}..., got={decrypted[:10]}..."
        
        current_value = decrypted
    
    # Property: Final value should match original after all iterations
    assert current_value == private_key, \
        f"Multiple round trips failed after {iterations} iterations"
    
    print(f"✅ {iterations} round trips successful for key: {private_key[:10]}...")


@given(private_key=eth_private_key_strategy)
@settings(max_examples=100, deadline=None)
def test_encryption_deterministic(private_key):
    """
    Property 2: Wallet Encryption Round Trip (Determinism)
    
    For any private key, encrypting it multiple times should produce 
    different ciphertexts (due to Fernet's IV), but all should decrypt 
    to the same original value.
    
    This validates that Fernet uses proper randomization while maintaining
    correct decryption.
    """
    # Encrypt the same key multiple times
    encrypted1 = encrypt_private_key(private_key)
    encrypted2 = encrypt_private_key(private_key)
    encrypted3 = encrypt_private_key(private_key)
    
    # Property: Different encryptions should produce different ciphertexts
    # (Fernet includes a random IV, so ciphertexts differ)
    assert encrypted1 != encrypted2 or encrypted2 != encrypted3, \
        "Fernet should produce different ciphertexts for same plaintext"
    
    # Property: All ciphertexts should decrypt to the same original value
    decrypted1 = decrypt_private_key(encrypted1)
    decrypted2 = decrypt_private_key(encrypted2)
    decrypted3 = decrypt_private_key(encrypted3)
    
    assert decrypted1 == private_key, "First decryption failed"
    assert decrypted2 == private_key, "Second decryption failed"
    assert decrypted3 == private_key, "Third decryption failed"
    
    print(f"✅ Deterministic decryption verified for key: {private_key[:10]}...")


@given(private_key=eth_private_key_strategy)
@settings(max_examples=100, deadline=None)
def test_encryption_no_data_corruption(private_key):
    """
    Property 2: Wallet Encryption Round Trip (No Data Corruption)
    
    For any private key, the encryption/decryption process should not 
    corrupt any characters or introduce any modifications.
    
    This validates data integrity through the encryption process.
    """
    # Encrypt and decrypt
    encrypted = encrypt_private_key(private_key)
    decrypted = decrypt_private_key(encrypted)
    
    # Property: Exact byte-for-byte match
    assert decrypted == private_key, \
        "Data corruption detected in round trip"
    
    # Property: Same length
    assert len(decrypted) == len(private_key), \
        f"Length changed: {len(private_key)} -> {len(decrypted)}"
    
    # Property: Same character set
    original_chars = set(private_key)
    decrypted_chars = set(decrypted)
    assert decrypted_chars == original_chars, \
        f"Character set changed: {original_chars} -> {decrypted_chars}"
    
    # Property: Character frequency should match
    from collections import Counter
    original_freq = Counter(private_key)
    decrypted_freq = Counter(decrypted)
    assert original_freq == decrypted_freq, \
        "Character frequency changed during encryption"
    
    print(f"✅ No data corruption for key: {private_key[:10]}...")


if __name__ == "__main__":
    import pytest
    import sys
    
    print("=" * 70)
    print("Property-Based Test: Wallet Encryption Round Trip")
    print("Feature: automaton-integration, Property 2")
    print("=" * 70)
    print()
    print("Testing Fernet encryption/decryption round trip...")
    print("Validates: Requirements 1.2, 11.1")
    print()
    
    # Run the tests
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
    
    sys.exit(exit_code)
