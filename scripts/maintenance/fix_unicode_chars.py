#!/usr/bin/env python3
"""
Fix unicode characters in menu_handlers.py that cause deployment errors
Replace problematic emojis and unicode chars with ASCII equivalents
"""

def fix_unicode_in_file(filepath):
    """Replace problematic unicode characters with ASCII equivalents"""
    print(f"Fixing unicode in {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace problematic emojis and unicode chars
    replacements = {
        '🤖': '[AI]',
        '💡': '[INFO]',
        '⚠️': '[!]',
        '💰': '[WALLET]',
        '💵': '[MONEY]',
        '📝': '[GUIDE]',
        '📊': '[RATE]',
        '🌐': '[NETWORK]',
        '•': '-',  # Bullet point
        '✅': '[OK]',
        '❌': '[X]',
        '🎯': '[TARGET]',
        '🔒': '[LOCK]',
        '📖': '[DOCS]',
        '❓': '[?]',
        '🔙': '[BACK]',
        '👑': '[PREMIUM]',
        '🏠': '[HOME]',
        '⭐': '[STAR]',
        '🔄': '[REFRESH]',
        '⏳': '[WAIT]',
        '🚀': '[ROCKET]',
        '⏹️': '[STOP]',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed {filepath}")

if __name__ == "__main__":
    import os
    os.chdir('Bismillah')
    
    files = [
        'menu_handlers.py',
        'app/handlers_ai_agent_education.py',
        'app/scheduler.py'
    ]
    
    for filepath in files:
        try:
            fix_unicode_in_file(filepath)
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
    
    print("\n✓ All files fixed!")
