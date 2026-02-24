#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify all Python files have no syntax errors
"""

import os
import py_compile
import sys

def verify_python_files():
    """Check all Python files for syntax errors"""
    
    errors = []
    success = []
    
    # Key files to check
    key_files = [
        'bot.py',
        'menu_handlers.py',
        'menu_system.py',
        'database.py',
        'ai_assistant.py',
        'crypto_api.py',
        'app/handlers_automaton.py',
        'app/handlers_admin_credits.py',
        'app/handlers_ai_agent_education.py',
    ]
    
    print("=" * 60)
    print("🔍 Verifying Python syntax...")
    print("=" * 60)
    print()
    
    for file_path in key_files:
        if not os.path.exists(file_path):
            print(f"⚠️  {file_path} - NOT FOUND")
            continue
            
        try:
            py_compile.compile(file_path, doraise=True)
            print(f"✅ {file_path} - OK")
            success.append(file_path)
        except py_compile.PyCompileError as e:
            print(f"❌ {file_path} - SYNTAX ERROR")
            print(f"   {e}")
            errors.append((file_path, str(e)))
        except Exception as e:
            print(f"⚠️  {file_path} - ERROR: {e}")
            errors.append((file_path, str(e)))
    
    print()
    print("=" * 60)
    print(f"✅ Success: {len(success)} files")
    print(f"❌ Errors: {len(errors)} files")
    print("=" * 60)
    
    if errors:
        print()
        print("❌ Files with errors:")
        for file_path, error in errors:
            print(f"  - {file_path}")
            print(f"    {error[:100]}")
        return False
    else:
        print()
        print("✅ All files verified successfully!")
        print("🚀 Bot is ready to run!")
        return True

if __name__ == "__main__":
    success = verify_python_files()
    sys.exit(0 if success else 1)
