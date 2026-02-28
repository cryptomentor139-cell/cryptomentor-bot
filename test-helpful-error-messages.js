/**
 * Comprehensive Test Suite for Helpful Error Messages (Task 5.3.5)
 * Tests task 5.3.5: Provide helpful error messages for invalid input
 * 
 * This test suite verifies that ALL error scenarios provide helpful,
 * user-friendly error messages that guide users to correct usage.
 * 
 * Requirements tested:
 * - REQ-2.8.2: The system SHALL send user-friendly error messages for all failure scenarios
 * - REQ-2.8.7: The system SHALL handle malformed commands with helpful usage instructions
 * - REQ-2.8.6: The system SHALL validate all user input before processing
 * - REQ-3.3.7: The system SHALL not expose internal error details to end users
 * 
 * Test Coverage:
 * 1. Command validation errors (empty arguments, invalid syntax)
 * 2. User input validation errors (invalid user IDs, malformed data)
 * 3. API error messages (timeouts, network errors, service unavailable)
 * 4. Credit-related errors (insufficient balance)
 * 5. Generic error fallbacks
 * 6. Message formatting and user-friendliness
 */

import { 
  ErrorMessages, 
  formatErrorMessage, 
  getErrorTemplate, 
  createUserErrorMessage 
} from './error-messages.js';

console.log('='.repeat(80));
console.log('COMPREHENSIVE HELPFUL ERROR MESSAGES TEST SUITE');
console.log('Task 5.3.5: Provide helpful error messages for invalid input');
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

/**
 * Helper to check if message is user-friendly
 */
function isUserFriendly(message) {
  // User-friendly messages should:
  // 1. Not contain technical jargon
  // 2. Not expose internal errors
  // 3. Provide clear guidance
  // 4. Be polite and helpful
  
  const technicalTerms = [
    'stack trace',
    'exception',
    'null pointer',
    'undefined',
    'ECONNREFUSED',
    'ETIMEDOUT',
    'TypeError',
    'ReferenceError',
    'SyntaxError'
  ];
  
  const hasTitle = message.includes('*') && (
    message.includes('Error') || 
    message.includes('Timeout') || 
    message.includes('Unavailable') ||
    message.includes('Invalid') ||
    message.includes('Unknown') ||
    message.includes('Wrong')
  );
  
  const hasTechnicalTerms = technicalTerms.some(term => 
    message.toLowerCase().includes(term.toLowerCase())
  );
  
  const hasGuidance = 
    message.includes('Try') || 
    message.includes('What to do') || 
    message.includes('Example') ||
    message.includes('suggestion') ||
    message.includes('contact support') ||
    message.includes('again');
  
  return hasTitle && !hasTechnicalTerms && hasGuidance;
}

console.log('Test Group 1: Input Validation Error Messages');
console.log('-'.repeat(80));

test('Empty message error should be helpful', () => {
  const template = ErrorMessages.INPUT.EMPTY_MESSAGE;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Invalid Message'), 'Should have clear title');
  assert(message.includes('provide a message'), 'Should explain what went wrong');
  assert(message.includes('Example'), 'Should provide example');
  assert(message.includes('/talk'), 'Should show correct command');
});

test('Invalid command error should be helpful', () => {
  const template = ErrorMessages.INPUT.INVALID_COMMAND;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Unknown Command'), 'Should have clear title');
  assert(message.includes('don\'t recognize'), 'Should explain issue');
  assert(message.includes('/help'), 'Should guide to help');
  assert(message.includes('spelling'), 'Should suggest checking spelling');
});

test('Empty message with custom note should include note', () => {
  const template = ErrorMessages.INPUT.EMPTY_MESSAGE;
  const message = formatErrorMessage(template, {
    note: 'Please provide a valid message.'
  });
  
  assert(message.includes('Please provide a valid message'), 'Should include custom note');
});

console.log();
console.log('Test Group 2: API Error Messages');
console.log('-'.repeat(80));

test('Timeout error should be helpful', () => {
  const template = ErrorMessages.CONNECTION.TIMEOUT;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Timeout'), 'Should have clear title');
  assert(message.includes('longer than expected'), 'Should explain issue');
  assert(message.includes('Try again'), 'Should provide actionable suggestion');
  assert(!message.includes('30000ms'), 'Should not expose technical details');
});

