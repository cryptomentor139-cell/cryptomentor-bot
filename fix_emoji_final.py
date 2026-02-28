#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final fix for emoji issue - replace robot emoji with [AI]
"""
import os
import sys

def fix_file(filepath):
    """Replace robot emoji in file"""
    print(f"Fixing {filepath}...")
    
    try:
        # Read as binary to avoid encoding issues
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Replace robot emoji bytes (UTF-8 encoding of 🤖)
        # 🤖 = \xf0\x9f\xa4\x96
        robot_emoji_bytes = b'\xf0\x9f\xa4\x96'
        replacement_bytes = b'[AI]'
        
        # Also replace other problematic emojis
        replacements = {
            b'\xf0\x9f\xa4\x96': b'[AI]',      # 🤖
            b'\xf0\x9f\x92\xa1': b'',          # 💡 (bulb)
            b'\xe2\x9a\xa0\xef\xb8\x8f': b'[!]',  # ⚠️
            b'\xf0\x9f\x92\xb0': b'',          # 💰
            b'\xf0\x9f\x92\xb5': b'',          # 💵
            b'\xf0\x9f\x93\x9d': b'',          # 📝
            b'\xf0\x9f\x93\x8a': b'',          # 📊
            b'\xf0\x9f\x8c\x90': b'',          # 🌐
            b'\xf0\x9f\x93\x9a': b'',          # 📚
            b'\xe2\x9d\x93': b'[?]',           # ❓
            b'\xf0\x9f\x94\x99': b'[<]',       # 🔙
        }
        
        modified = False
        for old_bytes, new_bytes in replacements.items():
            if old_bytes in content:
                content = content.replace(old_bytes, new_bytes)
                modified = True
        
        if modified:
            
            # Write back
            with open(filepath, 'wb') as f:
                f.write(content)
            
            print(f"  ✓ Fixed {filepath}")
            return True
        else:
            print(f"  - No robot emoji found in {filepath}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

if __name__ == "__main__":
    os.chdir('Bismillah')
    
    # Critical files that cause bot crash
    critical_files = [
        'menu_handlers.py',
        'app/handlers_ai_agent_education.py',
        'menu_system.py'
    ]
    
    fixed_count = 0
    for filepath in critical_files:
        if os.path.exists(filepath):
            if fix_file(filepath):
                fixed_count += 1
        else:
            print(f"  ! File not found: {filepath}")
    
    print(f"\n✓ Fixed {fixed_count} files")
    print("\nNow compile to verify:")
    print("  python -m py_compile menu_handlers.py")
