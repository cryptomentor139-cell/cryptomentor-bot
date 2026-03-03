#!/usr/bin/env python3
"""Fix admin button URL to point to @BillFarr"""

import re

with open('menu_handlers.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Pattern to match the admin contact section
pattern = r'# Get admin contact\s+admin_ids_str = os\.getenv\(\'ADMIN_IDS\', \'\'\)\s+admin_contact = ""\s+if admin_ids_str:\s+first_admin_id = admin_ids_str\.split\(\',\'\)\[0\]\.strip\(\)\s+admin_contact = f"tg://user\?id=\{first_admin_id\}"\s+keyboard = \[\s+\[InlineKeyboardButton\([^,]+, \s+url=admin_contact if admin_contact else "https://t\.me/"\)'

# Replacement - just the keyboard line with direct URL
replacement = '''keyboard = [
                    [InlineKeyboardButton("📤 Kirim Bukti ke Admin" if user_lang == 'id' else "📤 Send Proof to Admin", 
                                         url="https://t.me/BillFarr")'''

content_new = re.sub(pattern, replacement, content, flags=re.DOTALL, count=1)

if content_new != content:
    with open('menu_handlers.py', 'w', encoding='utf-8') as f:
        f.write(content_new)
    print("✅ Fixed admin button URL to @BillFarr")
else:
    print("❌ Pattern not found, trying alternative approach...")
    
    # Alternative: find and replace just the URL line
    content_new = re.sub(
        r'url=admin_contact if admin_contact else "https://t\.me/"',
        'url="https://t.me/BillFarr"',
        content,
        count=1
    )
    
    if content_new != content:
        with open('menu_handlers.py', 'w', encoding='utf-8') as f:
            f.write(content_new)
        print("✅ Fixed admin button URL using alternative method")
    else:
        print("❌ Could not find pattern to replace")
