# 🚀 IMPLEMENTASI CEO AGENT - AUTOMATON INDUK

## OVERVIEW

Dokumen ini menjelaskan cara mengimplementasikan AUTOMATON Induk (CEO Agent) untuk CryptoMentor AI.

## ARSITEKTUR

```
┌─────────────────────────────────────────┐
│     CRYPTOMENTOR AI ECOSYSTEM           │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────┐     │
│  │   AUTOMATON INDUK (CEO)       │     │
│  │   - Business Management       │     │
│  │   - User Follow-up            │     │
│  │   - Marketing & Growth        │     │
│  │   - Analytics & Reporting     │     │
│  └───────────────┬───────────────┘     │
│                  │                      │
│                  │ Manages              │
│                  ▼                      │
│  ┌───────────────────────────────┐     │
│  │   CHILD AGENTS (User Owned)   │     │
│  │   - Agent 1: User A           │     │
│  │   - Agent 2: User B           │     │
│  │   - Agent 3: User C           │     │
│  │   - ...                       │     │
│  └───────────────────────────────┘     │
│                                         │
└─────────────────────────────────────────┘
```

## CARA SPAWN CEO AGENT

### Option 1: Via Conway API (Recommended)

```python
import requests
import os

# Conway API credentials
CONWAY_API_KEY = os.getenv('CONWAY_API_KEY')
CONWAY_WALLET_ADDRESS = os.getenv('CONWAY_WALLET_ADDRESS')

# Spawn CEO Agent
def spawn_ceo_agent():
    url = "https://api.conway.so/v1/agents"
    
    # Load prompt dari file
    with open('AUTOMATON_INDUK_PROMPT.md', 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    
    payload = {
        "name": "CryptoMentor CEO Agent",
        "description": "AI Agent CEO untuk mengelola bisnis CryptoMentor AI",
        "system_prompt": system_prompt,
        "model": "gpt-4-turbo",  # atau model lain yang didukung
        "temperature": 0.7,
        "max_tokens": 2000,
        "owner_wallet": CONWAY_WALLET_ADDRESS,
        "is_public": False,  # Private agent untuk internal use
        "capabilities": [
            "text_generation",
            "data_analysis",
            "scheduling",
            "notifications"
        ],
        "metadata": {
            "type": "induk",
            "role": "ceo",
            "company": "CryptoMentor AI",
            "language": "id"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {CONWAY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        agent_data = response.json()
        agent_id = agent_data['agent_id']
        print(f"✅ CEO Agent spawned successfully!")
        print(f"   Agent ID: {agent_id}")
        return agent_id
    else:
        print(f"❌ Failed to spawn CEO Agent: {response.text}")
        return None

# Execute
if __name__ == "__main__":
    ceo_agent_id = spawn_ceo_agent()
    
    # Save agent ID untuk reference
    if ceo_agent_id:
        with open('.env', 'a') as f:
            f.write(f"\nCEO_AGENT_ID={ceo_agent_id}\n")
```

### Option 2: Via Bot Command (Admin Only)

```python
# Di bot.py, tambahkan command untuk admin

async def spawn_ceo_agent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Spawn CEO Agent - Admin only"""
    user_id = update.effective_user.id
    
    # Check admin
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin only command!")
        return
    
    try:
        # Load prompt
        with open('AUTOMATON_INDUK_PROMPT.md', 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        
        # Spawn via Conway API
        from app.conway_integration import spawn_agent
        
        agent_id = spawn_agent(
            name="CryptoMentor CEO Agent",
            prompt=system_prompt,
            owner_id=user_id,
            agent_type="induk"
        )
        
        if agent_id:
            await update.message.reply_text(
                f"✅ CEO Agent spawned!\n\n"
                f"🆔 Agent ID: `{agent_id}`\n"
                f"🤖 Type: AUTOMATON Induk\n"
                f"👔 Role: CEO\n\n"
                f"Agent siap mengelola bisnis CryptoMentor AI!",
                parse_mode='MARKDOWN'
            )
            
            # Save to database
            db = get_database()
            db.save_ceo_agent(agent_id, user_id)
        else:
            await update.message.reply_text("❌ Failed to spawn CEO Agent!")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# Register command
application.add_handler(CommandHandler("spawn_ceo_agent", spawn_ceo_agent_command))
```

## INTEGRASI DENGAN BOT

### 1. Auto Follow-Up System

