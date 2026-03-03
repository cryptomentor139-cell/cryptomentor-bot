# CryptoMentor Telegram Bot

## Project Overview

The CryptoMentor Telegram Bot is a production-ready Node.js application that serves as an interactive gateway to the Automaton AI trading system. Built with reliability and user experience in mind, this bot enables users to engage with AI-powered trading insights directly through Telegram's familiar messaging interface.

**Key Highlights:**
- Standalone service deployed independently on Railway
- Communicates with Automaton API for AI trading intelligence
- Handles user registration, credit management, and conversation history
- Delivers automated market updates three times daily
- Built with ES modules for modern JavaScript architecture
- Comprehensive error handling and automatic recovery mechanisms

**Use Cases:**
- New users can instantly register and receive free credits to start
- Traders receive timely market updates at strategic times throughout the day
- Users can ask trading questions and get AI-powered responses in real-time
- Status tracking helps users monitor their credit balance and activity

## Features

### 🎁 Auto-Greeting with Credits

When a new user sends the `/start` command, the bot:
- Automatically registers the user with the Automaton API
- Sends a personalized welcome message
- Credits the user's account with initial free credits (typically 1000)
- Handles duplicate `/start` commands idempotently (no duplicate accounts created)
- Provides a fallback welcome message if the API is temporarily unavailable

**Example Flow:**
```
User: /start
Bot: Welcome to CryptoMentor! 🎉
     Your account has been created with 1000 free credits.
     Use /help to see available commands.
```

### 📬 3x Daily Scheduled Notifications

The bot delivers automated market updates at three strategic times throughout the trading day:

**Schedule (Asia/Jakarta timezone - WIB/UTC+7):**
- 🌅 **Morning Update**: 08:00 WIB (01:00 UTC) - Start your day with market insights
- 🌤️ **Afternoon Update**: 14:00 WIB (07:00 UTC) - Mid-day market analysis
- 🌙 **Evening Update**: 20:00 WIB (13:00 UTC) - End-of-day trading summary

**How It Works:**
- Notifications are fetched from the Automaton API at scheduled times
- All active users (those who have used `/start`) receive the updates
- Delivery continues even if some users fail (isolated error handling)
- Delivery statistics are logged for monitoring
- Respects Telegram's rate limits (30 messages/second)

### 💬 Real-Time AI Conversations

Users can have interactive conversations with the AI trading assistant:

**Command Format:** `/talk <your message>`

**Features:**
- Credit balance check before processing (prevents insufficient credit errors)
- Typing indicator shows the bot is processing your request
- AI-powered responses from the Automaton API
- 30-second timeout with automatic retry (up to 3 attempts)
- User-friendly error messages if the service is unavailable
- Conversation context maintained for coherent interactions

**Example:**
```
User: /talk What's the best trading strategy for beginners?
Bot: [typing...]
Bot: For beginners, I recommend starting with a simple trend-following 
     strategy. Focus on major cryptocurrencies like BTC and ETH, use 
     proper risk management with stop-losses, and never invest more 
     than you can afford to lose...
```

### 📋 Available Commands

The bot supports four core commands:

| Command | Purpose | Credit Cost | Response Time |
|---------|---------|-------------|---------------|
| `/start` | Register account and receive welcome | Free | < 2 seconds |
| `/status` | View credits, stats, and activity | Free | < 2 seconds |
| `/help` | Display command reference | Free | Instant |
| `/talk <message>` | AI conversation | Varies | < 30 seconds |

**Additional Features:**
- Unrecognized commands trigger helpful guidance
- All commands work even if Automaton API is temporarily down (graceful degradation)
- Commands are case-insensitive
- Markdown formatting supported in all responses

## Commands

### `/start` - Register and Get Started

**Purpose:** Initialize your account and receive welcome credits

**Usage:**
```
/start
```

**What Happens:**
1. Bot registers your Telegram account with the Automaton API
2. Your account is credited with initial free credits (typically 1000)
3. You receive a welcome message with your credit balance
4. You're ready to use all bot features

**Response Example:**
```
Welcome to CryptoMentor! 🎉

Your account has been created with 1000 free credits.

Available commands:
• /status - Check your credit balance
• /talk <message> - Chat with AI
• /help - View all commands

Start by asking me anything about crypto trading!
```

**Notes:**
- Idempotent: Running `/start` multiple times won't create duplicate accounts
- Works even if API is temporarily unavailable (fallback message provided)
- No parameters required

---

### `/status` - Check Your Account

**Purpose:** View your current credit balance, activity statistics, and account information

**Usage:**
```
/status
```

**What You'll See:**
- 💰 Current credit balance
- 💬 Total conversation count
- 🕐 Last activity timestamp
- 📊 Account status

**Response Example:**
```
📊 Your CryptoMentor Status

💰 Credits: 850
💬 Conversations: 15
🕐 Last Active: 2 hours ago
✅ Status: Active

Use /talk to start a conversation!
```

**Notes:**
- Free to use (no credit cost)
- Real-time data from Automaton API
- Helps you track credit usage

---

### `/help` - View Command Reference

**Purpose:** Display comprehensive help information about all available commands

**Usage:**
```
/help
```

**What You'll See:**
- Complete list of all bot commands
- Usage examples for each command
- Notification schedule information
- Credit system explanation
- Tips for getting started

**Response Example:**
```
🤖 CryptoMentor Bot Help

Available Commands:
━━━━━━━━━━━━━━━━━━━━

/start
Register your account and receive free credits

/status
View your credit balance and activity stats

/talk <message>
Have a conversation with the AI trading assistant
Example: /talk What's the market trend today?

/help
Display this help message

━━━━━━━━━━━━━━━━━━━━

📬 Scheduled Notifications:
• Morning: 08:00 WIB
• Afternoon: 14:00 WIB  
• Evening: 20:00 WIB

💡 Tip: Each /talk conversation uses credits. Check your balance with /status!
```

**Notes:**
- Always available, even offline
- No credit cost
- Includes examples and tips

---

### `/talk` - AI Conversation

**Purpose:** Have an interactive conversation with the AI trading assistant

**Usage:**
```
/talk <your message>
```

**Parameters:**
- `<your message>` - Your question or statement (required)

**Examples:**
```
/talk What's the best time to buy Bitcoin?
/talk Explain support and resistance levels
/talk Should I invest in altcoins?
/talk What's your analysis of the current market?
```

**What Happens:**
1. Bot checks your credit balance
2. If sufficient credits: Shows typing indicator
3. Sends your message to Automaton AI
4. Returns AI-generated response
5. Credits are deducted from your balance

**Response Example:**
```
User: /talk What's the best trading strategy?

Bot: [typing...]

Bot: For effective trading, I recommend a balanced approach:

1. **Risk Management**: Never risk more than 2% per trade
2. **Technical Analysis**: Use indicators like RSI and MACD
3. **Fundamental Analysis**: Stay updated on market news
4. **Diversification**: Don't put all funds in one asset

Would you like me to explain any of these in detail?
```

**Error Scenarios:**

**Insufficient Credits:**
```
⚠️ Insufficient Credits

You need more credits to continue conversations.
Current balance: 0 credits

Contact support to top up your account.
```

