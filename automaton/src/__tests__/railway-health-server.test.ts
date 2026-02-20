import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import fc from "fast-check";
import http from "http";
import { createHealthServer, type HealthStatus } from "../railway/health-server.js";
import type { AutomatonDatabase, AgentState } from "../types.js";

const PROPERTY_TEST_ITERATIONS = 100;

// Mock database
function createMockDatabase(state: AgentState = "running", turnCount: number = 0): AutomatonDatabase {
  return {
    getAgentState: vi.fn(() => state),
    getTurnCount: vi.fn(() => turnCount),
    getIdentity: vi.fn(),
    setIdentity: vi.fn(),
    insertTurn: vi.fn(),
    getRecentTurns: vi.fn(() => []),
    getTurnById: vi.fn(),
    insertToolCall: vi.fn(),
    getToolCallsForTurn: vi.fn(() => []),
    getHeartbeatEntries: vi.fn(() => []),
    upsertHeartbeatEntry: vi.fn(),
    updateHeartbeatLastRun: vi.fn(),
    insertTransaction: vi.fn(),
    getRecentTransactions: vi.fn(() => []),
    getInstalledTools: vi.fn(() => []),
    installTool: vi.fn(),
    removeTool: vi.fn(),
    insertModification: vi.fn(),
    getRecentModifications: vi.fn(() => []),
    getKV: vi.fn(),
    setKV: vi.fn(),
    deleteKV: vi.fn(),
    getSkills: vi.fn(() => []),
    getSkillByName: vi.fn(),
    upsertSkill: vi.fn(),
    removeSkill: vi.fn(),
    getChildren: vi.fn(() => []),
    getChildById: vi.fn(),
    insertChild: vi.fn(),
    updateChildStatus: vi.fn(),
    getRegistryEntry: vi.fn(),
    setRegistryEntry: vi.fn(),
    insertReputation: vi.fn(),
    getReputation: vi.fn(() => []),
    insertInboxMessage: vi.fn(),
    getUnprocessedInboxMessages: vi.fn(() => []),
    markInboxMessageProcessed: vi.fn(),
    setAgentState: vi.fn(),
    close: vi.fn(),
  } as AutomatonDatabase;
}

// Helper to make HTTP request
async function makeHealthRequest(port: number): Promise<{ status: number; body: any }> {
  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        hostname: "localhost",
        port,
        path: "/health",
        method: "GET",
      },
      (res) => {
        let data = "";
        res.on("data", (chunk) => {
          data += chunk;
        });
        res.on("end", () => {
          resolve({
            status: res.statusCode || 0,
            body: JSON.parse(data),
          });
        });
      }
    );
    req.on("error", reject);
    req.end();
  });
}

