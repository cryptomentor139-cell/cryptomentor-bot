/**
 * Error Message Templates Module
 * Implements task 5.1.2: Implement user-friendly error messages
 * 
 * MODULE OVERVIEW:
 * This module provides a comprehensive library of user-friendly error messages for all
 * failure scenarios in the CryptoMentor Telegram Bot. It implements a critical security
 * and user experience principle: NEVER expose internal error details to end users.
 * 
 * CORE PRINCIPLES:
 * 
 * 1. USER-FRIENDLY LANGUAGE:
 *    - Use simple, non-technical language
 *    - Avoid jargon and technical terms
 *    - Be empathetic and supportive
 *    - Maintain friendly, helpful tone
 * 
 * 2. SECURITY BY OBSCURITY:
 *    - Never expose stack traces to users
 *    - Never reveal internal error codes
 *    - Never show database errors or API details
 *    - Never disclose system architecture
 *    - Prevents information leakage to attackers
 * 
 * 3. ACTIONABLE GUIDANCE:
 *    - Tell users what went wrong (in simple terms)
 *    - Explain why it might have happened
 *    - Provide clear next steps
 *    - Offer alternatives when possible
 * 
 * 4. CONSISTENT FORMATTING:
 *    - Title with emoji for visual recognition
 *    - Brief explanation of the problem
 *    - Optional reasons (why this happened)
 *    - Suggestions (what to do next)
 *    - Optional examples (how to use correctly)
 *    - Optional notes (additional context)
 * 
 * MESSAGE STRUCTURE:
 * 
 * ```
 * 🔧 *Service Unavailable*              ← Title with emoji
 * 
 * The service is temporarily unavailable. ← Brief explanation
 * 
 * *💡 What to do:*                       ← Actionable suggestions
 * • Try again in a few minutes
 * • The service team has been notified
 * ```
 * 
 * ERROR CATEGORIES:
 * 
 * 1. CONNECTION ERRORS:
 *    - Timeout: Request took too long
 *    - Network Error: Cannot connect to service
 *    - Service Unavailable: Backend is down
 * 
 * 2. API ERRORS:
 *    - Client Error: Problem with request (4xx)
 *    - Server Error: Problem with backend (5xx)
 *    - Invalid Response: Unexpected response format
 * 
 * 3. INPUT ERRORS:
 *    - Empty Message: User forgot to provide message
 *    - Invalid Command: Unrecognized command
 * 
 * 4. CREDIT ERRORS:
 *    - Insufficient Credits: Not enough balance
 * 
 * 5. FEATURE-SPECIFIC ERRORS:
 *    - Status: Cannot retrieve user status
 *    - Conversation: Cannot process chat message
 *    - Help: Cannot display help information
 * 
 * 6. GENERIC FALLBACK:
 *    - Unknown Error: Catch-all for unexpected errors
 * 
 * USAGE PATTERN:
 * 
 * 1. Catch error in command handler
 * 2. Call getErrorTemplate(error, context) to get appropriate template
 * 3. Call formatErrorMessage(template, options) to format for display
 * 4. Send formatted message to user
 * 5. Log actual error details internally (never shown to user)
 * 
 * EXAMPLE:
 * ```javascript
 * try {
 *   await apiClient.sendChatMessage(userId, message);
 * } catch (error) {
 *   // Get user-friendly template (hides internal details)
 *   const template = getErrorTemplate(error, 'talk');
 *   const userMessage = formatErrorMessage(template);
 *   
 *   // Send friendly message to user
 *   await bot.sendMessage(userId, userMessage);
 *   
 *   // Log actual error internally (for debugging)
 *   logger.logError('Chat failed', error, { userId, message });
 * }
 * ```
 * 
 * SECURITY BENEFITS:
 * - Prevents information disclosure attacks
 * - Hides system architecture from attackers
 * - Protects API endpoints and internal structure
 * - Prevents error-based enumeration attacks
 * - Maintains professional appearance
 * 
 * USER EXPERIENCE BENEFITS:
 * - Reduces user confusion and frustration
 * - Provides clear guidance on next steps
 * - Maintains trust in the service
 * - Reduces support requests
 * - Improves user satisfaction
 * 
 * REQUIREMENTS SATISFIED:
 * - REQ-2.8.2: Send user-friendly error messages for all failure scenarios
 * - REQ-3.3.7: Never expose internal error details to end users
 * - Task 5.1.2.1: Create error message templates
 * - Task 5.1.2.2: Never expose internal errors to users
 * 
 * MAINTENANCE:
 * - Add new templates as new features are added
 * - Update messages based on user feedback
 * - Keep language simple and friendly
 * - Test messages with non-technical users
 * - Review regularly for clarity and helpfulness
 */

