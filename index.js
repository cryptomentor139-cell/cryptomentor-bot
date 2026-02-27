import TelegramBot from 'node-telegram-bot-api';
import cron from 'node-cron';
import fetch from 'node-fetch';
import { ErrorMessages, formatErrorMessage, getErrorTemplate, createUserErrorMessage } from './error-messages.js';

// ============================================================================
// Error Logging Utility
// ============================================================================

/**
 * Error Logging Utility
 * Implements task 5.1.1: Create error logging utility
 *
 * This utility provides structured error logging with:
 * - Timestamp (REQ-2.8.3, sub-task 5.1.1.1)
 * - Error type and stack trace (REQ-2.8.3, sub-task 5.1.1.2)
 * - Context information (sub-task 5.1.1.3)
 * - Severity levels (REQ-3.7.4)
 * - Correlation IDs (REQ-3.7.5)
 * - JSON format output (REQ-3.7.6)
 */

// Generate unique correlation ID for tracking request flows
let correlationIdCounter = 0;
function generateCorrelationId() {
  correlationIdCounter++;
  return `${Date.now()}-${correlationIdCounter}`;
}

/**
 * Log levels enum
 */
const LogLevel = {
  ERROR: 'ERROR',
  WARN: 'WARN',
  INFO: 'INFO',
  DEBUG: 'DEBUG'
};

/**
 * Error Logger Class
 * Provides structured logging with JSON output format
 */
class ErrorLogger {
  constructor() {
    this.logLevel = process.env.LOG_LEVEL || 'INFO';
  }

  /**
   * Format log entry as JSON
   * Implements REQ-3.7.6: Output logs in JSON format for structured logging
   *
   * @param {string} level - Log level (ERROR, WARN, INFO, DEBUG)
   * @param {string} message - Log message
   * @param {Object} context - Additional context information
   * @returns {string} JSON formatted log entry
   */
  formatLogEntry(level, message, context = {}) {
    // Sub-task 5.1.1.1: Log errors with timestamp
    const timestamp = new Date().toISOString();

    // Sub-task 5.1.1.3: Include context information
    // REQ-3.7.5: Include correlation IDs for tracking request flows
    const logEntry = {
      timestamp,
      level,
      message,
      correlationId: context.correlationId || generateCorrelationId(),
      ...context
    };

    // REQ-3.7.6: Output logs in JSON format
    return JSON.stringify(logEntry);
  }

  /**
   * Log error with full details
   * Implements sub-task 5.1.1.2: Log error type and stack trace
   *
   * @param {string} message - Error message
   * @param {Error} error - Error object
   * @param {Object} context - Additional context (userId, operation, etc.)
   */
  logError(message, error = null, context = {}) {
    // Sub-task 5.1.1.2: Log error type and stack trace
    const errorContext = {
      ...context,
      errorType: error?.name || 'Unknown',
      errorMessage: error?.message || message,
      stackTrace: error?.stack || new Error().stack,
      errorCode: error?.code
    };

    const logEntry = this.formatLogEntry(LogLevel.ERROR, message, errorContext);
    console.error(logEntry);
  }

  /**
   * Log warning message
   *
   * @param {string} message - Warning message
   * @param {Object} context - Additional context
   */
  logWarn(message, context = {}) {
    const logEntry = this.formatLogEntry(LogLevel.WARN, message, context);
    console.warn(logEntry);
  }

  /**
   * Log info message
   *
   * @param {string} message - Info message
   * @param {Object} context - Additional context
   */
  logInfo(message, context = {}) {
    const logEntry = this.formatLogEntry(LogLevel.INFO, message, context);
    console.log(logEntry);
  }

  /**
   * Log debug message
   *
   * @param {string} message - Debug message
   * @param {Object} context - Additional context
   */
  logDebug(message, context = {}) {
    if (this.logLevel === 'DEBUG') {
      const logEntry = this.formatLogEntry(LogLevel.DEBUG, message, context);
      console.log(logEntry);
    }
  }

  /**
   * Log API request
   * Implements REQ-2.7.7: Log all API requests and responses
   *
   * @param {string} method - HTTP method
   * @param {string} url - Request URL
   * @param {Object} context - Additional context
   */
  logApiRequest(method, url, context = {}) {
    this.logInfo('API Request', {
      ...context,
      method,
      url,
      type: 'api_request'
    });
  }

  /**
   * Log API response
   * Implements REQ-2.7.7: Log all API requests and responses
   *
   * @param {string} method - HTTP method
   * @param {string} url - Request URL
   * @param {number} status - Response status code
   * @param {Object} context - Additional context
   */
  logApiResponse(method, url, status, context = {}) {
    const level = status >= 400 ? LogLevel.ERROR : LogLevel.INFO;
    const message = status >= 400 ? 'API Request Failed' : 'API Response';

    const logEntry = this.formatLogEntry(level, message, {
      ...context,
      method,
      url,
      status,
      type: 'api_response'
    });

    if (level === LogLevel.ERROR) {
      console.error(logEntry);
    } else {
      console.log(logEntry);
    }
  }

  /**
   * Log user command
   * Implements REQ-3.7.1: Log all incoming user commands
   *
   * @param {string} command - Command name
   * @param {number} userId - Telegram user ID
   * @param {Object} context - Additional context
   */
  logUserCommand(command, userId, context = {}) {
    this.logInfo('User Command', {
      ...context,
      command,
      userId,
      type: 'user_command'
    });
  }

  /**
   * Log notification delivery statistics
   * Implements REQ-3.7.3: Log notification delivery statistics
   *
   * @param {string} time - Scheduled time
   * @param {number} successCount - Number of successful deliveries
   * @param {number} failureCount - Number of failed deliveries
   * @param {Object} context - Additional context
   */
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

// Create global logger instance
const logger = new ErrorLogger();


// ============================================================================
// Configuration and Environment Variables
// ============================================================================

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const AUTOMATON_API_URL = process.env.AUTOMATON_API_URL;
const AUTOMATON_API_KEY = process.env.AUTOMATON_API_KEY;
const NODE_ENV = process.env.NODE_ENV || 'production';

// Conversation cost in credits
const CONVERSATION_COST = 10;

// Validate required environment variables
if (!TELEGRAM_BOT_TOKEN) {
  console.error('ERROR: TELEGRAM_BOT_TOKEN environment variable is required');
  process.exit(1);
}

if (!AUTOMATON_API_URL) {
  console.error('ERROR: AUTOMATON_API_URL environment variable is required');
  process.exit(1);
}

if (!AUTOMATON_API_KEY) {
  console.error('ERROR: AUTOMATON_API_KEY environment variable is required');
  process.exit(1);
}

// ============================================================================
// Error Handling and Reconnection Logic
// ============================================================================

// Reconnection state
let reconnectionAttempts = 0;
const MAX_RECONNECTION_ATTEMPTS = 5;
const BASE_DELAY = 1000; // 1 second
const MAX_DELAY = 60000; // 60 seconds

// Disconnection detection state
// Task 5.2.1: Detect Telegram API disconnection
let lastPollingCheck = Date.now();
let pollingHealthCheckInterval = null;
const POLLING_HEALTH_CHECK_INTERVAL = 60000; // Check every 60 seconds
const POLLING_TIMEOUT_THRESHOLD = 120000; // Consider disconnected if no activity for 2 minutes

/**
 * Calculate exponential backoff delay
 * @param {number} attempt - Current attempt number (0-indexed)
 * @returns {number} Delay in milliseconds
 */
function calculateBackoffDelay(attempt) {
  // Exponential backoff: 1s, 2s, 4s, 8s, 16s, capped at 60s
  const delay = Math.min(BASE_DELAY * Math.pow(2, attempt), MAX_DELAY);
  return delay;
}

/**
 * Detect Telegram API disconnection by monitoring polling state
 * Implements task 5.2.1: Detect Telegram API disconnection
 * 
 * This function proactively monitors the bot's polling state and detects
 * disconnections that might not trigger polling_error events.
 * 
 * @param {TelegramBot} bot - Bot instance to monitor
 */
function detectDisconnection(bot) {
  const now = Date.now();
  const timeSinceLastCheck = now - lastPollingCheck;
  
  // Check if bot is still polling
  const isPolling = bot.isPolling();
  
  // Update last check time
  lastPollingCheck = now;
  
  // Log polling state for monitoring
  logger.logDebug('Polling health check', {
    isPolling,
    timeSinceLastCheck,
    reconnectionAttempts
  });
  
  // Detect disconnection scenarios:
  // 1. Bot reports it's not polling
  // 2. No polling activity detected for extended period (handled by Telegram library)
  
  if (!isPolling) {
    console.warn(`[${new Date().toISOString()}] ⚠️ Disconnection detected: Bot is not polling`);
    logger.logWarn('Telegram API disconnection detected', {
      reason: 'Bot polling stopped',
      timeSinceLastCheck,
      reconnectionAttempts
    });
    
    // Attempt to reconnect
    console.log(`[${new Date().toISOString()}] 🔄 Initiating reconnection due to detected disconnection...`);
    handleReconnection(bot);
  } else {
    // Bot is polling normally
    if (reconnectionAttempts > 0) {
      // We were reconnecting but now we're back online
      console.log(`[${new Date().toISOString()}] ✅ Polling health check: Bot is connected and polling normally`);
    }
  }
}

/**
 * Start monitoring polling health to detect disconnections
 * Implements task 5.2.1: Detect Telegram API disconnection
 * 
 * @param {TelegramBot} bot - Bot instance to monitor
 */
function startPollingHealthMonitor(bot) {
  console.log(`[${new Date().toISOString()}] 🔍 Starting polling health monitor...`);
  console.log(`[${new Date().toISOString()}] Health check interval: ${POLLING_HEALTH_CHECK_INTERVAL}ms`);
  
  // Clear any existing interval
  if (pollingHealthCheckInterval) {
    clearInterval(pollingHealthCheckInterval);
  }
  
  // Start periodic health checks
  pollingHealthCheckInterval = setInterval(() => {
    detectDisconnection(bot);
  }, POLLING_HEALTH_CHECK_INTERVAL);
  
  console.log(`[${new Date().toISOString()}] ✅ Polling health monitor started`);
}

/**
 * Stop monitoring polling health
 */
function stopPollingHealthMonitor() {
  if (pollingHealthCheckInterval) {
    clearInterval(pollingHealthCheckInterval);
    pollingHealthCheckInterval = null;
    console.log(`[${new Date().toISOString()}] 🛑 Polling health monitor stopped`);
  }
}

/**
 * Handle reconnection with exponential backoff
 * Implements task 5.2.2: Implement exponential backoff
 * Enhanced for task 5.2.1: Detect Telegram API disconnection
 * 
 * @param {TelegramBot} bot - Bot instance to reconnect
 */
async function handleReconnection(bot) {
  if (reconnectionAttempts >= MAX_RECONNECTION_ATTEMPTS) {
    console.error(`[${new Date().toISOString()}] ❌ Maximum reconnection attempts (${MAX_RECONNECTION_ATTEMPTS}) reached. Giving up.`);
    console.error(`[${new Date().toISOString()}] Please check your network connection and bot token, then restart the service.`);
    
    // Log critical failure
    logger.logError('Maximum reconnection attempts reached', null, {
      maxAttempts: MAX_RECONNECTION_ATTEMPTS,
      totalAttempts: reconnectionAttempts
    });
    
    return;
  }

  const delay = calculateBackoffDelay(reconnectionAttempts);
  reconnectionAttempts++;

  console.log(`[${new Date().toISOString()}] 🔄 Attempting reconnection ${reconnectionAttempts}/${MAX_RECONNECTION_ATTEMPTS} in ${delay}ms...`);
  
  // Log reconnection attempt
  logger.logInfo('Reconnection attempt', {
    attempt: reconnectionAttempts,
    maxAttempts: MAX_RECONNECTION_ATTEMPTS,
    delayMs: delay
  });

  await new Promise(resolve => setTimeout(resolve, delay));

  try {
    // Try to restart polling
    if (!bot.isPolling()) {
      await bot.startPolling();
      console.log(`[${new Date().toISOString()}] ✅ Reconnection successful!`);
      
      // Reset reconnection counter on success
      reconnectionAttempts = 0;
      
      // Reset last polling check time
      lastPollingCheck = Date.now();
      
      // Log successful reconnection
      logger.logInfo('Reconnection successful', {
        attempt: reconnectionAttempts
      });
    } else {
      console.log(`[${new Date().toISOString()}] ℹ️ Bot is already polling`);
      reconnectionAttempts = 0; // Reset counter since we're connected
      lastPollingCheck = Date.now();
    }
  } catch (error) {
    console.error(`[${new Date().toISOString()}] ❌ Reconnection attempt ${reconnectionAttempts} failed:`, error.message);
    
    // Log failed reconnection attempt
    logger.logError('Reconnection attempt failed', error, {
      attempt: reconnectionAttempts,
      maxAttempts: MAX_RECONNECTION_ATTEMPTS
    });
    
    // Recursively try again
    await handleReconnection(bot);
  }
}

// ============================================================================
// Automaton API Client Class
// ============================================================================

/**
 * AutomatonAPIClient - Handles all HTTP communication with the Automaton API service
 * 
 * This class manages:
 * - User registration and status retrieval
 * - Chat message processing
 * - Notification content fetching
 * - Authentication and error handling
 */
class AutomatonAPIClient {
  /**
   * Create an AutomatonAPIClient instance
   * Implements task 2.2.1: Create AutomatonAPIClient class
   */
  constructor() {
    // Sub-task 2.2.1.1: Load AUTOMATON_API_URL from environment
    this.baseURL = AUTOMATON_API_URL;
    if (!this.baseURL) {
      throw new Error('AUTOMATON_API_URL is not defined');
    }

    // Sub-task 2.2.1.2: Load AUTOMATON_API_KEY from environment
    this.apiKey = AUTOMATON_API_KEY;
    if (!this.apiKey) {
      throw new Error('AUTOMATON_API_KEY is not defined');
    }

    // Sub-task 2.2.1.3: Set 30-second timeout for requests
    this.timeout = 30000; // 30 seconds in milliseconds

    console.log(`[${new Date().toISOString()}] ✅ AutomatonAPIClient initialized`);
    console.log(`[${new Date().toISOString()}] API URL: ${this.baseURL}`);
  }

