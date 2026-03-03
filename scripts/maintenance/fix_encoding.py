#!/usr/bin/env python3
"""
Fix encoding issues in menu_handlers.py
Remove invalid characters that cause crashes
"""

def fix_file_encoding(filepath):
    """Fix encoding issues in a file"""
    print(f"🔧 Fixing encoding in {filepath}...")
    
    try:
        # Read file in binary mode
        with open(filepath, 'rb') as f:
            data = f.read()
        
        # Decode with error handling - replace ALL invalid chars
        text = data.decode('utf-8', errors='ignore')  # Ignore instead of replace
        
        # Additional cleanup for any remaining problematic bytes
        # Remove all control characters except newline, tab, carriage return
        cleaned = ''
        for char in text:
            code = ord(char)
            # Keep: newline (10), tab (9), carriage return (13), and printable chars (32-126, 128+)
            if code in (9, 10, 13) or code >= 32:
                cleaned += char
        
        # Write back with explicit UTF-8 encoding
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(cleaned)
        
        print(f"✅ Fixed {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import os
    os.chdir('Bismillah')
    
    files_to_fix = [
        'menu_handlers.py',
        'app/handlers_ai_agent_education.py',
        'app/scheduler.py'
    ]
    
    for filepath in files_to_fix:
        fix_file_encoding(filepath)
    
    print("\n✅ All files fixed!")
