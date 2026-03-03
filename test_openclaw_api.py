#!/usr/bin/env python3
"""
Test OpenClaw GPT-4.1 API Connection
Quick test to verify API key works
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openclaw_api():
    """Test OpenClaw API connection"""
    print("🧪 Testing OpenClaw GPT-4.1 API Connection")
    print("=" * 60)
    
    # Get API key
    api_key = os.getenv('OPENCLAW_API_KEY') or os.getenv('DEEPSEEK_API_KEY')
    base_url = os.getenv('OPENCLAW_BASE_URL', 'https://openrouter.ai/api/v1')
    
    if not api_key:
        print("❌ Error: No API key found!")
        print("   Set OPENCLAW_API_KEY or DEEPSEEK_API_KEY in .env")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    print(f"✅ Base URL: {base_url}")
    print()
    
    # Test API call
    print("📡 Sending test request to GPT-4.1...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://cryptomentor.ai',
        'X-Title': 'CryptoMentor OpenClaw Test'
    }
    
    payload = {
        'model': 'openai/gpt-4.1',
        'messages': [
            {
                'role': 'system',
                'content': 'You are a helpful AI assistant. Respond concisely.'
            },
            {
                'role': 'user',
                'content': 'Say "Hello! OpenClaw is working!" in one sentence.'
            }
        ],
        'max_tokens': 50
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract response
            ai_response = data['choices'][0]['message']['content']
            input_tokens = data['usage']['prompt_tokens']
            output_tokens = data['usage']['completion_tokens']
            total_tokens = data['usage']['total_tokens']
            
            print()
            print("✅ SUCCESS! API is working!")
            print("=" * 60)
            print(f"🤖 AI Response: {ai_response}")
            print()
            print(f"📊 Token Usage:")
            print(f"   Input: {input_tokens} tokens")
            print(f"   Output: {output_tokens} tokens")
            print(f"   Total: {total_tokens} tokens")
            print()
            
            # Calculate cost
            input_cost = input_tokens * (2.5 / 1_000_000)
            output_cost = output_tokens * (10.0 / 1_000_000)
            total_cost = input_cost + output_cost
            credits_cost = int(total_cost * 100)
            
            print(f"💰 Cost Calculation:")
            print(f"   Input: ${input_cost:.6f}")
            print(f"   Output: ${output_cost:.6f}")
            print(f"   Total: ${total_cost:.6f}")
            print(f"   Credits: {credits_cost} credits")
            print()
            print("=" * 60)
            print("🎉 OpenClaw is ready to use!")
            print()
            print("Next steps:")
            print("1. Run migration: python3 run_openclaw_migration.py")
            print("2. Start bot: python3 bot.py")
            print("3. Test in Telegram: /openclaw_create MyBot friendly")
            
            return True
            
        else:
            print()
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            print()
            
            if response.status_code == 401:
                print("💡 Tip: Check your API key is correct")
            elif response.status_code == 402:
                print("💡 Tip: Check your OpenRouter account has credits")
            elif response.status_code == 429:
                print("💡 Tip: Rate limit exceeded, wait a moment")
            
            return False
            
    except requests.exceptions.Timeout:
        print()
        print("❌ Request timeout!")
        print("💡 Tip: Check your internet connection")
        return False
        
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    try:
        success = test_openclaw_api()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user")
        exit(1)
