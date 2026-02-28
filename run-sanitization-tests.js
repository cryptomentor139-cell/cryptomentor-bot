/**
 * Test Runner for Input Sanitization Tests
 * Sets up environment variables before running tests
 */

// Set dummy environment variables for testing
process.env.TELEGRAM_BOT_TOKEN = 'test-token-123';
process.env.AUTOMATON_API_URL = 'https://test-api.example.com';
process.env.AUTOMATON_API_KEY = 'test-api-key-123';
process.env.NODE_ENV = 'test';

// Import and run the tests
import('./test-input-sanitization.js')
  .then(() => {
    console.log('\n✅ Test runner completed successfully');
  })
  .catch((error) => {
    console.error('\n❌ Test runner failed:', error);
    process.exit(1);
  });
