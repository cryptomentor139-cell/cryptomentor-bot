# Phase 9: Testing and Validation Guide

## Overview

This guide provides comprehensive testing procedures for the CryptoMentor Telegram Bot. All tests should be performed manually to ensure the bot functions correctly in production.

**Prerequisites:**
- Bot is deployed to Railway
- All environment variables are configured
- You have access to the Telegram bot via your Telegram account
- You have access to Railway logs: `railway logs`

---

## 9.1 Manual Testing

### 9.1.1 Test /start Command

**Purpose:** Verify user registration and welcome message functionality

**Test Steps:**

1. **First-time user registration:**
   ```
   Action: Send /start to the bot
   Expected Result:
   - Welcome message appears within 2 seconds
   - Message includes your username
   - Message displays initial credit balance (e.g., "1000 credits")
   - Message uses Markdown formatting with emojis
   ```

2. **Idempotency test (duplicate registration):**
   ```
   Action: Send /start again (2-3 times)
   Expected Result:
   - Same welcome message appears
   - Credit balance remains unchanged
   - No duplicate user accounts created in Automaton API
   - No errors in Railway logs
   ```

3. **API failure scenario:**
   ```
   Action: If Automaton API is down, send /start
   Expected Result:
   - Fallback welcome message appears
   - Message indicates service is temporarily unavailable
   - Bot remains operational
   - Error is logged in Railway logs
   ```

**Verification Checklist:**
- [ ] Welcome message received within 2 seconds
- [ ] Credits displayed correctly
- [ ] Multiple /start commands don't create duplicates
- [ ] Fallback message works when API is down
- [ ] No errors in user-facing messages

---

### 9.1.2 Test /status Command

**Purpose:** Verify user status information retrieval and display

**Test Steps:**

1. **Check status display:**
   ```
   Action: Send /status to the bot
   Expected Result:
   - Status message appears within 2 seconds
   - Credit balance is displayed
   - Conversation count is shown
   - Last activity timestamp is shown
   - Information is formatted clearly with emojis
   ```

2. **Status after conversation:**
   ```
   Action: 
   1. Send /talk Hello
   2. Wait for response
   3. Send /status
   Expected Result:
   - Credit balance decreased (conversation cost deducted)
   - Conversation count increased by 1
   - Last activity timestamp updated
   ```

3. **API error handling:**
   ```
   Action: If API is slow/down, send /status
   Expected Result:
   - User-friendly error message appears
   - No internal error details exposed
   - Bot remains operational
   ```

**Verification Checklist:**
- [ ] Status displays within 2 seconds
- [ ] Credit balance is accurate
- [ ] Conversation count updates correctly
- [ ] Last activity time is human-readable
- [ ] Error messages are user-friendly

---

### 9.1.3 Test /help Command

**Purpose:** Verify help documentation is complete and accessible

**Test Steps:**

1. **View help message:**
   ```
   Action: Send /help to the bot
   Expected Result:
   - Help message appears immediately
   - All 4 commands listed (/start, /status, /help, /talk)
   - Each command has description
   - Usage examples provided
   - Notification schedule explained (08:00, 14:00, 20:00 WIB)
   - Credit system explained
   - Message uses Markdown formatting
   ```

2. **Help from invalid command:**
   ```
   Action: Send /unknown or /invalid
   Expected Result:
   - Bot responds with help message or suggestion
   - Message guides user to use /help
   ```

**Verification Checklist:**
- [ ] All commands documented
- [ ] Examples are clear and accurate
- [ ] Notification times listed correctly
- [ ] Credit system explained
- [ ] Formatting is readable

---

### 9.1.4 Test /talk Command

**Purpose:** Verify AI conversation functionality and credit system

**Test Steps:**

1. **Valid conversation:**
   ```
   Action: Send /talk What's the best trading strategy?
   Expected Result:
   - Typing indicator appears immediately
   - AI response received within 30 seconds
   - Response is relevant to the question
   - Credits deducted from balance
   - Response uses Markdown formatting
   ```

2. **Empty message:**
   ```
   Action: Send /talk (without message)
   Expected Result:
   - Error message explaining correct usage
   - Example provided: /talk <your message>
   - No credits deducted
   ```

3. **Insufficient credits:**
   ```
   Action: Use /talk until credits run out
   Expected Result:
   - Bot sends "insufficient credits" message
   - Message explains how to get more credits
   - No API call made
   - No error in logs
   ```

