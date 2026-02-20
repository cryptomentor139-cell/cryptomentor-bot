# Implementation Plan: Railway Deployment untuk Automaton

## Overview

Implementation plan ini memecah Railway deployment feature menjadi discrete coding tasks. Setiap task builds on previous tasks dan ends dengan integration. Focus pada implementasi Railway configuration, database persistence, payment authorization system, dan Telegram bot interface.

## Tasks

- [x] 1. Setup Railway configuration files dan dependencies
  - Create railway.json dengan build dan deploy configuration
  - Create nixpacks.toml untuk native module compilation
  - Create .railwayignore untuk exclude unnecessary files
  - Add node-telegram-bot-api dependency ke package.json
  - Create .env.example dengan Railway environment variables template
  - _Requirements: 1.1, 1.3, 1.4, 1.5_

- [x] 2. Implement Railway environment configuration module
  - [x] 2.1 Create src/railway/environment.ts dengan RailwayConfig interface
    - Implement loadRailwayConfig() function untuk load environment variables
    - Support Railway-provided variables (PORT, RAILWAY_ENVIRONMENT, RAILWAY_VOLUME_MOUNT_PATH)
    - Support Automaton-specific variables (DB_PATH, LOG_LEVEL, CONWAY_API_KEY, dll)
    - Support optional Telegram variables (TELEGRAM_BOT_TOKEN, TELEGRAM_CREATOR_ID)
    - Support payment configuration (PAYMENT_AUTO_APPROVE_THRESHOLD, PAYMENT_RATE_LIMIT_PER_HOUR)
    - Implement safe defaults untuk optional variables
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x]* 2.2 Write property test untuk environment variable fallback
    - **Property 1: Environment Variable Fallback**
    - **Validates: Requirements 2.4**
  
  - [x]* 2.3 Write unit tests untuk environment configuration
    - Test loading dengan valid environment variables
    - Test default values untuk optional variables
    - Test Railway-specific variable handling
    - _Requirements: 2.1, 2.2, 2.3, 2.5_


- [x] 3. Implement structured logging system
  - [x] 3.1 Create src/railway/logger.ts dengan RailwayLogger class
    - Implement log level filtering (debug, info, warn, error)
    - Implement structured JSON output ke stdout
    - Implement lifecycle event logging methods (logStartup, logShutdown, dll)
    - Implement error logging dengan stack trace
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x]* 3.2 Write property test untuk structured logging format
    - **Property 7: Structured Logging Format**
    - **Validates: Requirements 7.2**
  
  - [x]* 3.3 Write property test untuk error logging completeness
    - **Property 8: Error Logging Completeness**
    - **Validates: Requirements 7.3**
  
  - [x]* 3.4 Write unit tests untuk logger
    - Test log level filtering
    - Test JSON output format
    - Test lifecycle event logging
    - _Requirements: 7.1, 7.4, 7.5_

- [x] 4. Implement health check HTTP server
  - [x] 4.1 Create src/railway/health-server.ts dengan createHealthServer function
    - Implement HTTP server dengan /health endpoint
    - Implement HealthStatus interface dengan agent, database, telegram status
    - Return 200 untuk healthy state, 503 untuk unhealthy (agent dead)
    - Include uptime, turn count, agent state dalam response
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x]* 4.2 Write property test untuk health check status accuracy
    - **Property 6: Health Check Status Accuracy**
    - **Validates: Requirements 6.2, 6.4**
  
  - [x]* 4.3 Write unit tests untuk health server
    - Test /health endpoint returns correct status codes
    - Test response contains required fields
    - Test unhealthy state handling
    - _Requirements: 6.1, 6.3_

