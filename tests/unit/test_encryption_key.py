#!/usr/bin/env python3
"""
Test Encryption Key Configuration

This script verifies that the ENCRYPTION_KEY environment variable is:
1. Set and not empty
2. Valid Fernet key format
3. Can encrypt and decrypt data successfully
"""

import os
import sys
from cryptography.fernet import Fernet, InvalidToken

def test_encryption_key():
    """Test the encryption key configuration"""
    print("=" * 70)
    print("🔐 TESTING ENCRYPTION KEY CONFIGURATION")
    print("=" * 70)
    print()
    
    # Step 1: Check if key exists
    print("1️⃣ Checking if ENCRYPTION_KEY is set...")
    encryption_key = os.getenv('ENCRYPTION_KEY')
    
    if not encryption_key:
        print("❌ ENCRYPTION_KEY not found in environment variables!")
        print()
        print("📝 SOLUTION:")
        print("   1. Run: python generate_encryption_key.py")
        print("   2. Copy the generated key")
        print("   3. Add to .env file: ENCRYPTION_KEY=<your_key>")
        print()
        return False
    
    if encryption_key == '<your-fernet-key>':
        print("❌ ENCRYPTION_KEY is still placeholder!")
        print()
        print("📝 SOLUTION:")
        print("   1. Run: python generate_encryption_key.py")
        print("   2. Copy the generated key")
        print("   3. Replace placeholder in .env file")
        print()
        return False
    
    print(f"✅ ENCRYPTION_KEY found: {encryption_key[:20]}...{encryption_key[-10:]}")
    print()
    
    # Step 2: Check key format
    print("2️⃣ Validating Fernet key format...")
    try:
        cipher = Fernet(encryption_key.encode())
        print("✅ Key format is valid!")
        print()
    except Exception as e:
        print(f"❌ Invalid Fernet key format: {e}")
        print()
        print("📝 SOLUTION:")
        print("   The key must be a valid Fernet key (base64 encoded, 44 chars)")
        print("   Run: python generate_encryption_key.py")
        print()
        return False
    
    # Step 3: Test encryption
    print("3️⃣ Testing encryption...")
    test_data = b"test_private_key_0x1234567890abcdef"
    try:
        encrypted = cipher.encrypt(test_data)
        print(f"✅ Encryption successful!")
        print(f"   Original: {test_data.decode()}")
        print(f"   Encrypted: {encrypted[:30]}...{encrypted[-10:]}")
        print()
    except Exception as e:
        print(f"❌ Encryption failed: {e}")
        print()
        return False
    
    # Step 4: Test decryption
    print("4️⃣ Testing decryption...")
    try:
        decrypted = cipher.decrypt(encrypted)
        if decrypted == test_data:
            print("✅ Decryption successful!")
            print(f"   Decrypted: {decrypted.decode()}")
            print()
        else:
            print("❌ Decryption mismatch!")
            print(f"   Expected: {test_data.decode()}")
            print(f"   Got: {decrypted.decode()}")
            print()
            return False
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        print()
        return False
    
    # Step 5: Test with Ethereum private key format
    print("5️⃣ Testing with Ethereum private key format...")
    eth_private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    try:
        encrypted_eth = cipher.encrypt(eth_private_key.encode())
        decrypted_eth = cipher.decrypt(encrypted_eth)
        if decrypted_eth.decode() == eth_private_key:
            print("✅ Ethereum private key encryption/decryption works!")
            print()
        else:
            print("❌ Ethereum private key test failed!")
            print()
            return False
    except Exception as e:
        print(f"❌ Ethereum private key test failed: {e}")
        print()
        return False
    
    # All tests passed
    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("🎉 Your encryption key is properly configured and working!")
    print()
    print("📝 NEXT STEPS:")
    print("   1. Make sure this key is backed up securely")
    print("   2. Add the same key to Railway environment variables")
    print("   3. Test the deposit flow in your bot")
    print()
    print("⚠️  SECURITY REMINDER:")
    print("   - NEVER commit this key to git")
    print("   - NEVER share this key with anyone")
    print("   - Store backup in password manager")
    print("   - Rotate key every 90 days")
    print()
    print("=" * 70)
    return True

def main():
    """Main function"""
    # Load .env file if exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded .env file")
        print()
    except ImportError:
        print("⚠️  python-dotenv not installed, reading from system environment")
        print()
    
    # Run tests
    success = test_encryption_key()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
