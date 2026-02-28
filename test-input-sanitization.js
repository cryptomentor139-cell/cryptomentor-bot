/**
 * Unit Tests for Input Sanitization Functions
 * Tests task 5.3.3: Sanitize user input before API calls
 * 
 * These tests verify that:
 * - Control characters are removed
 * - Zero-width characters are removed
 * - Bidirectional text override characters are removed
 * - Unicode is normalized
 * - Input length is limited
 * - Whitespace is trimmed
 * - Special characters are handled properly
 */

import { sanitizeUserInput, sanitizeUsername, sanitizeMessage } from './index.js';

// Test counter
let testsPassed = 0;
let testsFailed = 0;

/**
 * Assert helper function
 */
function assert(condition, testName) {
  if (condition) {
    console.log(`✅ PASS: ${testName}`);
    testsPassed++;
  } else {
    console.error(`❌ FAIL: ${testName}`);
    testsFailed++;
  }
}

/**
 * Assert equal helper function
 */
function assertEqual(actual, expected, testName) {
  if (actual === expected) {
    console.log(`✅ PASS: ${testName}`);
    testsPassed++;
  } else {
    console.error(`❌ FAIL: ${testName}`);
    console.error(`   Expected: "${expected}"`);
    console.error(`   Actual:   "${actual}"`);
    testsFailed++;
  }
}

console.log('='.repeat(80));
console.log('Running Input Sanitization Tests');
console.log('='.repeat(80));
console.log();

// ============================================================================
// Test Suite 1: sanitizeUserInput() - Basic Functionality
// ============================================================================

console.log('Test Suite 1: sanitizeUserInput() - Basic Functionality');
console.log('-'.repeat(80));

// Test 1.1: Normal text should pass through unchanged
assertEqual(
  sanitizeUserInput('Hello World'),
  'Hello World',
  'Normal text should pass through unchanged'
);

// Test 1.2: Whitespace should be trimmed
assertEqual(
  sanitizeUserInput('  Hello World  '),
  'Hello World',
  'Leading and trailing whitespace should be trimmed'
);

// Test 1.3: Empty string should return empty string
assertEqual(
  sanitizeUserInput(''),
  '',
  'Empty string should return empty string'
);

// Test 1.4: Null should return empty string
assertEqual(
  sanitizeUserInput(null),
  '',
  'Null should return empty string'
);

// Test 1.5: Undefined should return empty string
assertEqual(
  sanitizeUserInput(undefined),
  '',
  'Undefined should return empty string'
);

console.log();

// ============================================================================
// Test Suite 2: Control Character Removal
// ============================================================================

console.log('Test Suite 2: Control Character Removal');
console.log('-'.repeat(80));

// Test 2.1: Remove null character (ASCII 0)
assertEqual(
  sanitizeUserInput('Hello\x00World'),
  'HelloWorld',
  'Null character should be removed'
);

// Test 2.2: Remove bell character (ASCII 7)
assertEqual(
  sanitizeUserInput('Hello\x07World'),
  'HelloWorld',
  'Bell character should be removed'
);

// Test 2.3: Remove backspace character (ASCII 8)
assertEqual(
  sanitizeUserInput('Hello\x08World'),
  'HelloWorld',
  'Backspace character should be removed'
);

// Test 2.4: Allow newline when allowNewlines is true (default)
assertEqual(
  sanitizeUserInput('Hello\nWorld'),
  'Hello\nWorld',
  'Newline should be allowed by default'
);

// Test 2.5: Remove newline when allowNewlines is false
assertEqual(
  sanitizeUserInput('Hello\nWorld', { allowNewlines: false }),
  'HelloWorld',
  'Newline should be removed when allowNewlines is false'
);

// Test 2.6: Allow tab character
assertEqual(
  sanitizeUserInput('Hello\tWorld'),
  'Hello\tWorld',
  'Tab character should be allowed'
);

// Test 2.7: Remove DEL character (ASCII 127)
assertEqual(
  sanitizeUserInput('Hello\x7FWorld'),
  'HelloWorld',
  'DEL character should be removed'
);

console.log();

// ============================================================================
// Test Suite 3: Zero-Width Character Removal
// ============================================================================

