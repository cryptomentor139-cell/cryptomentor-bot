# CryptoMentor Analytics Dashboard - Setup Guide

## Overview

The CryptoMentor Analytics System provides real-time observability of position coordination state, trading performance, and engine health. It consists of:

1. **Analytics Backend API** (`analytics_api.py`) - FastAPI server on port 8896
2. **Analytics Frontend Dashboard** (`analytics_dashboard.html`) - Web-based admin UI
3. **Symbol Coordinator** (`app/symbol_coordinator.py`) - In-memory position coordination

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Admin Browser                             │
│              analytics_dashboard.html                       │
│           (Modern UI, Real-time refresh)                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                   Bearer Token (JWT)
                             │
┌────────────────────────────▼────────────────────────────────┐
│          Analytics Backend API (FastAPI)                    │
│              analytics_api.py (Port 8896)                   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 3 Main Endpoints:                                  │    │
│  │ 1. GET /api/analytics/coordinator-state            │    │
│  │    → Symbol ownership, position metadata           │    │
│  │ 2. GET /api/analytics/trading-stats                │    │
│  │    → Win rate, PnL, daily aggregations             │    │
│  │ 3. GET /api/analytics/engine-health                │    │
│  │    → Engine status, error counts                   │    │
│  └────────────────────────────────────────────────────┘    │
│                          ▲                                  │
│            Queries DB + Coordinator State                  │
└────────────────────────────┼────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   ┌──────▼──────┐  ┌────────▼───────┐  ┌──────▼───────┐
   │  Supabase   │  │ Symbol         │  │ Supabase     │
   │  Database   │  │ Coordinator    │  │ Error Logs   │
   │  (Trades)   │  │ (In-Memory)    │  │              │
   └─────────────┘  └────────────────┘  └──────────────┘
```

## Installation

### 1. Backend Dependencies

Add to `requirements.txt`:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
PyJWT==2.8.1
slowapi==0.1.9
python-dotenv>=1.0.0
```

Install:
```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Add to `.env` (or set in your deployment environment):

```bash
# Admin IDs (same as bot.py)
ADMIN_IDS=123456789      # Space-separated or individual vars
ADMIN1=<REDACTED_ADMIN_ID>
ADMIN2=<REDACTED_ADMIN_ID>

# JWT Secret (optional, default: "analytics-secret-key")
JWT_SECRET=<REDACTED_JWT_SECRET>

# Supabase
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY=<REDACTED_SUPABASE_KEY>

# Analytics Server
ANALYTICS_PORT=8896
ANALYTICS_HOST=0.0.0.0
```

## Deployment

### Option 1: Development (Local Testing)

```bash
# Navigate to Bismillah directory
cd Bismillah

# Run analytics API
python -m uvicorn analytics_api:app --host 0.0.0.0 --port 8896 --reload

# In another terminal, serve the dashboard
# Simple Python server:
cd ..
python -m http.server 8000

# Access dashboard at: http://localhost:8000/Bismillah/analytics_dashboard.html
```

### Option 2: Production (Docker)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Bismillah/ ./Bismillah/

EXPOSE 8896

CMD ["uvicorn", "Bismillah.analytics_api:app", "--host", "0.0.0.0", "--port", "8896"]
```

Build and run:
```bash
docker build -t cryptomentor-analytics .
docker run -e ADMIN_IDS=123456789 -p 8896:8896 cryptomentor-analytics
```

### Option 3: Production (Systemd Service)

Create `/etc/systemd/system/analytics.service`:
```ini
[Unit]
Description=CryptoMentor Analytics API
After=network.target

[Service]
Type=simple
User=cryptomentor
WorkingDirectory=/opt/cryptomentor
Environment="PATH=/opt/cryptomentor/venv/bin"
EnvironmentFile=/opt/cryptomentor/.env
ExecStart=/opt/cryptomentor/venv/bin/uvicorn Bismillah.analytics_api:app --host 0.0.0.0 --port 8896
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable analytics
sudo systemctl start analytics
sudo systemctl status analytics
```

## Frontend Setup

### Option 1: Direct File Access

Open `analytics_dashboard.html` in a browser (works with CORS if API allows it):
```
file:///path/to/Bismillah/analytics_dashboard.html
```

### Option 2: Web Server (Recommended)

Serve via nginx:
```nginx
server {
    listen 443 ssl http2;
    server_name analytics4896.cryptomentor.id;

    ssl_certificate /etc/letsencrypt/live/analytics4896.cryptomentor.id/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/analytics4896.cryptomentor.id/privkey.pem;

    location / {
        alias /opt/cryptomentor/Bismillah/;
        default_type text/html;
        index analytics_dashboard.html;
    }
}
```

