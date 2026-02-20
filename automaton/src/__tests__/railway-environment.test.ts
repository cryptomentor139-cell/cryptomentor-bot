/**
 * Railway Environment Configuration Tests
 * 
 * Tests for Railway environment variable loading and validation.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fc from "fast-check";
import { loadRailwayConfig } from "../railway/environment.js";

// Configure property test iterations
const PROPERTY_TEST_ITERATIONS = 100;

describe("Railway Environment Configuration", () => {
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    // Save original environment
    originalEnv = { ...process.env };
  });

  afterEach(() => {
    // Restore original environment
    process.env = originalEnv;
  });

  describe("Unit Tests", () => {
    it("should load valid environment variables", () => {
      // Set all environment variables
      process.env.PORT = "8080";
      process.env.RAILWAY_ENVIRONMENT = "staging";
      process.env.RAILWAY_VOLUME_MOUNT_PATH = "/mnt/data";
      process.env.DB_PATH = "/mnt/data/test.db";
      process.env.LOG_LEVEL = "debug";
      process.env.PAYMENT_AUTO_APPROVE_THRESHOLD = "50";
      process.env.PAYMENT_RATE_LIMIT_PER_HOUR = "20";

      const config = loadRailwayConfig();

      expect(config.port).toBe(8080);
      expect(config.environment).toBe("staging");
      expect(config.volumePath).toBe("/mnt/data");
      expect(config.dbPath).toBe("/mnt/data/test.db");
      expect(config.logLevel).toBe("debug");
      expect(config.payment.autoApproveThreshold).toBe(50);
      expect(config.payment.rateLimitPerHour).toBe(20);
      expect(config.telegram).toBeUndefined();
    });

    it("should use default values for optional variables", () => {
      // Clear all optional environment variables
      delete process.env.PORT;
      delete process.env.RAILWAY_ENVIRONMENT;
      delete process.env.RAILWAY_VOLUME_MOUNT_PATH;
      delete process.env.DB_PATH;
      delete process.env.LOG_LEVEL;
      delete process.env.PAYMENT_AUTO_APPROVE_THRESHOLD;
      delete process.env.PAYMENT_RATE_LIMIT_PER_HOUR;
      delete process.env.TELEGRAM_BOT_TOKEN;
      delete process.env.TELEGRAM_CREATOR_ID;

      const config = loadRailwayConfig();

      expect(config.port).toBe(3000);
      expect(config.environment).toBe("production");
      expect(config.volumePath).toBe("/data");
      expect(config.dbPath).toBe("/data/automaton.db");
      expect(config.logLevel).toBe("info");
      expect(config.payment.autoApproveThreshold).toBe(0);
      expect(config.payment.rateLimitPerHour).toBe(10);
      expect(config.telegram).toBeUndefined();
    });

    it("should handle Railway-specific variables", () => {
      process.env.PORT = "5000";
      process.env.RAILWAY_ENVIRONMENT = "production";
      process.env.RAILWAY_VOLUME_MOUNT_PATH = "/railway/volume";

      const config = loadRailwayConfig();

      expect(config.port).toBe(5000);
      expect(config.environment).toBe("production");
      expect(config.volumePath).toBe("/railway/volume");
      // DB path should default to volume path + automaton.db
      expect(config.dbPath).toBe("/railway/volume/automaton.db");
    });

    it("should validate log level and use default for invalid values", () => {
      process.env.LOG_LEVEL = "invalid";

      const config = loadRailwayConfig();

      expect(config.logLevel).toBe("info");
    });

    it("should handle Telegram configuration when both token and creator ID are provided", () => {
      process.env.TELEGRAM_BOT_TOKEN = "123456:ABC-DEF";
      process.env.TELEGRAM_CREATOR_ID = "987654321";

      const config = loadRailwayConfig();

      expect(config.telegram).toBeDefined();
      expect(config.telegram?.botToken).toBe("123456:ABC-DEF");
      expect(config.telegram?.creatorId).toBe("987654321");
    });

    it("should throw error when TELEGRAM_BOT_TOKEN is set but TELEGRAM_CREATOR_ID is missing", () => {
      process.env.TELEGRAM_BOT_TOKEN = "123456:ABC-DEF";
      delete process.env.TELEGRAM_CREATOR_ID;

      expect(() => loadRailwayConfig()).toThrow(
        "TELEGRAM_CREATOR_ID is required when TELEGRAM_BOT_TOKEN is set"
      );
    });

    it("should handle case-insensitive log level", () => {
      process.env.LOG_LEVEL = "DEBUG";

      const config = loadRailwayConfig();

      expect(config.logLevel).toBe("debug");
    });

    it("should parse numeric environment variables correctly", () => {
      process.env.PORT = "9999";
      process.env.PAYMENT_AUTO_APPROVE_THRESHOLD = "100";
      process.env.PAYMENT_RATE_LIMIT_PER_HOUR = "50";

      const config = loadRailwayConfig();

      expect(config.port).toBe(9999);
      expect(config.payment.autoApproveThreshold).toBe(100);
      expect(config.payment.rateLimitPerHour).toBe(50);
    });

    it("should handle empty string environment variables as defaults", () => {
      process.env.PORT = "";
      process.env.LOG_LEVEL = "";

      const config = loadRailwayConfig();

      expect(config.port).toBe(3000); // Default
      expect(config.logLevel).toBe("info"); // Default
    });
  });

  /**
   * Feature: railway-deployment, Property 1: Environment Variable Fallback
   * 
   * **Validates: Requirements 2.4**
   */
  it("Property 1: Environment Variable Fallback", () => {
    fc.assert(
      fc.property(
        fc.record({
          PORT: fc.option(fc.integer({ min: 1, max: 65535 }).map(String), { nil: undefined }),
          LOG_LEVEL: fc.option(fc.constantFrom("debug", "info", "warn", "error"), { nil: undefined }),
          PAYMENT_AUTO_APPROVE_THRESHOLD: fc.option(fc.nat().map(String), { nil: undefined }),
          PAYMENT_RATE_LIMIT_PER_HOUR: fc.option(fc.integer({ min: 1, max: 100 }).map(String), { nil: undefined }),
          RAILWAY_ENVIRONMENT: fc.option(fc.constantFrom("production", "staging", "development"), { nil: undefined }),
          RAILWAY_VOLUME_MOUNT_PATH: fc.option(fc.string(), { nil: undefined }),
          DB_PATH: fc.option(fc.string(), { nil: undefined }),
        }),
        (env) => {
          // Clear environment
          delete process.env.PORT;
          delete process.env.LOG_LEVEL;
          delete process.env.PAYMENT_AUTO_APPROVE_THRESHOLD;
          delete process.env.PAYMENT_RATE_LIMIT_PER_HOUR;
          delete process.env.RAILWAY_ENVIRONMENT;
          delete process.env.RAILWAY_VOLUME_MOUNT_PATH;
          delete process.env.DB_PATH;
          delete process.env.TELEGRAM_BOT_TOKEN;
          delete process.env.TELEGRAM_CREATOR_ID;

          // Set test environment variables
          if (env.PORT !== undefined) process.env.PORT = env.PORT;
          if (env.LOG_LEVEL !== undefined) process.env.LOG_LEVEL = env.LOG_LEVEL;
          if (env.PAYMENT_AUTO_APPROVE_THRESHOLD !== undefined) {
            process.env.PAYMENT_AUTO_APPROVE_THRESHOLD = env.PAYMENT_AUTO_APPROVE_THRESHOLD;
          }
          if (env.PAYMENT_RATE_LIMIT_PER_HOUR !== undefined) {
            process.env.PAYMENT_RATE_LIMIT_PER_HOUR = env.PAYMENT_RATE_LIMIT_PER_HOUR;
          }
          if (env.RAILWAY_ENVIRONMENT !== undefined) {
            process.env.RAILWAY_ENVIRONMENT = env.RAILWAY_ENVIRONMENT;
          }
          if (env.RAILWAY_VOLUME_MOUNT_PATH !== undefined) {
            process.env.RAILWAY_VOLUME_MOUNT_PATH = env.RAILWAY_VOLUME_MOUNT_PATH;
          }
          if (env.DB_PATH !== undefined) process.env.DB_PATH = env.DB_PATH;

          // Load config - should not crash
          const config = loadRailwayConfig();

          // Should have valid configuration
          expect(config).toBeDefined();

          // Port should be valid
          expect(config.port).toBeGreaterThan(0);
          expect(config.port).toBeLessThanOrEqual(65535);

          // Log level should be valid
          expect(config.logLevel).toMatch(/^(debug|info|warn|error)$/);

          // Environment should be set
          expect(config.environment).toBeDefined();
          expect(typeof config.environment).toBe("string");

          // Volume path should be set
          expect(config.volumePath).toBeDefined();
          expect(typeof config.volumePath).toBe("string");

          // DB path should be set
          expect(config.dbPath).toBeDefined();
          expect(typeof config.dbPath).toBe("string");

          // Payment config should have safe defaults
          expect(config.payment.autoApproveThreshold).toBeGreaterThanOrEqual(0);
          expect(config.payment.rateLimitPerHour).toBeGreaterThan(0);

          // Telegram should be undefined when not configured
          expect(config.telegram).toBeUndefined();
        }
      ),
      { numRuns: PROPERTY_TEST_ITERATIONS }
    );
  });
});