```python
# app/ceo_agent_tasks.py

import asyncio
from datetime import datetime, timedelta
from services import get_database

async def auto_followup_new_users(bot, ceo_agent_id):
    """Follow-up user baru yang belum deposit"""
    db = get_database()
    
    # Get users registered in last 24 hours
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    new_users = db.get_users_since(cutoff_time)
    
    for user in new_users:
        user_id = user['telegram_id']
        user_name = user['first_name']
        
        # Check if already has AUTOMATON credits
        credits = db.get_automaton_credits(user_id)
        
        if credits < 3000:  # Belum deposit minimum
            # Generate personalized message via CEO Agent
            message = await generate_followup_message(
                ceo_agent_id,
                user_name,
                user['created_at']
            )
            
            # Send message
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='MARKDOWN'
                )
                print(f"✅ Follow-up sent to {user_name} ({user_id})")
            except Exception as e:
                print(f"❌ Failed to send to {user_id}: {e}")
            
            # Rate limiting
            await asyncio.sleep(2)

async def generate_followup_message(agent_id, user_name, signup_date):
    """Generate personalized follow-up via CEO Agent"""
    from app.conway_integration import chat_with_agent
    
    prompt = f"""
    Generate follow-up message untuk user baru:
    - Nama: {user_name}
    - Signup: {signup_date}
    - Status: Belum deposit
    
    Gunakan template follow-up yang friendly dan helpful.
    """
    
    response = await chat_with_agent(agent_id, prompt)
    return response

# Schedule task
async def start_ceo_agent_tasks(bot):
    """Start all CEO Agent automated tasks"""
    ceo_agent_id = os.getenv('CEO_AGENT_ID')
    
    if not ceo_agent_id:
        print("⚠️ CEO Agent not configured!")
        return
    
    print("🤖 Starting CEO Agent tasks...")
    
    while True:
        try:
            # Follow-up new users every 6 hours
            await auto_followup_new_users(bot, ceo_agent_id)
            
            # Wait 6 hours
            await asyncio.sleep(6 * 60 * 60)
            
        except Exception as e:
            print(f"❌ CEO Agent task error: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute
```

### 2. Daily Metrics Report

```python
# app/ceo_agent_reports.py

async def generate_daily_report(ceo_agent_id):
    """Generate daily business report"""
    db = get_database()
    
    # Collect metrics
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    
    metrics = {
        'new_users': db.count_users_on_date(today),
        'active_users': db.count_active_users(today),
        'premium_users': db.count_premium_users(),
        'deposits': db.sum_deposits_on_date(today),
        'revenue': db.sum_revenue_on_date(today),
        'agents_spawned': db.count_agents_spawned_on_date(today),
        'active_agents': db.count_active_agents()
    }
    
    # Generate report via CEO Agent
    from app.conway_integration import chat_with_agent
    
    prompt = f"""
    Generate daily report dengan data berikut:
    {metrics}
    
    Gunakan format laporan harian yang sudah ada di prompt.
    Tambahkan insights dan action items.
    """
    
    report = await chat_with_agent(ceo_agent_id, prompt)
    
    # Send to admin
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=report,
                parse_mode='MARKDOWN'
            )
        except Exception as e:
            print(f"Failed to send report to {admin_id}: {e}")
    
    return report

# Schedule daily at 21:00
async def schedule_daily_report(bot, ceo_agent_id):
    """Schedule daily report generation"""
    while True:
        now = datetime.utcnow()
        
        # Calculate next 21:00 UTC
        next_run = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if now.hour >= 21:
            next_run += timedelta(days=1)
        
        # Wait until next run
        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        
        # Generate report
        try:
            await generate_daily_report(ceo_agent_id)
        except Exception as e:
            print(f"❌ Daily report error: {e}")
```

### 3. User Inquiry Handler

```python
# app/ceo_agent_support.py

async def handle_user_inquiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user inquiry via CEO Agent"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    message = update.message.text
    
    ceo_agent_id = os.getenv('CEO_AGENT_ID')
    
    if not ceo_agent_id:
        # Fallback to standard response
        await update.message.reply_text(
            "Terima kasih! Tim kami akan segera membantu Anda."
        )
        return
    
    # Get user context
    db = get_database()
    user_data = db.get_user(user_id)
    
    # Generate response via CEO Agent
    from app.conway_integration import chat_with_agent
    
    prompt = f"""
    User inquiry dari:
    - Nama: {user_name}
    - User ID: {user_id}
    - Premium: {user_data.get('is_premium', False)}
    - Credits: {user_data.get('credits', 0)}
    
    Pertanyaan: {message}
    
    Berikan response yang helpful dan personal.
    """
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=user_id,
        action='typing'
    )
    
    response = await chat_with_agent(ceo_agent_id, prompt)
    
    await update.message.reply_text(
        response,
        parse_mode='MARKDOWN'
    )

# Register handler
application.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    handle_user_inquiry
))
```

