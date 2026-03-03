"""
Test OpenRouter API Key
Check if the API key is valid and can access GPT-4.1
"""

import os
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_openrouter_key():
    """Test OpenRouter API key"""
    print("=" * 60)
    print("OpenRouter API Key Test")
    print("=" * 60)
    
    # Get API key
    api_key = os.getenv('OPENCLAW_API_KEY')
    
    if not api_key:
        print("❌ OPENCLAW_API_KEY not found in .env")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...{api_key[-10:]}")
    print(f"   Length: {len(api_key)} characters")
    
    # Test API key with a simple request
    print("\n🧪 Testing API key with OpenRouter...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://cryptomentor.ai',
        'X-Title': 'CryptoMentor OpenClaw Test'
    }
    
    payload = {
        'model': 'openai/gpt-4.1',
        'messages': [
            {'role': 'user', 'content': 'Say "Hello" if you can hear me'}
        ],
        'max_tokens': 50
    }
    
    try:
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            message = data['choices'][0]['message']['content']
            tokens = data['usage']['total_tokens']
            
            print(f"✅ API Key is VALID!")
            print(f"✅ Model: openai/gpt-4.1")
            print(f"✅ Response: {message}")
            print(f"✅ Tokens used: {tokens}")
            return True
        else:
            print(f"❌ API Key is INVALID or has issues")
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Response: {response.text}")
            
            # Parse error
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"\n🔍 Error Details:")
                    print(f"   Message: {error_data['error'].get('message', 'N/A')}")
                    print(f"   Code: {error_data['error'].get('code', 'N/A')}")
            except:
                pass
            
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def check_openrouter_credits():
    """Check OpenRouter account credits"""
    print("\n" + "=" * 60)
    print("OpenRouter Account Credits Check")
    print("=" * 60)
    
    api_key = os.getenv('OPENCLAW_API_KEY')
    
    if not api_key:
        print("❌ API key not found")
        return
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        # Check credits endpoint
        response = requests.get(
            'https://openrouter.ai/api/v1/auth/key',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Account Info:")
            print(f"   Label: {data.get('data', {}).get('label', 'N/A')}")
            print(f"   Limit: ${data.get('data', {}).get('limit', 'N/A')}")
            print(f"   Usage: ${data.get('data', {}).get('usage', 'N/A')}")
            print(f"   Is Free Tier: {data.get('data', {}).get('is_free_tier', 'N/A')}")
        else:
            print(f"❌ Could not fetch account info: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error checking credits: {e}")

def main():
    """Run all tests"""
    success = test_openrouter_key()
    
    if success:
        check_openrouter_credits()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ OpenRouter API Key is working!")
        print("✅ GPT-4.1 model is accessible")
        print("\n📝 Next steps:")
        print("1. Make sure Railway has the same API key")
        print("2. Restart Railway deployment")
        print("3. Test bot in Telegram")
    else:
        print("❌ OpenRouter API Key has issues!")
        print("\n📝 Solutions:")
        print("1. Check if API key is correct")
        print("2. Verify OpenRouter account is active")
        print("3. Check if you have credits/balance")
        print("4. Get new API key from: https://openrouter.ai/keys")
    print("=" * 60)

if __name__ == "__main__":
    main()
