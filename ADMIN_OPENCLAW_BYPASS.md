# 🔓 Admin OpenClaw Bypass - Implementation Guide

## Tujuan

Admin harus punya unlimited access ke OpenClaw tanpa perlu credits.

## Implementation

### 1. Add Admin Check Method

Edit `app/openclaw_manager.py`:

```python
def _is_admin(self, user_id: int) -> bool:
    """Check if user is admin"""
    # Get admin IDs from environment
    admin_ids = set()
    for key in ['ADMIN1', 'ADMIN2', 'ADMIN3', 'ADMIN_IDS']:
        value = os.getenv(key)
        if value:
            try:
                if ',' in value:
                    admin_ids.update(int(aid.strip()) for aid in value.split(',') if aid.strip())
                else:
                    admin_ids.add(int(value))
            except ValueError:
                continue
    
    return user_id in admin_ids
```

### 2. Modify Chat Method

Edit `chat()` method in `app/openclaw_manager.py`:

```python
def chat(self, user_id, assistant_id, message, conversation_id=None):
    # ... existing code ...
    
    # Calculate cost
    credits_cost = self._calculate_credits_cost(input_tokens, output_tokens)
    
    # Check if user is admin
    is_admin = self._is_admin(user_id)
    
    if not is_admin:
        # Regular user: check and deduct credits
        user_credits = self._get_user_credits(user_id)
        if user_credits < credits_cost:
            raise ValueError(
                f"Insufficient credits. Balance: {user_credits}, Required: {credits_cost}"
            )
        
        # Deduct credits
        self._deduct_credits(
            user_id=user_id,
            credits=credits_cost,
            conversation_id=conversation_id,
            description=f"Chat with {assistant['name']}: {input_tokens}+{output_tokens} tokens"
        )
    else:
        # Admin: no credit check/deduction
        logger.info(f"Admin {user_id} using OpenClaw (no charge)")
        credits_cost = 0  # Show 0 cost for admin
    
    # ... rest of code ...
```

### 3. Update Message Handler

Edit `app/openclaw_message_handler.py`:

```python
async def handle_message(self, update, context):
    # ... existing code ...
    
    # Check if user is admin
    from services import get_database
    db = get_database()
    
    # Get admin IDs
    admin_ids = set()
    for key in ['ADMIN1', 'ADMIN2', 'ADMIN3']:
        value = os.getenv(key)
        if value:
            try:
                admin_ids.add(int(value))
            except:
                pass
    
    is_admin = user_id in admin_ids
    
    if not is_admin:
        # Check user credits
        user_credits = self.manager.get_user_credits(user_id)
        
        if user_credits < 1:
            await update.message.reply_text(
                "❌ **Insufficient Credits**\n\n"
                "You need credits to chat with your AI Assistant.\n\n"
                "💰 Purchase credits: /openclaw_buy\n"
                "🔙 Exit OpenClaw mode: /openclaw_exit",
                parse_mode=ParseMode.MARKDOWN
            )
            return True
    
    # ... rest of code ...
    
    # Format response
    if is_admin:
        footer = f"\n\n💬 {input_tokens + output_tokens} tokens • 👑 Admin (Free)"
    else:
        footer = f"\n\n💬 {input_tokens + output_tokens} tokens • 💰 {credits_cost} credits • Balance: {user_credits - credits_cost}"
```

### 4. Update Create Command

Edit `openclaw_create_command()` in `app/openclaw_message_handler.py`:

```python
async def openclaw_create_command(update, context):
    user_id = update.effective_user.id
    
    # Check if admin
    admin_ids = set()
    for key in ['ADMIN1', 'ADMIN2', 'ADMIN3']:
        value = os.getenv(key)
        if value:
            try:
                admin_ids.add(int(value))
            except:
                pass
    
    is_admin = user_id in admin_ids
    
    # ... existing code ...
    
    try:
        assistant = manager.create_assistant(
            user_id=user_id,
            name=name,
            personality=personality
        )
        
        if is_admin:
            await update.message.reply_text(
                f"✅ **AI Assistant Created!**\n\n"
                f"🤖 Name: {assistant['name']}\n"
                f"🎭 Personality: {assistant['personality']}\n"
                f"🆔 ID: `{assistant['assistant_id']}`\n"
                f"👑 **Admin Mode: Unlimited Access**\n\n"
                f"💬 Start chatting: /openclaw_start",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                f"✅ **AI Assistant Created!**\n\n"
                f"🤖 Name: {assistant['name']}\n"
                f"🎭 Personality: {assistant['personality']}\n"
                f"🆔 ID: `{assistant['assistant_id']}`\n\n"
                f"💬 Start chatting: /openclaw_start\n"
                f"💰 Buy credits: /openclaw_buy",
                parse_mode=ParseMode.MARKDOWN
            )
```

## Quick Implementation Script

Saya sudah buat file `implement_admin_bypass.py` yang akan otomatis implement semua changes di atas.

Run:
```bash
python implement_admin_bypass.py
```

## Testing

### As Admin:
```
/openclaw_create AdminBot friendly
/openclaw_start
Hello, test admin access
```

Expected: Chat works, shows "Admin (Free)" instead of credit cost

### As Regular User:
```
/openclaw_create UserBot friendly
/openclaw_buy
/openclaw_start
Hello
```

Expected: Shows credit cost and deducts from balance

## Deploy

After implementation:
```bash
git add app/openclaw_manager.py app/openclaw_message_handler.py
git commit -m "feat: add admin bypass for OpenClaw unlimited access"
git push origin main
railway up
```

## Summary

- ✅ Admin gets unlimited OpenClaw access
- ✅ No credit check for admin
- ✅ No credit deduction for admin
- ✅ Shows "Admin (Free)" in responses
- ✅ Regular users still pay credits
- ✅ Platform fee still applies to user purchases