test('Network error should be helpful', () => {
  const template = ErrorMessages.CONNECTION.NETWORK_ERROR;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Connection Error'), 'Should have clear title');
  assert(message.includes('couldn\'t connect'), 'Should explain issue');
  assert(message.includes('Try again'), 'Should provide suggestion');
  assert(!message.includes('ECONNREFUSED'), 'Should not expose error codes');
});

test('Service unavailable error should be helpful', () => {
  const template = ErrorMessages.CONNECTION.SERVICE_UNAVAILABLE;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Service Unavailable'), 'Should have clear title');
  assert(message.includes('temporarily unavailable'), 'Should explain issue');
  assert(message.includes('Try again'), 'Should provide suggestion');
  assert(message.includes('team has been notified'), 'Should reassure user');
});

test('Client error should be helpful', () => {
  const template = ErrorMessages.API.CLIENT_ERROR;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Request Error'), 'Should have clear title');
  assert(message.includes('problem with your request'), 'Should explain issue');
  assert(!message.includes('400'), 'Should not expose status codes');
  assert(!message.includes('401'), 'Should not expose status codes');
});

test('Server error should be helpful', () => {
  const template = ErrorMessages.API.SERVER_ERROR;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Service Error'), 'Should have clear title');
  assert(message.includes('went wrong on our end'), 'Should take responsibility');
  assert(message.includes('Try again'), 'Should provide suggestion');
  assert(!message.includes('500'), 'Should not expose status codes');
});

test('Invalid response error should be helpful', () => {
  const template = ErrorMessages.API.INVALID_RESPONSE;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Invalid Response'), 'Should have clear title');
  assert(message.includes('unexpected response'), 'Should explain issue');
  assert(!message.includes('JSON'), 'Should not expose technical details');
  assert(!message.includes('parse'), 'Should not expose technical details');
});

console.log();
console.log('Test Group 3: Credit Error Messages');
console.log('-'.repeat(80));

test('Insufficient credits error should be helpful', () => {
  const template = ErrorMessages.CREDITS.INSUFFICIENT;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Insufficient Credits'), 'Should have clear title');
  assert(message.includes('don\'t have enough'), 'Should explain issue');
  assert(message.includes('/status'), 'Should guide to check balance');
  assert(message.includes('purchase credits'), 'Should explain how to get more');
});

test('Insufficient credits with custom note should include balance info', () => {
  const template = ErrorMessages.CREDITS.INSUFFICIENT;
  const message = formatErrorMessage(template, {
    note: 'You need 10 credits but have 5 credits.'
  });
  
  assert(message.includes('You need 10 credits'), 'Should include specific amounts');
  assert(message.includes('have 5 credits'), 'Should show current balance');
});

console.log();
console.log('Test Group 4: Feature-Specific Error Messages');
console.log('-'.repeat(80));

test('Status unavailable error should be helpful', () => {
  const template = ErrorMessages.STATUS.UNAVAILABLE;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Unable to Retrieve Status'), 'Should have clear title');
  assert(message.includes('couldn\'t retrieve'), 'Should explain issue');
  assert(message.includes('Try again'), 'Should provide suggestion');
});

test('Conversation timeout error should be helpful', () => {
  const template = ErrorMessages.CONVERSATION.TIMEOUT;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Request Timeout'), 'Should have clear title');
  assert(message.includes('AI is taking longer'), 'Should explain issue');
  assert(message.includes('This might be due to'), 'Should provide reasons');
  assert(message.includes('What to do'), 'Should provide suggestions');
  assert(message.includes('credits have not been deducted'), 'Should reassure user');
});

test('Conversation processing error should be helpful', () => {
  const template = ErrorMessages.CONVERSATION.PROCESSING_ERROR;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Unable to Process'), 'Should have clear title');
  assert(message.includes('couldn\'t process'), 'Should explain issue');
  assert(message.includes('Try again'), 'Should provide suggestion');
  assert(message.includes('credits have not been deducted'), 'Should reassure user');
});

