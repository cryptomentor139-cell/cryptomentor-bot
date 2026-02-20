// Simple API server for Automaton Web UI
import express from 'express';
import cors from 'cors';
import Database from 'better-sqlite3';
import { ulid } from 'ulid';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Database path
const DB_PATH = 'C:/root/.automaton/state.db';

// Get automaton status
app.get('/status', (req, res) => {
  try {
    const db = new Database(DB_PATH, { readonly: true });
    
    // Get state
    const stateRow = db.prepare('SELECT value FROM kv WHERE key = ?').get('agent_state');
    const state = stateRow ? stateRow.value : 'unknown';
    
    // Get financial state
    const financialRow = db.prepare('SELECT value FROM kv WHERE key = ?').get('financial_state');
    let credits = 0;
    let usdc = 0;
    
    if (financialRow) {
      try {
        const financial = JSON.parse(financialRow.value);
        credits = financial.creditsCents || 0;
        usdc = financial.usdcBalance || 0;
      } catch {}
    }
    
    // Get turn count
    const turnsRow = db.prepare('SELECT COUNT(*) as count FROM turns').get();
    const turns = turnsRow ? turnsRow.count : 0;
    
    db.close();
    
    res.json({
      state,
      credits,
      usdc,
      turns,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Send command to automaton
app.post('/command', (req, res) => {
  try {
    const { command } = req.body;
    
    if (!command) {
      return res.status(400).json({ error: 'Command is required' });
    }
    
    const db = new Database(DB_PATH);
    const taskId = ulid();
    
    // Insert task to database
    db.prepare('INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)').run(
      'pending_task',
      JSON.stringify({
        id: taskId,
        task: command,
        timestamp: new Date().toISOString(),
        from: 'web-ui',
        status: 'pending'
      })
    );
    
    db.close();
    
    res.json({
      success: true,
      taskId,
      message: 'Command sent to automaton',
      command
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get recent activity
app.get('/activity', (req, res) => {
  try {
    const db = new Database(DB_PATH, { readonly: true });
    
    const turns = db.prepare(`
      SELECT id, timestamp, tool_calls, token_usage 
      FROM turns 
      ORDER BY timestamp DESC 
      LIMIT 10
    `).all();
    
    db.close();
    
    res.json({ turns });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`
🚀 Automaton Web UI Server Running!

📱 Open in browser: http://localhost:${PORT}
🔧 API Endpoint: http://localhost:${PORT}/status
💬 Send commands via UI

Press Ctrl+C to stop
  `);
});
