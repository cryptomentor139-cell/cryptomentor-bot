# 💰 Custodial Wallet System - Per User Deposit

## 🎯 Concept

Setiap user memiliki **custodial wallet sendiri** untuk deposit "bensin" automaton mereka. Admin tidak perlu isi dulu - user deposit langsung ke wallet mereka sendiri.

### Key Benefits
✅ **Zero Capital Risk** - Admin tidak perlu modal awal
✅ **Scalable** - Unlimited users, unlimited agents
✅ **Transparent** - User lihat balance real-time
✅ **Automated** - Deposit otomatis terdeteksi
✅ **Secure** - Wallet terpisah per user

---

## 🏗️ Architecture

### System Flow

```
User → Deposit USDT/USDC → User's Custodial Wallet
                                    ↓
                          Conway Credits Balance
                                    ↓
                          Agent Consumes Credits
                                    ↓
                          Low Balance → Notify User
```

### Wallet Structure

```
Platform Master Wallet (Admin)
├── User 1 Custodial Wallet
│   ├── Balance: 50 USDT
│   └── Agent 1 (consuming)
├── User 2 Custodial Wallet
│   ├── Balance: 100 USDT
│   └── Agent 2 (consuming)
└── User 3 Custodial Wallet
    ├── Balance: 25 USDT
    └── Agent 3 (consuming)
```

---

## 💾 Database Schema

### Custodial Wallets Table

```sql
CREATE TABLE custodial_wallets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id BIGINT REFERENCES users(telegram_id) UNIQUE,
  wallet_address TEXT UNIQUE NOT NULL,
  private_key_encrypted TEXT NOT NULL, -- Encrypted with master key
  balance_usdt DECIMAL DEFAULT 0,
  balance_usdc DECIMAL DEFAULT 0,
  conway_credits DECIMAL DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  last_deposit_at TIMESTAMP,
  total_deposited DECIMAL DEFAULT 0,
  total_spent DECIMAL DEFAULT 0
);

CREATE INDEX idx_wallet_address ON custodial_wallets(wallet_address);
CREATE INDEX idx_user_id ON custodial_wallets(user_id);
```

### Deposit Transactions Table

```sql
CREATE TABLE wallet_deposits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wallet_id UUID REFERENCES custodial_wallets(id),
  user_id BIGINT REFERENCES users(telegram_id),
  tx_hash TEXT UNIQUE NOT NULL,
  from_address TEXT NOT NULL,
  amount DECIMAL NOT NULL,
  token TEXT NOT NULL, -- 'USDT' or 'USDC'
  network TEXT NOT NULL, -- 'polygon', 'base', 'arbitrum'
  status TEXT DEFAULT 'pending', -- 'pending', 'confirmed', 'failed'
  confirmations INT DEFAULT 0,
  detected_at TIMESTAMP DEFAULT NOW(),
  confirmed_at TIMESTAMP,
  credited_conway DECIMAL -- Amount credited to Conway
);
```

### Withdrawal Requests Table

```sql
CREATE TABLE wallet_withdrawals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wallet_id UUID REFERENCES custodial_wallets(id),
  user_id BIGINT REFERENCES users(telegram_id),
  amount DECIMAL NOT NULL,
  token TEXT NOT NULL,
  to_address TEXT NOT NULL,
  tx_hash TEXT,
  status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
  requested_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP,
  fee DECIMAL DEFAULT 0
);
```

---

## 🔐 Wallet Generation

### On User First Spawn Agent

