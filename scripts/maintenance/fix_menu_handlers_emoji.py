#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix emoji encoding issues in menu_handlers.py
"""

def fix_menu_handlers():
    """Remove or replace problematic emojis in menu_handlers.py"""
    
    file_path = "menu_handlers.py"
    
    try:
        # Read file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Successfully read {file_path}")
        print(f"📊 File size: {len(content)} characters")
        
        # Replace problematic emojis with safe alternatives
        emoji_replacements = {
            '🎯': '🔹',  # Replace target emoji with diamond
            '🤖': '[AI]',  # Replace robot emoji
            '💰': '💵',  # Replace money bag
            '📊': '📈',  # Keep chart emoji
            '⚡': '⚡',  # Keep lightning
            '✅': '✓',  # Replace checkmark
            '❌': '✗',  # Replace cross
            '🔴': '🔴',  # Keep red circle
            '🟢': '🟢',  # Keep green circle
        }
        
        original_content = content
        
        for old_emoji, new_emoji in emoji_replacements.items():
            if old_emoji in content:
                count = content.count(old_emoji)
                content = content.replace(old_emoji, new_emoji)
                print(f"🔄 Replaced {count} instances of '{old_emoji}' with '{new_emoji}'")
        
        if content != original_content:
            # Write back with UTF-8 encoding
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n✅ Successfully fixed {file_path}")
            print(f"💾 File saved with UTF-8 encoding")
            return True
        else:
            print(f"\n⚠️ No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing file: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Fixing emoji encoding in menu_handlers.py")
    print("=" * 60)
    print()
    
    success = fix_menu_handlers()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Fix completed successfully!")
        print("🚀 You can now run the bot with: python bot.py")
    else:
        print("⚠️ Fix completed with warnings")
    print("=" * 60)
