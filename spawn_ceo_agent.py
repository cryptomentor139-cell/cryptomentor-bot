"""
Spawn CEO Agent (AUTOMATON Induk) untuk CryptoMentor AI
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def spawn_ceo_agent():
    """Spawn CEO Agent via Conway API"""
    
    # Get API credentials
    api_key = os.getenv('CONWAY_API_KEY')
    api_url = os.getenv('CONWAY_API_URL', 'https://api.conway.tech')
    wallet_address = os.getenv('CONWAY_WALLET_ADDRESS')
    
    if not api_key:
        print("❌ CONWAY_API_KEY not found in .env!")
        return None
    
    if not wallet_address or wallet_address == "'0x0000000000000000000000000000000000000000'":
        print("⚠️  CONWAY_WALLET_ADDRESS not configured properly!")
        print("   Using default address for now...")
        wallet_address = "0x0000000000000000000000000000000000000000"
    
    print("🚀 Spawning CEO Agent...")
    print(f"   API URL: {api_url}")
    print(f"   Wallet: {wallet_address}")
    
    # Load system prompt
    try:
        with open('AUTOMATON_INDUK_PROMPT.md', 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        print(f"✅ Loaded system prompt ({len(system_prompt)} characters)")
    except FileNotFoundError:
        print("❌ AUTOMATON_INDUK_PROMPT.md not found!")
        return None
    
    # Prepare payload
    payload = {
        "name": "CryptoMentor CEO Agent",
        "description": "AI Agent CEO untuk mengelola dan mengembangkan bisnis CryptoMentor AI",
        "system_prompt": system_prompt,
        "model": "gpt-4-turbo",  # atau model lain yang didukung
        "temperature": 0.7,
        "max_tokens": 2000,
        "owner_wallet": wallet_address,
        "is_public": False,  # Private agent untuk internal use
        "capabilities": [
            "text_generation",
            "data_analysis",
            "scheduling",
            "notifications"
        ],
        "metadata": {
            "type": "induk",
            "role": "ceo",
            "company": "CryptoMentor AI",
            "language": "id",
            "version": "1.0.0"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Make API request
    try:
        print("\n📡 Sending request to Conway API...")
        response = requests.post(
            f"{api_url}/v1/agents",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 201:
            agent_data = response.json()
            agent_id = agent_data.get('agent_id') or agent_data.get('id')
            
            print("\n✅ CEO Agent spawned successfully!")
            print(f"   Agent ID: {agent_id}")
            print(f"   Name: {agent_data.get('name')}")
            print(f"   Type: AUTOMATON Induk")
            print(f"   Role: CEO")
            
            # Save agent ID to .env
            try:
                with open('.env', 'a', encoding='utf-8') as f:
                    f.write(f"\n# CEO Agent Configuration\n")
                    f.write(f"CEO_AGENT_ID={agent_id}\n")
                print("\n✅ Agent ID saved to .env")
            except Exception as e:
                print(f"\n⚠️  Could not save to .env: {e}")
                print(f"   Please manually add: CEO_AGENT_ID={agent_id}")
            
            return agent_id
            
        elif response.status_code == 401:
            print("\n❌ Authentication failed!")
            print("   Check your CONWAY_API_KEY in .env")
            return None
            
        elif response.status_code == 400:
            print("\n❌ Bad request!")
            print(f"   Response: {response.text}")
            return None
            
        else:
            print(f"\n❌ Failed to spawn CEO Agent!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timeout!")
        print("   Conway API might be slow or unavailable")
        return None
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error!")
        print("   Check your internet connection")
        print("   Or Conway API might be down")
        return None
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_ceo_agent(agent_id):
    """Test CEO Agent with a simple query"""
    
    api_key = os.getenv('CONWAY_API_KEY')
    api_url = os.getenv('CONWAY_API_URL', 'https://api.conway.tech')
    
    print("\n🧪 Testing CEO Agent...")
    
    test_prompt = """
    Halo! Saya user baru yang baru saja signup di CryptoMentor AI.
    Bisa jelaskan apa itu AUTOMATON dan bagaimana cara mulai?
    """
    
    payload = {
        "agent_id": agent_id,
        "message": test_prompt,
        "stream": False
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{api_url}/v1/agents/chat",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            agent_response = result.get('response') or result.get('message')
            
            print("\n✅ CEO Agent Response:")
            print("─" * 50)
            print(agent_response)
            print("─" * 50)
            return True
        else:
            print(f"\n❌ Test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  CEO AGENT SPAWNER - CRYPTOMENTOR AI")
    print("=" * 60)
    
    # Spawn CEO Agent
    agent_id = spawn_ceo_agent()
    
    if agent_id:
        print("\n" + "=" * 60)
        print("  SPAWN SUCCESSFUL!")
        print("=" * 60)
        
        # Ask if user wants to test
        test_input = input("\n🧪 Test CEO Agent now? (y/n): ").strip().lower()
        
        if test_input == 'y':
            test_ceo_agent(agent_id)
        
        print("\n" + "=" * 60)
        print("  NEXT STEPS:")
        print("=" * 60)
        print("1. ✅ CEO Agent ID saved to .env")
        print("2. 📝 Review CEO_AGENT_QUICK_REFERENCE.md for daily tasks")
        print("3. 🔧 Integrate with bot using CEO_AGENT_IMPLEMENTATION.md")
        print("4. 📊 Setup monitoring and analytics")
        print("5. 🚀 Start auto follow-up and daily reports")
        print("\n💡 Read CARA_PAKAI_CEO_AGENT.md for complete guide")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("  SPAWN FAILED!")
        print("=" * 60)
        print("\n🔍 Troubleshooting:")
        print("1. Check CONWAY_API_KEY in .env")
        print("2. Verify Conway API is accessible")
        print("3. Check AUTOMATON_INDUK_PROMPT.md exists")
        print("4. Review error messages above")
        print("\n📖 See CEO_AGENT_IMPLEMENTATION.md for help")
        print("=" * 60)
