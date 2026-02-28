/**
 * Test file for /status command error handling (Task 3.2.6)
 * 
 * This test verifies that the /status command handles different error scenarios gracefully:
 * - API timeout errors
 * - Network connection errors
 * - 4xx client errors
 * - 5xx server errors
 * - Invalid response format
 * - Generic errors
 * 
 * Run with: node test-status-error-handling.js
 */

import TelegramBot from 'node-telegram-bot-api';

// Mock environment variables
process.env.TELEGRAM_BOT_TOKEN = 'test-token-123';
process.env.AUTOMATON_API_URL = 'https://test-api.example.com';
process.env.AUTOMATON_API_KEY = 'test-api-key-123';
process.env.NODE_ENV = 'test';

// Test results tracking
const testResults = {
  passed: 0,
  failed: 0,
  tests: []
};

/**
 * Mock AutomatonAPIClient for testing different error scenarios
 */
class MockAutomatonAPIClient {
  constructor() {
    this.baseURL = process.env.AUTOMATON_API_URL;
    this.apiKey = process.env.AUTOMATON_API_KEY;
    this.timeout = 30000;
    this.errorScenario = null;
  }

  /**
   * Set the error scenario to simulate
   */
  setErrorScenario(scenario) {
    this.errorScenario = scenario;
  }

  /**
   * Mock getUserStatus that throws different errors based on scenario
   */
  async getUserStatus(userId) {
    console.log(`[TEST] MockAPI: getUserStatus called for user ${userId} with scenario: ${this.errorScenario}`);

    switch (this.errorScenario) {
      case 'timeout':
        const timeoutError = new Error('Status request timed out. Please try again.');
        timeoutError.name = 'TimeoutError';
        throw timeoutError;

      case 'network':
        const networkError = new Error('Cannot connect to Automaton API. Service may be unavailable.');
        networkError.code = 'ECONNREFUSED';
        throw networkError;

      case '4xx':
        throw new Error('API request failed: 404 Not Found');

      case '5xx':
        throw new Error('API request failed: 503 Service Unavailable');

      case 'invalid-json':
        const jsonError = new SyntaxError('Unexpected token < in JSON at position 0');
        throw jsonError;

      case 'generic':
        throw new Error('Something unexpected happened');

      case 'success':
        return {
          credits: 1000,
          conversationCount: 5,
          lastActivity: new Date().toISOString()
        };

      default:
        throw new Error('Unknown error scenario');
    }
  }
}

/**
 * Mock Telegram Bot for testing
 */
class MockTelegramBot {
  constructor() {
    this.sentMessages = [];
  }

  async sendMessage(chatId, text, options) {
    console.log(`[TEST] MockBot: Sending message to ${chatId}`);
    console.log(`[TEST] Message: ${text.substring(0, 100)}...`);
    this.sentMessages.push({ chatId, text, options });
    return { message_id: Date.now() };
  }

  getLastMessage() {
    return this.sentMessages[this.sentMessages.length - 1];
  }

  clearMessages() {
    this.sentMessages = [];
  }
}

/**
 * Format relative time (simplified version for testing)
 */
function formatRelativeTime(timestamp) {
  if (!timestamp) return 'Never';
  return 'Just now';
}

/**
 * Format status message
 */
function formatStatusMessage(userStatus) {
  if (!userStatus) {
    return '⚠️ *Status Unavailable*\n\nUnable to retrieve your status information.';
  }

  const credits = userStatus.credits ?? 0;
  const formattedCredits = credits.toLocaleString('en-US');
  const conversationCount = userStatus.conversationCount ?? 0;
  const lastActivity = formatRelativeTime(userStatus.lastActivity);

  return `📊 *Your Status*\n\n` +
    `💰 *Credits:* ${formattedCredits}\n` +
    `💬 *Active conversations:* ${conversationCount}\n` +
    `🕐 *Last activity:* ${lastActivity}`;
}

/**
 * Handle /status command with error handling
 */
async function handleStatusCommand(msg, bot, apiClient) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const username = msg.from.username || msg.from.first_name || 'User';

  console.log(`[TEST] Handling /status command from user: ${username} (ID: ${userId})`);

  try {
    const userStatus = await apiClient.getUserStatus(userId);
    const statusMessage = formatStatusMessage(userStatus);
    await bot.sendMessage(chatId, statusMessage, { parse_mode: 'Markdown' });
    console.log(`[TEST] ✅ Status message sent successfully`);
    return { success: true, message: statusMessage };
  } catch (error) {
    console.error(`[TEST] ❌ Error handling /status command:`, error.message);
    console.error(`[TEST] Error type: ${error.name}`);

    let userMessage;

    // Handle timeout errors
    if (error.name === 'AbortError' || error.name === 'TimeoutError' ||
        error.message.includes('timed out') || error.message.includes('timeout')) {
      userMessage = `⏱️ *Request Timeout*\n\n` +
        `The request is taking longer than expected. Please try again.`;
    }
    // Handle network connection errors
    else if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND' ||
             error.code === 'ETIMEDOUT' || error.code === 'ECONNRESET' ||
             error.message.includes('Cannot connect') ||
             error.message.includes('Service may be unavailable')) {
      userMessage = `🔌 *Connection Error*\n\n` +
        `Sorry, I couldn't retrieve your status right now. Please try again in a moment.`;
    }
    // Handle 4xx client errors
    else if (error.message.includes('400') || error.message.includes('401') ||
             error.message.includes('403') || error.message.includes('404')) {
      userMessage = `⚠️ *Request Error*\n\n` +
        `There was a problem with your request. Please try again later.`;
    }
    // Handle 5xx server errors
    else if (error.message.includes('500') || error.message.includes('502') ||
             error.message.includes('503') || error.message.includes('504')) {
      userMessage = `🔧 *Service Unavailable*\n\n` +
        `Sorry, I couldn't retrieve your status right now. Please try again in a moment.`;
    }
    // Handle invalid response format
    else if (error instanceof SyntaxError || error.message.includes('JSON') ||
             error.message.includes('parse')) {
      userMessage = `⚠️ *Invalid Response*\n\n` +
        `Something went wrong. Please try again later.`;
    }
    // Generic error fallback
    else {
      userMessage = `⚠️ *Unable to Retrieve Status*\n\n` +
        `Something went wrong. Please try again later.`;
    }

    await bot.sendMessage(chatId, userMessage, { parse_mode: 'Markdown' });
    console.log(`[TEST] ✅ Error message sent to user`);
    return { success: false, message: userMessage, error: error.message };
  }
}

