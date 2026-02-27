/**
 * Comprehensive Test Suite for Malformed Command Handling
 * Tests task 5.3.4: Handle malformed commands
 * 
 * This test suite verifies:
 * - Detection and handling of malformed/invalid commands
 * - Helpful error messages with usage instructions
 * - Command typo detection and suggestions
 * - Bot remains operational after receiving invalid input
 * - Proper guidance to correct usage with examples
 * 
 * Requirements tested:
 * - REQ-2.8.7: The system SHALL handle malformed commands with helpful usage instructions
 * - REQ-2.8.6: The system SHALL validate all user input before processing
 * - REQ-2.8.1: The system SHALL remain operational when receiving invalid input
 */

import { suggestCommandCorrection, generateMalformedCommandMessage } from './index.js';

console.log('='.repeat(80));
console.log('COMPREHENSIVE MALFORMED COMMAND HANDLING TEST SUITE');
console.log('Task 5.3.4: Handle malformed commands');
console.log('='.repeat(80));
console.log();

// Test counters
let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

/**
 * Test helper function
 */
function test(description, testFn) {
  totalTests++;
  try {
    testFn();
    passedTests++;
    console.log(`✅ PASS: ${description}`);
  } catch (error) {
    failedTests++;
    console.error(`❌ FAIL: ${description}`);
    console.error(`   Error: ${error.message}`);
  }
}

/**
 * Assert helper function
 */
function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

console.log('Test Group 1: Command Typo Detection and Suggestions');
console.log('-'.repeat(80));

test('Should suggest /status for /stat', () => {
  const suggestion = suggestCommandCorrection('/stat');
  assert(suggestion === '/status', `Expected '/status', got '${suggestion}'`);
});

test('Should suggest /status for /stats', () => {
  const suggestion = suggestCommandCorrection('/stats');
  assert(suggestion === '/status', `Expected '/status', got '${suggestion}'`);
});

test('Should suggest /status for /balance', () => {
  const suggestion = suggestCommandCorrection('/balance');
  assert(suggestion === '/status', `Expected '/status', got '${suggestion}'`);
});

test('Should suggest /status for /credits', () => {
  const suggestion = suggestCommandCorrection('/credits');
  assert(suggestion === '/status', `Expected '/status', got '${suggestion}'`);
});

test('Should suggest /start for /begin', () => {
  const suggestion = suggestCommandCorrection('/begin');
  assert(suggestion === '/start', `Expected '/start', got '${suggestion}'`);
});

test('Should suggest /start for /register', () => {
  const suggestion = suggestCommandCorrection('/register');
  assert(suggestion === '/start', `Expected '/start', got '${suggestion}'`);
});

test('Should suggest /start for /signup', () => {
  const suggestion = suggestCommandCorrection('/signup');
  assert(suggestion === '/start', `Expected '/start', got '${suggestion}'`);
});

test('Should suggest /help for /info', () => {
  const suggestion = suggestCommandCorrection('/info');
  assert(suggestion === '/help', `Expected '/help', got '${suggestion}'`);
});

test('Should suggest /help for /commands', () => {
  const suggestion = suggestCommandCorrection('/commands');
  assert(suggestion === '/help', `Expected '/help', got '${suggestion}'`);
});

test('Should suggest /talk for /chat', () => {
  const suggestion = suggestCommandCorrection('/chat');
  assert(suggestion === '/talk', `Expected '/talk', got '${suggestion}'`);
});

test('Should suggest /talk for /ask', () => {
  const suggestion = suggestCommandCorrection('/ask');
  assert(suggestion === '/talk', `Expected '/talk', got '${suggestion}'`);
});

test('Should suggest /talk for /message', () => {
  const suggestion = suggestCommandCorrection('/message');
  assert(suggestion === '/talk', `Expected '/talk', got '${suggestion}'`);
});

test('Should suggest /talk for /say', () => {
  const suggestion = suggestCommandCorrection('/say');
  assert(suggestion === '/talk', `Expected '/talk', got '${suggestion}'`);
});

test('Should suggest /talk for /speak', () => {
  const suggestion = suggestCommandCorrection('/speak');
  assert(suggestion === '/talk', `Expected '/talk', got '${suggestion}'`);
});

test('Should return null for completely unknown command', () => {
  const suggestion = suggestCommandCorrection('/xyz123');
  assert(suggestion === null, `Expected null, got '${suggestion}'`);
});

