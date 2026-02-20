# Cara Interact dengan Automaton via Terminal

## Masalah: Automaton Looping Tanpa Input

Automaton sekarang dalam **autonomous mode** - dia akan:
1. Wake up
2. Check status
3. Think
4. Tidak ada task baru → Sleep
5. Repeat

Ini normal untuk autonomous agent, tapi untuk **interact langsung**, kamu perlu cara untuk **give input**.

## Cara 1: Modify Genesis Prompt (Give Task)

Stop automaton dan edit genesis prompt untuk kasih task spesifik:

```bash
# Stop automaton
taskkill /F /IM node.exe

# Edit config
notepad C:\root\.automaton\automaton.json
```

Ubah `genesisPrompt` menjadi task spesifik, contoh:
```json
{
  "genesisPrompt": "You are Chief AI Officer. Your first task: Create a business plan document for a tech startup. Save it to a file called business-plan.md. Include: executive summary, market analysis, revenue model, and growth strategy."
}
```

Lalu jalankan lagi:
```bash
node dist/index.js --run
```

## Cara 2: Use Social Inbox (Message Queue)

Automaton punya inbox system. Kamu bisa kirim message:

```bash
# Create message file
echo {"from":"creator","content":"Create a business plan for AI startup","timestamp":"2026-02-20T10:30:00.000Z"} > C:\root\.automaton\inbox\message-001.json
```

Automaton akan baca inbox di heartbeat cycle berikutnya.

## Cara 3: Database Direct Input (Advanced)

Insert task langsung ke database:

```bash
# Install sqlite3 kalau belum ada
npm install -g sqlite3

# Insert task
sqlite3 C:\root\.automaton\state.db "INSERT INTO kv (key, value) VALUES ('pending_task', 'Create a business plan document')"
```

## Cara 4: CLI Command (Recommended)

Buat script untuk send command ke automaton:

```javascript
// send-command.js
const Database = require('better-sqlite3');
const db = new Database('C:/root/.automaton/state.db');

const command = process.argv[2];
if (!command) {
  console.log('Usage: node send-command.js "your command here"');
  process.exit(1);
}

// Insert command to inbox
db.prepare('INSERT INTO kv (key, value) VALUES (?, ?)').run(
  'pending_command',
  JSON.stringify({
    command,
    timestamp: new Date().toISOString(),
    from: 'terminal'
  })
);

console.log(`Command sent: ${command}`);
db.close();
```

Usage:
```bash
node send-command.js "Create a business plan for AI startup"
```

## Cara 5: Stop Looping - Give Specific Task

Automaton looping karena tidak ada task. Solusi terbaik:

1. **Stop automaton**
```bash
taskkill /F /IM node.exe
```

2. **Edit genesis prompt dengan task spesifik**
```bash
notepad C:\root\.automaton\automaton.json
```

Contoh task yang bisa dikasih:
- "Research and summarize latest AI trends"
- "Create a marketing strategy document"
- "Analyze competitor landscape"
- "Draft a technical specification"
- "Create a content calendar"

3. **Jalankan lagi**
```bash
node dist/index.js --run
```

## Mengapa Automaton Looping?

Automaton dirancang untuk **autonomous operation** - dia akan:
- Monitor resources
- Check for tasks
- Execute tasks kalau ada
- Sleep kalau tidak ada

Tanpa **external input** (Telegram, social inbox, atau task queue), automaton akan idle loop.

## Recommended: Deploy ke Railway dengan Telegram

Untuk interaction yang lebih natural:
1. Deploy ke Railway
2. Enable Telegram bot
3. Chat dengan automaton via Telegram
4. Automaton akan respond dan execute tasks

Atau kalau mau local, jalankan dengan Telegram bot enabled.

## Check Automaton Activity

```bash
# Check status
node dist/index.js --status

# Check credits usage
node check-api-credits.js

# View recent turns
sqlite3 C:\root\.automaton\state.db "SELECT * FROM turns ORDER BY timestamp DESC LIMIT 5"
```

## Current Status

- **State**: Sleeping (normal)
- **Turns**: 18 completed
- **Credits**: ~$9.50-9.70 (used ~$0.30-0.50)
- **Behavior**: Idle loop (waiting for input)

Automaton **WORKING CORRECTLY** - hanya saja tidak ada task untuk dikerjakan!
