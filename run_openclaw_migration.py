#!/usr/bin/env python3
"""
OpenClaw Migration Runner
Run this script to setup OpenClaw database tables
"""

import os
import sys

def run_migration():
    """Run OpenClaw database migration"""
    print("🚀 OpenClaw Migration Runner")
    print("=" * 50)
    
    # Import database
    try:
        from database import Database
    except ImportError:
        print("❌ Error: Cannot import Database")
        print("   Make sure you're in the Bismillah directory")
        sys.exit(1)
    
    # Check migration file exists
    migration_file = 'migrations/010_openclaw_claude_assistant.sql'
    if not os.path.exists(migration_file):
        print(f"❌ Error: Migration file not found: {migration_file}")
        sys.exit(1)
    
    print(f"📄 Reading migration file: {migration_file}")
    
    # Read migration SQL
    with open(migration_file, 'r') as f:
        sql = f.read()
    
    print(f"✅ Migration file loaded ({len(sql)} bytes)")
    
    # Initialize database
    print("🔌 Connecting to database...")
    db = Database()
    print("✅ Database connected")
    
    # Split SQL into statements
    statements = []
    current_stmt = []
    in_function = False
    
    for line in sql.split('\n'):
        line_stripped = line.strip()
        
        # Track if we're inside a function/procedure
        if 'CREATE OR REPLACE FUNCTION' in line_stripped or 'CREATE FUNCTION' in line_stripped:
            in_function = True
        
        current_stmt.append(line)
        
        # End of statement
        if line_stripped.endswith(';'):
            if in_function:
                # Check if this is the end of function
                if line_stripped == '$$;' or line_stripped == '$;':
                    in_function = False
                    stmt = '\n'.join(current_stmt)
                    if stmt.strip():
                        statements.append(stmt)
                    current_stmt = []
            else:
                # Regular statement
                stmt = '\n'.join(current_stmt)
                if stmt.strip():
                    statements.append(stmt)
                current_stmt = []
    
    print(f"📊 Found {len(statements)} SQL statements")
    
    # Execute statements
    success_count = 0
    skip_count = 0
    error_count = 0
    
    print("\n🔄 Executing migration...")
    print("-" * 50)
    
    for i, stmt in enumerate(statements, 1):
        stmt_preview = stmt.strip()[:60].replace('\n', ' ')
        
        try:
            db.execute(stmt)
            success_count += 1
            print(f"✅ [{i}/{len(statements)}] {stmt_preview}...")
        except Exception as e:
            error_msg = str(e).lower()
            
            # Skip "already exists" errors
            if 'already exists' in error_msg or 'duplicate' in error_msg:
                skip_count += 1
                print(f"⏭️  [{i}/{len(statements)}] {stmt_preview}... (already exists)")
            else:
                error_count += 1
                print(f"❌ [{i}/{len(statements)}] {stmt_preview}...")
                print(f"   Error: {str(e)[:100]}")
    
    # Commit changes
    try:
        db.commit()
        print("\n✅ Migration committed to database")
    except Exception as e:
        print(f"\n❌ Error committing migration: {e}")
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Migration Summary:")
    print(f"   ✅ Success: {success_count}")
    print(f"   ⏭️  Skipped: {skip_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📝 Total: {len(statements)}")
    
    if error_count > 0:
        print("\n⚠️  Some statements failed, but migration may still be functional")
        print("   Check errors above for details")
    else:
        print("\n🎉 Migration completed successfully!")
    
    # Test OpenClaw Manager
    print("\n🧪 Testing OpenClaw Manager...")
    try:
        from app.openclaw_manager import get_openclaw_manager
        manager = get_openclaw_manager(db)
        
        print(f"✅ OpenClaw Manager initialized")
        print(f"   Using OpenRouter: {manager.use_openrouter}")
        print(f"   Model: {manager.MODEL}")
        
        if manager.use_openrouter:
            print(f"   Base URL: {manager.base_url}")
            print("   ✅ Will use existing DEEPSEEK_API_KEY")
        else:
            print("   ✅ Will use direct Anthropic API")
        
    except Exception as e:
        print(f"⚠️  OpenClaw Manager test failed: {e}")
        print("   This is OK if you haven't added API key yet")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("   1. Restart your bot: python3 bot.py")
    print("   2. Test OpenClaw: /openclaw_create MyBot friendly")
    print("   3. Activate mode: /openclaw_start")
    print("   4. Chat freely without commands!")
    print("\n✨ OpenClaw is ready to use!")


if __name__ == '__main__':
    try:
        run_migration()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
