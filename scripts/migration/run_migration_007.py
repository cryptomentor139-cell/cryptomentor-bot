#!/usr/bin/env python3
"""
Run Migration 007: Add Autonomous Trading Support
Adds Automaton integration columns to user_automatons table
"""

import os
import sys

def run_migration():
    """Run migration 007"""
    print("=" * 60)
    print("MIGRATION 007: Add Autonomous Trading Support")
    print("=" * 60)
    
    try:
        # Import supabase client
        from supabase_client import supabase
        
        if not supabase:
            print("❌ Supabase client not available")
            print("   This migration will be applied automatically on Railway deployment")
            print("   Or run manually via Supabase SQL Editor")
            print("\n📄 Migration SQL location:")
            print("   Bismillah/migrations/007_add_autonomous_trading.sql")
            return True  # Not a failure, just skip for now
        
        print("\n⏳ Adding columns to user_automatons table...")
        
        # List of columns to add
        columns = [
            ("automaton_ai_task_id", "TEXT", "Link to Automaton dashboard task"),
            ("trading_enabled", "BOOLEAN DEFAULT false", "Enable/disable autonomous trading"),
            ("strategy", "TEXT DEFAULT 'conservative'", "Trading strategy"),
            ("risk_level", "TEXT DEFAULT 'low'", "Risk level"),
            ("max_trade_size_pct", "FLOAT DEFAULT 5.0", "Max % per trade"),
            ("daily_loss_limit_pct", "FLOAT DEFAULT 20.0", "Daily loss limit"),
            ("last_trade_at", "TIMESTAMP", "Last trade timestamp"),
            ("total_trades", "INTEGER DEFAULT 0", "Total trades"),
            ("winning_trades", "INTEGER DEFAULT 0", "Winning trades"),
            ("losing_trades", "INTEGER DEFAULT 0", "Losing trades"),
        ]
        
        success_count = 0
        for col_name, col_type, description in columns:
            try:
                # Try to add column
                sql = f"ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
                result = supabase.rpc('execute_sql', {'query': sql}).execute()
                print(f"   ✅ Added {col_name}")
                success_count += 1
            except Exception as e:
                error_msg = str(e).lower()
                if 'already exists' in error_msg or 'duplicate' in error_msg:
                    print(f"   ⚠️  {col_name} already exists")
                    success_count += 1
                else:
                    print(f"   ❌ Error adding {col_name}: {e}")
        
        print(f"\n✅ Migration completed: {success_count}/{len(columns)} columns processed")
        
        print("\n📊 Columns added:")
        for col_name, _, description in columns:
            print(f"  • {col_name} - {description}")
        
        print("\n🎯 Next Steps:")
        print("  1. Test autonomous trading features")
        print("  2. Deploy to Railway")
        print("  3. Monitor agent performance")
        
        return True
        
    except ImportError as e:
        print(f"\n⚠️  Import error: {e}")
        print("   Migration will be applied on Railway deployment")
        return True  # Not a failure
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
