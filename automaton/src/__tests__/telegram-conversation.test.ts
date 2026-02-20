/**
 * Unit Tests for Telegram Conversational Interface
 *
 * Tests conversation handler functionality, message handling,
 * history management, and message splitting.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  TelegramConversationHandler,
  TaskProgressTracker,
} from "../telegram/conversation.js";
import type { AutomatonDatabase } from "../types.js";
import type { InferenceClient } from "../types.js";

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
      content: "Test response from AI",
      usage: { totalTokens: 100 },
    }),
  } as any;
}

describe("TelegramConversationHandler", () => {
  let bot: any;
  let db: AutomatonDatabase;
  let inference: InferenceClient;
  let handler: TelegramConversationHandler;

  beforeEach(() => {
    bot = createMockBot();
    db = createMockDb();
    inference = createMockInference();
    handler = new TelegramConversationHandler(bot, db, inference);
  });

  describe("handleMessage", () => {
    it("should handle user message and generate response", async () => {
      const msg = {
        chat: { id: 123 },
        from: { id: 456 },
        text: "Hello, how are you?",
      } as any;

      await handler.handleMessage(msg);

      // Should send typing indicator
      expect(bot.sendChatAction).toHaveBeenCalledWith(123, "typing");

      // Should call inference
      expect(inference.chat).toHaveBeenCalled();

      // Should send response
      expect(bot.sendMessage).toHaveBeenCalledWith(
        123,
        expect.stringContaining("Test response"),
        expect.any(Object)
      );
    });

    it("should maintain conversation history", async () => {
      const msg1 = {
        chat: { id: 123 },
        from: { id: 456 },
        text: "First message",
      } as any;

      const msg2 = {
        chat: { id: 123 },
        from: { id: 456 },
        text: "Second message",
      } as any;

      await handler.handleMessage(msg1);
      await handler.handleMessage(msg2);

      // Check history was saved
      const history = JSON.parse(db.getKV("telegram_history_123") || "[]");

      expect(history.length).toBeGreaterThan(2); // User + assistant messages
      expect(history[0].content).toBe("First message");
      expect(history[0].role).toBe("user");
    });

    it("should trim history when exceeds max length", async () => {
      // Add 25 messages (exceeds maxHistoryLength of 20)
      for (let i = 0; i < 25; i++) {
        const msg = {
          chat: { id: 123 },
          from: { id: 456 },
          text: `Message ${i}`,
        } as any;

        await handler.handleMessage(msg);
      }

      const history = JSON.parse(db.getKV("telegram_history_123") || "[]");

      // Should be trimmed to 20
      expect(history.length).toBeLessThanOrEqual(20);
    });

    it("should handle inference errors gracefully", async () => {
      const errorInference = {
        chat: vi.fn().mockRejectedValue(new Error("API error")),
      } as any;

      const errorHandler = new TelegramConversationHandler(
        bot,
        db,
        errorInference
      );

      const msg = {
        chat: { id: 123 },
        from: { id: 456 },
        text: "Test message",
      } as any;

      await errorHandler.handleMessage(msg);

      // Should send error message
      expect(bot.sendMessage).toHaveBeenCalledWith(
        123,
        expect.stringContaining("Error: API error")
      );
    });
  });

  describe("splitMessage", () => {
    it("should not split short messages", () => {
      const shortText = "This is a short message";
      const chunks = handler.splitMessage(shortText, 4000);

      expect(chunks.length).toBe(1);
      expect(chunks[0]).toBe(shortText);
    });

    it("should split long messages into chunks", () => {
      const longText = "A".repeat(5000);
      const chunks = handler.splitMessage(longText, 4000);

      expect(chunks.length).toBeGreaterThan(1);

      // Each chunk should be within limit
      for (const chunk of chunks) {
        expect(chunk.length).toBeLessThanOrEqual(4000);
      }
    });

    it("should split by paragraphs first", () => {
      const text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3";
      const chunks = handler.splitMessage(text, 20);

      // Should split at paragraph boundaries
      expect(chunks.length).toBeGreaterThan(1);
    });

    it("should split by sentences if paragraph too long", () => {
      const text = "Sentence one. Sentence two. Sentence three.";
      const chunks = handler.splitMessage(text, 20);

      expect(chunks.length).toBeGreaterThan(1);
    });
  });

  describe("clearHistory", () => {
    it("should clear conversation history", async () => {
      const msg = {
        chat: { id: 123 },
        from: { id: 456 },
        text: "Test message",
      } as any;

      await handler.handleMessage(msg);

      // Verify history exists
      expect(db.getKV("telegram_history_123")).toBeDefined();

      // Clear history
      handler.clearHistory(123);

      // Verify history cleared
      expect(db.getKV("telegram_history_123")).toBeUndefined();
    });
  });

  describe("system prompt generation", () => {
    it("should include automaton context in system prompt", async () => {
      const msg = {
        chat: { id: 123 },
        from: { id: 456 },
        text: "What's your status?",
      } as any;

      await handler.handleMessage(msg);

      // Check inference was called with system prompt
      expect(inference.chat).toHaveBeenCalledWith(
        expect.arrayContaining([
          expect.objectContaining({
            role: "system",
            content: expect.stringContaining("TestBot"),
          }),
        ]),
        expect.any(Object)
      );
    });
  });
});

describe("TaskProgressTracker", () => {
  let bot: any;
  let tracker: TaskProgressTracker;

  beforeEach(() => {
    bot = createMockBot();
    tracker = new TaskProgressTracker(bot, 123);
  });

  it("should start task and return message ID", async () => {
    const messageId = await tracker.startTask("Test task");

    expect(bot.sendMessage).toHaveBeenCalledWith(
      123,
      expect.stringContaining("Starting task: Test task")
    );
    expect(messageId).toBe(1);
  });

  it("should update progress", async () => {
    await tracker.updateProgress(1, "Processing...");

    expect(bot.editMessageText).toHaveBeenCalledWith(
      expect.stringContaining("Processing..."),
      expect.objectContaining({
        chat_id: 123,
        message_id: 1,
      })
    );
  });

  it("should complete task", async () => {
    await tracker.completeTask(1, "Task completed successfully");

    expect(bot.editMessageText).toHaveBeenCalledWith(
      expect.stringContaining("Task completed successfully"),
      expect.any(Object)
    );
  });

  it("should fail task", async () => {
    await tracker.failTask(1, "Something went wrong");

    expect(bot.editMessageText).toHaveBeenCalledWith(
      expect.stringContaining("Task failed: Something went wrong"),
      expect.any(Object)
    );
  });
});
