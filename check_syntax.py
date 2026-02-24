#!/usr/bin/env python3
import sys
import py_compile
import os

os.chdir('Bismillah')

try:
    py_compile.compile('menu_handlers.py', doraise=True)
    print("✓ menu_handlers.py syntax OK")
except SyntaxError as e:
    print(f"✗ Syntax error in menu_handlers.py:")
    print(f"  Line {e.lineno}: {e.msg}")
    print(f"  Text: {e.text}")
    print(f"  Offset: {e.offset}")
    
    # Show context
    with open('menu_handlers.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        print(f"\n  Context (lines {start+1}-{end}):")
        for i in range(start, end):
            marker = ">>>" if i == e.lineno - 1 else "   "
            print(f"  {marker} {i+1}: {lines[i].rstrip()}")
