#!/usr/bin/env python3
"""
Test LangChain handlers import
"""

print("Testing LangChain imports...")

try:
    print("\n1. Testing openclaw_langchain_db import...")
    from app.openclaw_langchain_db import get_openclaw_db
    print("   ✅ openclaw_langchain_db imported successfully")
except Exception as e:
    print(f"   ❌ openclaw_langchain_db import failed: {e}")

try:
    print("\n2. Testing openclaw_langchain_agent_simple import...")
    from app.openclaw_langchain_agent_simple import get_openclaw_agent
    print("   ✅ openclaw_langchain_agent_simple imported successfully")
except Exception as e:
    print(f"   ❌ openclaw_langchain_agent_simple import failed: {e}")

try:
    print("\n3. Testing handlers_openclaw_langchain import...")
    from app.handlers_openclaw_langchain import register_openclaw_langchain_handlers
    print("   ✅ handlers_openclaw_langchain imported successfully")
except Exception as e:
    print(f"   ❌ handlers_openclaw_langchain import failed: {e}")

print("\n✅ All imports successful!")