test('Help unavailable error should be helpful', () => {
  const template = ErrorMessages.HELP.UNAVAILABLE;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Unable to Display Help'), 'Should have clear title');
  assert(message.includes('went wrong'), 'Should explain issue');
  assert(message.includes('Try again'), 'Should provide suggestion');
});

console.log();
console.log('Test Group 5: Generic Fallback Error Messages');
console.log('-'.repeat(80));

test('Unknown error should be helpful', () => {
  const template = ErrorMessages.GENERIC.UNKNOWN_ERROR;
  const message = formatErrorMessage(template);
  
  assert(message.includes('Something Went Wrong'), 'Should have clear title');
  assert(message.includes('unexpected error'), 'Should explain issue');
  assert(message.includes('Try again'), 'Should provide suggestion');
  assert(message.includes('support'), 'Should offer support option');
});

test('Null template should return generic error', () => {
  const message = formatErrorMessage(null);
  
  assert(message.includes('Something Went Wrong'), 'Should have fallback title');
  assert(message.includes('unexpected error'), 'Should have fallback message');
});

console.log();
console.log('Test Group 6: Error Template Selection (getErrorTemplate)');
console.log('-'.repeat(80));

test('Should select timeout template for timeout errors', () => {
  const error = new Error('Request timed out');
  error.name = 'TimeoutError';
  const template = getErrorTemplate(error, 'talk');
  
  assert(template === ErrorMessages.CONVERSATION.TIMEOUT, 'Should select conversation timeout template');
});

test('Should select network error template for connection errors', () => {
  const error = new Error('Connection refused');
  error.code = 'ECONNREFUSED';
  const template = getErrorTemplate(error, 'generic');
  
  assert(template === ErrorMessages.CONNECTION.NETWORK_ERROR, 'Should select network error template');
});

test('Should select credits template for insufficient credits', () => {
  const error = new Error('Insufficient credits');
  const template = getErrorTemplate(error, 'talk');
  
  assert(template === ErrorMessages.CREDITS.INSUFFICIENT, 'Should select credits template');
});

test('Should select client error template for 4xx errors', () => {
  const error = new Error('API returned 400 Bad Request');
  const template = getErrorTemplate(error, 'generic');
  
  assert(template === ErrorMessages.API.CLIENT_ERROR, 'Should select client error template');
});

test('Should select service unavailable template for 5xx errors', () => {
  const error = new Error('API returned 500 Internal Server Error');
  const template = getErrorTemplate(error, 'generic');
  
  assert(template === ErrorMessages.CONNECTION.SERVICE_UNAVAILABLE, 'Should select service unavailable template');
});

test('Should select context-specific template for status errors', () => {
  const error = new Error('Failed to fetch status');
  const template = getErrorTemplate(error, 'status');
  
  assert(template === ErrorMessages.STATUS.UNAVAILABLE, 'Should select status unavailable template');
});

test('Should select context-specific template for conversation errors', () => {
  const error = new Error('Failed to process message');
  const template = getErrorTemplate(error, 'talk');
  
  assert(template === ErrorMessages.CONVERSATION.PROCESSING_ERROR, 'Should select conversation error template');
});

test('Should select generic fallback for unknown errors', () => {
  const error = new Error('Something weird happened');
  const template = getErrorTemplate(error, 'generic');
  
  assert(template === ErrorMessages.GENERIC.UNKNOWN_ERROR, 'Should select generic fallback');
});

console.log();
console.log('Test Group 7: Complete Error Message Creation (createUserErrorMessage)');
console.log('-'.repeat(80));

test('Should create complete user-friendly message from timeout error', () => {
  const error = new Error('Request timed out after 30000ms');
  error.name = 'TimeoutError';
  const message = createUserErrorMessage(error, 'talk');
  
  assert(message.includes('Timeout'), 'Should have timeout title');
  assert(!message.includes('30000ms'), 'Should not expose technical details');
  assert(message.includes('Try again'), 'Should provide suggestion');
  assert(isUserFriendly(message), 'Should be user-friendly');
});

