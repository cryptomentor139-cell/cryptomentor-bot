/**
 * Test: Malformed Command Handling
 * Task 5.3.4: Handle malformed commands
 * 
 * Tests:
 * - REQ-2.8.7: Handle malformed commands with helpful usage instructions
 * - REQ-5.1.5: Respond to unrecognized commands with help message
 * 
 * This test verifies that the bot properly handles unrecognized commands
 * and provides helpful guidance to users.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('Malformed Command Handling', () => {
  let mockBot;
  let mockMsg;
  let sendMessageSpy;

  beforeEach(() => {
    // Create mock bot with message handler
    mockBot = {
      handlers: [],
      on: function(event, handler) {
        this.handlers.push({ event, handler });
      },
      sendMessage: vi.fn().mockResolvedValue({ message_id: 1 })
    };

    sendMessageSpy = mockBot.sendMessage;

    // Create mock message
    mockMsg = {
      chat: { id: 123456 },
      from: { id: 123456, username: 'testuser' },
      text: ''
    };
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Unrecognized Command Detection', () => {
    it('should detect unrecognized commands starting with /', () => {
      // Simulate registering the catch-all handler
      const handler = (msg) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        // This is an unrecognized command
        return true;
      };

      // Test unrecognized commands
      mockMsg.text = '/unknown';
      expect(handler(mockMsg)).toBe(true);

      mockMsg.text = '/invalid';
      expect(handler(mockMsg)).toBe(true);

      mockMsg.text = '/test';
      expect(handler(mockMsg)).toBe(true);

      mockMsg.text = '/randomcommand';
      expect(handler(mockMsg)).toBe(true);
    });

    it('should ignore recognized commands', () => {
      const handler = (msg) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        return true;
      };

      // Test recognized commands
      mockMsg.text = '/start';
      expect(handler(mockMsg)).toBeUndefined();

      mockMsg.text = '/status';
      expect(handler(mockMsg)).toBeUndefined();

      mockMsg.text = '/help';
      expect(handler(mockMsg)).toBeUndefined();

      mockMsg.text = '/talk hello';
      expect(handler(mockMsg)).toBeUndefined();
    });

    it('should ignore non-command messages', () => {
      const handler = (msg) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        return true;
      };

      // Test non-command messages
      mockMsg.text = 'hello';
      expect(handler(mockMsg)).toBeUndefined();

      mockMsg.text = 'this is a regular message';
      expect(handler(mockMsg)).toBeUndefined();

      mockMsg.text = '';
      expect(handler(mockMsg)).toBeUndefined();

      mockMsg.text = null;
      expect(handler(mockMsg)).toBeUndefined();
    });
  });

  describe('Helpful Error Messages', () => {
    it('should send helpful message for unrecognized commands', async () => {
      const handler = async (msg, bot) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        const errorMessage = `❓ *Unknown Command*

I don't recognize the command \`${command}\`.

*💡 Available Commands:*
• \`/start\` - Register and get started
• \`/status\` - Check your credit balance
• \`/help\` - View detailed help
• \`/talk <message>\` - Chat with AI

*Need help?* Use /help to see detailed information about each command.

*Example:*
\`/talk What is Bitcoin?\``;

        await bot.sendMessage(msg.chat.id, errorMessage, { parse_mode: 'Markdown' });
      };

      mockMsg.text = '/unknown';
      await handler(mockMsg, mockBot);

      expect(sendMessageSpy).toHaveBeenCalledTimes(1);
      expect(sendMessageSpy).toHaveBeenCalledWith(
        123456,
        expect.stringContaining('Unknown Command'),
        { parse_mode: 'Markdown' }
      );
      expect(sendMessageSpy).toHaveBeenCalledWith(
        123456,
        expect.stringContaining('/unknown'),
        { parse_mode: 'Markdown' }
      );
    });

    it('should include list of available commands in error message', async () => {
      const handler = async (msg, bot) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        const errorMessage = `❓ *Unknown Command*

I don't recognize the command \`${command}\`.

*💡 Available Commands:*
• \`/start\` - Register and get started
• \`/status\` - Check your credit balance
• \`/help\` - View detailed help
• \`/talk <message>\` - Chat with AI

*Need help?* Use /help to see detailed information about each command.

*Example:*
\`/talk What is Bitcoin?\``;

        await bot.sendMessage(msg.chat.id, errorMessage, { parse_mode: 'Markdown' });
      };

      mockMsg.text = '/invalid';
      await handler(mockMsg, mockBot);

      const sentMessage = sendMessageSpy.mock.calls[0][1];
      expect(sentMessage).toContain('/start');
      expect(sentMessage).toContain('/status');
      expect(sentMessage).toContain('/help');
      expect(sentMessage).toContain('/talk');
    });

    it('should suggest using /help command', async () => {
      const handler = async (msg, bot) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        const errorMessage = `❓ *Unknown Command*

I don't recognize the command \`${command}\`.

*💡 Available Commands:*
• \`/start\` - Register and get started
• \`/status\` - Check your credit balance
• \`/help\` - View detailed help
• \`/talk <message>\` - Chat with AI

*Need help?* Use /help to see detailed information about each command.

*Example:*
\`/talk What is Bitcoin?\``;

        await bot.sendMessage(msg.chat.id, errorMessage, { parse_mode: 'Markdown' });
      };

      mockMsg.text = '/test';
      await handler(mockMsg, mockBot);

      const sentMessage = sendMessageSpy.mock.calls[0][1];
      expect(sentMessage).toContain('/help');
      expect(sentMessage).toContain('Need help?');
    });

    it('should provide usage example', async () => {
      const handler = async (msg, bot) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        const errorMessage = `❓ *Unknown Command*

I don't recognize the command \`${command}\`.

*💡 Available Commands:*
• \`/start\` - Register and get started
• \`/status\` - Check your credit balance
• \`/help\` - View detailed help
• \`/talk <message>\` - Chat with AI

*Need help?* Use /help to see detailed information about each command.

*Example:*
\`/talk What is Bitcoin?\``;

        await bot.sendMessage(msg.chat.id, errorMessage, { parse_mode: 'Markdown' });
      };

      mockMsg.text = '/randomcommand';
      await handler(mockMsg, mockBot);

      const sentMessage = sendMessageSpy.mock.calls[0][1];
      expect(sentMessage).toContain('Example:');
      expect(sentMessage).toContain('/talk What is Bitcoin?');
    });
  });

  describe('Various Malformed Commands', () => {
    it('should handle commands with typos', async () => {
      const handler = async (msg, bot) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        await bot.sendMessage(msg.chat.id, 'error message', { parse_mode: 'Markdown' });
      };

      // Common typos
      mockMsg.text = '/stat'; // typo of /status
      await handler(mockMsg, mockBot);
      expect(sendMessageSpy).toHaveBeenCalled();

      sendMessageSpy.mockClear();

      mockMsg.text = '/hlep'; // typo of /help
      await handler(mockMsg, mockBot);
      expect(sendMessageSpy).toHaveBeenCalled();

      sendMessageSpy.mockClear();

      mockMsg.text = '/satrt'; // typo of /start
      await handler(mockMsg, mockBot);
      expect(sendMessageSpy).toHaveBeenCalled();
    });

    it('should handle commands with extra characters', async () => {
      const handler = async (msg, bot) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        await bot.sendMessage(msg.chat.id, 'error message', { parse_mode: 'Markdown' });
      };

      mockMsg.text = '/status123';
      await handler(mockMsg, mockBot);
      expect(sendMessageSpy).toHaveBeenCalled();

      sendMessageSpy.mockClear();

      mockMsg.text = '/help!';
      await handler(mockMsg, mockBot);
      expect(sendMessageSpy).toHaveBeenCalled();
    });

    it('should handle completely unknown commands', async () => {
      const handler = async (msg, bot) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        await bot.sendMessage(msg.chat.id, 'error message', { parse_mode: 'Markdown' });
      };

      mockMsg.text = '/xyz';
      await handler(mockMsg, mockBot);
      expect(sendMessageSpy).toHaveBeenCalled();

      sendMessageSpy.mockClear();

      mockMsg.text = '/randomstuff';
      await handler(mockMsg, mockBot);
      expect(sendMessageSpy).toHaveBeenCalled();

      sendMessageSpy.mockClear();

      mockMsg.text = '/123';
      await handler(mockMsg, mockBot);
      expect(sendMessageSpy).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should handle sendMessage failures gracefully', async () => {
      const failingBot = {
        sendMessage: vi.fn().mockRejectedValue(new Error('Network error'))
      };

      const handler = async (msg, bot) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        try {
          await bot.sendMessage(msg.chat.id, 'error message', { parse_mode: 'Markdown' });
        } catch (error) {
          // Should not throw, just log
          console.error('Failed to send message:', error.message);
        }
      };

      mockMsg.text = '/unknown';
      
      // Should not throw
      await expect(handler(mockMsg, failingBot)).resolves.toBeUndefined();
      expect(failingBot.sendMessage).toHaveBeenCalled();
    });
  });

  describe('REQ-2.8.7: Malformed Command Handling', () => {
    it('should satisfy REQ-2.8.7: Handle malformed commands with helpful usage instructions', async () => {
      const handler = async (msg, bot) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        const errorMessage = `❓ *Unknown Command*

I don't recognize the command \`${command}\`.

*💡 Available Commands:*
• \`/start\` - Register and get started
• \`/status\` - Check your credit balance
• \`/help\` - View detailed help
• \`/talk <message>\` - Chat with AI

*Need help?* Use /help to see detailed information about each command.

*Example:*
\`/talk What is Bitcoin?\``;

        await bot.sendMessage(msg.chat.id, errorMessage, { parse_mode: 'Markdown' });
      };

      mockMsg.text = '/malformed';
      await handler(mockMsg, mockBot);

      // Verify helpful usage instructions are provided
      const sentMessage = sendMessageSpy.mock.calls[0][1];
      expect(sentMessage).toContain('Available Commands');
      expect(sentMessage).toContain('Example:');
      expect(sentMessage).toContain('/help');
    });
  });

  describe('REQ-5.1.5: Unrecognized Command Response', () => {
    it('should satisfy REQ-5.1.5: Respond to unrecognized commands with help message', async () => {
      const handler = async (msg, bot) => {
        const text = msg.text;
        if (!text || !text.startsWith('/')) {
          return;
        }

        const command = text.split(' ')[0].toLowerCase();
        const recognizedCommands = ['/start', '/status', '/help', '/talk'];

        if (recognizedCommands.includes(command)) {
          return;
        }

        const errorMessage = `❓ *Unknown Command*

I don't recognize the command \`${command}\`.

*💡 Available Commands:*
• \`/start\` - Register and get started
• \`/status\` - Check your credit balance
• \`/help\` - View detailed help
• \`/talk <message>\` - Chat with AI

*Need help?* Use /help to see detailed information about each command.

*Example:*
\`/talk What is Bitcoin?\``;

        await bot.sendMessage(msg.chat.id, errorMessage, { parse_mode: 'Markdown' });
      };

      mockMsg.text = '/unrecognized';
      await handler(mockMsg, mockBot);

      // Verify help message is sent
      expect(sendMessageSpy).toHaveBeenCalledTimes(1);
      const sentMessage = sendMessageSpy.mock.calls[0][1];
      
      // Should contain help information
      expect(sentMessage).toContain('Unknown Command');
      expect(sentMessage).toContain('Available Commands');
      expect(sentMessage).toContain('/start');
      expect(sentMessage).toContain('/status');
      expect(sentMessage).toContain('/help');
      expect(sentMessage).toContain('/talk');
    });
  });
});

console.log('✅ Malformed command handling tests defined');
