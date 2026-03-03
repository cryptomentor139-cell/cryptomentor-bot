#!/usr/bin/env python3
"""
Script untuk merapikan folder Bismillah/
Memindahkan file ke folder yang sesuai berdasarkan kategori
"""

import os
import shutil
from pathlib import Path

# Mapping file patterns ke folder tujuan
FILE_MAPPINGS = {
    # Dokumentasi Deployment
    'docs/deployment': [
        'DEPLOY_', 'DEPLOYMENT_', 'RAILWAY_', 'BACKUP_', 'MIGRATION_',
        'APPLY_MIGRATION', 'STEP2_RUN', 'VERIFY_DEPLOYMENT', 'FORCE_RAILWAY',
        'CHECK_RAILWAY', 'MONITOR_DEPLOYMENT', 'ROLLBACK_'
    ],
    
    # Dokumentasi Features
    'docs/features': [
        'AUTOMATON_', 'AI_AGENT_', 'AUTOSIGNAL_', 'CEO_AGENT_', 'ISOLATED_AI_',
        'LINEAGE_', 'CENTRALIZED_WALLET_', 'CUSTODIAL_WALLET_', 'DEPOSIT_',
        'WITHDRAWAL_', 'CREDIT_', 'BROADCAST_', 'SIGNAL_TRACKING_', 'SMC_',
        'REVENUE_', 'ADMIN_', 'PREMIUM_', 'REFERRAL_', 'MENU_', 'TRACKING_',
        'DUAL_MODE_', 'ONLINE_MODE_', 'OFFLINE_MODE_'
    ],
    
    # Panduan Pengguna
    'docs/guides': [
        'CARA_', 'PANDUAN_', 'GUIDE', 'START_HERE', 'QUICK_START', 'QUICK_REFERENCE',
        'QUICK_GUIDE', 'MULAI_DISINI', 'LANGKAH_', 'TAHAP_', 'README', 'INDEX_',
        'SUMMARY_', 'CHECKLIST', 'FAQ_', 'CHEATSHEET', 'RINGKASAN_', 'AKSES_',
        'INVITATION_', 'VISUAL_', 'FINAL_CHECKLIST'
    ],
    
    # Dokumentasi Fixes (Archive)
    'docs/archive': [
        'FIX_', 'TROUBLESHOOT_', 'DEBUG_', 'ERROR_', 'CRASH_', 'ISSUE_',
        'DIAGNOSIS_', 'SOLUSI_', 'MASALAH_', 'PERUBAHAN_', 'UPDATE_',
        'IMPROVEMENT_', 'OPTIMIZATION_', 'SPEED_', 'NETWORK_', 'TIMEOUT_',
        'EMOJI_', 'LOOPING_', 'DUPLICATE_', 'STATE_', 'SPAWN_FEE'
    ],
    
    # Tests - Property Based
    'tests/property': [
        'test_property_', 'test_withdrawal_balance_validation_property',
        'test_deposit_detection_property', 'test_conway_credits_conversion_property',
        'test_one_wallet_per_user_property', 'test_encryption_roundtrip_property',
        'test_wallet_generation_property', 'test_conway_api_balance_check_property',
        'test_conway_api_credit_transfer_property', 'test_audit_logging_property'
    ],
    
    # Tests - Integration
    'tests/integration': [
        'test_task_', 'test_core_business_logic', 'test_menu_integration',
        'test_handler_registration', 'test_signal_tracking_integration',
        'test_rate_limiter_integration', 'test_smc_integration',
        'test_lineage_system', 'test_autonomous_trading', 'comprehensive_test'
    ],
    
    # Tests - Unit (sisanya)
    'tests/unit': [
        'test_', 'test-'  # Catch-all untuk test files
    ],
    
    # Scripts - Migration
    'scripts/migration': [
        'run_migration_', 'apply_', 'migrate_', 'run_constraint_fix',
        'preserve_premium_users', 'setup_supabase', 'create_supabase'
    ],
    
    # Scripts - Setup
    'scripts/setup': [
        'setup_', 'generate_encryption_key', 'grant_automaton_access',
        'spawn_', 'verify_', 'check_', 'discover_', 'prove_',
        'find_lifetime_premium_user'
    ],
    
    # Scripts - Maintenance
    'scripts/maintenance': [
        'auto_backup', 'backup_supabase', 'credit_my_deposit', 'manual_credit_deposit',
        'analyze_', 'force_', 'fix_', 'integrate_', 'weekly_credit_refresh',
        'send_test_message', 'quick_test_', 'debug_'
    ],
}