describe("Railway Health Server", () => {
  let servers: http.Server[] = [];

  afterEach(() => {
    // Close all servers
    servers.forEach((server) => {
      server.close();
    });
    servers = [];
  });

  /**
   * Feature: railway-deployment, Property 6: Health Check Status Accuracy
   * **Validates: Requirements 6.2, 6.4**
   */
  it("Property 6: Health Check Status Accuracy", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constantFrom<AgentState>(
          "setup",
          "waking",
          "running",
          "sleeping",
          "low_compute",
          "critical",
          "dead"
        ),
        fc.nat({ max: 10000 }),
        async (state, turnCount) => {
          const db = createMockDatabase(state, turnCount);
          const port = 3000 + Math.floor(Math.random() * 1000);

          const server = createHealthServer(port, db);
          servers.push(server);

          await new Promise<void>((resolve) => {
            server.listen(port, () => resolve());
          });

          const response = await makeHealthRequest(port);

          // Should return 200 if not dead, 503 if dead
          if (state === "dead") {
            expect(response.status).toBe(503);
            expect(response.body.status).toBe("unhealthy");
          } else {
            expect(response.status).toBe(200);
            expect(response.body.status).toBe("healthy");
          }

          // Should have required fields
          expect(response.body).toHaveProperty("timestamp");
          expect(response.body).toHaveProperty("uptime");
          expect(response.body).toHaveProperty("agent");
          expect(response.body).toHaveProperty("database");

          // Agent state should match
          expect(response.body.agent.state).toBe(state);
          expect(response.body.agent.turnCount).toBe(turnCount);

          // Database should be connected
          expect(response.body.database.connected).toBe(true);

          server.close();
        }
      ),
      { numRuns: PROPERTY_TEST_ITERATIONS }
    );
  });

  describe("Unit Tests", () => {
    it("should return 200 for healthy agent", async () => {
      const db = createMockDatabase("running", 10);
      const port = 3100;

      const server = createHealthServer(port, db);
      servers.push(server);

      await new Promise<void>((resolve) => {
        server.listen(port, () => resolve());
      });

      const response = await makeHealthRequest(port);

      expect(response.status).toBe(200);
      expect(response.body.status).toBe("healthy");
      expect(response.body.agent.state).toBe("running");
      expect(response.body.agent.turnCount).toBe(10);
    });

    it("should return 503 for dead agent", async () => {
      const db = createMockDatabase("dead", 5);
      const port = 3101;

      const server = createHealthServer(port, db);
      servers.push(server);

      await new Promise<void>((resolve) => {
        server.listen(port, () => resolve());
      });

      const response = await makeHealthRequest(port);

      expect(response.status).toBe(503);
      expect(response.body.status).toBe("unhealthy");
      expect(response.body.agent.state).toBe("dead");
    });

    it("should include uptime in response", async () => {
      const db = createMockDatabase("running", 0);
      const port = 3102;

      const server = createHealthServer(port, db);
      servers.push(server);

      await new Promise<void>((resolve) => {
        server.listen(port, () => resolve());
      });

      // Wait a bit
      await new Promise((resolve) => setTimeout(resolve, 100));

      const response = await makeHealthRequest(port);

      expect(response.body.uptime).toBeGreaterThanOrEqual(0);
      expect(typeof response.body.uptime).toBe("number");
    });

    it("should include telegram status if bot provided", async () => {
      const db = createMockDatabase("running", 0);
      const port = 3103;

      const mockBot = {
        isPolling: vi.fn(() => true),
      };

      const server = createHealthServer(port, db, mockBot);
      servers.push(server);

      await new Promise<void>((resolve) => {
        server.listen(port, () => resolve());
      });

      const response = await makeHealthRequest(port);

      expect(response.body.telegram).toBeDefined();
      expect(response.body.telegram.connected).toBe(true);
      expect(mockBot.isPolling).toHaveBeenCalled();
    });

    it("should not include telegram status if bot not provided", async () => {
      const db = createMockDatabase("running", 0);
      const port = 3104;

      const server = createHealthServer(port, db);
      servers.push(server);

      await new Promise<void>((resolve) => {
        server.listen(port, () => resolve());
      });

      const response = await makeHealthRequest(port);

      expect(response.body.telegram).toBeUndefined();
    });

    it("should return 503 on database error", async () => {
      const db = createMockDatabase("running", 0);
      // Make getAgentState throw error
      vi.mocked(db.getAgentState).mockImplementation(() => {
        throw new Error("Database connection failed");
      });

      const port = 3105;

      const server = createHealthServer(port, db);
      servers.push(server);

      await new Promise<void>((resolve) => {
        server.listen(port, () => resolve());
      });

      const response = await makeHealthRequest(port);

      expect(response.status).toBe(503);
      expect(response.body.status).toBe("unhealthy");
      expect(response.body.error).toBe("Database connection failed");
    });

    it("should return 404 for non-health endpoints", async () => {
      const db = createMockDatabase("running", 0);
      const port = 3106;

      const server = createHealthServer(port, db);
      servers.push(server);

      await new Promise<void>((resolve) => {
        server.listen(port, () => resolve());
      });

      const response = await new Promise<{ status: number; body: string }>((resolve, reject) => {
        const req = http.request(
          {
            hostname: "localhost",
            port,
            path: "/other",
            method: "GET",
          },
          (res) => {
            let data = "";
            res.on("data", (chunk) => {
              data += chunk;
            });
            res.on("end", () => {
              resolve({
                status: res.statusCode || 0,
                body: data,
              });
            });
          }
        );
        req.on("error", reject);
        req.end();
      });

      expect(response.status).toBe(404);
      expect(response.body).toBe("Not Found");
    });

    it("should include timestamp in ISO format", async () => {
      const db = createMockDatabase("running", 0);
      const port = 3107;

      const server = createHealthServer(port, db);
      servers.push(server);

      await new Promise<void>((resolve) => {
        server.listen(port, () => resolve());
      });

      const response = await makeHealthRequest(port);

      expect(response.body.timestamp).toBeDefined();
      // Should be valid ISO string
      expect(() => new Date(response.body.timestamp)).not.toThrow();
      expect(new Date(response.body.timestamp).toISOString()).toBe(response.body.timestamp);
    });
  });
});