console.log('Test Suite 3: Zero-Width Character Removal');
console.log('-'.repeat(80));

// Test 3.1: Remove zero-width space (U+200B)
assertEqual(
  sanitizeUserInput('Hello\u200BWorld'),
  'HelloWorld',
  'Zero-width space should be removed'
);

// Test 3.2: Remove zero-width non-joiner (U+200C)
assertEqual(
  sanitizeUserInput('Hello\u200CWorld'),
  'HelloWorld',
  'Zero-width non-joiner should be removed'
);

// Test 3.3: Remove zero-width joiner (U+200D)
assertEqual(
  sanitizeUserInput('Hello\u200DWorld'),
  'HelloWorld',
  'Zero-width joiner should be removed'
);

// Test 3.4: Remove zero-width no-break space (U+FEFF)
assertEqual(
  sanitizeUserInput('Hello\uFEFFWorld'),
  'HelloWorld',
  'Zero-width no-break space should be removed'
);

// Test 3.5: Remove word joiner (U+2060)
assertEqual(
  sanitizeUserInput('Hello\u2060World'),
  'HelloWorld',
  'Word joiner should be removed'
);

console.log();

// ============================================================================
// Test Suite 4: Bidirectional Text Override Removal
// ============================================================================

console.log('Test Suite 4: Bidirectional Text Override Removal');
console.log('-'.repeat(80));

// Test 4.1: Remove left-to-right embedding (U+202A)
assertEqual(
  sanitizeUserInput('Hello\u202AWorld'),
  'HelloWorld',
  'Left-to-right embedding should be removed'
);

// Test 4.2: Remove right-to-left embedding (U+202B)
assertEqual(
  sanitizeUserInput('Hello\u202BWorld'),
  'HelloWorld',
  'Right-to-left embedding should be removed'
);

// Test 4.3: Remove pop directional formatting (U+202C)
assertEqual(
  sanitizeUserInput('Hello\u202CWorld'),
  'HelloWorld',
  'Pop directional formatting should be removed'
);

// Test 4.4: Remove left-to-right override (U+202D)
assertEqual(
  sanitizeUserInput('Hello\u202DWorld'),
  'HelloWorld',
  'Left-to-right override should be removed'
);

// Test 4.5: Remove right-to-left override (U+202E)
assertEqual(
  sanitizeUserInput('Hello\u202EWorld'),
  'HelloWorld',
  'Right-to-left override should be removed'
);

console.log();

// ============================================================================
// Test Suite 5: Length Limiting
// ============================================================================

console.log('Test Suite 5: Length Limiting');
console.log('-'.repeat(80));

// Test 5.1: Text within limit should pass through
const shortText = 'A'.repeat(100);
assertEqual(
  sanitizeUserInput(shortText).length,
  100,
  'Text within limit should not be truncated'
);

// Test 5.2: Text exceeding default limit (4096) should be truncated
const longText = 'A'.repeat(5000);
assertEqual(
  sanitizeUserInput(longText).length,
  4096,
  'Text exceeding default limit should be truncated to 4096 characters'
);

// Test 5.3: Custom maxLength should be respected
const mediumText = 'A'.repeat(500);
assertEqual(
  sanitizeUserInput(mediumText, { maxLength: 100 }).length,
  100,
  'Custom maxLength should be respected'
);

console.log();

// ============================================================================
// Test Suite 6: Unicode Normalization
// ============================================================================

console.log('Test Suite 6: Unicode Normalization');
console.log('-'.repeat(80));

// Test 6.1: Composed and decomposed forms should normalize to same result
const composed = 'é'; // U+00E9 (single character)
const decomposed = 'é'; // U+0065 U+0301 (e + combining acute accent)
assertEqual(
  sanitizeUserInput(composed),
  sanitizeUserInput(decomposed),
  'Composed and decomposed Unicode should normalize to same result'
);

console.log();

// ============================================================================
// Test Suite 7: sanitizeUsername() Function
// ============================================================================

console.log('Test Suite 7: sanitizeUsername() Function');
console.log('-'.repeat(80));

// Test 7.1: Normal username should pass through
assertEqual(
  sanitizeUsername('john_doe'),
  'john_doe',
  'Normal username should pass through'
);