4. **Long conversation:**
   ```
   Action: Send multiple /talk commands in sequence
   Expected Result:
   - Each response is contextually relevant
   - Typing indicator shows for each
   - Credits deducted for each message
   - No timeout errors
   ```

5. **API timeout:**
   ```
   Action: Send /talk during high API load
   Expected Result:
   - If timeout occurs, user-friendly error message
   - Message suggests trying again
   - No internal error details exposed
   ```

**Verification Checklist:**
- [ ] Typing indicator appears
- [ ] AI responses are relevant
- [ ] Credits deducted correctly
- [ ] Empty messages handled gracefully
- [ ] Insufficient credits message clear
- [ ] Timeout errors handled well
- [ ] Long conversations work smoothly

---

### 9.1.5 Test Scheduled Notifications

**Purpose:** Verify automated notifications are sent at correct times

**Test Steps:**

1. **08:00 WIB notification:**
   ```
   Action: Wait for 08:00 WIB (UTC+7)
   Expected Result:
   - Notification received within 1 minute of 08:00
   - Content is relevant (market update, trading tips, etc.)
   - Message uses Markdown formatting
   - All active users receive notification
   ```

2. **14:00 WIB notification:**
   ```
   Action: Wait for 14:00 WIB (UTC+7)
   Expected Result:
   - Notification received within 1 minute of 14:00
   - Content is different from morning notification
   - Formatting is consistent
   ```

3. **20:00 WIB notification:**
   ```
   Action: Wait for 20:00 WIB (UTC+7)
   Expected Result:
   - Notification received within 1 minute of 20:00
   - Evening-appropriate content
   - Formatting is consistent
   ```

4. **Check delivery statistics:**
   ```
   Action: Run `railway logs` after each notification
   Expected Result:
   - Log shows "Notifications sent: X success, Y failed"
   - Success count matches active user count
   - Failed deliveries logged with reasons
   ```

**Verification Checklist:**
- [ ] 08:00 WIB notification received on time
- [ ] 14:00 WIB notification received on time
- [ ] 20:00 WIB notification received on time
- [ ] Content is relevant and well-formatted
- [ ] Delivery statistics logged correctly
- [ ] Failed deliveries don't stop batch

**Note:** Notification testing requires waiting for scheduled times. Plan accordingly.

---

## 9.2 Error Scenario Testing

### 9.2.1 Test with Automaton API Down

**Purpose:** Verify bot resilience when backend API is unavailable

**Test Steps:**

1. **Simulate API downtime:**
   ```
   Action: 
   1. Temporarily set wrong AUTOMATON_API_URL in Railway
   2. Send /start command
   Expected Result:
   - Fallback welcome message appears
   - Message indicates service is temporarily unavailable
   - Bot doesn't crash
   ```

2. **Test all commands during downtime:**
   ```
   Action: Send /status, /talk, /help during API downtime
   Expected Result:
   - Each command returns user-friendly error message
   - /help still works (doesn't require API)
   - Bot remains operational
   - Errors logged in Railway logs
   ```

3. **Test recovery:**
   ```
   Action: 
   1. Restore correct AUTOMATON_API_URL
   2. Send commands again
   Expected Result:
   - Bot automatically recovers
   - Commands work normally
   - No restart required
   ```

**Verification Checklist:**
- [ ] Fallback messages displayed
- [ ] Bot doesn't crash
- [ ] /help works without API
- [ ] Automatic recovery works
- [ ] Errors logged properly

---

### 9.2.2 Test with Invalid Commands

**Purpose:** Verify bot handles malformed input gracefully

**Test Steps:**

1. **Unknown commands:**
   ```
   Action: Send /unknown, /test, /random
   Expected Result:
   - Helpful error message
   - Suggestion to use /help
   - No crash or internal errors
   ```

2. **Malformed /talk:**
   ```
   Action: Send /talk, /talk   , /talk123
   Expected Result:
   - Usage instructions provided
   - Example shown: /talk <your message>
   - No API call made
   ```

3. **Special characters:**
   ```
   Action: Send /talk <script>alert('test')</script>
   Expected Result:
   - Input sanitized before API call
   - No injection attack possible
   - Normal response received
   ```

4. **Very long messages:**
   ```
   Action: Send /talk followed by 5000+ characters
   Expected Result:
   - Message truncated or rejected
   - User-friendly error if too long
   - No crash
   ```