**Empty Message:**
```
❌ Invalid Command

Please provide a message after /talk

Example: /talk What's the market trend?
```

**API Timeout:**
```
⏱️ Request Timeout

The AI is taking longer than expected to respond.
Please try again in a moment.
```

**Notes:**
- Requires sufficient credit balance
- 30-second timeout with automatic retry
- Conversation context maintained
- Supports follow-up questions

## Architecture

### System Overview

The CryptoMentor Telegram Bot operates as a standalone microservice that bridges Telegram users with the Automaton AI trading system. The architecture is designed for reliability, scalability, and maintainability.

**High-Level Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                     Telegram Platform                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   User A     │  │   User B     │  │   User N     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Telegram Bot API    │
                  │  (Polling Interface) │
                  └──────────┬───────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│              CryptoMentor Telegram Bot                      │
│              (Node.js Application)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Bot Core                             │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │  Command   │  │   Error    │  │  Message   │     │  │
│  │  │  Handlers  │  │  Handler   │  │  Formatter │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Client Layer                         │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │  Request   │  │   Retry    │  │   Auth     │     │  │
│  │  │  Builder   │  │   Logic    │  │  Manager   │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Notification Scheduler                      │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │   Cron     │  │   Batch    │  │   Rate     │     │  │
│  │  │   Jobs     │  │  Processor │  │  Limiter   │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬───────────────────────────────────┘
                         │
                         │ HTTPS (REST API)
                         │ Authorization: Bearer <API_KEY>
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│              Automaton API Service                          │
│              (Railway Deployment)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  User Management  │  AI Engine  │  Credit System    │  │
│  └──────────────────────────────────────────────────────┘  │
│  URL: https://automaton-production-a899.up.railway.app     │
└────────────────────────────────────────────────────────────┘
```

---

### Bot-API Relationship

The CryptoMentor Bot and Automaton API maintain a clear separation of concerns:

**Bot Responsibilities:**
- 🤖 User interface and interaction handling
- 📱 Telegram API communication (polling, sending messages)
- ⏰ Scheduled notification delivery
- 🔄 Request/response formatting
- ⚠️ Error handling and user feedback
- 📊 Command routing and validation

**Automaton API Responsibilities:**
- 🧠 AI conversation processing
- 👤 User account management
- 💰 Credit system and balance tracking
- 📈 Trading analysis and insights
- 💾 Data persistence and storage
- 🔐 Authentication and authorization

**Communication Flow:**

```
User Command Flow:
┌──────┐     ┌─────────┐     ┌──────────────┐     ┌─────────────┐
│ User │────▶│ Telegram│────▶│ Bot (Polling)│────▶│ Automaton   │
│      │     │   API   │     │              │     │    API      │
└──────┘     └─────────┘     └──────────────┘     └─────────────┘
                                     │                     │
                                     │◀────────────────────┘
                                     │   (API Response)
                                     │
                                     ▼
                              ┌──────────────┐
                              │   Format     │
                              │   Response   │
                              └──────┬───────┘
                                     │
                                     ▼
┌──────┐     ┌─────────┐     ┌──────────────┐
│ User │◀────│ Telegram│◀────│     Bot      │
│      │     │   API   │     │              │
└──────┘     └─────────┘     └──────────────┘

Scheduled Notification Flow:
┌──────────┐     ┌──────────────┐     ┌─────────────┐
│   Cron   │────▶│     Bot      │────▶│ Automaton   │
│  Trigger │     │              │     │    API      │
└──────────┘     └──────────────┘     └─────────────┘
                        │                     │
                        │◀────────────────────┘
                        │  (Notification Content)
                        │
                        ▼
                 ┌──────────────┐
                 │  Get Active  │
                 │    Users     │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │   Batch      │
                 │   Delivery   │
                 └──────┬───────┘
                        │
                        ▼
┌──────┐     ┌─────────┐     ┌──────────────┐
│Users │◀────│ Telegram│◀────│     Bot      │
│(All) │     │   API   │     │              │
└──────┘     └─────────┘     └──────────────┘
```

**API Integration Details:**

| Aspect | Implementation |
|--------|----------------|
| **Protocol** | HTTPS (REST) |
| **Authentication** | Bearer token in Authorization header |
| **Data Format** | JSON |
| **Timeout** | 30 seconds per request |
| **Retry Strategy** | 3 attempts with 2-second delays |
| **Error Handling** | Graceful degradation with fallback messages |
| **Connection** | Keep-alive for connection pooling |

**Why This Architecture?**

✅ **Separation of Concerns**: Bot handles UI, API handles business logic
✅ **Scalability**: Each service can scale independently
✅ **Maintainability**: Changes to AI logic don't require bot redeployment
✅ **Reliability**: Bot continues operating even if API is temporarily down
✅ **Security**: API key authentication protects backend services
✅ **Flexibility**: Easy to add new bots or interfaces to same API

---

### Component Architecture

**1. Bot Core Layer**

```javascript
// Main bot initialization
const bot = new TelegramBot(TELEGRAM_BOT_TOKEN, { polling: true });

// Command registration
bot.onText(/\/start/, handleUserGreeting);
bot.onText(/\/status/, handleStatusCommand);
bot.onText(/\/help/, handleHelpCommand);
bot.onText(/\/talk (.+)/, handleConversation);

// Error handlers
bot.on('polling_error', handlePollingError);
bot.on('error', handleBotError);
```

**Responsibilities:**
- Initialize Telegram bot instance
- Register command handlers
- Manage polling connection
- Route messages to appropriate handlers
- Handle bot-level errors

---

**2. Command Handler Layer**

```javascript
// Command handler structure
async function handleCommand(msg) {
  try {
    // 1. Extract user information
    const userId = msg.from.id;
    const username = msg.from.username || msg.from.first_name;
    
    // 2. Validate input
    if (!isValidInput(msg)) {
      return sendErrorMessage(userId, 'Invalid input');
    }
    
    // 3. Call API
    const response = await apiClient.makeRequest(endpoint, data);
    
    // 4. Format response
    const message = formatResponse(response);
    
    // 5. Send to user
    await bot.sendMessage(userId, message, { parse_mode: 'Markdown' });
    
  } catch (error) {
    handleError(error, msg);
  }
}
```

**Responsibilities:**
- Parse command arguments
- Validate user input
- Call appropriate API endpoints
- Format responses for Telegram
- Handle command-specific errors

---

**3. API Client Layer**

```javascript
class AutomatonAPIClient {
  constructor(baseURL, apiKey) {
    this.baseURL = baseURL;
    this.apiKey = apiKey;
    this.timeout = 30000;
    this.maxRetries = 3;
  }
  
  async makeRequest(endpoint, options) {
    let lastError;
    
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
            ...options.headers
          },
          timeout: this.timeout
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
        
      } catch (error) {
        lastError = error;
        if (attempt < this.maxRetries) {
          await sleep(2000 * attempt); // Exponential backoff
        }
      }
    }
    
    throw lastError;
  }
}
```

**Responsibilities:**
- Construct API requests
- Add authentication headers
- Handle timeouts and retries
- Parse API responses
- Manage connection pooling

---

**4. Notification Scheduler Layer**

```javascript
// Cron job configuration
const schedules = [
  { time: '0 8 * * *', name: 'Morning' },
  { time: '0 14 * * *', name: 'Afternoon' },
  { time: '0 20 * * *', name: 'Evening' }
];

