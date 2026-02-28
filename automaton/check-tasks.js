import Database from 'better-sqlite3';

const db = new Database('C:/root/.automaton/state.db');

// Check tables
console.log('=== Database Tables ===');
const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all();
console.log(tables);

// Check inbox_messages
console.log('\n=== Recent Inbox Messages ===');
try {
  const messages = db.prepare('SELECT * FROM inbox_messages ORDER BY timestamp DESC LIMIT 5').all();
  console.log(JSON.stringify(messages, null, 2));
} catch (e) {
  console.log('Error:', e.message);
}

// Check turns (agent activity)
console.log('\n=== Recent Turns ===');
try {
  const turns = db.prepare('SELECT * FROM turns ORDER BY timestamp DESC LIMIT 5').all();
  console.log(JSON.stringify(turns, null, 2));
} catch (e) {
  console.log('Error:', e.message);
}

db.close();
