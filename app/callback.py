"""GUVI callback helper."""

import logging
from typing import Dict, List

import requests

from app.config import GUVI_CALLBACK_URL, LOG_PAYLOADS

logger = logging.getLogger(__name__)


def send_guvi_callback(
    session_id: str,
    total_messages: int,
    intelligence: Dict[str, List[str]],
    agent_notes: str,
) -> None:
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": agent_notes,
    }
    try:
        if LOG_PAYLOADS:
            logger.debug("Callback payload session=%s", session_id)
        response = requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
        logger.debug("Callback status=%s", response.status_code)
        if LOG_PAYLOADS:
            logger.debug("Callback response=%s", response.text[:500])
    except Exception as exc:
        logger.exception("Callback failed: %s", exc)
