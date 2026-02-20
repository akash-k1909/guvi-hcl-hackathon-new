# 🔧 Fixing 405 Error from GUVI Platform

## Problem Identified

You were getting a **405 Method Not Allowed** error when testing from the GUVI hackathon platform.

## Root Cause

**CORS Configuration Issue**: Your API was configured to only allow requests from `https://guvi.in`, but the GUVI hackathon platform is at `https://hackathon.guvi.in`. This caused the browser to block the requests.

## ✅ Fixes Applied

### 1. Updated CORS Configuration

**Before:**
```python
allow_origins=["*"] if settings.debug else ["https://guvi.in"]
```

**After:**
```python
allow_origins=["*"] if settings.debug else [
    "https://guvi.in",
    "https://hackathon.guvi.in",  # ✅ Added
    "https://www.guvi.in",
]
```

### 2. Added OPTIONS Handler

Added explicit CORS preflight handler:
```python
@app.options("/api/honeypot")
async def honeypot_options():
    """Handle CORS preflight requests."""
    return {"message": "OK"}
```

### 3. Added Diagnostic Endpoints

Created test endpoints to help debug integration:

**GET `/api/test`** - Simple health check (no auth required)
```bash
curl https://your-app.onrender.com/api/test
```

**POST `/api/test-honeypot`** - Test honeypot without auth
```bash
curl -X POST https://your-app.onrender.com/api/test-honeypot \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-123",
    "message": {"text": "test", "sender": "scammer", "timestamp": 1234567890},
    "conversationHistory": []
  }'
```

---

## 🚀 Next Steps

### Step 1: Wait for Render to Redeploy

Render should automatically redeploy with the new changes. This takes 5-10 minutes.

**Check deployment status:**
1. Go to your Render dashboard
2. Look for "Deploy" in progress
3. Wait for "Live" status

### Step 2: Test the Diagnostic Endpoints

Once deployed, test these endpoints:

**Test 1: Simple Health Check**
```bash
curl https://your-app.onrender.com/api/test
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "Honeypot API is running",
  "timestamp": "2026-02-09T00:00:00",
  "endpoints": {
    "health": "/health",
    "honeypot": "/api/honeypot (POST)",
    "test": "/api/test (GET)"
  }
}
```

**Test 2: Main Health Endpoint**
```bash
curl https://your-app.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "redis_connected": true,
  "timestamp": "2026-02-09T00:00:00",
  "version": "1.0.0"
}
```

**Test 3: Test Honeypot (No Auth)**
```bash
curl -X POST https://your-app.onrender.com/api/test-honeypot \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "text": "Test message",
      "sender": "scammer",
      "timestamp": 1234567890
    },
    "conversationHistory": []
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "reply": "Test response from honeypot API. Authentication is working!"
}
```

### Step 3: Test from GUVI Platform

1. Go back to https://hackathon.guvi.in/timeline?hackathon-id=a90c3b95-4406-46b9-870d-b52d0e430a6f
2. Enter your Render URL: `https://your-app.onrender.com/api/honeypot`
3. Test the integration
4. The 405 error should now be resolved! ✅

---

## 🐛 If You Still Get Errors

### Error: 401 Unauthorized

**Cause**: Missing or invalid `X-API-Key` header

**Solution**: Make sure GUVI platform is sending the correct API key in the header:
```
X-API-Key: <your-API_KEY-from-render-env-vars>
```

### Error: 400 Bad Request

**Cause**: Invalid request format

**Solution**: Check that GUVI is sending the correct JSON format:
```json
{
  "sessionId": "unique-id",
  "message": {
    "text": "message text",
    "sender": "scammer",
    "timestamp": 1234567890
  },
  "conversationHistory": []
}
```

### Error: 500 Internal Server Error

**Cause**: Application error (likely Redis connection or API key issue)

**Solution**: Check Render logs:
1. Go to Render dashboard → Your service → Logs
2. Look for error messages
3. Common issues:
   - `redis_connected: false` → Check REDIS_URL
   - `Missing API key` → Check GOOGLE_API_KEY and ANTHROPIC_API_KEY

### Error: 502 Bad Gateway

**Cause**: Application not running or crashed

**Solution**: 
1. Check Render service status (should be "Live")
2. Check Render logs for crash errors
3. Verify health endpoint: `curl https://your-app.onrender.com/health`

---

## 📋 Checklist

Before testing from GUVI platform:

- [ ] Render deployment is complete (status: "Live")
- [ ] `/api/test` endpoint returns `{"status": "ok"}`
- [ ] `/health` endpoint returns `{"redis_connected": true}`
- [ ] `/api/test-honeypot` returns a success response
- [ ] All environment variables are set in Render
- [ ] API_KEY matches what GUVI platform is using

---

## 🔍 Debugging Tips

### View Render Logs in Real-Time

1. Go to Render dashboard → Your service
2. Click "Logs" tab
3. Watch for incoming requests when you test from GUVI

**What to look for:**
```
🛡️ [SYSTEM] Incoming GUVI message
🔍 [PROFILER] Starting zero-trust analysis
🎭 [ACTOR] Generating response
💎 [AUDITOR] Intelligence extracted
```

### Test with curl (Simulating GUVI)

```bash
# Replace with your actual Render URL and API key
curl -X POST https://your-app.onrender.com/api/honeypot \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Origin: https://hackathon.guvi.in" \
  -d '{
    "sessionId": "test-session-123",
    "message": {
      "text": "Your account is blocked. Click here to verify.",
      "sender": "scammer",
      "timestamp": 1707436800000
    },
    "conversationHistory": []
  }'
```

---

## 📝 Summary

✅ **Fixed CORS** to allow `hackathon.guvi.in`  
✅ **Added OPTIONS handler** for CORS preflight  
✅ **Created diagnostic endpoints** for testing  
✅ **Pushed to GitHub** - Render will auto-deploy  

**Wait for Render to redeploy (5-10 min), then test again from GUVI platform!**

---

**Need more help? Check the Render logs and let me know what errors you see!** 🚀
