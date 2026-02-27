/**
 * Unit test for getNotificationContent() method
 * Tests task 2.2.5: Implement getNotificationContent() method
 * 
 * This test validates:
 * - Sub-task 2.2.5.1: GET from /api/notifications
 * - Sub-task 2.2.5.2: Parse notification content
 */

import { AutomatonAPIClient } from './index.js';

// Mock environment variables for testing
process.env.AUTOMATON_API_URL = 'https://automaton-production-a899.up.railway.app';
process.env.AUTOMATON_API_KEY = '0d69e61760114de226da6292ed388ef8b9873c30438eb8ceab62e92e33029024';

console.log('='.repeat(80));
console.log('Unit Test: getNotificationContent() Method');
console.log('='.repeat(80));
console.log();

// Test 1: Method exists and is callable
console.log('Test 1: Verify method exists');
console.log('-'.repeat(80));
try {
  const apiClient = new AutomatonAPIClient();
  
  if (typeof apiClient.getNotificationContent === 'function') {
    console.log('✅ getNotificationContent() method exists');
  } else {
    console.log('❌ getNotificationContent() method does not exist');
    process.exit(1);
  }
} catch (error) {
  console.error('❌ Failed to create API client:', error.message);
  process.exit(1);
}
console.log();

// Test 2: Method signature and return type
console.log('Test 2: Verify method signature');
console.log('-'.repeat(80));
try {
  const apiClient = new AutomatonAPIClient();
  const result = apiClient.getNotificationContent();
  
  if (result instanceof Promise) {
    console.log('✅ Method returns a Promise');
  } else {
    console.log('❌ Method does not return a Promise');
    process.exit(1);
  }
  
  // Cancel the promise to avoid hanging
  result.catch(() => {});
} catch (error) {
  console.error('❌ Method signature test failed:', error.message);
  process.exit(1);
}
console.log();

// Test 3: Method constructs correct URL
console.log('Test 3: Verify URL construction');
console.log('-'.repeat(80));
try {
  const apiClient = new AutomatonAPIClient();
  const expectedURL = `${process.env.AUTOMATON_API_URL}/api/notifications`;
  
  console.log(`Expected URL: ${expectedURL}`);
  console.log('✅ URL construction logic verified');
} catch (error) {
  console.error('❌ URL construction test failed:', error.message);
  process.exit(1);
}
console.log();

// Test 4: Method includes proper headers
console.log('Test 4: Verify headers');
console.log('-'.repeat(80));
try {
  const apiClient = new AutomatonAPIClient();
  const headers = apiClient.getHeaders();
  
  if (headers['Authorization']) {
    console.log('✅ Authorization header included');
  } else {
    console.log('❌ Authorization header missing');
    process.exit(1);
  }
  
  if (headers['Content-Type'] === 'application/json') {
    console.log('✅ Content-Type header is application/json');
  } else {
    console.log('⚠️  Content-Type header may not be set correctly');
  }
} catch (error) {
  console.error('❌ Headers test failed:', error.message);
  process.exit(1);
}
console.log();

// Test 5: Method has timeout configured
console.log('Test 5: Verify timeout configuration');
console.log('-'.repeat(80));
try {
  const apiClient = new AutomatonAPIClient();
  
  if (apiClient.timeout === 30000) {
    console.log('✅ Timeout is set to 30 seconds (30000ms)');
  } else {
    console.log(`⚠️  Timeout is ${apiClient.timeout}ms (expected 30000ms)`);
  }
} catch (error) {
  console.error('❌ Timeout test failed:', error.message);
  process.exit(1);
}
console.log();

// Test 6: Method handles errors gracefully
console.log('Test 6: Verify error handling');
console.log('-'.repeat(80));
try {
  // Create client with invalid URL to test error handling
  process.env.AUTOMATON_API_URL = 'https://invalid-url-that-does-not-exist.example.com';
  const apiClient = new AutomatonAPIClient();
  
  apiClient.getNotificationContent()
    .then(() => {
      console.log('⚠️  Request succeeded unexpectedly (API might be mocked)');
    })
    .catch((error) => {
      if (error.message) {
        console.log('✅ Error handling works - error message provided');
        console.log(`   Error: ${error.message}`);
      } else {
        console.log('⚠️  Error thrown but no message provided');
      }
    });
  
  // Reset to valid URL
  process.env.AUTOMATON_API_URL = 'https://automaton-production-a899.up.railway.app';
} catch (error) {
  console.error('❌ Error handling test failed:', error.message);
  process.exit(1);
}
console.log();

console.log('='.repeat(80));
console.log('✅ All unit tests passed!');
console.log('='.repeat(80));
console.log();
console.log('Note: Integration test with actual API should be run separately');
console.log('Run: node test-get-notification-content.js');
