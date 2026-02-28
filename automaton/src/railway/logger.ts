export type LogLevel = "debug" | "info" | "warn" | "error";

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: Record<string, any>;
  error?: {
    message: string;
    stack?: string;
  };
}

export class RailwayLogger {
  private level: LogLevel;
  private levels: Record<LogLevel, number> = {
    debug: 0,
    info: 1,
    warn: 2,
    error: 3,
  };

  constructor(level: LogLevel = "info") {
    this.level = level;
  }

  private shouldLog(level: LogLevel): boolean {
    return this.levels[level] >= this.levels[this.level];
  }

  private log(level: LogLevel, message: string, context?: Record<string, any>, error?: Error): void {
    if (!this.shouldLog(level)) return;

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
    };

    if (error) {
      entry.error = {
        message: error.message,
        stack: error.stack,
      };
    }

    // Output to stdout as JSON for Railway log aggregation
    console.log(JSON.stringify(entry));
  }

  debug(message: string, context?: Record<string, any>): void {
    this.log("debug", message, context);
  }

  info(message: string, context?: Record<string, any>): void {
    this.log("info", message, context);
  }

  warn(message: string, context?: Record<string, any>): void {
    this.log("warn", message, context);
  }

  error(message: string, error?: Error, context?: Record<string, any>): void {
    this.log("error", message, context, error);
  }

  // Lifecycle events
  logStartup(config: any): void {
    this.info("Automaton starting", {
      environment: config.environment,
      dbPath: config.dbPath,
      port: config.port,
    });
  }

  logShutdown(): void {
    this.info("Automaton shutting down");
  }

  logDatabaseInit(path: string): void {
    this.info("Database initialized", { path });
  }

  logStateChange(from: string, to: string): void {
    this.info("State change", { from, to });
  }

  logTurn(turnId: string, toolCount: number, tokens: number): void {
    this.info("Turn completed", {
      turnId,
      toolCount,
      tokens,
    });
  }

  logPaymentRequest(requestId: string, amount: number, toAddress: string): void {
    this.info("Payment request created", {
      requestId,
      amountCents: amount,
      toAddress,
    });
  }

  logPaymentApproval(requestId: string, reviewedBy: string): void {
    this.info("Payment approved", {
      requestId,
      reviewedBy,
    });
  }

  logPaymentRejection(requestId: string, reviewedBy: string, reason: string): void {
    this.warn("Payment rejected", {
      requestId,
      reviewedBy,
      reason,
    });
  }
}

export function createLogger(level: LogLevel = "info"): RailwayLogger {
  return new RailwayLogger(level);
}