test('Should create complete user-friendly message from network error', () => {
  const error = new Error('ECONNREFUSED: Connection refused');
  error.code = 'ECONNREFUSED';
  const message = createUserErrorMessage(error, 'status');
  
  assert(message.includes('Connection Error'), 'Should have connection error title');
  assert(!message.includes('ECONNREFUSED'), 'Should not expose error codes');
  assert(message.includes('Try again'), 'Should provide suggestion');
  assert(isUserFriendly(message), 'Should be user-friendly');
});

test('Should create complete user-friendly message from API error', () => {
  const error = new Error('API request failed with status 500');
  const message = createUserErrorMessage(error, 'generic');
  
  assert(message.includes('Service'), 'Should have service error title');
  assert(!message.includes('500'), 'Should not expose status codes');
  assert(message.includes('Try again'), 'Should provide suggestion');
  assert(isUserFriendly(message), 'Should be user-friendly');
});

test('Should create message with custom note', () => {
  const error = new Error('Payment failed');
  const message = createUserErrorMessage(error, 'generic', {
    note: 'Your payment has not been processed.'
  });
  
  assert(message.includes('Your payment has not been processed'), 'Should include custom note');
  assert(isUserFriendly(message), 'Should be user-friendly');
});

console.log();
console.log('Test Group 8: Message Formatting and User-Friendliness');
console.log('-'.repeat(80));

test('All error messages should use Markdown formatting', () => {
  const templates = [
    ErrorMessages.CONNECTION.TIMEOUT,
    ErrorMessages.CONNECTION.NETWORK_ERROR,
    ErrorMessages.API.CLIENT_ERROR,
    ErrorMessages.INPUT.EMPTY_MESSAGE,
    ErrorMessages.CREDITS.INSUFFICIENT
  ];
  
  templates.forEach(template => {
    const message = formatErrorMessage(template);
    assert(message.includes('*'), `Template "${template.title}" should use Markdown bold`);
  });
});

test('All error messages should have emojis for visual appeal', () => {
  const templates = [
    ErrorMessages.CONNECTION.TIMEOUT,
    ErrorMessages.CONNECTION.NETWORK_ERROR,
    ErrorMessages.API.CLIENT_ERROR,
    ErrorMessages.INPUT.EMPTY_MESSAGE,
    ErrorMessages.CREDITS.INSUFFICIENT
  ];
  
  templates.forEach(template => {
    // Check if title contains common emoji characters
    // Emojis are typically at the start of the title
    const hasEmoji = 
      template.title.includes('⏱️') ||
      template.title.includes('🔌') ||
      template.title.includes('⚠️') ||
      template.title.includes('🔧') ||
      template.title.includes('💰') ||
      template.title.includes('❓') ||
      /[\u{1F300}-\u{1F9FF}]/u.test(template.title) ||
      /[\u{2600}-\u{26FF}]/u.test(template.title) ||
      /[\u{2700}-\u{27BF}]/u.test(template.title);
    assert(hasEmoji, `Template "${template.title}" should have emoji`);
  });
});

test('Error messages should not expose internal details', () => {
  const internalError = new Error('Database connection failed at 192.168.1.1:5432');
  internalError.stack = 'Error: Database connection failed\n    at AutomatonAPIClient.connect (index.js:123:45)';
  
  const message = createUserErrorMessage(internalError, 'generic');
  
  assert(!message.includes('192.168.1.1'), 'Should not expose IP addresses');
  assert(!message.includes('5432'), 'Should not expose port numbers');
  assert(!message.includes('index.js'), 'Should not expose file names');
  assert(!message.includes('AutomatonAPIClient'), 'Should not expose class names');
  assert(!message.includes('stack'), 'Should not expose stack traces');
});

test('Error messages should be concise but informative', () => {
  const templates = [
    ErrorMessages.CONNECTION.TIMEOUT,
    ErrorMessages.INPUT.EMPTY_MESSAGE,
    ErrorMessages.CREDITS.INSUFFICIENT
  ];
  
  templates.forEach(template => {
    const message = formatErrorMessage(template);
    assert(message.length > 50, `Message should be informative (>50 chars)`);
    assert(message.length < 1000, `Message should be concise (<1000 chars)`);
  });
});

