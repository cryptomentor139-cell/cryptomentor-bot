import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import fc from "fast-check";
import { RailwayLogger, createLogger, type LogLevel } from "../railway/logger.js";

const PROPERTY_TEST_ITERATIONS = 100;

describe("Railway Logger", () => {
  let consoleLogSpy: any;

  beforeEach(() => {
    consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});
  });

  afterEach(() => {
    consoleLogSpy.mockRestore();
  });

  /**
   * Feature: railway-deployment, Property 7: Structured Logging Format
   * **Validates: Requirements 7.2**
   */
  it("Property 7: Structured Logging Format", () => {
    fc.assert(
      fc.property(
        fc.constantFrom<LogLevel>("debug", "info", "warn", "error"),
        fc.string({ minLength: 1 }),
        fc.option(fc.dictionary(fc.string(), fc.anything()), { nil: undefined }),
        (level, message, context) => {
          const logger = createLogger("debug");

          // Call appropriate log method
          switch (level) {
            case "debug":
              logger.debug(message, context);
              break;
            case "info":
              logger.info(message, context);
              break;
            case "warn":
              logger.warn(message, context);
              break;
            case "error":
              logger.error(message, undefined, context);
              break;
          }

          // Should have called console.log
          expect(consoleLogSpy).toHaveBeenCalled();

          // Get the logged output
          const loggedOutput = consoleLogSpy.mock.calls[0][0];

          // Should be valid JSON
          let parsed: any;
          expect(() => {
            parsed = JSON.parse(loggedOutput);
          }).not.toThrow();

          // Should have required fields
          expect(parsed).toHaveProperty("timestamp");
          expect(parsed).toHaveProperty("level");
          expect(parsed).toHaveProperty("message");

          // Timestamp should be valid ISO string
          expect(() => new Date(parsed.timestamp)).not.toThrow();
          expect(new Date(parsed.timestamp).toISOString()).toBe(parsed.timestamp);

          // Level should match
          expect(parsed.level).toBe(level);

          // Message should match
          expect(parsed.message).toBe(message);

          // Context should match if provided
          if (context) {
            expect(parsed.context).toBeDefined();
          }

          consoleLogSpy.mockClear();
        }
      ),
      { numRuns: PROPERTY_TEST_ITERATIONS }
    );
  });

  /**
   * Feature: railway-deployment, Property 8: Error Logging Completeness
   * **Validates: Requirements 7.3**
   */
  it("Property 8: Error Logging Completeness", () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1 }),
        fc.string({ minLength: 1 }),
        fc.option(fc.string(), { nil: undefined }),
        (errorMessage, logMessage, stack) => {
          const logger = createLogger("debug");

          // Create error with optional stack
          const error = new Error(errorMessage);
          if (stack) {
            error.stack = stack;
          }

          // Log error
          logger.error(logMessage, error);

          // Should have called console.log
          expect(consoleLogSpy).toHaveBeenCalled();

          // Get the logged output
          const loggedOutput = consoleLogSpy.mock.calls[0][0];
          const parsed = JSON.parse(loggedOutput);

          // Should have error object
          expect(parsed.error).toBeDefined();
          expect(parsed.error.message).toBe(errorMessage);

          // Should have stack if available
          if (error.stack) {
            expect(parsed.error.stack).toBeDefined();
            expect(parsed.error.stack).toBe(error.stack);
          }

          consoleLogSpy.mockClear();
        }
      ),
      { numRuns: PROPERTY_TEST_ITERATIONS }
    );
  });

  describe("Unit Tests", () => {
    it("should filter logs based on log level", () => {
      const logger = createLogger("warn");

      logger.debug("debug message");
      logger.info("info message");
      logger.warn("warn message");
      logger.error("error message");

      // Should only log warn and error
      expect(consoleLogSpy).toHaveBeenCalledTimes(2);

      const logs = consoleLogSpy.mock.calls.map((call: any) => JSON.parse(call[0]));
      expect(logs[0].level).toBe("warn");
      expect(logs[1].level).toBe("error");
    });

    it("should log lifecycle events with correct context", () => {
      const logger = createLogger("info");

      logger.logStartup({
        environment: "production",
        dbPath: "/data/automaton.db",
        port: 3000,
      });

      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      const log = JSON.parse(consoleLogSpy.mock.calls[0][0]);

      expect(log.message).toBe("Automaton starting");
      expect(log.context.environment).toBe("production");
      expect(log.context.dbPath).toBe("/data/automaton.db");
      expect(log.context.port).toBe(3000);
    });

    it("should log database initialization", () => {
      const logger = createLogger("info");

      logger.logDatabaseInit("/data/automaton.db");

      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      const log = JSON.parse(consoleLogSpy.mock.calls[0][0]);

      expect(log.message).toBe("Database initialized");
      expect(log.context.path).toBe("/data/automaton.db");
    });

    it("should log state changes", () => {
      const logger = createLogger("info");

      logger.logStateChange("idle", "active");

      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      const log = JSON.parse(consoleLogSpy.mock.calls[0][0]);

      expect(log.message).toBe("State change");
      expect(log.context.from).toBe("idle");
      expect(log.context.to).toBe("active");
    });

    it("should log turn completion", () => {
      const logger = createLogger("info");

      logger.logTurn("turn-123", 5, 1000);

      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      const log = JSON.parse(consoleLogSpy.mock.calls[0][0]);

      expect(log.message).toBe("Turn completed");
      expect(log.context.turnId).toBe("turn-123");
      expect(log.context.toolCount).toBe(5);
      expect(log.context.tokens).toBe(1000);
    });

    it("should log payment request", () => {
      const logger = createLogger("info");

      logger.logPaymentRequest("req-123", 500, "0x1234");

      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      const log = JSON.parse(consoleLogSpy.mock.calls[0][0]);

      expect(log.message).toBe("Payment request created");
      expect(log.context.requestId).toBe("req-123");
      expect(log.context.amountCents).toBe(500);
      expect(log.context.toAddress).toBe("0x1234");
    });

    it("should log payment approval", () => {
      const logger = createLogger("info");

      logger.logPaymentApproval("req-123", "user-456");

      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      const log = JSON.parse(consoleLogSpy.mock.calls[0][0]);

      expect(log.message).toBe("Payment approved");
      expect(log.context.requestId).toBe("req-123");
      expect(log.context.reviewedBy).toBe("user-456");
    });

    it("should log payment rejection as warning", () => {
      const logger = createLogger("info");

      logger.logPaymentRejection("req-123", "user-456", "Insufficient funds");

      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      const log = JSON.parse(consoleLogSpy.mock.calls[0][0]);

      expect(log.level).toBe("warn");
      expect(log.message).toBe("Payment rejected");
      expect(log.context.requestId).toBe("req-123");
      expect(log.context.reviewedBy).toBe("user-456");
      expect(log.context.reason).toBe("Insufficient funds");
    });

    it("should log shutdown", () => {
      const logger = createLogger("info");

      logger.logShutdown();

      expect(consoleLogSpy).toHaveBeenCalledTimes(1);
      const log = JSON.parse(consoleLogSpy.mock.calls[0][0]);

      expect(log.message).toBe("Automaton shutting down");
    });
  });
});