  /**
   * Get common headers for API requests
   * @returns {Object} Headers object with Authorization and Content-Type
   */
  getHeaders() {
    return {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json'
    };
  }

  /**
   * Classify error type and create appropriate error object
   * Implements task 5.1.4: Handle Automaton API errors
   * 
   * @param {Error} error - Original error object
   * @param {Response} response - HTTP response object (if available)
   * @param {string} operationName - Name of the operation for context
   * @returns {Error} Classified error with appropriate message
   */
  classifyError(error, response = null, operationName = '') {
    // Sub-task 5.1.4.1: Handle timeout errors
    if (error.name === 'AbortError' || error.name === 'TimeoutError') {
      const timeoutError = new Error(`Request timed out after ${this.timeout}ms`);
      timeoutError.name = 'TimeoutError';
      timeoutError.isTimeout = true;
      timeoutError.originalError = error;
      return timeoutError;
    }

    // Handle network errors (connection refused, DNS errors, etc.)
    if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND' || 
        error.code === 'ETIMEDOUT' || error.code === 'ECONNRESET') {
      const networkError = new Error('Cannot connect to Automaton API. Service may be unavailable.');
      networkError.name = 'NetworkError';
      networkError.isNetworkError = true;
      networkError.code = error.code;
      networkError.originalError = error;
      return networkError;
    }

    // Sub-task 5.1.4.2: Handle 4xx errors (client errors)
    if (response && response.status >= 400 && response.status < 500) {
      const clientError = new Error(`API client error: ${response.status} ${response.statusText}`);
      clientError.name = 'ClientError';
      clientError.statusCode = response.status;
      clientError.isClientError = true;
      
      // Specific 4xx error handling
      if (response.status === 400) {
        clientError.message = 'Bad request. Please check your input.';
        clientError.isBadRequest = true;
      } else if (response.status === 401) {
        clientError.message = 'Authentication failed. Invalid API key.';
        clientError.isUnauthorized = true;
      } else if (response.status === 403) {
        clientError.message = 'Access forbidden. Insufficient permissions.';
        clientError.isForbidden = true;
      } else if (response.status === 404) {
        clientError.message = 'Resource not found.';
        clientError.isNotFound = true;
      } else if (response.status === 429) {
        clientError.message = 'Rate limit exceeded. Please try again later.';
        clientError.isRateLimited = true;
      }
      
      clientError.originalError = error;
      return clientError;
    }

    // Sub-task 5.1.4.3: Handle 5xx errors (server errors)
    if (response && response.status >= 500 && response.status < 600) {
      const serverError = new Error(`API server error: ${response.status} ${response.statusText}`);
      serverError.name = 'ServerError';
      serverError.statusCode = response.status;
      serverError.isServerError = true;
      
      // Specific 5xx error handling
      if (response.status === 500) {
        serverError.message = 'Internal server error. Please try again later.';
      } else if (response.status === 502) {
        serverError.message = 'Bad gateway. Service temporarily unavailable.';
      } else if (response.status === 503) {
        serverError.message = 'Service unavailable. Please try again later.';
      } else if (response.status === 504) {
        serverError.message = 'Gateway timeout. Service is taking too long to respond.';
      }
      
      serverError.originalError = error;
      return serverError;
    }

    // Return original error if no specific classification
    return error;
  }

  /**
   * Determine if an error should be retried
   * Implements task 5.1.4: Handle Automaton API errors
   * 
   * @param {Error} error - Classified error object
   * @returns {boolean} True if error should be retried
   */
  shouldRetryError(error) {
    // Don't retry client errors (4xx) except rate limiting
    if (error.isClientError && !error.isRateLimited) {
      return false;
    }

    // Retry server errors (5xx)
    if (error.isServerError) {
      return true;
    }

    // Retry timeout errors
    if (error.isTimeout) {
      return true;
    }

    // Retry network errors
    if (error.isNetworkError) {
      return true;
    }

    // Retry rate limit errors
    if (error.isRateLimited) {
      return true;
    }

    // Default: retry unknown errors
    return true;
  }

  /**
   * Get fallback response for when API is unavailable
   * Implements sub-task 5.1.4.4: Provide fallback responses
   * 
   * @param {string} operationName - Name of the operation
   * @returns {Object} Fallback response object
   */
  getFallbackResponse(operationName) {
    switch (operationName) {
      case 'registerUser':
        return {
          success: false,
          fallback: true,
          credits: 0,
          message: 'User registration is temporarily unavailable. Please try again later.'
        };
      
      case 'getUserStatus':
        return {
          success: false,
          fallback: true,
          credits: 0,
          conversationCount: 0,
          lastActivity: null,
          message: 'Status information is temporarily unavailable.'
        };
      
      case 'sendChatMessage':
        return {
          success: false,
          fallback: true,
          response: 'I apologize, but I\'m temporarily unable to process your message. Please try again in a few moments.',
          message: 'Chat service is temporarily unavailable.'
        };
      
      case 'getNotificationContent':
        return {
          success: false,
          fallback: true,
          content: '📢 *System Notification*\n\nScheduled notifications are temporarily unavailable. Please check back later.',
          message: 'Notification service is temporarily unavailable.'
        };
      
      default:
        return {
          success: false,
          fallback: true,
          message: 'Service is temporarily unavailable. Please try again later.'
        };
    }
  }

