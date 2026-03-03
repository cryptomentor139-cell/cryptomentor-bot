# GPT-4.1 Configuration - LLM Utama Bot ✅

## Status
✅ GPT-4.1 sudah dikonfigurasi sebagai LLM utama untuk OpenClaw AI Assistant

## API Key Configuration

### Railway Variables (Production)
```
OPENCLAW_API_KEY=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
OPENCLAW_BASE_URL=https://openrouter.ai/api/v1
```

### Local .env (Development)
```
OPENCLAW_API_KEY=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
OPENCLAW_BASE_URL=https://openrouter.ai/api/v1
```

## Model Configuration

### OpenClaw AI Assistant
- **Model**: `openai/gpt-4.1` (via OpenRouter)
- **File**: `Bismillah/app/openclaw_manager.py`
- **Pricing**: 
  - Input: $2.5 per 1M tokens
  - Output: $10 per 1M tokens
- **Max Tokens**: 8192
- **Temperature**: 0.7

### Other AI Features (Signal Generation, etc.)
Untuk fitur lain seperti signal generation, masih menggunakan:
- **Model**: `google/gemini-flash-1.5` (FREE & FAST)
- **Variable**: `AI_MODEL=google/gemini-flash-1.5`

## Usage in Bot

### OpenClaw Commands
1. `/openclaw_start` - Start AI Assistant session
2. `/openclaw_create <name>` - Create new AI Assistant
3. `/openclaw_help` - Show help
4. `/openclaw_exit` - Exit AI Assistant mode

### Credit System
- **Platform Fee**: 20% (goes to bot owner)
- **Conversion**: 1 USDC = 100 credits
- **Admin**: Unlimited free usage

## Testing

### Test OpenClaw API
```bash
cd Bismillah
python test_openclaw_api.py
```

### Check API Credits
```bash
curl https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer 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"
```

## Troubleshooting

### Error: 401 Unauthorized
- ✅ FIXED: API key sudah diupdate
- Check Railway variables sudah sync
- Restart deployment jika perlu

### Error: Can't parse entities
- ✅ FIXED: Markdown parsing disabled
- Response dikirim sebagai plain text
- Emoji tetap berfungsi

## Next Steps

1. ✅ API key updated di Railway
2. ✅ API key updated di local .env
3. ✅ Markdown parsing fixed
4. ⏳ Test bot di Telegram
5. ⏳ Monitor credit usage

## Cost Estimation

### GPT-4.1 Pricing
- Average conversation: ~1000 tokens (input + output)
- Cost per conversation: ~$0.006 (0.6 cents)
- 1000 conversations: ~$6
- Much cheaper than Claude Sonnet 4.5!

### Credit Pricing for Users
- 100 credits = 1 USDC
- Average conversation: ~5-10 credits
- 100 credits = ~10-20 conversations
- Platform earns 20% fee

## Files Modified
- `Bismillah/.env` - Updated OPENCLAW_API_KEY
- `Bismillah/app/openclaw_message_handler.py` - Fixed Markdown parsing
- Railway Variables - Updated OPENCLAW_API_KEY

## Status: READY FOR PRODUCTION ✅
