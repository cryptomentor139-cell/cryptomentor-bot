/**
 * Railway Environment Configuration Module
 * 
 * Loads and validates environment variables for Railway deployment.
 * Provides safe defaults for optional variables.
 */

export interface RailwayConfig {
  port: number;
  environment: string;
  volumePath: string;
  dbPath: string;
  logLevel: "debug" | "info" | "warn" | "error";
  telegram?: {
    botToken: string;
    creatorId: string;
  };
  payment: {
    autoApproveThreshold: number; // cents
    rateLimitPerHour: number;
  };
}

/**
 * Load Railway configuration from environment variables.
 * 
 * Required variables:
 * - None (all have safe defaults)
 * 
 * Optional variables with defaults:
 * - PORT: defaults to 3000
 * - RAILWAY_ENVIRONMENT: defaults to "production"
 * - RAILWAY_VOLUME_MOUNT_PATH: defaults to "/data"
 * - DB_PATH: defaults to "{volumePath}/automaton.db"
 * - LOG_LEVEL: defaults to "info"
 * - TELEGRAM_BOT_TOKEN: optional, enables Telegram features
 * - TELEGRAM_CREATOR_ID: required if TELEGRAM_BOT_TOKEN is set
 * - PAYMENT_AUTO_APPROVE_THRESHOLD: defaults to 0 (disabled)
 * - PAYMENT_RATE_LIMIT_PER_HOUR: defaults to 10
 * 
 * @returns RailwayConfig object with all configuration values
 * @throws Error if TELEGRAM_CREATOR_ID is missing when TELEGRAM_BOT_TOKEN is set
 */
export function loadRailwayConfig(): RailwayConfig {
  // Parse PORT with safe default
  const port = parseInt(process.env.PORT || "3000", 10);
  
  // Get Railway-provided variables with defaults
  const environment = process.env.RAILWAY_ENVIRONMENT || "production";
  const volumePath = process.env.RAILWAY_VOLUME_MOUNT_PATH || "/data";
  
  // Database path: use DB_PATH if provided, otherwise default to volume path
  const dbPath = process.env.DB_PATH || `${volumePath}/automaton.db`;
  
  // Log level with validation
  const logLevelEnv = process.env.LOG_LEVEL?.toLowerCase();
  const validLogLevels = ["debug", "info", "warn", "error"];
  const logLevel = (validLogLevels.includes(logLevelEnv || "") 
    ? logLevelEnv 
    : "info") as "debug" | "info" | "warn" | "error";
  
  // Telegram configuration (optional)
  let telegram: RailwayConfig["telegram"] = undefined;
  if (process.env.TELEGRAM_BOT_TOKEN) {
    const creatorId = process.env.TELEGRAM_CREATOR_ID;
    if (!creatorId) {
      throw new Error("TELEGRAM_CREATOR_ID is required when TELEGRAM_BOT_TOKEN is set");
    }
    telegram = {
      botToken: process.env.TELEGRAM_BOT_TOKEN,
      creatorId,
    };
  }
  
  // Payment configuration with safe defaults
  const autoApproveThreshold = parseInt(
    process.env.PAYMENT_AUTO_APPROVE_THRESHOLD || "0", 
    10
  );
  const rateLimitPerHour = parseInt(
    process.env.PAYMENT_RATE_LIMIT_PER_HOUR || "10", 
    10
  );
  
  return {
    port,
    environment,
    volumePath,
    dbPath,
    logLevel,
    telegram,
    payment: {
      autoApproveThreshold,
      rateLimitPerHour,
    },
  };
}