  /**
   * Retry a failed API request with exponential backoff
   * Implements task 2.2.6: Implement retry logic
   * Enhanced for task 5.1.4: Handle Automaton API errors
   * 
   * @param {Function} requestFn - Async function that performs the API request
   * @param {string} operationName - Name of the operation for logging
   * @param {number} maxRetries - Maximum number of retry attempts (default: 3)
   * @param {number} retryDelay - Delay between retries in milliseconds (default: 2000)
   * @returns {Promise<any>} Result from the API request
   * @throws {Error} If all retry attempts fail
   */
  async retryRequest(requestFn, operationName, maxRetries = 3, retryDelay = 2000) {
    let lastError;
    let response = null;
    
    // Sub-task 2.2.6.1: Retry failed requests up to 3 times
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        // First attempt (attempt 0) is not a retry
        if (attempt === 0) {
          console.log(`[${new Date().toISOString()}] 🔄 Executing ${operationName}...`);
        } else {
          // Sub-task 2.2.6.3: Log retry attempts
          console.log(`[${new Date().toISOString()}] 🔄 Retry attempt ${attempt}/${maxRetries} for ${operationName}...`);
        }
        
        // Execute the request function
        const result = await requestFn();
        
        // If successful, return the result
        if (attempt > 0) {
          console.log(`[${new Date().toISOString()}] ✅ ${operationName} succeeded on retry attempt ${attempt}`);
        }
        return result;
        
      } catch (error) {
        // Classify the error using our enhanced error handling
        lastError = this.classifyError(error, response, operationName);
        
        // Log the classified error
        console.error(`[${new Date().toISOString()}] ❌ ${operationName} error (attempt ${attempt + 1}/${maxRetries + 1}):`, {
          type: lastError.name,
          message: lastError.message,
          statusCode: lastError.statusCode,
          isTimeout: lastError.isTimeout,
          isNetworkError: lastError.isNetworkError,
          isClientError: lastError.isClientError,
          isServerError: lastError.isServerError
        });
        
        // Determine if we should retry this error
        const shouldRetry = this.shouldRetryError(lastError);
        
        if (!shouldRetry) {
          console.error(`[${new Date().toISOString()}] ❌ ${operationName} failed with non-retryable error: ${lastError.message}`);
          throw lastError;
        }
        
        // If this was the last attempt, throw the error
        if (attempt === maxRetries) {
          console.error(`[${new Date().toISOString()}] ❌ ${operationName} failed after ${maxRetries} retries`);
          throw lastError;
        }
        
        // Calculate delay with exponential backoff for rate limiting
        let currentDelay = retryDelay;
        if (lastError.isRateLimited) {
          currentDelay = retryDelay * Math.pow(2, attempt); // Exponential backoff for rate limits
          console.log(`[${new Date().toISOString()}] ⏳ Rate limited. Using exponential backoff: ${currentDelay}ms`);
        }
        
        // Sub-task 2.2.6.2: Use 2-second delay between retries (or exponential for rate limits)
        console.log(`[${new Date().toISOString()}] ⏳ Waiting ${currentDelay}ms before retry...`);
        await new Promise(resolve => setTimeout(resolve, currentDelay));
      }
    }
    
    // This should never be reached, but just in case
    throw lastError;
  }

  /**
   * Register a new user with the Automaton API
   * Implements task 2.2.2: Implement registerUser() method
   * Enhanced for task 5.1.4: Handle Automaton API errors
   * 
   * @param {number} telegramId - Telegram user ID
   * @param {string} username - Telegram username or first name
   * @returns {Promise<Object>} User data including credits
   * @throws {Error} If registration fails
   */
  async registerUser(telegramId, username) {
    // Wrap the actual request in retry logic
    return this.retryRequest(
      async () => {
        let response = null;
        try {
          console.log(`[${new Date().toISOString()}] 📝 Registering user: ${username} (ID: ${telegramId})`);

          // Sub-task 2.2.2.1: POST to /api/users/register
          const url = `${this.baseURL}/api/users/register`;
          
          // Sub-task 2.2.2.2: Include Authorization header with API key
          response = await fetch(url, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({
              telegramId: telegramId,
              username: username
            }),
            signal: AbortSignal.timeout(this.timeout)
          });

          // Sub-task 2.2.2.4: Handle errors gracefully
          if (!response.ok) {
            const errorText = await response.text();
            console.error(`[${new Date().toISOString()}] ❌ API error: ${response.status} ${response.statusText}`);
            console.error(`[${new Date().toISOString()}] Error details: ${errorText}`);
            
            // Create error with response for classification
            const error = new Error(`API request failed: ${response.status} ${response.statusText}`);
            error.response = response;
            error.responseText = errorText;
            throw error;
          }

          // Sub-task 2.2.2.3: Parse JSON response
          const userData = await response.json();
          
          console.log(`[${new Date().toISOString()}] ✅ User registered successfully`);
          console.log(`[${new Date().toISOString()}] Credits: ${userData.credits || 'N/A'}`);
          
          return userData;

        } catch (error) {
          // Classify error with response object
          const classifiedError = this.classifyError(error, response, 'registerUser');
          
          // Sub-task 2.2.2.4: Handle errors gracefully
          console.error(`[${new Date().toISOString()}] ❌ Failed to register user:`, classifiedError.message);
          
          throw classifiedError;
        }
      },
      'registerUser'
    );
  }

  /**
   * Get user status from the Automaton API
   * Implements task 2.2.3: Implement getUserStatus() method
   * Enhanced for task 5.1.4: Handle Automaton API errors
   * 
   * @param {number} userId - Telegram user ID
   * @returns {Promise<Object>} User status data including credits, conversation count, and last activity
   * @throws {Error} If status retrieval fails
   */
  async getUserStatus(userId) {
    // Wrap the actual request in retry logic
    return this.retryRequest(
      async () => {
        let response = null;
        try {
          console.log(`[${new Date().toISOString()}] 📊 Fetching status for user ID: ${userId}`);

          // Sub-task 2.2.3.1: GET from /api/users/{userId}/status
          const url = `${this.baseURL}/api/users/${userId}/status`;
          
          // Sub-task 2.2.3.2: Include Authorization header
          response = await fetch(url, {
            method: 'GET',
            headers: this.getHeaders(),
            signal: AbortSignal.timeout(this.timeout)
          });

          // Handle errors gracefully
          if (!response.ok) {
            const errorText = await response.text();
            console.error(`[${new Date().toISOString()}] ❌ API error: ${response.status} ${response.statusText}`);
            console.error(`[${new Date().toISOString()}] Error details: ${errorText}`);
            
            const error = new Error(`API request failed: ${response.status} ${response.statusText}`);
            error.response = response;
            error.responseText = errorText;
            throw error;
          }

          // Sub-task 2.2.3.3: Parse JSON response
          const userStatus = await response.json();
          
          console.log(`[${new Date().toISOString()}] ✅ User status retrieved successfully`);
          console.log(`[${new Date().toISOString()}] Credits: ${userStatus.credits || 'N/A'}`);
          console.log(`[${new Date().toISOString()}] Conversations: ${userStatus.conversationCount || 'N/A'}`);
          console.log(`[${new Date().toISOString()}] Last Activity: ${userStatus.lastActivity || 'N/A'}`);
          
          return userStatus;

        } catch (error) {
          // Classify error with response object
          const classifiedError = this.classifyError(error, response, 'getUserStatus');
          console.error(`[${new Date().toISOString()}] ❌ Failed to get user status:`, classifiedError.message);
          throw classifiedError;
        }
      },
      'getUserStatus'
    );
  }

  /**
   * Send a chat message to the Automaton API and get AI response
   * Implements task 2.2.4: Implement sendChatMessage() method
   * Enhanced for task 5.1.4: Handle Automaton API errors
   * 
   * @param {number} userId - Telegram user ID
   * @param {string} message - User's message text
   * @returns {Promise<Object>} Chat response data including AI response
   * @throws {Error} If chat request fails
   */
  async sendChatMessage(userId, message) {
    // Wrap the actual request in retry logic
    return this.retryRequest(
      async () => {
        let response = null;
        try {
          console.log(`[${new Date().toISOString()}] 💬 Sending chat message for user ID: ${userId}`);
          console.log(`[${new Date().toISOString()}] Message: ${message.substring(0, 50)}${message.length > 50 ? '...' : ''}`);

          // Sub-task 2.2.4.1: POST to /api/chat
          const url = `${this.baseURL}/api/chat`;
          
          // Sub-task 2.2.4.2: Include user message in request body
          response = await fetch(url, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({
              userId: userId,
              message: message
            }),
            signal: AbortSignal.timeout(this.timeout)
          });

          // Handle errors gracefully
          if (!response.ok) {
            const errorText = await response.text();
            console.error(`[${new Date().toISOString()}] ❌ API error: ${response.status} ${response.statusText}`);
            console.error(`[${new Date().toISOString()}] Error details: ${errorText}`);
            
            const error = new Error(`API request failed: ${response.status} ${response.statusText}`);
            error.response = response;
            error.responseText = errorText;
            throw error;
          }

          // Parse JSON response
          const chatResponse = await response.json();
          
          console.log(`[${new Date().toISOString()}] ✅ Chat response received successfully`);
          console.log(`[${new Date().toISOString()}] Response length: ${chatResponse.response?.length || 0} characters`);
          
          return chatResponse;

        } catch (error) {
          // Classify error with response object
          const classifiedError = this.classifyError(error, response, 'sendChatMessage');
          
          // Sub-task 2.2.4.3: Handle timeout errors
          console.error(`[${new Date().toISOString()}] ❌ Failed to send chat message:`, classifiedError.message);
          
          throw classifiedError;
        }
      },
      'sendChatMessage'
    );
  }

  /**
   * Get notification content from the Automaton API
   * Implements task 2.2.5: Implement getNotificationContent() method
   * Enhanced for task 5.1.4: Handle Automaton API errors
   * 
   * @returns {Promise<Object>} Notification data including content to send to users
   * @throws {Error} If notification content retrieval fails
   */
  async getNotificationContent() {
    // Wrap the actual request in retry logic
    return this.retryRequest(
      async () => {
        let response = null;
        try {
          console.log(`[${new Date().toISOString()}] 🔔 Fetching notification content from API`);

          // Sub-task 2.2.5.1: GET from /api/notifications
          const url = `${this.baseURL}/api/notifications`;
          
          response = await fetch(url, {
            method: 'GET',
            headers: this.getHeaders(),
            signal: AbortSignal.timeout(this.timeout)
          });

          // Handle errors gracefully
          if (!response.ok) {
            const errorText = await response.text();
            console.error(`[${new Date().toISOString()}] ❌ API error: ${response.status} ${response.statusText}`);
            console.error(`[${new Date().toISOString()}] Error details: ${errorText}`);
            
            const error = new Error(`API request failed: ${response.status} ${response.statusText}`);
            error.response = response;
            error.responseText = errorText;
            throw error;
          }

          // Sub-task 2.2.5.2: Parse notification content
          const notificationData = await response.json();
          
          console.log(`[${new Date().toISOString()}] ✅ Notification content retrieved successfully`);
          console.log(`[${new Date().toISOString()}] Content length: ${notificationData.content?.length || 0} characters`);
          
          return notificationData;

        } catch (error) {
          // Classify error with response object
          const classifiedError = this.classifyError(error, response, 'getNotificationContent');
          console.error(`[${new Date().toISOString()}] ❌ Failed to get notification content:`, classifiedError.message);
          throw classifiedError;
        }
      },
      'getNotificationContent'
    );
  }
}

// ============================================================================
// Bot Initialization Function
// ============================================================================

/**
 * Initialize the Telegram bot with polling enabled
 * @returns {TelegramBot} Initialized bot instance
 */
function initializeBot() {
  // Sub-task 2.1.1.1: Load TELEGRAM_BOT_TOKEN from environment
  if (!TELEGRAM_BOT_TOKEN) {
    throw new Error('TELEGRAM_BOT_TOKEN is not defined');
  }

  console.log(`[${new Date().toISOString()}] Initializing CryptoMentor Telegram Bot...`);

  // Sub-task 2.1.1.2: Create TelegramBot instance with polling enabled
  const bot = new TelegramBot(TELEGRAM_BOT_TOKEN, {
    polling: {
      interval: 300,
      autoStart: true,
      params: {
        timeout: 10
      }
    }
  });

  // Sub-task 2.1.1.3: Validate bot token on startup
  bot.getMe()
    .then((botInfo) => {
      // Sub-task 2.1.1.4: Log successful initialization
      console.log(`[${new Date().toISOString()}] ✅ Bot initialized successfully!`);
      console.log(`[${new Date().toISOString()}] Bot username: @${botInfo.username}`);
      console.log(`[${new Date().toISOString()}] Bot ID: ${botInfo.id}`);
      console.log(`[${new Date().toISOString()}] Bot is ready and listening for messages...`);
      
      // Task 5.2.1: Detect Telegram API disconnection
      // Start polling health monitor to proactively detect disconnections
      startPollingHealthMonitor(bot);
    })
    .catch((error) => {
      console.error(`[${new Date().toISOString()}] ❌ Failed to validate bot token:`, error.message);
      process.exit(1);
    });

  // Task 2.1.2: Implement error handlers
  
  // Sub-task 2.1.2.1: Add polling_error event handler
  // Task 5.1.3: Handle Telegram API errors
  // Task 5.2.1: Detect Telegram API disconnection
  bot.on('polling_error', (error) => {
    console.error(`[${new Date().toISOString()}] ⚠️ Polling error detected:`, error.message);
    console.error(`[${new Date().toISOString()}] Error code:`, error.code);
    
    // Update last polling check time to track activity
    lastPollingCheck = Date.now();
    
    // Log full error details for debugging
    if (NODE_ENV !== 'production') {
      console.error(`[${new Date().toISOString()}] Full error:`, error);
    }

    // Task 5.1.3.1: Handle connection failures
    // Task 5.2.1: Detect Telegram API disconnection
    // REQ-2.8.4: Implement exponential backoff for Telegram API reconnection attempts
    // REQ-3.2.2: Automatically recover from Telegram API connection failures
    // Handle various connection-related errors that indicate disconnection
    const connectionErrors = [
      'EFATAL',           // Fatal Telegram API error
      'ETELEGRAM',        // Telegram-specific error
      'ECONNRESET',       // Connection reset by peer
      'ECONNREFUSED',     // Connection refused (server not reachable)
      'ETIMEDOUT',        // Connection timeout
      'ENOTFOUND',        // DNS lookup failed (hostname not found)
      'ENETUNREACH',      // Network unreachable
      'EHOSTUNREACH'      // Host unreachable
    ];
    
    if (connectionErrors.includes(error.code)) {
      console.log(`[${new Date().toISOString()}] 🔌 Telegram API disconnection detected (${error.code})`);
      console.log(`[${new Date().toISOString()}] Initiating automatic reconnection...`);
      
      // Log disconnection event
      logger.logWarn('Telegram API disconnection detected', {
        errorCode: error.code,
        errorMessage: error.message,
        reconnectionAttempts
      });
      
      handleReconnection(bot);
      return;
    }

    // Task 5.1.3.2: Handle rate limiting
    // REQ-2.8.5: Handle Telegram API rate limiting with message queuing
    // CONSTRAINT-7.3.1: Respect Telegram API rate limits (30 messages/second)
    if (error.code === 'ETELEGRAM' && error.response && error.response.statusCode === 429) {
      const retryAfter = error.response.body?.parameters?.retry_after || 60;
      console.warn(`[${new Date().toISOString()}] ⏱️ Rate limit exceeded! Telegram API returned 429.`);
      console.warn(`[${new Date().toISOString()}] Retry after: ${retryAfter} seconds`);
      console.log(`[${new Date().toISOString()}] 💡 Consider reducing message frequency or implementing message queuing`);
      
      // Log rate limiting event for monitoring
      logger.logWarn('Telegram API rate limit exceeded', {
        retryAfter,
        errorCode: error.code,
        statusCode: 429
      });
      return;
    }

    // Task 5.1.3.3: Handle blocked users
    // When a user blocks the bot, Telegram returns 403 Forbidden
    if (error.code === 'ETELEGRAM' && error.response && error.response.statusCode === 403) {
      console.warn(`[${new Date().toISOString()}] 🚫 User blocked the bot or chat not found (403 Forbidden)`);
      console.log(`[${new Date().toISOString()}] This is expected behavior when users block the bot`);
      
      // Extract chat ID if available for logging
      const chatId = error.response.body?.parameters?.chat_id || 'unknown';
      logger.logWarn('User blocked bot or chat not accessible', {
        chatId,
        errorCode: error.code,
        statusCode: 403
      });
      return;
    }

    // Handle other Telegram API errors
    if (error.code === 'ETELEGRAM') {
      const statusCode = error.response?.statusCode;
      console.error(`[${new Date().toISOString()}] 📡 Telegram API error (${statusCode}):`, error.message);
      
      // Log specific error details
      if (error.response?.body) {
        console.error(`[${new Date().toISOString()}] API response:`, JSON.stringify(error.response.body));
      }
      
      logger.logError('Telegram API error', error, {
        statusCode,
        responseBody: error.response?.body
      });
    }

    // Sub-task 2.1.2.3: Implement exponential backoff for reconnection
    // For other fatal errors, attempt reconnection
    if (error.code === 'EFATAL') {
      console.log(`[${new Date().toISOString()}] Fatal error detected, initiating reconnection...`);
      handleReconnection(bot);
    }
  });

  // Sub-task 2.1.2.2: Add general error event handler
  bot.on('error', (error) => {
    console.error(`[${new Date().toISOString()}] ❌ General bot error:`, error.message);
    console.error(`[${new Date().toISOString()}] Error type:`, error.name);
    
    // Log stack trace for debugging
    if (error.stack) {
      console.error(`[${new Date().toISOString()}] Stack trace:`, error.stack);
    }

    // Log full error details in non-production environments
    if (NODE_ENV !== 'production') {
      console.error(`[${new Date().toISOString()}] Full error object:`, error);
    }

    // Use centralized error logger
    logger.logError('General bot error', error, {
      errorName: error.name,
      errorCode: error.code
    });
  });

  return bot;
}