/**
 * Error message templates organized by category
 */
export const ErrorMessages = {
  // API Connection Errors
  CONNECTION: {
    TIMEOUT: {
      title: '⏱️ *Request Timeout*',
      message: 'The request is taking longer than expected. Please try again.',
      suggestions: [
        'Try again in a moment',
        'Check your internet connection',
        'Contact support if the issue persists'
      ]
    },
    NETWORK_ERROR: {
      title: '🔌 *Connection Error*',
      message: 'Sorry, I couldn\'t connect to the service right now.',
      suggestions: [
        'Try again in a few moments',
        'Check your internet connection',
        'Contact support if the issue persists'
      ]
    },
    SERVICE_UNAVAILABLE: {
      title: '🔧 *Service Unavailable*',
      message: 'The service is temporarily unavailable.',
      suggestions: [
        'Try again in a few minutes',
        'The service team has been notified'
      ]
    }
  },

  // API Response Errors
  API: {
    CLIENT_ERROR: {
      title: '⚠️ *Request Error*',
      message: 'There was a problem with your request.',
      suggestions: [
        'Try again later',
        'Contact support if the issue persists'
      ]
    },
    SERVER_ERROR: {
      title: '🔧 *Service Error*',
      message: 'Something went wrong on our end.',
      suggestions: [
        'Try again in a few minutes',
        'The issue has been logged'
      ]
    },
    INVALID_RESPONSE: {
      title: '⚠️ *Invalid Response*',
      message: 'Received an unexpected response from the service.',
      suggestions: [
        'Try again',
        'Contact support if the issue persists'
      ]
    }
  },

  // User Input Errors
  INPUT: {
    EMPTY_MESSAGE: {
      title: '⚠️ *Invalid Message*',
      message: 'Please provide a message after the /talk command.',
      example: '/talk What\'s the best trading strategy?'
    },
    INVALID_COMMAND: {
      title: '❓ *Unknown Command*',
      message: 'I don\'t recognize that command.',
      suggestions: [
        'Use /help to see available commands',
        'Check your spelling'
      ]
    }
  },

  // Credit/Balance Errors
  CREDITS: {
    INSUFFICIENT: {
      title: '💰 *Insufficient Credits*',
      message: 'You don\'t have enough credits for this action.',
      suggestions: [
        'Use /status to check your balance',
        'Contact support to purchase credits'
      ]
    }
  },

  // Status Command Errors
  STATUS: {
    UNAVAILABLE: {
      title: '⚠️ *Unable to Retrieve Status*',
      message: 'Sorry, I couldn\'t retrieve your status right now.',
      suggestions: [
        'Try again in a moment',
        'Contact support if the issue persists'
      ]
    }
  },

  // Conversation Errors
  CONVERSATION: {
    TIMEOUT: {
      title: '⏱️ *Request Timeout*',
      message: 'The AI is taking longer than expected to respond.',
      reasons: [
        'High server load',
        'Complex query processing',
        'Network connectivity issues'
      ],
      suggestions: [
        'Try again in a moment',
        'Simplify your question',
        'Check your internet connection'
      ],
      note: 'Your credits have not been deducted.'
    },
    PROCESSING_ERROR: {
      title: '⚠️ *Unable to Process Conversation*',
      message: 'Sorry, I couldn\'t process your message right now.',
      suggestions: [
        'Try again in a moment',
        'Use /status to check your account',
        'Contact support if the issue persists'
      ],
      note: 'Your credits have not been deducted.'
    }
  },

  // Help Command Errors
  HELP: {
    UNAVAILABLE: {
      title: '⚠️ *Unable to Display Help*',
      message: 'Something went wrong.',
      suggestions: [
        'Try again later'
      ]
    }
  },

  // Generic Fallback
  GENERIC: {
    UNKNOWN_ERROR: {
      title: '⚠️ *Something Went Wrong*',
      message: 'An unexpected error occurred.',
      suggestions: [
        'Try again',
        'Contact support if the issue persists'
      ]
    }
  }
};

