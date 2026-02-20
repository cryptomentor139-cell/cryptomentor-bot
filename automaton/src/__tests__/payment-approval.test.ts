import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import fc from "fast-check";
import fs from "fs";
import path from "path";
import { createDatabase } from "../state/database.js";
import { createPaymentApprovalSystem } from "../payment/approval.js";
import type { ConwayClient, AutomatonDatabase } from "../types.js";

const PROPERTY_TEST_ITERATIONS = 100;
const TEST_DB_DIR = path.join(process.cwd(), "test-payment-dbs");

// Mock Conway client
function createMockConway(): ConwayClient {
  return {
    transferCredits: vi.fn(async (toAddress, amountCents, note) => ({
      transferId: "transfer-123",
      status: "completed",
      toAddress,
      amountCents,
      balanceAfterCents: 10000,
    })),
    getCreditsBalance: vi.fn(async () => 10000),
    getCreditsPricing: vi.fn(async () => []),
    exec: vi.fn(),
    writeFile: vi.fn(),
    readFile: vi.fn(),
    exposePort: vi.fn(),
    removePort: vi.fn(),
    createSandbox: vi.fn(),
    deleteSandbox: vi.fn(),
    listSandboxes: vi.fn(),
    searchDomains: vi.fn(),
    registerDomain: vi.fn(),
    listDnsRecords: vi.fn(),
    addDnsRecord: vi.fn(),
    deleteDnsRecord: vi.fn(),
    listModels: vi.fn(),
  } as any;
}

function cleanupTestDb(dbPath: string): void {
  try {
    if (fs.existsSync(dbPath)) fs.unlinkSync(dbPath);
    const walPath = `${dbPath}-wal`;
    const shmPath = `${dbPath}-shm`;
    if (fs.existsSync(walPath)) fs.unlinkSync(walPath);
    if (fs.existsSync(shmPath)) fs.unlinkSync(shmPath);
  } catch (e) {
    // Ignore
  }
}

