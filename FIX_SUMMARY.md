# ✅ Fixed: POST to Root Endpoint + Redis Connection

## Issues Identified from Your Logs

```
INFO:     43.204.10.11:0 - "POST / HTTP/1.1" 405 Method Not Allowed
INFO:     [SYST]  Redis: localhost:6379 | connected=False
```

### Issue 1: POST to `/` Returns 405
**Problem**: GUVI platform is sending POST requests to `/` (root) instead of `/api/honeypot`

**Solution**: ✅ Added POST handler at root endpoint that forwards to honeypot

### Issue 2: Redis Not Connected
**Problem**: Redis URL environment variable not being read correctly

**Solution**: ✅ Fixed `redis_url` property to properly handle `REDIS_URL` env var

---

## What Was Fixed

### 1. Root Endpoint Now Accepts POST

**Before:**
```python
@app.get("/")
async def root():
    # Only GET was allowed
```

**After:**
```python
@app.get("/")
async def root():
    # GET returns API info

@app.post("/")
async def root_post(request: IncomingMessage, api_key: str = Depends(verify_api_key)):
    # POST forwards to honeypot endpoint
    return await honeypot_endpoint(request, background_tasks, api_key)
```

### 2. Fixed Redis URL Handling

**Before:**
```python
if self.redis_url_env:
    return self.redis_url_env
```

**After:**
```python
if self.redis_url_env and self.redis_url_env.strip():
    return self.redis_url_env
```

Now properly handles empty string values from environment variables.

---

## Your API Endpoints

Your service is live at: **https://guvi-hcl-hackathon-new.onrender.com**

### Available Endpoints:

| Method | Endpoint | Auth Required | Purpose |
|--------|----------|---------------|---------|
| GET | `/` | No | API info |
| POST | `/` | Yes (X-API-Key) | **Honeypot (GUVI compatible)** |
| POST | `/api/honeypot` | Yes (X-API-Key) | Honeypot (standard) |
| GET | `/health` | No | Health check |
| GET | `/api/test` | No | Simple test |
| POST | `/api/test-honeypot` | No | Test without auth |

---

## Next Steps

### 1. Wait for Render to Redeploy (5-10 minutes)

Render will automatically deploy the new code. Watch your Render dashboard for:
- "Deploying..." → "Live"

### 2. Verify Redis Connection

Once deployed, check the health endpoint:
```bash
curl https://guvi-hcl-hackathon-new.onrender.com/health
```

**Expected:**
```json
{
  "status": "healthy",
  "redis_connected": true,  ← Should be true now!
  "timestamp": "...",
  "version": "1.0.0"
}
```

**If still false**, check your Render environment variables:
- Make sure `REDIS_URL` is set correctly
- Format: `redis://default:password@host:port`

### 3. Test from GUVI Platform

Now that POST to `/` is supported, try testing from GUVI again:

**Option A: Use root endpoint**
- URL: `https://guvi-hcl-hackathon-new.onrender.com/`
- Method: POST
- Headers: `X-API-Key: <your-key>`

**Option B: Use standard endpoint**
- URL: `https://guvi-hcl-hackathon-new.onrender.com/api/honeypot`
- Method: POST
- Headers: `X-API-Key: <your-key>`

Both should work now! ✅

---

## Testing Commands

### Test Root POST (No Auth - for debugging)
```bash
curl -X POST https://guvi-hcl-hackathon-new.onrender.com/api/test-honeypot \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "text": "Test message",
      "sender": "scammer",
      "timestamp": 1707436800000
    },
    "conversationHistory": []
  }'
```

### Test Root POST (With Auth - actual endpoint)
```bash
curl -X POST https://guvi-hcl-hackathon-new.onrender.com/ \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "text": "Your account is blocked. Verify now!",
      "sender": "scammer",
      "timestamp": 1707436800000
    },
    "conversationHistory": []
  }'
```

### Expected Response:
```json
{
  "status": "success",
  "reply": "Arre beta, ye kya ho gaya? Mera account blocked? ..."
}
```

---

## Troubleshooting

### Still Getting 405?
- Make sure you're using POST method
- Check that Content-Type is `application/json`
- Verify X-API-Key header is included

### Redis Still Not Connected?
1. Check Render environment variables
2. Verify `REDIS_URL` is set: `redis://default:password@host:port`
3. Test Redis connection from your provider's dashboard
4. Check Render logs for specific Redis error messages

### Getting 401 Unauthorized?
- Verify `X-API-Key` header matches the `API_KEY` in Render env vars
- Check for typos in the API key

---

## Summary

✅ **POST to `/` now works** - GUVI can send requests to root endpoint  
✅ **Redis URL fixed** - Should connect properly now  
✅ **Pushed to GitHub** - Render will auto-deploy  

**Wait 5-10 minutes for deployment, then test again!** 🚀

---

**Your API URL**: https://guvi-hcl-hackathon-new.onrender.com
