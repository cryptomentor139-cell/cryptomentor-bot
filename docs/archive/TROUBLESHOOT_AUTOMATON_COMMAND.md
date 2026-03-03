# 🔧 Troubleshoot: /automaton status Tidak Respond

## ❌ Masalah

Command `/automaton status` tidak memberikan response di Telegram.

## 🔍 Root Cause

Setelah investigasi code:

1. ✅ Handler `agent_status_command` ADA di `handlers_automaton.py`
2. ✅ Handler sudah di-register di `bot.py`
3. ❌ **TAPI** command yang di-register adalah `/agent_status`, BUKAN `/automaton status`

**Code di bot.py (line 228):**
```python
self.application.add_handler(CommandHandler("agent_status", agent_status_command))
```

Ini artinya command yang benar adalah:
- ✅ `/agent_status` → WORKS
- ❌ `/automaton status` → NOT REGISTERED

## ✅ Solusi

Ada 2 opsi:

### Opsi 1: Gunakan Command yang Sudah Ada (QUICK FIX)

Gunakan command yang sudah di-register:

```
/agent_status     ← Ini yang benar!
/spawn_agent
/agent_lineage
/deposit
/balance
/agent_logs
/withdraw
```

### Opsi 2: Tambah Command `/automaton` dengan Subcommand (PROPER FIX)

Buat handler baru yang support subcommand seperti `/automaton status`.

---

## 🎯 Quick Fix: Gunakan Command yang Benar

### Available Automaton Commands:

| Command | Description |
|---------|-------------|
| `/spawn_agent` | Spawn new AI agent |
| `/agent_status` | Check agent status |
| `/agent_lineage` | View agent lineage tree |
| `/deposit` | Deposit USDC to agent |
| `/balance` | Check agent balance |
| `/agent_logs` | View agent activity logs |
| `/withdraw` | Withdraw funds from agent |

### Test Sekarang:

```
/agent_status
```

Bot harus respond dengan status agent kamu!

---

## 🔧 Proper Fix: Tambah Command `/automaton`

Jika kamu mau command `/automaton status` bekerja, kita perlu:

1. Buat handler baru yang parse subcommand
2. Register command `/automaton`
3. Route ke handler yang sesuai

### Implementation:

```python
# Di handlers_automaton.py, tambah:

async def automaton_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /automaton command with subcommands"""
    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/automaton status - Check agent status\n"
            "/automaton spawn - Spawn new agent\n"
            "/automaton deposit - Deposit funds\n"
            "/automaton balance - Check balance\n"
            "/automaton logs - View logs\n"
            "/automaton withdraw - Withdraw funds\n"
            "/automaton lineage - View lineage"
        )
        return
    
    subcommand = context.args[0].lower()
    
    if subcommand == "status":
        await agent_status_command(update, context)
    elif subcommand == "spawn":
        await spawn_agent_command(update, context)
    elif subcommand == "deposit":
        await deposit_command(update, context)
    elif subcommand == "balance":
        await balance_command(update, context)
    elif subcommand == "logs":
        await agent_logs_command(update, context)
    elif subcommand == "withdraw":
        await withdraw_command(update, context)
    elif subcommand == "lineage":
        await agent_lineage_command(update, context)
    else:
        await update.message.reply_text(f"Unknown subcommand: {subcommand}")
```

```python
# Di bot.py, tambah registration:

from app.handlers_automaton import (
    automaton_command,  # ← Tambah ini
    spawn_agent_command, agent_status_command, ...
)

self.application.add_handler(CommandHandler("automaton", automaton_command))  # ← Tambah ini
```

---

## 📊 Command Comparison

### Current (What Works):
```
/agent_status
/spawn_agent
/deposit
/balance
/agent_logs
/withdraw
/agent_lineage
```

### Desired (What You Want):
```
/automaton status
/automaton spawn
/automaton deposit
/automaton balance
/automaton logs
/automaton withdraw
/automaton lineage
```

---

## 🧪 Test Commands

### Test 1: Current Commands (Should Work)
```
/agent_status
```

**Expected Response:**
```
📊 Agent Status

Agent ID: agent_xxx
Status: Active
Balance: 10.5 USDC
Parent: None
Children: 0
Created: 2026-02-22
```

### Test 2: Check All Commands
```
/spawn_agent
/agent_lineage
/deposit
/balance
/agent_logs
```

Semua harus respond!

---

## 🚀 Recommended Action

**QUICK FIX (5 seconds):**
Gunakan `/agent_status` instead of `/automaton status`

**PROPER FIX (5 minutes):**
Implement `/automaton` command dengan subcommand support

Mau saya implement proper fix sekarang?

---

## 📝 Summary

**Problem:** `/automaton status` tidak di-register

**Current Commands:** `/agent_status`, `/spawn_agent`, etc.

**Solution:** 
- Quick: Gunakan `/agent_status`
- Proper: Tambah `/automaton` command handler

**Test:** `/agent_status` harus work sekarang!
