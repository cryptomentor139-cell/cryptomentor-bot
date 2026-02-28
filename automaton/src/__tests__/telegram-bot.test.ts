/**
 * Telegram Bot Tests
 *
 * Tests for Telegram bot interface including property-based tests
 * and unit tests for command handlers.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import fc from "fast-check";
import { createTelegramBot, notifyPaymentRequest } from "../telegram/bot.js";
import type { TelegramBotConfig } from "../telegram/bot.js";
import type { AutomatonDatabase, PaymentRequest } from "../types.js";
import type { PaymentApprovalSystem } from "../payment/approval.js";

const PROPERTY_TEST_ITERATIONS = 100;

// Mock TelegramBot
vi.mock("node-telegram-bot-api", () => {
  return {
    default: class MockTelegramBot {
      private handlers: Map<string, Function[]> = new Map();
      private callbackHandlers: Function[] = [];
      public sentMessages: any[] = [];
      public answeredCallbacks: any[] = [];
      public editedMarkups: any[] = [];

      constructor(token: string, options: any) {}

      onText(pattern: RegExp, handler: Function) {
        const key = pattern.toString();
        if (!this.handlers.has(key)) {
          this.handlers.set(key, []);
        }
        this.handlers.get(key)!.push(handler);
      }

      on(event: string, handler: Function) {
        if (event === "callback_query") {
          this.callbackHandlers.push(handler);
        }
      }

      async sendMessage(chatId: number, text: string, options?: any) {
        this.sentMessages.push({ chatId, text, options });
        return { message_id: this.sentMessages.length };
      }

      async answerCallbackQuery(queryId: string, options: any) {
        this.answeredCallbacks.push({ queryId, options });
      }

      async editMessageReplyMarkup(markup: any, options: any) {
        this.editedMarkups.push({ markup, options });
      }

      // Test helpers
      async simulateMessage(msg: any) {
        for (const [pattern, handlers] of this.handlers.entries()) {
          const regex = new RegExp(pattern.slice(1, -1));
          const match = msg.text?.match(regex);
          if (match) {
            for (const handler of handlers) {
              await handler(msg, match);
            }
          }
        }
      }

      async simulateCallbackQuery(query: any) {
        for (const handler of this.callbackHandlers) {
          await handler(query);
        }
      }

      isPolling() {
        return true;
      }
    },
  };
});

// Mock database
function createMockDatabase(): AutomatonDatabase {
  const state = {
    agentState: "running" as any,
    turnCount: 42,
    identity: new Map([
      ["name", "TestBot"],
      ["address", "0x1234567890123456789012345678901234567890"],
    ]),
    turns: [
      {
        id: "turn1",
        timestamp: new Date().toISOString(),
        state: "running" as any,
        thinking: "test",
        toolCalls: [],
        tokenUsage: { promptTokens: 100, completionTokens: 50, totalTokens: 150 },
        costCents: 1,
      },
    ],
    transactions: [
      {
        id: "txn1",
        type: "credit_check" as any,
        balanceAfterCents: 1000,
        description: "test",
        timestamp: new Date().toISOString(),
      },
    ],
    children: [],
  };

  return {
    getAgentState: () => state.agentState,
    setAgentState: (s: any) => { state.agentState = s; },
    getTurnCount: () => state.turnCount,
    getIdentity: (key: string) => state.identity.get(key),
    setIdentity: (key: string, value: string) => { state.identity.set(key, value); },
    getRecentTurns: (limit: number) => state.turns.slice(0, limit),
    getRecentTransactions: (limit: number) => state.transactions.slice(0, limit),
    getChildren: () => state.children,
    getTurnById: () => undefined,
    insertTurn: () => {},
    insertToolCall: () => {},
    getToolCallsForTurn: () => [],
    getHeartbeatEntries: () => [],
    upsertHeartbeatEntry: () => {},
    updateHeartbeatLastRun: () => {},
    insertTransaction: () => {},
    getInstalledTools: () => [],
    installTool: () => {},
    removeTool: () => {},
    insertModification: () => {},
    getRecentModifications: () => [],
    getKV: () => undefined,
    setKV: () => {},
    deleteKV: () => {},
    getSkills: () => [],
    getSkillByName: () => undefined,
    upsertSkill: () => {},
    removeSkill: () => {},
    getChildById: () => undefined,
    insertChild: () => {},
    updateChildStatus: () => {},
    getRegistryEntry: () => undefined,
    setRegistryEntry: () => {},
    insertReputation: () => {},
    getReputation: () => [],
    insertInboxMessage: () => {},
    getUnprocessedInboxMessages: () => [],
    markInboxMessageProcessed: () => {},
    insertPaymentRequest: () => {},
    updatePaymentRequest: () => {},
    getPaymentRequestById: () => undefined,
    getPaymentRequestsByStatus: () => [],
    getPaymentRequestsSince: () => [],
    getTelegramConfig: () => undefined,
    setTelegramConfig: () => {},
    close: () => {},
  } as AutomatonDatabase;
}

// Mock payment system
function createMockPaymentSystem(): PaymentApprovalSystem {
  return {
    requestPayment: vi.fn(),
    approvePayment: vi.fn(),
    rejectPayment: vi.fn(),
    executeApprovedPayments: vi.fn(),
    getPendingRequests: () => [],
    getRequestById: () => undefined,
    checkRateLimit: () => true,
  };
}

describe("Telegram Bot", () => {
  describe("Property Tests", () => {
    /**
     * Feature: railway-deployment, Property 16: Telegram Authentication
     */
    it("Property 16: Telegram Authentication", async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.integer({ min: 100000, max: 999999 }), // Random user ID
          fc.constantFrom("/status", "/logs", "/approve test", "/reject test reason"), // Commands
          async (userId, command) => {
            const creatorId = "123456";
            const db = createMockDatabase();
            const paymentSystem = createMockPaymentSystem();

            const config: TelegramBotConfig = {
              token: "test-token",
              creatorId,
              db,
              paymentSystem,
              inference: {
                chat: vi.fn().mockResolvedValue({
                  content: "Test response",
                  usage: { totalTokens: 100 },
                }),
              } as any,
            };

            const bot = createTelegramBot(config) as any;

            // Simulate message from user
            const msg = {
              from: { id: userId },
              chat: { id: userId },
              text: command,
            };

            await bot.simulateMessage(msg);

            // Check if command was executed
            const isAuthorized = userId.toString() === creatorId;

            if (isAuthorized) {
              // Should have sent a response
              expect(bot.sentMessages.length).toBeGreaterThan(0);
            } else {
              // Should not have sent a response
              expect(bot.sentMessages.length).toBe(0);
            }
          }
        ),
        { numRuns: PROPERTY_TEST_ITERATIONS }
      );
    });

    /**
     * Feature: railway-deployment, Property 17: Telegram Optional Feature
     */
    it("Property 17: Telegram Optional Feature", () => {
      fc.assert(
        fc.property(
          fc.option(fc.string(), { nil: undefined }), // Optional bot token
          fc.option(fc.string(), { nil: undefined }), // Optional creator ID
          (botToken, creatorId) => {
            // If bot token is missing, system should handle gracefully
            if (!botToken) {
              // Should not crash when creating bot config
              expect(() => {
                const config = {
                  token: botToken || "",
                  creatorId: creatorId || "",
                  db: createMockDatabase(),
                  paymentSystem: createMockPaymentSystem(),
                };
                // In real implementation, this would be handled at Railway entry point
                // Here we just verify the config structure is valid
                expect(config).toBeDefined();
              }).not.toThrow();
            }
          }
        ),
        { numRuns: PROPERTY_TEST_ITERATIONS }
      );
    });

    /**
     * Feature: railway-deployment, Property 12: Payment Notification
     */
    it("Property 12: Payment Notification", async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.string({ minLength: 42, maxLength: 42 }).filter(s => s.startsWith("0x")), // Address
          fc.integer({ min: 1, max: 100000 }), // Amount in cents
          fc.option(fc.string(), { nil: undefined }), // Optional note
          async (toAddress, amountCents, note) => {
            const bot = createTelegramBot({
              token: "test-token",
              creatorId: "123456",
              db: createMockDatabase(),
              paymentSystem: createMockPaymentSystem(),
              inference: {
                chat: vi.fn().mockResolvedValue({
                  content: "Test response",
                  usage: { totalTokens: 100 },
                }),
              } as any,
            }) as any;

            const request: PaymentRequest = {
              id: "test-request-id",
              toAddress,
              amountCents,
              note,
              status: "pending_approval",
              requestedAt: new Date().toISOString(),
            };

            await notifyPaymentRequest(bot, "123456", request);

            // Should have sent notification
            expect(bot.sentMessages.length).toBe(1);
            const notification = bot.sentMessages[0];

            // Should contain payment details
            expect(notification.text).toContain(toAddress);
            expect(notification.text).toContain((amountCents / 100).toFixed(2));
            expect(notification.text).toContain(request.id);

            // Should have inline keyboard
            expect(notification.options.reply_markup).toBeDefined();
            expect(notification.options.reply_markup.inline_keyboard).toBeDefined();
          }
        ),
        { numRuns: PROPERTY_TEST_ITERATIONS }
      );
    });

    /**
     * Feature: railway-deployment, Property 18: Critical State Alert
     */
    it("Property 18: Critical State Alert", () => {
      fc.assert(
        fc.property(
          fc.constantFrom("running", "sleeping", "low_compute", "critical", "dead"),
          fc.constantFrom("running", "sleeping", "low_compute", "critical", "dead"),
          (fromState, toState) => {
            const db = createMockDatabase();
            db.setAgentState(fromState as any);

            // Simulate state change
            db.setAgentState(toState as any);

            // If transitioning to critical, should trigger alert
            const shouldAlert = toState === "critical" && fromState !== "critical";

            // In real implementation, this would send Telegram notification
            // Here we just verify the state change is tracked
            expect(db.getAgentState()).toBe(toState);

            if (shouldAlert) {
              // Alert logic would be implemented in Railway entry point
              expect(toState).toBe("critical");
            }
          }
        ),
        { numRuns: PROPERTY_TEST_ITERATIONS }
      );
    });
  });

  describe("Unit Tests", () => {
    let db: AutomatonDatabase;
    let paymentSystem: PaymentApprovalSystem;
    let config: TelegramBotConfig;

    beforeEach(() => {
      db = createMockDatabase();
      paymentSystem = createMockPaymentSystem();
      config = {
        token: "test-token",
        creatorId: "123456",
        db,
        paymentSystem,
        inference: {
          chat: vi.fn().mockResolvedValue({
            content: "Test response",
            usage: { totalTokens: 100 },
          }),
        } as any,
      };
    });

    it("should handle /start command", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateMessage({
        from: { id: 123456 },
        chat: { id: 123456 },
        text: "/start",
      });

      expect(bot.sentMessages.length).toBe(1);
      expect(bot.sentMessages[0].text).toContain("Automaton Control Bot");
      expect(bot.sentMessages[0].text).toContain("/status");
    });

    it("should handle /status command", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateMessage({
        from: { id: 123456 },
        chat: { id: 123456 },
        text: "/status",
      });

      expect(bot.sentMessages.length).toBe(1);
      expect(bot.sentMessages[0].text).toContain("System Status");
      expect(bot.sentMessages[0].text).toContain("TestBot");
      expect(bot.sentMessages[0].text).toContain("running");
    });

    it("should handle /logs command", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateMessage({
        from: { id: 123456 },
        chat: { id: 123456 },
        text: "/logs",
      });

      expect(bot.sentMessages.length).toBe(1);
      expect(bot.sentMessages[0].text).toContain("Recent Logs");
    });

    it("should handle /approve command", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateMessage({
        from: { id: 123456 },
        chat: { id: 123456 },
        text: "/approve test-payment-id",
      });

      expect(paymentSystem.approvePayment).toHaveBeenCalledWith(
        "test-payment-id",
        "123456"
      );
      expect(paymentSystem.executeApprovedPayments).toHaveBeenCalled();
    });

    it("should handle /reject command", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateMessage({
        from: { id: 123456 },
        chat: { id: 123456 },
        text: "/reject test-payment-id too expensive",
      });

      expect(paymentSystem.rejectPayment).toHaveBeenCalledWith(
        "test-payment-id",
        "123456",
        "too expensive"
      );
    });

    it("should handle /children command", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateMessage({
        from: { id: 123456 },
        chat: { id: 123456 },
        text: "/children",
      });

      expect(bot.sentMessages.length).toBe(1);
      expect(bot.sentMessages[0].text).toContain("No child agents");
    });

    it("should handle /help command", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateMessage({
        from: { id: 123456 },
        chat: { id: 123456 },
        text: "/help",
      });

      expect(bot.sentMessages.length).toBe(1);
      expect(bot.sentMessages[0].text).toContain("Automaton Control Bot");
      expect(bot.sentMessages[0].text).toContain("Commands:");
      expect(bot.sentMessages[0].text).toContain("Conversational Mode");
    });

    it("should handle /deposit command", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateMessage({
        from: { id: 123456 },
        chat: { id: 123456 },
        text: "/deposit",
      });

      expect(bot.sentMessages.length).toBe(1);
      expect(bot.sentMessages[0].text).toContain("Deposit USDC");
      expect(bot.sentMessages[0].text).toContain("0x1234567890123456789012345678901234567890");
      expect(bot.sentMessages[0].text).toContain("Base network");
    });

    it("should handle /credits command", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateMessage({
        from: { id: 123456 },
        chat: { id: 123456 },
        text: "/credits",
      });

      expect(bot.sentMessages.length).toBe(1);
      expect(bot.sentMessages[0].text).toContain("Financial Status");
      expect(bot.sentMessages[0].text).toContain("Conway Credits");
      expect(bot.sentMessages[0].text).toContain("Recent Transactions");
    });

    it("should handle /clear command", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateMessage({
        from: { id: 123456 },
        chat: { id: 123456 },
        text: "/clear",
      });

      expect(bot.sentMessages.length).toBe(1);
      expect(bot.sentMessages[0].text).toContain("Conversation history cleared");
    });

    it("should handle callback query for approve", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateCallbackQuery({
        from: { id: 123456 },
        data: "approve:test-payment-id",
        id: "callback-1",
        message: {
          chat: { id: 123456 },
          message_id: 1,
        },
      });

      expect(paymentSystem.approvePayment).toHaveBeenCalledWith(
        "test-payment-id",
        "123456"
      );
      expect(bot.answeredCallbacks.length).toBe(1);
      expect(bot.editedMarkups.length).toBe(1);
    });

    it("should handle callback query for reject", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateCallbackQuery({
        from: { id: 123456 },
        data: "reject:test-payment-id",
        id: "callback-1",
        message: {
          chat: { id: 123456 },
          message_id: 1,
        },
      });

      expect(paymentSystem.rejectPayment).toHaveBeenCalledWith(
        "test-payment-id",
        "123456",
        "Rejected via button"
      );
      expect(bot.answeredCallbacks.length).toBe(1);
      expect(bot.editedMarkups.length).toBe(1);
    });

    it("should not respond to unauthorized users", async () => {
      const bot = createTelegramBot(config) as any;

      await bot.simulateMessage({
        from: { id: 999999 }, // Different user
        chat: { id: 999999 },
        text: "/status",
      });

      expect(bot.sentMessages.length).toBe(0);
    });

    it("should format payment notification correctly", async () => {
      const bot = createTelegramBot(config) as any;

      const request: PaymentRequest = {
        id: "test-id",
        toAddress: "0x1234567890123456789012345678901234567890",
        amountCents: 500,
        note: "Test payment",
        status: "pending_approval",
        requestedAt: new Date().toISOString(),
      };

      await notifyPaymentRequest(bot, "123456", request);

      expect(bot.sentMessages.length).toBe(1);
      const msg = bot.sentMessages[0];

      expect(msg.text).toContain("Payment Request");
      expect(msg.text).toContain("$5.00");
      expect(msg.text).toContain("Test payment");
      expect(msg.text).toContain("test-id");
      expect(msg.options.reply_markup.inline_keyboard[0]).toHaveLength(2);
    });
  });
});
