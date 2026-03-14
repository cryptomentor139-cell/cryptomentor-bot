#!/usr/bin/env python3
"""
Deploy Restored Files to Railway
Push all restored essential files to production
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
    """Check git status and show what will be deployed"""
    print("🔍 Checking git status...")
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository")
        return False
    
    # Show current status
    result = subprocess.run(['git', 'status', '--porcelain'], 
                          capture_output=True, text=True, cwd='.')
    
    if result.returncode != 0:
        print("❌ Failed to check git status")
        return False
    
    changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
    
    if not changes:
        print("✅ No changes to deploy")
        return True
    
    print(f"📋 Found {len(changes)} changes to deploy:")
    
    # Show important files
    important_files = []
    for change in changes:
        if len(change) >= 3:
            status = change[:2]
            filename = change[3:]
            
            # Highlight important restored files
            if any(keyword in filename.lower() for keyword in 
                   ['premium', 'ai_assistant', 'crypto_api', 'preserve', 'credits_guard']):
                important_files.append(f"   🔥 {status} {filename}")
            else:
                print(f"   📄 {status} {filename}")
    
    # Show important files at the end
    if important_files:
        print("\n🔥 CRITICAL RESTORED FILES:")
        for file in important_files:
            print(file)
    
    return True

def deploy_to_railway():
    """Deploy all changes to Railway"""
    print("🚀 DEPLOYING RESTORED FILES TO RAILWAY")
    print("=" * 60)
    print(f"📅 Deployment Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')}")
    print()
    
    # Step 1: Check git status
    if not check_git_status():
        return False
    
    # Step 2: Add all changes
    if not run_command('git add .', 'Adding all changes to git'):
        return False
    
    # Step 3: Commit changes
    commit_message = f"🔧 Restore essential files - Premium detection & AI system\n\n✅ Restored files:\n• premium_users_backup_20250802_130229.json\n• preserve_premium_users.py\n• ai_assistant.py\n• crypto_api.py\n• Fixed premium detection in menu system\n• Enhanced credits_guard with premium bypass\n\n🎯 Premium users now get unlimited access\n📅 Deployed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')}"
    
    if not run_command(f'git commit -m "{commit_message}"', 'Committing changes'):
        print("ℹ️ No new changes to commit (files already committed)")
    
    # Step 4: Push to Railway
    print("\n🚀 Pushing to Railway...")
    if not run_command('git push origin main', 'Pushing to Railway (main branch)'):
        # Try master branch as fallback
        print("⚠️ Main branch failed, trying master branch...")
        if not run_command('git push origin master', 'Pushing to Railway (master branch)'):
            return False
    
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 60)
    
    print("\n✅ What was deployed:")
    print("   • Premium detection system restored")
    print("   • AI Assistant module fixed")
    print("   • Crypto API module restored")
    print("   • Premium users backup file")
    print("   • Credits guard with premium bypass")
    
    print("\n🔍 Next steps:")
    print("   1. Monitor Railway deployment logs")
    print("   2. Test premium detection with actual premium users")
    print("   3. Verify menu system works correctly")
    print("   4. Check AI features functionality")
    
    print("\n📊 Expected behavior:")
    print("   • Premium/Lifetime users: Unlimited access to all features")
    print("   • Free users: Credit deduction for paid features")
    print("   • Menu buttons: All working correctly")
    print("   • AI Assistant: Generating signals properly")
    
    print("\n🌐 Railway Dashboard:")
    print("   • Check deployment status at railway.app")
    print("   • Monitor logs for any startup errors")
    print("   • Verify bot responds to /menu command")
    
    return True

def verify_restored_files():
    """Verify that all essential files exist"""
    print("🔍 Verifying restored files...")
    
    essential_files = [
        'ai_assistant.py',
        'crypto_api.py', 
        'premium_users_backup_20250802_130229.json',
        'preserve_premium_users.py',
        'app/premium_checker.py',
        'app/credits_guard.py'
    ]
    
    missing_files = []
    for file in essential_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ {len(missing_files)} files are missing!")
        print("   Run restore_all_deleted_files.py first")
        return False
    
    print(f"\n✅ All {len(essential_files)} essential files verified")
    return True

def main():
    """Main deployment function"""
    print("🔧 RAILWAY DEPLOYMENT - RESTORED FILES")
    print("=" * 50)
    
    # Verify files exist
    if not verify_restored_files():
        print("\n❌ Cannot deploy - missing essential files")
        return False
    
    # Deploy to Railway
    success = deploy_to_railway()
    
    if success:
        print("\n🎉 SUCCESS: All restored files deployed to Railway!")
        print("🔗 Check your Railway dashboard for deployment status")
        print("🤖 Test the bot with /menu command")
    else:
        print("\n❌ DEPLOYMENT FAILED")
        print("🔧 Check the errors above and try again")
    
    return success

if __name__ == "__main__":
    main()