**Verification Checklist:**
- [ ] Unknown commands handled
- [ ] Malformed commands explained
- [ ] Special characters sanitized
- [ ] Long messages handled
- [ ] No crashes or exposures

---

### 9.2.3 Test with Network Issues

**Purpose:** Verify bot handles connection problems gracefully

**Test Steps:**

1. **Telegram API disconnection:**
   ```
   Action: Monitor Railway logs during network issues
   Expected Result:
   - Bot detects disconnection
   - Exponential backoff reconnection starts
   - Delays: 1s, 2s, 4s, 8s, 16s, 32s, 60s (max)
   - Bot reconnects automatically
   - Logs show reconnection attempts
   ```

2. **API timeout:**
   ```
   Action: Send /talk during high network latency
   Expected Result:
   - Request times out after 30 seconds
   - User receives timeout error message
   - Bot remains operational
   - Retry logic attempts 3 times
   ```

3. **Partial network failure:**
   ```
   Action: Test during intermittent connectivity
   Expected Result:
   - Some requests succeed, some fail
   - Failed requests retried automatically
   - Users receive responses or error messages
   - No silent failures
   ```

**Verification Checklist:**
- [ ] Disconnection detected
- [ ] Exponential backoff works
- [ ] Automatic reconnection succeeds
- [ ] Timeouts handled gracefully
- [ ] Retry logic functions correctly

---

### 9.2.4 Test Rate Limiting

**Purpose:** Verify bot respects Telegram API rate limits

**Test Steps:**

1. **Rapid command sending:**
   ```
   Action: Send 50+ commands rapidly (within 10 seconds)
   Expected Result:
   - All commands processed
   - Responses may be delayed
   - No "Too Many Requests" errors
   - Messages queued internally
   - Rate stays under 30 msg/sec
   ```

2. **Notification delivery rate:**
   ```
   Action: Check logs during scheduled notification
   Expected Result:
   - Delivery rate doesn't exceed 30 msg/sec
   - Large user base handled smoothly
   - Delays added between messages if needed
   - All users eventually receive notification
   ```

3. **Queue behavior:**
   ```
   Action: Send many commands while bot is busy
   Expected Result:
   - Commands queued in order
   - Processed sequentially
   - No dropped messages
   - Queue cleared eventually
   ```

**Verification Checklist:**
- [ ] Rate limit respected (30 msg/sec)
- [ ] Messages queued properly
- [ ] No dropped messages
- [ ] Large batches handled
- [ ] No Telegram API errors

---

## 9.3 Integration Testing

### 9.3.1 Verify API Integration

**Purpose:** Ensure bot correctly integrates with Automaton API

**Test Steps:**

1. **User registration verification:**
   ```
   Action:
   1. Send /start with new user
   2. Check Automaton API database/logs
   Expected Result:
   - User record created in Automaton
   - Telegram ID matches
   - Username stored correctly
   - Initial credits assigned
   ```

2. **Credit deduction verification:**
   ```
   Action:
   1. Note current credits with /status
   2. Send /talk message
   3. Check /status again
   4. Verify in Automaton API
   Expected Result:
   - Credits deducted in bot response
   - Credits deducted in Automaton database
   - Amounts match exactly
   - Transaction logged
   ```

3. **Status synchronization:**
   ```
   Action:
   1. Have multiple conversations
   2. Check /status
   3. Verify in Automaton API
   Expected Result:
   - Conversation count matches
   - Last activity time matches
   - Credit balance matches
   - All data synchronized
   ```

**Verification Checklist:**
- [ ] User registration synced
- [ ] Credit deductions accurate
- [ ] Status data synchronized
- [ ] No data inconsistencies
- [ ] API calls authenticated correctly

---

### 9.3.2 Verify Notification Delivery

**Purpose:** Ensure notifications reach all active users

**Test Steps:**

1. **Delivery to all users:**
   ```
   Action: Wait for scheduled notification time
   Expected Result:
   - All active users receive notification
   - Check Railway logs for delivery stats
   - Success count matches active user count
   ```

2. **Delivery statistics:**
   ```
   Action: Check Railway logs after notification
   Expected Result:
   - Log shows: "Notifications sent: X success, Y failed"
   - Failed deliveries have reasons logged
   - Reasons include: blocked bot, deleted account, etc.
   ```

