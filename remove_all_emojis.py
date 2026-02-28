#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove ALL emojis from Python files to fix deployment
"""
import os
import re

def remove_emojis_from_file(filepath):
    """Remove all emoji characters from file"""
    print(f"Processing {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex to match all emoji characters AND bullet points
        # This matches most emoji ranges in Unicode
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\u2600-\u26FF"          # Miscellaneous Symbols
            "\u2700-\u27BF"          # Dingbats
            "\u2022"                 # Bullet point
            "]+", 
            flags=re.UNICODE
        )
        
        # Remove emojis
        cleaned = emoji_pattern.sub('', content)
        
        if cleaned != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            print(f"  ✓ Removed emojis from {filepath}")
            return True
        else:
            print(f"  - No emojis found in {filepath}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

if __name__ == "__main__":
    os.chdir('Bismillah')
    
    files = [
        'menu_handlers.py',
        'app/handlers_ai_agent_education.py',
        'menu_system.py'
    ]
    
    for filepath in files:
        if os.path.exists(filepath):
            remove_emojis_from_file(filepath)
        else:
            print(f"! File not found: {filepath}")
    
    print("\n✓ Done! Now test compile:")
    print("  python -m py_compile menu_handlers.py")