```python
# app/wallet_manager.py
from eth_account import Account
from cryptography.fernet import Fernet
import os

class WalletManager:
    def __init__(self):
        # Master encryption key (store in env)
        self.cipher = Fernet(os.getenv('WALLET_ENCRYPTION_KEY'))
    
    def create_custodial_wallet(self, user_id: int):
        """Create new custodial wallet for user"""
        # Generate new Ethereum wallet
        account = Account.create()
        
        # Encrypt private key
        encrypted_key = self.cipher.encrypt(
            account.key.hex().encode()
        ).decode()
        
        # Save to database
        wallet = {
            'user_id': user_id,
            'wallet_address': account.address,
            'private_key_encrypted': encrypted_key,
            'balance_usdt': 0,
            'balance_usdc': 0,
            'conway_credits': 0
        }
        
        # Insert to Supabase
        from supabase_client import supabase
        result = supabase.table('custodial_wallets').insert(wallet).execute()
        
        return result.data[0]
    
    def get_user_wallet(self, user_id: int):
        """Get user's custodial wallet"""
        from supabase_client import supabase
        result = supabase.table('custodial_wallets')\
            .select('*')\
            .eq('user_id', user_id)\
            .single()\
            .execute()
        
        return result.data if result.data else None
    
    def decrypt_private_key(self, encrypted_key: str) -> str:
        """Decrypt private key for transactions"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

---

## 💸 Deposit Detection

### Blockchain Monitoring Service

```python
# app/deposit_monitor.py
from web3 import Web3
import asyncio

class DepositMonitor:
    def __init__(self):
        # Connect to Polygon (cheap gas)
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('POLYGON_RPC_URL')))
        
        # USDT/USDC contract addresses on Polygon
        self.usdt_address = '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'
        self.usdc_address = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
        
        # Load contract ABIs
        self.usdt_contract = self.w3.eth.contract(
            address=self.usdt_address,
            abi=self._load_erc20_abi()
        )
        self.usdc_contract = self.w3.eth.contract(
            address=self.usdc_address,
            abi=self._load_erc20_abi()
        )
    
    async def monitor_deposits(self):
        """Monitor all custodial wallets for deposits"""
        while True:
            try:
                # Get all custodial wallets
                wallets = self._get_all_wallets()
                
                for wallet in wallets:
                    # Check USDT balance
                    usdt_balance = self._check_token_balance(
                        wallet['wallet_address'],
                        self.usdt_contract
                    )
                    
                    # Check USDC balance
                    usdc_balance = self._check_token_balance(
                        wallet['wallet_address'],
                        self.usdc_contract
                    )
                    
                    # If balance increased, process deposit
                    if usdt_balance > wallet['balance_usdt']:
                        await self._process_deposit(
                            wallet,
                            usdt_balance - wallet['balance_usdt'],
                            'USDT'
                        )
                    
                    if usdc_balance > wallet['balance_usdc']:
                        await self._process_deposit(
                            wallet,
                            usdc_balance - wallet['balance_usdc'],
                            'USDC'
                        )
                
                # Check every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"Deposit monitor error: {e}")
                await asyncio.sleep(60)
    
    def _check_token_balance(self, address: str, contract) -> float:
        """Check ERC20 token balance"""
        balance_wei = contract.functions.balanceOf(address).call()
        return balance_wei / 10**6  # USDT/USDC have 6 decimals
    
    async def _process_deposit(self, wallet, amount: float, token: str):
        """Process detected deposit"""
        print(f"💰 Deposit detected: {amount} {token} to {wallet['wallet_address']}")
        
        # Update wallet balance
        from supabase_client import supabase
        supabase.table('custodial_wallets').update({
            f'balance_{token.lower()}': amount,
            'last_deposit_at': 'NOW()',
            'total_deposited': wallet['total_deposited'] + amount
        }).eq('id', wallet['id']).execute()
        
        # Convert to Conway credits (1 USDT = 100 Conway credits)
        conway_credits = amount * 100
        
        # Credit Conway account
        await self._credit_conway(wallet, conway_credits)
        
        # Notify user
        await self._notify_user_deposit(
            wallet['user_id'],
            amount,
            token,
            conway_credits
        )
    
    async def _credit_conway(self, wallet, credits: float):
        """Credit Conway credits to user's agent"""
        # Call Conway API to add credits
        # Implementation depends on Conway API
        pass
    
    async def _notify_user_deposit(self, user_id: int, amount: float, 
                                   token: str, conway_credits: float):
        """Send Telegram notification to user"""
        from telegram import Bot
        bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        
        message = f"""✅ Deposit Confirmed!

💰 Amount: {amount:.2f} {token}
🔄 Converted: {conway_credits:.0f} Conway Credits
⚡ Your agent is now fueled!

Use /agent_status to check balance."""
        
        await bot.send_message(chat_id=user_id, text=message)
