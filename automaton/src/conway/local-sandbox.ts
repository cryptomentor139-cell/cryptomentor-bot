/**
 * Local Sandbox Adapter
 * 
 * Provides sandbox-like functionality using local filesystem and shell
 * when no Conway sandbox is available. This allows automaton to execute
 * tools without paying for cloud sandbox.
 */

import { execSync } from "child_process";
import fs from "fs";
import path from "path";

export interface LocalExecResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export class LocalSandbox {
  private workDir: string;

  constructor(workDir?: string) {
    // Use ~/.automaton/workspace as default work directory
    this.workDir = workDir || path.join(
      process.env.HOME || process.env.USERPROFILE || "/root",
      ".automaton",
      "workspace"
    );
    
    // Create work directory if it doesn't exist
    if (!fs.existsSync(this.workDir)) {
      fs.mkdirSync(this.workDir, { recursive: true });
    }
  }

  /**
   * Execute a shell command locally
   */
  async exec(command: string, timeoutMs: number = 30000): Promise<LocalExecResult> {
    try {
      const stdout = execSync(command, {
        cwd: this.workDir,
        encoding: "utf-8",
        timeout: timeoutMs,
        maxBuffer: 10 * 1024 * 1024, // 10MB
      });

      return {
        stdout: stdout.toString(),
        stderr: "",
        exitCode: 0,
      };
    } catch (error: any) {
      return {
        stdout: error.stdout?.toString() || "",
        stderr: error.stderr?.toString() || error.message,
        exitCode: error.status || 1,
      };
    }
  }

  /**
   * Write content to a file
   */
  async writeFile(filePath: string, content: string): Promise<void> {
    const fullPath = this.resolvePath(filePath);
    const dir = path.dirname(fullPath);
    
    // Create directory if it doesn't exist
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    fs.writeFileSync(fullPath, content, "utf-8");
  }

  /**
   * Read content from a file
   */
  async readFile(filePath: string): Promise<string> {
    const fullPath = this.resolvePath(filePath);
    
    if (!fs.existsSync(fullPath)) {
      throw new Error(`File not found: ${filePath}`);
    }
    
    return fs.readFileSync(fullPath, "utf-8");
  }

  /**
   * Resolve relative path to absolute path within work directory
   */
  private resolvePath(filePath: string): string {
    // If absolute path, use as-is (but be careful!)
    if (path.isAbsolute(filePath)) {
      return filePath;
    }
    
    // Otherwise, resolve relative to work directory
    return path.join(this.workDir, filePath);
  }

  /**
   * Get work directory path
   */
  getWorkDir(): string {
    return this.workDir;
  }

  /**
   * List files in work directory
   */
  async listFiles(subPath: string = ""): Promise<string[]> {
    const fullPath = this.resolvePath(subPath);
    
    if (!fs.existsSync(fullPath)) {
      return [];
    }
    
    return fs.readdirSync(fullPath);
  }

  /**
   * Port exposure (no-op for local mode, just return localhost URL)
   */
  async exposePort(port: number): Promise<{ port: number; publicUrl: string }> {
    return {
      port,
      publicUrl: `http://localhost:${port}`,
    };
  }

  /**
   * Remove port (no-op for local mode)
   */
  async removePort(_port: number): Promise<void> {
    // No-op in local mode
  }
}
