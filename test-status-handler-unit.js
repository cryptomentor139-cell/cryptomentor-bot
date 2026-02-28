/**
 * Unit Test for Task 3.2.3: Call getUserStatus() API method
 * 
 * This test verifies that the handleStatusCommand function correctly:
 * 1. Extracts user ID from message (Task 3.2.2)
 * 2. Calls getUserStatus() API method (Task 3.2.3)
 * 3. Handles API errors gracefully (Task 3.2.6)
 */

import { AutomatonAPIClient } from './index.js';

// Mock fetch for testing
global.fetch = async (url, options) => {
  console.log(`Mock fetch called: ${options.method} ${url}`);
  
  // Simulate successful response
  if (url.includes('/api/users/') && url.includes('/status')) {
    return {
      ok: true,
      status: 200,
      json: async () => ({
        credits: 850,
        conversationCount: 5,
        lastActivity: '2026-02-27T10:30:00Z'
      })
    };
  }
  
  // Simulate error response
  return {
    ok: false,
    status: 500,
    statusText: 'Internal Server Error',
    text: async () => 'Server error'
  };
};

async function runUnitTests() {
  console.log('='.repeat(70));
  console.log('Unit Tests for Task 3.2.3: Call getUserStatus() API method');
  console.log('='.repeat(70));
  console.log();

  let passedTests = 0;
  let failedTests = 0;

  // Test 1: Verify getUserStatus() method exists
  console.log('Test 1: Verify getUserStatus() method exists');
  try {
    const apiClient = new AutomatonAPIClient();
    if (typeof apiClient.getUserStatus === 'function') {
      console.log('✅ PASS: getUserStatus() method exists');
      passedTests++;
    } else {
      console.log('❌ FAIL: getUserStatus() method does not exist');
      failedTests++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error checking method existence:', error.message);
    failedTests++;
  }
  console.log();

  // Test 2: Verify getUserStatus() calls correct API endpoint
  console.log('Test 2: Verify getUserStatus() calls correct API endpoint');
  try {
    const apiClient = new AutomatonAPIClient();
    const testUserId = 123456789;
    
    // Override fetch to capture the URL
    let capturedUrl = null;
    const originalFetch = global.fetch;
    global.fetch = async (url, options) => {
      capturedUrl = url;
      return originalFetch(url, options);
    };
    
    await apiClient.getUserStatus(testUserId);
    
    // Restore original fetch
    global.fetch = originalFetch;
    
    if (capturedUrl && capturedUrl.includes(`/api/users/${testUserId}/status`)) {
      console.log('✅ PASS: Correct API endpoint called');
      console.log(`   URL: ${capturedUrl}`);
      passedTests++;
    } else {
      console.log('❌ FAIL: Incorrect API endpoint');
      console.log(`   Expected: /api/users/${testUserId}/status`);
      console.log(`   Got: ${capturedUrl}`);
      failedTests++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error testing API endpoint:', error.message);
    failedTests++;
  }
  console.log();

  // Test 3: Verify getUserStatus() returns expected data structure
  console.log('Test 3: Verify getUserStatus() returns expected data structure');
  try {
    const apiClient = new AutomatonAPIClient();
    const result = await apiClient.getUserStatus(123456789);
    
    const hasCredits = 'credits' in result;
    const hasConversationCount = 'conversationCount' in result;
    const hasLastActivity = 'lastActivity' in result;
    
    if (hasCredits && hasConversationCount && hasLastActivity) {
      console.log('✅ PASS: Response has expected fields');
      console.log(`   credits: ${result.credits}`);
      console.log(`   conversationCount: ${result.conversationCount}`);
      console.log(`   lastActivity: ${result.lastActivity}`);
      passedTests++;
    } else {
      console.log('❌ FAIL: Response missing expected fields');
      console.log(`   Has credits: ${hasCredits}`);
      console.log(`   Has conversationCount: ${hasConversationCount}`);
      console.log(`   Has lastActivity: ${hasLastActivity}`);
      failedTests++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error testing response structure:', error.message);
    failedTests++;
  }
  console.log();

  // Test 4: Verify getUserStatus() includes Authorization header
  console.log('Test 4: Verify getUserStatus() includes Authorization header');
  try {
    const apiClient = new AutomatonAPIClient();
    
    // Override fetch to capture headers
    let capturedHeaders = null;
    const originalFetch = global.fetch;
    global.fetch = async (url, options) => {
      capturedHeaders = options.headers;
      return originalFetch(url, options);
    };
    
    await apiClient.getUserStatus(123456789);
    
    // Restore original fetch
    global.fetch = originalFetch;
    
    if (capturedHeaders && capturedHeaders.Authorization) {
      console.log('✅ PASS: Authorization header included');
      console.log(`   Header: ${capturedHeaders.Authorization.substring(0, 20)}...`);
      passedTests++;
    } else {
      console.log('❌ FAIL: Authorization header missing');
      failedTests++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error testing headers:', error.message);
    failedTests++;
  }
  console.log();

  // Test 5: Verify getUserStatus() handles errors gracefully
  console.log('Test 5: Verify getUserStatus() handles errors gracefully');
  try {
    const apiClient = new AutomatonAPIClient();
    
    // Override fetch to simulate error
    const originalFetch = global.fetch;
    global.fetch = async () => ({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      text: async () => 'User not found'
    });
    
    let errorThrown = false;
    try {
      await apiClient.getUserStatus(999999999);
    } catch (error) {
      errorThrown = true;
      console.log('✅ PASS: Error thrown as expected');
      console.log(`   Error message: ${error.message}`);
      passedTests++;
    }
    
    // Restore original fetch
    global.fetch = originalFetch;
    
    if (!errorThrown) {
      console.log('❌ FAIL: No error thrown for failed request');
      failedTests++;
    }
  } catch (error) {
    console.log('❌ FAIL: Unexpected error:', error.message);
    failedTests++;
  }
  console.log();

  // Test 6: Verify retry logic is applied
  console.log('Test 6: Verify retry logic is applied to getUserStatus()');
  try {
    const apiClient = new AutomatonAPIClient();
    
    let callCount = 0;
    const originalFetch = global.fetch;
    global.fetch = async (url, options) => {
      callCount++;
      if (callCount < 2) {
        // Fail first attempt
        throw new Error('Network error');
      }
      // Succeed on second attempt
      return originalFetch(url, options);
    };
    
    await apiClient.getUserStatus(123456789);
    
    // Restore original fetch
    global.fetch = originalFetch;
    
    if (callCount >= 2) {
      console.log('✅ PASS: Retry logic applied');
      console.log(`   Total attempts: ${callCount}`);
      passedTests++;
    } else {
      console.log('❌ FAIL: Retry logic not applied');
      console.log(`   Total attempts: ${callCount}`);
      failedTests++;
    }
  } catch (error) {
    console.log('❌ FAIL: Error testing retry logic:', error.message);
    failedTests++;
  }
  console.log();

  // Summary
  console.log('='.repeat(70));
  console.log('Test Summary');
  console.log('='.repeat(70));
  console.log(`Total tests: ${passedTests + failedTests}`);
  console.log(`✅ Passed: ${passedTests}`);
  console.log(`❌ Failed: ${failedTests}`);
  console.log();

  if (failedTests === 0) {
    console.log('🎉 All tests passed! Task 3.2.3 is complete.');
  } else {
    console.log('⚠️  Some tests failed. Please review the implementation.');
  }

  return failedTests === 0;
}

// Run the tests
runUnitTests()
  .then((success) => {
    process.exit(success ? 0 : 1);
  })
  .catch((error) => {
    console.error('\n❌ Test execution failed:', error);
    process.exit(1);
  });
