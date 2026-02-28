#!/usr/bin/env python3
"""
Fix only the robot emoji that causes deployment error
"""

def fix_robot_emoji(filepath):
    """Replace problematic emojis with proper text"""
    print(f"Fixing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace problematic emojis - keep formatting intact
    replacements = {
        '🤖 ': '[AI] ',
        '💡 ': '[INFO] ',
        '⚠️ ': '[!] ',
        '💰 ': '[WALLET] ',
        '💵 ': '[MONEY] ',
        '📝 ': '[GUIDE] ',
        '📊 ': '[RATE] ',
        '🌐 ': '[NETWORK] ',
        '📚 ': '[DOCS] ',
        '❓ ': '[?] ',
        '🔙 ': '[<] ',
        '• ': '- ',  # Bullet point to dash
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
        'app/handlers_ai_agent_education.py'
    ]
    
    for filepath in files:
        try:
            fix_robot_emoji(filepath)
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
    
    print("\n✓ Robot emoji fixed!")