- [x] 5. Checkpoint - Ensure basic Railway infrastructure tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 6. Extend database schema untuk payment requests
  - [x] 6.1 Update src/state/schema.ts dengan MIGRATION_V4
    - Add payment_requests table dengan all required columns
    - Add indexes untuk status dan requested_at
    - Add telegram_config table untuk store creator chat ID
    - Update SCHEMA_VERSION ke 4
    - _Requirements: 11.2, 11.9, 12.11_
  
  - [x] 6.2 Extend AutomatonDatabase interface dalam src/types.ts
    - Add PaymentRequest dan PaymentStatus types
    - Add database methods: insertPaymentRequest, updatePaymentRequest, getPaymentRequestById, dll
    - Add telegram config methods: getTelegramConfig, setTelegramConfig
    - _Requirements: 11.2, 11.3_
  
  - [x] 6.3 Implement payment request database methods dalam src/state/database.ts
    - Implement insertPaymentRequest dengan prepared statement
    - Implement updatePaymentRequest untuk status changes
    - Implement getPaymentRequestsByStatus untuk query by status
    - Implement getPaymentRequestsSince untuk rate limiting
    - _Requirements: 11.2, 11.9_
  
  - [x]* 6.4 Write property test untuk database initialization idempotency
    - **Property 3: Database Initialization Idempotency**
    - **Validates: Requirements 4.2, 4.3**
  
  - [x]* 6.5 Write property test untuk database path error handling
    - **Property 4: Database Path Error Handling**
    - **Validates: Requirements 4.5**
  
  - [x]* 6.6 Write unit tests untuk payment request database operations
    - Test insert, update, query operations
    - Test status transitions
    - Test rate limiting queries
    - _Requirements: 11.2, 11.9_

- [x] 7. Implement payment approval system
  - [x] 7.1 Create src/payment/approval.ts dengan PaymentApprovalSystem interface
    - Implement requestPayment untuk create payment requests
    - Implement auto-approve logic based on threshold
    - Implement approvePayment untuk manual approval
    - Implement rejectPayment dengan rejection reason logging
    - Implement executeApprovedPayments untuk execute transfers
    - Implement rate limiting check
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.7, 11.10_
  
  - [x]* 7.2 Write property test untuk payment request creation
    - **Property 9: Payment Request Creation**
    - **Validates: Requirements 11.1, 11.2, 11.7**
  
  - [x]* 7.3 Write property test untuk payment rejection handling
    - **Property 10: Payment Rejection Handling**
    - **Validates: Requirements 11.4**
  
  - [x]* 7.4 Write property test untuk payment approval execution
    - **Property 11: Payment Approval Execution**
    - **Validates: Requirements 11.5**
  
  - [x]* 7.5 Write property test untuk payment audit trail
    - **Property 13: Payment Audit Trail**
    - **Validates: Requirements 11.9**
  
  - [x]* 7.6 Write property test untuk payment rate limiting
    - **Property 14: Payment Rate Limiting**
    - **Validates: Requirements 11.10**
  
  - [x]* 7.7 Write property test untuk payment approval required in all states
    - **Property 15: Payment Approval Required in All States**
    - **Validates: Requirements 11.8**
  
  - [x]* 7.8 Write unit tests untuk payment approval system
    - Test payment request creation dengan various amounts
    - Test auto-approve threshold logic
    - Test approval dan rejection flows
    - Test execution success dan failure handling
    - Test rate limiting enforcement
    - _Requirements: 11.1, 11.3, 11.4, 11.5, 11.7, 11.10_

