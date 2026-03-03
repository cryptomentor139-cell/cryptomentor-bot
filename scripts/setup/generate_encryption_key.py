#!/usr/bin/env python3
"""
Generate Wallet Encryption Key for Automaton Integration

This script generates a Fernet encryption key for encrypting custodial wallet private keys.
The generated key must be stored securely in Railway environment variables.

CRITICAL SECURITY NOTES:
- This key encrypts ALL user wallet private keys
- NEVER commit this key to git
- NEVER share this key with anyone
- Store backup in secure location (password manager)
- Rotate every 90 days for security

Usage:
    python generate_encryption_key.py
"""

from cryptography.fernet import Fernet
import os
from datetime import datetime, timedelta

def generate_encryption_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key()
    return key.decode()

def test_encryption_key(key_string):
    """Test that the encryption key works correctly"""
    try:
        cipher = Fernet(key_string.encode())
        
        # Test encryption/decryption
        test_data = b"test_private_key_0x1234567890abcdef"
        encrypted = cipher.encrypt(test_data)
        decrypted = cipher.decrypt(encrypted)
        
        if decrypted == test_data:
            return True, "Encryption test passed"
        else:
            return False, "Decryption mismatch"
    except Exception as e:
        return False, f"Encryption test failed: {e}"

def main():
    print("=" * 70)
    print("🔐 WALLET ENCRYPTION KEY GENERATOR")
    print("=" * 70)
    print()
    
    # Generate new key
    print("🔑 Generating new Fernet encryption key...")
    key = generate_encryption_key()
    print("✅ Key generated successfully!")
    print()
    
    # Test the key
    print("🧪 Testing encryption key...")
    success, message = test_encryption_key(key)
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        return
    print()
    
    # Display the key
    print("=" * 70)
    print("📋 YOUR WALLET ENCRYPTION KEY:")
    print("=" * 70)
    print()
    print(f"WALLET_ENCRYPTION_KEY={key}")
    print()
    print("=" * 70)
    print()
    
    # Security instructions
    print("🔒 SECURITY INSTRUCTIONS:")
    print()
    print("1. Copy the key above and add it to Railway environment variables")
    print("   - Go to Railway dashboard → Your service → Variables")
    print("   - Add: WALLET_ENCRYPTION_KEY = <the key above>")
    print()
    print("2. Store a backup of this key in a secure location:")
    print("   - Password manager (1Password, Bitwarden, etc.)")
    print("   - Encrypted file on secure storage")
    print("   - Physical backup in safe location")
    print()
    print("3. NEVER commit this key to git or share it publicly")
    print()
    print("4. Set a reminder to rotate this key in 90 days")
    rotation_date = datetime.now() + timedelta(days=90)
    print(f"   - Next rotation date: {rotation_date.strftime('%Y-%m-%d')}")
    print()
    print("=" * 70)
    print()
    
    # Save to .env.example (without the actual key)
    print("💾 Creating .env.example template...")
    env_example = """# Automaton Integration Environment Variables
# Copy this file to .env and fill in the actual values

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Blockchain (Polygon)
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/your_api_key
POLYGON_USDT_CONTRACT=0xc2132D05D31c914a87C6611C10748AEb04B58e8F
POLYGON_USDC_CONTRACT=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174

# Wallet Encryption (CRITICAL - Generate using generate_encryption_key.py)
WALLET_ENCRYPTION_KEY=your_fernet_key_here

# Conway Cloud API
CONWAY_API_URL=https://api.conway.tech
CONWAY_API_KEY=your_conway_api_key_here

# Admin Configuration
ADMIN_IDS=1187119989,7255533151
ADMIN_USER_ID=1187119989
"""
    
    with open('.env.automaton.example', 'w') as f:
        f.write(env_example)
    
    print("✅ Created .env.automaton.example template")
    print()
    
    # Warning
    print("⚠️  WARNING:")
    print("   Without this key, you CANNOT decrypt user wallet private keys!")
    print("   Make sure to backup this key before proceeding.")
    print()
    print("=" * 70)
    print()
    
    # Next steps
    print("📝 NEXT STEPS:")
    print()
    print("1. Add the key to Railway environment variables")
    print("2. Run: python test_env.py (to verify all variables)")
    print("3. Run database migration: 001_automaton_tables.sql")
    print("4. Deploy bot to Railway")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