Or Apache:
```apache
<VirtualHost *:443>
    ServerName analytics4896.cryptomentor.id
    DocumentRoot /opt/cryptomentor/Bismillah

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/analytics4896.cryptomentor.id/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/analytics4896.cryptomentor.id/privkey.pem

    <Directory /opt/cryptomentor/Bismillah>
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

## Authentication

### Getting Admin JWT Tokens

Tokens are issued by the Telegram bot during login. Admins can:

1. **Get token from bot**: `/start` → login via web → copy JWT from web dashboard URL
2. **Manual token creation** (for testing):

```python
import jwt
import json
from datetime import datetime, timedelta

secret = "analytics-secret-key"
admin_id = 123456789
token = jwt.encode(
    {"sub": str(admin_id), "exp": datetime.utcnow() + timedelta(days=7)},
    secret,
    algorithm="HS256"
)
print(token)
```

### Testing Authentication

```bash
# Health check (no auth)
curl http://localhost:8896/health

# Coordinator state (requires JWT)
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8896/api/analytics/coordinator-state

# With user filter
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  "http://localhost:8896/api/analytics/coordinator-state?user_id=123456789"
```

## Usage

### Accessing the Dashboard

1. Open `https://analytics4896.cryptomentor.id/analytics_dashboard.html`
2. Paste your JWT token in the "Admin JWT Token" field
3. Click "Connect Dashboard"
4. View real-time data with auto-refresh every 30 seconds

### Dashboard Features

#### Coordinator State Panel
Shows current symbol ownership:
- Total symbols managed
- Total users being tracked
- Detailed table with: User ID, Symbol, Owner (SWING/SCALP/etc), Position status, Size, Entry price

#### Engine Health Panel
Monitors engine status:
- 🟢 Running engines count
- 🔴 Stopped engines count
- ⚠️ Errors in last 24 hours

#### Trading Performance Panel
Performance metrics:
- Total trades across all users
- Total PnL (USDT)
- Average win rate (%)

### Filtering

Use the filter inputs to view specific data:
- **User ID**: Filter by specific Telegram user ID
- **Symbol**: Filter by trading pair (e.g., BTCUSDT)

Click "🔍 Filter" to apply or "🔄 Refresh" for manual refresh.

## Monitoring & Troubleshooting

### Check API Status

```bash
curl http://localhost:8896/health
```

Expected response:
```json
{"status": "ok", "timestamp": "2026-04-14T10:30:00+00:00"}
```

### Check Admin IDs Loaded

```bash
# Look for this in logs when API starts:
# [Analytics] Loaded 3 admin IDs
```

### Common Issues

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Token invalid or expired. Re-authenticate. |
| 403 Forbidden | User ID not in ADMIN_ALLOWLIST. Check ADMIN_IDS env var. |
| 500 Service Error | Supabase connection failed. Check SUPABASE_URL and SUPABASE_KEY. |
| Slow dashboard | Increase auto-refresh interval (edit HTML). |
| CORS errors | Ensure API is running with CORS enabled (included by default). |

### Log Monitoring

Watch API logs for errors:
```bash
# If running with systemd:
sudo journalctl -u analytics -f

# If running with docker:
docker logs -f analytics-container

# If running with uvicorn:
# Check console output
```

## Performance Considerations

- **Coordinator queries**: O(1) in-memory lookup, no DB calls
- **Trading stats queries**: May scan many trades if user has long history
- **Rate limiting**: 100 req/minute per authenticated admin
- **Database load**: Minimal, data pulled on-demand from Supabase

## Security

1. **JWT Authentication**: All endpoints except `/health` require valid JWT
2. **Admin Allowlist**: Only users in ADMIN_ALLOWLIST can authenticate
3. **Rate Limiting**: 100 req/minute per admin prevents abuse
4. **HTTPS**: Deploy with SSL/TLS in production
5. **Secrets**: Never expose JWT_SECRET or ADMIN_IDS in version control

## Maintenance

### Backing Up Coordinator State

Coordinator state is in-memory and ephemeral. On bot restart, state is reconciled from:
- Live exchange positions
- DB trade records (open status)

No manual backup needed.

### Clearing Coordinator State

```python
from Bismillah.app.symbol_coordinator import reset_coordinator_for_testing

# Only for testing/debugging:
reset_coordinator_for_testing()
```

## Integration with Trading Engines

The coordinator automatically syncs with:

1. **Swing Engine** (`autotrade_engine.py`):
   - Calls `can_enter()` before order placement
   - Calls `confirm_open()` after successful entry
   - Calls `confirm_closed()` when position closes

2. **Scalping Engine** (`scalping_engine.py`):
   - Calls `can_enter()` before open_managed_position
   - Calls `confirm_open()` after position creation
   - Calls `confirm_closed()` in all close methods

3. **Engine Restore** (`engine_restore.py`):
   - Calls `reconcile_user()` on bot startup
   - Syncs coordinator with exchange positions + DB hints

No manual configuration needed; integration is automatic.

## Support & Debugging

For issues or feature requests:
1. Check logs for error messages
2. Verify environment variables are set correctly
3. Test with curl to isolate API vs frontend issues
4. Consult CHANGELOG.md for version details

---

**Last Updated**: 2026-04-14
**Version**: 2.2.0
**Status**: Production Ready