```

---

## 📱 User Commands

### 1. Get Deposit Address

```python
# /deposit or button "💰 Deposit"
async def deposit_command(update, context):
    user_id = update.effective_user.id
    
    # Get or create wallet
    wallet = wallet_manager.get_user_wallet(user_id)
    if not wallet:
        wallet = wallet_manager.create_custodial_wallet(user_id)
    
    # Generate QR code for deposit address
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={wallet['wallet_address']}"
    
    message = f"""💰 **Deposit Address**

Send USDT or USDC to this address:

`{wallet['wallet_address']}`

**Supported Networks:**
• Polygon (Recommended - Low fees)
• Base
• Arbitrum

**Conversion Rate:**
1 USDT = 100 Conway Credits
1 USDC = 100 Conway Credits

**Minimum Deposit:** 5 USDT

⚠️ Only send USDT/USDC! Other tokens will be lost.

Deposits are detected automatically within 1-2 minutes."""
    
    await update.message.reply_photo(
        photo=qr_code_url,
        caption=message,
        parse_mode='MARKDOWN'
    )
```

### 2. Check Balance

```python
# /balance or button "💰 Balance"
async def balance_command(update, context):
    user_id = update.effective_user.id
    
    wallet = wallet_manager.get_user_wallet(user_id)
    if not wallet:
        await update.message.reply_text(
            "❌ No wallet found. Use /spawn_agent to create one."
        )
        return
    
    message = f"""💰 **Your Wallet Balance**

**Custodial Wallet:**
`{wallet['wallet_address']}`

**Balances:**
• USDT: {wallet['balance_usdt']:.2f}
• USDC: {wallet['balance_usdc']:.2f}
• Conway Credits: {wallet['conway_credits']:.0f}

**Statistics:**
• Total Deposited: ${wallet['total_deposited']:.2f}
• Total Spent: ${wallet['total_spent']:.2f}
• Net Balance: ${wallet['total_deposited'] - wallet['total_spent']:.2f}

**Agent Status:**
• Survival Tier: {get_agent_tier(wallet['conway_credits'])}
• Estimated Runtime: {estimate_runtime(wallet['conway_credits'])} days

Use /deposit to add more funds."""
    
    await update.message.reply_text(message, parse_mode='MARKDOWN')
```

### 3. Withdraw (Optional)

```python
# /withdraw <amount> <address>
async def withdraw_command(update, context):
    user_id = update.effective_user.id
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /withdraw <amount> <address>\n"
            "Example: /withdraw 10 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        )
        return
    
    amount = float(context.args[0])
    to_address = context.args[1]
    
    wallet = wallet_manager.get_user_wallet(user_id)
    
    # Check balance
    if wallet['balance_usdt'] < amount:
        await update.message.reply_text(
            f"❌ Insufficient balance!\n"
            f"Available: {wallet['balance_usdt']:.2f} USDT"
        )
        return
    
    # Minimum withdrawal
    if amount < 10:
        await update.message.reply_text(
            "❌ Minimum withdrawal: 10 USDT"
        )
        return
    
    # Create withdrawal request
    withdrawal = create_withdrawal_request(
        wallet_id=wallet['id'],
        user_id=user_id,
        amount=amount,
        to_address=to_address
    )
    
    await update.message.reply_text(
        f"✅ Withdrawal request created!\n\n"
        f"Amount: {amount:.2f} USDT\n"
        f"To: `{to_address}`\n"
        f"Fee: 1 USDT\n"
        f"You'll receive: {amount - 1:.2f} USDT\n\n"
        f"Processing time: 1-24 hours\n"
        f"Request ID: `{withdrawal['id']}`",
        parse_mode='MARKDOWN'
    )
