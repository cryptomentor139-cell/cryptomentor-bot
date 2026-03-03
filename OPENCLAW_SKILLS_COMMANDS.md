# OpenClaw Skills - Command Reference

## 📚 All Commands

### Browse & Discovery

#### `/openclaw_skills`
Browse all available skills in the marketplace

**Example:**
```
/openclaw_skills
```

**Output:**
- Shows all available skills
- Grouped by category
- Shows price and premium status
- Your current credits

---

#### `/openclaw_skill <skill_id>`
View detailed information about a specific skill

**Example:**
```
/openclaw_skill skill_crypto_analysis
```

**Output:**
- Skill name and description
- Category and price
- Capabilities list
- Whether you can afford it
- Install command

---

### Installation & Management

#### `/openclaw_install <skill_id>`
Install a skill on your assistant

**Example:**
```
/openclaw_install skill_crypto_analysis
```

**Requirements:**
- Active OpenClaw session
- Sufficient credits
- Skill not already installed

**Output:**
- Installation confirmation
- Credits deducted
- New balance
- New capabilities

---

#### `/openclaw_myskills`
View all skills installed on your assistant

**Example:**
```
/openclaw_myskills
```

**Output:**
- Total installed skills
- Grouped by category
- Active/inactive status
- Usage statistics

---

#### `/openclaw_toggle <skill_id>`
Enable or disable a skill

**Example:**
```
/openclaw_toggle skill_crypto_analysis
```

**Output:**
- New status (enabled/disabled)
- Skill remains installed

---

## 🎯 Common Workflows

### First Time Setup

1. Start OpenClaw
```
/openclaw_start
```

2. Browse available skills
```
/openclaw_skills
```

3. View skill details
```
/openclaw_skill skill_crypto_analysis
```

4. Install the skill
```
/openclaw_install skill_crypto_analysis
```

5. Start using it!
```
User: "Analyze BTC trend"
```

---

### Managing Skills

1. View installed skills
```
/openclaw_myskills
```

2. Disable a skill temporarily
```
/openclaw_toggle skill_crypto_analysis
```

3. Re-enable when needed
```
/openclaw_toggle skill_crypto_analysis
```

---

### Buying More Skills

1. Check your balance
```
/openclaw_balance
```

2. Buy more credits if needed
```
/openclaw_buy
```

3. Browse and install
```
/openclaw_skills
/openclaw_install skill_trading_signals
```

---

## 💰 Skill Pricing

### Free Skills
- **Basic Chat** - FREE
- Included with every assistant

### Low Cost (500-600 credits)
- **Crypto Market Analysis** - 500 credits
- **NFT Advisor** - 600 credits
- **Research Assistant** - 500 credits

### Mid Tier (750-900 credits)
- **Portfolio Management** - 750 credits
- **DeFi Expert** - 800 credits
- **Risk Manager** - 900 credits

### Premium (1,000-1,500 credits)
- **Trading Signal Generation** - 1,000 credits
- **Automation Helper** - 1,200 credits
- **On-Chain Analysis** - 1,500 credits

---

## 🎓 Skill Categories

### ₿ Crypto
- Crypto Market Analysis
- DeFi Expert
- NFT Advisor

### 📈 Trading
- Trading Signal Generation
- Portfolio Management
- Risk Manager

### 📊 Analysis
- On-Chain Analysis

### 🤖 Automation
- Automation Helper

### 🔍 Research
- Research Assistant

### 💬 General
- Basic Chat

---

## ⚡ Quick Tips

1. **Start with free skills** - Test the system before buying
2. **Install based on needs** - Don't buy all at once
3. **Toggle instead of uninstall** - Keep skills for later
4. **Check usage stats** - See which skills you use most
5. **Buy credits in bulk** - Better value for money

---

## 🆘 Troubleshooting

### "No active session"
**Solution:** Start OpenClaw first
```
/openclaw_start
```

### "Insufficient credits"
**Solution:** Buy more credits
```
/openclaw_buy
```

### "Skill already installed"
**Solution:** Check your installed skills
```
/openclaw_myskills
```

### "Skill not found"
**Solution:** Check the skill ID
```
/openclaw_skills
```

---

## 📞 Need Help?

- General help: `/openclaw_help`
- Check balance: `/openclaw_balance`
- View history: `/openclaw_history`
- Browse skills: `/openclaw_skills`

---

## 🚀 Ready to Start?

```
/openclaw_start
/openclaw_skills
/openclaw_install skill_crypto_analysis
```

Your AI Assistant is about to get a major upgrade! 🎉
