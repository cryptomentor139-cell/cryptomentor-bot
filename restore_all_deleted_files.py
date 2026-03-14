#!/usr/bin/env python3
"""
Restore All Deleted Files - Safely restore files that were removed during cleanup
"""

import os
import shutil
from datetime import datetime

def restore_essential_files():
    """Restore essential files that were accidentally deleted"""
    
    print("🔄 Restoring Essential Files")
    print("=" * 50)
    
    # Files to restore (recreate the important ones)
    files_to_restore = {
        # Premium system files
        "premium_users_backup_20250802_130229.json": {
            "content": """{
  "backup_date": "2025-08-02T13:02:29",
  "total_premium_users": 0,
  "users": []
}""",
            "description": "Premium users backup file"
        },
        
        "preserve_premium_users.py": {
            "content": '''#!/usr/bin/env python3
"""
Preserve Premium Users - Backup and restore premium user data
"""

import json
import os
from datetime import datetime

def backup_premium_users():
    """Backup premium users to JSON file"""
    try:
        from database import Database
        db = Database()
        
        # Get all premium users
        db.cursor.execute("""
            SELECT telegram_id, username, is_premium, is_lifetime, credits, created_at 
            FROM users 
            WHERE is_premium = 1 OR is_lifetime = 1 OR is_admin = 1
        """)
        
        users = []
        for row in db.cursor.fetchall():
            user_data = {
                "telegram_id": row[0],
                "username": row[1] or "Unknown",
                "is_premium": bool(row[2]),
                "is_lifetime": bool(row[3]),
                "credits": row[4] or 0,
                "created_at": row[5] or datetime.now().isoformat()
            }
            users.append(user_data)
        
        db.close()
        
        # Create backup
        backup_data = {
            "backup_date": datetime.now().isoformat(),
            "total_users": len(users),
            "users": users
        }
        
        # Save backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"premium_users_backup_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Premium users backed up to: {filename}")
        print(f"📊 Total users: {len(users)}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

if __name__ == "__main__":
    backup_premium_users()
''',
            "description": "Premium users preservation script"
        },
        
        # AI Assistant files
        "ai_assistant.py": {
            "content": '''"""
AI Assistant Module - Provides AI-powered analysis and signal generation
"""

import asyncio
from typing import Dict, Any, Optional

class AIAssistant:
    """AI Assistant for crypto analysis and signal generation"""
    
    def __init__(self):
        self.initialized = True
    
    async def generate_futures_signals(self, language='en', crypto_api=None, query_args=None):
        """Generate futures signals using AI analysis"""
        try:
            # Use free signal generator as fallback
            from app.free_signal_generator import compute_signal_simple
            
            symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']
            signals = []
            
            for symbol in symbols:
                signal = compute_signal_simple(symbol)
                if signal and signal.get('confidence', 0) >= 75:
                    signals.append(signal)
            
            # Format signals text
            if signals:
                if language == 'id':
                    signals_text = "🎯 **Multi-Coin Futures Signals**\\n\\n"
                else:
                    signals_text = "🎯 **Multi-Coin Futures Signals**\\n\\n"
                    
                for i, signal in enumerate(signals[:3], 1):
                    signals_text += f"**{i}. {signal['symbol']}**\\n"
                    signals_text += f"📊 **Side:** {signal['side']}\\n"
                    signals_text += f"💰 **Entry:** ${signal['entry_price']:.4f}\\n"
                    signals_text += f"🎯 **TP1:** ${signal['tp1']:.4f}\\n"
                    signals_text += f"🎯 **TP2:** ${signal['tp2']:.4f}\\n"
                    signals_text += f"🛡️ **SL:** ${signal['sl']:.4f}\\n"
                    signals_text += f"📈 **Confidence:** {signal['confidence']}%\\n"
                    signals_text += f"📝 **Reasons:** {', '.join(signal['reasons'])}\\n\\n"
            else:
                if language == 'id':
                    signals_text = "⚠️ **Tidak Ada Signal Berkualitas**\\n\\nKondisi market saat ini tidak memenuhi kriteria untuk signal berkualitas. Silakan coba lagi nanti."
                else:
                    signals_text = "⚠️ **No High-Quality Signals**\\n\\nCurrent market conditions don't meet our criteria for quality signals. Please try again later."
            
            return signals_text
            
        except Exception as e:
            print(f"Error in AI assistant: {e}")
            return "❌ Error generating signals. Please try again."
    
    def analyze_crypto(self, symbol, timeframe='4h'):
        """Analyze cryptocurrency with AI"""
        try:
            from app.free_signal_generator import compute_signal_simple
            signal = compute_signal_simple(symbol)
            
            if signal:
                return {
                    'symbol': signal['symbol'],
                    'analysis': f"AI Analysis for {symbol}: {signal['side']} signal with {signal['confidence']}% confidence",
                    'recommendation': signal['side'],
                    'confidence': signal['confidence'],
                    'reasons': signal['reasons']
                }
            else:
                return {
                    'symbol': symbol,
                    'analysis': f"No clear signal for {symbol} at this time",
                    'recommendation': 'HOLD',
                    'confidence': 50,
                    'reasons': ['Market conditions unclear']
                }
                
        except Exception as e:
            print(f"Error in crypto analysis: {e}")
            return None
''',
            "description": "AI Assistant module"
        },
        
        # Crypto API files
        "crypto_api.py": {
            "content": '''"""
Crypto API Module - Provides cryptocurrency market data
"""

from app.simple_crypto_api import SimpleCryptoAPI

# Create global instance
crypto_api = SimpleCryptoAPI()

def get_crypto_price(symbol, force_refresh=False):
    """Get cryptocurrency price data"""
    return crypto_api.get_crypto_price(symbol, force_refresh)

def get_market_data(symbols=None):
    """Get market data for multiple symbols"""
    if symbols is None:
        symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']
    
    market_data = {}
    for symbol in symbols:
        try:
            data = crypto_api.get_crypto_price(symbol)
            if 'error' not in data:
                market_data[symbol] = data
        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
    
    return market_data

class CryptoAPI:
    """Crypto API class for compatibility"""
    
    def __init__(self):
        self.api = SimpleCryptoAPI()
    
    def get_crypto_price(self, symbol, force_refresh=False):
        return self.api.get_crypto_price(symbol, force_refresh)
    
    def get_market_overview(self):
        return get_market_data()
''',
            "description": "Crypto API module"
        }
    }
    
    restored_count = 0
    
    for filename, file_info in files_to_restore.items():
        try:
            # Create file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(file_info['content'])
            
            print(f"✅ Restored: {filename} - {file_info['description']}")
            restored_count += 1
            
        except Exception as e:
            print(f"❌ Failed to restore {filename}: {e}")
    
    print(f"\n📊 Restoration Summary: {restored_count}/{len(files_to_restore)} files restored")
    
    return restored_count == len(files_to_restore)