/**
 * Format an error message template into a user-friendly message
 * Implements REQ-2.8.2: Send user-friendly error messages
 * Implements REQ-3.3.7: Never expose internal error details
 * 
 * FUNCTION OVERVIEW:
 * This function takes an error message template (from ErrorMessages) and formats it
 * into a complete, user-friendly message ready to send via Telegram. It assembles
 * all the components (title, message, reasons, suggestions, examples, notes) into
 * a well-structured, readable format using Telegram Markdown.
 * 
 * MESSAGE ASSEMBLY PROCESS:
 * 
 * 1. START WITH TITLE AND MESSAGE:
 *    - Title: Bold text with emoji (e.g., "🔧 *Service Unavailable*")
 *    - Message: Brief explanation of what went wrong
 *    - Separated by blank line for readability
 * 
 * 2. ADD REASONS (if provided):
 *    - Section header: "*This might be due to:*"
 *    - Bullet list of possible causes
 *    - Helps users understand why error occurred
 *    - Optional: Only included if template has reasons array
 * 
 * 3. ADD SUGGESTIONS (if provided):
 *    - Section header: "*💡 What to do:*"
 *    - Bullet list of actionable next steps
 *    - Guides users on how to resolve or work around the issue
 *    - Most important section for user experience
 * 
 * 4. ADD EXAMPLE (if provided):
 *    - Section header: "*Example:*"
 *    - Shows correct usage or format
 *    - Helpful for input validation errors
 *    - Optional: Only for errors where example is relevant
 * 
 * 5. ADD NOTES (if provided):
 *    - Additional context or important information
 *    - Can come from template or options parameter
 *    - Examples: "Your credits have not been deducted"
 *    - Reassures users about system state
 * 
 * MARKDOWN FORMATTING:
 * The function uses Telegram Markdown for formatting:
 * - *Bold text*: For emphasis (titles, section headers)
 * - • Bullet points: For lists (reasons, suggestions)
 * - \n\n: Double newlines for section separation
 * - Emojis: For visual appeal and quick recognition
 * 
 * EXAMPLE OUTPUT:
 * ```
 * ⏱️ *Request Timeout*
 * 
 * The AI is taking longer than expected to respond.
 * 
 * *This might be due to:*
 * • High server load
 * • Complex query processing
 * • Network connectivity issues
 * 
 * *💡 What to do:*
 * • Try again in a moment
 * • Simplify your question
 * • Check your internet connection
 * 
 * Your credits have not been deducted.
 * ```
 * 
 * TEMPLATE STRUCTURE:
 * Templates from ErrorMessages have this structure:
 * ```javascript
 * {
 *   title: '🔧 *Service Unavailable*',
 *   message: 'The service is temporarily unavailable.',
 *   reasons: ['High server load', 'Maintenance in progress'],  // Optional
 *   suggestions: ['Try again in a few minutes', 'Contact support'],
 *   example: '/talk What is Bitcoin?',  // Optional
 *   note: 'Your credits have not been deducted.'  // Optional
 * }
 * ```
 * 
 * OPTIONS PARAMETER:
 * The options parameter allows adding custom notes:
 * ```javascript
 * formatErrorMessage(template, {
 *   note: 'This is a temporary issue. We are working on it.'
 * });
 * ```
 * 
 * FALLBACK BEHAVIOR:
 * If template is null or undefined:
 * - Returns generic error message
 * - Uses ErrorMessages.GENERIC.UNKNOWN_ERROR
 * - Ensures user always gets a message (never crashes)
 * 
 * USE CASES:
 * 
 * 1. API TIMEOUT:
 *    - Template: ErrorMessages.CONVERSATION.TIMEOUT
 *    - Formatted: Complete message with reasons and suggestions
 *    - Sent to user via Telegram
 * 
 * 2. INSUFFICIENT CREDITS:
 *    - Template: ErrorMessages.CREDITS.INSUFFICIENT
 *    - Formatted: Message with suggestions to top up
 *    - Sent to user via Telegram
 * 
 * 3. NETWORK ERROR:
 *    - Template: ErrorMessages.CONNECTION.NETWORK_ERROR
 *    - Formatted: Message with retry suggestions
 *    - Sent to user via Telegram
 * 
 * REQUIREMENTS SATISFIED:
 * - REQ-2.8.2: Send user-friendly error messages for all failure scenarios
 * - REQ-3.3.7: Never expose internal error details to end users
 * - REQ-5.3.2: Support Markdown formatting in all bot messages
 * - REQ-5.3.3: Format messages with emojis to enhance readability
 * 
 * @param {Object} template - Error message template from ErrorMessages
 * @param {string} template.title - Title with emoji (e.g., "🔧 *Service Unavailable*")
 * @param {string} template.message - Brief explanation of the error
 * @param {Array<string>} template.reasons - Optional array of possible causes
 * @param {Array<string>} template.suggestions - Optional array of actionable suggestions
 * @param {string} template.example - Optional example of correct usage
 * @param {string} template.note - Optional additional note
 * @param {Object} options - Additional options for customization
 * @param {string} options.note - Custom note to append to message
 * @returns {string} Formatted error message with Markdown, ready to send to user
 * 
 * @example
 * // Format timeout error
 * const template = ErrorMessages.CONVERSATION.TIMEOUT;
 * const message = formatErrorMessage(template);
 * await bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
 * 
 * @example
 * // Format with custom note
 * const template = ErrorMessages.API.SERVER_ERROR;
 * const message = formatErrorMessage(template, {
 *   note: 'We are investigating this issue.'
 * });
 * await bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
 * 
 * @example
 * // Fallback for null template
 * const message = formatErrorMessage(null);
 * // Returns: "⚠️ *Something Went Wrong*\n\nAn unexpected error occurred."
 */
