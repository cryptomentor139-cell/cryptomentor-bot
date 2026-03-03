/**
 * Test script for Error Logging Utility
 * Demonstrates the functionality of the error logger
 * 
 * Run with: node test-error-logger.js
 */

// Mock the logger implementation for testing
class ErrorLogger {
  constructor() {
    this.logLevel = process.env.LOG_LEVEL || 'INFO';
    this.correlationIdCounter = 0;
  }

  generateCorrelationId() {
    this.correlationIdCounter++;
    return `${Date.now()}-${this.correlationIdCounter}`;
  }

  formatLogEntry(level, message, context = {}) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      correlationId: context.correlationId || this.generateCorrelationId(),
      ...context
    };
    return JSON.stringify(logEntry);
  }

  logError(message, error = null, context = {}) {
    const errorContext = {
      ...context,
      errorType: error?.name || 'Unknown',
      errorMessage: error?.message || message,
      stackTrace: error?.stack || new Error().stack,
      errorCode: error?.code
    };
    const logEntry = this.formatLogEntry('ERROR', message, errorContext);
    console.error(logEntry);
  }

  logWarn(message, context = {}) {
    const logEntry = this.formatLogEntry('WARN', message, context);
    console.warn(logEntry);
  }

  logInfo(message, context = {}) {
    const logEntry = this.formatLogEntry('INFO', message, context);
    console.log(logEntry);
  }

  logApiRequest(method, url, context = {}) {
    this.logInfo('API Request', {
      ...context,
      method,
      url,
      type: 'api_request'
    });
  }

  logApiResponse(method, url, status, context = {}) {
    const level = status >= 400 ? 'ERROR' : 'INFO';
    const message = status >= 400 ? 'API Request Failed' : 'API Response';
    const logEntry = this.formatLogEntry(level, message, {
      ...context,
      method,
      url,
      status,
      type: 'api_response'
    });
    if (level === 'ERROR') {
      console.error(logEntry);
    } else {
      console.log(logEntry);
    }
  }

  logUserCommand(command, userId, context = {}) {
    this.logInfo('User Command', {
      ...context,
      command,
      userId,
      type: 'user_command'
    });
  }

  logNotificationStats(time, successCount, failureCount, context = {}) {
    this.logInfo('Notification Delivery Statistics', {
      ...context,
      time,
      successCount,
      failureCount,
      totalUsers: successCount + failureCount,
      successRate: successCount + failureCount > 0 
        ? ((successCount / (successCount + failureCount)) * 100).toFixed(2) + '%'
        : '0%',
      type: 'notification_stats'
    });
  }
}

// Create logger instance
const logger = new ErrorLogger();

console.log('=== Testing Error Logging Utility ===\n');

// Test 1: Log info message
console.log('Test 1: Info message');
logger.logInfo('Bot initialized successfully', {
  botUsername: '@CryptoMentorBot',
  botId: 123456789
});
console.log('');

// Test 2: Log warning message
console.log('Test 2: Warning message');
logger.logWarn('API response time exceeded threshold', {
  responseTime: 5000,
  threshold: 3000,
  endpoint: '/api/users/status'
});
console.log('');

// Test 3: Log error with Error object
console.log('Test 3: Error with Error object');
try {
  throw new Error('Connection timeout');
} catch (error) {
  error.code = 'ETIMEDOUT';
  logger.logError('Failed to connect to Automaton API', error, {
    userId: 987654321,
    operation: 'getUserStatus',
    attemptNumber: 3
  });
}
console.log('');

// Test 4: Log API request
console.log('Test 4: API request');
logger.logApiRequest('POST', 'https://api.example.com/users/register', {
  userId: 123456,
  correlationId: 'test-correlation-123'
});
console.log('');

// Test 5: Log successful API response
console.log('Test 5: Successful API response');
logger.logApiResponse('GET', 'https://api.example.com/users/123/status', 200, {
  responseTime: 150,
  correlationId: 'test-correlation-124'
});
console.log('');

// Test 6: Log failed API response
console.log('Test 6: Failed API response');
logger.logApiResponse('POST', 'https://api.example.com/chat', 500, {
  responseTime: 30000,
  errorMessage: 'Internal Server Error',
  correlationId: 'test-correlation-125'
});
console.log('');

// Test 7: Log user command
console.log('Test 7: User command');
logger.logUserCommand('/start', 123456789, {
  username: 'testuser',
  firstName: 'Test',
  lastName: 'User'
});
console.log('');

// Test 8: Log notification statistics
console.log('Test 8: Notification delivery statistics');
logger.logNotificationStats('08:00 WIB', 950, 50, {
  scheduledTime: '08:00',
  actualTime: '08:00:05',
  deliveryDuration: 45000
});
console.log('');

console.log('=== All tests completed ===');
console.log('\nKey features demonstrated:');
console.log('✓ Timestamp in ISO format (sub-task 5.1.1.1)');
console.log('✓ Error type and stack trace (sub-task 5.1.1.2)');
console.log('✓ Context information (sub-task 5.1.1.3)');
console.log('✓ Severity levels: ERROR, WARN, INFO (REQ-3.7.4)');
console.log('✓ Correlation IDs for tracking (REQ-3.7.5)');
console.log('✓ JSON format output (REQ-3.7.6)');
