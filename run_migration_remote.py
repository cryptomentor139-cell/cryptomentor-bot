#!/usr/bin/env python3
"""
Run OpenClaw Skills Migration Remotely
This script can be executed via Railway CLI
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the migration"""
    print("🔄 Starting OpenClaw Skills Migration...")
    print("=" * 60)
    
    try:
        # Import and run migration
        from run_openclaw_skills_migration import run_migration
        
        print("\n📦 Running migration...")
        run_migration()
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print("\n🔄 Please restart your bot now:")
        print("   railway restart")
        print("\n📊 Check logs:")
        print("   railway logs --tail 50")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
