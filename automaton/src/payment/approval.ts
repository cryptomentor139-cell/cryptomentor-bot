import { ulid } from "ulid";
import type {
  AutomatonDatabase,
  PaymentRequest,
  PaymentStatus,
  ConwayClient,
} from "../types.js";

export interface PaymentApprovalSystem {
  requestPayment(
    toAddress: string,
    amountCents: number,
    note?: string
  ): Promise<PaymentRequest>;
  approvePayment(requestId: string, reviewedBy: string): Promise<void>;
  rejectPayment(
    requestId: string,
    reviewedBy: string,
    reason: string
  ): Promise<void>;
  executeApprovedPayments(): Promise<void>;
  getPendingRequests(): PaymentRequest[];
  getRequestById(id: string): PaymentRequest | undefined;
  checkRateLimit(): boolean;
}

export interface PaymentApprovalConfig {
  autoApproveThreshold: number; // cents
  rateLimitPerHour: number;
}

export function createPaymentApprovalSystem(
  db: AutomatonDatabase,
  conway: ConwayClient,
  config: PaymentApprovalConfig
): PaymentApprovalSystem {
  async function requestPayment(
    toAddress: string,
    amountCents: number,
    note?: string
  ): Promise<PaymentRequest> {
    // Check rate limit
    if (!checkRateLimit()) {
      throw new Error("Payment rate limit exceeded");
    }

    const id = ulid();
    const request: PaymentRequest = {
      id,
      toAddress,
      amountCents,
      note,
      status: "pending_approval",
      requestedAt: new Date().toISOString(),
    };

    // Auto-approve if below threshold
    if (
      config.autoApproveThreshold > 0 &&
      amountCents <= config.autoApproveThreshold
    ) {
      request.status = "approved";
      request.reviewedAt = new Date().toISOString();
      request.reviewedBy = "auto";
    }

    db.insertPaymentRequest(request);

    // Log audit trail
    db.insertTransaction({
      id: ulid(),
      type: "payment_request",
      amountCents,
      description: `Payment request to ${toAddress}: ${note || "no note"}`,
      timestamp: new Date().toISOString(),
    });

    return request;
  }

  async function approvePayment(
    requestId: string,
    reviewedBy: string
  ): Promise<void> {
    const request = db.getPaymentRequestById(requestId);
    if (!request) throw new Error("Payment request not found");
    if (request.status !== "pending_approval") {
      throw new Error(`Cannot approve payment in status: ${request.status}`);
    }

    db.updatePaymentRequest(requestId, {
      status: "approved",
      reviewedAt: new Date().toISOString(),
      reviewedBy,
    });
  }

  async function rejectPayment(
    requestId: string,
    reviewedBy: string,
    reason: string
  ): Promise<void> {
    const request = db.getPaymentRequestById(requestId);
    if (!request) throw new Error("Payment request not found");
    if (request.status !== "pending_approval") {
      throw new Error(`Cannot reject payment in status: ${request.status}`);
    }

    db.updatePaymentRequest(requestId, {
      status: "rejected",
      reviewedAt: new Date().toISOString(),
      reviewedBy,
      rejectionReason: reason,
    });

    // Log rejection
    db.insertTransaction({
      id: ulid(),
      type: "payment_rejected",
      amountCents: request.amountCents,
      description: `Payment rejected: ${reason}`,
      timestamp: new Date().toISOString(),
    });
  }

  async function executeApprovedPayments(): Promise<void> {
    const approved = db.getPaymentRequestsByStatus("approved");

    for (const request of approved) {
      try {
        const result = await conway.transferCredits(
          request.toAddress,
          request.amountCents,
          request.note
        );

        db.updatePaymentRequest(request.id, {
          status: "executed",
          executionResult: JSON.stringify(result),
          executedAt: new Date().toISOString(),
        });

        // Log successful transfer
        db.insertTransaction({
          id: ulid(),
          type: "transfer_out",
          amountCents: request.amountCents,
          balanceAfterCents: result.balanceAfterCents,
          description: `Transfer to ${request.toAddress}: ${request.note || ""}`,
          timestamp: new Date().toISOString(),
        });
      } catch (error: any) {
        db.updatePaymentRequest(request.id, {
          status: "failed",
          executionResult: error.message,
          executedAt: new Date().toISOString(),
        });
      }
    }
  }

  function getPendingRequests(): PaymentRequest[] {
    return db.getPaymentRequestsByStatus("pending_approval");
  }

  function getRequestById(id: string): PaymentRequest | undefined {
    return db.getPaymentRequestById(id);
  }

  function checkRateLimit(): boolean {
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();
    const recentRequests = db.getPaymentRequestsSince(oneHourAgo);
    return recentRequests.length < config.rateLimitPerHour;
  }

  return {
    requestPayment,
    approvePayment,
    rejectPayment,
    executeApprovedPayments,
    getPendingRequests,
    getRequestById,
    checkRateLimit,
  };
}
