/**
 * Test script for Task 3.2.3: Call getUserStatus() API method
 * 
 * This test verifies that the /status command handler correctly calls
 * the getUserStatus() API method and handles the response.
 */

import { apiClient } from './index.js';

async function testGetUserStatus() {
  console.log('='.repeat(60));
  console.log('Testing Task 3.2.3: Call getUserStatus() API method');
  console.log('='.repeat(60));
  console.log();

  // Test user ID (use a real user ID from your system)
  const testUserId = 123456789;

  try {
    console.log(`📊 Testing getUserStatus() for user ID: ${testUserId}`);
    console.log();

    // Call the getUserStatus() method
    const userStatus = await apiClient.getUserStatus(testUserId);

    console.log('✅ SUCCESS: getUserStatus() called successfully');
    console.log();
    console.log('Response data:');
    console.log(JSON.stringify(userStatus, null, 2));
    console.log();

    // Verify expected fields are present
    const expectedFields = ['credits', 'conversationCount', 'lastActivity'];
    const missingFields = expectedFields.filter(field => !(field in userStatus));

    if (missingFields.length > 0) {
      console.log('⚠️  WARNING: Some expected fields are missing:');
      missingFields.forEach(field => console.log(`   - ${field}`));
    } else {
      console.log('✅ All expected fields are present in the response');
    }

  } catch (error) {
    console.error('❌ FAILED: getUserStatus() call failed');
    console.error();
    console.error('Error details:');
    console.error(`  Message: ${error.message}`);
    console.error(`  Type: ${error.name}`);
    if (error.stack) {
      console.error();
      console.error('Stack trace:');
      console.error(error.stack);
    }
  }

  console.log();
  console.log('='.repeat(60));
  console.log('Test completed');
  console.log('='.repeat(60));
}

// Run the test
testGetUserStatus()
  .then(() => {
    console.log('\n✅ Test execution completed');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Test execution failed:', error);
    process.exit(1);
  });