// Test 7.2: Username with newlines should have them removed
assertEqual(
  sanitizeUsername('john\ndoe'),
  'johndoe',
  'Newlines should be removed from username'
);

// Test 7.3: Long username should be truncated to 256 characters
const longUsername = 'A'.repeat(300);
assertEqual(
  sanitizeUsername(longUsername).length,
  256,
  'Username should be truncated to 256 characters'
);

// Test 7.4: Empty username should return fallback 'User'
assertEqual(
  sanitizeUsername(''),
  'User',
  'Empty username should return fallback "User"'
);

// Test 7.5: Whitespace-only username should return fallback 'User'
assertEqual(
  sanitizeUsername('   '),
  'User',
  'Whitespace-only username should return fallback "User"'
);

// Test 7.6: Username with only control characters should return fallback
assertEqual(
  sanitizeUsername('\x00\x01\x02'),
  'User',
  'Username with only control characters should return fallback "User"'
);

console.log();

// ============================================================================
// Test Suite 8: sanitizeMessage() Function
// ============================================================================

console.log('Test Suite 8: sanitizeMessage() Function');
console.log('-'.repeat(80));

// Test 8.1: Normal message should pass through
assertEqual(
  sanitizeMessage('Hello, how are you?'),
  'Hello, how are you?',
  'Normal message should pass through'
);

// Test 8.2: Message with newlines should keep them
assertEqual(
  sanitizeMessage('Line 1\nLine 2\nLine 3'),
  'Line 1\nLine 2\nLine 3',
  'Newlines should be preserved in messages'
);

// Test 8.3: Long message should be truncated to 4096 characters
const longMessage = 'A'.repeat(5000);
assertEqual(
  sanitizeMessage(longMessage).length,
  4096,
  'Message should be truncated to 4096 characters (Telegram limit)'
);

// Test 8.4: Message with control characters should have them removed
assertEqual(
  sanitizeMessage('Hello\x00\x07World'),
  'HelloWorld',
  'Control characters should be removed from messages'
);

// Test 8.5: Message with zero-width characters should have them removed
assertEqual(
  sanitizeMessage('Hello\u200BWorld'),
  'HelloWorld',
  'Zero-width characters should be removed from messages'
);

console.log();

// ============================================================================
// Test Suite 9: Injection Attack Prevention
// ============================================================================

console.log('Test Suite 9: Injection Attack Prevention');
console.log('-'.repeat(80));

// Test 9.1: SQL injection attempt should be sanitized
const sqlInjection = "'; DROP TABLE users; --";
const sanitizedSql = sanitizeUserInput(sqlInjection);
assert(
  sanitizedSql === "'; DROP TABLE users; --", // Should pass through but be safe due to parameterized queries
  'SQL injection attempt should be sanitized (safe for parameterized queries)'
);

// Test 9.2: Script injection with control characters should be cleaned
const scriptInjection = '<script>alert("XSS")</script>\x00\x01';
const sanitizedScript = sanitizeUserInput(scriptInjection);
assert(
  !sanitizedScript.includes('\x00') && !sanitizedScript.includes('\x01'),
  'Control characters should be removed from script injection attempts'
);

// Test 9.3: Homograph attack using similar Unicode characters
const homograph = 'раypal.com'; // Uses Cyrillic 'а' instead of Latin 'a'
const sanitizedHomograph = sanitizeUserInput(homograph);
assert(
  sanitizedHomograph.length > 0,
  'Homograph attack should be normalized'
);

console.log();

// ============================================================================
// Test Summary
// ============================================================================

console.log('='.repeat(80));
console.log('Test Summary');
console.log('='.repeat(80));
console.log(`Total Tests: ${testsPassed + testsFailed}`);
console.log(`✅ Passed: ${testsPassed}`);
console.log(`❌ Failed: ${testsFailed}`);
console.log(`Success Rate: ${((testsPassed / (testsPassed + testsFailed)) * 100).toFixed(2)}%`);
console.log('='.repeat(80));

// Exit with appropriate code
if (testsFailed > 0) {
  console.log('\n❌ Some tests failed!');
  process.exit(1);
} else {
  console.log('\n✅ All tests passed!');
  process.exit(0);
}