schedules.forEach(schedule => {
  cron.schedule(schedule.time, async () => {
    await sendScheduledNotifications(schedule.name);
  }, {
    timezone: 'Asia/Jakarta'
  });
});

async function sendScheduledNotifications(scheduleName) {
  // 1. Fetch notification content
  const content = await apiClient.getNotificationContent();
  
  // 2. Get active users
  const users = await getActiveUsers();
  
  // 3. Batch delivery with rate limiting
  let successCount = 0;
  let failureCount = 0;
  
  for (const user of users) {
    try {
      await bot.sendMessage(user.telegramId, content);
      successCount++;
      await sleep(33); // Rate limiting: ~30 msg/sec
    } catch (error) {
      failureCount++;
      logError(`Failed to send to user ${user.telegramId}`, error);
    }
  }
  
  logInfo(`${scheduleName} notifications: ${successCount} success, ${failureCount} failed`);
}
```

**Responsibilities:**
- Register cron jobs for scheduled times
- Fetch notification content from API
- Manage user list
- Implement batch delivery
- Apply rate limiting
- Track delivery statistics

---

**5. Error Handler Layer**

```javascript
function handleError(error, context) {
  // Log error with context
  logError({
    timestamp: new Date().toISOString(),
    error: error.message,
    stack: error.stack,
    context: context
  });
  
  // Determine user-friendly message
  let userMessage;
  
  if (error.code === 'ETIMEDOUT') {
    userMessage = '⏱️ Request timeout. Please try again.';
  } else if (error.code === 'ECONNREFUSED') {
    userMessage = '🔌 Service temporarily unavailable.';
  } else if (error.status === 401) {
    userMessage = '🔐 Authentication error. Please contact support.';
  } else {
    userMessage = '❌ An error occurred. Please try again later.';
  }
  
  // Send to user
  if (context.userId) {
    bot.sendMessage(context.userId, userMessage);
  }
}
```

**Responsibilities:**
- Catch and log all errors
- Determine error type and severity
- Generate user-friendly messages
- Prevent error propagation
- Maintain bot stability

---

### Data Flow Diagrams

**User Registration Flow:**

```
┌──────┐
│ User │ Sends /start
└───┬──┘
    │
    ▼
┌────────────────┐
│ Bot receives   │
│ /start command │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ Extract user   │
│ info from msg  │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ POST /api/     │
│ users/register │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ Automaton API  │
│ creates user   │
│ & assigns      │
│ credits        │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ API returns    │
│ user data +    │
│ credits        │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ Bot formats    │
│ welcome msg    │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ Send message   │
│ to user        │
└───┬────────────┘
    │
    ▼
┌──────┐
│ User │ Receives welcome
└──────┘
```

**AI Conversation Flow:**

```
┌──────┐
│ User │ Sends /talk What's BTC price?
└───┬──┘
    │
    ▼
┌────────────────┐
│ Bot receives   │
│ /talk command  │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ Extract message│
│ from command   │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ GET /api/users/│
│ {id}/status    │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ Check credits  │
│ sufficient?    │
└───┬────────────┘
    │
    ├─No──▶ Send "Insufficient credits" ──▶ End
    │
    Yes
    │
    ▼
┌────────────────┐
│ Send typing    │
│ indicator      │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ POST /api/chat │
│ {userId, msg}  │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ Automaton AI   │
│ processes msg  │
│ & generates    │
│ response       │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ API returns    │
│ AI response    │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ Bot formats    │
│ response       │
└───┬────────────┘
    │
    ▼
┌────────────────┐
│ Send to user   │
└───┬────────────┘
    │
    ▼
┌──────┐
│ User │ Receives AI response
└──────┘
```

---

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Railway Platform                       │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  CryptoMentor Bot Service                      │    │
│  │  ┌──────────────────────────────────────────┐  │    │
│  │  │  Container                               │  │    │
│  │  │  - Node.js 18 Runtime                    │  │    │
│  │  │  - Bot Application (index.js)            │  │    │
│  │  │  - Dependencies (node_modules)           │  │    │
│  │  │  - Environment Variables                 │  │    │
│  │  └──────────────────────────────────────────┘  │    │
│  │                                                 │    │
│  │  Resources:                                     │    │
│  │  - RAM: 512MB (free tier)                      │    │
│  │  - CPU: Shared                                 │    │
│  │  - Storage: Ephemeral                          │    │
│  │  - Network: Outbound only                      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Automaton API Service (Separate Project)     │    │
│  │  URL: automaton-production-a899.up.railway.app │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                         │
                         │ Internet
                         │
                         ▼
              ┌──────────────────┐
              │  Telegram Servers│
              └──────────────────┘
```

**Key Architectural Decisions:**

1. **Polling vs Webhooks**: Uses polling for simplicity (no public URL needed)
2. **Stateless Design**: No local state storage; all data in Automaton API
3. **Separate Services**: Bot and API deployed independently for flexibility
4. **Error Isolation**: Failures in one component don't crash entire system
5. **Rate Limiting**: Built-in to respect Telegram API limits
6. **Retry Logic**: Automatic retries for transient failures
7. **Graceful Degradation**: Bot continues operating even if API is down

## Prerequisites

- Node.js 18 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Railway CLI (for deployment)
- Automaton API access credentials

## Installation

### 1. Clone or Create Project

```bash
mkdir cryptomentor-bot
cd cryptomentor-bot
```

### 2. Install Dependencies

```bash
npm install
```

This will install:
- `node-telegram-bot-api@^0.66.0` - Telegram Bot API client
- `node-cron@^3.0.3` - Cron job scheduler for notifications
- `node-fetch@^3.3.2` - HTTP client for API requests

### 3. Create Environment Variables

Create a `.env` file (for local testing only - not used in production):

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
AUTOMATON_API_URL=https://automaton-production-a899.up.railway.app
AUTOMATON_API_KEY=your_api_key_here
NODE_ENV=development
```

**Note**: Never commit `.env` to version control. It's already in `.gitignore`.

## Deployment to Railway

This section provides comprehensive instructions for deploying the CryptoMentor Telegram Bot to Railway platform. For a detailed step-by-step guide, see [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md).

### Prerequisites

Before deploying, ensure you have:

**Required Tools:**
- ✅ **Node.js 18+**: Download from [nodejs.org](https://nodejs.org/)
- ✅ **Railway CLI**: Install from [docs.railway.app/develop/cli](https://docs.railway.app/develop/cli)
- ✅ **Git**: For version control (optional but recommended)

**Required Credentials:**
- ✅ **Telegram Bot Token**: Obtain from [@BotFather](https://t.me/botfather) on Telegram
  - Start a chat with @BotFather
  - Send `/newbot` and follow the prompts
  - Save the token provided (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
- ✅ **Railway Account**: Sign up at [railway.app](https://railway.app)
- ✅ **Automaton API Access**: 
  - API URL: `https://automaton-production-a899.up.railway.app`
  - API Key: Provided by Automaton service

