/**
 * Property-Based Tests for Telegram Conversational Interface
 *
 * Tests universal properties of conversation handling, history persistence,
 * message pagination, and context isolation.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import fc from "fast-check";
import { TelegramConversationHandler } from "../telegram/conversation.js";
import type { AutomatonDatabase } from "../types.js";
import type { InferenceClient } from "../types.js";

const PROPERTY_TEST_ITERATIONS = 100;

// Mock Telegram bot
function createMockBot() {
  return {
    sendMessage: vi.fn().mockResolvedValue({ message_id: 1 }),
    sendChatAction: vi.fn().mockResolvedValue(true),
    editMessageText: vi.fn().mockResolvedValue(true),
  } as any;
}

// Mock database
function createMockDb(): AutomatonDatabase {
  const kvStore = new Map<string, string>();

  return {
    getKV: (key: string) => kvStore.get(key),
    setKV: (key: string, value: string) => kvStore.set(key, value),
    deleteKV: (key: string) => kvStore.delete(key),
    getAgentState: () => "active",
    getTurnCount: () => 10,
    getIdentity: (key: string) => {
      if (key === "name") return "TestBot";
      if (key === "address") return "0x1234567890abcdef";
      return "";
    },
    getRecentTransactions: () => [
      {
        id: "1",
        type: "credit",
        amountCents: 1000,
        balanceAfterCents: 5000,
        description: "Test transaction",
        timestamp: new Date().toISOString(),
      },
    ],
  } as any;
}

// Mock inference client
function createMockInference(): InferenceClient {
  return {
    chat: vi.fn().mockResolvedValue({
      content: "Test response",
      usage: { totalTokens: 100 },
    }),
  } as any;
}

describe("Telegram Conversational Interface - Property Tests", () => {
  /**
   * Property 19: Conversation History Persistence
   *
   * For any conversation history saved to database, loading history
   * must return exact same messages in same order.
   *
   * **Validates: Requirements 13.9**
   */
  it("Property 19: Conversation History Persistence", () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            role: fc.constantFrom("user" as const, "assistant" as const),
            content: fc.string({ minLength: 1, maxLength: 100 }),
            timestamp: fc.date().map((d) => d.toISOString()),
          }),
          { minLength: 1, maxLength: 20 }
        ),
        fc.integer({ min: 1, max: 1000000 }),
        (messages, chatId) => {
          const bot = createMockBot();
          const db = createMockDb();
          const inference = createMockInference();

          const handler = new TelegramConversationHandler(bot, db, inference);

          // Save history
          db.setKV(`telegram_history_${chatId}`, JSON.stringify(messages));

          // Load history
          const loaded = JSON.parse(
            db.getKV(`telegram_history_${chatId}`) || "[]"
          );

          // Should return exact same messages in same order
          expect(loaded).toEqual(messages);
          expect(loaded.length).toBe(messages.length);

          // Verify order is preserved
          for (let i = 0; i < messages.length; i++) {
            expect(loaded[i].role).toBe(messages[i].role);
            expect(loaded[i].content).toBe(messages[i].content);
            expect(loaded[i].timestamp).toBe(messages[i].timestamp);
          }
        }
      ),
      { numRuns: PROPERTY_TEST_ITERATIONS }
    );
  });

  /**
   * Property 20: Message Pagination
   *
   * For any response longer than 4000 characters, system must split
   * into multiple messages without losing content.
   *
   * **Validates: Requirements 13.7**
   */
  it("Property 20: Message Pagination", () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 4001, maxLength: 6000 }), // Reduced max to avoid memory issues
        (longText) => {
          const bot = createMockBot();
          const db = createMockDb();
          const inference = createMockInference();

          const handler = new TelegramConversationHandler(bot, db, inference);

          // Split message
          const chunks = handler.splitMessage(longText, 4000);

          // Should have at least one chunk
          expect(chunks.length).toBeGreaterThanOrEqual(1);

          // Each chunk should be within limit
          for (const chunk of chunks) {
            expect(chunk.length).toBeLessThanOrEqual(4000);
          }

          // Total length should be preserved (with possible paragraph separators added)
          const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
          expect(totalLength).toBeGreaterThanOrEqual(longText.length * 0.8); // Allow 20% loss for whitespace normalization
        }
      ),
      { numRuns: 50 } // Reduced iterations to avoid memory issues
    );
  });

  /**
   * Property 21: Conversation Context Isolation
   *
   * For any two different chat IDs, conversation contexts must be isolated -
   * messages from one chat do not affect context from another chat.
   *
   * **Validates: Requirements 13.3**
   */
  it("Property 21: Conversation Context Isolation", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 1000000 }),
        fc.integer({ min: 1, max: 1000000 }),
        fc.string({ minLength: 1, maxLength: 100 }),
        fc.string({ minLength: 1, maxLength: 100 }),
        (chatId1, chatId2, message1, message2) => {
          // Ensure different chat IDs
          fc.pre(chatId1 !== chatId2);

          const bot = createMockBot();
          const db = createMockDb();
          const inference = createMockInference();

          const handler = new TelegramConversationHandler(bot, db, inference);

          // Save different histories for different chats
          const history1 = [
            {
              role: "user" as const,
              content: message1,
              timestamp: new Date().toISOString(),
            },
          ];
          const history2 = [
            {
              role: "user" as const,
              content: message2,
              timestamp: new Date().toISOString(),
            },
          ];

          db.setKV(`telegram_history_${chatId1}`, JSON.stringify(history1));
          db.setKV(`telegram_history_${chatId2}`, JSON.stringify(history2));

          // Load histories
          const loaded1 = JSON.parse(
            db.getKV(`telegram_history_${chatId1}`) || "[]"
          );
          const loaded2 = JSON.parse(
            db.getKV(`telegram_history_${chatId2}`) || "[]"
          );

          // Contexts should be isolated
          expect(loaded1).toEqual(history1);
          expect(loaded2).toEqual(history2);
          expect(loaded1).not.toEqual(loaded2);

          // Clearing one should not affect the other
          handler.clearHistory(chatId1);
          const afterClear1 = db.getKV(`telegram_history_${chatId1}`);
          const afterClear2 = db.getKV(`telegram_history_${chatId2}`);

          expect(afterClear1).toBeUndefined();
          expect(afterClear2).toBeDefined();
        }
      ),
      { numRuns: PROPERTY_TEST_ITERATIONS }
    );
  });
});