def should_skip_file(filename):
    """File yang tidak perlu dipindahkan"""
    skip_patterns = [
        'organize_files.py',  # Script ini sendiri
        '.env', '.gitignore', '.railwayignore', '.replit',
        'bot.py', 'main.py', 'config.py', 'database.py', 'utils.py',
        'requirements.txt', 'requirements_openai.txt', 'pyproject.toml',
        'Procfile', 'runtime.txt', 'railway.json',
        'package.json', 'package-lock.json', 'index.js',
        'cryptomentor.db',
        # File yang sudah di folder yang benar
        'app/', 'migrations/', 'automaton/', 'data/', 'signal_logs/',
        '__pycache__/', '.git/', '.hypothesis/', '.pytest_cache/', 'Bismillah/'
    ]
    
    for pattern in skip_patterns:
        if filename.startswith(pattern) or pattern in filename:
            return True
    return False

def get_destination_folder(filename):
    """Tentukan folder tujuan berdasarkan nama file"""
    # Cek setiap kategori
    for dest_folder, patterns in FILE_MAPPINGS.items():
        for pattern in patterns:
            if filename.startswith(pattern):
                return dest_folder
    
    # Default: jika tidak cocok dengan pattern manapun
    if filename.endswith('.md'):
        return 'docs/archive'
    elif filename.startswith('test'):
        return 'tests/unit'
    elif filename.endswith('.py'):
        return 'scripts/maintenance'
    elif filename.endswith(('.sh', '.bat', '.ps1')):
        return 'scripts/maintenance'
    elif filename.endswith(('.sql', '.json', '.txt', '.js')):
        return 'docs/archive'
    
    return None

def organize_files(dry_run=True):
    """Organisir file-file di folder Bismillah"""
    base_path = Path('.')
    moved_files = []
    skipped_files = []
    
    # List semua file di root folder
    for item in base_path.iterdir():
        if item.is_file():
            filename = item.name
            
            # Skip file yang tidak perlu dipindahkan
            if should_skip_file(filename):
                skipped_files.append(filename)
                continue
            
            # Tentukan folder tujuan
            dest_folder = get_destination_folder(filename)
            
            if dest_folder:
                dest_path = base_path / dest_folder / filename
                
                if dry_run:
                    print(f"[DRY RUN] {filename} -> {dest_folder}/")
                    moved_files.append((filename, dest_folder))
                else:
                    try:
                        # Pastikan folder tujuan ada
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Pindahkan file
                        shutil.move(str(item), str(dest_path))
                        print(f"✓ Moved: {filename} -> {dest_folder}/")
                        moved_files.append((filename, dest_folder))
                    except Exception as e:
                        print(f"✗ Error moving {filename}: {e}")
            else:
                print(f"? Unknown category: {filename}")
                skipped_files.append(filename)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Files to move: {len(moved_files)}")
    print(f"  Files skipped: {len(skipped_files)}")
    print(f"{'='*60}")
    
    if dry_run:
        print("\nThis was a DRY RUN. No files were actually moved.")
        print("Run with --execute to actually move the files.")
    
    return moved_files, skipped_files

if __name__ == '__main__':
    import sys
    
    # Check if --execute flag is provided
    execute = '--execute' in sys.argv
    
    if not execute:
        print("="*60)
        print("DRY RUN MODE - No files will be moved")
        print("="*60)
        print()
    
    moved, skipped = organize_files(dry_run=not execute)
    
    if not execute:
        print(f"\nTo actually move the files, run:")
        print(f"  python organize_files.py --execute")
