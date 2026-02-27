/**
 * Error Message Templates
 * Implements task 5.1.2.1: Create error message templates
 * 
 * This module provides user-friendly error messages for all failure scenarios.
 * All messages follow these principles:
 * - REQ-2.8.2: User-friendly and helpful
 * - REQ-3.3.7: Never expose internal error details
 * - Maintain friendly, supportive tone
 * - Guide users on what to do next
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
 * @param {Object} template - Error message template
 * @param {Object} options - Additional options (creditsDeducted, customMessage, etc.)
 * @returns {string} Formatted error message with Markdown
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
 * This function analyzes an error and returns the appropriate user-friendly
 * message template WITHOUT exposing any internal error details.
 * 
 * @param {Error} error - The error object
 * @param {string} context - Context where error occurred (e.g., 'status', 'talk', 'start')
 * @returns {Object} Error message template
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
 * @param {Error} error - The error object
 * @param {string} context - Context where error occurred
 * @param {Object} options - Additional options
 * @returns {string} Formatted user-friendly error message
 */
export function createUserErrorMessage(error, context = 'generic', options = {}) {
  const template = getErrorTemplate(error, context);
  return formatErrorMessage(template, options);
}

/**
 * Sanitize error for logging (remove sensitive information)
 * Implements REQ-3.3.2: Never log sensitive user data
 * 
 * @param {Error} error - The error object
 * @returns {Object} Sanitized error object safe for logging
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