3. **Content consistency:**
   ```
   Action: Compare notifications received by multiple users
   Expected Result:
   - All users receive identical content
   - Formatting is consistent
   - Timing is synchronized (within 1 minute)
   ```

4. **Failed delivery handling:**
   ```
   Action: Block bot, then wait for notification
   Expected Result:
   - Delivery fails for blocked user
   - Other users still receive notification
   - Failure logged but doesn't stop batch
   ```

**Verification Checklist:**
- [ ] All active users receive notifications
- [ ] Delivery statistics accurate
- [ ] Content consistent across users
- [ ] Failed deliveries logged
- [ ] Batch continues despite failures

---

### 9.3.3 Verify Error Handling

**Purpose:** Ensure errors are handled correctly throughout the system

**Test Steps:**

1. **Error logging verification:**
   ```
   Action: 
   1. Trigger various errors (API down, invalid input, etc.)
   2. Check Railway logs
   Expected Result:
   - All errors logged with timestamp
   - Error type and stack trace included
   - Context information provided
   - Severity level indicated (ERROR, WARN, INFO)
   ```

2. **User-facing error messages:**
   ```
   Action: Trigger errors and check bot responses
   Expected Result:
   - All error messages are user-friendly
   - No internal error details exposed
   - No stack traces shown to users
   - Helpful guidance provided
   ```

3. **Error recovery:**
   ```
   Action: 
   1. Trigger error condition
   2. Resolve error condition
   3. Test bot functionality
   Expected Result:
   - Bot automatically recovers
   - No manual intervention needed
   - Normal operation resumes
   - No lingering issues
   ```

**Verification Checklist:**
- [ ] All errors logged properly
- [ ] User messages are friendly
- [ ] No internal details exposed
- [ ] Automatic recovery works
- [ ] Logs provide debugging info

---

## Testing Summary

### Quick Test Checklist

Use this checklist for rapid validation after deployment or updates:

**Basic Functionality:**
- [ ] /start - Welcome message with credits
- [ ] /status - Shows credit balance
- [ ] /help - Lists all commands
- [ ] /talk - AI responds correctly

**Error Handling:**
- [ ] Invalid commands handled
- [ ] API downtime handled
- [ ] Network issues handled
- [ ] Rate limiting works

**Integration:**
- [ ] User registration synced
- [ ] Credits deducted correctly
- [ ] Notifications delivered
- [ ] Errors logged properly

### Testing Schedule

**After Initial Deployment:**
- Complete all 9.1 tests (Manual Testing)
- Complete all 9.2 tests (Error Scenarios)
- Complete all 9.3 tests (Integration)

**After Each Update:**
- Run Quick Test Checklist
- Test affected functionality thoroughly
- Verify no regressions

**Weekly:**
- Verify scheduled notifications (all 3 times)
- Check delivery statistics
- Review error logs

**Monthly:**
- Complete full test suite
- Performance testing
- Security review

---

## Troubleshooting Common Issues

### Issue: Bot not responding

**Diagnosis:**
```bash
railway logs
```

**Solutions:**
- Check if bot is running (look for "Bot is ready" in logs)
- Verify environment variables are set
- Check Telegram API connectivity
- Restart deployment if needed

### Issue: Notifications not sent

**Diagnosis:**
```bash
railway logs | grep "Notifications sent"
```

**Solutions:**
- Verify cron jobs are scheduled (check logs at notification times)
- Check timezone configuration (Asia/Jakarta)
- Verify Automaton API is accessible
- Check active user list

### Issue: API errors

**Diagnosis:**
```bash
railway logs | grep "ERROR"
```

**Solutions:**
- Verify AUTOMATON_API_URL is correct
- Verify AUTOMATON_API_KEY is valid
- Check Automaton API health
- Review retry logic in logs

### Issue: Rate limiting errors

**Diagnosis:**
```bash
railway logs | grep "rate limit"
```

**Solutions:**
- Reduce message sending rate
- Implement longer delays between messages
- Check queue size
- Verify rate limiting logic

---

## Next Steps

After completing Phase 9 testing:

1. **Document Results:** Note any issues found and resolutions
2. **Update Code:** Fix any bugs discovered during testing
3. **Proceed to Phase 10:** Setup monitoring and maintenance procedures
4. **Create Runbook:** Document operational procedures for ongoing management

---

**Last Updated:** 2024
**Version:** 1.0
**Status:** Ready for Testing