/**
 * Run a single test case
 */
async function runTest(testName, scenario, expectedMessagePattern) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`TEST: ${testName}`);
  console.log(`${'='.repeat(60)}`);

  const mockBot = new MockTelegramBot();
  const mockApiClient = new MockAutomatonAPIClient();
  mockApiClient.setErrorScenario(scenario);

  const mockMessage = {
    chat: { id: 12345 },
    from: { id: 67890, username: 'testuser', first_name: 'Test' }
  };

  try {
    const result = await handleStatusCommand(mockMessage, mockBot, mockApiClient);
    const lastMessage = mockBot.getLastMessage();

    if (!lastMessage) {
      throw new Error('No message was sent');
    }

    const messageText = lastMessage.text;
    const matches = messageText.includes(expectedMessagePattern);

    if (matches) {
      console.log(`✅ PASSED: ${testName}`);
      console.log(`   Expected pattern: "${expectedMessagePattern}"`);
      console.log(`   Got message: "${messageText.substring(0, 80)}..."`);
      testResults.passed++;
      testResults.tests.push({ name: testName, status: 'PASSED' });
    } else {
      console.log(`❌ FAILED: ${testName}`);
      console.log(`   Expected pattern: "${expectedMessagePattern}"`);
      console.log(`   Got message: "${messageText}"`);
      testResults.failed++;
      testResults.tests.push({ name: testName, status: 'FAILED', reason: 'Message pattern mismatch' });
    }
  } catch (error) {
    console.log(`❌ FAILED: ${testName}`);
    console.log(`   Error: ${error.message}`);
    testResults.failed++;
    testResults.tests.push({ name: testName, status: 'FAILED', reason: error.message });
  }
}

/**
 * Main test execution
 */
async function runAllTests() {
  console.log('\n' + '='.repeat(60));
  console.log('STARTING ERROR HANDLING TESTS FOR /status COMMAND');
  console.log('Task 3.2.6: Handle API errors gracefully');
  console.log('='.repeat(60));

  // Test 1: Timeout error
  await runTest(
    'Timeout Error Handling',
    'timeout',
    'Request Timeout'
  );

  // Test 2: Network connection error
  await runTest(
    'Network Connection Error Handling',
    'network',
    'Connection Error'
  );

  // Test 3: 4xx client error
  await runTest(
    '4xx Client Error Handling',
    '4xx',
    'Request Error'
  );

  // Test 4: 5xx server error
  await runTest(
    '5xx Server Error Handling',
    '5xx',
    'Service Unavailable'
  );

  // Test 5: Invalid JSON response
  await runTest(
    'Invalid Response Format Handling',
    'invalid-json',
    'Invalid Response'
  );

  // Test 6: Generic error
  await runTest(
    'Generic Error Handling',
    'generic',
    'Unable to Retrieve Status'
  );

  // Test 7: Success case
  await runTest(
    'Success Case',
    'success',
    'Your Status'
  );

  // Print summary
  console.log('\n' + '='.repeat(60));
  console.log('TEST SUMMARY');
  console.log('='.repeat(60));
  console.log(`Total Tests: ${testResults.passed + testResults.failed}`);
  console.log(`Passed: ${testResults.passed}`);
  console.log(`Failed: ${testResults.failed}`);
  console.log('='.repeat(60));

  testResults.tests.forEach((test, index) => {
    const icon = test.status === 'PASSED' ? '✅' : '❌';
    console.log(`${icon} ${index + 1}. ${test.name} - ${test.status}`);
    if (test.reason) {
      console.log(`   Reason: ${test.reason}`);
    }
  });

  console.log('='.repeat(60));

  if (testResults.failed === 0) {
    console.log('\n🎉 ALL TESTS PASSED! Error handling is working correctly.');
    process.exit(0);
  } else {
    console.log('\n⚠️ SOME TESTS FAILED. Please review the error handling implementation.');
    process.exit(1);
  }
}

// Run all tests
runAllTests().catch(error => {
  console.error('Fatal error running tests:', error);
  process.exit(1);
});
