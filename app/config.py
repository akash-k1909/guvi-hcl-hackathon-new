"""Configuration loader (env-first)."""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HONEY_API_KEY", "guvi2026")
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "1") == "1"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com")

# Sanitize GROQ_BASE_URL to avoid double suffixes (common config error)
GROQ_BASE_URL = GROQ_BASE_URL.rstrip("/")
if GROQ_BASE_URL.endswith("/openai/v1"):
    GROQ_BASE_URL = GROQ_BASE_URL.replace("/openai/v1", "")

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.85"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "80"))

GUVI_CALLBACK_URL = os.getenv(
    "GUVI_CALLBACK_URL",
    "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
)
ENABLE_NGROK = os.getenv("ENABLE_NGROK", "0") == "1"
NGROK_PORT = int(os.getenv("NGROK_PORT", "8000"))

MIN_TURNS_BEFORE_CALLBACK = int(os.getenv("MIN_TURNS_BEFORE_CALLBACK", "3"))
MAX_TURNS_BEFORE_CALLBACK = int(os.getenv("MAX_TURNS_BEFORE_CALLBACK", "8"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
LOG_PAYLOADS = os.getenv("LOG_PAYLOADS", "1") == "1"
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