// ============================================================================
// Input Validation Functions
// ============================================================================

/**
 * Validate Telegram user ID
 * Implements task 5.3.1: Validate Telegram user IDs
 * 
 * Telegram user IDs are positive integers (int64) that uniquely identify users.
 * Valid user IDs must be:
 * - A number (not null, undefined, or NaN)
 * - A positive integer (> 0)
 * - Within valid range (1 to 2^53-1 for JavaScript safe integers)
 * 
 * This validation satisfies:
 * - REQ-3.3.3: The system SHALL validate Telegram user IDs before processing requests
 * - REQ-2.8.6: The system SHALL validate all user input before processing
 * 
 * @param {any} userId - User ID to validate
 * @returns {boolean} True if user ID is valid, false otherwise
 */
function isValidTelegramUserId(userId) {
  // Check if userId is null or undefined
  if (userId == null) {
    return false;
  }

  // Check if userId is a number
  if (typeof userId !== 'number') {
    return false;
  }

  // Check if userId is NaN
  if (isNaN(userId)) {
    return false;
  }

  // Check if userId is a positive integer
  if (userId <= 0) {
    return false;
  }

  // Check if userId is an integer (not a float)
  if (!Number.isInteger(userId)) {
    return false;
  }

  // Check if userId is within JavaScript safe integer range
  // Telegram user IDs are int64, but JavaScript can safely represent integers up to 2^53-1
  if (userId > Number.MAX_SAFE_INTEGER) {
    return false;
  }

  // All checks passed - user ID is valid
  return true;
}

/**
 * Validate Telegram message object and extract user information
 * Implements task 5.3.1: Validate Telegram user IDs
 * 
 * This function validates that a message object contains valid user information
 * before processing any commands. It checks:
 * - Message object exists and has required structure
 * - User object exists (msg.from)
 * - User ID is valid according to Telegram specifications
 * 
 * @param {Object} msg - Telegram message object
 * @returns {Object} Validation result with { valid: boolean, userId: number, error: string }
 */
function validateMessageUser(msg) {
  // Check if message object exists
  if (!msg) {
    return {
      valid: false,
      userId: null,
      error: 'Message object is null or undefined'
    };
  }

  // Check if message has 'from' property (user information)
  if (!msg.from) {
    return {
      valid: false,
      userId: null,
      error: 'Message does not contain user information (msg.from is missing)'
    };
  }

  // Extract user ID
  const userId = msg.from.id;

  // Validate user ID using our validation function
  if (!isValidTelegramUserId(userId)) {
    return {
      valid: false,
      userId: userId,
      error: `Invalid Telegram user ID: ${userId}. User ID must be a positive integer.`
    };
  }

  // All validation passed
  return {
    valid: true,
    userId: userId,
    error: null
  };
}

// ============================================================================
// Input Sanitization Functions
// ============================================================================

/**
 * Sanitize user input to prevent injection attacks
 * Implements task 5.3.3: Sanitize user input before API calls
 * 
 * This function sanitizes user input by:
 * - Removing control characters (ASCII 0-31 except newline, tab, carriage return)
 * - Removing zero-width characters and other invisible Unicode characters
 * - Trimming whitespace
 * - Limiting input length to prevent buffer overflow attacks
 * - Normalizing Unicode to prevent homograph attacks
 * 
 * This satisfies:
 * - REQ-2.8.6: The system SHALL sanitize user input to prevent injection attacks
 * - REQ-3.3.4: The system SHALL sanitize user input to prevent injection attacks
 * 
 * @param {string} input - Raw user input to sanitize
 * @param {Object} options - Sanitization options
 * @param {number} options.maxLength - Maximum allowed length (default: 4096 for Telegram limit)
 * @param {boolean} options.allowNewlines - Whether to allow newline characters (default: true)
 * @returns {string} Sanitized input string
 */
function sanitizeUserInput(input, options = {}) {
  // Set default options
  const maxLength = options.maxLength || 4096; // Telegram message limit
  const allowNewlines = options.allowNewlines !== false; // Default to true

  // Handle null, undefined, or non-string input
  if (input == null) {
    return '';
  }

  // Convert to string if not already
  let sanitized = String(input);

  // Normalize Unicode to prevent homograph attacks
  // NFC (Canonical Decomposition, followed by Canonical Composition)
  // This prevents attacks using visually similar Unicode characters
  sanitized = sanitized.normalize('NFC');

  // Remove control characters (ASCII 0-31) except allowed ones
  // Control characters can be used for injection attacks or cause display issues
  // We allow: \n (10), \r (13), \t (9) if newlines are allowed
  if (allowNewlines) {
    // Allow newline, carriage return, and tab
    sanitized = sanitized.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
  } else {
    // Remove all control characters including newlines
    sanitized = sanitized.replace(/[\x00-\x1F\x7F]/g, '');
  }

  // Remove zero-width characters and other invisible Unicode characters
  // These can be used for steganography or to bypass filters
  sanitized = sanitized.replace(/[\u200B-\u200D\uFEFF]/g, ''); // Zero-width spaces
  sanitized = sanitized.replace(/[\u2060-\u2069]/g, ''); // Word joiner, invisible separators
  sanitized = sanitized.replace(/[\u180E]/g, ''); // Mongolian vowel separator

  // Remove bidirectional text override characters
  // These can be used to manipulate text display direction
  sanitized = sanitized.replace(/[\u202A-\u202E]/g, '');
  sanitized = sanitized.replace(/[\u2066-\u2069]/g, '');

  // Trim leading and trailing whitespace
  sanitized = sanitized.trim();

  // Limit length to prevent buffer overflow or DoS attacks
  if (sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
    console.warn(`[${new Date().toISOString()}] ⚠️ Input truncated from ${input.length} to ${maxLength} characters`);
  }

  return sanitized;
}

/**
 * Sanitize username for safe API transmission
 * Implements task 5.3.3: Sanitize username and user data in /start command
 * 
 * Usernames have stricter requirements than messages:
 * - No newlines allowed
 * - Shorter maximum length
 * - Additional character restrictions
 * 
 * @param {string} username - Raw username to sanitize
 * @returns {string} Sanitized username
 */
function sanitizeUsername(username) {
  // Use base sanitization with stricter options
  let sanitized = sanitizeUserInput(username, {
    maxLength: 256, // Reasonable username length limit
    allowNewlines: false // Usernames should not contain newlines
  });

  // If sanitization resulted in empty string, provide fallback
  if (!sanitized || sanitized.length === 0) {
    sanitized = 'User';
  }

  return sanitized;
}

/**
 * Sanitize message text for safe API transmission
 * Implements task 5.3.3: Sanitize user messages in /talk command
 * 
 * @param {string} message - Raw message text to sanitize
 * @returns {string} Sanitized message text
 */
function sanitizeMessage(message) {
  // Use base sanitization with message-appropriate options
  const sanitized = sanitizeUserInput(message, {
    maxLength: 4096, // Telegram message limit
    allowNewlines: true // Messages can contain newlines
  });

  return sanitized;
}

// ============================================================================
// Command Handlers
// ============================================================================

/**
 * Safely send a message to a user with error handling
 * Handles blocked users, deleted chats, and other Telegram API errors
 * Implements task 5.1.3.3: Handle blocked users
 * 
 * @param {TelegramBot} bot - Bot instance
 * @param {number} chatId - Chat ID to send message to
 * @param {string} text - Message text
 * @param {Object} options - Message options (parse_mode, etc.)
 * @returns {Promise<boolean>} True if message sent successfully, false otherwise
 */
async function safeSendMessage(bot, chatId, text, options = {}) {
  try {
    await bot.sendMessage(chatId, text, options);
    return true;
  } catch (error) {
    // Task 5.1.3.3: Handle blocked users
    // When a user blocks the bot, Telegram returns 403 Forbidden
    if (error.response && error.response.statusCode === 403) {
      console.warn(`[${new Date().toISOString()}] 🚫 Cannot send message to chat ${chatId}: User blocked bot or chat not found (403)`);
      logger.logWarn('Message delivery failed - user blocked bot', {
        chatId,
        errorCode: error.code,
        statusCode: 403
      });
      return false;
    }

    // Task 5.1.3.2: Handle rate limiting
    // If we hit rate limits, log and return false
    if (error.response && error.response.statusCode === 429) {
      const retryAfter = error.response.body?.parameters?.retry_after || 60;
      console.warn(`[${new Date().toISOString()}] ⏱️ Rate limit hit when sending to chat ${chatId}. Retry after ${retryAfter}s`);
      logger.logWarn('Message delivery failed - rate limit', {
        chatId,
        retryAfter,
        statusCode: 429
      });
      return false;
    }

    // Task 5.1.3.1: Handle connection failures
    // Log connection errors but don't crash
    const connectionErrors = ['ECONNREFUSED', 'ETIMEDOUT', 'ENOTFOUND', 'ENETUNREACH', 'EHOSTUNREACH', 'ECONNRESET'];
    if (connectionErrors.includes(error.code)) {
      console.error(`[${new Date().toISOString()}] 🔌 Connection error sending to chat ${chatId}: ${error.code}`);
      logger.logError('Message delivery failed - connection error', error, {
        chatId,
        errorCode: error.code
      });
      return false;
    }

    // Log other errors
    console.error(`[${new Date().toISOString()}] ❌ Error sending message to chat ${chatId}:`, error.message);
    logger.logError('Message delivery failed', error, {
      chatId,
      errorCode: error.code,
      statusCode: error.response?.statusCode
    });
    return false;
  }
}

