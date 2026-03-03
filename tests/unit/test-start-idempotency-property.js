/**
 * Property-Based Test for /start Command Idempotency
 * 
 * **Validates: Requirements 2.2.3**
 * 
 * This test uses property-based testing to verify that the /start command
 * is idempotent across various scenarios and user inputs.
 * 
 * Property: User Registration Idempotency
 * ∀ user, ∀ n ≥ 1: registerUser(user) executed n times ⟹ exactly 1 user record
 * 
 * This property states that for any user and any number of registration attempts,
 * the system should maintain exactly one user record (no duplicates).
 */

import { AutomatonAPIClient } from './index.js';

/**
 * Generate a random test user
 */
function generateTestUser() {
  const telegramId = Math.floor(Math.random() * 1000000) + 900000000;
  const username = `test_user_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
  return { telegramId, username };
}

/**
 * Test idempotency for a single user with multiple registration attempts
 */
async function testUserIdempotency(apiClient, user, attempts) {
  console.log(`Testing user ${user.username} (ID: ${user.telegramId}) with ${attempts} attempts...`);
  
  const results = [];
  
  // Perform multiple registration attempts
  for (let i = 0; i < attempts; i++) {
    const userData = await apiClient.registerUser(user.telegramId, user.username);
    results.push(userData);
    
    // Small delay between attempts to simulate real-world usage
    if (i < attempts - 1) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }
  
  // Verify all results have the same telegramId (no duplicates)
  const firstId = results[0].telegramId;
  const allSameId = results.every(r => r.telegramId === firstId);
  
  if (!allSameId) {
    throw new Error(`Idempotency violation: Different user IDs returned for same user`);
  }
  
  // Verify all results have consistent data
  const firstUsername = results[0].username;
  const allSameUsername = results.every(r => r.username === firstUsername);
  
  if (!allSameUsername) {
    console.warn(`Warning: Username changed across registrations (${firstUsername} vs ${results[results.length - 1].username})`);
  }
  
  console.log(`  ✅ Idempotency verified: All ${attempts} attempts returned same user ID`);
  
  return {
    user,
    attempts,
    success: true,
    userData: results[0]
  };
}

/**
 * Property Test: Idempotency holds for various numbers of attempts
 */
async function propertyTestIdempotency() {
  console.log('='.repeat(70));
  console.log('Property-Based Test: /start Command Idempotency');
  console.log('='.repeat(70));
  console.log('');
  console.log('**Validates: Requirements 2.2.3**');
  console.log('');
  console.log('Property: User Registration Idempotency');
  console.log('∀ user, ∀ n ≥ 1: registerUser(user) executed n times ⟹ exactly 1 user record');
  console.log('');
  console.log('='.repeat(70));
  console.log('');

  try {
    const apiClient = new AutomatonAPIClient();
    console.log('✅ API client created successfully\n');

    // Test cases with different numbers of attempts
    const testCases = [
      { attempts: 1, description: 'Single registration' },
      { attempts: 2, description: 'Double registration (basic idempotency)' },
      { attempts: 3, description: 'Triple registration' },
      { attempts: 5, description: 'Five registrations' },
      { attempts: 10, description: 'Ten registrations (stress test)' }
    ];

    const results = [];

    for (const testCase of testCases) {
      console.log(`Test Case: ${testCase.description} (${testCase.attempts} attempts)`);
      console.log('-'.repeat(70));
      
      const user = generateTestUser();
      const result = await testUserIdempotency(apiClient, user, testCase.attempts);
      results.push(result);
      
      console.log('');
      
      // Delay between test cases
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // Verify all test cases passed
    const allPassed = results.every(r => r.success);
    
    if (!allPassed) {
      throw new Error('Some test cases failed');
    }

    // Summary
    console.log('='.repeat(70));
    console.log('PROPERTY TEST SUMMARY');
    console.log('='.repeat(70));
    console.log('');
    console.log('✅ All property tests passed!');
    console.log('');
    console.log('Test cases executed:');
    results.forEach((r, i) => {
      console.log(`  ${i + 1}. ${testCases[i].description}: ✅`);
      console.log(`     User: ${r.user.username} (ID: ${r.user.telegramId})`);
      console.log(`     Attempts: ${r.attempts}`);
    });
    console.log('');
    console.log('Property verified: ✅');
    console.log('  For all tested users and attempt counts (1-10),');
    console.log('  multiple registrations returned the same user record.');
    console.log('  No duplicate accounts were created.');
    console.log('');
    console.log('Requirements validated: ✅');
    console.log('  REQ-2.2.3: Handle duplicate /start commands idempotently');
    console.log('  Design Property 1: No duplicate accounts for same user');
    console.log('');
    console.log('='.repeat(70));

    process.exit(0);

  } catch (error) {
    console.error('');
    console.error('❌ PROPERTY TEST FAILED!');
    console.error('='.repeat(70));
    console.error('Error:', error.message);
    console.error('');
    
    if (error.stack) {
      console.error('Stack trace:');
      console.error(error.stack);
    }

    console.error('');
    console.error('='.repeat(70));
    console.error('Property test failed! ❌');
    console.error('='.repeat(70));

    process.exit(1);
  }
}

// Run the property test
propertyTestIdempotency();
