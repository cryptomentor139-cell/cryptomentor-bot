#!/usr/bin/env python3
"""
Environment Variables Test Script for Automaton Integration

This script verifies that all required environment variables are set correctly
before deploying the Automaton integration feature.

Usage:
    python test_env.py
"""

import os
import sys
from cryptography.fernet import Fernet

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print formatted header"""
    print()
    print("=" * 70)
    print(f"{BLUE}{text}{RESET}")
    print("=" * 70)
    print()

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")

def mask_sensitive_value(value, show_chars=8):
    """Mask sensitive values for display"""
    if len(value) <= show_chars + 4:
        return value[:4] + '...'
    return value[:show_chars] + '...' + value[-4:]

def check_environment_variables():
    """Check all required environment variables"""
    print_header("🔍 CHECKING ENVIRONMENT VARIABLES")
    
    required_vars = {
        'TELEGRAM_BOT_TOKEN': {'sensitive': True, 'description': 'Telegram bot token'},
        'SUPABASE_URL': {'sensitive': False, 'description': 'Supabase project URL'},
        'SUPABASE_KEY': {'sensitive': True, 'description': 'Supabase anon key'},
        'SUPABASE_SERVICE_KEY': {'sensitive': True, 'description': 'Supabase service role key'},
        'POLYGON_RPC_URL': {'sensitive': True, 'description': 'Polygon RPC endpoint'},
        'WALLET_ENCRYPTION_KEY': {'sensitive': True, 'description': 'Fernet encryption key'},
        'CONWAY_API_URL': {'sensitive': False, 'description': 'Conway Cloud API URL'},
        'CONWAY_API_KEY': {'sensitive': True, 'description': 'Conway Cloud API key'},
        'ADMIN_IDS': {'sensitive': False, 'description': 'Admin Telegram IDs'},
    }
    
    optional_vars = {
        'POLYGON_USDT_CONTRACT': {'default': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'},
        'POLYGON_USDC_CONTRACT': {'default': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'},
        'ADMIN_USER_ID': {'default': '1187119989'},
    }
    
    missing = []
    present = []
    
    # Check required variables
    for var, config in required_vars.items():
        value = os.getenv(var)
        if value:
            if config['sensitive']:
                display = mask_sensitive_value(value)
            else:
                display = value
            print_success(f"{var}: {display}")
            present.append(var)
        else:
            print_error(f"{var}: MISSING - {config['description']}")
            missing.append(var)
    
    print()
    
    # Check optional variables
    print("📋 Optional variables (will use defaults if not set):")
    print()
    for var, config in optional_vars.items():
        value = os.getenv(var)
        if value:
            print_success(f"{var}: {value}")
        else:
            print_warning(f"{var}: Not set (will use default: {config['default']})")
    
    print()
    
    # Summary
    if missing:
        print_error(f"Missing {len(missing)} required variables:")
        for var in missing:
            print(f"   - {var}")
        return False
    else:
        print_success(f"All {len(required_vars)} required variables are set!")
        return True

def test_encryption_key():
    """Test wallet encryption key"""
    print_header("🔐 TESTING WALLET ENCRYPTION KEY")
    
    key = os.getenv('WALLET_ENCRYPTION_KEY')
    if not key:
        print_error("WALLET_ENCRYPTION_KEY not set!")
        return False
    
    try:
        # Test key format
        cipher = Fernet(key.encode())
        print_success("Encryption key format is valid")
        
        # Test encryption/decryption
        test_data = b"test_private_key_0x1234567890abcdef"
        encrypted = cipher.encrypt(test_data)
        print_success(f"Encryption test passed (encrypted length: {len(encrypted)} bytes)")
        
        decrypted = cipher.decrypt(encrypted)
        if decrypted == test_data:
            print_success("Decryption test passed")
        else:
            print_error("Decryption mismatch!")
            return False
        
        # Test with actual private key format
        test_pk = b"0x" + b"a" * 64  # Simulated private key
        encrypted_pk = cipher.encrypt(test_pk)
        decrypted_pk = cipher.decrypt(encrypted_pk)
        if decrypted_pk == test_pk:
            print_success("Private key encryption/decryption works correctly")
        else:
            print_error("Private key decryption failed!")
            return False
        
        print()
        print_success("Wallet encryption key is fully functional!")
        return True
        
    except Exception as e:
        print_error(f"Encryption key test failed: {e}")
        return False

def test_polygon_rpc():
    """Test Polygon RPC connection"""
    print_header("🔗 TESTING POLYGON RPC CONNECTION")
    
    rpc_url = os.getenv('POLYGON_RPC_URL')
    if not rpc_url:
        print_error("POLYGON_RPC_URL not set!")
        return False
    
    try:
        from web3 import Web3
        
        # Connect to Polygon
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Test connection
        if w3.is_connected():
            print_success("Connected to Polygon network")
        else:
            print_error("Failed to connect to Polygon network")
            return False
        
        # Get latest block
        latest_block = w3.eth.block_number
        print_success(f"Latest block number: {latest_block}")
        
        # Get chain ID (Polygon mainnet = 137)
        chain_id = w3.eth.chain_id
        if chain_id == 137:
            print_success(f"Chain ID: {chain_id} (Polygon Mainnet)")
        else:
            print_warning(f"Chain ID: {chain_id} (Not Polygon Mainnet)")
        
        print()
        print_success("Polygon RPC connection is working!")
        return True
        
    except ImportError:
        print_warning("web3 library not installed (pip install web3)")
        print_warning("Skipping RPC connection test")
        return True
    except Exception as e:
        print_error(f"RPC connection test failed: {e}")
        return False

def test_supabase_connection():
    """Test Supabase database connection"""
    print_header("🗄️  TESTING SUPABASE CONNECTION")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not url or not key:
        print_error("Supabase credentials not set!")
        return False
    
    try:
        from supabase import create_client
        
        # Create client
        supabase = create_client(url, key)
        print_success("Supabase client created")
        
        # Test connection by querying users table
        response = supabase.table('users').select('count', count='exact').limit(1).execute()
        print_success(f"Database connection successful")
        
        print()
        print_success("Supabase connection is working!")
        return True
        
    except ImportError:
        print_warning("supabase library not installed (pip install supabase)")
        print_warning("Skipping Supabase connection test")
        return True
    except Exception as e:
        print_error(f"Supabase connection test failed: {e}")
        return False

def test_admin_ids():
    """Test admin IDs configuration"""
    print_header("👤 TESTING ADMIN CONFIGURATION")
    
    admin_ids_str = os.getenv('ADMIN_IDS')
    if not admin_ids_str:
        print_error("ADMIN_IDS not set!")
        return False
    
    try:
        # Parse admin IDs
        admin_ids = [int(id.strip()) for id in admin_ids_str.split(',')]
        print_success(f"Found {len(admin_ids)} admin ID(s)")
        
        for i, admin_id in enumerate(admin_ids, 1):
            if admin_id > 0:
                print_success(f"Admin {i}: {admin_id}")
            else:
                print_error(f"Invalid admin ID: {admin_id}")
                return False
        
        print()
        print_success("Admin configuration is valid!")
        return True
        
    except Exception as e:
        print_error(f"Admin ID parsing failed: {e}")
        return False

def main():
    """Main test function"""
    print()
    print("=" * 70)
    print(f"{BLUE}🧪 AUTOMATON INTEGRATION - ENVIRONMENT TEST{RESET}")
    print("=" * 70)
    
    # Run all tests
    tests = [
        ("Environment Variables", check_environment_variables),
        ("Encryption Key", test_encryption_key),
        ("Admin Configuration", test_admin_ids),
        ("Polygon RPC", test_polygon_rpc),
        ("Supabase Connection", test_supabase_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Final summary
    print_header("📊 TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print()
    print("=" * 70)
    
    if passed == total:
        print_success(f"ALL TESTS PASSED ({passed}/{total})")
        print()
        print("✅ Your environment is ready for Automaton integration!")
        print()
        print("📝 Next steps:")
        print("   1. Run database migration: 001_automaton_tables.sql")
        print("   2. Deploy bot to Railway")
        print("   3. Test wallet generation")
        print("   4. Test deposit detection")
        print()
        return 0
    else:
        failed = total - passed
        print_error(f"SOME TESTS FAILED ({passed}/{total} passed, {failed} failed)")
        print()
        print("❌ Please fix the issues above before proceeding")
        print()
        print("📚 Documentation:")
        print("   - See RAILWAY_ENV_SETUP.md for setup instructions")
        print("   - Run: python generate_encryption_key.py (for encryption key)")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
