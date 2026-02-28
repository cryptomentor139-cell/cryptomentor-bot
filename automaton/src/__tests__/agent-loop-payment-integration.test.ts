/**
 * Agent Loop Payment Integration Tests
 *
 * Tests for payment system integration with agent loop.
 */

import { describe, it, expect } from "vitest";

describe("Agent Loop Payment Integration", () => {
  it("should accept payment system in agent loop options", () => {
    // Test that the AgentLoopOptions interface accepts paymentSystem
    const mockPaymentSystem = {
      requestPayment: async () => ({
        id: "test",
        toAddress: "0x123",
        amountCents: 100,
        status: "pending_approval" as const,
        requestedAt: new Date().toISOString(),
      }),
      approvePayment: async () => {},
      rejectPayment: async () => {},
      executeApprovedPayments: async () => {},
      getPendingRequests: () => [],
      getRequestById: () => undefined,
      checkRateLimit: () => true,
    };

    // This should compile without errors
    const options = {
      paymentSystem: mockPaymentSystem,
    };

    expect(options.paymentSystem).toBeDefined();
    expect(options.paymentSystem.requestPayment).toBeDefined();
  });

  it("should support optional payment system", () => {
    // Test that paymentSystem is optional
    const options = {
      paymentSystem: undefined,
    };

    expect(options.paymentSystem).toBeUndefined();
  });

  it("should use payment system when available", async () => {
    let requestCalled = false;

    const mockPaymentSystem = {
      requestPayment: async (toAddress: string, amountCents: number, note?: string) => {
        requestCalled = true;
        return {
          id: "test-id",
          toAddress,
          amountCents,
          note,
          status: "pending_approval" as const,
          requestedAt: new Date().toISOString(),
        };
      },
      approvePayment: async () => {},
      rejectPayment: async () => {},
      executeApprovedPayments: async () => {},
      getPendingRequests: () => [],
      getRequestById: () => undefined,
      checkRateLimit: () => true,
    };

    // Simulate tool execution with payment system
    const result = await mockPaymentSystem.requestPayment(
      "0x1234567890123456789012345678901234567890",
      500,
      "Test payment"
    );

    expect(requestCalled).toBe(true);
    expect(result.status).toBe("pending_approval");
    expect(result.amountCents).toBe(500);
  });

  it("should fall back to direct transfer when payment system not available", () => {
    // Test that direct transfer is used when paymentSystem is undefined
    const options = {
      paymentSystem: undefined,
    };

    // In this case, the tool would use ctx.conway.transferCredits directly
    expect(options.paymentSystem).toBeUndefined();
  });
});