/**
 * Handle /start command - Register user and send welcome message
 * Implements task 3.1.1: Register /start command handler
 * 
 * @param {Object} msg - Telegram message object
 */
/**
 * Handle /start command - Register user and send welcome message
 * Implements task 3.1: Implement /start Command
 *
 * @param {Object} msg - Telegram message object
 */
async function handleStartCommand(msg) {
  const chatId = msg.chat.id;

  // Task 5.3.1: Validate Telegram user IDs
  // REQ-3.3.3: The system SHALL validate Telegram user IDs before processing requests
  const validation = validateMessageUser(msg);
  
  if (!validation.valid) {
    console.error(`[${new Date().toISOString()}] ❌ Invalid user ID in /start command: ${validation.error}`);
    logger.logError('Invalid user ID in /start command', null, {
      error: validation.error,
      userId: validation.userId,
      command: '/start'
    });
    
    // Send error message to user
    const errorMessage = '⚠️ *Validation Error*\n\nYour user information could not be validated. Please try again or contact support.';
    try {
      await bot.sendMessage(chatId, errorMessage, { parse_mode: 'Markdown' });
    } catch (sendError) {
      console.error(`[${new Date().toISOString()}] ❌ Failed to send validation error message:`, sendError.message);
    }
    return;
  }

  // Task 3.1.2: Extract user information from message

  // Sub-task 3.1.2.1: Get Telegram user ID
  // The user ID is a unique identifier for each Telegram user
  const userId = validation.userId;

  // Sub-task 3.1.2.2: Get username or first name
  // Prefer username if available, otherwise use first_name as fallback
  // This ensures we always have a human-readable identifier for the user
  const rawUsername = msg.from.username || msg.from.first_name || 'User';

  // Task 5.3.3: Sanitize username and user data in /start command before API calls
  // REQ-2.8.6: The system SHALL sanitize user input to prevent injection attacks
  // REQ-3.3.4: The system SHALL sanitize user input to prevent injection attacks
  const username = sanitizeUsername(rawUsername);

  console.log(`[${new Date().toISOString()}] 📥 Received /start command from user: ${username} (ID: ${userId})`);
  console.log(`[${new Date().toISOString()}] ✅ User ID validated successfully`);
  console.log(`[${new Date().toISOString()}] ✅ Username sanitized successfully`);
  console.log(`[${new Date().toISOString()}] User details - Username: ${msg.from.username || 'N/A'}, First Name: ${msg.from.first_name || 'N/A'}, Last Name: ${msg.from.last_name || 'N/A'}`);

  try {
    // Task 3.1.3: Call registerUser() API method
    // Task 3.1.7: Ensure idempotency (no duplicate registrations)
    // The Automaton API handles idempotency server-side by checking if a user
    // with the given telegramId already exists. If the user exists, it returns
    // the existing user data instead of creating a duplicate account.
    // This ensures that multiple /start commands from the same user will not
    // create duplicate accounts, satisfying REQ-2.2.3 and Design Property 1.
    const userData = await apiClient.registerUser(userId, username);

    // Determine if this is a new user or returning user based on response
    // The API may include an 'isNewUser' flag or we can infer from the response
    const isNewUser = userData.isNewUser !== false; // Default to true if not specified

    // Task 3.1.4: Format welcome message with credits
    // Customize message based on whether user is new or returning
    let welcomeMessage;
    if (isNewUser) {
      welcomeMessage = `🎉 *Welcome to CryptoMentor!*\n\n` +
        `Your account has been created successfully.\n` +
        `💰 Initial Credits: ${userData.credits || 1000}\n\n` +
        `Use /help to see available commands and get started!`;
    } else {
      welcomeMessage = `👋 *Welcome back to CryptoMentor!*\n\n` +
        `Your account is already set up.\n` +
        `💰 Current Credits: ${userData.credits || 0}\n\n` +
        `Use /help to see available commands.`;
    }

    // Task 3.1.5: Send welcome message to user
    await bot.sendMessage(chatId, welcomeMessage, { parse_mode: 'Markdown' });

    console.log(`[${new Date().toISOString()}] ✅ Welcome message sent to user ${userId} (${isNewUser ? 'new user' : 'returning user'})`);

  } catch (error) {
    console.error(`[${new Date().toISOString()}] ❌ Error handling /start command:`, error.message);

    // Task 3.1.6: Handle API failure with fallback message
    const fallbackMessage = `🎉 *Welcome to CryptoMentor!*\n\n` +
      `We're experiencing some technical difficulties, but you're all set!\n\n` +
      `Please try again in a few moments or use /help to see available commands.`;

    await bot.sendMessage(chatId, fallbackMessage, { parse_mode: 'Markdown' });
  }
}
/**
 * Format a timestamp into human-readable relative time (e.g., "2 hours ago")
 * Helper function for task 3.2.4.3: Display last activity time
 * 
 * @param {string|Date} timestamp - ISO timestamp or Date object
 * @returns {string} Human-readable relative time string
 */
