"""Agent behavior and Async Groq integration."""

import logging
import random
import time
from typing import Any, Dict, List, Union

from groq import AsyncGroq

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

# --- Configuration & Templates ---

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

# --- Helper Utilities ---


def _phase_index(turn_count: int) -> int:
    if turn_count <= 1:
        return 1
    if turn_count <= 2:
        return 2
    return 3


def _select_templates(scam_type: str, turn_count: int) -> List[str]:
    phase = _phase_index(turn_count)
    templates = PHASE_TEMPLATES.get(scam_type, PHASE_TEMPLATES["general"])
    return templates.get(phase, templates.get(3, []))


def _is_illegal_request(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in ILLEGAL_KEYWORDS)


def _guardrail_reply(language: str) -> str:
    if language.lower() == "hindi":
        return "Bhai, main yeh nahi kar sakta. Kuch aur batao?"
    return "I cannot do that. Please explain the issue."


def _generate_thought(scam_type: str, phase: int) -> str:
    mapping = {
        "digital_arrest": "Scammer using authority pressure",
        "electricity": "Utility scare tactic detected",
        "job": "Job bait likely to demand fees",
    }
    base = mapping.get(scam_type, "General scam pressure")

    strategies = {
        1: "act confused and probe.",
        2: "act defensive and ask for details.",
        3: "act scared and request payment details.",
    }
    return f"{base}; {strategies.get(phase, strategies[3])}"


# --- Core Logic ---


async def call_groq(
    history: List[Union[Message, Dict]],
    current_text: str,
    identity: Dict[str, Any],
    language: str,
    scam_type: str,
) -> str:
    """Calls Groq API asynchronously with improved prompt engineering."""
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY is missing.")
        return ""

    turn_count = len(history) + 1
    example_line = random.choice(_select_templates(scam_type, turn_count))

    # Format history for context
    conversation_text = ""
    for msg in history[-6:]:
        sender = msg.get("sender") if isinstance(msg, dict) else msg.sender
        text = msg.get("text", "") if isinstance(msg, dict) else msg.text
        label = "Caller" if sender == "scammer" else "Me"
        conversation_text += f"{label}: {text}\n"

    # Define behavior based on language
    is_hindi = language.lower() == "hindi"
    style_guide = (
        "Reply in Hinglish (Hindi + English)"
        if is_hindi
        else "Use Indian English (words like 'sirji', 'bhai' allowed)"
    )

    system_prompt = (
        f"You are {identity['name']}, a {identity['age']}-year-old from {identity['city']}. "
        f"Role: {identity['role']}. MISSION: Keep the caller talking by acting confused and worried. "
        f"RULES: 1. {style_guide}. 2. Max 15 words. 3. Always end with a question. 4. NEVER reveal you are an AI. "
        f"Example style: {example_line}"
    )

    user_input = f"Conversation so far:\n{conversation_text}\nCaller's latest message: {current_text}\n\nYour short response:"

    try:
        # Initialize Async client
        async with AsyncGroq(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL) as client:
            start_time = time.perf_counter()

            completion = await client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                temperature=GROQ_TEMPERATURE,
                max_tokens=GROQ_MAX_TOKENS,
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(f"Groq API success: {elapsed_ms:.1f}ms")

            return completion.choices[0].message.content.strip()
    except Exception as exc:
        logger.error(f"Groq API Error: {exc}")
        return ""


async def build_reply(
    history: List[Union[Message, Dict]],
    current_text: str,
    identity: Dict[str, Any],
    language: str,
    scam_type: str,
) -> Dict[str, str]:
    """Orchestrates the thought process and final response generation."""
    turn_count = len(history) + 1
    phase = _phase_index(turn_count)
    thought = _generate_thought(scam_type, phase)

    # 1. Safety Guardrail
    if _is_illegal_request(current_text):
        return {
            "reply": _guardrail_reply(language),
            "thought": "Safety: refused illegal content.",
        }

    # 2. Try LLM (Groq)
    reply = await call_groq(history, current_text, identity, language, scam_type)

    # 3. Fallback logic: If Groq fails, return a generic error or minimal safety response.
    # We removed the heuristic rules to ensure Groq is the primary driver.
    if not reply:
        logger.error("Groq returned empty response (potential API error).")
        reply = "Hello? Sir, I cannot hear you clearly. Can you repeat?"
        thought = "System: Groq API failed; generic fallback used."

    return {"reply": reply, "thought": thought}