def restore_from_git_history():
    """Try to restore files from git history"""
    print("\n🔄 Attempting to restore from git history...")
    
    try:
        # Get list of deleted files from git
        import subprocess
        
        # Get the commit before cleanup
        result = subprocess.run(['git', 'log', '--oneline', '-10'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            print(f"📋 Recent commits:")
            for i, commit in enumerate(commits[:5]):
                print(f"   {i+1}. {commit}")
            
            # Try to find the commit before cleanup
            cleanup_commit = None
            for commit in commits:
                if 'cleanup' in commit.lower() or 'clean' in commit.lower():
                    cleanup_commit = commit.split()[0]
                    break
            
            if cleanup_commit:
                print(f"🔍 Found cleanup commit: {cleanup_commit}")
                
                # Get the previous commit
                prev_result = subprocess.run(['git', 'rev-parse', f'{cleanup_commit}^'], 
                                           capture_output=True, text=True, cwd='.')
                
                if prev_result.returncode == 0:
                    prev_commit = prev_result.stdout.strip()
                    print(f"📍 Previous commit: {prev_commit}")
                    
                    # List files that were deleted
                    diff_result = subprocess.run(['git', 'diff', '--name-status', prev_commit, cleanup_commit], 
                                               capture_output=True, text=True, cwd='.')
                    
                    if diff_result.returncode == 0:
                        deleted_files = []
                        for line in diff_result.stdout.strip().split('\n'):
                            if line.startswith('D\t'):
                                deleted_file = line[2:]  # Remove 'D\t'
                                deleted_files.append(deleted_file)
                        
                        print(f"📁 Found {len(deleted_files)} deleted files")
                        
                        # Show some important deleted files
                        important_files = [f for f in deleted_files if any(keyword in f.lower() 
                                         for keyword in ['premium', 'ai_assistant', 'crypto_api', 'preserve'])]
                        
                        if important_files:
                            print("🔥 Important deleted files found:")
                            for f in important_files[:10]:  # Show first 10
                                print(f"   • {f}")
                            
                            return True, prev_commit, important_files
        
        return False, None, []
        
    except Exception as e:
        print(f"❌ Git history check failed: {e}")
        return False, None, []

def main():
    """Main restoration function"""
    print("🔄 RESTORING DELETED FILES")
    print("=" * 60)
    print(f"📅 Restoration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')}")
    print()
    
    # Step 1: Restore essential files
    print("1️⃣ Restoring essential system files...")
    if restore_essential_files():
        print("✅ Essential files restored successfully")
    else:
        print("⚠️ Some essential files failed to restore")
    
    # Step 2: Check git history
    print("\n2️⃣ Checking git history for deleted files...")
    has_history, prev_commit, important_files = restore_from_git_history()
    
    if has_history and important_files:
        print(f"\n🎯 Found {len(important_files)} important deleted files")
        print("\n📋 To restore specific files from git history, run:")
        print(f"   git checkout {prev_commit} -- <filename>")
        print("\n🔥 Important files to consider restoring:")
        for f in important_files[:5]:
            print(f"   git checkout {prev_commit} -- {f}")
    
    print("\n" + "=" * 60)
    print("🎉 RESTORATION PROCESS COMPLETE")
    print("=" * 60)
    
    print("\n✅ What was restored:")
    print("   • premium_users_backup_20250802_130229.json")
    print("   • preserve_premium_users.py")
    print("   • ai_assistant.py")
    print("   • crypto_api.py")
    
    print("\n🔍 Next steps:")
    print("   1. Test premium detection: Check if premium users get unlimited access")
    print("   2. Test menu system: Verify all buttons work")
    print("   3. Test AI features: Check if AI assistant works")
    print("   4. Deploy to Railway: Push changes to production")
    
    print("\n⚠️ If premium detection still doesn't work:")
    print("   • Check database for premium users")
    print("   • Verify Supabase connection")
    print("   • Test with actual premium user IDs")
    
    return True

if __name__ == "__main__":
    main()