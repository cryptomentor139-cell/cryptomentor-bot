#!/usr/bin/env python3
"""
Fix all OpenClaw database issues:
1. Change db.cursor() to db.cursor (property, not method)
2. Change PostgreSQL %s to SQLite ?
"""

import re
import os

files_to_fix = [
    'app/openclaw_user_credits.py',
    'app/openclaw_chat_monitor.py',
    'app/handlers_openclaw_deposit.py',
    'app/handlers_openclaw_admin_credits.py',
    'app/handlers_openclaw_admin.py'
]

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f"⚠️ File not found: {filepath}")
        continue
    
    print(f"🔧 Fixing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix 1: Change db.cursor() to db.cursor
    content = content.replace('cursor = db.cursor()', 'cursor = db.cursor  # Property, not method')
    
    # Fix 2: Change PostgreSQL %s to SQLite ? in SQL queries
    # This is tricky - we need to replace %s only in SQL strings, not in Python format strings
    
    # Pattern: Find SQL execute statements and replace %s with ?
    def replace_sql_placeholders(match):
        sql_block = match.group(0)
        # Replace %s with ? in this SQL block
        sql_block = sql_block.replace('%s', '?')
        return sql_block
    
    # Match cursor.execute(""" ... """, (...)) blocks
    pattern = r'cursor\.execute\s*\(\s*""".*?"""\s*,\s*\([^)]*\)\s*\)'
    content = re.sub(pattern, replace_sql_placeholders, content, flags=re.DOTALL)
    
    # Match cursor.execute("...", (...)) blocks (single quotes)
    pattern = r'cursor\.execute\s*\(\s*"[^"]*"\s*,\s*\([^)]*\)\s*\)'
    content = re.sub(pattern, replace_sql_placeholders, content, flags=re.DOTALL)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed {filepath}")
    else:
        print(f"ℹ️ No changes needed for {filepath}")

print("\n✅ All files processed!")
print("\n⚠️ IMPORTANT: Review changes before committing!")
print("Run: git diff")
