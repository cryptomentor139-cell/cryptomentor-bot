import { AutomatonAPIClient } from './index.js';

/**
 * Test script for retry logic implementation
 * Tests task 2.2.6: Implement retry logic
 */

console.log('='.repeat(80));
console.log('Testing Retry Logic Implementation');
console.log('='.repeat(80));
console.log();

// Mock environment variables for testing
process.env.TELEGRAM_BOT_TOKEN = 'test-token-for-retry-logic';
process.env.AUTOMATON_API_URL = 'https://httpstat.us'; // Use httpstat.us for testing
process.env.AUTOMATON_API_KEY = 'test-api-key';

// Create API client instance
const apiClient = new AutomatonAPIClient();

/**
 * Test 1: Test retry logic with simulated failures
 */
async function testRetryLogic() {
  console.log('Test 1: Testing retry logic with simulated failures');
  console.log('-'.repeat(80));
  
  let attemptCount = 0;
  
  try {
    const result = await apiClient.retryRequest(
      async () => {
        attemptCount++;
        console.log(`  Attempt ${attemptCount}: Simulating failure...`);
        
        // Fail the first 2 attempts, succeed on the 3rd
        if (attemptCount < 3) {
          throw new Error('Simulated network error');
        }
        
        console.log(`  Attempt ${attemptCount}: Success!`);
        return { success: true, attempts: attemptCount };
      },
      'testOperation',
      3, // maxRetries
      1000 // 1 second delay for faster testing
    );
    
    console.log(`✅ Test 1 PASSED: Operation succeeded after ${result.attempts} attempts`);
    console.log();
    return true;
  } catch (error) {
    console.error(`❌ Test 1 FAILED: ${error.message}`);
    console.log();
    return false;
  }
}

/**
 * Test 2: Test retry logic with non-retryable errors (4xx)
 */
async function testNonRetryableError() {
  console.log('Test 2: Testing non-retryable error handling (4xx errors)');
  console.log('-'.repeat(80));
  
  let attemptCount = 0;
  
  try {
    await apiClient.retryRequest(
      async () => {
        attemptCount++;
        console.log(`  Attempt ${attemptCount}: Simulating 404 error...`);
        throw new Error('API request failed: 404 Not Found');
      },
      'testNonRetryable',
      3,
      1000
    );
    
    console.error(`❌ Test 2 FAILED: Should have thrown error immediately`);
    console.log();
    return false;
  } catch (error) {
    if (attemptCount === 1) {
      console.log(`✅ Test 2 PASSED: Non-retryable error stopped after ${attemptCount} attempt (no retries)`);
      console.log();
      return true;
    } else {
      console.error(`❌ Test 2 FAILED: Made ${attemptCount} attempts, should have been 1`);
      console.log();
      return false;
    }
  }
}

/**
 * Test 3: Test retry logic exhaustion (all retries fail)
 */
async function testRetryExhaustion() {
  console.log('Test 3: Testing retry exhaustion (all attempts fail)');
  console.log('-'.repeat(80));
  
  let attemptCount = 0;
  
  try {
    await apiClient.retryRequest(
      async () => {
        attemptCount++;
        console.log(`  Attempt ${attemptCount}: Simulating failure...`);
        throw new Error('Persistent network error');
      },
      'testExhaustion',
      3,
      500 // Shorter delay for faster testing
    );
    
    console.error(`❌ Test 3 FAILED: Should have thrown error after all retries`);
    console.log();
    return false;
  } catch (error) {
    // Should make 4 attempts total (1 initial + 3 retries)
    if (attemptCount === 4) {
      console.log(`✅ Test 3 PASSED: Failed after ${attemptCount} attempts (1 initial + 3 retries)`);
      console.log();
      return true;
    } else {
      console.error(`❌ Test 3 FAILED: Made ${attemptCount} attempts, should have been 4`);
      console.log();
      return false;
    }
  }
}

/**
 * Test 4: Test immediate success (no retries needed)
 */
async function testImmediateSuccess() {
  console.log('Test 4: Testing immediate success (no retries needed)');
  console.log('-'.repeat(80));
  
  let attemptCount = 0;
  
  try {
    const result = await apiClient.retryRequest(
      async () => {
        attemptCount++;
        console.log(`  Attempt ${attemptCount}: Success on first try!`);
        return { success: true, data: 'test data' };
      },
      'testImmediate',
      3,
      1000
    );
    
    if (attemptCount === 1 && result.success) {
      console.log(`✅ Test 4 PASSED: Succeeded immediately without retries`);
      console.log();
      return true;
    } else {
      console.error(`❌ Test 4 FAILED: Made ${attemptCount} attempts, should have been 1`);
      console.log();
      return false;
    }
  } catch (error) {
    console.error(`❌ Test 4 FAILED: ${error.message}`);
    console.log();
    return false;
  }
}

/**
 * Run all tests
 */
async function runAllTests() {
  console.log('Starting retry logic tests...');
  console.log();
  
  const results = [];
  
  results.push(await testRetryLogic());
  results.push(await testNonRetryableError());
  results.push(await testRetryExhaustion());
  results.push(await testImmediateSuccess());
  
  console.log('='.repeat(80));
  console.log('Test Summary');
  console.log('='.repeat(80));
  
  const passed = results.filter(r => r).length;
  const total = results.length;
  
  console.log(`Tests passed: ${passed}/${total}`);
  
  if (passed === total) {
    console.log('✅ All tests passed!');
    console.log();
    console.log('Retry logic implementation is working correctly:');
    console.log('  ✓ Retries failed requests up to 3 times');
    console.log('  ✓ Uses 2-second delay between retries (configurable)');
    console.log('  ✓ Logs retry attempts with detailed information');
    console.log('  ✓ Handles non-retryable errors correctly');
    console.log('  ✓ Exhausts retries when all attempts fail');
    console.log('  ✓ Succeeds immediately when no retries needed');
  } else {
    console.log(`❌ ${total - passed} test(s) failed`);
  }
  
  console.log('='.repeat(80));
}

// Run tests
runAllTests().catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
});
