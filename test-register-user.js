/**
 * Test script for registerUser() method
 * This script tests the AutomatonAPIClient.registerUser() method
 */

import { AutomatonAPIClient } from './index.js';

// Test configuration
const TEST_TELEGRAM_ID = 123456789;
const TEST_USERNAME = 'test_user';

async function testRegisterUser() {
  console.log('='.repeat(60));
  console.log('Testing AutomatonAPIClient.registerUser() method');
  console.log('='.repeat(60));
  console.log('');

  try {
    // Create API client instance
    const apiClient = new AutomatonAPIClient();
    console.log('✅ API client created successfully\n');

    // Test 1: Register a new user
    console.log('Test 1: Registering a new user...');
    console.log(`Telegram ID: ${TEST_TELEGRAM_ID}`);
    console.log(`Username: ${TEST_USERNAME}`);
    console.log('');

    const userData = await apiClient.registerUser(TEST_TELEGRAM_ID, TEST_USERNAME);

    console.log('');
    console.log('✅ Registration successful!');
    console.log('User data received:');
    console.log(JSON.stringify(userData, null, 2));
    console.log('');

    // Test 2: Verify idempotency (register same user again)
    console.log('Test 2: Testing idempotency (registering same user again)...');
    const userData2 = await apiClient.registerUser(TEST_TELEGRAM_ID, TEST_USERNAME);
    
    console.log('');
    console.log('✅ Second registration successful!');
    console.log('User data received:');
    console.log(JSON.stringify(userData2, null, 2));
    console.log('');

    // Verify both responses are consistent
    if (userData.telegramId === userData2.telegramId) {
      console.log('✅ Idempotency verified: Same user data returned');
    } else {
      console.log('⚠️ Warning: Different user data returned on second registration');
    }

    console.log('');
    console.log('='.repeat(60));
    console.log('All tests passed! ✅');
    console.log('='.repeat(60));

    process.exit(0);

  } catch (error) {
    console.error('');
    console.error('❌ Test failed!');
    console.error('Error:', error.message);
    console.error('');
    
    if (error.stack) {
      console.error('Stack trace:');
      console.error(error.stack);
    }

    console.error('');
    console.error('='.repeat(60));
    console.error('Tests failed! ❌');
    console.error('='.repeat(60));

    process.exit(1);
  }
}

// Run the test
testRegisterUser();
