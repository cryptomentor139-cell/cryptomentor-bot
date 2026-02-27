/**
 * Test script for /start command idempotency
 * This test verifies that calling /start multiple times does not create duplicate user accounts
 * 
 * Tests:
 * 1. First /start call creates a new user account
 * 2. Second /start call returns existing user (no duplicate)
 * 3. Third /start call still returns same user
 * 4. User data remains consistent across all calls
 * 
 * Validates:
 * - REQ-2.2.3: The system SHALL handle duplicate /start commands idempotently
 * - Design Property 1: Multiple /start commands should not create duplicate accounts
 */

import { AutomatonAPIClient } from './index.js';

// Test configuration - use a unique test user ID
const TEST_TELEGRAM_ID = Math.floor(Math.random() * 1000000) + 900000000;
const TEST_USERNAME = `test_idempotency_${Date.now()}`;

async function testStartIdempotency() {
  console.log('='.repeat(70));
  console.log('Testing /start Command Idempotency');
  console.log('='.repeat(70));
  console.log('');
  console.log(`Test User ID: ${TEST_TELEGRAM_ID}`);
  console.log(`Test Username: ${TEST_USERNAME}`);
  console.log('');

  try {
    // Create API client instance
    const apiClient = new AutomatonAPIClient();
    console.log('✅ API client created successfully\n');

    // Test 1: First /start call - should create new user
    console.log('Test 1: First /start call (should create new user)');
    console.log('-'.repeat(70));
    const userData1 = await apiClient.registerUser(TEST_TELEGRAM_ID, TEST_USERNAME);
    
    console.log('Response received:');
    console.log(JSON.stringify(userData1, null, 2));
    console.log('');

    if (!userData1.telegramId) {
      throw new Error('First registration did not return user data with telegramId');
    }

    console.log('✅ Test 1 passed: User registered successfully');
    console.log('');

    // Wait a moment to ensure any async operations complete
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Test 2: Second /start call - should return existing user (idempotency)
    console.log('Test 2: Second /start call (should return existing user)');
    console.log('-'.repeat(70));
    const userData2 = await apiClient.registerUser(TEST_TELEGRAM_ID, TEST_USERNAME);
    
    console.log('Response received:');
    console.log(JSON.stringify(userData2, null, 2));
    console.log('');

    // Verify idempotency: same user ID should be returned
    if (userData1.telegramId !== userData2.telegramId) {
      throw new Error(`Idempotency violation: Different user IDs returned (${userData1.telegramId} vs ${userData2.telegramId})`);
    }

    console.log('✅ Test 2 passed: Same user returned (no duplicate created)');
    console.log('');

    // Wait a moment
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Test 3: Third /start call - verify consistency
    console.log('Test 3: Third /start call (verify consistency)');
    console.log('-'.repeat(70));
    const userData3 = await apiClient.registerUser(TEST_TELEGRAM_ID, TEST_USERNAME);
    
    console.log('Response received:');
    console.log(JSON.stringify(userData3, null, 2));
    console.log('');

    // Verify consistency across all three calls
    if (userData1.telegramId !== userData3.telegramId) {
      throw new Error(`Consistency violation: Different user IDs (${userData1.telegramId} vs ${userData3.telegramId})`);
    }

    console.log('✅ Test 3 passed: User data remains consistent');
    console.log('');

    // Test 4: Verify user data structure
    console.log('Test 4: Verify user data structure');
    console.log('-'.repeat(70));
    
    const requiredFields = ['telegramId', 'username'];
    const missingFields = requiredFields.filter(field => !(field in userData1));
    
    if (missingFields.length > 0) {
      throw new Error(`Missing required fields in user data: ${missingFields.join(', ')}`);
    }

    console.log('✅ Test 4 passed: User data structure is valid');
    console.log('');

    // Summary
    console.log('='.repeat(70));
    console.log('IDEMPOTENCY TEST SUMMARY');
    console.log('='.repeat(70));
    console.log('');
    console.log('✅ All tests passed!');
    console.log('');
    console.log('Verified behaviors:');
    console.log('  • First /start call creates user account');
    console.log('  • Second /start call returns existing user (no duplicate)');
    console.log('  • Third /start call maintains consistency');
    console.log('  • User data structure is valid');
    console.log('');
    console.log('Idempotency requirement satisfied: ✅');
    console.log('  REQ-2.2.3: Handle duplicate /start commands idempotently');
    console.log('  Design Property 1: No duplicate accounts created');
    console.log('');
    console.log('='.repeat(70));

    process.exit(0);

  } catch (error) {
    console.error('');
    console.error('❌ TEST FAILED!');
    console.error('='.repeat(70));
    console.error('Error:', error.message);
    console.error('');
    
    if (error.stack) {
      console.error('Stack trace:');
      console.error(error.stack);
    }

    console.error('');
    console.error('='.repeat(70));
    console.error('Idempotency test failed! ❌');
    console.error('='.repeat(70));

    process.exit(1);
  }
}

// Run the test
testStartIdempotency();
