#!/usr/bin/env python3
"""
Fix Git Push Conflict - Safely sync with Railway remote
"""

import subprocess
import os
from datetime import datetime

def run_command(cmd, description):
    """Run shell command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def check_git_status():
    """Check current git status"""
    print("🔍 Checking git status...")
    
    # Check current branch
    result = subprocess.run(['git', 'branch', '--show-current'], 
                          capture_output=True, text=True, cwd='.')
    if result.returncode == 0:
        current_branch = result.stdout.strip()
        print(f"📍 Current branch: {current_branch}")
    
    # Check remote status
    result = subprocess.run(['git', 'remote', '-v'], 
                          capture_output=True, text=True, cwd='.')
    if result.returncode == 0:
        remotes = result.stdout.strip()
        print(f"🌐 Remotes:\n{remotes}")
    
    # Check status
    result = subprocess.run(['git', 'status', '--porcelain'], 
                          capture_output=True, text=True, cwd='.')
    if result.returncode == 0:
        changes = result.stdout.strip()
        if changes:
            print(f"📋 Uncommitted changes:\n{changes}")
        else:
            print("✅ Working directory clean")
    
    return True

def fix_push_conflict():
    """Fix git push conflict by syncing with remote"""
    print("🔧 FIXING GIT PUSH CONFLICT")
    print("=" * 50)
    print(f"📅 Fix Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')}")
    print()
    
    # Step 1: Check current status
    check_git_status()
    
    # Step 2: Fetch latest from remote
    print("\n🔄 Fetching latest changes from remote...")
    if not run_command('git fetch origin', 'Fetching from origin'):
        return False
    
    # Step 3: Check what's different
    print("\n🔍 Checking differences with remote...")
    result = subprocess.run(['git', 'log', '--oneline', 'HEAD..origin/main'], 
                          capture_output=True, text=True, cwd='.')
    
    if result.returncode == 0:
        remote_commits = result.stdout.strip()
        if remote_commits:
            print("📋 Remote commits not in local:")
            for line in remote_commits.split('\n'):
                print(f"   • {line}")
        else:
            print("✅ Local is up to date with remote")
    
    # Step 4: Show local commits not in remote
    result = subprocess.run(['git', 'log', '--oneline', 'origin/main..HEAD'], 
                          capture_output=True, text=True, cwd='.')
    
    if result.returncode == 0:
        local_commits = result.stdout.strip()
        if local_commits:
            print("📋 Local commits not in remote:")
            for line in local_commits.split('\n'):
                print(f"   • {line}")
        else:
            print("✅ No local commits ahead of remote")
    
    # Step 5: Offer solutions
    print("\n🎯 SOLUTION OPTIONS:")
    print("1. Pull and merge (safe, preserves both histories)")
    print("2. Pull and rebase (clean, linear history)")
    print("3. Force push (DANGEROUS, overwrites remote)")
    
    # Option 1: Safe pull and merge
    print("\n🔄 Attempting safe pull and merge...")
    if run_command('git pull origin main --no-edit', 'Pulling and merging from remote'):
        print("✅ Successfully merged remote changes")
        
        # Now try to push
        print("\n🚀 Attempting to push merged changes...")
        if run_command('git push origin main', 'Pushing merged changes'):
            print("🎉 SUCCESS: Changes pushed to Railway!")
            return True
        else:
            print("❌ Push still failed after merge")
    
    # Option 2: If merge failed, try rebase
    print("\n🔄 Attempting rebase approach...")
    if run_command('git pull origin main --rebase', 'Pulling with rebase'):
        print("✅ Successfully rebased on remote")
        
        # Now try to push
        print("\n🚀 Attempting to push rebased changes...")
        if run_command('git push origin main', 'Pushing rebased changes'):
            print("🎉 SUCCESS: Changes pushed to Railway!")
            return True
        else:
            print("❌ Push still failed after rebase")
    
    # Option 3: Last resort - force push (with backup)
    print("\n⚠️ LAST RESORT: Force push (with backup)")
    print("Creating backup branch first...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_branch = f"backup_before_force_push_{timestamp}"
    
    if run_command(f'git branch {backup_branch}', f'Creating backup branch: {backup_branch}'):
        print(f"✅ Backup created: {backup_branch}")
        
        print("\n🚨 Force pushing (this will overwrite remote history)...")
        if run_command('git push origin main --force', 'Force pushing to remote'):
            print("🎉 SUCCESS: Force push completed!")
            print(f"💾 Backup available in branch: {backup_branch}")
            return True
        else:
            print("❌ Even force push failed")
    
    return False

def main():
    """Main function"""
    print("🔧 GIT PUSH CONFLICT RESOLVER")
    print("=" * 40)
    
    success = fix_push_conflict()
    
    if success:
        print("\n🎉 GIT CONFLICT RESOLVED!")
        print("✅ Your changes are now on Railway")
        print("🤖 Bot should redeploy automatically")
        print("\n🔍 Next steps:")
        print("   1. Check Railway deployment logs")
        print("   2. Test bot with /menu command")
        print("   3. Verify premium detection works")
    else:
        print("\n❌ COULD NOT RESOLVE CONFLICT")
        print("🔧 Manual intervention required")
        print("\n💡 Manual options:")
        print("   1. Use GitHub Desktop or VS Code Git")
        print("   2. Manually resolve conflicts in files")
        print("   3. Contact Railway support if needed")
    
    return success

if __name__ == "__main__":
    main()