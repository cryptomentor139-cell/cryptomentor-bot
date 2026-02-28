import Database from 'better-sqlite3';

const db = new Database('C:/root/.automaton/state.db');

console.log('=== TASK STATUS ===');
const task = db.prepare('SELECT * FROM inbox_messages ORDER BY received_at DESC LIMIT 1').get();
console.log(`Task ID: ${task.id}`);
console.log(`From: ${task.from_address}`);
console.log(`Received: ${task.received_at}`);
console.log(`Processed: ${task.processed_at || 'NOT YET'}`);
console.log(`Content: ${task.content.substring(0, 150)}...`);

console.log('\n=== LATEST TURN DETAILS ===');
const turn = db.prepare('SELECT * FROM turns ORDER BY timestamp DESC LIMIT 1').get();
console.log(`Turn ID: ${turn.id}`);
console.log(`Timestamp: ${turn.timestamp}`);
console.log(`State: ${turn.state}`);
console.log(`Cost: ${turn.cost_cents} cents`);
console.log(`\nThinking:`);
console.log(turn.thinking);

console.log('\n=== TOOL CALLS ===');
const tools = JSON.parse(turn.tool_calls);
if (tools.length === 0) {
  console.log('No tool calls in this turn');
} else {
  tools.forEach((t, i) => {
    console.log(`\n${i + 1}. ${t.name}`);
    console.log(`   Arguments: ${JSON.stringify(t.arguments)}`);
    console.log(`   Result: ${t.result ? t.result.substring(0, 200) : 'no result'}...`);
  });
}

console.log('\n=== CREDIT USAGE ===');
const totalTurns = db.prepare('SELECT COUNT(*) as count FROM turns').get();
const totalCost = db.prepare('SELECT SUM(cost_cents) as total FROM turns').get();
console.log(`Total turns: ${totalTurns.count}`);
console.log(`Total cost: $${(totalCost.total / 100).toFixed(2)}`);
console.log(`Remaining credits: $10.00 - $${(totalCost.total / 100).toFixed(2)} = $${(1000 - totalCost.total) / 100}`);

db.close();
