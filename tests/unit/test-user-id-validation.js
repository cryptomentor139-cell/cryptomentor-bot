/**
 * Unit Tests for Telegram User ID Validation
 * Tests task 5.3.1: Validate Telegram user IDs
 * 
 * This test suite validates:
 * - REQ-3.3.3: The system SHALL validate Telegram user IDs before processing requests
 * - REQ-2.8.6: The system SHALL validate all user input before processing
 */

import { isValidTelegramUserId, validateMessageUser } from './index.js';

// Test counter
let testsPassed = 0;
let testsFailed = 0;

/**
 * Helper function to run a test
 */
function test(description, testFn) {
  try {
    testFn();
    console.log(`✅ PASS: ${description}`);
    testsPassed++;
  } catch (error) {
    console.error(`❌ FAIL: ${description}`);
    console.error(`   Error: ${error.message}`);
    testsFailed++;
  }
}

/**
 * Helper function to assert equality
 */
function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(`${message}\n   Expected: ${expected}\n   Actual: ${actual}`);
  }
}

/**
 * Helper function to assert truthiness
 */
function assertTrue(value, message) {
  if (!value) {
    throw new Error(message);
  }
}

/**
 * Helper function to assert falsiness
 */
function assertFalse(value, message) {
  if (value) {
    throw new Error(message);
  }
}

console.log('='.repeat(80));
console.log('Running Telegram User ID Validation Tests');
console.log('='.repeat(80));
console.log();

// ============================================================================
// Test Suite 1: isValidTelegramUserId() - Valid User IDs
// ============================================================================

console.log('Test Suite 1: isValidTelegramUserId() - Valid User IDs');
console.log('-'.repeat(80));

test('Should accept valid positive integer user ID', () => {
  const result = isValidTelegramUserId(123456789);
  assertTrue(result, 'Valid user ID should return true');
});

test('Should accept user ID of 1 (minimum valid ID)', () => {
  const result = isValidTelegramUserId(1);
  assertTrue(result, 'User ID 1 should be valid');
});

test('Should accept large valid user ID', () => {
  const result = isValidTelegramUserId(9876543210);
  assertTrue(result, 'Large user ID should be valid');
});

test('Should accept user ID at MAX_SAFE_INTEGER', () => {
  const result = isValidTelegramUserId(Number.MAX_SAFE_INTEGER);
  assertTrue(result, 'MAX_SAFE_INTEGER should be valid');
});

console.log();

// ============================================================================
// Test Suite 2: isValidTelegramUserId() - Invalid User IDs
// ============================================================================

console.log('Test Suite 2: isValidTelegramUserId() - Invalid User IDs');
console.log('-'.repeat(80));

test('Should reject null user ID', () => {
  const result = isValidTelegramUserId(null);
  assertFalse(result, 'Null user ID should be invalid');
});

test('Should reject undefined user ID', () => {
  const result = isValidTelegramUserId(undefined);
  assertFalse(result, 'Undefined user ID should be invalid');
});

test('Should reject NaN user ID', () => {
  const result = isValidTelegramUserId(NaN);
  assertFalse(result, 'NaN user ID should be invalid');
});

test('Should reject zero user ID', () => {
  const result = isValidTelegramUserId(0);
  assertFalse(result, 'Zero user ID should be invalid');
});

test('Should reject negative user ID', () => {
  const result = isValidTelegramUserId(-123456789);
  assertFalse(result, 'Negative user ID should be invalid');
});

test('Should reject float user ID', () => {
  const result = isValidTelegramUserId(123.456);
  assertFalse(result, 'Float user ID should be invalid');
});

test('Should reject string user ID', () => {
  const result = isValidTelegramUserId('123456789');
  assertFalse(result, 'String user ID should be invalid');
});

test('Should reject object user ID', () => {
  const result = isValidTelegramUserId({ id: 123456789 });
  assertFalse(result, 'Object user ID should be invalid');
});

test('Should reject array user ID', () => {
  const result = isValidTelegramUserId([123456789]);
  assertFalse(result, 'Array user ID should be invalid');
});

test('Should reject boolean user ID', () => {
  const result = isValidTelegramUserId(true);
  assertFalse(result, 'Boolean user ID should be invalid');
});

test('Should reject user ID exceeding MAX_SAFE_INTEGER', () => {
  const result = isValidTelegramUserId(Number.MAX_SAFE_INTEGER + 1);
  assertFalse(result, 'User ID exceeding MAX_SAFE_INTEGER should be invalid');
});

console.log();

// ============================================================================
// Test Suite 3: validateMessageUser() - Valid Messages
// ============================================================================

console.log('Test Suite 3: validateMessageUser() - Valid Messages');
console.log('-'.repeat(80));

test('Should validate message with valid user ID', () => {
  const msg = {
    from: {
      id: 123456789,
      username: 'testuser',
      first_name: 'Test'
    },
    chat: {
      id: 123456789
    }
  };
  
  const result = validateMessageUser(msg);
  assertTrue(result.valid, 'Message with valid user should be valid');
  assertEqual(result.userId, 123456789, 'Should extract correct user ID');
  assertEqual(result.error, null, 'Should have no error');
});

