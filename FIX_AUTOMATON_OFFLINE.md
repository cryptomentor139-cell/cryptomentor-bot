# Fix: Automaton Service Offline

## 🔍 Problem
Bot menampilkan "❌ Automaton service offline" padahal:
- Automaton Railway sudah running
- CONWAY_API_URL dan CONWAY_API_KEY sudah dikonfigurasi

## 🎯 Root Cause Analysis

### Health Check Implementation
File: `Bismillah/app/conway_integration.py`

```python
def health_check(self) -> bool:
    try:
        response = requests.get(
            f"{self.api_url}/api/v1/wallets/0/deposit-address",
            headers=self.headers,
            timeout=10
        )
        return response.status_code in [200, 404]
    except Exception as e:
        print(f"❌ Conway API health check failed: {e}")
        return False
```

### Possible Issues:

1. **Endpoint Tidak Ada**
   - `/api/v1/wallets/0/deposit-address` mungkin tidak exist di Automaton API
   - Automaton API mungkin punya endpoint berbeda

2. **API Key Invalid**
   - `CONWAY_API_KEY` salah atau expired
   - Authorization header format salah

3. **URL Salah**
   - `CONWAY_API_URL` tidak benar
   - Missing `/api` prefix atau trailing slash

4. **Network Issue**
   - Railway bot tidak bisa reach Automaton Railway
   - Firewall blocking

5. **Timeout**
   - Automaton API lambat respond (>10s)
   - Railway cold start

## 🔧 SOLUTIONS

### Solution 1: Update Health Check Endpoint

Ganti endpoint health check ke endpoint yang pasti ada:

```python
def health_check(self) -> bool:
    """
    Check if Conway API is accessible
    
    Returns:
        True if API is healthy, False otherwise
    """
    try:
        # Try root endpoint first
        response = requests.get(
            self.api_url,
            headers=self.headers,
            timeout=10
        )
        # Any response means API is up
        return response.status_code < 500
    except Exception as e:
        print(f"❌ Conway API health check failed: {e}")
        return False
```

### Solution 2: Add Multiple Fallback Endpoints

```python
def health_check(self) -> bool:
    """Check API health with multiple fallback endpoints"""
    endpoints = [
        '/',  # Root
        '/health',  # Health endpoint
        '/api/v1/health',  # API health
        '/api/v1/wallets/0/deposit-address',  # Original
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{self.api_url}{endpoint}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # Any non-500 response means API is up
            if response.status_code < 500:
                print(f"✅ Health check passed via {endpoint}")
                return True
        except:
            continue
    
    print(f"❌ All health check endpoints failed")
    return False
```

### Solution 3: Remove Health Check (Temporary)

Jika health check terus gagal tapi API sebenarnya working, comment out health check:

```python
# In handlers_automaton_api.py
async def automaton_status_api(update, context):
    # TEMPORARY: Skip health check
    # if not conway.health_check():
    #     await update.message.reply_text("❌ Automaton service offline")
    #     return
    
    # Continue with actual API call...
```

## 🧪 TESTING

### Step 1: Run Diagnostic Script
```bash
cd Bismillah
python test_automaton_connection.py
```

This will test:
1. Environment variables
2. API connectivity
3. Conway Integration class
4. Specific endpoints

### Step 2: Check Railway Logs

**Bot Railway:**
```
# Look for:
❌ Conway API health check failed: [error message]
```

**Automaton Railway:**
```
# Check if it's receiving requests
# Look for incoming API calls
```

### Step 3: Manual API Test

```bash
# Test with curl
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://your-automaton-url.railway.app/

# Or with Python
python -c "
import requests
url = 'https://your-automaton-url.railway.app/'
headers = {'Authorization': 'Bearer YOUR_API_KEY'}
r = requests.get(url, headers=headers)
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:200]}')
"
```

## 📋 CHECKLIST

### Railway Bot Environment Variables:
- [ ] `CONWAY_API_URL` is set (e.g., `https://automaton-xxx.railway.app`)
- [ ] `CONWAY_API_KEY` is set
- [ ] No trailing slash in URL
- [ ] URL is accessible from Railway

### Railway Automaton:
- [ ] Service is running (not crashed)
- [ ] Has API endpoints exposed
- [ ] API key matches bot's key
- [ ] Logs show no errors

### Code:
- [ ] `health_check()` uses correct endpoint
- [ ] Timeout is reasonable (10s)
- [ ] Error handling is proper

## 🚀 RECOMMENDED FIX

### Option A: Simplify Health Check (RECOMMENDED)

Update `app/conway_integration.py`:

```python
def health_check(self) -> bool:
    """
    Check if Conway API is accessible
    
    Uses root endpoint for simplicity
    """
    try:
        response = requests.get(
            self.api_url,  # Just root URL
            timeout=10
        )
        # Any response < 500 means API is up
        is_healthy = response.status_code < 500
        
        if is_healthy:
            print(f"✅ Conway API health check passed: {response.status_code}")
        else:
            print(f"❌ Conway API health check failed: {response.status_code}")
        
        return is_healthy
    
    except requests.exceptions.Timeout:
        print(f"❌ Conway API timeout")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Conway API connection error")
        return False
    except Exception as e:
        print(f"❌ Conway API health check failed: {e}")
        return False
```

### Option B: Skip Health Check for Critical Operations

Update `app/handlers_automaton_api.py`:

```python
async def automaton_status_api(update, context):
    # Try API call directly, let it fail naturally if offline
    try:
        # ... actual API call ...
    except Exception as e:
        await update.message.reply_text(
            f"❌ Automaton service offline\n\nError: {str(e)}"
        )
```

## 📝 NEXT STEPS

1. **Run diagnostic script** to identify exact issue
2. **Check Railway logs** for both bot and automaton
3. **Update health_check()** based on findings
4. **Test with `/automaton status`** command
5. **Deploy fix** to Railway

---

**Status**: 🔍 Investigating
**Priority**: High
**Impact**: Automaton features unavailable
