#!/usr/bin/env python3
"""
Test script untuk verifikasi branding update V3.0
"""

import re
from pathlib import Path

def test_branding_update():
    """Test apakah semua branding sudah diupdate ke V3.0"""
    
    print("🔍 Testing Branding Update to V3.0...\n")
    
    files_to_check = {
        'bot.py': [
            ('Welcome message', r'Welcome to CryptoMentor AI 3\.0'),
            ('Subscribe command', r'CryptoMentor AI 3\.0 – Paket Berlangganan'),
            ('Admin panel', r'CryptoMentorAI V3\.0.*Admin Panel'),
        ],
        'menu_system.py': [
            ('Header comment', r'CryptoMentor AI 3\.0 - Button-Based Menu System'),
            ('Main menu ID', r'CryptoMentor AI 3\.0'),
            ('Main menu EN', r'CryptoMentor AI 3\.0'),
        ],
        'menu_handlers.py': [
            ('Header comment', r'CryptoMentor AI 3\.0 - Menu Callback Handlers'),
        ],
        'menu_handler.py': [
            ('Subscribe text', r'CryptoMentor AI 3\.0 – Paket Berlangganan'),
        ],
        'futures_signal_generator.py': [
            ('Header comment', r'CryptoMentor AI 3\.0 format'),
            ('Signal format', r'CRYPTOMENTOR AI 3\.0 – TRADING SIGNAL'),
            ('Generate signal docstring', r'CryptoMentor AI 3\.0 format'),
        ],
        'app/handlers_automaton.py': [
            ('Automaton price', r'Rp2\.300\.000'),
        ],
        'app/automaton_manager.py': [
            ('Automaton price', r'Rp2,300,000'),
        ],
    }
    
    results = []
    base_path = Path('.')  # Current directory is already Bismillah
    
    for filename, patterns in files_to_check.items():
        filepath = base_path / filename
        
        if not filepath.exists():
            print(f"❌ File not found: {filename}")
            results.append(False)
            continue
            
        content = filepath.read_text(encoding='utf-8')
        
        print(f"📄 Checking {filename}...")
        for description, pattern in patterns:
            if re.search(pattern, content):
                print(f"   ✅ {description}")
                results.append(True)
            else:
                print(f"   ❌ {description} - Pattern not found: {pattern}")
                results.append(False)
        print()
    
    return all(results)

def test_pricing_update():
    """Test apakah semua harga sudah diupdate dengan kenaikan 15%"""
    
    print("\n💰 Testing Pricing Update (15% increase)...\n")
    
    expected_prices = {
        'Monthly': 'Rp368.000',
        '2 Bulan': 'Rp690.000',
        '1 Tahun': 'Rp4.025.000',
        'Lifetime': 'Rp7.475.000',
        'Automaton': 'Rp2.300.000',
    }
    
    bot_file = Path('bot.py')  # Current directory is already Bismillah
    
    if not bot_file.exists():
        print("❌ bot.py not found")
        return False
    
    content = bot_file.read_text(encoding='utf-8')
    
    results = []
    for package, price in expected_prices.items():
        if price in content:
            print(f"✅ {package}: {price}")
            results.append(True)
        else:
            print(f"❌ {package}: {price} not found")
            results.append(False)
    
    return all(results)

def test_no_old_branding():
    """Test apakah masih ada branding lama yang tertinggal"""
    
    print("\n🔍 Checking for old branding (V2.0)...\n")
    
    files_to_check = [
        'bot.py',
        'menu_system.py',
        'menu_handlers.py',
        'menu_handler.py',
        'futures_signal_generator.py',
    ]
    
    base_path = Path('.')  # Current directory is already Bismillah
    old_patterns = [
        r'CryptoMentor AI 2\.0',
        r'CRYPTOMENTOR AI 2\.0',
        r'CryptoMentorAI V2\.0',
    ]
    
    found_old = False
    
    for filename in files_to_check:
        filepath = base_path / filename
        
        if not filepath.exists():
            continue
            
        content = filepath.read_text(encoding='utf-8')
        
        for pattern in old_patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"⚠️  Found old branding in {filename}: {matches[0]}")
                found_old = True
    
    if not found_old:
        print("✅ No old branding found!")
        return True
    else:
        print("\n❌ Old branding still exists in some files")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 CryptoMentor AI V3.0 Branding Update Test")
    print("=" * 60)
    
    test1 = test_branding_update()
    test2 = test_pricing_update()
    test3 = test_no_old_branding()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"Branding Update: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Pricing Update: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"No Old Branding: {'✅ PASS' if test3 else '❌ FAIL'}")
    print("=" * 60)
    
    if test1 and test2 and test3:
        print("\n🎉 ALL TESTS PASSED! Ready to deploy V3.0")
        exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED! Please review the changes")
        exit(1)