- [x] 8. Checkpoint - Ensure payment system tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 9. Implement Telegram bot interface
  - [x] 9.1 Create src/telegram/bot.ts dengan createTelegramBot function
    - Initialize TelegramBot dengan polling
    - Implement authentication middleware untuk verify creator ID
    - Implement /start command handler
    - Implement /status command handler dengan system synopsis
    - Implement /logs command handler dengan recent turns
    - Implement /approve command handler untuk approve payments
    - Implement /reject command handler untuk reject payments
    - Implement /fund command handler (placeholder)
    - Implement /children command handler untuk list child agents
    - Implement /help command handler
    - Implement callback query handler untuk inline buttons
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.10_
  
  - [x] 9.2 Implement notifyPaymentRequest helper function
    - Send formatted payment request message ke creator
    - Include inline keyboard dengan approve/reject buttons
    - _Requirements: 11.6, 12.8_
  
  - [x]* 9.3 Write property test untuk Telegram authentication
    - **Property 16: Telegram Authentication**
    - **Validates: Requirements 12.2**
  
  - [x]* 9.4 Write property test untuk Telegram optional feature
    - **Property 17: Telegram Optional Feature**
    - **Validates: Requirements 12.13**
  
  - [x]* 9.5 Write property test untuk payment notification
    - **Property 12: Payment Notification**
    - **Validates: Requirements 11.6, 12.8**
  
  - [x]* 9.6 Write property test untuk critical state alert
    - **Property 18: Critical State Alert**
    - **Validates: Requirements 12.9**
  
  - [x]* 9.7 Write unit tests untuk Telegram bot
    - Test command handlers dengan mock bot
    - Test authentication logic
    - Test inline button callbacks
    - Test notification formatting
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.10_

- [x] 10. Implement Railway entry point dan lifecycle management
  - [x] 10.1 Create src/railway/index.ts dengan runOnRailway function
    - Load Railway configuration
    - Override automaton config dengan Railway-specific settings
    - Initialize database dengan Railway volume path
    - Create Conway dan inference clients
    - Create payment approval system
    - Initialize Telegram bot (optional)
    - Start health check server
    - Setup graceful shutdown handlers (SIGTERM, SIGINT)
    - Hook payment request notifications ke Telegram
    - Start main agent loop dengan payment system integration
    - _Requirements: 5.1, 5.2, 5.4, 5.5, 6.5, 11.6, 12.1_
  
  - [x] 10.2 Modify src/index.ts untuk detect Railway environment
    - Add Railway environment detection (check RAILWAY_ENVIRONMENT)
    - Import dan call runOnRailway jika detected
    - _Requirements: 5.1_
  
  - [x]* 10.3 Write property test untuk graceful shutdown cleanup
    - **Property 5: Graceful Shutdown Cleanup**
    - **Validates: Requirements 5.4, 5.5**
  
  - [x]* 10.4 Write unit tests untuk Railway entry point
    - Test initialization sequence
    - Test graceful shutdown handling
    - Test Telegram bot optional initialization
    - _Requirements: 5.1, 5.4, 5.5_

- [x] 11. Integrate payment system dengan agent loop
  - [x] 11.1 Modify src/agent/loop.ts untuk support payment approval
    - Add optional paymentSystem parameter ke runAgentLoop
    - Replace direct conway.transferCredits calls dengan paymentSystem.requestPayment
    - Add logic untuk check dan execute approved payments
    - _Requirements: 11.1, 11.5_
  
  - [x]* 11.2 Write unit tests untuk agent loop payment integration
    - Test payment request creation during agent loop
    - Test approved payment execution
    - Test fallback ke direct transfer jika payment system not provided
    - _Requirements: 11.1, 11.5_