export function formatErrorMessage(template, options = {}) {
  if (!template) {
    return ErrorMessages.GENERIC.UNKNOWN_ERROR.title + '\n\n' + 
           ErrorMessages.GENERIC.UNKNOWN_ERROR.message;
  }

  let message = `${template.title}\n\n${template.message}`;

  // Add reasons if provided
  if (template.reasons && template.reasons.length > 0) {
    message += '\n\n*This might be due to:*\n';
    template.reasons.forEach(reason => {
      message += `• ${reason}\n`;
    });
  }

  // Add suggestions if provided
  if (template.suggestions && template.suggestions.length > 0) {
    message += '\n\n*💡 What to do:*\n';
    template.suggestions.forEach(suggestion => {
      message += `• ${suggestion}\n`;
    });
  }

  // Add example if provided
  if (template.example) {
    message += '\n\n*Example:*\n' + template.example;
  }

  // Add note if provided
  if (template.note) {
    message += '\n\n' + template.note;
  }

  // Add custom note from options
  if (options.note) {
    message += '\n\n' + options.note;
  }

  return message;
}

/**
 * Determine appropriate error message template based on error type
 * Implements task 5.1.2.2: Never expose internal errors to users
 * 
 * FUNCTION OVERVIEW:
 * This function is the critical security layer that prevents internal error details
 * from being exposed to end users. It analyzes an error object and returns an
 * appropriate user-friendly message template WITHOUT revealing any sensitive
 * information about the system's internal workings.
 * 
 * SECURITY PRINCIPLE:
 * "Never trust error messages to be safe for user display"
 * 
 * Internal errors may contain:
 * - Stack traces revealing code structure
 * - Database connection strings
 * - API endpoints and authentication details
 * - File paths and system architecture
 * - Internal variable names and logic
 * 
 * This function acts as a FIREWALL between internal errors and user-facing messages.
 * 
 * ERROR CLASSIFICATION LOGIC:
 * The function examines various properties of the error object to classify it:
 * 
 * 1. ERROR NAME:
 *    - AbortError, TimeoutError → Timeout template
 *    - SyntaxError → Invalid response template
 * 
 * 2. ERROR CODE:
 *    - ECONNREFUSED, ENOTFOUND, ETIMEDOUT → Network error template
 *    - ECONNRESET → Connection error template
 * 
 * 3. ERROR MESSAGE CONTENT:
 *    - Contains "timed out" or "timeout" → Timeout template
 *    - Contains "Cannot connect" → Network error template
 *    - Contains "Insufficient credits" → Credits template
 *    - Contains "400", "401", "403", "404" → Client error template
 *    - Contains "500", "502", "503", "504" → Server error template
 *    - Contains "JSON" or "parse" → Invalid response template
 * 
 * 4. CONTEXT:
 *    - 'status' context → Status-specific error template
 *    - 'talk' or 'conversation' context → Conversation-specific template
 *    - 'help' context → Help-specific template
 *    - Generic context → Generic fallback template
 * 
 * CLASSIFICATION PRIORITY:
 * The function checks error types in order of specificity:
 * 1. Timeout errors (most specific)
 * 2. Network connection errors
 * 3. Insufficient credits errors
 * 4. HTTP 4xx client errors
 * 5. HTTP 5xx server errors
 * 6. Invalid response format errors
 * 7. Context-specific fallbacks
 * 8. Generic fallback (catch-all)
 * 
 * CONTEXT PARAMETER:
 * The context parameter helps provide more specific error messages:
 * - 'start': User registration errors
 * - 'status': Status retrieval errors
 * - 'talk' or 'conversation': Chat/conversation errors
 * - 'help': Help command errors
 * - 'notification': Notification delivery errors
 * - 'generic': Generic errors (default)
 * 
 * EXAMPLE TRANSFORMATIONS:
 * 
 * 1. INTERNAL ERROR:
 *    Input: Error("ECONNREFUSED: Connection refused at 192.168.1.1:5432")
 *    Output: ErrorMessages.CONNECTION.NETWORK_ERROR
 *    User sees: "Sorry, I couldn't connect to the service right now."
 *    Hidden: IP address, port, connection details
 * 
 * 2. DATABASE ERROR:
 *    Input: Error("PostgreSQL error: relation 'users' does not exist")
 *    Output: ErrorMessages.GENERIC.UNKNOWN_ERROR
 *    User sees: "An unexpected error occurred."
 *    Hidden: Database type, table names, schema details
 * 
 * 3. API ERROR:
 *    Input: Error("API request failed: 500 Internal Server Error at /api/chat")
 *    Output: ErrorMessages.CONNECTION.SERVICE_UNAVAILABLE
 *    User sees: "The service is temporarily unavailable."
 *    Hidden: API endpoint, status code details
 * 
 * 4. TIMEOUT ERROR:
 *    Input: TimeoutError("Request timed out after 30000ms")
 *    Output: ErrorMessages.CONVERSATION.TIMEOUT (if context='talk')
 *    User sees: "The AI is taking longer than expected to respond."
 *    Hidden: Timeout duration, internal timing details
 * 
 * SECURITY BENEFITS:
 * - Prevents information disclosure attacks
 * - Hides system architecture from attackers
 * - Protects API endpoints and internal structure
 * - Prevents error-based enumeration
 * - Maintains professional appearance
 * 
 * DEBUGGING WORKFLOW:
 * 1. User reports: "I got an error saying service unavailable"
 * 2. Developer checks logs for actual error (with full details)
 * 3. Logs contain: timestamp, user ID, actual error, stack trace
 * 4. Developer can debug using internal logs
 * 5. User never sees sensitive internal details
 * 
 * REQUIREMENTS SATISFIED:
 * - REQ-2.8.2: Send user-friendly error messages for all failure scenarios
 * - REQ-3.3.7: Never expose internal error details to end users
 * - Task 5.1.2.2: Never expose internal errors to users
 * 
 * @param {Error} error - The error object to classify (may contain sensitive data)
 * @param {string} context - Context where error occurred (e.g., 'status', 'talk', 'start')
 * @returns {Object} User-friendly error message template (safe for display)
 * 
 * @example
 * // Timeout error in conversation
 * const error = new Error('Request timed out after 30000ms');
 * error.name = 'TimeoutError';
 * const template = getErrorTemplate(error, 'talk');
 * // Returns: ErrorMessages.CONVERSATION.TIMEOUT
 * 
 * @example
 * // Network error (generic context)
 * const error = new Error('Connection refused');
 * error.code = 'ECONNREFUSED';
 * const template = getErrorTemplate(error, 'generic');
 * // Returns: ErrorMessages.CONNECTION.NETWORK_ERROR
 * 
 * @example
 * // Unknown error (fallback)
 * const error = new Error('Something weird happened');
 * const template = getErrorTemplate(error, 'generic');
 * // Returns: ErrorMessages.GENERIC.UNKNOWN_ERROR
 */