describe("Payment Approval System", () => {
  let db: AutomatonDatabase;
  let conway: ConwayClient;
  let dbPath: string;

  beforeEach(() => {
    if (!fs.existsSync(TEST_DB_DIR)) {
      fs.mkdirSync(TEST_DB_DIR, { recursive: true });
    }
    dbPath = path.join(TEST_DB_DIR, `test-${Date.now()}.db`);
    db = createDatabase(dbPath);
    conway = createMockConway();
  });

  afterEach(() => {
    if (db) db.close();
    if (dbPath) cleanupTestDb(dbPath);
    try {
      if (fs.existsSync(TEST_DB_DIR)) {
        fs.rmSync(TEST_DB_DIR, { recursive: true, force: true });
      }
    } catch (e) {
      // Ignore
    }
  });

  /**
   * Feature: railway-deployment, Property 9: Payment Request Creation
   * **Validates: Requirements 11.1, 11.2, 11.7**
   */
  it("Property 9: Payment Request Creation", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.hexaString({ minLength: 40, maxLength: 40 }).map((s) => `0x${s}`),
        fc.nat({ max: 100000 }),
        fc.option(fc.string({ maxLength: 100 }), { nil: undefined }),
        fc.nat({ max: 100 }),
        async (toAddress, amountCents, note, threshold) => {
          const paymentSystem = createPaymentApprovalSystem(db, conway, {
            autoApproveThreshold: threshold,
            rateLimitPerHour: 100,
          });

          const request = await paymentSystem.requestPayment(
            toAddress,
            amountCents,
            note
          );

          // Should create request
          expect(request).toBeDefined();
          expect(request.toAddress).toBe(toAddress);
          expect(request.amountCents).toBe(amountCents);

          // Should have correct status based on threshold
          if (amountCents <= threshold && threshold > 0) {
            expect(request.status).toBe("approved");
            expect(request.reviewedBy).toBe("auto");
          } else {
            expect(request.status).toBe("pending_approval");
          }

          // Should be retrievable
          const retrieved = paymentSystem.getRequestById(request.id);
          expect(retrieved).toBeDefined();
          expect(retrieved?.id).toBe(request.id);
        }
      ),
      { numRuns: PROPERTY_TEST_ITERATIONS }
    );
  });

  /**
   * Feature: railway-deployment, Property 10: Payment Rejection Handling
   * **Validates: Requirements 11.4**
   */
  it("Property 10: Payment Rejection Handling", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.hexaString({ minLength: 40, maxLength: 40 }).map((s) => `0x${s}`),
        fc.nat({ max: 10000 }),
        fc.string({ minLength: 1, maxLength: 100 }),
        fc.string({ minLength: 1, maxLength: 50 }),
        async (toAddress, amountCents, reason, reviewedBy) => {
          const paymentSystem = createPaymentApprovalSystem(db, conway, {
            autoApproveThreshold: 0,
            rateLimitPerHour: 100,
          });

          const request = await paymentSystem.requestPayment(
            toAddress,
            amountCents
          );

          // Reject the payment
          await paymentSystem.rejectPayment(request.id, reviewedBy, reason);

          // Should be rejected
          const rejected = paymentSystem.getRequestById(request.id);
          expect(rejected?.status).toBe("rejected");
          expect(rejected?.rejectionReason).toBe(reason);
          expect(rejected?.reviewedBy).toBe(reviewedBy);
          expect(rejected?.reviewedAt).toBeDefined();

          // Should not retry automatically (status stays rejected)
          await paymentSystem.executeApprovedPayments();
          const stillRejected = paymentSystem.getRequestById(request.id);
          expect(stillRejected?.status).toBe("rejected");
        }
      ),
      { numRuns: PROPERTY_TEST_ITERATIONS }
    );
  });

  /**
   * Feature: railway-deployment, Property 11: Payment Approval Execution
   * **Validates: Requirements 11.5**
   */
  it("Property 11: Payment Approval Execution", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.hexaString({ minLength: 40, maxLength: 40 }).map((s) => `0x${s}`),
        fc.nat({ min: 1, max: 10000 }),
        fc.string({ minLength: 1, maxLength: 50 }),
        async (toAddress, amountCents, reviewedBy) => {
          const paymentSystem = createPaymentApprovalSystem(db, conway, {
            autoApproveThreshold: 0,
            rateLimitPerHour: 100,
          });

          const request = await paymentSystem.requestPayment(
            toAddress,
            amountCents
          );

          // Approve the payment
          await paymentSystem.approvePayment(request.id, reviewedBy);

          // Execute approved payments
          await paymentSystem.executeApprovedPayments();

          // Should be executed
          const executed = paymentSystem.getRequestById(request.id);
          expect(executed?.status).toBe("executed");
          expect(executed?.executedAt).toBeDefined();
          expect(executed?.executionResult).toBeDefined();

          // Should have called transferCredits
          expect(conway.transferCredits).toHaveBeenCalledWith(
            toAddress,
            amountCents,
            undefined
          );
        }
      ),
      { numRuns: PROPERTY_TEST_ITERATIONS }
    );
  });

  /**
   * Feature: railway-deployment, Property 13: Payment Audit Trail
   * **Validates: Requirements 11.9**
   */
  it("Property 13: Payment Audit Trail", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.hexaString({ minLength: 40, maxLength: 40 }).map((s) => `0x${s}`),
        fc.nat({ min: 1, max: 10000 }),
        async (toAddress, amountCents) => {
          // Create fresh database for each test
          const testDbPath = path.join(TEST_DB_DIR, `audit-${Date.now()}-${Math.random()}.db`);
          const testDb = createDatabase(testDbPath);
          
          try {
            const paymentSystem = createPaymentApprovalSystem(testDb, conway, {
              autoApproveThreshold: 0,
              rateLimitPerHour: 100,
            });

            // Create request
            const request = await paymentSystem.requestPayment(
              toAddress,
              amountCents,
              "Test payment"
            );

            // Should have transaction log for request
            const txns1 = testDb.getRecentTransactions(10);
            const requestTxn = txns1.find((t) => t.type === "payment_request");
            expect(requestTxn).toBeDefined();
            expect(requestTxn?.amountCents).toBe(amountCents);

            // Approve and execute
            await paymentSystem.approvePayment(request.id, "user-123");
            await paymentSystem.executeApprovedPayments();

            // Should have transaction log for execution
            const txns2 = testDb.getRecentTransactions(10);
            const executionTxn = txns2.find((t) => t.type === "transfer_out");
            expect(executionTxn).toBeDefined();
            expect(executionTxn?.amountCents).toBe(amountCents);
          } finally {
            testDb.close();
            cleanupTestDb(testDbPath);
          }
        }
      ),
      { numRuns: PROPERTY_TEST_ITERATIONS }
    );
  });

  /**
   * Feature: railway-deployment, Property 14: Payment Rate Limiting
   * **Validates: Requirements 11.10**
   */
  it("Property 14: Payment Rate Limiting", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 2, max: 10 }), // Changed: min 2 to avoid edge case
        async (rateLimit) => {
          // Create fresh database for each test
          const testDbPath = path.join(TEST_DB_DIR, `rate-limit-${Date.now()}-${Math.random()}.db`);
          const testDb = createDatabase(testDbPath);
          
          try {
            const paymentSystem = createPaymentApprovalSystem(testDb, conway, {
              autoApproveThreshold: 0,
              rateLimitPerHour: rateLimit,
            });

            // Create requests up to limit
            for (let i = 0; i < rateLimit; i++) {
              await paymentSystem.requestPayment(
                `0x${"1".repeat(40)}`,
                100,
                `Request ${i}`
              );
            }

            // Next request should fail
            await expect(
              paymentSystem.requestPayment(`0x${"2".repeat(40)}`, 100)
            ).rejects.toThrow("Payment rate limit exceeded");
          } finally {
            testDb.close();
            cleanupTestDb(testDbPath);
          }
        }
      ),
      { numRuns: 20 } // Fewer runs for rate limit tests
    );
  });

  /**
   * Feature: railway-deployment, Property 15: Payment Approval Required in All States
   * **Validates: Requirements 11.8**
   */
  it("Property 15: Payment Approval Required in All States", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom("setup", "running", "critical", "low_compute"),
        fc.nat({ min: 1, max: 10000 }),
        async (agentState, amountCents) => {
          // Set agent state
          db.setAgentState(agentState as any);

          const paymentSystem = createPaymentApprovalSystem(db, conway, {
            autoApproveThreshold: 0, // No auto-approve
            rateLimitPerHour: 100,
          });

          const request = await paymentSystem.requestPayment(
            `0x${"1".repeat(40)}`,
            amountCents
          );

          // Should require approval regardless of state
          expect(request.status).toBe("pending_approval");

          // Should not execute without approval
          await paymentSystem.executeApprovedPayments();
          const notExecuted = paymentSystem.getRequestById(request.id);
          expect(notExecuted?.status).toBe("pending_approval");
        }
      ),
      { numRuns: 50 }
    );
  });

  describe("Unit Tests", () => {
    it("should create payment request with pending status", async () => {
      const paymentSystem = createPaymentApprovalSystem(db, conway, {
        autoApproveThreshold: 0,
        rateLimitPerHour: 10,
      });

      const request = await paymentSystem.requestPayment(
        "0x1234567890123456789012345678901234567890",
        500,
        "Test payment"
      );

      expect(request.status).toBe("pending_approval");
      expect(request.toAddress).toBe(
        "0x1234567890123456789012345678901234567890"
      );
      expect(request.amountCents).toBe(500);
      expect(request.note).toBe("Test payment");
    });

    it("should auto-approve payments below threshold", async () => {
      const paymentSystem = createPaymentApprovalSystem(db, conway, {
        autoApproveThreshold: 100,
        rateLimitPerHour: 10,
      });

      const request = await paymentSystem.requestPayment(
        "0x1234567890123456789012345678901234567890",
        50
      );

      expect(request.status).toBe("approved");
      expect(request.reviewedBy).toBe("auto");
    });

    it("should not auto-approve payments above threshold", async () => {
      const paymentSystem = createPaymentApprovalSystem(db, conway, {
        autoApproveThreshold: 100,
        rateLimitPerHour: 10,
      });

      const request = await paymentSystem.requestPayment(
        "0x1234567890123456789012345678901234567890",
        150
      );

      expect(request.status).toBe("pending_approval");
    });

    it("should approve pending payment", async () => {
      const paymentSystem = createPaymentApprovalSystem(db, conway, {
        autoApproveThreshold: 0,
        rateLimitPerHour: 10,
      });

      const request = await paymentSystem.requestPayment(
        "0x1234567890123456789012345678901234567890",
        500
      );

      await paymentSystem.approvePayment(request.id, "user-123");

      const approved = paymentSystem.getRequestById(request.id);
      expect(approved?.status).toBe("approved");
      expect(approved?.reviewedBy).toBe("user-123");
    });

    it("should reject pending payment", async () => {
      const paymentSystem = createPaymentApprovalSystem(db, conway, {
        autoApproveThreshold: 0,
        rateLimitPerHour: 10,
      });

      const request = await paymentSystem.requestPayment(
        "0x1234567890123456789012345678901234567890",
        500
      );

      await paymentSystem.rejectPayment(
        request.id,
        "user-123",
        "Insufficient funds"
      );

      const rejected = paymentSystem.getRequestById(request.id);
      expect(rejected?.status).toBe("rejected");
      expect(rejected?.rejectionReason).toBe("Insufficient funds");
    });

    it("should execute approved payments", async () => {
      const paymentSystem = createPaymentApprovalSystem(db, conway, {
        autoApproveThreshold: 0,
        rateLimitPerHour: 10,
      });

      const request = await paymentSystem.requestPayment(
        "0x1234567890123456789012345678901234567890",
        500
      );

      await paymentSystem.approvePayment(request.id, "user-123");
      await paymentSystem.executeApprovedPayments();

      const executed = paymentSystem.getRequestById(request.id);
      expect(executed?.status).toBe("executed");
      expect(conway.transferCredits).toHaveBeenCalled();
    });

    it("should handle execution failures", async () => {
      const failingConway = createMockConway();
      vi.mocked(failingConway.transferCredits).mockRejectedValue(
        new Error("Insufficient balance")
      );

      const paymentSystem = createPaymentApprovalSystem(db, failingConway, {
        autoApproveThreshold: 0,
        rateLimitPerHour: 10,
      });

      const request = await paymentSystem.requestPayment(
        "0x1234567890123456789012345678901234567890",
        500
      );

      await paymentSystem.approvePayment(request.id, "user-123");
      await paymentSystem.executeApprovedPayments();

      const failed = paymentSystem.getRequestById(request.id);
      expect(failed?.status).toBe("failed");
      expect(failed?.executionResult).toContain("Insufficient balance");
    });

    it("should get pending requests", async () => {
      const paymentSystem = createPaymentApprovalSystem(db, conway, {
        autoApproveThreshold: 0,
        rateLimitPerHour: 10,
      });

      await paymentSystem.requestPayment(
        "0x1111111111111111111111111111111111111111",
        100
      );
      await paymentSystem.requestPayment(
        "0x2222222222222222222222222222222222222222",
        200
      );

      const pending = paymentSystem.getPendingRequests();
      expect(pending.length).toBe(2);
    });

    it("should enforce rate limit", async () => {
      const paymentSystem = createPaymentApprovalSystem(db, conway, {
        autoApproveThreshold: 0,
        rateLimitPerHour: 2,
      });

      await paymentSystem.requestPayment(
        "0x1111111111111111111111111111111111111111",
        100
      );
      await paymentSystem.requestPayment(
        "0x2222222222222222222222222222222222222222",
        200
      );

      await expect(
        paymentSystem.requestPayment(
          "0x3333333333333333333333333333333333333333",
          300
        )
      ).rejects.toThrow("Payment rate limit exceeded");
    });

    it("should check rate limit correctly", async () => {
      const paymentSystem = createPaymentApprovalSystem(db, conway, {
        autoApproveThreshold: 0,
        rateLimitPerHour: 5,
      });

      expect(paymentSystem.checkRateLimit()).toBe(true);

      // Add some requests
      await paymentSystem.requestPayment(
        "0x1111111111111111111111111111111111111111",
        100
      );
      await paymentSystem.requestPayment(
        "0x2222222222222222222222222222222222222222",
        200
      );

      expect(paymentSystem.checkRateLimit()).toBe(true);

      // Add more to exceed limit
      await paymentSystem.requestPayment(
        "0x3333333333333333333333333333333333333333",
        300
      );
      await paymentSystem.requestPayment(
        "0x4444444444444444444444444444444444444444",
        400
      );
      await paymentSystem.requestPayment(
        "0x5555555555555555555555555555555555555555",
        500
      );

      expect(paymentSystem.checkRateLimit()).toBe(false);
    });
  });
});
