"""
Comprehensive Test Suite for Lineage System

Tests parent-child agent relationships and 10% revenue sharing.
"""

import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.lineage_manager import LineageManager
from app.supabase_conn import get_supabase_client
from decimal import Decimal


class TestLineageSystem:
    """Test suite for lineage system"""
    
    def __init__(self):
        self.lineage_manager = LineageManager()
        self.supabase = get_supabase_client()
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'message': message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
    
    def test_parent_share_calculation(self):
        """Test 10% parent share calculation"""
        test_name = "Parent Share Calculation (10%)"
        
        try:
            # Test various earnings amounts
            test_cases = [
                (1000, 100),    # 1000 * 0.10 = 100
                (5000, 500),    # 5000 * 0.10 = 500
                (100, 10),      # 100 * 0.10 = 10
                (1234.56, 123.456)  # Decimal precision
            ]
            
            all_passed = True
            for earnings, expected_share in test_cases:
                actual_share = self.lineage_manager.calculate_parent_share(earnings)
                if abs(actual_share - expected_share) > 0.01:  # Allow small floating point error
                    all_passed = False
                    self.log_test(
                        test_name,
                        False,
                        f"Expected {expected_share}, got {actual_share} for earnings {earnings}"
                    )
                    return
            
            self.log_test(test_name, True, "All calculations correct")
            
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {e}")
    
    def test_lineage_manager_initialization(self):
        """Test LineageManager initializes correctly"""
        test_name = "LineageManager Initialization"
        
        try:
            assert self.lineage_manager.MAX_LINEAGE_DEPTH == 10
            assert self.lineage_manager.PARENT_SHARE_PERCENTAGE == Decimal('0.10')
            assert self.lineage_manager.supabase is not None
            assert self.lineage_manager.conway is not None
            
            self.log_test(test_name, True, "All properties initialized correctly")
            
        except AssertionError as e:
            self.log_test(test_name, False, f"Assertion failed: {e}")
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {e}")
    
    def test_database_connection(self):
        """Test database connection works"""
        test_name = "Database Connection"
        
        try:
            # Try to query user_automatons table
            response = self.supabase.table('user_automatons').select('id').limit(1).execute()
            
            self.log_test(test_name, True, "Database connection successful")
            
        except Exception as e:
            self.log_test(test_name, False, f"Connection failed: {e}")
    
    def test_lineage_tables_exist(self):
        """Test that lineage tables exist in database"""
        test_name = "Lineage Tables Existence"
        
        try:
            # Check if lineage_transactions table exists
            response = self.supabase.table('lineage_transactions').select('id').limit(1).execute()
            
            self.log_test(test_name, True, "lineage_transactions table exists")
            
        except Exception as e:
            self.log_test(
                test_name,
                False,
                f"Table not found. Run migration 005 first: {e}"
            )
    
    def test_user_automatons_columns(self):
        """Test that user_automatons has lineage columns"""
        test_name = "user_automatons Lineage Columns"
        
        try:
            # Try to select lineage columns
            response = self.supabase.table('user_automatons').select(
                'id, parent_agent_id, total_children_revenue, autonomous_spawn_enabled'
            ).limit(1).execute()
            
            self.log_test(test_name, True, "All lineage columns exist")
            
        except Exception as e:
            self.log_test(
                test_name,
                False,
                f"Columns not found. Run migration 005 first: {e}"
            )
    
    async def test_get_agent_lineage_empty(self):
        """Test getting lineage for non-existent agent"""
        test_name = "Get Lineage for Non-Existent Agent"
        
        try:
            fake_agent_id = "00000000-0000-0000-0000-000000000000"
            lineage = self.lineage_manager.get_agent_lineage(fake_agent_id)
            
            # Should return empty dict
            if lineage == {}:
                self.log_test(test_name, True, "Returns empty dict for non-existent agent")
            else:
                self.log_test(test_name, False, f"Expected empty dict, got: {lineage}")
                
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {e}")
    
    async def test_get_lineage_statistics_empty(self):
        """Test getting statistics for non-existent agent"""
        test_name = "Get Statistics for Non-Existent Agent"
        
        try:
            fake_agent_id = "00000000-0000-0000-0000-000000000000"
            stats = self.lineage_manager.get_lineage_statistics(fake_agent_id)
            
            # Should return empty dict
            if stats == {}:
                self.log_test(test_name, True, "Returns empty dict for non-existent agent")
            else:
                self.log_test(test_name, False, f"Expected empty dict, got: {stats}")
                
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {e}")
    
    def test_recursive_revenue_sharing_logic(self):
        """Test the logic of recursive revenue sharing"""
        test_name = "Recursive Revenue Sharing Logic"
        
        try:
            # Simulate: Child earns 1000, Parent gets 100, Grandparent gets 10
            child_earnings = 1000
            parent_share = self.lineage_manager.calculate_parent_share(child_earnings)
            grandparent_share = self.lineage_manager.calculate_parent_share(parent_share)
            
            expected_parent = 100
            expected_grandparent = 10
            
            if (abs(parent_share - expected_parent) < 0.01 and 
                abs(grandparent_share - expected_grandparent) < 0.01):
                self.log_test(
                    test_name,
                    True,
                    f"Child: 1000 → Parent: {parent_share} → Grandparent: {grandparent_share}"
                )
            else:
                self.log_test(
                    test_name,
                    False,
                    f"Expected Parent: 100, Grandparent: 10, got {parent_share}, {grandparent_share}"
                )
                
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {e}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   - {result['name']}")
                    if result['message']:
                        print(f"     {result['message']}")
        
        print("\n" + "=" * 70)
        
        return failed == 0


async def run_all_tests():
    """Run all lineage system tests"""
    print("=" * 70)
    print("LINEAGE SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    
    tester = TestLineageSystem()
    
    # Run synchronous tests
    print("📋 Running Synchronous Tests...")
    print("-" * 70)
    tester.test_lineage_manager_initialization()
    tester.test_parent_share_calculation()
    tester.test_database_connection()
    tester.test_lineage_tables_exist()
    tester.test_user_automatons_columns()
    tester.test_recursive_revenue_sharing_logic()
    
    # Run async tests
    print("\n📋 Running Async Tests...")
    print("-" * 70)
    await tester.test_get_agent_lineage_empty()
    await tester.test_get_lineage_statistics_empty()
    
    # Print summary
    all_passed = tester.print_summary()
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Lineage System is ready for integration")
        print("\n📋 Next Steps:")
        print("1. Apply migration 005 to Supabase (if not done)")
        print("2. Update handlers to use LineageManager")
        print("3. Test with real agents in development")
        print("4. Deploy to production")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\n📋 Action Required:")
        print("1. Check if migration 005 has been applied")
        print("2. Verify Supabase connection")
        print("3. Fix any issues and re-run tests")
    
    return all_passed


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