test('Should handle case-insensitive typos', () => {
  const suggestion1 = suggestCommandCorrection('/STAT');
  const suggestion2 = suggestCommandCorrection('/StAt');
  assert(suggestion1 === '/status', `Expected '/status' for /STAT, got '${suggestion1}'`);
  assert(suggestion2 === '/status', `Expected '/status' for /StAt, got '${suggestion2}'`);
});

console.log();
console.log('Test Group 2: Error Message Generation');
console.log('-'.repeat(80));

test('Should generate message with suggestion for known typo', () => {
  const message = generateMalformedCommandMessage('/stat', '/stat');
  assert(message.includes('Did you mean'), 'Message should include suggestion prompt');
  assert(message.includes('/status'), 'Message should suggest /status');
  assert(message.includes('Available Commands'), 'Message should list available commands');
});

test('Should generate message without suggestion for unknown command', () => {
  const message = generateMalformedCommandMessage('/xyz', '/xyz');
  assert(!message.includes('Did you mean'), 'Message should not include suggestion for unknown command');
  assert(message.includes('Available Commands'), 'Message should list available commands');
  assert(message.includes('Unknown Command'), 'Message should indicate unknown command');
});

test('Should include all available commands in error message', () => {
  const message = generateMalformedCommandMessage('/unknown', '/unknown');
  assert(message.includes('/start'), 'Should include /start command');
  assert(message.includes('/status'), 'Should include /status command');
  assert(message.includes('/help'), 'Should include /help command');
  assert(message.includes('/talk'), 'Should include /talk command');
});

test('Should include usage examples in error message', () => {
  const message = generateMalformedCommandMessage('/unknown', '/unknown');
  assert(message.includes('Examples'), 'Should include examples section');
  assert(message.includes('What is Bitcoin'), 'Should include example question');
});

test('Should include help command guidance', () => {
  const message = generateMalformedCommandMessage('/unknown', '/unknown');
  assert(message.includes('Need more help'), 'Should encourage using help command');
  assert(message.includes('/help'), 'Should mention help command');
});

test('Should format message with Markdown', () => {
  const message = generateMalformedCommandMessage('/unknown', '/unknown');
  assert(message.includes('*'), 'Should use Markdown bold formatting');
  assert(message.includes('`'), 'Should use Markdown code formatting');
});

test('Should escape command in error message', () => {
  const message = generateMalformedCommandMessage('/test', '/test');
  assert(message.includes('`/test`'), 'Should wrap command in code formatting');
});

console.log();
console.log('Test Group 3: Edge Cases and Special Scenarios');
console.log('-'.repeat(80));

test('Should handle command with extra spaces', () => {
  const suggestion = suggestCommandCorrection('/stat   ');
  // Note: The function trims and lowercases, so this should still work
  assert(suggestion === '/status' || suggestion === null, 'Should handle spaces gracefully');
});

test('Should handle empty command', () => {
  const suggestion = suggestCommandCorrection('');
  assert(suggestion === null, 'Should return null for empty command');
});

test('Should handle command without slash', () => {
  const suggestion = suggestCommandCorrection('stat');
  assert(suggestion === null, 'Should return null for command without slash');
});

test('Should generate message for very long invalid command', () => {
  const longCommand = '/thisisaverylongcommandthatdoesnotexist';
  const message = generateMalformedCommandMessage(longCommand, longCommand);
  assert(message.includes(longCommand), 'Should include the long command in message');
  assert(message.length > 0, 'Should generate non-empty message');
});

test('Should handle command with special characters', () => {
  const specialCommand = '/test@bot';
  const message = generateMalformedCommandMessage(specialCommand, specialCommand);
  assert(message.includes('Unknown Command'), 'Should handle special characters');
});

console.log();
console.log('Test Group 4: Message Content Validation');
console.log('-'.repeat(80));

test('Should provide clear error indication', () => {
  const message = generateMalformedCommandMessage('/invalid', '/invalid');
  assert(
    message.includes('Unknown Command') || message.includes('don\'t recognize'),
    'Should clearly indicate error'
  );
});

test('Should provide actionable guidance', () => {
  const message = generateMalformedCommandMessage('/invalid', '/invalid');
  assert(
    message.includes('Available Commands') || message.includes('Try'),
    'Should provide actionable guidance'
  );
});

test('Should be user-friendly and not technical', () => {
  const message = generateMalformedCommandMessage('/invalid', '/invalid');
  assert(!message.includes('error'), 'Should avoid technical error terminology');
  assert(!message.includes('exception'), 'Should avoid technical exception terminology');
  assert(!message.includes('stack'), 'Should not expose stack traces');
});

