# 🚀 Quick Deployment Reference

## Files Created ✅

- ✅ `Dockerfile` - Production Docker configuration
- ✅ `render.yaml` - Render service blueprint
- ✅ `build.sh` - Build script for Render
- ✅ `DEPLOYMENT.md` - Full deployment guide
- ✅ `validate.sh` - Pre-deployment validation
- ✅ `.dockerignore` - Docker build optimization

## Files Modified ✅

- ✅ `requirements.txt` - Added gunicorn
- ✅ `config.py` - Added PORT env var support
- ✅ `main.py` - Updated to use server_port

---

## Deploy in 5 Steps

### 1️⃣ Set Up Redis (Choose One)

**Option A: Redis Cloud** (Recommended)
- Go to: https://redis.com/try-free/
- Create free database (30MB)
- Copy REDIS_URL

**Option B: Upstash**
- Go to: https://upstash.com/
- Create free database (10K commands/day)
- Copy REDIS_URL

**Option C: Railway**
- Go to: https://railway.app/
- Add Redis service
- Copy REDIS_URL

### 2️⃣ Create Render Service

1. Go to: https://dashboard.render.com/
2. Click: **New +** → **Web Service**
3. Connect your GitHub repository
4. Select: **Docker** runtime
5. **DON'T DEPLOY YET** - add env vars first!

### 3️⃣ Add Environment Variables

In Render dashboard → **Environment** tab, add:

```
API_KEY=<generate-strong-random-32-chars>
REDIS_URL=redis://default:password@host:port
GOOGLE_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
GUVI_CALLBACK_URL=<your-url>
GUVI_API_KEY=<your-key>
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 4️⃣ Deploy

- Click **Manual Deploy** → **Deploy latest commit**
- Wait 5-10 minutes for build
- Watch for "Live" status

### 5️⃣ Verify

```bash
# Test health
curl https://your-app.onrender.com/health

# Expected: {"status":"healthy","redis_connected":true,...}
```

---

## Pre-Deployment Validation

Run this before deploying:

```bash
bash validate.sh
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `redis_connected: false` | Check REDIS_URL format |
| Build failed | Run `bash validate.sh` |
| Health check timeout | Check Render logs |
| Missing API key | Verify env vars in dashboard |

---

## Important Security Notes

⚠️ **ROTATE YOUR API KEYS!** Your `.env.example` has real keys exposed.

1. Generate new keys from provider dashboards
2. Set in Render env vars only
3. Never commit keys to git

---

## Full Documentation

📖 **Complete Guide**: [DEPLOYMENT.md](file:///c:/Users/lekka/OneDrive/Desktop/guvi-hcl-hackathon-new/DEPLOYMENT.md)

📋 **Walkthrough**: See artifacts folder

---

**Ready to deploy!** 🚀
