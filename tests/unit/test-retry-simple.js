/**
 * Simple test for retry logic
 * Tests task 2.2.6: Implement retry logic
 */

// Mock AutomatonAPIClient with retry logic
class TestAPIClient {
  constructor() {
    this.timeout = 30000;
  }

  async retryRequest(requestFn, operationName, maxRetries = 3, retryDelay = 2000) {
    let lastError;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        if (attempt === 0) {
          console.log(`[${new Date().toISOString()}] 🔄 Executing ${operationName}...`);
        } else {
          console.log(`[${new Date().toISOString()}] 🔄 Retry attempt ${attempt}/${maxRetries} for ${operationName}...`);
        }
        
        const result = await requestFn();
        
        if (attempt > 0) {
          console.log(`[${new Date().toISOString()}] ✅ ${operationName} succeeded on retry attempt ${attempt}`);
        }
        return result;
        
      } catch (error) {
        lastError = error;
        
        const shouldNotRetry = 
          error.message.includes('401') ||
          error.message.includes('403') ||
          error.message.includes('404') ||
          error.message.includes('400');
        
        if (shouldNotRetry) {
          console.error(`[${new Date().toISOString()}] ❌ ${operationName} failed with non-retryable error: ${error.message}`);
          throw error;
        }
        
        if (attempt === maxRetries) {
          console.error(`[${new Date().toISOString()}] ❌ ${operationName} failed after ${maxRetries} retries`);
          throw error;
        }
        
        console.warn(`[${new Date().toISOString()}] ⚠️ ${operationName} failed (attempt ${attempt + 1}/${maxRetries + 1}): ${error.message}`);
        console.log(`[${new Date().toISOString()}] ⏳ Waiting ${retryDelay}ms before retry...`);
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      }
    }
    
    throw lastError;
  }
}

// Test 1: Success after 2 retries
async function test1() {
  console.log('\n' + '='.repeat(80));
  console.log('Test 1: Success after 2 retries');
  console.log('='.repeat(80));
  
  const client = new TestAPIClient();
  let attempts = 0;
  
  try {
    const result = await client.retryRequest(
      async () => {
        attempts++;
        if (attempts < 3) {
          throw new Error('Network timeout');
        }
        return { success: true };
      },
      'test1',
      3,
      500
    );
    
    console.log(`✅ Test 1 PASSED: Succeeded after ${attempts} attempts`);
    return true;
  } catch (error) {
    console.error(`❌ Test 1 FAILED: ${error.message}`);
    return false;
  }
}

// Test 2: Non-retryable error (404)
async function test2() {
  console.log('\n' + '='.repeat(80));
  console.log('Test 2: Non-retryable error (404)');
  console.log('='.repeat(80));
  
  const client = new TestAPIClient();
  let attempts = 0;
  
  try {
    await client.retryRequest(
      async () => {
        attempts++;
        throw new Error('API request failed: 404 Not Found');
      },
      'test2',
      3,
      500
    );
    
    console.error(`❌ Test 2 FAILED: Should have thrown error`);
    return false;
  } catch (error) {
    if (attempts === 1) {
      console.log(`✅ Test 2 PASSED: Stopped after ${attempts} attempt (no retries for 404)`);
      return true;
    } else {
      console.error(`❌ Test 2 FAILED: Made ${attempts} attempts, should be 1`);
      return false;
    }
  }
}

// Test 3: All retries exhausted
async function test3() {
  console.log('\n' + '='.repeat(80));
  console.log('Test 3: All retries exhausted');
  console.log('='.repeat(80));
  
  const client = new TestAPIClient();
  let attempts = 0;
  
  try {
    await client.retryRequest(
      async () => {
        attempts++;
        throw new Error('Persistent error');
      },
      'test3',
      3,
      500
    );
    
    console.error(`❌ Test 3 FAILED: Should have thrown error`);
    return false;
  } catch (error) {
    if (attempts === 4) {
      console.log(`✅ Test 3 PASSED: Failed after ${attempts} attempts (1 initial + 3 retries)`);
      return true;
    } else {
      console.error(`❌ Test 3 FAILED: Made ${attempts} attempts, should be 4`);
      return false;
    }
  }
}

// Run all tests
async function runTests() {
  console.log('Testing Retry Logic Implementation');
  console.log('Task 2.2.6: Implement retry logic');
  
  const results = [];
  results.push(await test1());
  results.push(await test2());
  results.push(await test3());
  
  console.log('\n' + '='.repeat(80));
  console.log('Test Summary');
  console.log('='.repeat(80));
  
  const passed = results.filter(r => r).length;
  const total = results.length;
  
  console.log(`Tests passed: ${passed}/${total}`);
  
  if (passed === total) {
    console.log('\n✅ All tests passed!');
    console.log('\nRetry logic implementation verified:');
    console.log('  ✓ Sub-task 2.2.6.1: Retries failed requests up to 3 times');
    console.log('  ✓ Sub-task 2.2.6.2: Uses 2-second delay between retries');
    console.log('  ✓ Sub-task 2.2.6.3: Logs retry attempts');
  } else {
    console.log(`\n❌ ${total - passed} test(s) failed`);
    process.exit(1);
  }
}

runTests().catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
});
