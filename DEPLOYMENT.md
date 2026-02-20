# 🚀 Deployment Guide - Render.com

Complete step-by-step guide to deploy the Agentic Honey-Pot API on Render.

## Prerequisites

- [x] GitHub repository with your code
- [ ] External Redis service (choose one below)
- [ ] All required API keys ready

---

## Step 1: Set Up External Redis

Choose **ONE** of these free Redis providers:

### Option A: Redis Cloud (Recommended)

1. Go to [Redis Cloud](https://redis.com/try-free/)
2. Sign up for a free account (30MB free tier)
3. Create a new database:
   - **Name**: honeypot-redis
   - **Region**: Choose closest to your Render region
   - **Type**: Redis Stack (includes all features)
4. Copy your connection URL:
   - Format: `redis://default:password@host:port`
   - Found in: Database → Configuration → Public endpoint

### Option B: Upstash

1. Go to [Upstash](https://upstash.com/)
2. Sign up for free account (10,000 commands/day free)
3. Create Redis database:
   - **Name**: honeypot-redis
   - **Region**: Choose closest to Render
4. Copy **UPSTASH_REDIS_REST_URL** from dashboard
   - Format: `redis://default:password@host:port`

### Option C: Railway

1. Go to [Railway](https://railway.app/)
2. Create new project → Add Redis
3. Copy the `REDIS_URL` from environment variables
4. Format: `redis://default:password@host:port`

> [!IMPORTANT]
> Save your `REDIS_URL` - you'll need it in Step 3!

---

## Step 2: Create Web Service on Render

1. **Go to [Render Dashboard](https://dashboard.render.com/)**

2. **Click "New +" → "Web Service"**

3. **Connect Your Repository**:
   - Connect your GitHub account if not already connected
   - Select your repository: `guvi-hcl-hackathon-new`
   - Click "Connect"

4. **Configure Service**:
   - **Name**: `honeypot-api` (or your preferred name)
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Runtime**: Docker
   - **Plan**: Free (or Starter for better performance)

5. **Advanced Settings** (click to expand):
   - **Dockerfile Path**: `./Dockerfile`
   - **Docker Context**: `.`
   - **Health Check Path**: `/health`
   - **Auto-Deploy**: Yes

6. **Click "Create Web Service"** (don't deploy yet - we need to add environment variables first!)

---

## Step 3: Configure Environment Variables

In your Render service dashboard, go to **Environment** tab and add these variables:

### 🔐 Required Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `API_KEY` | `your-secret-key-here` | Generate a strong random string (min 32 chars) |
| `REDIS_URL` | `redis://default:password@host:port` | From Step 1 |
| `GOOGLE_API_KEY` | `AIzaSy...` | Your Google AI API key |
| `ANTHROPIC_API_KEY` | `sk-ant-api03...` | Your Anthropic API key |
| `GUVI_CALLBACK_URL` | `https://...` | GUVI hackathon callback endpoint |
| `GUVI_API_KEY` | `your-guvi-key` | GUVI API key |

### ⚙️ Production Configuration

| Variable | Value |
|----------|-------|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `LOG_LEVEL` | `INFO` |
| `LOG_FORMAT` | `json` |

### 🤖 Agent Configuration (Optional - uses defaults if not set)

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `MAX_CONVERSATION_TURNS` | `35` | Maximum conversation turns |
| `SCAM_THRESHOLD` | `0.7` | Scam detection threshold |
| `DEFAULT_PERSONA` | `confused_senior` | Default persona type |
| `GEMINI_MODEL` | `gemini-2.0-flash-exp` | Gemini model |
| `CLAUDE_MODEL` | `claude-3-5-sonnet-20241022` | Claude model |

### 🔍 Optional Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `OPENAI_API_KEY` | `sk-proj-...` | Optional backup LLM |
| `GROQ_API_KEY` | `gsk_...` | Optional free fast LLM |
| `WORKERS` | `2` | Gunicorn worker count |

> [!WARNING]
> **Security Best Practice**: Never commit API keys to git! Always use environment variables.

---

## Step 4: Deploy

1. **Save all environment variables** in Render dashboard

2. **Trigger deployment**:
   - Render will automatically start building
   - Or click "Manual Deploy" → "Deploy latest commit"

3. **Monitor build logs**:
   - Watch for: `🛡️ [BUILD] Build completed successfully!`
   - Build takes ~5-10 minutes on first deploy

4. **Wait for health checks**:
   - Render will ping `/health` endpoint
   - Service status should show "Live" when ready

---

## Step 5: Verify Deployment

### Test Health Endpoint

```bash
curl https://your-app.onrender.com/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "redis_connected": true,
  "timestamp": "2026-02-09T00:00:00Z",
  "version": "1.0.0"
}
```

> [!CAUTION]
> If `redis_connected: false`, check your `REDIS_URL` environment variable!

### Test Root Endpoint

```bash
curl https://your-app.onrender.com/
```

**Expected Response**:
```json
{
  "service": "Agentic Honey-Pot API",
  "version": "1.0.0",
  "status": "operational",
  "timestamp": "2026-02-09T00:00:00Z"
}
```

### Test Honey-Pot Endpoint

```bash
curl -X POST https://your-app.onrender.com/api/honeypot \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-123",
    "message": {
      "text": "Your account is blocked. Click here to verify.",
      "sender": "SCAMMER-001"
    }
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "reply": "Arre beta, ye kya ho gaya? Mera account blocked? ..."
}
```

---

## Step 6: Monitor and Debug

### View Logs

1. Go to Render dashboard → Your service → **Logs** tab
2. Look for:
   - `🛡️ [SYSTEM] === AGENTIC HONEY-POT API STARTING ===`
   - `🛡️ [SYSTEM] Redis: <host>:<port>` with `connected=true`
   - `🔍 [PROFILER]` logs for scam detection
   - `🎭 [ACTOR]` logs for persona responses

### Common Issues

#### ❌ Redis Connection Failed

**Symptom**: `redis_connected: false` in health check

**Solution**:
1. Verify `REDIS_URL` format: `redis://default:password@host:port`
2. Check Redis service is running (test with Redis CLI)
3. Verify firewall allows connections from Render IPs
4. Check Redis password is correct

#### ❌ Missing API Key Error

**Symptom**: `Missing API key` or `Invalid API key` errors

**Solution**:
1. Verify all required env vars are set in Render dashboard
2. Check for typos in variable names (case-sensitive!)
3. Redeploy after adding missing variables

#### ❌ Build Failed

**Symptom**: Build logs show errors during `pip install`

**Solution**:
1. Check `requirements.txt` is valid
2. Verify Python version compatibility (3.11+)
3. Check Render build logs for specific error messages

#### ❌ Health Check Timeout

**Symptom**: Service shows "Unhealthy" status

**Solution**:
1. Increase health check timeout in Render settings
2. Check application starts within 60 seconds
3. Verify `/health` endpoint is accessible

---

## Step 7: Production Best Practices

### Security

- [x] Rotate all API keys that were exposed in `.env.example`
- [x] Use strong `API_KEY` (min 32 characters, random)
- [x] Enable HTTPS only (Render provides this automatically)
- [ ] Set up rate limiting (consider Cloudflare)
- [ ] Monitor for suspicious activity

### Performance

- [ ] Upgrade to Render Starter plan for better performance ($7/month)
- [ ] Increase `WORKERS` to 4 for higher traffic
- [ ] Monitor response times in Render metrics
- [ ] Consider Redis persistence settings

### Monitoring

- [ ] Set up Render alerts for downtime
- [ ] Monitor Redis memory usage
- [ ] Track callback success rates
- [ ] Review logs regularly for errors

---

## Troubleshooting Commands

### Check Render Service Status
```bash
# Using Render CLI (install: npm install -g render-cli)
render services list
render logs <service-id>
```

### Test Redis Connection Locally
```bash
# Install redis-cli
redis-cli -u "redis://default:password@host:port" ping
# Expected: PONG
```

### Verify Environment Variables
```bash
# In Render dashboard → Environment tab
# Or via API:
curl https://api.render.com/v1/services/<service-id>/env-vars \
  -H "Authorization: Bearer YOUR_RENDER_API_KEY"
```

---

## Next Steps

✅ **Deployment Complete!** Your API is now live at:
- **URL**: `https://your-app.onrender.com`
- **Health**: `https://your-app.onrender.com/health`
- **API**: `https://your-app.onrender.com/api/honeypot`

### Update GUVI Integration

1. Update your GUVI hackathon submission with your Render URL
2. Test the full flow with GUVI Mock Scammer API
3. Monitor callback success in logs

### Optional Enhancements

- [ ] Set up custom domain
- [ ] Add Cloudflare for DDoS protection
- [ ] Implement rate limiting
- [ ] Add monitoring with Datadog/New Relic
- [ ] Set up CI/CD with GitHub Actions

---

## Support

If you encounter issues:

1. **Check Render Logs**: Most issues are visible in logs
2. **Verify Environment Variables**: Double-check all required vars are set
3. **Test Redis Connection**: Ensure external Redis is accessible
4. **Review Health Endpoint**: Check `/health` for specific errors

**Common Error Messages**:
- `Connection refused` → Redis URL incorrect or service down
- `Invalid API key` → Check `API_KEY` environment variable
- `Module not found` → Rebuild with updated `requirements.txt`

---

**🛡️ Deployment Guide Complete** | Built for India AI Impact Buildathon 2026
