# 🛡️ Honey-Pot API - Quick Testing Guide

## Step 1: Start the Server

Open PowerShell in this directory and run:
```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

You should see:
```
[SYST] === AGENTIC HONEY-POT API STARTING ===
[SYST] Environment: development | debug=True
[SYST] Redis: localhost:6379 | connected=True
INFO: Uvicorn running on http://0.0.0.0:8001
```

## Step 2: Test Health Endpoint

Open a **new PowerShell window** and run:
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/health"
```

Expected output:
```
status          : healthy
redis_connected : True
```

## Step 3: Send a Test Scam Message

```powershell
$headers = @{
    "X-API-Key" = "honeypot_secure_key_2026"
    "Content-Type" = "application/json"
}

$body = @{
    session_id = "test-session-1"
    sender_id = "SCAM-BANK"
    message = "URGENT! Your account blocked. Click https://fake-bank.tk to verify KYC"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/honeypot" -Method POST -Headers $headers -Body $body
```

Expected response:
```
session_id          : test-session-1
response            : Arre beta, ye kya ho gaya? Mera account blocked...
engagement_duration : 12.5 (seconds)
turn_number         : 1
is_complete         : False
```

## Step 4: Continue the Conversation

Send more messages with the **same session_id** to see the persona evolve:

### Turn 2:
```powershell
$body = @{
    session_id = "test-session-1"
    sender_id = "SCAM-BANK"
    message = "Sir, click the link and enter your card details to unblock"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/honeypot" -Method POST -Headers $headers -Body $body
```

### Turn 3-5:
Keep sending messages. The persona will get more suspicious and start asking questions.

## Step 5: View Session State (Optional)

```powershell
Invoke-RestMethod -Uri "http://localhost:8001/api/session/test-session-1" -Headers @{"X-API-Key" = "honeypot_secure_key_2026"}
```

This shows the full state including:
- Conversation history
- Extracted intelligence (UPI IDs, URLs, phone numbers)
- Scam probability scores
- Forensic analysis

## Step 6: Test Different Scam Types

### Prize Scam:
```powershell
$body = @{
    session_id = "prize-test"
    sender_id = "VM-LUCKY"
    message = "Congratulations! You won iPhone 15 Pro. Send 500 Rs to winner@paytm to claim"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/honeypot" -Method POST -Headers $headers -Body $body
```

### Job Scam:
```powershell
$body = @{
    session_id = "job-test"
    sender_id = "HR-GOOGLE"
    message = "Selected for Google job! Pay 10000 Rs registration fee to jobs@paytm"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/honeypot" -Method POST -Headers $headers -Body $body
```

## Monitoring Logs

Watch the first PowerShell window (server) to see beautiful logs:
```
[SYST] === NEW REQUEST ===
[PROF] (test-ses...) Scam probability: 0.875 | engage=True
[ACTR] (test-ses...) Generating response | persona=confused_senior | turn=1
[AUDT] (test-ses...) Intelligence extracted: URLs=1, Keywords=2
```

## Troubleshooting

### Port 8001 already in use?
```powershell
# Stop the existing process
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process

# Or use a different port
python -m uvicorn main:app --host 0.0.0.0 --port 8002
```

### Redis not connected?
```powershell
# Start Docker Desktop first, then:
docker-compose up -d

# Check if running:
docker ps
```

### Invalid API Key?
Make sure you're using: `honeypot_secure_key_2026`

## For Hackathon Submission

When ready to submit to GUVI's endpoint tester:

1. **Install ngrok**: https://ngrok.com/download
2. **Start ngrok**:
   ```powershell
   ngrok http 8001
   ```
3. **Copy the https URL** (e.g., `https://abc123.ngrok.io`)
4. **Submit to GUVI**:
   - Endpoint: `https://abc123.ngrok.io/api/honeypot`
   - API Key: `honeypot_secure_key_2026`

## Quick One-Liner Test

```powershell
# All in one command:
Invoke-RestMethod -Uri "http://localhost:8001/api/honeypot" -Method POST -Headers @{"X-API-Key"="honeypot_secure_key_2026";"Content-Type"="application/json"} -Body '{"session_id":"quick-test","sender_id":"SCAM","message":"Urgent! Account blocked. Click: https://fake.tk"}'
```

---

**Your API is ready!** 🎉

**Key Features Working:**
- ✅ Profiler: Zero-trust scam detection
- ✅ Actor: Hinglish persona with Claude
- ✅ Auditor: Intelligence extraction
- ✅ Redis: Session persistence
- ✅ LangGraph: Multi-turn state machine
- ✅ Self-healing callbacks to GUVI
