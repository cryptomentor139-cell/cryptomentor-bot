import type TelegramBot from "node-telegram-bot-api";
import type { AutomatonDatabase } from "../types.js";
import type { InferenceClient } from "../types.js";

export interface ConversationContext {
  chatId: number;
  userId: string;
  history: ConversationMessage[];
}

export interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export class TelegramConversationHandler {
  private contexts: Map<number, ConversationContext> = new Map();
  private maxHistoryLength = 20; // Keep last 20 messages

  constructor(
    private bot: TelegramBot,
    private db: AutomatonDatabase,
    private inference: InferenceClient
  ) {}

  async handleMessage(msg: TelegramBot.Message): Promise<void> {
    const chatId = msg.chat.id;
    const userId = msg.from!.id.toString();
    const userMessage = msg.text || "";

    // Get atau create conversation context
    let context = this.contexts.get(chatId);
    if (!context) {
      context = {
        chatId,
        userId,
        history: this.loadHistoryFromDb(chatId),
      };
      this.contexts.set(chatId, context);
    }

    // Add user message ke history
    context.history.push({
      role: "user",
      content: userMessage,
      timestamp: new Date().toISOString(),
    });

    // Trim history jika terlalu panjang
    if (context.history.length > this.maxHistoryLength) {
      context.history = context.history.slice(-this.maxHistoryLength);
    }

    // Send "typing" indicator
    await this.bot.sendChatAction(chatId, "typing");

    try {
      // Generate response menggunakan inference
      const response = await this.generateResponse(context);

      // Add assistant response ke history
      context.history.push({
        role: "assistant",
        content: response,
        timestamp: new Date().toISOString(),
      });

      // Trim history jika terlalu panjang (AFTER adding response)
      if (context.history.length > this.maxHistoryLength) {
        context.history = context.history.slice(-this.maxHistoryLength);
      }

      // Save history ke database
      this.saveHistoryToDb(chatId, context.history);

      // Send response (dengan pagination jika terlalu panjang)
      await this.sendResponse(chatId, response);
    } catch (error: any) {
      await this.bot.sendMessage(
        chatId,
        `❌ Error: ${error.message}\n\nSilakan coba lagi atau gunakan /help untuk bantuan.`
      );
    }
  }

  private async generateResponse(context: ConversationContext): Promise<string> {
    // Build system prompt dengan automaton context
    const systemPrompt = this.buildSystemPrompt();

    // Build conversation messages
    const messages = [
      { role: "system" as const, content: systemPrompt },
      ...context.history.map((m) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
      })),
    ];

    // Call inference API
    const response = await this.inference.chat(messages, {
      maxTokens: 1000,
      temperature: 0.7,
    });

    return response.message.content;
  }

  private buildSystemPrompt(): string {
    // Get automaton state
    const state = this.db.getAgentState();
    const turnCount = this.db.getTurnCount();
    const identity = {
      name: this.db.getIdentity("name"),
      address: this.db.getIdentity("address"),
    };

    // Get financial state
    const recentTxns = this.db.getRecentTransactions(1);
    const lastBalance = recentTxns[0]?.balanceAfterCents || 0;

    return `You are ${identity.name}, an autonomous AI agent running on Conway infrastructure.

Current Status:
- State: ${state}
- Turns completed: ${turnCount}
- Credit balance: ${(lastBalance / 100).toFixed(2)} USD
- Wallet: ${identity.address}

You are chatting with your creator via Telegram. You can:
1. Answer questions about your status, capabilities, and activities
2. Accept instructions and tasks from your creator
3. Explain what you're working on or planning to do
4. Ask for clarification when needed
5. Report on your survival status and resource needs

Be helpful, concise, and honest. Use emojis sparingly for clarity.
If you need to perform actions (like transfers), explain what you'll do and ask for confirmation.
Format responses using Markdown for better readability.`;
  }

  private async sendResponse(chatId: number, response: string): Promise<void> {
    // Telegram message limit: 4096 characters
    const MAX_LENGTH = 4000;

    if (response.length <= MAX_LENGTH) {
      await this.bot.sendMessage(chatId, response, {
        parse_mode: "Markdown",
      });
      return;
    }

    // Split into chunks
    const chunks = this.splitMessage(response, MAX_LENGTH);

    for (let i = 0; i < chunks.length; i++) {
      const chunk = chunks[i];
      const prefix = i === 0 ? "" : `_(continued ${i + 1}/${chunks.length})_\n\n`;

      await this.bot.sendMessage(chatId, prefix + chunk, {
        parse_mode: "Markdown",
      });

      // Small delay between chunks
      if (i < chunks.length - 1) {
        await new Promise((resolve) => setTimeout(resolve, 500));
      }
    }
  }

  splitMessage(text: string, maxLength: number): string[] {
    const chunks: string[] = [];
    let currentChunk = "";

    // If text is short enough, return as is
    if (text.length <= maxLength) {
      return [text];
    }

    // Split by paragraphs first
    const paragraphs = text.split("\n\n");

    for (const para of paragraphs) {
      // If adding this paragraph would exceed limit
      if (currentChunk.length + para.length + 2 > maxLength) {
        // Save current chunk if it has content
        if (currentChunk) {
          chunks.push(currentChunk);
          currentChunk = "";
        }

        // If single paragraph is too long, split it
        if (para.length > maxLength) {
          // Try splitting by sentences
          const sentences = para.match(/[^.!?]+[.!?]+/g) || [para];

          for (const sentence of sentences) {
            if (currentChunk.length + sentence.length <= maxLength) {
              currentChunk += sentence;
            } else {
              if (currentChunk) {
                chunks.push(currentChunk);
                currentChunk = "";
              }

              // If single sentence is still too long, split by character
              if (sentence.length > maxLength) {
                for (let i = 0; i < sentence.length; i += maxLength) {
                  chunks.push(sentence.slice(i, i + maxLength));
                }
              } else {
                currentChunk = sentence;
              }
            }
          }
        } else {
          currentChunk = para;
        }
      } else {
        // Add paragraph to current chunk
        currentChunk += (currentChunk ? "\n\n" : "") + para;
      }
    }

    // Add remaining chunk
    if (currentChunk) {
      chunks.push(currentChunk);
    }

    return chunks.length > 0 ? chunks : [text];
  }

  private loadHistoryFromDb(chatId: number): ConversationMessage[] {
    const historyJson = this.db.getKV(`telegram_history_${chatId}`);
    if (!historyJson) return [];

    try {
      return JSON.parse(historyJson);
    } catch {
      return [];
    }
  }

  private saveHistoryToDb(chatId: number, history: ConversationMessage[]): void {
    this.db.setKV(`telegram_history_${chatId}`, JSON.stringify(history));
  }

  clearHistory(chatId: number): void {
    this.contexts.delete(chatId);
    this.db.deleteKV(`telegram_history_${chatId}`);
  }
}

export class TaskProgressTracker {
  constructor(
    private bot: TelegramBot,
    private chatId: number
  ) {}

  async startTask(taskName: string): Promise<number> {
    const msg = await this.bot.sendMessage(this.chatId, `⏳ Starting task: ${taskName}...`);
    return msg.message_id;
  }

  async updateProgress(messageId: number, progress: string): Promise<void> {
    await this.bot.editMessageText(`⏳ ${progress}`, {
      chat_id: this.chatId,
      message_id: messageId,
    });
  }

  async completeTask(messageId: number, result: string): Promise<void> {
    await this.bot.editMessageText(`✅ ${result}`, {
      chat_id: this.chatId,
      message_id: messageId,
    });
  }

  async failTask(messageId: number, error: string): Promise<void> {
    await this.bot.editMessageText(`❌ Task failed: ${error}`, {
      chat_id: this.chatId,
      message_id: messageId,
    });
  }
}
