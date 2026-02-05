"""Configuration loader (env-first)."""

import os

API_KEY = os.getenv("HONEY_API_KEY", "guvi2026")
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "1") == "1"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = os.getenv(
    "GEMINI_API_URL",
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
)
GUVI_CALLBACK_URL = os.getenv(
    "GUVI_CALLBACK_URL",
    "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
)
ENABLE_NGROK = os.getenv("ENABLE_NGROK", "0") == "1"
NGROK_PORT = int(os.getenv("NGROK_PORT", "8000"))

MIN_TURNS_BEFORE_CALLBACK = int(os.getenv("MIN_TURNS_BEFORE_CALLBACK", "3"))
MAX_TURNS_BEFORE_CALLBACK = int(os.getenv("MAX_TURNS_BEFORE_CALLBACK", "8"))