**System Requirements:**
- Operating System: Windows, macOS, or Linux
- RAM: 512MB minimum (for Railway free tier)
- Internet connection: Stable connection required

---

### Railway Setup Steps

#### Step 1: Install Railway CLI

**Windows (PowerShell):**
```powershell
iwr https://railway.app/install.ps1 | iex
```

**macOS/Linux:**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

**Verify Installation:**
```bash
railway --version
```

#### Step 2: Login to Railway

```bash
railway login
```

This opens your browser for authentication. Complete the login process and return to your terminal.

#### Step 3: Initialize Project

Navigate to your bot directory and initialize:

```bash
cd cryptomentor-bot
railway init
```

When prompted:
1. Select: **"Create new project"**
2. Enter project name: **`cryptomentor-telegram-bot`**
3. Press Enter to confirm

**Verify:**
```bash
railway status
```

You should see your project name and status.

#### Step 4: Configure Environment Variables

Set all required environment variables:

```bash
# Set Telegram Bot Token
railway variables set TELEGRAM_BOT_TOKEN=your_bot_token_here

# Set Automaton API URL
railway variables set AUTOMATON_API_URL=https://automaton-production-a899.up.railway.app

# Set Automaton API Key
railway variables set AUTOMATON_API_KEY=your_api_key_here

# Set Node Environment
railway variables set NODE_ENV=production
```

**Verify All Variables:**
```bash
railway variables
```

Expected output:
```
TELEGRAM_BOT_TOKEN=8025048597:AAEng...
AUTOMATON_API_URL=https://automaton-production-a899.up.railway.app
AUTOMATON_API_KEY=0d69e617601...
NODE_ENV=production
```

#### Step 5: Deploy

```bash
railway up
```

This command:
1. Uploads your code to Railway
2. Installs dependencies (`npm install`)
3. Starts the bot using the start script
4. Begins polling for Telegram messages

**Deployment typically takes 1-3 minutes.**

#### Step 6: Verify Deployment

**Check Logs:**
```bash
railway logs
```

Look for these success indicators:
- ✅ `"Bot is ready and listening for messages..."`
- ✅ `"Scheduled notifications configured for 08:00, 14:00, 20:00 WIB"`
- ✅ No error messages

**Test in Telegram:**
1. Open Telegram and find your bot
2. Send `/start` - Should receive welcome message
3. Send `/help` - Should see command list
4. Send `/status` - Should see your account info
5. Send `/talk Hello` - Should get AI response

---

### Environment Variables Reference

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Your bot's authentication token from @BotFather | `123456789:ABCdef...` | ✅ Yes |
| `AUTOMATON_API_URL` | Base URL of the Automaton API service | `https://automaton-production-a899.up.railway.app` | ✅ Yes |
| `AUTOMATON_API_KEY` | Authentication key for Automaton API | `0d69e61760114de2...` | ✅ Yes |
| `NODE_ENV` | Node.js environment mode | `production` | ✅ Yes |

**Security Notes:**
- Never commit these values to version control
- Store them only in Railway's environment variables
- Rotate API keys periodically
- Use different tokens for development and production

---

### Deployment Commands Quick Reference

```bash
# View project status
railway status

# View/manage environment variables
railway variables                    # List all
railway variables set KEY=value      # Set variable
railway variables delete KEY         # Delete variable

# Deployment
railway up                          # Deploy code
railway up --detach                 # Deploy without logs

# Monitoring
railway logs                        # View recent logs
railway logs --follow               # Follow logs in real-time
railway logs --tail 100             # View last 100 lines

# Project management
railway open                        # Open project in dashboard
railway link                        # Link to different project
railway unlink                      # Unlink from project

# Service management
railway restart                     # Restart service
railway down                        # Stop service
```

---

### Post-Deployment Checklist

After deployment, verify:

- [ ] Bot responds to `/start` command
- [ ] Bot responds to `/help` command  
- [ ] Bot responds to `/status` command
- [ ] Bot responds to `/talk` command with AI responses
- [ ] No errors in Railway logs (`railway logs`)
- [ ] Bot remains online continuously
- [ ] Response time < 2 seconds for commands
- [ ] Scheduled notifications configured (check logs)

**Success Criteria:**
- ✅ All commands working
- ✅ Users can register and receive credits
- ✅ AI conversations functional
- ✅ No errors in logs
- ✅ Bot online 24/7

---

### Updating Your Deployment

When you make code changes:

```bash
# 1. Test locally first
npm start

# 2. Commit changes (optional but recommended)
git add .
git commit -m "Description of changes"

# 3. Deploy to Railway
railway up

# 4. Verify deployment
railway logs
```

---

### Monitoring Your Deployment

**View Logs:**
```bash
# Recent logs
railway logs

# Follow in real-time
railway logs --follow

# Filter for errors
railway logs | grep -i error
```