## MONITORING & ANALYTICS

### Dashboard Metrics

```python
# app/ceo_dashboard.py

def get_ceo_dashboard_metrics():
    """Get real-time metrics for CEO dashboard"""
    db = get_database()
    
    return {
        'users': {
            'total': db.count_total_users(),
            'active_today': db.count_active_users_today(),
            'new_today': db.count_new_users_today(),
            'premium': db.count_premium_users()
        },
        'revenue': {
            'today': db.sum_revenue_today(),
            'this_week': db.sum_revenue_this_week(),
            'this_month': db.sum_revenue_this_month(),
            'mrr': db.calculate_mrr()
        },
        'agents': {
            'total_spawned': db.count_total_agents(),
            'active': db.count_active_agents(),
            'total_trades': db.count_total_trades()
        },
        'engagement': {
            'messages_today': db.count_messages_today(),
            'commands_used': db.count_commands_today(),
            'avg_session_time': db.avg_session_time_today()
        },
        'health': {
            'churn_rate': db.calculate_churn_rate(),
            'conversion_rate': db.calculate_conversion_rate(),
            'retention_rate': db.calculate_retention_rate(),
            'nps': db.calculate_nps()
        }
    }

# API endpoint for dashboard
@app.route('/api/ceo/dashboard')
async def ceo_dashboard_api():
    """API endpoint for CEO dashboard"""
    metrics = get_ceo_dashboard_metrics()
    return jsonify(metrics)
```

## TESTING

### Test CEO Agent Response

```python
# test_ceo_agent.py

import asyncio
from app.conway_integration import chat_with_agent

async def test_ceo_agent():
    """Test CEO Agent responses"""
    ceo_agent_id = os.getenv('CEO_AGENT_ID')
    
    test_scenarios = [
        "User baru signup, belum deposit. Generate follow-up message.",
        "User komplain tentang slow response. Handle complaint.",
        "Generate daily report untuk hari ini.",
        "User bertanya cara deposit USDC. Berikan panduan.",
        "Analisis conversion rate minggu ini dan berikan insights."
    ]
    
    for scenario in test_scenarios:
        print(f"\n📝 Scenario: {scenario}")
        print("─" * 50)
        
        response = await chat_with_agent(ceo_agent_id, scenario)
        print(f"🤖 Response:\n{response}\n")
        
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_ceo_agent())
```

## DEPLOYMENT CHECKLIST

- [ ] CEO Agent prompt file ready (`AUTOMATON_INDUK_PROMPT.md`)
- [ ] Conway API credentials configured
- [ ] Spawn CEO Agent via API or command
- [ ] Save CEO Agent ID to `.env`
- [ ] Integrate auto follow-up system
- [ ] Setup daily report generation
- [ ] Configure user inquiry handler
- [ ] Test all CEO Agent functions
- [ ] Monitor performance and adjust
- [ ] Document any customizations

## MAINTENANCE

### Weekly Tasks
- Review CEO Agent performance
- Analyze user feedback
- Adjust prompts if needed
- Check automation tasks
- Update metrics targets

### Monthly Tasks
- Comprehensive performance review
- Update roadmap progress
- Refine communication templates
- Optimize automation workflows
- Strategic planning session

## TROUBLESHOOTING

### CEO Agent Not Responding
1. Check Conway API status
2. Verify agent ID is correct
3. Check API credits balance
4. Review error logs
5. Test with simple prompt

### Follow-Up Not Sending
1. Check bot permissions
2. Verify user IDs are valid
3. Review rate limiting
4. Check database queries
5. Test manually first

### Reports Not Generated
1. Check scheduled task is running
2. Verify database connections
3. Review metric calculations
4. Check admin IDs
5. Test report generation manually

---

**Status**: Ready for deployment
**Last Updated**: 2026-02-22
**Version**: 1.0.0
