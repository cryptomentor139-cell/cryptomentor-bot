#!/usr/bin/env python3
"""
Fix OpenClaw cursor usage - replace self.cursor with local cursor
"""

import re

# Read the file
with open('app/openclaw_manager.py', 'r', encoding='utf-8') as f:
    content = f.content()

# Replace all self.cursor with cursor
content = content.replace('self.cursor', 'cursor')

# Replace PostgreSQL %s with SQLite ?
content = content.replace('"%s"', '"?"')
content = content.replace("'%s'", "'?'")
content = re.sub(r'%s(?=[,\)])', '?', content)

# Write back
with open('app/openclaw_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed cursor usage in openclaw_manager.py")
print("⚠️ Manual review needed: Add 'cursor = self._get_cursor()' at start of methods")
print("⚠️ Manual review needed: Add 'cursor.close()' before returns")