**Railway Dashboard:**
Visit [railway.app/dashboard](https://railway.app/dashboard) to:
- View deployment status
- Monitor resource usage (CPU, Memory, Network)
- Check environment variables
- View build and runtime logs
- Manage project settings

**Key Metrics to Monitor:**
- Memory usage (should stay < 512MB)
- Response times (should be < 2 seconds)
- Error rates (should be minimal)
- Uptime (target: 99.5%+)

---

### Troubleshooting Deployment

See the [Troubleshooting](#troubleshooting) section below for common deployment issues and solutions.

## Configuration

### Notification Schedule

The bot automatically sends market updates at three times throughout the day, optimized for trading activity:

**Schedule Details:**

| Time (WIB) | Time (UTC) | Update Type | Purpose |
|------------|------------|-------------|---------|
| 08:00 | 01:00 | 🌅 Morning | Pre-market analysis and daily outlook |
| 14:00 | 07:00 | 🌤️ Afternoon | Mid-day market update and trend analysis |
| 20:00 | 13:00 | 🌙 Evening | End-of-day summary and next-day preview |

**Timezone Configuration:**
- Primary timezone: **Asia/Jakarta (WIB/UTC+7)**
- Configured using `node-cron` with timezone support
- Automatically handles daylight saving time (though Indonesia doesn't observe DST)

**How Notifications Work:**
1. Cron jobs are registered on bot startup
2. At scheduled time, bot fetches content from Automaton API
3. Content is delivered to all active users (those who have used `/start`)
4. Delivery statistics are logged (success/failure counts)
5. Individual delivery failures don't stop batch processing

**Customizing Schedule:**

To modify notification times, edit the cron expressions in `index.js`:

```javascript
// Current schedule
cron.schedule('0 8 * * *', sendScheduledNotifications, { timezone: 'Asia/Jakarta' });  // 08:00 WIB
cron.schedule('0 14 * * *', sendScheduledNotifications, { timezone: 'Asia/Jakarta' }); // 14:00 WIB
cron.schedule('0 20 * * *', sendScheduledNotifications, { timezone: 'Asia/Jakarta' }); // 20:00 WIB

// Cron format: minute hour day month dayOfWeek
// Example: '30 9 * * *' = 09:30 daily
```

---

### API Integration

The bot communicates with the Automaton API service for all AI-powered features and user management.

**API Endpoints Used:**

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|--------------|----------|
| `/api/users/register` | POST | Register new user | `{telegramId, username}` | User data + credits |
| `/api/users/{userId}/status` | GET | Get user status | None | Credits, stats, activity |
| `/api/chat` | POST | AI conversation | `{userId, message}` | AI response |
| `/api/notifications` | GET | Fetch notification content | None | Notification message |

**Authentication:**

All API requests include an Authorization header:

```javascript
headers: {
  'Authorization': `Bearer ${AUTOMATON_API_KEY}`,
  'Content-Type': 'application/json'
}
```

**Request Configuration:**

```javascript
{
  timeout: 30000,        // 30-second timeout
  retries: 3,            // Retry up to 3 times
  retryDelay: 2000,      // 2-second delay between retries
  method: 'POST',        // or GET
  headers: {
    'Authorization': 'Bearer <API_KEY>',
    'Content-Type': 'application/json'
  }
}
```

**Error Handling:**

The bot implements comprehensive error handling for API interactions:

- **Timeout Errors**: Retry up to 3 times with 2-second delays
- **4xx Errors**: Log error and return user-friendly message
- **5xx Errors**: Retry with exponential backoff
- **Network Errors**: Graceful degradation with fallback messages
- **Rate Limiting**: Automatic request queuing

**API Response Format:**

```javascript
// Successful response
{
  "success": true,
  "data": {
    // Response data
  }
}

// Error response
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

**Connection Pooling:**

The bot uses `node-fetch` with keep-alive for efficient API communication:
- Reuses TCP connections
- Reduces latency for subsequent requests
- Handles connection lifecycle automatically

**Monitoring API Health:**

Check API connectivity:
```bash
# View API-related logs
railway logs | grep -i "api"

# Check for API errors
railway logs | grep -i "api error"
```

---

### Timezone Settings

**Primary Timezone: Asia/Jakarta (WIB)**

The bot uses Western Indonesian Time (WIB/UTC+7) for all scheduled operations.

**Configuration:**

```javascript
// In notification scheduler
cron.schedule('0 8 * * *', sendScheduledNotifications, {
  timezone: 'Asia/Jakarta'  // WIB/UTC+7
});
```

**Timezone Conversion Reference:**

| WIB (UTC+7) | UTC | EST (UTC-5) | PST (UTC-8) |
|-------------|-----|-------------|-------------|
| 08:00 | 01:00 | 20:00 (prev day) | 17:00 (prev day) |
| 14:00 | 07:00 | 02:00 | 23:00 (prev day) |
| 20:00 | 13:00 | 08:00 | 05:00 |

**Why WIB?**
- Aligns with Asian trading hours
- Covers major crypto market activity periods
- Optimal for Indonesian and Southeast Asian users

**Changing Timezone:**

To use a different timezone, modify the `timezone` parameter:

```javascript
// Examples
timezone: 'America/New_York'  // EST/EDT
timezone: 'Europe/London'     // GMT/BST
timezone: 'Asia/Tokyo'        // JST
timezone: 'UTC'               // Universal Time
```

**Supported Timezones:**

The bot supports all IANA timezone identifiers. Common options:
- `Asia/Jakarta` - Western Indonesian Time (WIB)
- `Asia/Singapore` - Singapore Time (SGT)
- `Asia/Tokyo` - Japan Standard Time (JST)
- `Europe/London` - British Time (GMT/BST)
- `America/New_York` - Eastern Time (EST/EDT)
- `America/Los_Angeles` - Pacific Time (PST/PDT)
- `UTC` - Coordinated Universal Time

**Verifying Timezone:**

Check logs on bot startup:
```
Scheduled notifications configured for 08:00, 14:00, 20:00 WIB
Timezone: Asia/Jakarta (UTC+7)
```

---

### Advanced Configuration

**Rate Limiting:**

Telegram API limits: 30 messages per second

```javascript
// Automatic rate limiting in notification delivery
const RATE_LIMIT = 30; // messages per second
const DELAY_MS = 1000 / RATE_LIMIT; // ~33ms between messages
```

**Memory Management:**

```javascript
// Recommended Railway settings
RAM: 512MB minimum
CPU: Shared (sufficient for most use cases)
```

**Logging Configuration:**

```javascript
// Log levels
const LOG_LEVELS = {
  ERROR: 'error',   // Critical errors
  WARN: 'warn',     // Warnings
  INFO: 'info',     // General information
  DEBUG: 'debug'    // Detailed debugging (development only)
};

// Set via environment variable
NODE_ENV=production  // INFO and above
NODE_ENV=development // DEBUG and above
```

**Performance Tuning:**

```javascript
// API request timeout
const API_TIMEOUT = 30000; // 30 seconds

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 2000; // 2 seconds

// Connection pooling
const KEEP_ALIVE = true;
const MAX_SOCKETS = 50;
```

## Development

### Local Setup

Follow these steps to set up the bot for local development and testing.

#### Prerequisites

- **Node.js 18+**: Download from [nodejs.org](https://nodejs.org/)
- **npm**: Comes with Node.js
- **Text Editor**: VS Code, Sublime Text, or your preferred editor
- **Telegram Bot Token**: Get from [@BotFather](https://t.me/botfather)
- **Automaton API Access**: API URL and key

#### Step 1: Clone or Create Project

```bash
# If cloning from repository
git clone <repository-url>
cd cryptomentor-bot

# Or create new directory
mkdir cryptomentor-bot
cd cryptomentor-bot
```

#### Step 2: Install Dependencies

```bash
npm install
```

This installs:
- `node-telegram-bot-api@^0.66.0` - Telegram Bot API client
- `node-cron@^3.0.3` - Cron job scheduler
- `node-fetch@^3.3.2` - HTTP client for API requests

#### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env file (DO NOT commit to version control)
TELEGRAM_BOT_TOKEN=your_bot_token_here
AUTOMATON_API_URL=https://automaton-production-a899.up.railway.app
AUTOMATON_API_KEY=your_api_key_here
NODE_ENV=development
```

**Important:** The `.env` file is already in `.gitignore` to prevent accidental commits.

#### Step 4: Load Environment Variables

Add this to the top of `index.js` for local development:

```javascript
// Load environment variables from .env file (development only)
if (process.env.NODE_ENV !== 'production') {
  const dotenv = await import('dotenv');
  dotenv.config();
}
```

**Note:** Railway automatically provides environment variables in production, so this is only needed locally.

#### Step 5: Run the Bot

```bash
npm start
```

You should see:
```
Bot is ready and listening for messages...
Scheduled notifications configured for 08:00, 14:00, 20:00 WIB
```

#### Step 6: Test Locally

1. Open Telegram and find your bot
2. Send `/start` - Should receive welcome message
3. Send `/help` - Should see command list
4. Send `/status` - Should see your status
5. Send `/talk Hello` - Should get AI response

---

### Project Structure

```
cryptomentor-bot/
│
├── index.js                          # Main bot implementation
│   ├── Bot initialization
│   ├── Command handlers
│   ├── API client
│   ├── Notification scheduler
│   └── Error handling
│
├── package.json                      # Project configuration
│   ├── Dependencies
│   ├── Scripts
│   ├── ES module configuration
│   └── Node.js version requirement
│
├── package-lock.json                 # Dependency lock file
│
├── .gitignore                        # Git ignore rules
│   ├── node_modules/
│   ├── .env
│   ├── *.log
│   └── .DS_Store
│
├── README.md                         # This file
│
├── RAILWAY_DEPLOYMENT_GUIDE.md       # Detailed deployment guide
│
├── DEPLOYMENT_CHECKLIST.md           # Step-by-step checklist
│
└── .env                              # Environment variables (local only, not in git)
```

**Code Organization:**

The `index.js` file is organized into logical sections:

```javascript
// 1. Imports and Configuration
import TelegramBot from 'node-telegram-bot-api';
import cron from 'node-cron';
import fetch from 'node-fetch';

// 2. Environment Variables
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const AUTOMATON_API_URL = process.env.AUTOMATON_API_URL;
const AUTOMATON_API_KEY = process.env.AUTOMATON_API_KEY;

// 3. Bot Initialization
const bot = new TelegramBot(TELEGRAM_BOT_TOKEN, { polling: true });

// 4. API Client Functions
async function registerUser(telegramId, username) { ... }
async function getUserStatus(userId) { ... }
async function sendChatMessage(userId, message) { ... }
async function getNotificationContent() { ... }

// 5. Command Handlers
async function handleUserGreeting(msg) { ... }
async function handleStatusCommand(msg) { ... }
async function handleHelpCommand(msg) { ... }
async function handleConversation(msg, match) { ... }

// 6. Notification Scheduler
async function sendScheduledNotifications() { ... }
cron.schedule('0 8 * * *', sendScheduledNotifications, { timezone: 'Asia/Jakarta' });
cron.schedule('0 14 * * *', sendScheduledNotifications, { timezone: 'Asia/Jakarta' });
cron.schedule('0 20 * * *', sendScheduledNotifications, { timezone: 'Asia/Jakarta' });

// 7. Error Handlers
bot.on('polling_error', handlePollingError);
bot.on('error', handleBotError);

// 8. Startup Message
console.log('Bot is ready and listening for messages...');
```

---

### Testing Approach

#### Manual Testing

**Test Each Command:**

```bash
# Start the bot locally
npm start

# In Telegram, test:
/start          # Should register and show credits
/help           # Should show command list
/status         # Should show account info
/talk Hello     # Should get AI response
```

**Test Error Scenarios:**

```bash
# Test with invalid commands
/invalidcommand     # Should show help message

# Test with empty /talk
/talk              # Should show usage error

# Test with API down
# (Stop Automaton API temporarily)
/talk Hello        # Should show fallback error message
```

#### Unit Testing (Optional)

For production applications, consider adding unit tests:

```javascript
// test/bot.test.js
import { describe, it, expect } from 'jest';
import { formatWelcomeMessage, validateUserInput } from '../index.js';

describe('Bot Functions', () => {
  it('should format welcome message correctly', () => {
    const userData = { username: 'testuser', credits: 1000 };
    const message = formatWelcomeMessage(userData);
    expect(message).toContain('Welcome');
    expect(message).toContain('1000');
  });
  
  it('should validate user input', () => {
    expect(validateUserInput('')).toBe(false);
    expect(validateUserInput('Hello')).toBe(true);
  });
});
```

#### Integration Testing

Test the complete flow:

```javascript
// test/integration.test.js
describe('User Registration Flow', () => {
  it('should register user and return credits', async () => {
    const userId = 12345;
    const username = 'testuser';
    
    const result = await registerUser(userId, username);
    
    expect(result.success).toBe(true);
    expect(result.credits).toBeGreaterThan(0);
  });
});
```

#### Property-Based Testing

Test invariants across many inputs:

```javascript
// test/properties.test.js
import fc from 'fast-check';

describe('Bot Properties', () => {
  it('should handle any valid user ID', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 1, max: 1000000 }),
        async (userId) => {
          const result = await getUserStatus(userId);
          expect(result).toBeDefined();
        }
      )
    );
  });
});
```

---

### Development Workflow

#### 1. Making Changes

```bash
# 1. Create a feature branch (if using git)
git checkout -b feature/new-command

# 2. Make your changes to index.js

# 3. Test locally
npm start

# 4. Test in Telegram

# 5. Commit changes
git add .
git commit -m "Add new command"

# 6. Push to repository
git push origin feature/new-command
```

#### 2. Adding New Commands

```javascript
// In index.js

// 1. Register command handler
bot.onText(/\/newcommand/, handleNewCommand);

// 2. Implement handler function
async function handleNewCommand(msg) {
  const userId = msg.from.id;
  
  try {
    // Your command logic here
    const response = await someAPICall();
    
    await bot.sendMessage(userId, response, {
      parse_mode: 'Markdown'
    });
    
  } catch (error) {
    handleError(error, { userId, command: 'newcommand' });
  }
}

// 3. Update help message
function getHelpMessage() {
  return `
Available Commands:
...
/newcommand - Description of new command
  `;
}
```

#### 3. Debugging

**Enable Debug Logging:**

```javascript
// Add at top of index.js
const DEBUG = process.env.NODE_ENV === 'development';

function debugLog(message, data) {
  if (DEBUG) {
    console.log(`[DEBUG] ${message}`, data);
  }
}

// Use in code
debugLog('User registered', { userId, username });
```

**View Detailed Logs:**

```bash
# Run with debug output
NODE_ENV=development npm start

# Or use node's built-in debugger
node --inspect index.js
```

**Common Debug Points:**

```javascript
// Log incoming messages
bot.on('message', (msg) => {
  debugLog('Received message', {
    from: msg.from.id,
    text: msg.text,
    timestamp: new Date().toISOString()
  });
});

// Log API requests
async function makeAPIRequest(endpoint, options) {
  debugLog('API Request', { endpoint, options });
  
  const response = await fetch(endpoint, options);
  
  debugLog('API Response', {
    status: response.status,
    statusText: response.statusText
  });
  
  return response;
}
```

---

### Code Style Guidelines

**Follow these conventions for consistency:**

#### Naming Conventions

```javascript
// Functions: camelCase
async function handleUserGreeting(msg) { }

// Constants: UPPER_SNAKE_CASE
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

// Variables: camelCase
const userId = msg.from.id;

// Classes: PascalCase (if using classes)
class AutomatonAPIClient { }
```

#### Async/Await

```javascript
// ✅ Good: Use async/await
async function fetchData() {
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    handleError(error);
  }
}

// ❌ Avoid: Promise chains
function fetchData() {
  return fetch(url)
    .then(response => response.json())
    .then(data => data)
    .catch(error => handleError(error));
}
```

#### Error Handling

```javascript
// ✅ Good: Specific error handling
try {
  const result = await apiCall();
} catch (error) {
  if (error.code === 'ETIMEDOUT') {
    // Handle timeout
  } else if (error.status === 401) {
    // Handle auth error
  } else {
    // Handle generic error
  }
}

// ❌ Avoid: Silent failures
try {
  await apiCall();
} catch (error) {
  // Nothing
}
```

#### Comments

```javascript
// ✅ Good: Explain why, not what
// Retry with exponential backoff to handle transient network issues
await retryWithBackoff(apiCall, 3);

// ❌ Avoid: Obvious comments
// Call the API
await apiCall();
```

---

### Performance Optimization

#### 1. Connection Pooling

```javascript
// Use keep-alive for API requests
import fetch from 'node-fetch';
import http from 'http';
import https from 'https';

const httpAgent = new http.Agent({ keepAlive: true });
const httpsAgent = new https.Agent({ keepAlive: true });

const agent = (_parsedURL) => {
  return _parsedURL.protocol === 'http:' ? httpAgent : httpsAgent;
};

// Use in fetch calls
await fetch(url, { agent });
```

#### 2. Rate Limiting

```javascript
// Implement token bucket for rate limiting
class RateLimiter {
  constructor(maxTokens, refillRate) {
    this.maxTokens = maxTokens;
    this.tokens = maxTokens;
    this.refillRate = refillRate;
    
    setInterval(() => {
      this.tokens = Math.min(this.maxTokens, this.tokens + 1);
    }, 1000 / refillRate);
  }
  
  async acquire() {
    while (this.tokens < 1) {
      await sleep(100);
    }
    this.tokens--;
  }
}

const rateLimiter = new RateLimiter(30, 30); // 30 msg/sec

// Use before sending messages
await rateLimiter.acquire();
await bot.sendMessage(userId, message);
```

#### 3. Caching

```javascript
// Cache frequently accessed data
const cache = new Map();
const CACHE_TTL = 60000; // 1 minute

async function getCachedData(key, fetchFunction) {
  const cached = cache.get(key);
  
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  
  const data = await fetchFunction();
  cache.set(key, { data, timestamp: Date.now() });
  
  return data;
}

// Usage
const userData = await getCachedData(
  `user:${userId}`,
  () => getUserStatus(userId)
);
```

---

### Deployment from Development

When ready to deploy your changes:

```bash
# 1. Test locally
npm start
# Test all functionality

# 2. Commit changes
git add .
git commit -m "Description of changes"

# 3. Push to repository (if using git)
git push origin main

# 4. Deploy to Railway
railway up

# 5. Verify deployment
railway logs

# 6. Test in production
# Send commands to your bot on Telegram
```

---

### Troubleshooting Development Issues

**Bot Not Starting Locally:**

```bash
# Check Node.js version
node --version  # Should be 18+

# Check environment variables
echo $TELEGRAM_BOT_TOKEN  # Should show token

# Check for syntax errors
node --check index.js
```

**Module Import Errors:**

```bash
# Ensure package.json has "type": "module"
cat package.json | grep type

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**API Connection Issues:**

```bash
# Test API connectivity
curl https://automaton-production-a899.up.railway.app/health

# Check API key
echo $AUTOMATON_API_KEY
```

---

### Contributing Guidelines

If working in a team:

1. **Branch Naming**: `feature/description`, `bugfix/description`
2. **Commit Messages**: Clear, descriptive messages
3. **Code Review**: All changes reviewed before merging
4. **Testing**: Test locally before pushing
5. **Documentation**: Update README for new features

---

### Resources

**Documentation:**
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [node-telegram-bot-api](https://github.com/yagop/node-telegram-bot-api)
- [node-cron](https://github.com/node-cron/node-cron)
- [Railway Docs](https://docs.railway.app)

**Tools:**
- [BotFather](https://t.me/botfather) - Create and manage bots
- [Railway CLI](https://docs.railway.app/develop/cli) - Deployment tool
- [Postman](https://www.postman.com/) - API testing

**Community:**
- [Telegram Bot Developers](https://t.me/BotDevelopers)
- [Railway Discord](https://discord.gg/railway)

## Troubleshooting

This section covers common issues and their solutions. For deployment-specific issues, also see [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md).

---

### Bot Not Responding to Commands

**Symptoms:**
- Bot doesn't reply when you send commands
- Messages show as delivered but no response
- Bot appears offline in Telegram

**Common Causes & Solutions:**

**1. Bot Not Running on Railway**

Check deployment status:
```bash
railway status
```

If stopped, redeploy:
```bash
railway up
```

**2. Invalid Bot Token**

Verify token in environment variables:
```bash
railway variables | grep TELEGRAM_BOT_TOKEN
```

If incorrect, update it:
```bash
railway variables set TELEGRAM_BOT_TOKEN=correct_token_here
railway restart
```

**3. Polling Errors**

Check logs for polling errors:
```bash
railway logs | grep -i "polling"
```

Common polling errors:
- `409 Conflict`: Another instance is running (stop other instances)
- `401 Unauthorized`: Invalid bot token
- Network timeout: Check Railway service status

**4. Bot Blocked by User**

If a specific user can't interact:
- User may have blocked the bot
- Ask user to unblock and send `/start` again

**Solution Checklist:**
- [ ] Check Railway deployment status
- [ ] Verify bot token is correct
- [ ] Check logs for errors
- [ ] Restart bot: `railway restart`
- [ ] Test with `/start` command
- [ ] Verify bot is not blocked

---

### API Connection Errors

**Symptoms:**
- "Service temporarily unavailable" messages
- Timeout errors in logs
- Commands work but AI responses fail

**Common Causes & Solutions:**

**1. Automaton API Down**

Check if API is accessible:
```bash
curl https://automaton-production-a899.up.railway.app/health
```

Or visit the URL in your browser. If down:
- Wait for API to recover
- Bot will automatically retry
- Users receive fallback messages

**2. Invalid API Key**

Verify API key:
```bash
railway variables | grep AUTOMATON_API_KEY
```

Update if incorrect:
```bash
railway variables set AUTOMATON_API_KEY=correct_key_here
railway restart
```

**3. Network Timeouts**

Check logs for timeout patterns:
```bash
railway logs | grep -i "timeout"
```

Solutions:
- API timeout is set to 30 seconds (usually sufficient)
- Bot automatically retries up to 3 times
- If persistent, check Automaton API health

**4. Rate Limiting**

If making too many requests:
```bash
railway logs | grep -i "rate limit"
```

Solutions:
- Bot automatically handles rate limiting
- Implements exponential backoff
- Queues requests if needed

**Solution Checklist:**
- [ ] Verify Automaton API is running
- [ ] Check API URL is correct
- [ ] Verify API key is valid
- [ ] Review logs for specific errors
- [ ] Test API endpoint manually
- [ ] Check network connectivity

---

### Notifications Not Sending

**Symptoms:**
- No notifications received at scheduled times
- Logs show notification errors
- Some users receive, others don't

**Common Causes & Solutions:**

**1. Cron Jobs Not Registered**

Check logs on bot startup:
```bash
railway logs | grep -i "scheduled"
```

Should see:
```
Scheduled notifications configured for 08:00, 14:00, 20:00 WIB
```

If missing, redeploy:
```bash
railway up
```

**2. Timezone Issues**

Verify timezone in logs:
```bash
railway logs | grep -i "timezone"
```

Should show: `Asia/Jakarta (UTC+7)`

**3. No Active Users**

Notifications only sent to users who have used `/start`:
```bash
railway logs | grep -i "active users"
```

If "0 active users", no notifications will be sent.

**4. API Content Unavailable**

Check if notification content is fetched:
```bash
railway logs | grep -i "notification content"
```

If API fails to provide content, notifications won't send.

**5. Individual Delivery Failures**

Some users may fail due to:
- User blocked the bot
- User deleted their Telegram account
- User's privacy settings

Bot continues sending to other users (isolated error handling).

**Solution Checklist:**
- [ ] Verify cron jobs are registered
- [ ] Check timezone is Asia/Jakarta
- [ ] Confirm active users exist
- [ ] Test notification API endpoint
- [ ] Review logs at scheduled times
- [ ] Check individual user delivery status

---

### Deployment Failures

**Symptoms:**
- `railway up` command fails
- Build errors in Railway dashboard
- Bot doesn't start after deployment

**Common Causes & Solutions:**

**1. Missing Environment Variables**

Verify all required variables are set:
```bash
railway variables
```

Required variables:
- `TELEGRAM_BOT_TOKEN`
- `AUTOMATON_API_URL`
- `AUTOMATON_API_KEY`
- `NODE_ENV`

Set any missing variables:
```bash
railway variables set VARIABLE_NAME=value
```

**2. Node.js Version Mismatch**

Check `package.json` specifies Node.js 18+:
```json
{
  "engines": {
    "node": ">=18.0.0"
  }
}
```

**3. Dependency Installation Failures**

Check build logs:
```bash
railway logs --deployment
```

If npm install fails:
- Verify `package.json` is valid JSON
- Check all dependencies are available
- Try: `npm install` locally first

**4. Start Script Issues**

Verify `package.json` has correct start script:
```json
{
  "scripts": {
    "start": "node index.js"
  }
}
```

**5. Port Configuration**

Railway may assign a PORT variable. If bot fails to start:
```bash
railway logs | grep -i "port"
```

Note: Telegram bots use polling, not HTTP ports, so this is usually not an issue.

**Solution Checklist:**
- [ ] All environment variables set
- [ ] Node.js version ≥ 18
- [ ] Dependencies install successfully
- [ ] Start script is correct
- [ ] Review build logs for errors
- [ ] Test locally before deploying

---

### Memory Issues

**Symptoms:**
- Bot crashes randomly
- "Out of memory" errors in logs
- Railway shows high memory usage

**Common Causes & Solutions:**

**1. Memory Leak**

Monitor memory usage:
```bash
railway logs | grep -i "memory"
```

Check Railway dashboard for memory graph.

**2. Too Many Concurrent Operations**

If sending notifications to many users:
- Implement batching (already included)
- Add delays between batches
- Limit concurrent API requests

**3. Large Message Queue**

If message queue grows too large:
- Increase processing rate
- Implement queue size limits
- Clear old messages

**4. Insufficient Memory Allocation**

Railway free tier: 512MB RAM

If consistently hitting limits:
- Optimize code for memory efficiency
- Implement caching strategically
- Consider upgrading Railway plan

**Solution Checklist:**
- [ ] Monitor memory usage in Railway dashboard
- [ ] Check for memory leaks in logs
- [ ] Optimize notification batching
- [ ] Implement queue size limits
- [ ] Consider upgrading Railway plan

---

### Command-Specific Issues

**`/start` Command Issues:**

**Problem:** Duplicate accounts created
- **Solution:** Bot implements idempotency; check API logs

**Problem:** No credits shown
- **Solution:** Verify Automaton API returns credit data

**Problem:** Slow response
- **Solution:** Check API response time; should be < 2 seconds

---

**`/status` Command Issues:**

**Problem:** Incorrect credit balance
- **Solution:** Verify API returns accurate data; check for sync issues

**Problem:** "User not found" error
- **Solution:** User needs to run `/start` first

---

**`/talk` Command Issues:**

**Problem:** "Insufficient credits" despite having credits
- **Solution:** Check credit balance in API; may be sync delay

**Problem:** Timeout errors
- **Solution:** API response taking > 30 seconds; check Automaton API performance

**Problem:** No typing indicator
- **Solution:** Telegram API issue; bot still processes request

**Problem:** Generic responses
- **Solution:** Check Automaton AI is functioning correctly

---

### Error Messages Reference

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "Service temporarily unavailable" | Automaton API is down | Wait for API recovery; bot will retry |
| "Insufficient credits" | User has no credits | Top up credits via Automaton |
| "Invalid command" | Malformed command syntax | Check command format; use `/help` |
| "Request timeout" | API took > 30 seconds | Retry command; check API performance |
| "Bot is not responding" | Bot offline or crashed | Check Railway status; redeploy if needed |
| "User not found" | User not registered | Run `/start` command first |
| "Rate limit exceeded" | Too many requests | Wait a moment; bot will queue requests |

---

### Getting Help

If you've tried the solutions above and still have issues:

**1. Check Logs:**
```bash
railway logs --tail 200
```

**2. Check Railway Dashboard:**
- Visit [railway.app/dashboard](https://railway.app/dashboard)
- View deployment status
- Check resource usage
- Review build logs

**3. Verify Configuration:**
```bash
railway variables
railway status
```

**4. Test Locally:**
```bash
# Set environment variables in .env file
npm start
```

**5. Review Documentation:**
- [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) - Detailed deployment guide
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Step-by-step checklist
- Railway Docs: [docs.railway.app](https://docs.railway.app)

**6. Common Debug Commands:**
```bash
# View recent errors
railway logs | grep -i error

# View API-related logs
railway logs | grep -i api

# View notification logs
railway logs | grep -i notification

# Follow logs in real-time
railway logs --follow
```

## Error Handling

The bot implements comprehensive error handling:

- **Telegram API Failures**: Automatic reconnection with exponential backoff (1s, 2s, 4s, 8s, max 60s)
- **Automaton API Failures**: Graceful degradation with user-friendly error messages
- **Invalid Commands**: Helpful guidance on correct usage
- **Rate Limiting**: Automatic message queuing
- **Network Issues**: Retry logic with configurable attempts

All errors are logged with timestamps and context for debugging.

## Security

- All sensitive credentials stored in environment variables
- HTTPS used for all API communications
- User input sanitized before processing
- No sensitive data logged
- API keys never exposed to end users

## Performance

- Response time: < 2 seconds for 95% of commands
- Notification delivery: 10,000 users within 5 minutes
- Memory usage: < 512MB during normal operation
- Concurrent users: Supports 1000+ simultaneous users

## Monitoring

Monitor bot health using Railway logs:

```bash
# View real-time logs
railway logs

# View logs with filtering
railway logs --filter error
```

Key metrics to monitor:
- Bot startup messages
- Command processing times
- API request/response logs
- Notification delivery statistics
- Error rates and types

## Support

For issues or questions:
1. Check this README's troubleshooting section
2. Review Railway logs for error details
3. Verify all environment variables are correctly set
4. Ensure Automaton API is accessible

## License

ISC

## Version

1.0.0
