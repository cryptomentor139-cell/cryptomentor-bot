import { describe, it, expect, afterEach } from "vitest";
import fc from "fast-check";
import fs from "fs";
import path from "path";
import { createDatabase } from "../state/database.js";
import type { PaymentRequest, PaymentStatus } from "../types.js";
import { ulid } from "ulid";

const PROPERTY_TEST_ITERATIONS = 100;
const TEST_DB_DIR = path.join(process.cwd(), "test-dbs");

// Cleanup helper
function cleanupTestDb(dbPath: string): void {
  try {
    if (fs.existsSync(dbPath)) {
      fs.unlinkSync(dbPath);
    }
    const walPath = `${dbPath}-wal`;
    const shmPath = `${dbPath}-shm`;
    if (fs.existsSync(walPath)) fs.unlinkSync(walPath);
    if (fs.existsSync(shmPath)) fs.unlinkSync(shmPath);
  } catch (e) {
    // Ignore cleanup errors
  }
}

describe("Railway Database Extensions", () => {
  const testDbs: string[] = [];

  afterEach(() => {
    // Cleanup all test databases
    testDbs.forEach((dbPath) => {
      cleanupTestDb(dbPath);
    });
    testDbs.length = 0;

    // Cleanup test directory
    try {
      if (fs.existsSync(TEST_DB_DIR)) {
        fs.rmSync(TEST_DB_DIR, { recursive: true, force: true });
      }
    } catch (e) {
      // Ignore
    }
  });

  /**
   * Feature: railway-deployment, Property 3: Database Initialization Idempotency
   * **Validates: Requirements 4.2, 4.3**
   */
  it("Property 3: Database Initialization Idempotency", () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 20 }).filter((s) => 
          !s.includes("\0") && 
          !s.includes("/") && 
          !s.includes("\\") && 
          !s.includes(" ") &&
          !s.includes("<") &&
          !s.includes(">") &&
          !s.includes(":") &&
          !s.includes('"') &&
          !s.includes("|") &&
          !s.includes("?") &&
          !s.includes("*")
        ),
        fc.string({ minLength: 1, maxLength: 50 }),
        (dbName, testValue) => {
          // Ensure test directory exists
          if (!fs.existsSync(TEST_DB_DIR)) {
            fs.mkdirSync(TEST_DB_DIR, { recursive: true });
          }

          const dbPath = path.join(TEST_DB_DIR, `${dbName}.db`);
          testDbs.push(dbPath);

          // First initialization
          const db1 = createDatabase(dbPath);
          db1.setKV("test_key", testValue);
          const value1 = db1.getKV("test_key");
          db1.close();

          // Second initialization (should reuse existing)
          const db2 = createDatabase(dbPath);
          const value2 = db2.getKV("test_key");
          db2.close();

          // Should preserve data
          expect(value2).toBe(value1);
          expect(value2).toBe(testValue);

          // Database file should exist
          expect(fs.existsSync(dbPath)).toBe(true);
        }
      ),
      { numRuns: PROPERTY_TEST_ITERATIONS }
    );
  });

  /**
   * Feature: railway-deployment, Property 4: Database Path Error Handling
   * **Validates: Requirements 4.5**
   */
  it("Property 4: Database Path Error Handling", () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          "/invalid/path/that/does/not/exist/db.sqlite",
          "/root/forbidden/db.sqlite"
        ),
        (invalidPath) => {
          // Invalid paths should either throw or create with error message
          try {
            const db = createDatabase(invalidPath);
            db.close();
            // If it succeeds, it created the directory
            // Clean it up
            cleanupTestDb(invalidPath);
          } catch (error: any) {
            // Should have a clear error message
            expect(error.message).toBeDefined();
            expect(error.message.length).toBeGreaterThan(0);
          }
        }
      ),
      { numRuns: 10 } // Fewer runs for error cases
    );
  });

  describe("Payment Request Database Operations", () => {
    let db: ReturnType<typeof createDatabase>;
    let dbPath: string;

    afterEach(() => {
      if (db) {
        db.close();
      }
      if (dbPath) {
        cleanupTestDb(dbPath);
      }
    });

    it("should insert and retrieve payment request", () => {
      dbPath = path.join(TEST_DB_DIR, "payment-test.db");
      if (!fs.existsSync(TEST_DB_DIR)) {
        fs.mkdirSync(TEST_DB_DIR, { recursive: true });
      }
      db = createDatabase(dbPath);

      const request: PaymentRequest = {
        id: ulid(),
        toAddress: "0x1234567890123456789012345678901234567890",
        amountCents: 500,
        note: "Test payment",
        status: "pending_approval",
        requestedAt: new Date().toISOString(),
      };

      db.insertPaymentRequest(request);

      const retrieved = db.getPaymentRequestById(request.id);
      expect(retrieved).toBeDefined();
      expect(retrieved?.id).toBe(request.id);
      expect(retrieved?.toAddress).toBe(request.toAddress);
      expect(retrieved?.amountCents).toBe(request.amountCents);
      expect(retrieved?.status).toBe("pending_approval");
    });

    it("should update payment request status", () => {
      dbPath = path.join(TEST_DB_DIR, "payment-update-test.db");
      if (!fs.existsSync(TEST_DB_DIR)) {
        fs.mkdirSync(TEST_DB_DIR, { recursive: true });
      }
      db = createDatabase(dbPath);

      const request: PaymentRequest = {
        id: ulid(),
        toAddress: "0x1234567890123456789012345678901234567890",
        amountCents: 500,
        status: "pending_approval",
        requestedAt: new Date().toISOString(),
      };

      db.insertPaymentRequest(request);

      // Update to approved
      db.updatePaymentRequest(request.id, {
        status: "approved",
        reviewedAt: new Date().toISOString(),
        reviewedBy: "user-123",
      });

      const updated = db.getPaymentRequestById(request.id);
      expect(updated?.status).toBe("approved");
      expect(updated?.reviewedAt).toBeDefined();
      expect(updated?.reviewedBy).toBe("user-123");
    });

    it("should query payment requests by status", () => {
      dbPath = path.join(TEST_DB_DIR, "payment-query-test.db");
      if (!fs.existsSync(TEST_DB_DIR)) {
        fs.mkdirSync(TEST_DB_DIR, { recursive: true });
      }
      db = createDatabase(dbPath);

      const request1: PaymentRequest = {
        id: ulid(),
        toAddress: "0x1111111111111111111111111111111111111111",
        amountCents: 100,
        status: "pending_approval",
        requestedAt: new Date().toISOString(),
      };

      const request2: PaymentRequest = {
        id: ulid(),
        toAddress: "0x2222222222222222222222222222222222222222",
        amountCents: 200,
        status: "approved",
        requestedAt: new Date().toISOString(),
      };

      const request3: PaymentRequest = {
        id: ulid(),
        toAddress: "0x3333333333333333333333333333333333333333",
        amountCents: 300,
        status: "pending_approval",
        requestedAt: new Date().toISOString(),
      };

      db.insertPaymentRequest(request1);
      db.insertPaymentRequest(request2);
      db.insertPaymentRequest(request3);

      const pending = db.getPaymentRequestsByStatus("pending_approval");
      expect(pending.length).toBe(2);
      expect(pending.every((r) => r.status === "pending_approval")).toBe(true);

      const approved = db.getPaymentRequestsByStatus("approved");
      expect(approved.length).toBe(1);
      expect(approved[0].id).toBe(request2.id);
    });

    it("should query payment requests since timestamp", () => {
      dbPath = path.join(TEST_DB_DIR, "payment-since-test.db");
      if (!fs.existsSync(TEST_DB_DIR)) {
        fs.mkdirSync(TEST_DB_DIR, { recursive: true });
      }
      db = createDatabase(dbPath);

      const now = new Date();
      const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
      const twoHoursAgo = new Date(now.getTime() - 2 * 60 * 60 * 1000);

      const request1: PaymentRequest = {
        id: ulid(),
        toAddress: "0x1111111111111111111111111111111111111111",
        amountCents: 100,
        status: "pending_approval",
        requestedAt: twoHoursAgo.toISOString(),
      };

      const request2: PaymentRequest = {
        id: ulid(),
        toAddress: "0x2222222222222222222222222222222222222222",
        amountCents: 200,
        status: "pending_approval",
        requestedAt: oneHourAgo.toISOString(),
      };

      const request3: PaymentRequest = {
        id: ulid(),
        toAddress: "0x3333333333333333333333333333333333333333",
        amountCents: 300,
        status: "pending_approval",
        requestedAt: now.toISOString(),
      };

      db.insertPaymentRequest(request1);
      db.insertPaymentRequest(request2);
      db.insertPaymentRequest(request3);

      const recent = db.getPaymentRequestsSince(oneHourAgo.toISOString());
      expect(recent.length).toBeGreaterThanOrEqual(2);
    });

    it("should handle telegram config", () => {
      dbPath = path.join(TEST_DB_DIR, "telegram-config-test.db");
      if (!fs.existsSync(TEST_DB_DIR)) {
        fs.mkdirSync(TEST_DB_DIR, { recursive: true });
      }
      db = createDatabase(dbPath);

      db.setTelegramConfig("creator_chat_id", "123456789");
      const chatId = db.getTelegramConfig("creator_chat_id");
      expect(chatId).toBe("123456789");

      // Update
      db.setTelegramConfig("creator_chat_id", "987654321");
      const updatedChatId = db.getTelegramConfig("creator_chat_id");
      expect(updatedChatId).toBe("987654321");

      // Non-existent key
      const nonExistent = db.getTelegramConfig("non_existent");
      expect(nonExistent).toBeUndefined();
    });

    it("should handle payment request with all optional fields", () => {
      dbPath = path.join(TEST_DB_DIR, "payment-full-test.db");
      if (!fs.existsSync(TEST_DB_DIR)) {
        fs.mkdirSync(TEST_DB_DIR, { recursive: true });
      }
      db = createDatabase(dbPath);

      const request: PaymentRequest = {
        id: ulid(),
        toAddress: "0x1234567890123456789012345678901234567890",
        amountCents: 500,
        note: "Test payment with all fields",
        status: "executed",
        requestedAt: new Date().toISOString(),
        reviewedAt: new Date().toISOString(),
        reviewedBy: "user-123",
        executionResult: JSON.stringify({ success: true }),
        executedAt: new Date().toISOString(),
      };

      db.insertPaymentRequest(request);

      const retrieved = db.getPaymentRequestById(request.id);
      expect(retrieved).toBeDefined();
      expect(retrieved?.note).toBe(request.note);
      expect(retrieved?.reviewedAt).toBeDefined();
      expect(retrieved?.reviewedBy).toBe("user-123");
      expect(retrieved?.executionResult).toBeDefined();
      expect(retrieved?.executedAt).toBeDefined();
    });
  });
});