- [x] 12. Checkpoint - Ensure all integration tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 13. Implement Telegram conversational interface
  - [x] 13.1 Create src/telegram/conversation.ts dengan TelegramConversationHandler class
    - Implement handleMessage untuk process non-command messages
    - Implement generateResponse menggunakan inference client
    - Implement buildSystemPrompt dengan automaton context
    - Implement conversation history management (load/save dari database)
    - Implement message pagination untuk responses > 4000 characters
    - Implement splitMessage helper untuk smart text splitting
    - _Requirements: 13.1, 13.2, 13.3, 13.5, 13.7, 13.9, 13.10_
  
  - [x] 13.2 Create TaskProgressTracker class untuk long-running tasks
    - Implement startTask untuk send initial progress message
    - Implement updateProgress untuk edit message dengan progress updates
    - Implement completeTask dan failTask untuk final status
    - _Requirements: 13.6_
  
  - [x] 13.3 Update src/telegram/bot.ts untuk integrate conversation handler
    - Add conversation handler initialization
    - Add message event listener untuk non-command messages
    - Add /clear command untuk clear conversation history
    - Add /deposit command untuk USDC deposit instructions
    - Add /credits command untuk detailed financial status
    - Update /help command dengan conversational examples
    - _Requirements: 12.7, 12.8, 13.1, 13.4_
  
  - [x]* 13.4 Write property test untuk conversation history persistence
    - **Property 19: Conversation History Persistence**
    - **Validates: Requirements 13.9**
  
  - [x]* 13.5 Write property test untuk message pagination
    - **Property 20: Message Pagination**
    - **Validates: Requirements 13.7**
  
  - [x]* 13.6 Write property test untuk conversation context isolation
    - **Property 21: Conversation Context Isolation**
    - **Validates: Requirements 13.3**
  
  - [x]* 13.7 Write unit tests untuk conversation handler
    - Test handleMessage dengan various user inputs
    - Test conversation history management
    - Test message splitting logic
    - Test system prompt generation
    - _Requirements: 13.1, 13.2, 13.3, 13.7, 13.9_
  
  - [x]* 13.8 Write unit tests untuk new Telegram commands
    - Test /deposit command response
    - Test /credits command dengan financial data
    - Test /clear command clears history
    - _Requirements: 12.7, 12.8_

- [x] 14. Create deployment documentation
  - [x] 13.1 Create docs/railway-deployment.md dengan comprehensive guide
    - Document initial Railway setup (project creation, volume setup)
    - Document environment variables configuration dengan examples
    - Document Telegram bot setup steps (@BotFather, @userinfobot)
    - Document deployment process dan build steps
    - Document health check configuration
    - Document monitoring via Railway dashboard dan Telegram
    - Document troubleshooting common issues
    - Document rollback procedure
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 13.2 Update README.md dengan Railway deployment section
    - Add quick start guide untuk Railway deployment
    - Link ke detailed deployment documentation
    - _Requirements: 8.1_

- [ ] 14. Add TypeScript compilation verification
  - [ ]* 14.1 Write property test untuk TypeScript compilation completeness
    - **Property 2: TypeScript Compilation Completeness**
    - **Validates: Requirements 1.2**
  
  - [ ]* 14.2 Write unit tests untuk build verification
    - Test dist/ directory contains compiled files
    - Test all packages compiled successfully
    - Test native modules (better-sqlite3) compiled
    - _Requirements: 1.2, 1.4, 1.5_

- [x] 15. Final integration dan end-to-end testing
  - [x] 15.1 Test complete deployment flow locally
    - Set Railway environment variables locally
    - Test database initialization dengan volume path
    - Test health endpoint accessibility
    - Test Telegram bot commands
    - Test payment approval flow end-to-end
    - Test graceful shutdown
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.2, 4.3, 4.4, 5.1, 5.4, 5.5, 6.1, 6.2, 6.5, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.8_
  
  - [x]* 15.2 Write integration tests untuk critical paths
    - Test startup sequence (database → health server → telegram → agent loop)
    - Test payment request → notification → approval → execution flow
    - Test shutdown sequence (cleanup resources)
    - _Requirements: 5.1, 5.4, 5.5, 11.1, 11.5, 11.6_

- [x] 16. Final checkpoint - Ensure all tests pass dan ready untuk deployment
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional test tasks dan can be skipped for faster MVP
- Each task references specific requirements untuk traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties dengan minimum 100 iterations
- Unit tests validate specific examples, edge cases, dan error conditions
- Integration tests validate end-to-end flows
- Documentation tasks ensure deployment process is well-documented
- All code should be written dalam TypeScript
- Follow existing code style dan patterns dalam Automaton codebase