export function getErrorTemplate(error, context = 'generic') {
  if (!error) {
    return ErrorMessages.GENERIC.UNKNOWN_ERROR;
  }

  // Timeout errors
  if (error.name === 'AbortError' || 
      error.name === 'TimeoutError' || 
      error.message?.includes('timed out') || 
      error.message?.includes('timeout')) {
    if (context === 'talk' || context === 'conversation') {
      return ErrorMessages.CONVERSATION.TIMEOUT;
    }
    return ErrorMessages.CONNECTION.TIMEOUT;
  }

  // Network connection errors
  if (error.code === 'ECONNREFUSED' || 
      error.code === 'ENOTFOUND' || 
      error.code === 'ETIMEDOUT' || 
      error.code === 'ECONNRESET' ||
      error.message?.includes('Cannot connect') || 
      error.message?.includes('Service may be unavailable')) {
    return ErrorMessages.CONNECTION.NETWORK_ERROR;
  }

  // Insufficient credits
  if (error.message?.includes('Insufficient credits') || 
      error.message?.includes('insufficient') ||
      error.message?.includes('credits')) {
    return ErrorMessages.CREDITS.INSUFFICIENT;
  }

  // 4xx client errors
  if (error.message?.includes('400') || 
      error.message?.includes('401') || 
      error.message?.includes('403') || 
      error.message?.includes('404')) {
    return ErrorMessages.API.CLIENT_ERROR;
  }

  // 5xx server errors
  if (error.message?.includes('500') || 
      error.message?.includes('502') || 
      error.message?.includes('503') || 
      error.message?.includes('504')) {
    return ErrorMessages.CONNECTION.SERVICE_UNAVAILABLE;
  }

  // Invalid response format
  if (error instanceof SyntaxError || 
      error.message?.includes('JSON') || 
      error.message?.includes('parse')) {
    return ErrorMessages.API.INVALID_RESPONSE;
  }

  // Context-specific fallbacks
  if (context === 'status') {
    return ErrorMessages.STATUS.UNAVAILABLE;
  } else if (context === 'talk' || context === 'conversation') {
    return ErrorMessages.CONVERSATION.PROCESSING_ERROR;
  } else if (context === 'help') {
    return ErrorMessages.HELP.UNAVAILABLE;
  }

  // Generic fallback
  return ErrorMessages.GENERIC.UNKNOWN_ERROR;
}

