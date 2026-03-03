#!/usr/bin/env python3
"""
Quick OpenClaw Gateway Test
Simple test to verify gateway is running
"""

import requests

def test_gateway():
    """Quick gateway health check"""
    gateway_url = "http://localhost:18789"
    
    print("🧪 Testing OpenClaw Gateway...")
    print(f"   URL: {gateway_url}")
    
    try:
        # Test health endpoint
        response = requests.get(f"{gateway_url}/health", timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Gateway is RUNNING!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return True
        else:
            print(f"   ⚠️ Gateway responded with: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Gateway is NOT running")
        print("\n📋 To start gateway:")
        print("   1. Open new terminal")
        print("   2. Run: start_openclaw_gateway.bat")
        print("   3. Wait for 'Gateway listening on port 18789'")
        print("   4. Run this test again")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_gateway()
    
    if success:
        print("\n✅ Gateway is ready!")
        print("\nNext: Run full test suite")
        print("   python test_openclaw_gateway.py")
    else:
        print("\n❌ Gateway not ready")
        print("\nStart gateway first:")
        print("   start_openclaw_gateway.bat")