function formatRelativeTime(timestamp) {
  if (!timestamp) {
    return 'Never';
  }

  try {
    const now = new Date();
    const activityDate = new Date(timestamp);
    
    // Calculate difference in milliseconds
    const diffMs = now - activityDate;
    
    // Handle invalid dates or future dates
    if (isNaN(diffMs) || diffMs < 0) {
      return 'Recently';
    }
    
    // Convert to different time units
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    const diffWeeks = Math.floor(diffDays / 7);
    const diffMonths = Math.floor(diffDays / 30);
    const diffYears = Math.floor(diffDays / 365);
    
    // Return appropriate format based on time difference
    if (diffSeconds < 60) {
      return 'Just now';
    } else if (diffMinutes < 60) {
      return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else if (diffWeeks < 4) {
      return `${diffWeeks} week${diffWeeks !== 1 ? 's' : ''} ago`;
    } else if (diffMonths < 12) {
      return `${diffMonths} month${diffMonths !== 1 ? 's' : ''} ago`;
    } else {
      return `${diffYears} year${diffYears !== 1 ? 's' : ''} ago`;
    }
  } catch (error) {
    console.error(`[${new Date().toISOString()}] ⚠️ Error formatting relative time:`, error.message);
    return 'Unknown';
  }
}

/**
 * Format user status data into a readable message with Markdown and emojis
 * Implements task 3.2.4: Format status message
 * 
 * @param {Object} userStatus - User status data from API
 * @returns {string} Formatted status message with Markdown
 */
function formatStatusMessage(userStatus) {
  // Handle missing or null userStatus
  if (!userStatus) {
    return '⚠️ *Status Unavailable*\n\nUnable to retrieve your status information.';
  }

  // Task 3.2.4.1: Display credit balance
  // Format credit balance with proper number formatting (thousand separators)
  const credits = userStatus.credits ?? 0;
  const formattedCredits = credits.toLocaleString('en-US');

  // Task 3.2.4.2: Display conversation count
  // Handle missing conversation count gracefully
  const conversationCount = userStatus.conversationCount ?? 0;

  // Task 3.2.4.3: Display last activity time
  // Format last activity timestamp in human-readable format (e.g., "2 hours ago")
  const lastActivity = formatRelativeTime(userStatus.lastActivity);

  // Build the status message with Markdown formatting and emojis
  // Following the design example: "📊 Your Status:\n Credits: 850\n Active conversations: 3\n Last activity: 2 hours ago"
  const statusMessage = 
    `📊 *Your Status*\n\n` +
    `💰 *Credits:* ${formattedCredits}\n` +
    `💬 *Active conversations:* ${conversationCount}\n` +
    `🕐 *Last activity:* ${lastActivity}`;

  return statusMessage;
}

/**
 * Handle /status command - Display user status information
 * Implements task 3.2.1: Register /status command handler
 *
 * @param {Object} msg - Telegram message object
 */
async function handleStatusCommand(msg) {
  const chatId = msg.chat.id;
  
  // Task 5.3.1: Validate Telegram user IDs
  // REQ-3.3.3: The system SHALL validate Telegram user IDs before processing requests
  const validation = validateMessageUser(msg);
  
  if (!validation.valid) {
    console.error(`[${new Date().toISOString()}] ❌ Invalid user ID in /status command: ${validation.error}`);
    logger.logError('Invalid user ID in /status command', null, {
      error: validation.error,
      userId: validation.userId,
      command: '/status'
    });
    
    // Send error message to user
    const errorMessage = '⚠️ *Validation Error*\n\nYour user information could not be validated. Please try again or contact support.';
    try {
      await bot.sendMessage(chatId, errorMessage, { parse_mode: 'Markdown' });
    } catch (sendError) {
      console.error(`[${new Date().toISOString()}] ❌ Failed to send validation error message:`, sendError.message);
    }
    return;
  }
  
  // Task 3.2.2: Extract user ID from message
  const userId = validation.userId;
  const username = msg.from.username || msg.from.first_name || 'User';

  console.log(`[${new Date().toISOString()}] 📥 Received /status command from user: ${username} (ID: ${userId})`);
  console.log(`[${new Date().toISOString()}] ✅ User ID validated successfully`);

  try {
    // Task 3.2.3: Call getUserStatus() API method
    const userStatus = await apiClient.getUserStatus(userId);

    // Task 3.2.4: Format status message
    const statusMessage = formatStatusMessage(userStatus);
    
    // Task 3.2.5: Send status message to user
    await bot.sendMessage(chatId, statusMessage, { parse_mode: 'Markdown' });
    
    console.log(`[${new Date().toISOString()}] ✅ Status message sent to user ${userId}`);
    
  } catch (error) {
    // Task 3.2.6: Handle API errors gracefully
    // Task 5.1.2.2: Never expose internal errors to users
    // Log error with full context (timestamp, error type, stack trace, user ID)
    console.error(`[${new Date().toISOString()}] ❌ Error handling /status command for user ${userId}:`, error.message);
    console.error(`[${new Date().toISOString()}] Error type: ${error.name}`);
    if (error.stack) {
      console.error(`[${new Date().toISOString()}] Stack trace:`, error.stack);
    }
    
    // Task 5.1.2.1: Use error message templates
    // Create user-friendly error message using centralized templates
    // This ensures consistent, helpful messages that never expose internal details
    const userMessage = createUserErrorMessage(error, 'status');
    
    // Send user-friendly error message (REQ-3.3.7: never expose internal errors)
    try {
      await bot.sendMessage(chatId, userMessage, { parse_mode: 'Markdown' });
      console.log(`[${new Date().toISOString()}] ✅ Error message sent to user ${userId}`);
    } catch (sendError) {
      // If we can't even send the error message, log it but don't crash
      console.error(`[${new Date().toISOString()}] ❌ Failed to send error message to user ${userId}:`, sendError.message);
    }
    
    // Bot continues operating normally after error (REQ-2.8.1)
    console.log(`[${new Date().toISOString()}] Bot continues operating normally after /status error`);
  }
}


/**
 * Format comprehensive help message with all commands, examples, and system information
 * Implements task 3.3.2: Create help message content
 * 
 * @returns {string} Formatted help message with Markdown
 */
function formatHelpMessage() {
  // Task 3.3.2.1: List all available commands
  // Task 3.3.2.2: Provide usage examples
  // Task 3.3.2.3: Explain notification schedule
  // Task 3.3.2.4: Explain credit system
  
  const helpMessage = 
    `📚 *CryptoMentor Help Guide*\n\n` +
    
    // Task 3.3.2.1: List all available commands with descriptions
    `*Available Commands:*\n\n` +
    
    `🚀 */start*\n` +
    `Register your account and receive initial credits.\n` +
    `_Example:_ /start\n\n` +
    
    `📊 */status*\n` +
    `Check your current credit balance, conversation count, and last activity.\n` +
    `_Example:_ /status\n\n` +
    
    `💬 */talk <message>*\n` +
    `Start a conversation with the AI trading mentor. Ask questions about crypto trading, market analysis, or strategies.\n` +
    `_Example:_ /talk What's the best strategy for Bitcoin trading?\n\n` +
    
    `❓ */help*\n` +
    `Display this help message with all available commands and information.\n` +
    `_Example:_ /help\n\n` +
    
    `━━━━━━━━━━━━━━━━━━━━\n\n` +
    
    // Task 3.3.2.3: Explain notification schedule
    `🔔 *Scheduled Notifications*\n\n` +
    `You'll receive automated market updates and insights at:\n` +
    `• 08:00 WIB (Morning Update)\n` +
    `• 14:00 WIB (Afternoon Update)\n` +
    `• 20:00 WIB (Evening Update)\n\n` +
    `All times are in Western Indonesian Time (UTC+7).\n\n` +
    
    `━━━━━━━━━━━━━━━━━━━━\n\n` +
    
    // Task 3.3.2.4: Explain credit system
    `💰 *Credit System*\n\n` +
    `Credits are used to power your AI conversations:\n\n` +
    `• New users receive initial credits upon registration\n` +
    `• Each /talk conversation uses credits\n` +
    `• Check your balance anytime with /status\n` +
    `• Contact support to obtain more credits\n\n` +
    
    `━━━━━━━━━━━━━━━━━━━━\n\n` +
    
    `💡 *Tips:*\n` +
    `• Be specific in your questions for better AI responses\n` +
    `• Use /status regularly to monitor your credit balance\n` +
    `• Scheduled notifications are free and automatic\n\n` +
    
    `Need more help? Just ask using /talk!`;
  
  return helpMessage;
}

/**
 * Handle /help command - Display available commands and usage information
 * Implements task 3.3.1: Register /help command handler
 *
 * @param {Object} msg - Telegram message object
 */
async function handleHelpCommand(msg) {
  const chatId = msg.chat.id;
  
  // Task 5.3.1: Validate Telegram user IDs
  // REQ-3.3.3: The system SHALL validate Telegram user IDs before processing requests
  const validation = validateMessageUser(msg);
  
  if (!validation.valid) {
    console.error(`[${new Date().toISOString()}] ❌ Invalid user ID in /help command: ${validation.error}`);
    logger.logError('Invalid user ID in /help command', null, {
      error: validation.error,
      userId: validation.userId,
      command: '/help'
    });
    
    // Send error message to user
    const errorMessage = '⚠️ *Validation Error*\n\nYour user information could not be validated. Please try again or contact support.';
    try {
      await bot.sendMessage(chatId, errorMessage, { parse_mode: 'Markdown' });
    } catch (sendError) {
      console.error(`[${new Date().toISOString()}] ❌ Failed to send validation error message:`, sendError.message);
    }
    return;
  }
  
  const userId = validation.userId;
  const username = msg.from.username || msg.from.first_name || 'User';

  console.log(`[${new Date().toISOString()}] 📥 Received /help command from user: ${username} (ID: ${userId})`);
  console.log(`[${new Date().toISOString()}] ✅ User ID validated successfully`);

  try {
    // Task 3.3.3: Format help message with Markdown
    const helpMessage = formatHelpMessage();

    // Task 3.3.4: Send help message to user
    await bot.sendMessage(chatId, helpMessage, { parse_mode: 'Markdown' });
    
    console.log(`[${new Date().toISOString()}] ✅ Help message sent to user ${userId}`);
    
  } catch (error) {
    console.error(`[${new Date().toISOString()}] ❌ Error handling /help command for user ${userId}:`, error.message);
    
    // Task 5.1.2.1: Use error message templates
    // Task 5.1.2.2: Never expose internal errors to users
    const errorMessage = createUserErrorMessage(error, 'help');
    
    try {
      await bot.sendMessage(chatId, errorMessage, { parse_mode: 'Markdown' });
    } catch (sendError) {
      console.error(`[${new Date().toISOString()}] ❌ Failed to send error message to user ${userId}:`, sendError.message);
    }
  }
}

/**
 * Handle /talk command - Process user conversation with AI
 * Implements task 3.4.1: Register /talk command handler with regex pattern
 * 
 * This function is called when a user sends a message matching the pattern /\/talk (.+)/
 * The regex captures the message text after "/talk " in match[1]
 * 
 * @param {Object} msg - Telegram message object
 * @param {Array} match - Regex match array where match[1] contains the captured message text
 */
async function handleConversation(msg, match) {
  const chatId = msg.chat.id;
  
  // Task 5.3.1: Validate Telegram user IDs
  // REQ-3.3.3: The system SHALL validate Telegram user IDs before processing requests
  const validation = validateMessageUser(msg);
  
  if (!validation.valid) {
    console.error(`[${new Date().toISOString()}] ❌ Invalid user ID in /talk command: ${validation.error}`);
    logger.logError('Invalid user ID in /talk command', null, {
      error: validation.error,
      userId: validation.userId,
      command: '/talk'
    });
    
    // Send error message to user
    const errorMessage = '⚠️ *Validation Error*\n\nYour user information could not be validated. Please try again or contact support.';
    try {
      await bot.sendMessage(chatId, errorMessage, { parse_mode: 'Markdown' });
    } catch (sendError) {
      console.error(`[${new Date().toISOString()}] ❌ Failed to send validation error message:`, sendError.message);
    }
    return;
  }
  
  const userId = validation.userId;
  const username = msg.from.username || msg.from.first_name || 'User';

  // Task 3.4.2: Extract user message from command arguments
  // The regex pattern /\/talk (.+)/ captures everything after "/talk " in match[1]
  const rawUserMessage = match[1];

  console.log(`[${new Date().toISOString()}] 📥 Received /talk command from user: ${username} (ID: ${userId})`);
  console.log(`[${new Date().toISOString()}] ✅ User ID validated successfully`);
  console.log(`[${new Date().toISOString()}] User message (raw): ${rawUserMessage.substring(0, 100)}${rawUserMessage.length > 100 ? '...' : ''}`);

  // Task 3.4.3: Validate message is not empty
  // Check if the message is empty or contains only whitespace
  // The regex /\/talk (.+)/ requires at least one character, but we need to check for whitespace-only messages
  // This satisfies REQ-2.8.6 (validate all user input) and REQ-2.8.7 (handle malformed commands)
  if (!rawUserMessage || rawUserMessage.trim().length === 0) {
    console.log(`[${new Date().toISOString()}] ⚠️ Empty or whitespace-only message detected from user ${userId}`);
    
    // Task 5.1.2.1: Use error message templates
    const errorMessage = formatErrorMessage(ErrorMessages.INPUT.EMPTY_MESSAGE);
    
    try {
      await bot.sendMessage(chatId, errorMessage, { parse_mode: 'Markdown' });
      console.log(`[${new Date().toISOString()}] ✅ Validation error message sent to user ${userId}`);
    } catch (error) {
      console.error(`[${new Date().toISOString()}] ❌ Failed to send validation error message to user ${userId}:`, error.message);
    }
    
    // Return early without processing the conversation
    return;
  }

  // Task 5.3.3: Sanitize user messages in /talk command before API calls
  // REQ-2.8.6: The system SHALL sanitize user input to prevent injection attacks
  // REQ-3.3.4: The system SHALL sanitize user input to prevent injection attacks
  const userMessage = sanitizeMessage(rawUserMessage);

  console.log(`[${new Date().toISOString()}] ✅ User message sanitized successfully`);
  console.log(`[${new Date().toISOString()}] User message (sanitized): ${userMessage.substring(0, 100)}${userMessage.length > 100 ? '...' : ''}`);

  // Validate sanitized message is not empty (in case sanitization removed everything)
  if (!userMessage || userMessage.length === 0) {
    console.log(`[${new Date().toISOString()}] ⚠️ Message became empty after sanitization for user ${userId}`);
    
    const errorMessage = formatErrorMessage(ErrorMessages.INPUT.EMPTY_MESSAGE, {
      note: 'Your message contained only invalid characters. Please send a valid message.'
    });
    
    try {
      await bot.sendMessage(chatId, errorMessage, { parse_mode: 'Markdown' });
      console.log(`[${new Date().toISOString()}] ✅ Sanitization error message sent to user ${userId}`);
    } catch (error) {
      console.error(`[${new Date().toISOString()}] ❌ Failed to send sanitization error message to user ${userId}:`, error.message);
    }
    
    return;
  }

  try {
    // Task 3.4.4: Check user credit balance
    // REQ-2.4.2: The system SHALL check user credit balance before processing conversation requests
    
    // Sub-task 3.4.4.1: Call getUserStatus() to get credits
    console.log(`[${new Date().toISOString()}] 💰 Checking credit balance for user ${userId}...`);
    const userStatus = await apiClient.getUserStatus(userId);
    
    // Sub-task 3.4.4.2: Verify sufficient credits
    // Check if user has enough credits to cover the conversation cost
    const userCredits = userStatus.credits ?? 0;
    console.log(`[${new Date().toISOString()}] User has ${userCredits} credits, conversation costs ${CONVERSATION_COST} credits`);
    
    if (userCredits < CONVERSATION_COST) {
      // Sub-task 3.4.4.3: Send insufficient credits message if needed
      // REQ-2.4.6: The system SHALL notify users when they have insufficient credits for conversation
      console.log(`[${new Date().toISOString()}] ⚠️ User ${userId} has insufficient credits (${userCredits} < ${CONVERSATION_COST})`);
      
      // Task 5.1.2.1: Use error message templates
      const template = ErrorMessages.CREDITS.INSUFFICIENT;
      const insufficientCreditsMessage = formatErrorMessage(template, {
        note: `You need ${CONVERSATION_COST} credits to start a conversation, but you currently have ${userCredits} credits.\n\nUse /status to check your current balance anytime.`
      });
      
      await bot.sendMessage(chatId, insufficientCreditsMessage, { parse_mode: 'Markdown' });
      console.log(`[${new Date().toISOString()}] ✅ Insufficient credits message sent to user ${userId}`);
      
      // Return early without processing the conversation
      return;
    }
    
    // User has sufficient credits, log success and continue
    console.log(`[${new Date().toISOString()}] ✅ User ${userId} has sufficient credits (${userCredits} >= ${CONVERSATION_COST})`);
    
    // Task 3.4.5: Send typing indicator to user
    // REQ-2.4.3: The system SHALL send "typing" chat action indicator while processing conversation requests
    // This provides visual feedback to the user that their message is being processed
    console.log(`[${new Date().toISOString()}] ⌨️ Sending typing indicator to user ${userId}...`);
    try {
      await bot.sendChatAction(chatId, 'typing');
      console.log(`[${new Date().toISOString()}] ✅ Typing indicator sent to user ${userId}`);
    } catch (typingError) {
      // Log error but continue processing - typing indicator is not critical
      console.warn(`[${new Date().toISOString()}] ⚠️ Failed to send typing indicator to user ${userId}:`, typingError.message);
    }
    
    // Task 3.4.6: Call sendChatMessage() API method
    // REQ-2.4.4: The system SHALL forward user messages to the Automaton API chat endpoint
    console.log(`[${new Date().toISOString()}] 🤖 Sending message to Automaton API for user ${userId}...`);
    const chatResponse = await apiClient.sendChatMessage(userId, userMessage);
    
    // Task 3.4.7: Send AI response to user
    // REQ-2.4.5: The system SHALL deliver AI-generated responses from the API to the user
    // Extract the AI response from the API result
    const aiResponse = chatResponse.response || chatResponse.message || 'No response received from AI.';
    
    console.log(`[${new Date().toISOString()}] 📤 Sending AI response to user ${userId}...`);
    console.log(`[${new Date().toISOString()}] Response length: ${aiResponse.length} characters`);
    
    // Send the AI response to the user with Markdown formatting
    await bot.sendMessage(chatId, aiResponse, { parse_mode: 'Markdown' });
    
    console.log(`[${new Date().toISOString()}] ✅ AI response sent successfully to user ${userId}`);
    
  } catch (error) {
    // Task 3.4.8: Handle timeout errors with user-friendly message
    // Task 3.4.9: Handle API errors gracefully
    // Task 5.1.2.1: Use error message templates
    // Task 5.1.2.2: Never expose internal errors to users
    // REQ-2.4.7: The system SHALL handle API timeouts gracefully with user-friendly error messages
    // REQ-2.8.2: The system SHALL send user-friendly error messages for all failure scenarios
    // REQ-3.3.7: The system SHALL not expose internal error details to end users
    
    console.error(`[${new Date().toISOString()}] ❌ Error in conversation handler for user ${userId}:`, error.message);
    console.error(`[${new Date().toISOString()}] Error type: ${error.name}`);
    if (error.stack) {
      console.error(`[${new Date().toISOString()}] Stack trace:`, error.stack);
    }
    
    // Use centralized error message templates
    const userMessage = createUserErrorMessage(error, 'talk');
    
    // Send user-friendly error message (never expose internal errors)
    try {
      await bot.sendMessage(chatId, userMessage, { parse_mode: 'Markdown' });
      console.log(`[${new Date().toISOString()}] ✅ Error message sent to user ${userId}`);
    } catch (sendError) {
      // If we can't even send the error message, log it but don't crash
      console.error(`[${new Date().toISOString()}] ❌ Failed to send error message to user ${userId}:`, sendError.message);
    }
    
    // Bot continues operating normally after error (REQ-2.8.1)
    console.log(`[${new Date().toISOString()}] Bot continues operating normally after /talk error`);
  }
}

// ============================================================================
// Notification Scheduler
// ============================================================================

/**
 * Get list of active users who should receive notifications
 * Implements task 4.2.3.1: Implement getActiveUsers() function
 * 
 * @returns {Promise<Array>} Array of active user objects with telegramId
 */
async function getActiveUsers() {
  // Task 4.2.3.2: Filter out inactive users
  // For now, we'll return a simple implementation that would need to be
  // connected to a user database or API endpoint in production
  
  console.log(`[${new Date().toISOString()}] 📋 Fetching active users list...`);
  
  try {
    // In a production system, this would call an API endpoint like:
    // const response = await fetch(`${AUTOMATON_API_URL}/api/users/active`, {
    //   headers: apiClient.getHeaders()
    // });
    // const users = await response.json();
    
    // For now, return an empty array as a placeholder
    // The actual implementation would depend on the Automaton API providing
    // an endpoint to list active users
    console.log(`[${new Date().toISOString()}] ⚠️ getActiveUsers() is a placeholder - no users to notify yet`);
    console.log(`[${new Date().toISOString()}] 💡 In production, this would fetch from ${AUTOMATON_API_URL}/api/users/active`);
    
    return [];
    
  } catch (error) {
    console.error(`[${new Date().toISOString()}] ❌ Failed to fetch active users:`, error.message);
    // Return empty array on error to prevent notification delivery failure
    return [];
  }
}

/**
 * Send scheduled notifications to all active users
 * Implements task 4.2.1: Create sendScheduledNotifications() function
 * 
 * This function is called by cron jobs at scheduled times (08:00, 14:00, 20:00 WIB)
 * It fetches notification content from the API and delivers it to all active users
 * 
 * @param {string} time - The scheduled time (for logging purposes)
 */
async function sendScheduledNotifications(time) {
  console.log(`[${new Date().toISOString()}] 🔔 ========================================`);
  console.log(`[${new Date().toISOString()}] 🔔 Starting scheduled notification delivery for ${time}`);
  console.log(`[${new Date().toISOString()}] 🔔 ========================================`);
  
  try {
    // Task 4.2.2: Fetch notification content from API
    // Sub-task 4.2.2.1: Call getNotificationContent()
    console.log(`[${new Date().toISOString()}] 📥 Fetching notification content from Automaton API...`);
    
    let notificationContent;
    try {
      const notificationData = await apiClient.getNotificationContent();
      notificationContent = notificationData.content || notificationData.message || 'No notification content available.';
      console.log(`[${new Date().toISOString()}] ✅ Notification content fetched successfully`);
      console.log(`[${new Date().toISOString()}] Content preview: ${notificationContent.substring(0, 100)}${notificationContent.length > 100 ? '...' : ''}`);
    } catch (error) {
      // Sub-task 4.2.2.2: Handle API failure gracefully
      // REQ-2.3.5: Continue notification delivery even if content fetch fails
      console.error(`[${new Date().toISOString()}] ❌ Failed to fetch notification content:`, error.message);
      console.log(`[${new Date().toISOString()}] 📝 Using fallback notification message`);
      
      // Use fallback notification content
      notificationContent = 
        `🔔 *Scheduled Update - ${time}*\n\n` +
        `Hello! This is your scheduled notification from CryptoMentor.\n\n` +
        `We're currently experiencing technical difficulties fetching the latest content, ` +
        `but we wanted to let you know we're still here!\n\n` +
        `Use /talk to ask questions or /status to check your account.`;
    }
    
    // Task 4.2.3: Get list of active users
    console.log(`[${new Date().toISOString()}] 👥 Fetching active users list...`);
    const activeUsers = await getActiveUsers();
    console.log(`[${new Date().toISOString()}] 📊 Found ${activeUsers.length} active users to notify`);
    
    // If no active users, log and return early
    if (activeUsers.length === 0) {
      console.log(`[${new Date().toISOString()}] ℹ️ No active users to notify. Notification delivery complete.`);
      console.log(`[${new Date().toISOString()}] 🔔 ========================================`);
      return;
    }
    
    // Task 4.2.5: Track delivery statistics
    // Sub-task 4.2.5.1: Count successful deliveries
    // Sub-task 4.2.5.2: Count failed deliveries
    let successCount = 0;
    let failureCount = 0;
    const failedUsers = []; // Track which users failed for detailed logging
    
    // Task 4.2.4: Implement delivery loop
    // Sub-task 4.2.4.1: Iterate through all active users
    console.log(`[${new Date().toISOString()}] 📤 Starting notification delivery to ${activeUsers.length} users...`);
    
    for (let i = 0; i < activeUsers.length; i++) {
      const user = activeUsers[i];
      
      // Validate user has telegramId
      if (!user.telegramId) {
        console.warn(`[${new Date().toISOString()}] ⚠️ Skipping user ${i + 1}/${activeUsers.length}: Missing telegramId`);
        failureCount++;
        failedUsers.push({ user: `User ${i + 1}`, reason: 'Missing telegramId' });
        continue;
      }
      
      try {
        // Sub-task 4.2.4.2: Send notification to each user
        console.log(`[${new Date().toISOString()}] 📨 Sending notification to user ${user.telegramId} (${i + 1}/${activeUsers.length})...`);
        
        // Use safeSendMessage to handle blocked users and other errors gracefully
        // Task 5.1.3.3: Handle blocked users
        const sent = await safeSendMessage(bot, user.telegramId, notificationContent, { 
          parse_mode: 'Markdown' 
        });
        
        if (sent) {
          // Increment success counter
          successCount++;
          console.log(`[${new Date().toISOString()}] ✅ Notification sent successfully to user ${user.telegramId}`);
        } else {
          // Message sending failed (blocked user, rate limit, etc.)
          failureCount++;
          failedUsers.push({ 
            user: user.telegramId, 
            username: user.username || 'Unknown',
            reason: 'Message delivery failed (see logs for details)' 
          });
          console.log(`[${new Date().toISOString()}] ⚠️ Failed to send notification to user ${user.telegramId}`);
        }
        
        // Task 4.2.6: Implement rate limiting
        // Sub-task 4.2.6.1: Respect Telegram's 30 msg/sec limit
        // Sub-task 4.2.6.2: Add delays between messages if needed
        // Telegram API limit is 30 messages per second
        // To be safe, we'll send at most 20 messages per second (50ms delay between messages)
        // This gives us a safety margin and prevents rate limiting errors
        if (i < activeUsers.length - 1) { // Don't delay after the last message
          const delayMs = 50; // 50ms = 20 messages per second
          console.log(`[${new Date().toISOString()}] ⏳ Rate limiting: waiting ${delayMs}ms before next message...`);
          await new Promise(resolve => setTimeout(resolve, delayMs));
        }
        
      } catch (error) {
        // Sub-task 4.2.4.3: Handle individual delivery failures
        // Sub-task 4.2.4.4: Continue on failure (don't stop batch)
        // REQ-2.3.5: The system SHALL continue notification delivery to remaining users even if delivery to some users fails
        console.error(`[${new Date().toISOString()}] ❌ Failed to send notification to user ${user.telegramId}:`, error.message);
        
        // Increment failure counter
        failureCount++;
        failedUsers.push({ 
          user: user.telegramId, 
          username: user.username || 'Unknown',
          reason: error.message 
        });
        
        // Log specific error types for debugging
        if (error.response && error.response.body) {
          console.error(`[${new Date().toISOString()}] Error details:`, error.response.body);
        }
        
        // Common error scenarios:
        // - User blocked the bot
        // - User deleted their account
        // - Invalid chat ID
        // - Network error
        
        // Continue to next user (don't throw or break)
        console.log(`[${new Date().toISOString()}] ℹ️ Continuing with remaining users...`);
      }
    }
    
    // Task 4.2.5.3: Log statistics after batch
    // REQ-2.3.6: The system SHALL log delivery statistics (success count, failure count) after each notification batch
    console.log(`[${new Date().toISOString()}] 🔔 ========================================`);
    console.log(`[${new Date().toISOString()}] 📊 Notification Delivery Statistics for ${time}:`);
    console.log(`[${new Date().toISOString()}] ✅ Successful deliveries: ${successCount}`);
    console.log(`[${new Date().toISOString()}] ❌ Failed deliveries: ${failureCount}`);
    console.log(`[${new Date().toISOString()}] 📈 Success rate: ${activeUsers.length > 0 ? ((successCount / activeUsers.length) * 100).toFixed(2) : 0}%`);
    
    // Log details of failed deliveries for debugging
    if (failedUsers.length > 0) {
      console.log(`[${new Date().toISOString()}] 📋 Failed delivery details:`);
      failedUsers.forEach((failure, index) => {
        console.log(`[${new Date().toISOString()}]   ${index + 1}. User: ${failure.user} (${failure.username || 'N/A'}) - Reason: ${failure.reason}`);
      });
    }
    
    console.log(`[${new Date().toISOString()}] 🔔 Notification delivery complete for ${time}`);
    console.log(`[${new Date().toISOString()}] 🔔 ========================================`);
    
  } catch (error) {
    // Handle unexpected errors in the notification delivery process
    console.error(`[${new Date().toISOString()}] ❌ Critical error in sendScheduledNotifications:`, error.message);
    console.error(`[${new Date().toISOString()}] Stack trace:`, error.stack);
    console.log(`[${new Date().toISOString()}] 🔔 ========================================`);
    
    // Don't throw - we want the bot to continue operating even if notifications fail
    // REQ-2.8.1: The system SHALL remain operational when the Automaton API is unavailable
  }
}

// ============================================================================
// Main Execution
// ============================================================================

// Initialize the API client
const apiClient = new AutomatonAPIClient();

// Initialize the bot
const bot = initializeBot();

// Task 3.1.1: Register /start command handler
bot.onText(/\/start/, handleStartCommand);

console.log(`[${new Date().toISOString()}] ✅ /start command handler registered`);

// Task 3.2.1: Register /status command handler
bot.onText(/\/status/, handleStatusCommand);

console.log(`[${new Date().toISOString()}] ✅ /status command handler registered`);

// Task 3.3.1: Register /help command handler
bot.onText(/\/help/, handleHelpCommand);

console.log(`[${new Date().toISOString()}] ✅ /help command handler registered`);

// Task 3.4.1: Register /talk command handler with regex pattern
// The regex pattern /\/talk (.+)/ captures the message text after "/talk "
// The (.+) group matches one or more characters (the user's message)
// This pattern is passed to handleConversation() which will extract the message
// NOTE: This must be registered BEFORE the validation handler so it matches first
bot.onText(/\/talk (.+)/, handleConversation);

console.log(`[${new Date().toISOString()}] ✅ /talk command handler registered`);

// Task 5.3.2: Validate command arguments
// Handle /talk command without arguments (validation)
// This catches when user sends just "/talk" without a message
// NOTE: This is registered AFTER the main handler, so it only catches "/talk" with no args
bot.onText(/\/talk\s*$/, async (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from?.id;
  
  console.log(`[${new Date().toISOString()}] ⚠️ User ${userId} sent /talk without message argument`);
  
  // REQ-2.8.7: Handle malformed commands with helpful usage instructions
  const errorMessage = formatErrorMessage(ErrorMessages.INPUT.EMPTY_MESSAGE, {
    note: 'Please provide a message after the /talk command.\n\n*Example:*\n`/talk What is Bitcoin?`'
  });
  
  try {
    await bot.sendMessage(chatId, errorMessage, { parse_mode: 'Markdown' });
    console.log(`[${new Date().toISOString()}] ✅ Usage instruction sent to user ${userId}`);
  } catch (error) {
    console.error(`[${new Date().toISOString()}] ❌ Failed to send usage instruction:`, error.message);
  }
});

console.log(`[${new Date().toISOString()}] ✅ /talk validation handler registered (no arguments)`);

// ============================================================================
// Task 5.3.4: Handle Malformed Commands
// ============================================================================

/**
 * Detect common command typos and suggest corrections
 * Implements task 5.3.4: Provide helpful error messages with examples
 * 
 * @param {string} command - The malformed command
 * @returns {string|null} Suggested correction or null if no match
 */
function suggestCommandCorrection(command) {
  const commandLower = command.toLowerCase();
  
  // Common typos and variations
  const suggestions = {
    '/stat': '/status',
    '/stats': '/status',
    '/balance': '/status',
    '/credits': '/status',
    '/begin': '/start',
    '/register': '/start',
    '/signup': '/start',
    '/info': '/help',
    '/commands': '/help',
    '/chat': '/talk',
    '/ask': '/talk',
    '/message': '/talk',
    '/say': '/talk',
    '/speak': '/talk'
  };
  
  return suggestions[commandLower] || null;
}

/**
 * Generate helpful error message for malformed commands
 * Implements task 5.3.4: Provide helpful error messages when users send incorrect command syntax
 * 
 * @param {string} command - The malformed command
 * @param {string} fullText - The full message text
 * @returns {string} Formatted error message with guidance
 */
function generateMalformedCommandMessage(command, fullText) {
  // Check for suggested correction
  const suggestion = suggestCommandCorrection(command);
  
  let message = `❓ *Unknown Command*\n\n`;
  
  if (suggestion) {
    // Provide specific suggestion for common typos
    message += `I don't recognize \`${command}\`.\n\n`;
    message += `💡 *Did you mean:* \`${suggestion}\`?\n\n`;
    message += `Try typing \`${suggestion}\` to use this command.\n\n`;
  } else {
    // Generic unknown command message
    message += `I don't recognize the command \`${command}\`.\n\n`;
  }
  
  // Add list of available commands
  message += `*✅ Available Commands:*\n\n`;
  message += `• \`/start\` - Register and get started\n`;
  message += `• \`/status\` - Check your credit balance\n`;
  message += `• \`/help\` - View detailed help\n`;
  message += `• \`/talk <message>\` - Chat with AI\n\n`;
  
  // Add usage examples
  message += `*📝 Examples:*\n`;
  message += `\`/start\` - Create your account\n`;
  message += `\`/status\` - View your credits\n`;
  message += `\`/talk What is Bitcoin?\` - Ask a question\n\n`;
  
  // Encourage using help command
  message += `*Need more help?* Use \`/help\` for detailed information.`;
  
  return message;
}

/**
 * Handle unrecognized and malformed commands
 * Implements task 5.3.4: Handle malformed commands
 * Implements REQ-2.8.7: Handle malformed commands with helpful usage instructions
 * Implements REQ-5.1.5: Respond to unrecognized commands with help message
 * 
 * This catch-all handler responds to any message that starts with "/" but
 * doesn't match any registered command. It provides helpful guidance to users
 * including:
 * - Detection of common typos with suggestions
 * - Clear error messages explaining the issue
 * - List of available commands
 * - Usage examples
 * - Guidance to correct usage
 */
bot.on('message', async (msg) => {
  // Only handle messages that start with "/" (commands)
  const text = msg.text;
  if (!text || !text.startsWith('/')) {
    return; // Not a command, ignore
  }

  const chatId = msg.chat.id;
  const userId = msg.from?.id;

  // Extract the command (first word)
  const command = text.split(' ')[0].toLowerCase();

  // List of recognized commands
  const recognizedCommands = ['/start', '/status', '/help', '/talk'];

  // Check if this is a recognized command
  if (recognizedCommands.includes(command)) {
    return; // This is a recognized command, let the specific handler deal with it
  }

  // Task 5.3.4: Handle malformed or invalid commands
  // This is an unrecognized/malformed command
  console.log(`[${new Date().toISOString()}] ⚠️ User ${userId} sent unrecognized command: ${command}`);
  console.log(`[${new Date().toISOString()}] Full message text: ${text}`);
  
  // Log malformed command for monitoring
  logger.logWarn('Malformed command received', {
    userId,
    command,
    fullText: text,
    operation: 'handleMalformedCommand'
  });

  // Task 5.3.4: Provide helpful error messages when users send incorrect command syntax
  // Task 5.3.4: Guide users to correct usage with examples
  // REQ-2.8.7: Handle malformed commands with helpful usage instructions
  const errorMessage = generateMalformedCommandMessage(command, text);

  try {
    // Task 5.3.4: Ensure bot remains operational when receiving invalid input
    await bot.sendMessage(chatId, errorMessage, { parse_mode: 'Markdown' });
    console.log(`[${new Date().toISOString()}] ✅ Malformed command help sent to user ${userId}`);
    
    // Log successful error message delivery
    logger.logInfo('Malformed command help sent', {
      userId,
      command,
      operation: 'handleMalformedCommand'
    });
  } catch (error) {
    console.error(`[${new Date().toISOString()}] ❌ Failed to send malformed command help:`, error.message);
    logger.logError('Failed to send malformed command help', error, {
      userId,
      command,
      operation: 'handleMalformedCommand'
    });
  }
});

console.log(`[${new Date().toISOString()}] ✅ Malformed command handler registered (catch-all)`);

// ============================================================================
// Schedule Notifications
// ============================================================================

// Task 4.1: Implement Notification Scheduler
// Task 4.1.2: Import node-cron library (already imported at top of file)
// Task 4.1.3: Configure Asia/Jakarta timezone

console.log(`[${new Date().toISOString()}] 🔔 Setting up scheduled notifications...`);

// Task 4.1.4: Schedule notification for 08:00 WIB
// Sub-task 4.1.4.1: Create cron expression: "0 8 * * *"
// Sub-task 4.1.4.2: Register cron job
// REQ-2.3.1: The system SHALL send automated notifications to all active users at 08:00 WIB (UTC+7)
// REQ-2.3.7: The system SHALL use Asia/Jakarta timezone for all scheduled notifications
cron.schedule('0 8 * * *', () => {
  console.log(`[${new Date().toISOString()}] ⏰ Cron job triggered: 08:00 WIB notification`);
  sendScheduledNotifications('08:00 WIB');
}, {
  timezone: 'Asia/Jakarta'
});

console.log(`[${new Date().toISOString()}] ✅ Scheduled notification for 08:00 WIB (Asia/Jakarta timezone)`);

// Task 4.1.5: Schedule notification for 14:00 WIB
// Sub-task 4.1.5.1: Create cron expression: "0 14 * * *"
// Sub-task 4.1.5.2: Register cron job
// REQ-2.3.2: The system SHALL send automated notifications to all active users at 14:00 WIB (UTC+7)
cron.schedule('0 14 * * *', () => {
  console.log(`[${new Date().toISOString()}] ⏰ Cron job triggered: 14:00 WIB notification`);
  sendScheduledNotifications('14:00 WIB');
}, {
  timezone: 'Asia/Jakarta'
});

console.log(`[${new Date().toISOString()}] ✅ Scheduled notification for 14:00 WIB (Asia/Jakarta timezone)`);

// Task 4.1.6: Schedule notification for 20:00 WIB
// Sub-task 4.1.6.1: Create cron expression: "0 20 * * *"
// Sub-task 4.1.6.2: Register cron job
// REQ-2.3.3: The system SHALL send automated notifications to all active users at 20:00 WIB (UTC+7)
cron.schedule('0 20 * * *', () => {
  console.log(`[${new Date().toISOString()}] ⏰ Cron job triggered: 20:00 WIB notification`);
  sendScheduledNotifications('20:00 WIB');
}, {
  timezone: 'Asia/Jakarta'
});

console.log(`[${new Date().toISOString()}] ✅ Scheduled notification for 20:00 WIB (Asia/Jakarta timezone)`);
console.log(`[${new Date().toISOString()}] 🔔 All scheduled notifications configured successfully`);

// Export for testing purposes
export { 
  bot, 
  initializeBot, 
  apiClient, 
  AutomatonAPIClient, 
  formatStatusMessage, 
  formatRelativeTime, 
  formatHelpMessage, 
  sendScheduledNotifications, 
  getActiveUsers,
  detectDisconnection,
  startPollingHealthMonitor,
  stopPollingHealthMonitor,
  handleReconnection,
  isValidTelegramUserId,
  validateMessageUser,
  sanitizeUserInput,
  sanitizeUsername,
  sanitizeMessage,
  suggestCommandCorrection,
  generateMalformedCommandMessage
};

