import http from "http";
import type { AutomatonDatabase } from "../types.js";

export interface HealthStatus {
  status: "healthy" | "unhealthy";
  timestamp: string;
  uptime: number;
  agent: {
    state: string;
    turnCount: number;
  };
  database: {
    connected: boolean;
  };
  telegram?: {
    connected: boolean;
  };
}

export function createHealthServer(
  port: number,
  db: AutomatonDatabase,
  telegramBot?: any
): http.Server {
  const startTime = Date.now();

  const server = http.createServer((req, res) => {
    if (req.url === "/health" && req.method === "GET") {
      try {
        const state = db.getAgentState();
        const turnCount = db.getTurnCount();

        const health: HealthStatus = {
          status: "healthy",
          timestamp: new Date().toISOString(),
          uptime: Math.floor((Date.now() - startTime) / 1000),
          agent: {
            state,
            turnCount,
          },
          database: {
            connected: true,
          },
        };

        if (telegramBot) {
          health.telegram = {
            connected: telegramBot.isPolling(),
          };
        }

        // Unhealthy if agent dead
        if (state === "dead") {
          health.status = "unhealthy";
          res.writeHead(503, { "Content-Type": "application/json" });
        } else {
          res.writeHead(200, { "Content-Type": "application/json" });
        }

        res.end(JSON.stringify(health, null, 2));
      } catch (error: any) {
        res.writeHead(503, { "Content-Type": "application/json" });
        res.end(
          JSON.stringify({
            status: "unhealthy",
            error: error.message,
            timestamp: new Date().toISOString(),
          })
        );
      }
    } else {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("Not Found");
    }
  });

  return server;
}