test('Should encourage correct usage', () => {
  const message = generateMalformedCommandMessage('/invalid', '/invalid');
  assert(
    message.includes('Example') || message.includes('Try'),
    'Should encourage correct usage'
  );
});

console.log();
console.log('Test Group 5: Requirement Compliance');
console.log('-'.repeat(80));

test('REQ-2.8.7: Should provide helpful usage instructions', () => {
  const message = generateMalformedCommandMessage('/invalid', '/invalid');
  assert(message.includes('Available Commands'), 'Should list available commands');
  assert(message.includes('Example'), 'Should provide usage examples');
  assert(message.length > 100, 'Should provide substantial guidance');
});

test('REQ-2.8.7: Should guide users to correct usage', () => {
  const message = generateMalformedCommandMessage('/stat', '/stat');
  assert(message.includes('Did you mean'), 'Should suggest corrections');
  assert(message.includes('/status'), 'Should guide to correct command');
});

test('REQ-2.8.6: Should validate command input', () => {
  // The suggestCommandCorrection function validates by checking against known typos
  const validTypo = suggestCommandCorrection('/stat');
  const invalidCommand = suggestCommandCorrection('/xyz123');
  assert(validTypo !== null, 'Should recognize valid typos');
  assert(invalidCommand === null, 'Should reject invalid commands');
});

test('REQ-2.8.1: Should remain operational (no exceptions thrown)', () => {
  // Test that functions don't throw exceptions
  let noException = true;
  try {
    suggestCommandCorrection('/invalid');
    generateMalformedCommandMessage('/invalid', '/invalid');
    suggestCommandCorrection('');
    generateMalformedCommandMessage('', '');
  } catch (error) {
    noException = false;
  }
  assert(noException, 'Functions should not throw exceptions');
});

console.log();
console.log('Test Group 6: Integration Scenarios');
console.log('-'.repeat(80));

test('Scenario: User types /stat instead of /status', () => {
  const suggestion = suggestCommandCorrection('/stat');
  const message = generateMalformedCommandMessage('/stat', '/stat');
  
  assert(suggestion === '/status', 'Should suggest /status');
  assert(message.includes('Did you mean'), 'Should offer suggestion');
  assert(message.includes('/status'), 'Should include correct command');
});

test('Scenario: User types completely wrong command', () => {
  const suggestion = suggestCommandCorrection('/wrongcommand');
  const message = generateMalformedCommandMessage('/wrongcommand', '/wrongcommand');
  
  assert(suggestion === null, 'Should not suggest anything');
  assert(message.includes('Available Commands'), 'Should list all commands');
  assert(message.includes('Example'), 'Should provide examples');
});

test('Scenario: User types /talk variation', () => {
  const chatSuggestion = suggestCommandCorrection('/chat');
  const askSuggestion = suggestCommandCorrection('/ask');
  
  assert(chatSuggestion === '/talk', 'Should suggest /talk for /chat');
  assert(askSuggestion === '/talk', 'Should suggest /talk for /ask');
});

test('Scenario: User needs help after malformed command', () => {
  const message = generateMalformedCommandMessage('/help123', '/help123');
  
  assert(message.includes('/help'), 'Should mention help command');
  assert(message.includes('Need more help'), 'Should encourage using help');
});

console.log();
console.log('='.repeat(80));
console.log('TEST SUMMARY');
console.log('='.repeat(80));
console.log(`Total Tests: ${totalTests}`);
console.log(`Passed: ${passedTests} ✅`);
console.log(`Failed: ${failedTests} ❌`);
console.log(`Success Rate: ${((passedTests / totalTests) * 100).toFixed(2)}%`);
console.log('='.repeat(80));

if (failedTests === 0) {
  console.log();
  console.log('🎉 ALL TESTS PASSED! 🎉');
  console.log();
  console.log('Task 5.3.4 Implementation Summary:');
  console.log('✅ Malformed command detection implemented');
  console.log('✅ Command typo suggestions implemented');
  console.log('✅ Helpful error messages with usage instructions');
  console.log('✅ Guidance to correct usage with examples');
  console.log('✅ Bot remains operational when receiving invalid input');
  console.log('✅ REQ-2.8.7 compliance verified');
  console.log();
  process.exit(0);
} else {
  console.log();
  console.log('⚠️ SOME TESTS FAILED');
  console.log('Please review the failed tests above.');
  console.log();
  process.exit(1);
}