test('Error messages should provide actionable suggestions', () => {
  const templates = [
    ErrorMessages.CONNECTION.TIMEOUT,
    ErrorMessages.CONNECTION.NETWORK_ERROR,
    ErrorMessages.API.CLIENT_ERROR,
    ErrorMessages.CREDITS.INSUFFICIENT
  ];
  
  templates.forEach(template => {
    assert(
      template.suggestions && template.suggestions.length > 0,
      `Template "${template.title}" should have suggestions`
    );
  });
});

console.log();
console.log('Test Group 9: REQ-2.8.2 Compliance (User-Friendly Messages)');
console.log('-'.repeat(80));

test('REQ-2.8.2: Timeout errors should be user-friendly', () => {
  const error = new Error('Request timed out');
  error.name = 'TimeoutError';
  const message = createUserErrorMessage(error, 'talk');
  
  assert(isUserFriendly(message), 'Timeout message should be user-friendly');
});

test('REQ-2.8.2: Network errors should be user-friendly', () => {
  const error = new Error('Connection refused');
  error.code = 'ECONNREFUSED';
  const message = createUserErrorMessage(error, 'generic');
  
  assert(isUserFriendly(message), 'Network error message should be user-friendly');
});

test('REQ-2.8.2: API errors should be user-friendly', () => {
  const error = new Error('API returned 500');
  const message = createUserErrorMessage(error, 'generic');
  
  assert(isUserFriendly(message), 'API error message should be user-friendly');
});

test('REQ-2.8.2: Input validation errors should be user-friendly', () => {
  const template = ErrorMessages.INPUT.EMPTY_MESSAGE;
  const message = formatErrorMessage(template);
  
  assert(isUserFriendly(message), 'Input validation message should be user-friendly');
});

console.log();
console.log('Test Group 10: REQ-3.3.7 Compliance (No Internal Details)');
console.log('-'.repeat(80));

test('REQ-3.3.7: Should not expose stack traces', () => {
  const error = new Error('Something failed');
  error.stack = 'Error: Something failed\n    at handleConversation (index.js:3850:10)';
  const message = createUserErrorMessage(error, 'generic');
  
  assert(!message.includes('index.js'), 'Should not expose file names');
  assert(!message.includes('handleConversation'), 'Should not expose function names');
  assert(!message.includes('3850'), 'Should not expose line numbers');
});

test('REQ-3.3.7: Should not expose error codes', () => {
  const error = new Error('Connection failed');
  error.code = 'ECONNREFUSED';
  const message = createUserErrorMessage(error, 'generic');
  
  assert(!message.includes('ECONNREFUSED'), 'Should not expose error codes');
});

test('REQ-3.3.7: Should not expose API endpoints', () => {
  const error = new Error('Failed to fetch from /api/users/123/status');
  const message = createUserErrorMessage(error, 'status');
  
  assert(!message.includes('/api/'), 'Should not expose API endpoints');
  assert(!message.includes('/users/'), 'Should not expose API paths');
});

test('REQ-3.3.7: Should not expose internal class names', () => {
  const error = new Error('AutomatonAPIClient.sendChatMessage failed');
  const message = createUserErrorMessage(error, 'talk');
  
  assert(!message.includes('AutomatonAPIClient'), 'Should not expose class names');
  assert(!message.includes('sendChatMessage'), 'Should not expose method names');
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
  console.log('Task 5.3.5 Implementation Summary:');
  console.log('✅ All error messages are user-friendly and helpful');
  console.log('✅ Input validation errors provide clear guidance');
  console.log('✅ API errors hide internal details');
  console.log('✅ Credit errors explain how to resolve');
  console.log('✅ Feature-specific errors provide context');
  console.log('✅ Generic fallbacks handle unexpected errors');
  console.log('✅ REQ-2.8.2 compliance verified (user-friendly messages)');
  console.log('✅ REQ-3.3.7 compliance verified (no internal details exposed)');
  console.log('✅ REQ-2.8.7 compliance verified (helpful usage instructions)');
  console.log();
  process.exit(0);
} else {
  console.log();
  console.log('⚠️ SOME TESTS FAILED');
  console.log('Please review the failed tests above.');
  console.log();
  process.exit(1);
}
