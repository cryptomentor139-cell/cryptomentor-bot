// Send task to automaton via database
import Database from 'better-sqlite3';
import { ulid } from 'ulid';

const task = process.argv.slice(2).join(' ');

if (!task) {
  console.log('Usage: node send-task.js <your task here>');
  console.log('');
  console.log('Examples:');
  console.log('  node send-task.js Create a business plan for AI startup');
  console.log('  node send-task.js Research latest AI trends and summarize');
  console.log('  node send-task.js Draft a marketing strategy document');
  process.exit(1);
}

try {
  const db = new Database('C:/root/.automaton/state.db');
  
  // Insert task to inbox_messages (the correct table automaton reads from)
  const taskId = ulid();
  const creatorAddress = '0xdf7fd9d111a3c1a027d3e92e26704a1672196967'; // From automaton.json
  
  db.prepare(`
    INSERT INTO inbox_messages (id, from_address, content, received_at, processed_at, reply_to)
    VALUES (?, ?, ?, datetime('now'), NULL, NULL)
  `).run(taskId, creatorAddress, task);
  
  console.log(`✅ Task sent to automaton!`);
  console.log(`Task ID: ${taskId}`);
  console.log(`Task: ${task}`);
  console.log('');
  console.log('Automaton will pick up this task on next wake cycle (within 60 seconds).');
  console.log('Watch the terminal where automaton is running to see it execute.');
  
  db.close();
} catch (err) {
  console.error(`❌ Error: ${err.message}`);
  process.exit(1);
}