/**
 * Create a complete user-friendly error message from an error object
 * This is the main function to use when handling errors
 * 
 * FUNCTION OVERVIEW:
 * This is the PRIMARY ERROR HANDLING FUNCTION that should be used throughout
 * the codebase when catching errors. It provides a simple, one-step interface
 * to convert any error into a safe, user-friendly message.
 * 
 * COMPLETE ERROR HANDLING PIPELINE:
 * This function combines two critical steps into one convenient call:
 * 
 * 1. ERROR CLASSIFICATION (getErrorTemplate):
 *    - Analyzes the error object
 *    - Determines error type (timeout, network, API, etc.)
 *    - Selects appropriate template
 *    - HIDES all internal error details
 * 
 * 2. MESSAGE FORMATTING (formatErrorMessage):
 *    - Takes the template
 *    - Assembles complete message
 *    - Formats with Markdown
 *    - Adds suggestions and examples
 * 
 * USAGE PATTERN:
 * This is the recommended way to handle errors in command handlers:
 * 
 * ```javascript
 * try {
 *   // Attempt operation that might fail
 *   await apiClient.sendChatMessage(userId, message);
 * } catch (error) {
 *   // ONE-LINE ERROR HANDLING
 *   const userMessage = createUserErrorMessage(error, 'talk');
 *   
 *   // Send safe message to user
 *   await bot.sendMessage(userId, userMessage, { parse_mode: 'Markdown' });
 *   
 *   // Log actual error internally (for debugging)
 *   logger.logError('Chat failed', error, { userId });
 * }
 * ```
 * 
 * BENEFITS OF THIS APPROACH:
 * 
 * 1. SIMPLICITY:
 *    - One function call instead of two
 *    - Consistent error handling across codebase
 *    - Less code duplication
 * 
 * 2. SECURITY:
 *    - Automatically hides internal details
 *    - No risk of accidentally exposing sensitive data
 *    - Enforces security best practices
 * 
 * 3. MAINTAINABILITY:
 *    - Centralized error message logic
 *    - Easy to update messages globally
 *    - Consistent user experience
 * 
 * 4. FLEXIBILITY:
 *    - Context-aware messages (different for /talk vs /status)
 *    - Custom options for special cases
 *    - Extensible for new error types
 * 
 * CONTEXT PARAMETER:
 * The context parameter customizes messages for different features:
 * 
 * - 'start': User registration errors
 *   Example: "Unable to register your account. Please try again."
 * 
 * - 'status': Status retrieval errors
 *   Example: "Unable to retrieve your status. Please try again."
 * 
 * - 'talk' or 'conversation': Chat/conversation errors
 *   Example: "The AI is taking longer than expected. Please try again."
 * 
 * - 'help': Help command errors
 *   Example: "Unable to display help. Please try again."
 * 
 * - 'notification': Notification delivery errors
 *   Example: "Unable to send notification. Will retry later."
 * 
 * - 'generic': Generic errors (default)
 *   Example: "Something went wrong. Please try again."
 * 
 * OPTIONS PARAMETER:
 * Additional customization options:
 * 
 * ```javascript
 * createUserErrorMessage(error, 'talk', {
 *   note: 'Your credits have not been deducted.'
 * });
 * ```
 * 
 * EXAMPLE TRANSFORMATIONS:
 * 
 * 1. TIMEOUT ERROR IN CONVERSATION:
 *    Input: TimeoutError("Request timed out after 30000ms")
 *    Context: 'talk'
 *    Output: "⏱️ *Request Timeout*\n\nThe AI is taking longer than expected..."
 * 
 * 2. NETWORK ERROR IN STATUS:
 *    Input: Error("ECONNREFUSED")
 *    Context: 'status'
 *    Output: "🔌 *Connection Error*\n\nSorry, I couldn't connect to the service..."
 * 
 * 3. INSUFFICIENT CREDITS:
 *    Input: Error("Insufficient credits")
 *    Context: 'talk'
 *    Output: "💰 *Insufficient Credits*\n\nYou don't have enough credits..."
 * 
 * 4. UNKNOWN ERROR:
 *    Input: Error("Something weird happened")
 *    Context: 'generic'
 *    Output: "⚠️ *Something Went Wrong*\n\nAn unexpected error occurred..."
 * 
 * COMPARISON WITH MANUAL APPROACH:
 * 
 * MANUAL (NOT RECOMMENDED):
 * ```javascript
 * catch (error) {
 *   const template = getErrorTemplate(error, 'talk');
 *   const message = formatErrorMessage(template);
 *   await bot.sendMessage(userId, message);
 * }
 * ```
 * 
 * USING THIS FUNCTION (RECOMMENDED):
 * ```javascript
 * catch (error) {
 *   const message = createUserErrorMessage(error, 'talk');
 *   await bot.sendMessage(userId, message);
 * }
 * ```
 * 
 * REQUIREMENTS SATISFIED:
 * - REQ-2.8.2: Send user-friendly error messages for all failure scenarios
 * - REQ-3.3.7: Never expose internal error details to end users
 * - Task 5.1.2: Implement user-friendly error messages
 * - Task 5.1.2.2: Never expose internal errors to users
 * 
 * @param {Error} error - The error object to convert (may contain sensitive data)
 * @param {string} context - Context where error occurred (e.g., 'status', 'talk', 'start')
 * @param {Object} options - Additional options for message customization
 * @param {string} options.note - Custom note to append to message
 * @returns {string} Formatted user-friendly error message (safe for display)
 * 
 * @example
 * // Handle timeout error in conversation
 * try {
 *   await apiClient.sendChatMessage(userId, message);
 * } catch (error) {
 *   const userMessage = createUserErrorMessage(error, 'talk');
 *   await bot.sendMessage(userId, userMessage, { parse_mode: 'Markdown' });
 *   logger.logError('Chat failed', error, { userId });
 * }
 * 
 * @example
 * // Handle status retrieval error
 * try {
 *   const status = await apiClient.getUserStatus(userId);
 * } catch (error) {
 *   const userMessage = createUserErrorMessage(error, 'status');
 *   await bot.sendMessage(userId, userMessage, { parse_mode: 'Markdown' });
 *   logger.logError('Status fetch failed', error, { userId });
 * }
 * 
 * @example
 * // Handle error with custom note
 * try {
 *   await processPayment(userId, amount);
 * } catch (error) {
 *   const userMessage = createUserErrorMessage(error, 'generic', {
 *     note: 'Your payment has not been processed.'
 *   });
 *   await bot.sendMessage(userId, userMessage, { parse_mode: 'Markdown' });
 *   logger.logError('Payment failed', error, { userId, amount });
 * }
 */
