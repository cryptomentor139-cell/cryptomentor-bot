# Quick Start - License System Testing

## Prerequisites

✅ Python 3.10+ installed
✅ Dependencies installed: `cd license_server && pip install -r requirements.txt`

---

## Step 1: Start License API (Terminal 1)

```bash
cd license_server
python license_api.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

---

## Step 2: Test License API (Terminal 2)

```bash
python test_license_local.py
```

Expected output:
```
✅ License check berhasil!
   Valid: True
   Status: active
   Expires in: 29 days
   Balance: $40.00 USDT
```

---

## Step 3: Test Whitelabel Bot

```bash
python test_wl_bot_local.py
```

Expected output:
```
✅ Bot boleh jalan (startup_check returned True)
```

---

## Step 4: Start Whitelabel Bot

```bash
cd "Whitelabel #1"
python bot.py
```

Bot akan:
1. Check license via http://localhost:8080
2. Jika valid: bot start dan ready untuk menerima command
3. Jika invalid: bot halt dan kirim notifikasi ke admin

---

## Test Payment Flow (Admin2)

Sebagai user 1187119989 di Telegram:

1. `/start` - Start bot
2. Klik "Start Auto Trading"
3. Setup Bitunix API key
4. Bot akan mulai autotrade

---

## Simulate Payment Scenarios

### Scenario 1: Low Balance Warning

```bash
# Reduce balance to < $10
python -c "
import asyncio
import sys
sys.path.insert(0, 'license_server')
from license_manager import LicenseManager

async def main():
    m = LicenseManager()
    # Debit multiple times to reduce balance
    for i in range(3):
        await m.debit_billing('36741b13-c92d-46d8-aa2f-1acdaefee634')
    
asyncio.run(main())
"
```

Bot akan kirim warning ke admin.

### Scenario 2: Grace Period

Ketika balance < monthly_fee, billing akan fail dan status berubah ke `grace_period`.

### Scenario 3: Suspension

Setelah 3 hari di grace_period, billing_cron akan suspend license.

---

## Useful Commands

### Check WL Status
```bash
python check_wl_database.py
```

### Add Balance
```bash
python credit_balance_test.py
```

### Run Billing
```bash
python run_billing_test.py
```

### Register New WL
```bash
cd license_server
python register_wl.py
```

---

## Current WL#1 Credentials

```
WL_ID=36741b13-c92d-46d8-aa2f-1acdaefee634
WL_SECRET_KEY=2c51ecd6-a477-49a1-ae60-baa2250e3b10
DEPOSIT_ADDRESS=0xadB2a65685e0259BaDa4BAA5A4ed432AF3E82042
LICENSE_API_URL=http://localhost:8080
```

Admin1: 801937545
Admin2: 1187119989

---

## Troubleshooting

### Error: ModuleNotFoundError
```bash
cd license_server
pip install -r requirements.txt
```

### Error: Connection refused
Make sure license_api.py is running in Terminal 1.

### Error: License check failed
Check if WL_ID and WL_SECRET_KEY in `Whitelabel #1/.env` match the registered values.

---

## Next: Deploy to Production

See `LICENSE_SYSTEM_TEST_RESULTS.md` for deployment instructions.
