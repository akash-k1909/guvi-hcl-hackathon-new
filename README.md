# 🛡️ AGENTIC HONEY-POT SYSTEM
**National Public Safety Initiative - MeitY Hackathon**  
Production-Grade Scam Detection & Intelligence Extraction Platform

---

## 🎯 SYSTEM OVERVIEW

The Agentic Honey-Pot is a multi-agent AI system designed to engage with scammers, extract actionable intelligence, and automatically alert law enforcement. Built to handle **1.4 Billion scale** challenges with production-grade resilience.

### Core Features
- ✅ **Dynamic Identity Engine**: Random Indian personas (names, cities, ages)
- ✅ **Language Intelligence**: Auto-detects Hindi and responds in Hinglish
- ✅ **Intelligence Extraction**: Regex-based extraction of UPI IDs, bank accounts, phone numbers, phishing URLs
- ✅ **Law Enforcement Callback**: Automatic POST to GUVI platform when threats detected
- ✅ **Resilience Layer**: Fallback mechanisms for AI failures (1.4B scale readiness)
- ✅ **Public URL**: Auto-generates ngrok tunnel for judge testing

---

## 🚀 QUICK START

### Prerequisites
- **Python 3.10+** (Recommended: Python 3.11)
- **Gemini API Key** (Get from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
# Windows (PowerShell)
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
$env:HONEY_API_KEY="YOUR_SECRET_API_KEY"

# Linux/Mac
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
export HONEY_API_KEY="YOUR_SECRET_API_KEY"

# Optional: enable ngrok tunnel for local testing
# $env:ENABLE_NGROK="1"

# 3. Run the server
python main.py
```

### Expected Output
```
🛡️ AGENTIC HONEY-POT SYSTEM - ACTIVE
============================================================
🌐 PUBLIC URL: https://xxxx-xx-xx-xx-xx.ngrok-free.app
🔒 Local URL: http://localhost:8000
📡 GUVI Callback: https://hackathon.guvi.in/api/updateHoneyPotFinalResult
🔑 API Key: from HONEY_API_KEY (default: guvi2026 if not set)
============================================================
📊 Ready to handle 1.4 Billion scale challenge
============================================================
```

---

## 📡 API ENDPOINTS

### 1. Health Check
```bash
GET /
Response: {"status": "🛡️ CYBERGUARD ACTIVE", "activeSessions": 0}
```

### 2. Chat Endpoint (Main Interface)
```bash
POST /chat
Headers:
  x-api-key: YOUR_SECRET_API_KEY
  Content-Type: application/json

Body (Judge-Compatible Schema):
{
  "sessionId": "SESSION_123",
  "message": {
    "sender": "scammer",
    "text": "Your account will be blocked. Send UPI to verify: victim@paytm",
    "timestamp": 1738776632
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}

Response:
{
  "status": "success",
  "reply": "Wrong number? I don't have account.",
  "scamDetected": true,
  "totalMessagesExchanged": 2,
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": ["victim@paytm"],
    "phishingLinks": [],
    "phoneNumbers": [],
    "suspiciousKeywords": ["block", "verify"]
  },
  "agentIdentity": {
    "name": "Ramesh",
    "city": "Mumbai"
  }
}
```

---

## 🧠 INTELLIGENCE EXTRACTION

### Patterns Detected
| Type | Regex Pattern | Example |
|------|--------------|---------|
| **UPI IDs** | `[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}` | `ramesh@paytm`, `fraud123@ybl` |
| **Bank Accounts** | `\b\d{9,18}\b` | `123456789012` |
| **Phone Numbers** | `(\+91[\-\s]?)?[6789]\d{9}` | `+91-9876543210`, `9876543210` |
| **Phishing URLs** | `https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+` | `https://fake-bank.com` |
| **Keywords** | 21 suspicious terms | `kyc`, `suspend`, `warrant`, `otp`, `cvv` |

---

## 🎭 AGENT BEHAVIOR

### Engagement Strategy (3-Phase)
1. **Phase 1: Confusion** → "Wrong number?"
2. **Phase 2: Fear** → "Please don't block my account!"
3. **Phase 3: Intelligence Gathering** → "Where do I send money?"

### Language Adaptation
- **English Input** → English responses ("Hello sir")
- **Hindi Input** → Hinglish responses ("Haan sir, bolo")

---

## 📡 GUVI CALLBACK SYSTEM

### Trigger Conditions
- **Condition 1**: Scam intent confirmed
- **Condition 2**: Engagement complete (turn threshold and/or actionable intel)

### Callback Payload
```json
{
  "sessionId": "SESSION_123",
  "scamDetected": true,
  "totalMessagesExchanged": 4,
  "extractedIntelligence": {
    "bankAccounts": ["123456789012"],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": ["https://fake-kyc.com"],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["kyc", "urgent", "block"]
  },
  "agentNotes": "CRITICAL THREAT: Detected UPI Fraud scam. Engaged as Ramesh from Mumbai. Financial evidence secured for Cyber Crime Cell."
}
```

---

## 🏗️ PRODUCTION ARCHITECTURE

### Resilience Features (1.4B Scale)
- ✅ **Fallback AI Responses**: "Hello? Network is slow. Can you message again?"
- ✅ **Timeout Handling**: 10-second Gemini API timeout
- ✅ **Background Tasks**: Non-blocking GUVI callbacks
- ✅ **Session Persistence**: In-memory store (upgrade to Redis/PostgreSQL for cloud)

### Recommended Cloud Deployment
```bash
# Option 1: Railway/Render (Auto-scaling)
# Option 2: AWS Lambda + API Gateway (Serverless)
# Option 3: Google Cloud Run (Containerized)

# Environment Variables Required:
# - GEMINI_API_KEY
# - Optional: REDIS_URL (for distributed sessions)
```

---

## 🧪 TESTING

### Test with cURL
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "x-api-key: guvi2026" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "TEST_001",
    "message": {
      "sender": "scammer",
      "text": "Your KYC is expired. Send money to 9876543210 or account will be blocked.",
      "timestamp": 1738776632
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

---

## 📊 TECHNICAL SPECIFICATIONS

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI 0.109.0 | High-performance async API |
| **AI Engine** | Gemini 1.5 Flash | Scammer engagement responses |
| **Validation** | Pydantic 2.5.3 | Judge-compatible schema validation |
| **Tunneling** | Pyngrok 7.0.5 | Public URL generation |
| **HTTP Client** | Requests 2.31.0 | Gemini API + GUVI callbacks |
| **Server** | Uvicorn 0.27.0 | ASGI server with auto-reload |

---

## 🔒 SECURITY

- ✅ **API Key Authentication**: `x-api-key: guvi2026`
- ✅ **Environment Variable Protection**: Gemini API key not hardcoded
- ✅ **Input Validation**: Pydantic strict schema enforcement
- ✅ **Rate Limiting**: Recommended for production (not implemented in MVP)

---

## 📈 SCALABILITY ROADMAP

### Current (MVP)
- In-memory session store (single server)
- Direct Gemini API calls (10 QPS limit)

### Production Upgrade Path
1. **Session Store**: Migrate to Redis/PostgreSQL
2. **Load Balancing**: Nginx + multiple uvicorn workers
3. **Caching**: Redis cache for AI responses
4. **Monitoring**: Prometheus + Grafana metrics
5. **Rate Limiting**: Token bucket algorithm (100 RPS)

---

## 🏆 HACKATHON SUBMISSION CHECKLIST

- ✅ Production-grade code with error handling
- ✅ Judge-compatible camelCase → snake_case Pydantic aliases
- ✅ GUVI callback integration with BackgroundTasks
- ✅ 1.4 Billion scale resilience features
- ✅ Ngrok auto-tunneling for public testing
- ✅ Comprehensive documentation (this README)
- ✅ Deployment-ready requirements.txt

---

## 📞 SUPPORT

For issues or questions during hackathon:
- **Email**: [Your Email]
- **GitHub**: [Your Repo]
- **Demo Video**: [YouTube Link]

---

**Built with 🇮🇳 for National Public Safety**  
*Protecting 1.4 Billion Citizens from Digital Fraud*