test('Should validate message with minimum valid user ID', () => {
  const msg = {
    from: {
      id: 1,
      username: 'user1'
    },
    chat: {
      id: 1
    }
  };
  
  const result = validateMessageUser(msg);
  assertTrue(result.valid, 'Message with user ID 1 should be valid');
  assertEqual(result.userId, 1, 'Should extract user ID 1');
});

test('Should validate message with large user ID', () => {
  const msg = {
    from: {
      id: 9876543210,
      first_name: 'LargeID'
    },
    chat: {
      id: 9876543210
    }
  };
  
  const result = validateMessageUser(msg);
  assertTrue(result.valid, 'Message with large user ID should be valid');
  assertEqual(result.userId, 9876543210, 'Should extract correct large user ID');
});

console.log();

// ============================================================================
// Test Suite 4: validateMessageUser() - Invalid Messages
// ============================================================================

console.log('Test Suite 4: validateMessageUser() - Invalid Messages');
console.log('-'.repeat(80));

test('Should reject null message', () => {
  const result = validateMessageUser(null);
  assertFalse(result.valid, 'Null message should be invalid');
  assertEqual(result.userId, null, 'User ID should be null');
  assertTrue(result.error.includes('null or undefined'), 'Error should mention null/undefined');
});

test('Should reject undefined message', () => {
  const result = validateMessageUser(undefined);
  assertFalse(result.valid, 'Undefined message should be invalid');
  assertEqual(result.userId, null, 'User ID should be null');
});

test('Should reject message without from property', () => {
  const msg = {
    chat: {
      id: 123456789
    }
  };
  
  const result = validateMessageUser(msg);
  assertFalse(result.valid, 'Message without from property should be invalid');
  assertEqual(result.userId, null, 'User ID should be null');
  assertTrue(result.error.includes('msg.from'), 'Error should mention missing msg.from');
});

test('Should reject message with null from property', () => {
  const msg = {
    from: null,
    chat: {
      id: 123456789
    }
  };
  
  const result = validateMessageUser(msg);
  assertFalse(result.valid, 'Message with null from property should be invalid');
  assertEqual(result.userId, null, 'User ID should be null');
});

test('Should reject message with invalid user ID (zero)', () => {
  const msg = {
    from: {
      id: 0,
      username: 'invalid'
    },
    chat: {
      id: 123456789
    }
  };
  
  const result = validateMessageUser(msg);
  assertFalse(result.valid, 'Message with zero user ID should be invalid');
  assertEqual(result.userId, 0, 'Should extract the invalid user ID');
  assertTrue(result.error.includes('Invalid Telegram user ID'), 'Error should mention invalid user ID');
});

test('Should reject message with negative user ID', () => {
  const msg = {
    from: {
      id: -123456789,
      username: 'negative'
    },
    chat: {
      id: 123456789
    }
  };
  
  const result = validateMessageUser(msg);
  assertFalse(result.valid, 'Message with negative user ID should be invalid');
  assertEqual(result.userId, -123456789, 'Should extract the invalid user ID');
});

test('Should reject message with string user ID', () => {
  const msg = {
    from: {
      id: '123456789',
      username: 'stringid'
    },
    chat: {
      id: 123456789
    }
  };
  
  const result = validateMessageUser(msg);
  assertFalse(result.valid, 'Message with string user ID should be invalid');
  assertEqual(result.userId, '123456789', 'Should extract the invalid user ID');
});

test('Should reject message with null user ID', () => {
  const msg = {
    from: {
      id: null,
      username: 'nullid'
    },
    chat: {
      id: 123456789
    }
  };
  
  const result = validateMessageUser(msg);
  assertFalse(result.valid, 'Message with null user ID should be invalid');
  assertEqual(result.userId, null, 'Should extract null user ID');
});

test('Should reject message with undefined user ID', () => {
  const msg = {
    from: {
      username: 'noid'
    },
    chat: {
      id: 123456789
    }
  };
  
  const result = validateMessageUser(msg);
  assertFalse(result.valid, 'Message with undefined user ID should be invalid');
  assertEqual(result.userId, undefined, 'Should extract undefined user ID');
});

console.log();

// ============================================================================
// Test Results Summary
// ============================================================================

console.log('='.repeat(80));
console.log('Test Results Summary');
console.log('='.repeat(80));
console.log(`Total Tests: ${testsPassed + testsFailed}`);
console.log(`✅ Passed: ${testsPassed}`);
console.log(`❌ Failed: ${testsFailed}`);
console.log();

if (testsFailed === 0) {
  console.log('🎉 All tests passed!');
  console.log();
  console.log('✅ Task 5.3.1 Implementation Verified:');
  console.log('   - Telegram user IDs are validated before processing');
  console.log('   - Invalid user IDs are rejected with appropriate error messages');
  console.log('   - REQ-3.3.3: User ID validation implemented');
  console.log('   - REQ-2.8.6: Input validation implemented');
  process.exit(0);
} else {
  console.log('❌ Some tests failed. Please review the implementation.');
  process.exit(1);
}
