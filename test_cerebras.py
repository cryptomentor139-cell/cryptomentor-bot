#!/usr/bin/env python3
"""
Test Cerebras API - Ultra Fast LLM
"""
import os
import time
from openai import OpenAI

def test_cerebras():
    """Test Cerebras API speed and quality"""
    
    # Get API key from environment
    api_key = os.getenv('CEREBRAS_API_KEY')
    
    if not api_key:
        print("❌ CEREBRAS_API_KEY not found in environment")
        print("\n📝 Setup:")
        print("1. Get API key from: https://cloud.cerebras.ai/")
        print("2. Add to .env file:")
        print("   CEREBRAS_API_KEY=your_api_key_here")
        return False
    
    print("🧪 Testing Cerebras API...")
    print("=" * 60)
    
    try:
        # Initialize Cerebras client (OpenAI-compatible)
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.cerebras.ai/v1"
        )
        
        # Test 1: Simple chat
        print("\n📊 Test 1: Simple Chat")
        print("-" * 60)
        
        start_time = time.time()
        
        response = client.chat.completions.create(
            model="llama3.1-8b",  # Cerebras Llama 3.1 8B (faster, free tier)
            messages=[
                {"role": "system", "content": "You are a helpful crypto trading assistant."},
                {"role": "user", "content": "Explain Bitcoin in 2 sentences."}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        elapsed = time.time() - start_time
        
        answer = response.choices[0].message.content
        
        print(f"⏱️ Response time: {elapsed:.2f} seconds")
        print(f"📝 Answer: {answer}")
        print(f"✅ Status: {'FAST' if elapsed < 2 else 'SLOW'}")
        
        # Test 2: Market analysis (crypto-specific)
        print("\n\n📊 Test 2: Crypto Market Analysis")
        print("-" * 60)
        
        start_time = time.time()
        
        response = client.chat.completions.create(
            model="llama3.1-8b",
            messages=[
                {"role": "system", "content": "You are an expert crypto analyst. Provide concise analysis."},
                {"role": "user", "content": "BTC price: $68,000. RSI: 55. Volume: High. Market bias?"}
            ],
            max_tokens=150,
            temperature=0.5
        )
        
        elapsed = time.time() - start_time
        
        analysis = response.choices[0].message.content
        
        print(f"⏱️ Response time: {elapsed:.2f} seconds")
        print(f"📝 Analysis: {analysis}")
        print(f"✅ Status: {'FAST' if elapsed < 2 else 'SLOW'}")
        
        # Test 3: Speed test (multiple requests)
        print("\n\n📊 Test 3: Speed Test (5 requests)")
        print("-" * 60)
        
        times = []
        for i in range(5):
            start_time = time.time()
            
            response = client.chat.completions.create(
                model="llama3.1-8b",
                messages=[
                    {"role": "user", "content": f"Quick test {i+1}"}
                ],
                max_tokens=50
            )
            
            elapsed = time.time() - start_time
            times.append(elapsed)
            print(f"Request {i+1}: {elapsed:.2f}s")
        
        avg_time = sum(times) / len(times)
        print(f"\n⏱️ Average response time: {avg_time:.2f} seconds")
        print(f"✅ Status: {'EXCELLENT' if avg_time < 1 else 'GOOD' if avg_time < 2 else 'SLOW'}")
        
        # Summary
        print("\n\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"✅ API Key: Valid")
        print(f"✅ Model: llama3.1-8b")
        print(f"✅ Average Speed: {avg_time:.2f}s")
        print(f"✅ Quality: Good (Llama 3.1 8B)")
        
        if avg_time < 2:
            print("\n🎉 EXCELLENT! Cerebras is MUCH faster than DeepSeek!")
            print("💡 Recommended for production use")
        else:
            print("\n⚠️ Slower than expected. Check network connection.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check API key is correct")
        print("2. Check internet connection")
        print("3. Check Cerebras service status")
        return False

if __name__ == "__main__":
    # Load .env
    from dotenv import load_dotenv
    load_dotenv()
    
    success = test_cerebras()
    exit(0 if success else 1)
