#!/usr/bin/env python3
"""
Test script to debug Conway API key loading issue
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*60)
print("CONWAY API KEY DEBUG TEST")
print("="*60)

# Test 1: Check current directory
print("\n1. Current Directory:")
print(f"   {os.getcwd()}")

# Test 2: Check if .env file exists
env_file = Path('.env')
print(f"\n2. .env File Check:")
print(f"   Exists: {env_file.exists()}")
if env_file.exists():
    print(f"   Path: {env_file.absolute()}")

# Test 3: Try to load .env manually
print(f"\n3. Loading .env file...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("   ✅ .env loaded successfully")
except ImportError:
    print("   ❌ python-dotenv not installed!")
    print("   Run: pip install python-dotenv")
except Exception as e:
    print(f"   ❌ Error loading .env: {e}")

# Test 4: Check environment variables
print(f"\n4. Environment Variables:")
conway_key = os.getenv('CONWAY_API_KEY')
conway_url = os.getenv('CONWAY_API_URL')

if conway_key:
    # Mask the key for security
    masked_key = conway_key[:10] + "..." + conway_key[-4:] if len(conway_key) > 14 else "***"
    print(f"   CONWAY_API_KEY: {masked_key} ✅")
else:
    print(f"   CONWAY_API_KEY: NOT FOUND ❌")

if conway_url:
    print(f"   CONWAY_API_URL: {conway_url} ✅")
else:
    print(f"   CONWAY_API_URL: NOT FOUND (will use default)")

# Test 5: Try to initialize Conway client
print(f"\n5. Conway Client Initialization:")
try:
    from app.conway_integration import ConwayIntegration
    client = ConwayIntegration()
    print("   ✅ Conway client initialized successfully")
    
    # Test 6: Health check
    print(f"\n6. Conway API Health Check:")
    is_healthy = client.health_check()
    if is_healthy:
        print("   ✅ Conway API is healthy")
    else:
        print("   ❌ Conway API health check failed")
        
except ValueError as e:
    print(f"   ❌ {e}")
    print("\n   SOLUTION:")
    print("   1. Make sure .env file exists in Bismillah/ directory")
    print("   2. Add this line to .env:")
    print("      CONWAY_API_KEY=your_api_key_here")
    print("   3. Run this script again")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("DEBUG TEST COMPLETE")
print("="*60)
