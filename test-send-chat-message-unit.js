/**
 * Unit Tests for sendChatMessage() method
 * Tests the chat message sending functionality with mocked API responses
 */

// Set required environment variables before importing
process.env.TELEGRAM_BOT_TOKEN = 'test-bot-token';
process.env.AUTOMATON_API_URL = 'https://automaton-production-a899.up.railway.app';
process.env.AUTOMATON_API_KEY = 'test-api-key';

import { AutomatonAPIClient } from './index.js';

// Mock fetch globally
global.fetch = async (url, options) => {
  console.log(`Mock fetch called: ${url}`);
  console.log(`Method: ${options.method}`);
  console.log(`Body: ${options.body}`);
  
  // Parse the request body
  const body = JSON.parse(options.body);
  
  // Simulate successful chat response
  return {
    ok: true,
    status: 200,
    statusText: 'OK',
    json: async () => ({
      userId: body.userId,
      message: body.message,
      response: 'This is a mock AI response to your message.',
      creditsUsed: 10,
      timestamp: new Date().toISOString(),
      conversationId: 'mock-conversation-123'
    }),
    text: async () => 'OK'
  };
};

// Test 1: Successful chat message
async function testSuccessfulChatMessage() {
  console.log('\n=== Test 1: Successful Chat Message ===');
  
  try {
    // Set environment variables
    process.env.AUTOMATON_API_URL = 'https://automaton-production-a899.up.railway.app';
    process.env.AUTOMATON_API_KEY = 'test-api-key';
    
    const client = new AutomatonAPIClient();
    const result = await client.sendChatMessage(12345, 'What is Bitcoin?');
    
    console.log('✅ Test passed: Chat message sent successfully');
    console.log('Response:', result);
    
    // Verify response structure
    if (!result.response) {
      throw new Error('Response missing "response" field');
    }
    if (!result.userId) {
      throw new Error('Response missing "userId" field');
    }
    
    console.log('✅ Response structure validated');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    throw error;
  }
}

// Test 2: Chat message with timeout
async function testChatMessageTimeout() {
  console.log('\n=== Test 2: Chat Message Timeout ===');
  
  // Override fetch to simulate timeout
  const originalFetch = global.fetch;
  global.fetch = async (url, options) => {
    // Simulate timeout by throwing AbortError
    const error = new Error('The operation was aborted');
    error.name = 'AbortError';
    throw error;
  };
  
  try {
    process.env.AUTOMATON_API_URL = 'https://automaton-production-a899.up.railway.app';
    process.env.AUTOMATON_API_KEY = 'test-api-key';
    
    const client = new AutomatonAPIClient();
    
    try {
      await client.sendChatMessage(12345, 'What is Bitcoin?');
      console.error('❌ Test failed: Should have thrown timeout error');
      throw new Error('Expected timeout error was not thrown');
    } catch (error) {
      if (error.message.includes('timed out')) {
        console.log('✅ Test passed: Timeout error handled correctly');
        console.log('Error message:', error.message);
      } else {
        throw error;
      }
    }
    
  } finally {
    // Restore original fetch
    global.fetch = originalFetch;
  }
}

// Test 3: Chat message with API error
async function testChatMessageAPIError() {
  console.log('\n=== Test 3: Chat Message API Error ===');
  
  // Override fetch to simulate API error
  const originalFetch = global.fetch;
  global.fetch = async (url, options) => {
    return {
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      text: async () => 'Server error occurred',
      json: async () => ({ error: 'Internal server error' })
    };
  };
  
  try {
    process.env.AUTOMATON_API_URL = 'https://automaton-production-a899.up.railway.app';
    process.env.AUTOMATON_API_KEY = 'test-api-key';
    
    const client = new AutomatonAPIClient();
    
    try {
      await client.sendChatMessage(12345, 'What is Bitcoin?');
      console.error('❌ Test failed: Should have thrown API error');
      throw new Error('Expected API error was not thrown');
    } catch (error) {
      if (error.message.includes('API request failed')) {
        console.log('✅ Test passed: API error handled correctly');
        console.log('Error message:', error.message);
      } else {
        throw error;
      }
    }
    
  } finally {
    // Restore original fetch
    global.fetch = originalFetch;
  }
}

// Test 4: Chat message with network error
async function testChatMessageNetworkError() {
  console.log('\n=== Test 4: Chat Message Network Error ===');
  
  // Override fetch to simulate network error
  const originalFetch = global.fetch;
  global.fetch = async (url, options) => {
    const error = new Error('Network request failed');
    error.code = 'ECONNREFUSED';
    throw error;
  };
  
  try {
    process.env.AUTOMATON_API_URL = 'https://automaton-production-a899.up.railway.app';
    process.env.AUTOMATON_API_KEY = 'test-api-key';
    
    const client = new AutomatonAPIClient();
    
    try {
      await client.sendChatMessage(12345, 'What is Bitcoin?');
      console.error('❌ Test failed: Should have thrown network error');
      throw new Error('Expected network error was not thrown');
    } catch (error) {
      if (error.message.includes('Cannot connect to Automaton API')) {
        console.log('✅ Test passed: Network error handled correctly');
        console.log('Error message:', error.message);
      } else {
        throw error;
      }
    }
    
  } finally {
    // Restore original fetch
    global.fetch = originalFetch;
  }
}

// Test 5: Chat message with empty message
async function testChatMessageEmptyMessage() {
  console.log('\n=== Test 5: Chat Message with Empty Message ===');
  
  try {
    process.env.AUTOMATON_API_URL = 'https://automaton-production-a899.up.railway.app';
    process.env.AUTOMATON_API_KEY = 'test-api-key';
    
    const client = new AutomatonAPIClient();
    const result = await client.sendChatMessage(12345, '');
    
    console.log('✅ Test passed: Empty message handled (API should validate)');
    console.log('Response:', result);
    
  } catch (error) {
    console.log('✅ Test passed: Empty message rejected');
    console.log('Error message:', error.message);
  }
}

// Run all tests
async function runAllTests() {
  console.log('Starting sendChatMessage() Unit Tests...\n');
  
  try {
    await testSuccessfulChatMessage();
    await testChatMessageTimeout();
    await testChatMessageAPIError();
    await testChatMessageNetworkError();
    await testChatMessageEmptyMessage();
    
    console.log('\n=== All Tests Completed Successfully ===');
    process.exit(0);
  } catch (error) {
    console.error('\n=== Test Suite Failed ===');
    console.error('Error:', error.message);
    process.exit(1);
  }
}

runAllTests();
