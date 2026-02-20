/**
 * Railway Entry Point
 *
 * Specialized entry point for running Automaton on Railway platform.
 * Handles Railway-specific configuration, Telegram bot, payment system,
 * and graceful lifecycle management.
 */

import { loadRailwayConfig } from "./environment.js";
import { createHealthServer } from "./health-server.js";
import { createTelegramBot, notifyPaymentRequest } from "../telegram/bot.js";
import { createPaymentApprovalSystem } from "../payment/approval.js";
import { createDatabase } from "../state/database.js";
import { loadConfig } from "../config.js";
import { getWallet } from "../identity/wallet.js";
import { createConwayClient } from "../conway/client.js";
import { createInferenceClient } from "../conway/inference.js";
import { runAgentLoop } from "../agent/loop.js";
import { loadSkills } from "../skills/loader.js";
import { createSocialClient } from "../social/client.js";
import type { AutomatonIdentity, AgentState } from "../types.js";
import type TelegramBot from "node-telegram-bot-api";

export async function runOnRailway(): Promise<void> {
  console.log(
    `[${new Date().toISOString()}] Starting Automaton on Railway...`
  );

  // Load Railway-specific config
  const railwayConfig = loadRailwayConfig();
  console.log(
    `[${new Date().toISOString()}] Railway environment: ${railwayConfig.environment}`
  );
  console.log(
    `[${new Date().toISOString()}] Database path: ${railwayConfig.dbPath}`
  );

  // Load automaton config
  let config = loadConfig();
  if (!config) {
    console.warn("Automaton config not found. Using Railway environment variables only.");
    // Create minimal config from environment
    config = {
      name: process.env.AUTOMATON_NAME || "Railway Automaton",
      version: "0.1.0",
      walletAddress: "" as `0x${string}`,
      creatorAddress: (process.env.CREATOR_ADDRESS || "0x0000000000000000000000000000000000000000") as `0x${string}`,
      sandboxId: process.env.SANDBOX_ID || "",
      conwayApiUrl: process.env.CONWAY_API_URL || "https://api.conway.tech",
      conwayApiKey: process.env.CONWAY_API_KEY || "",
      inferenceModel: process.env.INFERENCE_MODEL || "gpt-4o",
      maxTokensPerTurn: parseInt(process.env.MAX_TOKENS_PER_TURN || "4096"),
      dbPath: railwayConfig.dbPath,
      heartbeatConfigPath: "~/.automaton/heartbeat.yml",
      skillsDir: "~/.automaton/skills",
      genesisPrompt: process.env.GENESIS_PROMPT || "I am an autonomous AI agent.",
      registeredWithConway: !!process.env.CONWAY_API_KEY,
      logLevel: railwayConfig.logLevel,
      maxChildren: parseInt(process.env.MAX_CHILDREN || "3"),
    };
  }

  // Override DB path with Railway volume path
  config.dbPath = railwayConfig.dbPath;
  config.logLevel = railwayConfig.logLevel;

  // Initialize database
  const db = createDatabase(config.dbPath);
  console.log(`[${new Date().toISOString()}] Database initialized`);

  // Load wallet
  const { account } = await getWallet();

  // Create identity
  const identity: AutomatonIdentity = {
    name: config.name,
    address: account.address,
    account,
    creatorAddress: config.creatorAddress,
    sandboxId: config.sandboxId,
    apiKey: config.conwayApiKey,
    createdAt: db.getIdentity("created_at") || new Date().toISOString(),
  };

  // Create Conway client
  const conway = createConwayClient({
    apiUrl: config.conwayApiUrl,
    apiKey: config.conwayApiKey,
    sandboxId: config.sandboxId,
  });

  // Create inference client
  const inference = createInferenceClient({
    apiUrl: config.conwayApiUrl,
    apiKey: config.conwayApiKey,
    defaultModel: config.inferenceModel,
    maxTokens: config.maxTokensPerTurn,
    account,
  });

  // Create payment approval system
  const paymentSystem = createPaymentApprovalSystem(db, conway, {
    autoApproveThreshold: railwayConfig.payment.autoApproveThreshold,
    rateLimitPerHour: railwayConfig.payment.rateLimitPerHour,
  });

  // Create Telegram bot (optional)
  let telegramBot: TelegramBot | undefined;
  let creatorChatId: string | undefined;

  if (railwayConfig.telegram) {
    try {
      telegramBot = createTelegramBot({
        token: railwayConfig.telegram.botToken,
        creatorId: railwayConfig.telegram.creatorId,
        db,
        paymentSystem,
        inference,
      });

      // Get creator chat ID (same as user ID for private chats)
      creatorChatId = railwayConfig.telegram.creatorId;

      console.log(`[${new Date().toISOString()}] Telegram bot started`);
    } catch (error: any) {
      console.warn(
        `[${new Date().toISOString()}] Telegram bot initialization failed: ${error.message}`
      );
      console.warn(
        `[${new Date().toISOString()}] Continuing without Telegram features`
      );
    }
  }

  // Start health check server
  const healthServer = createHealthServer(
    railwayConfig.port,
    db,
    telegramBot
  );
  healthServer.listen(railwayConfig.port, () => {
    console.log(
      `[${new Date().toISOString()}] Health server listening on port ${railwayConfig.port}`
    );
  });

  // Graceful shutdown handler
  const shutdown = async () => {
    console.log(`[${new Date().toISOString()}] Shutting down...`);

    if (telegramBot) {
      try {
        await telegramBot.stopPolling();
      } catch (error: any) {
        console.warn(
          `[${new Date().toISOString()}] Error stopping Telegram bot: ${error.message}`
        );
      }
    }

    healthServer.close();
    db.setAgentState("sleeping");
    db.close();

    process.exit(0);
  };

  process.on("SIGTERM", shutdown);
  process.on("SIGINT", shutdown);

  // Payment request notification hook
  const originalRequestPayment =
    paymentSystem.requestPayment.bind(paymentSystem);
  paymentSystem.requestPayment = async (toAddress, amountCents, note) => {
    const request = await originalRequestPayment(toAddress, amountCents, note);

    // Notify via Telegram if pending approval
    if (
      request.status === "pending_approval" &&
      telegramBot &&
      creatorChatId
    ) {
      try {
        await notifyPaymentRequest(telegramBot, creatorChatId, request);
      } catch (error: any) {
        console.warn(
          `[${new Date().toISOString()}] Failed to send Telegram notification: ${error.message}`
        );
      }
    }

    return request;
  };

  // Load skills
  const skills = await loadSkills(config.skillsDir, db);
  console.log(
    `[${new Date().toISOString()}] Loaded ${skills.length} skills`
  );

  // Create social client (optional)
  let social: any = undefined;
  if (config.socialRelayUrl) {
    try {
      social = createSocialClient(config.socialRelayUrl, identity.account);
      console.log(`[${new Date().toISOString()}] Social client initialized`);
    } catch (error: any) {
      console.warn(
        `[${new Date().toISOString()}] Social client initialization failed: ${error.message}`
      );
    }
  }

  // Track previous state for critical state alerts
  let previousState: AgentState = db.getAgentState();

  // Main agent loop
  console.log(`[${new Date().toISOString()}] Starting agent loop...`);

  while (true) {
    try {
      await runAgentLoop({
        identity,
        config,
        db,
        conway,
        inference,
        social,
        skills,
        onStateChange: (state) => {
          console.log(`[${new Date().toISOString()}] State: ${state}`);

          // Send critical state alert
          if (
            state === "critical" &&
            previousState !== "critical" &&
            telegramBot &&
            creatorChatId
          ) {
            telegramBot
              .sendMessage(
                creatorChatId,
                `⚠️ *Critical State Alert*\n\nAutomaton has entered critical state. Credits are running low!`,
                { parse_mode: "Markdown" }
              )
              .catch((error) => {
                console.warn(
                  `[${new Date().toISOString()}] Failed to send critical alert: ${error.message}`
                );
              });
          }

          previousState = state;
        },
        onTurnComplete: (turn) => {
          console.log(
            `[${new Date().toISOString()}] Turn ${turn.id}: ${turn.toolCalls.length} tools, ${turn.tokenUsage.totalTokens} tokens`
          );
        },
      });

      // Execute approved payments after each loop
      try {
        await paymentSystem.executeApprovedPayments();
      } catch (error: any) {
        console.warn(
          `[${new Date().toISOString()}] Error executing approved payments: ${error.message}`
        );
      }

      // Sleep between loops
      await new Promise((resolve) => setTimeout(resolve, 60000));
    } catch (error: any) {
      console.error(
        `[${new Date().toISOString()}] Error in agent loop: ${error.message}`
      );
      console.error(error.stack);

      // Sleep before retry
      await new Promise((resolve) => setTimeout(resolve, 30000));
    }
  }
}
