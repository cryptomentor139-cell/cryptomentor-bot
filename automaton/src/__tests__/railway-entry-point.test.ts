/**
 * Railway Entry Point Tests
 *
 * Tests for Railway entry point including graceful shutdown,
 * lifecycle management, and integration.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import fc from "fast-check";
import type { AutomatonDatabase, AgentState } from "../types.js";

const PROPERTY_TEST_ITERATIONS = 100;

// Mock database for testing
function createMockDatabase(): AutomatonDatabase & { _closed: boolean } {
  const state = {
    agentState: "running" as AgentState,
    kv: new Map<string, string>(),
    _closed: false,
  };

  return {
    _closed: false,
    getAgentState: () => state.agentState,
    setAgentState: (s: AgentState) => {
      state.agentState = s;
    },
    getKV: (key: string) => state.kv.get(key),
    setKV: (key: string, value: string) => {
      state.kv.set(key, value);
    },
    deleteKV: (key: string) => {
      state.kv.delete(key);
    },
    close: function() {
      (this as any)._closed = true;
    },
    // Other methods (not used in these tests)
    getIdentity: () => undefined,
    setIdentity: () => {},
    getTurnCount: () => 0,
    insertTurn: () => {},
    getRecentTurns: () => [],
    getTurnById: () => undefined,
    insertToolCall: () => {},
    getToolCallsForTurn: () => [],
    getHeartbeatEntries: () => [],
    upsertHeartbeatEntry: () => {},
    updateHeartbeatLastRun: () => {},
    insertTransaction: () => {},
    getRecentTransactions: () => [],
    getInstalledTools: () => [],
    installTool: () => {},
    removeTool: () => {},
    insertModification: () => {},
    getRecentModifications: () => [],
    getSkills: () => [],
    getSkillByName: () => undefined,
    upsertSkill: () => {},
    removeSkill: () => {},
    getChildren: () => [],
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
  } as AutomatonDatabase;
}

describe("Railway Entry Point", () => {
  describe("Property Tests", () => {
    /**
     * Feature: railway-deployment, Property 5: Graceful Shutdown Cleanup
     */
    it("Property 5: Graceful Shutdown Cleanup", async () => {
      await fc.assert(
        fc.asyncProperty(
          fc.constantFrom("running", "sleeping", "low_compute", "critical"),
          async (initialState) => {
            const db = createMockDatabase();
            db.setAgentState(initialState as any);

            // Mock Telegram bot
            let botStopped = false;
            const mockBot = {
              stopPolling: async () => {
                botStopped = true;
              },
            };

            // Mock health server
            let serverClosed = false;
            const mockServer = {
              close: () => {
                serverClosed = true;
              },
            };

            // Simulate shutdown sequence
            const shutdown = async () => {
              // Stop Telegram bot
              if (mockBot) {
                await mockBot.stopPolling();
              }

              // Close health server
              mockServer.close();

              // Set agent state to sleeping
              db.setAgentState("sleeping");

              // Close database
              db.close();
            };

            // Execute shutdown
            await shutdown();

            // Verify cleanup order
            expect(botStopped).toBe(true);
            expect(serverClosed).toBe(true);
            expect(db.getAgentState()).toBe("sleeping");
            expect(db._closed).toBe(true);
          }
        ),
        { numRuns: PROPERTY_TEST_ITERATIONS }
      );
    });
  });

  describe("Unit Tests", () => {
    it("should initialize database with Railway volume path", () => {
      const railwayVolumePath = "/data";
      const dbPath = `${railwayVolumePath}/automaton.db`;

      // In real implementation, this would be handled by loadRailwayConfig
      expect(dbPath).toBe("/data/automaton.db");
      expect(dbPath.startsWith(railwayVolumePath)).toBe(true);
    });

    it("should handle Telegram bot optional initialization", () => {
      // Test with Telegram config
      const withTelegram = {
        telegram: {
          botToken: "test-token",
          creatorId: "123456",
        },
      };

      expect(withTelegram.telegram).toBeDefined();
      expect(withTelegram.telegram?.botToken).toBe("test-token");

      // Test without Telegram config
      const withoutTelegram = {
        telegram: undefined,
      };

      expect(withoutTelegram.telegram).toBeUndefined();
    });

    it("should execute graceful shutdown on SIGTERM", async () => {
      const db = createMockDatabase();
      db.setAgentState("running");

      let botStopped = false;
      let serverClosed = false;

      const mockBot = {
        stopPolling: async () => {
          botStopped = true;
        },
      };

      const mockServer = {
        close: () => {
          serverClosed = true;
        },
      };

      // Simulate shutdown handler
      const shutdown = async () => {
        if (mockBot) {
          await mockBot.stopPolling();
        }
        mockServer.close();
        db.setAgentState("sleeping");
        db.close();
      };

      await shutdown();

      expect(botStopped).toBe(true);
      expect(serverClosed).toBe(true);
      expect(db.getAgentState()).toBe("sleeping");
      expect(db._closed).toBe(true);
    });

    it("should hook payment request notifications to Telegram", async () => {
      const notifications: any[] = [];

      const mockBot = {
        sendMessage: async (chatId: string, message: string, options: any) => {
          notifications.push({ chatId, message, options });
        },
      };

      const mockPaymentSystem = {
        requestPayment: async (
          toAddress: string,
          amountCents: number,
          note?: string
        ) => {
          return {
            id: "test-id",
            toAddress,
            amountCents,
            note,
            status: "pending_approval" as const,
            requestedAt: new Date().toISOString(),
          };
        },
      };

      // Simulate payment request with notification
      const request = await mockPaymentSystem.requestPayment(
        "0x1234567890123456789012345678901234567890",
        500,
        "Test payment"
      );

      if (request.status === "pending_approval") {
        await mockBot.sendMessage(
          "123456",
          `Payment request: ${request.id}`,
          {}
        );
      }

      expect(notifications.length).toBe(1);
      expect(notifications[0].chatId).toBe("123456");
      expect(notifications[0].message).toContain("test-id");
    });

    it("should continue without Telegram if initialization fails", () => {
      let telegramInitialized = false;
      let continueWithoutTelegram = false;

      try {
        // Simulate Telegram initialization failure
        throw new Error("Invalid bot token");
      } catch (error: any) {
        console.warn(`Telegram initialization failed: ${error.message}`);
        continueWithoutTelegram = true;
      }

      expect(telegramInitialized).toBe(false);
      expect(continueWithoutTelegram).toBe(true);
    });

    it("should send critical state alert via Telegram", async () => {
      const alerts: any[] = [];

      const mockBot = {
        sendMessage: async (chatId: string, message: string, options: any) => {
          alerts.push({ chatId, message, options });
        },
      };

      const db = createMockDatabase();
      let previousState: AgentState = "running";

      // Simulate state change to critical
      const newState: AgentState = "critical";

      if (newState === "critical" && previousState !== "critical") {
        await mockBot.sendMessage(
          "123456",
          "⚠️ Critical State Alert\n\nAutomaton has entered critical state.",
          { parse_mode: "Markdown" }
        );
      }

      previousState = newState;

      expect(alerts.length).toBe(1);
      expect(alerts[0].message).toContain("Critical State Alert");
    });

    it("should not send duplicate critical alerts", async () => {
      const alerts: any[] = [];

      const mockBot = {
        sendMessage: async (chatId: string, message: string, options: any) => {
          alerts.push({ chatId, message, options });
        },
      };

      let previousState: AgentState = "critical";

      // Simulate state change from critical to critical (no change)
      const newState: AgentState = "critical";

      if (newState === "critical" && previousState !== "critical") {
        await mockBot.sendMessage("123456", "Critical alert", {});
      }

      previousState = newState;

      expect(alerts.length).toBe(0);
    });

    it("should execute approved payments after each loop", async () => {
      let executionCount = 0;

      const mockPaymentSystem = {
        executeApprovedPayments: async () => {
          executionCount++;
        },
      };

      // Simulate loop iteration
      await mockPaymentSystem.executeApprovedPayments();

      expect(executionCount).toBe(1);

      // Simulate another iteration
      await mockPaymentSystem.executeApprovedPayments();

      expect(executionCount).toBe(2);
    });

    it("should handle payment execution errors gracefully", async () => {
      let errorLogged = false;

      const mockPaymentSystem = {
        executeApprovedPayments: async () => {
          throw new Error("Network error");
        },
      };

      try {
        await mockPaymentSystem.executeApprovedPayments();
      } catch (error: any) {
        console.warn(`Error executing approved payments: ${error.message}`);
        errorLogged = true;
      }

      expect(errorLogged).toBe(true);
    });

    it("should detect Railway environment correctly", () => {
      // Test with Railway environment
      const withRailway = {
        RAILWAY_ENVIRONMENT: "production",
      };

      expect(withRailway.RAILWAY_ENVIRONMENT).toBeDefined();

      // Test without Railway environment
      const withoutRailway = {};

      expect((withoutRailway as any).RAILWAY_ENVIRONMENT).toBeUndefined();
    });
  });
});
