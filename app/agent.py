"""Agent behavior and Groq integration."""

import logging
import random
import time
from typing import Any, Dict, List

from groq import Groq

from app.config import (
    GROQ_API_KEY,
    GROQ_BASE_URL,
    GROQ_MODEL,
    GROQ_TEMPERATURE,
    GROQ_MAX_TOKENS,
    LOG_PAYLOADS,
)
from app.models import Message

logger = logging.getLogger(__name__)

PHASE_TEMPLATES = {
    "general": {
        1: ["Who is this?", "Wrong number?", "Is this my bank?"],
        2: ["I already paid, why again?", "I am not sure, please explain."],
        3: ["Please do not block me. What should I do?", "Where do I send it?"],
    },
    "digital_arrest": {
        1: ["Sir, who are you?", "Police? Which station, sir?"],
        2: ["I am a small businessman, please explain.", "Why is this happening?"],
        3: ["Please help me. What should I do?", "Where do I send money?"],
    },
    "electricity": {
        1: ["Which bill? I paid last month.", "This is my meter?"],
        2: ["I am old, please explain slowly.", "Why is my connection cut?"],
        3: ["Please help me with payment. How to pay now?", "Which number to pay?"],
    },
    "job": {
        1: ["Which company? I applied many places.", "Is this about an interview?"],
        2: ["I need a job, please explain clearly.", "Is there any fee?"],
        3: ["I can pay later, how to proceed?", "Where do I submit details?"],
    },
}

ILLEGAL_KEYWORDS = [
    "drugs",
    "cocaine",
    "heroin",
    "hack",
    "malware",
    "bomb",
    "gun",
    "pistol",
    "child porn",
]


def _phase_index(turn_count: int) -> int:
    if turn_count <= 1:
        return 1
    if turn_count <= 2:
        return 2
    return 3


def _select_templates(scam_type: str, turn_count: int) -> List[str]:
    phase = _phase_index(turn_count)
    templates = PHASE_TEMPLATES.get(scam_type, PHASE_TEMPLATES["general"])
    return templates.get(phase, templates[3])


def _is_illegal_request(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in ILLEGAL_KEYWORDS)


def _guardrail_reply(language: str) -> str:
    if language.lower() == "hindi":
        return "Bhai, main yeh nahi kar sakta. Kuch aur batao?"
    return "I cannot do that. Please explain the issue."


def _generate_thought(scam_type: str, phase: int) -> str:
    if scam_type == "digital_arrest":
        base = "Scammer using authority pressure"
    elif scam_type == "electricity":
        base = "Utility scare tactic detected"
    elif scam_type == "job":
        base = "Job bait likely to demand fees"
    else:
        base = "General scam pressure"

    if phase == 1:
        return f"{base}; act confused and probe."
    if phase == 2:
        return f"{base}; act defensive and ask for details."
    return f"{base}; act scared and request payment details."


def call_groq(
    history: List[Message],
    current_text: str,
    identity: Dict[str, Any],
    language: str,
    scam_type: str,
) -> str:
    if not GROQ_API_KEY:
        return "Sorry, can you explain again?"

    client = Groq(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

    turn_count = len(history) + 1
    phase_lines = _select_templates(scam_type, turn_count)
    example_line = random.choice(phase_lines)

    conversation_text = ""
    for msg in history[-6:]:
        if isinstance(msg, dict):
            sender = msg.get("sender")
            text = msg.get("text", "")
        else:
            sender = msg.sender
            text = msg.text
        sender_label = "Caller" if sender == "scammer" else "Me"
        conversation_text += f"{sender_label}: {text}\n"

    if language.lower() == "hindi":
        system_prompt = (
            f"You are {identity['name']}, {identity['age']} years old from {identity['city']}, India.\n"
            f"Role: {identity['role']}.\n"
            "MISSION: Keep the caller talking by acting confused, worried, and curious.\n"
            "RULES: Reply in Hinglish, keep it under 15 words, ask a question, never reveal scam detection.\n"
            f"Example style: {example_line}\n\n"
            f"Previous conversation:\n{conversation_text}\n"
            f"Their latest message: {current_text}\n\n"
            "Your response:"
        )
    else:
        system_prompt = (
            f"You are {identity['name']}, {identity['age']} years old from {identity['city']}, India.\n"
            f"Role: {identity['role']}.\n"
            "MISSION: Keep the caller talking by acting confused, worried, and curious.\n"
            "RULES: Keep it under 15 words, ask a question, never reveal scam detection.\n"
            "STYLE: Use Indian English, may include words like bhai or sirji.\n"
            f"Example style: {example_line}\n\n"
            f"Previous conversation:\n{conversation_text}\n"
            f"Their latest message: {current_text}\n\n"
            "Your response:"
        )

    start = time.perf_counter()
    try:
        if LOG_PAYLOADS:
            logger.debug("Groq request model=%s tokens=%s", GROQ_MODEL, GROQ_MAX_TOKENS)

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": system_prompt}],
            temperature=GROQ_TEMPERATURE,
            max_tokens=GROQ_MAX_TOKENS,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.debug("Groq response time_ms=%.1f", elapsed_ms)

        text = response.choices[0].message.content.strip()
        if LOG_PAYLOADS:
            logger.debug("Groq reply len=%s", len(text))
        return text or "Please explain again."
    except Exception as exc:
        logger.exception("Groq call failed: %s", exc)
        return "Sorry, I did not get that. Can you repeat?"


def build_reply(
    history: List[Message],
    current_text: str,
    identity: Dict[str, Any],
    language: str,
    scam_type: str,
) -> Dict[str, str]:
    turn_count = len(history) + 1
    phase = _phase_index(turn_count)
    thought = _generate_thought(scam_type, phase)

    if _is_illegal_request(current_text):
        reply = _guardrail_reply(language)
        return {"reply": reply, "thought": "Safety: refuse illegal request."}

    if GROQ_API_KEY:
        reply = call_groq(history, current_text, identity, language, scam_type)
    else:
        text_lower = current_text.lower()
        if "otp" in text_lower:
            reply = "OTP? Which bank branch and account number, sirji?"
        elif "account" in text_lower or "blocked" in text_lower:
            reply = "Which account? Please share last 4 digits and branch."
        elif "upi" in text_lower or "pay" in text_lower or "send" in text_lower:
            reply = "Bhai, send UPI ID and exact amount."
        else:
            candidates = _select_templates(scam_type, turn_count)
            last_reply = ""
            for msg in reversed(history):
                if isinstance(msg, dict):
                    sender = msg.get("sender")
                    text = msg.get("text", "")
                else:
                    sender = msg.sender
                    text = msg.text
                if sender == "user":
                    last_reply = text
                    break
            filtered = [c for c in candidates if c != last_reply]
            reply = random.choice(filtered or candidates)

    return {"reply": reply, "thought": thought}