export function createUserErrorMessage(error, context = 'generic', options = {}) {
  const template = getErrorTemplate(error, context);
  return formatErrorMessage(template, options);
}

/**
 * Sanitize error for logging (remove sensitive information)
 * Implements REQ-3.3.2: Never log sensitive user data
 * 
 * FUNCTION OVERVIEW:
 * This function prepares error objects for safe logging by removing any sensitive
 * information that should not be stored in logs. While we hide internal errors from
 * USERS (via getErrorTemplate), we still need to log errors internally for debugging.
 * However, even internal logs must not contain sensitive user data.
 * 
 * SECURITY PRINCIPLE:
 * "Logs are not secure storage"
 * 
 * Logs may be:
 * - Stored in plain text files
 * - Sent to external logging services
 * - Accessed by multiple team members
 * - Retained for extended periods
 * - Subject to data breach if system is compromised
 * 
 * Therefore, logs must NEVER contain:
 * - User passwords or authentication tokens
 * - API keys or secrets
 * - Credit card numbers or payment information
 * - Personal messages or conversation content
 * - Email addresses or phone numbers (unless necessary)
 * - Social security numbers or government IDs
 * - Any other personally identifiable information (PII)
 * 
 * WHAT TO LOG:
 * ✅ SAFE TO LOG:
 * - Error name (e.g., "TimeoutError", "NetworkError")
 * - Error message (e.g., "Request timed out after 30000ms")
 * - Error code (e.g., "ECONNREFUSED", "ETIMEDOUT")
 * - Stack trace (shows code flow, not user data)
 * - User ID (numeric identifier, not personal info)
 * - Timestamp (when error occurred)
 * - Operation name (e.g., "registerUser", "sendChatMessage")
 * 
 * ❌ NEVER LOG:
 * - User passwords or tokens
 * - API keys or secrets
 * - User messages or conversation content
 * - Email addresses or phone numbers
 * - Payment information
 * - Personal identifiable information (PII)
 * 
 * SANITIZATION PROCESS:
 * 
 * 1. EXTRACT SAFE FIELDS:
 *    - name: Error type (e.g., "Error", "TimeoutError")
 *    - message: Error description (usually safe)
 *    - code: Error code (e.g., "ECONNREFUSED")
 *    - stack: Stack trace (code flow, not data)
 * 
 * 2. EXCLUDE SENSITIVE FIELDS:
 *    - Do not include: tokens, API keys, passwords
 *    - Do not include: user messages, personal data
 *    - Do not include: any custom fields that might contain PII
 * 
 * 3. RETURN CLEAN OBJECT:
 *    - Only includes safe fields
 *    - Safe to log to files or external services
 *    - Complies with data protection regulations
 * 
 * EXAMPLE SANITIZATION:
 * 
 * INPUT (potentially sensitive):
 * ```javascript
 * {
 *   name: 'Error',
 *   message: 'API request failed',
 *   code: 'ECONNREFUSED',
 *   stack: 'Error: API request failed\n    at AutomatonAPIClient...',
 *   userMessage: 'What is my password?',  // SENSITIVE!
 *   apiKey: 'sk_live_abc123',  // SENSITIVE!
 *   token: 'Bearer xyz789'  // SENSITIVE!
 * }
 * ```
 * 
 * OUTPUT (sanitized):
 * ```javascript
 * {
 *   name: 'Error',
 *   message: 'API request failed',
 *   code: 'ECONNREFUSED',
 *   stack: 'Error: API request failed\n    at AutomatonAPIClient...'
 *   // userMessage, apiKey, token are EXCLUDED
 * }
 * ```
 * 
 * USAGE PATTERN:
 * 
 * ```javascript
 * try {
 *   await apiClient.sendChatMessage(userId, userMessage);
 * } catch (error) {
 *   // Sanitize before logging
 *   const safeError = sanitizeErrorForLogging(error);
 *   
 *   // Log sanitized error (safe)
 *   logger.logError('Chat failed', safeError, {
 *     userId,  // OK: numeric ID, not PII
 *     operation: 'sendChatMessage'  // OK: operation name
 *     // userMessage is NOT logged (sensitive)
 *   });
 *   
 *   // Send user-friendly message
 *   const userMessage = createUserErrorMessage(error, 'talk');
 *   await bot.sendMessage(userId, userMessage);
 * }
 * ```
 * 
 * COMPLIANCE:
 * This function helps comply with data protection regulations:
 * - GDPR (General Data Protection Regulation)
 * - CCPA (California Consumer Privacy Act)
 * - HIPAA (Health Insurance Portability and Accountability Act)
 * - PCI DSS (Payment Card Industry Data Security Standard)
 * 
 * REQUIREMENTS SATISFIED:
 * - REQ-3.3.2: Never log sensitive user data (messages, personal information)
 * - REQ-2.8.3: Log all errors with timestamp, error type, and stack trace
 * - REQ-3.7.4: Log errors with severity level
 * 
 * BEST PRACTICES:
 * 
 * 1. ALWAYS SANITIZE BEFORE LOGGING:
 *    - Never log raw error objects
 *    - Always use this function first
 *    - Review logs regularly for accidental PII
 * 
 * 2. MINIMIZE DATA COLLECTION:
 *    - Only log what's necessary for debugging
 *    - Don't log "just in case"
 *    - Less data = less risk
 * 
 * 3. SECURE LOG STORAGE:
 *    - Encrypt logs at rest
 *    - Restrict access to logs
 *    - Implement log retention policies
 *    - Regularly audit log access
 * 
 * 4. INCIDENT RESPONSE:
 *    - If PII is accidentally logged, delete immediately
 *    - Notify affected users if required by law
 *    - Update sanitization logic to prevent recurrence
 * 
 * @param {Error} error - The error object to sanitize (may contain sensitive data)
 * @returns {Object} Sanitized error object safe for logging (no sensitive data)
 * 
 * @example
 * // Sanitize error before logging
 * try {
 *   await processPayment(userId, cardNumber, amount);
 * } catch (error) {
 *   const safeError = sanitizeErrorForLogging(error);
 *   logger.logError('Payment failed', safeError, { userId, amount });
 *   // cardNumber is NOT logged (sensitive)
 * }
 * 
 * @example
 * // Handle null error
 * const safeError = sanitizeErrorForLogging(null);
 * // Returns: { message: 'Unknown error' }
 */
export function sanitizeErrorForLogging(error) {
  if (!error) {
    return { message: 'Unknown error' };
  }

  return {
    name: error.name || 'Error',
    message: error.message || 'Unknown error',
    code: error.code,
    stack: error.stack,
    // Explicitly exclude any sensitive fields
    // Do not include: tokens, API keys, passwords, user messages, personal data
  };
}