```

---

## 🔄 Conway Credits Integration

### Auto-Funding Agent

```python
# app/conway_integration.py
class ConwayIntegration:
    def __init__(self):
        self.api_key = os.getenv('CONWAY_API_KEY')
        self.base_url = 'https://api.conway.tech'
    
    async def fund_agent(self, agent_wallet: str, amount: float):
        """Fund agent's Conway account"""
        # Transfer from custodial wallet to agent wallet
        # This happens automatically when user deposits
        
        response = requests.post(
            f'{self.base_url}/credits/transfer',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json={
                'to_wallet': agent_wallet,
                'amount': amount,
                'currency': 'USDT'
            }
        )
        
        return response.json()
    
    async def check_agent_balance(self, agent_wallet: str):
        """Check agent's Conway credits"""
        response = requests.get(
            f'{self.base_url}/credits/balance',
            headers={'Authorization': f'Bearer {self.api_key}'},
            params={'wallet': agent_wallet}
        )
        
        return response.json()
```

---

## 📊 Admin Dashboard

### Monitor All Wallets

```python
# /admin_wallets (admin only)
async def admin_wallets_command(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    # Get all wallets summary
    from supabase_client import supabase
    result = supabase.table('custodial_wallets')\
        .select('*')\
        .execute()
    
    wallets = result.data
    
    total_usdt = sum(w['balance_usdt'] for w in wallets)
    total_usdc = sum(w['balance_usdc'] for w in wallets)
    total_deposited = sum(w['total_deposited'] for w in wallets)
    total_spent = sum(w['total_spent'] for w in wallets)
    
    message = f"""📊 **Custodial Wallets Summary**

**Total Wallets:** {len(wallets)}

**Total Balances:**
• USDT: ${total_usdt:,.2f}
• USDC: ${total_usdc:,.2f}
• Total: ${total_usdt + total_usdc:,.2f}

**All-Time Stats:**
• Total Deposited: ${total_deposited:,.2f}
• Total Spent: ${total_spent:,.2f}
• Platform Revenue: ${(total_deposited - total_spent) * 0.1:,.2f}

**Active Agents:** {count_active_agents()}
**Survival Rate:** {calculate_survival_rate()}%

Use /admin_wallet_details <user_id> for specific wallet."""
    
    await update.message.reply_text(message, parse_mode='MARKDOWN')
```

---

## 🚨 Low Balance Alerts

### Automatic Notifications

```python
# app/balance_monitor.py
async def monitor_low_balances():
    """Alert users when balance is low"""
    while True:
        try:
            # Get all wallets
            wallets = get_all_wallets()
            
            for wallet in wallets:
                conway_credits = wallet['conway_credits']
                
                # Critical: < 1000 credits (1 day runtime)
                if conway_credits < 1000 and conway_credits > 0:
                    await send_low_balance_alert(
                        wallet['user_id'],
                        conway_credits,
                        'critical'
                    )
                
                # Warning: < 5000 credits (5 days runtime)
                elif conway_credits < 5000:
                    await send_low_balance_alert(
                        wallet['user_id'],
                        conway_credits,
                        'warning'
                    )
            
            # Check every hour
            await asyncio.sleep(3600)
            
        except Exception as e:
            print(f"Balance monitor error: {e}")
            await asyncio.sleep(3600)

async def send_low_balance_alert(user_id: int, balance: float, level: str):
    """Send low balance notification"""
    from telegram import Bot
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    
    if level == 'critical':
        emoji = "🚨"
        message = f"""{emoji} **CRITICAL: Low Balance!**

Your agent is running out of fuel!

💰 Current Balance: {balance:.0f} Conway Credits
⏱️ Estimated Runtime: < 1 day

⚠️ Your agent will stop if balance reaches 0!

Use /deposit to add funds immediately."""
    
    else:  # warning
        emoji = "⚠️"
        message = f"""{emoji} **Warning: Low Balance**

Your agent balance is getting low.

💰 Current Balance: {balance:.0f} Conway Credits
⏱️ Estimated Runtime: ~{balance/200:.1f} days

Consider depositing more funds to keep your agent running.

Use /deposit to add funds."""
    
    await bot.send_message(chat_id=user_id, text=message, parse_mode='MARKDOWN')
```

---

## 💡 Pricing & Economics

### Conversion Rates

**Deposit to Conway:**
- 1 USDT = 100 Conway Credits
- 1 USDC = 100 Conway Credits

**Conway Consumption:**
- Normal tier: ~200 credits/day
- Low compute: ~100 credits/day
- Critical: ~50 credits/day

**Minimum Deposits:**
- Minimum: 5 USDT (500 credits = 2.5 days)
- Recommended: 20 USDT (2000 credits = 10 days)
- Optimal: 50 USDT (5000 credits = 25 days)

### Platform Revenue

**Revenue Streams:**
1. **Deposit Fee**: 2% on deposits (optional)
2. **Withdrawal Fee**: 1 USDT flat fee
3. **Performance Fee**: 20% of agent profits
4. **Conversion Spread**: 1% on USDT→Conway conversion

**Example Revenue (100 users):**
- Average deposit: 20 USDT/user/month
- Total deposits: 2000 USDT/month
- Deposit fees (2%): 40 USDT/month
- Performance fees: ~200 USDT/month (estimated)
- **Total**: ~240 USDT/month (~Rp3,600,000)

**At Scale (1000 users):**
- Total deposits: 20,000 USDT/month
- Deposit fees: 400 USDT/month
- Performance fees: ~2000 USDT/month
- **Total**: ~2400 USDT/month (~Rp36,000,000)

---

## 🔒 Security Measures

### Wallet Security

1. **Encryption**: All private keys encrypted with Fernet
2. **Master Key**: Stored in Railway secrets, never in code
3. **Key Rotation**: Rotate master key every 90 days
4. **Access Control**: Only wallet_manager can decrypt keys
5. **Audit Logs**: All transactions logged

### Transaction Security

1. **Withdrawal Limits**: Max 1000 USDT per withdrawal
2. **Daily Limits**: Max 3 withdrawals per day
3. **Verification**: Email/2FA for large withdrawals (>100 USDT)
4. **Whitelist**: Users can whitelist withdrawal addresses
5. **Cooldown**: 24h cooldown for new withdrawal addresses

### Monitoring

1. **Anomaly Detection**: Flag unusual deposit/withdrawal patterns
2. **Balance Checks**: Verify on-chain balance matches DB
3. **Transaction Verification**: Confirm all txs on blockchain
4. **Alert System**: Notify admin of suspicious activity

---

## 🚀 Implementation Checklist

### Phase 1: Core Infrastructure (Week 1)
- [ ] Create database schema
- [ ] Implement wallet generation
- [ ] Set up encryption system
- [ ] Deploy deposit monitor
- [ ] Test on testnet

### Phase 2: User Interface (Week 2)
- [ ] Add /deposit command
- [ ] Add /balance command
- [ ] Add /withdraw command
- [ ] Create QR code generation
- [ ] Add balance notifications

### Phase 3: Conway Integration (Week 3)
- [ ] Integrate Conway API
- [ ] Auto-fund agents on deposit
- [ ] Monitor agent consumption
- [ ] Implement low balance alerts
- [ ] Test full flow

### Phase 4: Security & Testing (Week 4)
- [ ] Security audit
- [ ] Penetration testing
- [ ] Load testing
- [ ] Beta testing with 10 users
- [ ] Fix bugs and optimize

### Phase 5: Launch (Week 5)
- [ ] Deploy to production
- [ ] Monitor closely
- [ ] Collect user feedback
- [ ] Iterate and improve

---

## 📈 Success Metrics

### KPIs to Track

**User Adoption:**
- Wallets created per week
- Average deposit amount
- Deposit frequency
- Active wallets (deposited in last 30 days)

**Financial:**
- Total deposits (all-time)
- Total balance (current)
- Average wallet balance
- Platform revenue

**Agent Performance:**
- Agent survival rate
- Average runtime per deposit
- Credits consumed per day
- User satisfaction

### Target Metrics (Month 3)
- 200+ wallets created
- $10,000+ total deposits
- 70% active wallet rate
- $500+ monthly revenue

---

**Status**: 📋 Ready for Implementation
**Risk Level**: Low (user funds their own wallet)
**Capital Required**: $0 (users deposit directly)
**Timeline**: 5 weeks to production
**ROI**: Immediate (fees on every deposit)

🚀 **Zero capital risk, infinite scalability!**
