/**
 * Telegram Bot Interface
 *
 * Provides remote monitoring and control via Telegram bot.
 * Supports commands for status, logs, payment approval, and more.
 */

import TelegramBot from "node-telegram-bot-api";
import type {
  AutomatonDatabase,
  PaymentRequest,
} from "../types.js";
import type { PaymentApprovalSystem } from "../payment/approval.js";
import type { InferenceClient } from "../types.js";
import { TelegramConversationHandler } from "./conversation.js";

export interface TelegramBotConfig {
  token: string;
  creatorId: string;
  db: AutomatonDatabase;
  paymentSystem: PaymentApprovalSystem;
  inference: InferenceClient;
}

export function createTelegramBot(config: TelegramBotConfig): TelegramBot {
  const bot = new TelegramBot(config.token, { polling: true });

  // Store creator ID
  const creatorId = config.creatorId;

  // Create conversation handler
  const conversationHandler = new TelegramConversationHandler(
    bot,
    config.db,
    config.inference
  );

  // Authentication middleware
  function isAuthorized(msg: TelegramBot.Message): boolean {
    return msg.from?.id.toString() === creatorId;
  }

  // Command: /start
  bot.onText(/\/start/, async (msg) => {
    if (!isAuthorized(msg)) return;

    await bot.sendMessage(
      msg.chat.id,
      "🤖 *Automaton Control Bot*\n\n" +
        "Available commands:\n" +
        "/status - System synopsis\n" +
        "/logs - Recent logs\n" +
        "/credits - Financial status\n" +
        "/deposit - Deposit USDC instructions\n" +
        "/approve <id> - Approve payment\n" +
        "/reject <id> <reason> - Reject payment\n" +
        "/children - List child agents\n" +
        "/clear - Clear conversation history\n" +
        "/help - Show this help\n\n" +
        "*Conversational Mode:*\n" +
        "You can also chat with me naturally! Just send a message without a command.",
      { parse_mode: "Markdown" }
    );
  });

  // Command: /status
  bot.onText(/\/status/, async (msg) => {
    if (!isAuthorized(msg)) return;

    try {
      const state = config.db.getAgentState();
      const turnCount = config.db.getTurnCount();
      const identity = {
        name: config.db.getIdentity("name"),
        address: config.db.getIdentity("address"),
      };

      // Get financial state
      const recentTxns = config.db.getRecentTransactions(1);
      const lastBalance = recentTxns[0]?.balanceAfterCents || 0;

      // Get uptime
      const firstTurn = config.db.getRecentTurns(1)[0];
      const uptimeMs = firstTurn
        ? Date.now() - new Date(firstTurn.timestamp).getTime()
        : 0;
      const uptimeHours = Math.floor(uptimeMs / (1000 * 60 * 60));

      const statusMsg =
        `📊 *System Status*\n\n` +
        `Name: ${identity.name}\n` +
        `Address: \`${identity.address}\`\n` +
        `State: ${state}\n` +
        `Turns: ${turnCount}\n` +
        `Balance: $${(lastBalance / 100).toFixed(2)}\n` +
        `Uptime: ${uptimeHours}h\n`;

      await bot.sendMessage(msg.chat.id, statusMsg, { parse_mode: "Markdown" });
    } catch (error: any) {
      await bot.sendMessage(msg.chat.id, `❌ Error: ${error.message}`);
    }
  });

  // Command: /logs
  bot.onText(/\/logs/, async (msg) => {
    if (!isAuthorized(msg)) return;

    try {
      const turns = config.db.getRecentTurns(5);

      let logsMsg = "📝 *Recent Logs*\n\n";
      for (const turn of turns) {
        const time = new Date(turn.timestamp).toLocaleTimeString();
        logsMsg += `[${time}] ${turn.state}\n`;
        logsMsg += `  Tools: ${turn.toolCalls.length}\n`;
        logsMsg += `  Tokens: ${turn.tokenUsage.totalTokens}\n\n`;
      }

      await bot.sendMessage(msg.chat.id, logsMsg, { parse_mode: "Markdown" });
    } catch (error: any) {
      await bot.sendMessage(msg.chat.id, `❌ Error: ${error.message}`);
    }
  });

  // Command: /approve <id>
  bot.onText(/\/approve (.+)/, async (msg, match) => {
    if (!isAuthorized(msg)) return;

    const requestId = match?.[1];
    if (!requestId) {
      await bot.sendMessage(msg.chat.id, "Usage: /approve <payment_id>");
      return;
    }

    try {
      await config.paymentSystem.approvePayment(requestId, creatorId);
      await bot.sendMessage(msg.chat.id, `✅ Payment ${requestId} approved`);

      // Execute approved payments
      await config.paymentSystem.executeApprovedPayments();
    } catch (error: any) {
      await bot.sendMessage(msg.chat.id, `❌ Error: ${error.message}`);
    }
  });

  // Command: /reject <id> <reason>
  bot.onText(/\/reject (\S+) (.+)/, async (msg, match) => {
    if (!isAuthorized(msg)) return;

    const requestId = match?.[1];
    const reason = match?.[2];

    if (!requestId || !reason) {
      await bot.sendMessage(
        msg.chat.id,
        "Usage: /reject <payment_id> <reason>"
      );
      return;
    }

    try {
      await config.paymentSystem.rejectPayment(requestId, creatorId, reason);
      await bot.sendMessage(msg.chat.id, `❌ Payment ${requestId} rejected`);
    } catch (error: any) {
      await bot.sendMessage(msg.chat.id, `❌ Error: ${error.message}`);
    }
  });

  // Command: /children
  bot.onText(/\/children/, async (msg) => {
    if (!isAuthorized(msg)) return;

    try {
      const children = config.db.getChildren();

      if (children.length === 0) {
        await bot.sendMessage(msg.chat.id, "No child agents");
        return;
      }

      let childrenMsg = "👶 *Child Agents*\n\n";
      for (const child of children) {
        childrenMsg += `${child.name}\n`;
        childrenMsg += `  Status: ${child.status}\n`;
        childrenMsg += `  Address: \`${child.address}\`\n\n`;
      }

      await bot.sendMessage(msg.chat.id, childrenMsg, {
        parse_mode: "Markdown",
      });
    } catch (error: any) {
      await bot.sendMessage(msg.chat.id, `❌ Error: ${error.message}`);
    }
  });

  // Command: /help
  bot.onText(/\/help/, async (msg) => {
    if (!isAuthorized(msg)) return;

    const helpMsg =
      `🤖 *Automaton Control Bot*\n\n` +
      `*Commands:*\n` +
      `/status - System synopsis\n` +
      `/logs - Recent activity logs\n` +
      `/credits - Financial status\n` +
      `/deposit - Deposit USDC instructions\n` +
      `/approve <id> - Approve payment\n` +
      `/reject <id> <reason> - Reject payment\n` +
      `/children - List child agents\n` +
      `/clear - Clear conversation history\n` +
      `/help - Show this help\n\n` +
      `*Conversational Mode:*\n` +
      `You can also chat with me naturally! Just send a message without a command.\n\n` +
      `Examples:\n` +
      `• "Berapa sisa credits saya?"\n` +
      `• "Tolong buat file README.md"\n` +
      `• "Status child agents gimana?"\n` +
      `• "Transfer 5 USD ke alamat 0x..."\n\n` +
      `I'll understand and help you! 🚀`;

    await bot.sendMessage(msg.chat.id, helpMsg, { parse_mode: "Markdown" });
  });

  // Command: /clear - Clear conversation history
  bot.onText(/\/clear/, async (msg) => {
    if (!isAuthorized(msg)) return;

    conversationHandler.clearHistory(msg.chat.id);
    await bot.sendMessage(msg.chat.id, "✅ Conversation history cleared");
  });

  // Command: /deposit - USDC deposit instructions
  bot.onText(/\/deposit/, async (msg) => {
    if (!isAuthorized(msg)) return;

    try {
      const address = config.db.getIdentity("address");

      const depositMsg =
        `💰 *Deposit USDC*\n\n` +
        `Wallet Address:\n\`${address}\`\n\n` +
        `*How to deposit:*\n` +
        `1. Send USDC on Base network to address above\n` +
        `2. Wait for confirmation (usually 1-2 minutes)\n` +
        `3. Use /credits to check updated balance\n\n` +
        `*Note:* USDC on Base can be converted to Conway credits automatically.`;

      await bot.sendMessage(msg.chat.id, depositMsg, {
        parse_mode: "Markdown",
      });
    } catch (error: any) {
      await bot.sendMessage(msg.chat.id, `❌ Error: ${error.message}`);
    }
  });

  // Command: /credits - Detailed financial status
  bot.onText(/\/credits/, async (msg) => {
    if (!isAuthorized(msg)) return;

    try {
      // Get recent transactions
      const recentTxns = config.db.getRecentTransactions(5);
      const lastBalance = recentTxns[0]?.balanceAfterCents || 0;

      let txnList = "";
      for (const txn of recentTxns) {
        const time = new Date(txn.timestamp).toLocaleTimeString();
        const amount = ((txn.amountCents || 0) / 100).toFixed(2);
        const sign = txn.type.includes("out") ? "-" : "+";
        txnList += `[${time}] ${sign}${amount} - ${txn.description}\n`;
      }

      const creditsMsg =
        `💳 *Financial Status*\n\n` +
        `Conway Credits: ${(lastBalance / 100).toFixed(2)}\n\n` +
        `*Recent Transactions:*\n\`\`\`\n${txnList || "No recent transactions"}\n\`\`\`\n\n` +
        `Use /deposit to add more USDC`;

      await bot.sendMessage(msg.chat.id, creditsMsg, {
        parse_mode: "Markdown",
      });
    } catch (error: any) {
      await bot.sendMessage(msg.chat.id, `❌ Error: ${error.message}`);
    }
  });

  // Callback query handler for inline buttons
  bot.on("callback_query", async (query) => {
    if (!query.from || query.from.id.toString() !== creatorId) return;
    if (!query.data) return;

    const [action, requestId] = query.data.split(":");

    try {
      if (action === "approve") {
        await config.paymentSystem.approvePayment(requestId, creatorId);
        await bot.answerCallbackQuery(query.id, { text: "Payment approved" });
        await bot.editMessageReplyMarkup(
          { inline_keyboard: [] },
          {
            chat_id: query.message!.chat.id,
            message_id: query.message!.message_id,
          }
        );

        // Execute
        await config.paymentSystem.executeApprovedPayments();
      } else if (action === "reject") {
        await config.paymentSystem.rejectPayment(
          requestId,
          creatorId,
          "Rejected via button"
        );
        await bot.answerCallbackQuery(query.id, { text: "Payment rejected" });
        await bot.editMessageReplyMarkup(
          { inline_keyboard: [] },
          {
            chat_id: query.message!.chat.id,
            message_id: query.message!.message_id,
          }
        );
      }
    } catch (error: any) {
      await bot.answerCallbackQuery(query.id, {
        text: `Error: ${error.message}`,
      });
    }
  });

  // Handle non-command messages (conversational)
  bot.on("message", async (msg) => {
    if (!isAuthorized(msg)) return;

    // Skip if it's a command
    if (msg.text?.startsWith("/")) return;

    // Skip if no text
    if (!msg.text) return;

    // Handle as conversation
    await conversationHandler.handleMessage(msg);
  });

  return bot;
}

/**
 * Send payment request notification to creator
 */
export async function notifyPaymentRequest(
  bot: TelegramBot,
  creatorChatId: string,
  request: PaymentRequest
): Promise<void> {
  const message =
    `💰 *Payment Request*\n\n` +
    `To: \`${request.toAddress}\`\n` +
    `Amount: $${(request.amountCents / 100).toFixed(2)}\n` +
    `Note: ${request.note || "none"}\n` +
    `ID: \`${request.id}\``;

  const keyboard = {
    inline_keyboard: [
      [
        { text: "✅ Approve", callback_data: `approve:${request.id}` },
        { text: "❌ Reject", callback_data: `reject:${request.id}` },
      ],
    ],
  };

  await bot.sendMessage(creatorChatId, message, {
    parse_mode: "Markdown",
    reply_markup: keyboard,
  });
}
