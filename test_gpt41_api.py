#!/usr/bin/env python3
"""
Test GPT-4.1 API via OpenRouter
Quick test to verify API key and model are working
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter_api():
    """Test OpenRouter API with GPT-4.1"""
    
    api_key = os.getenv('OPENCLAW_API_KEY')
    base_url = os.getenv('OPENCLAW_BASE_URL', 'https://openrouter.ai/api/v1')
    
    print("=" * 60)
    print("🧪 Testing GPT-4.1 API via OpenRouter")
    print("=" * 60)
    
    # Check API key
    if not api_key:
        print("❌ ERROR: OPENCLAW_API_KEY not found in .env")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...{api_key[-10:]}")
    print(f"✅ Base URL: {base_url}")
    print()
    
    # Test 1: Check API key validity
    print("📡 Test 1: Checking API key validity...")
    try:
        auth_response = requests.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        
        if auth_response.status_code == 200:
            data = auth_response.json()
            print(f"✅ API Key is VALID")
            print(f"   - Label: {data.get('data', {}).get('label', 'N/A')}")
            print(f"   - Limit: ${data.get('data', {}).get('limit', 'N/A')}")
            print(f"   - Usage: ${data.get('data', {}).get('usage', 'N/A')}")
        else:
            print(f"❌ API Key validation failed: {auth_response.status_code}")
            print(f"   Response: {auth_response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ Error checking API key: {e}")
        return False
    
    print()
    
    # Test 2: Send test message to GPT-4.1
    print("📡 Test 2: Sending test message to GPT-4.1...")
    try:
        chat_response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4.1",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello! Please respond with a short greeting about crypto trading."
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if chat_response.status_code == 200:
            data = chat_response.json()
            response_text = data['choices'][0]['message']['content']
            usage = data.get('usage', {})
            
            print(f"✅ GPT-4.1 Response received!")
            print(f"\n📝 Response:")
            print(f"   {response_text}")
            print(f"\n📊 Token Usage:")
            print(f"   - Input tokens: {usage.get('prompt_tokens', 0)}")
            print(f"   - Output tokens: {usage.get('completion_tokens', 0)}")
            print(f"   - Total tokens: {usage.get('total_tokens', 0)}")
            
            # Calculate cost
            input_cost = usage.get('prompt_tokens', 0) * (2.5 / 1_000_000)
            output_cost = usage.get('completion_tokens', 0) * (10.0 / 1_000_000)
            total_cost = input_cost + output_cost
            
            print(f"\n💰 Estimated Cost:")
            print(f"   - Input: ${input_cost:.6f}")
            print(f"   - Output: ${output_cost:.6f}")
            print(f"   - Total: ${total_cost:.6f}")
            
        else:
            print(f"❌ Chat request failed: {chat_response.status_code}")
            print(f"   Response: {chat_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending chat request: {e}")
        return False
    
    print()
    print("=" * 60)
    print("✅ ALL TESTS PASSED! GPT-4.1 is working correctly!")
    print("=" * 60)
    
    return True

def test_alternative_models():
    """Test alternative free models"""
    
    api_key = os.getenv('OPENCLAW_API_KEY')
    base_url = os.getenv('OPENCLAW_BASE_URL', 'https://openrouter.ai/api/v1')
    
    print("\n" + "=" * 60)
    print("🧪 Testing Alternative Free Models")
    print("=" * 60)
    
    models = [
        "google/gemini-flash-1.5",
        "meta-llama/llama-3.2-3b-instruct:free"
    ]
    
    for model in models:
        print(f"\n📡 Testing {model}...")
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Say hello in 5 words"}
                    ],
                    "max_tokens": 50
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data['choices'][0]['message']['content']
                print(f"✅ {model}: {text}")
            else:
                print(f"❌ {model}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {model}: Error - {e}")

if __name__ == "__main__":
    print("\n🚀 Starting GPT-4.1 API Test...\n")
    
    success = test_openrouter_api()
    
    if success:
        # Test alternative models
        test_alternative_models()
    
    print("\n✅ Test complete!\n")
