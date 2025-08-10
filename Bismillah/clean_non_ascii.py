
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script untuk membersihkan karakter non-ASCII dari semua file Python
"""

import os
import ast
import json
import shutil
from pathlib import Path

def get_ascii_replacement_map():
    """Mapping karakter non-ASCII ke ASCII equivalent"""
    return {
        # Emoji status
        '✅': '[OK]',
        '✔': '[OK]',
        '✓': '[OK]',
        '❌': '[ERR]',
        '✖': '[ERR]',
        '⚠': '[WARN]',
        '⚠️': '[WARN]',
        '🚀': '[START]',
        '🔧': '[TOOL]',
        '🔍': '[SCAN]',
        '📊': '[STAT]',
        '📅': '[DATE]',
        '🤖': '[BOT]',
        '🎯': '[TARGET]',
        '🌍': '[GLOBAL]',
        '🏥': '[HEALTH]',
        '💡': '[INFO]',
        '💰': '[MONEY]',
        '📈': '[UP]',
        '📉': '[DOWN]',
        '🎁': '[GIFT]',
        '🔄': '[REFRESH]',
        '🛑': '[STOP]',
        '⭐': '[STAR]',
        '💎': '[DIAMOND]',
        '🔔': '[BELL]',
        '📱': '[MOBILE]',
        '💳': '[CARD]',
        '🏦': '[BANK]',
        '👤': '[USER]',
        '👥': '[USERS]',
        '🎉': '[CELEBRATE]',
        '🌟': '[SPARKLE]',
        '⚡': '[LIGHTNING]',
        '🔥': '[FIRE]',
        '💻': '[COMPUTER]',
        '📧': '[EMAIL]',
        '📞': '[PHONE]',
        '🛡️': '[SHIELD]',
        '🎨': '[ART]',
        '📝': '[NOTE]',
        '🔗': '[LINK]',
        '⚖️': '[BALANCE]',
        '📋': '[CLIPBOARD]',
        '🎊': '[CONFETTI]',
        '🌈': '[RAINBOW]',
        '🚨': '[ALERT]',
        '🔐': '[SECURE]',
        '🎮': '[GAME]',
        '📦': '[PACKAGE]',
        '🏆': '[TROPHY]',
        '💪': '[STRONG]',
        '🧠': '[BRAIN]',
        '👑': '[CROWN]',
        
        # Bullets and dashes
        '•': '-',
        '–': '-',  # en dash
        '—': '-',  # em dash
        '→': '->',
        '➔': '->',
        '➜': '->',
        
        # Quotes
        '"': '"',  # left double quotation
        '"': '"',  # right double quotation
        ''': "'",  # left single quotation
        ''': "'",  # right single quotation
        
        # Other symbols
        '…': '...',
        '©': '(c)',
        '®': '(R)',
        '™': '(TM)',
        '°': ' degrees',
        '±': '+/-',
        '×': 'x',
        '÷': '/',
        '≤': '<=',
        '≥': '>=',
        '≠': '!=',
        '∞': 'infinity',
    }

def clean_non_ascii_text(text):
    """Bersihkan karakter non-ASCII dari teks"""
    replacement_map = get_ascii_replacement_map()
    
    # Replace menggunakan mapping
    for non_ascii, ascii_replacement in replacement_map.items():
        text = text.replace(non_ascii, ascii_replacement)
    
    # Hapus sisa karakter non-ASCII yang tidak terpetakan
    # Gunakan encode/decode untuk menghapus karakter non-ASCII
    try:
        # Coba encode ke ASCII, replace karakter yang tidak bisa di-encode
        text = text.encode('ascii', 'ignore').decode('ascii')
    except Exception:
        # Fallback: hapus karakter dengan codepoint > 127
        text = ''.join(char for char in text if ord(char) <= 127)
    
    return text

def add_encoding_header(content):
    """Tambahkan header encoding jika belum ada"""
    lines = content.split('\n')
    
    # Cek apakah sudah ada header encoding di 2 baris pertama
    has_encoding = False
    for i in range(min(2, len(lines))):
        if 'coding' in lines[i] or 'encoding' in lines[i]:
            has_encoding = True
            break
    
    if not has_encoding:
        # Tambahkan header di baris pertama
        if lines[0].startswith('#!'):
            # Jika ada shebang, tambahkan setelahnya
            lines.insert(1, '# -*- coding: utf-8 -*-')
        else:
            # Tambahkan di baris pertama
            lines.insert(0, '# -*- coding: utf-8 -*-')
    
    return '\n'.join(lines)

def validate_python_syntax(content):
    """Validasi syntax Python menggunakan ast.parse"""
    try:
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def find_python_files(root_dir):
    """Cari semua file Python, abaikan folder tertentu"""
    ignore_dirs = {'__pycache__', '.venv', 'venv', 'node_modules', '.git', '.replit'}
    python_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Hapus direktori yang diabaikan dari pencarian
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def clean_python_file(file_path):
    """Bersihkan satu file Python"""
    try:
        # Buat backup
        backup_path = file_path + '.bak'
        shutil.copy2(file_path, backup_path)
        
        # Baca file dengan UTF-8
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            original_content = f.read()
        
        # Bersihkan karakter non-ASCII
        cleaned_content = clean_non_ascii_text(original_content)
        
        # Tambahkan header encoding
        cleaned_content = add_encoding_header(cleaned_content)
        
        # Validasi syntax
        is_valid, error = validate_python_syntax(cleaned_content)
        
        if is_valid:
            # Simpan file yang sudah dibersihkan
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            # Hitung jumlah penggantian
            replacements = len(original_content) - len(cleaned_content.encode('ascii', 'ignore').decode('ascii'))
            
            return True, replacements, None
        else:
            # Jika gagal parse, coba fallback: hapus semua non-ASCII
            fallback_content = original_content.encode('ascii', 'ignore').decode('ascii')
            fallback_content = add_encoding_header(fallback_content)
            
            is_valid_fallback, error_fallback = validate_python_syntax(fallback_content)
            
            if is_valid_fallback:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fallback_content)
                
                replacements = len(original_content) - len(fallback_content)
                return True, replacements, "Used fallback cleanup"
            else:
                # Restore dari backup jika gagal
                shutil.copy2(backup_path, file_path)
                return False, 0, f"Parse failed: {error_fallback}"
                
    except Exception as e:
        return False, 0, f"File processing error: {str(e)}"

def main():
    """Main function untuk membersihkan semua file Python"""
    root_dir = "/home/runner/workspace/Bismillah"
    
    print("🔍 Mencari file Python...")
    python_files = find_python_files(root_dir)
    
    print(f"📂 Ditemukan {len(python_files)} file Python")
    
    results = {
        "status": "success",
        "files_scanned": len(python_files),
        "files_modified": 0,
        "replacements_total": 0,
        "errors": []
    }
    
    for file_path in python_files:
        print(f"🧹 Membersihkan: {file_path}")
        
        success, replacements, error = clean_python_file(file_path)
        
        if success:
            results["files_modified"] += 1
            results["replacements_total"] += replacements
            print(f"  ✅ Berhasil ({replacements} replacements)")
        else:
            results["errors"].append({
                "file": file_path,
                "reason": error
            })
            print(f"  ❌ Gagal: {error}")
    
    # Jika ada error, ubah status
    if results["errors"]:
        results["status"] = "partial_success"
    
    print("\n📋 RINGKASAN:")
    print(json.dumps(results, indent=2, ensure_ascii=True))
    
    return results

if __name__ == "__main__":
    main()
