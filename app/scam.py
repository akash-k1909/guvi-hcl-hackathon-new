"""Scam intent scoring and confirmation."""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

SCAM_SIGNAL_KEYWORDS = [
    "account blocked",
    "verify immediately",
    "urgent",
    "kyc",
    "suspend",
    "blocked",
    "otp",
    "cvv",
    "pin",
    "bank",
    "upi",
    "refund",
    "lottery",
    "winner",
    "police",
    "cbi",
    "warrant",
    "arrest",
    "fine",
    "tax",
    "prize",
]

DIGITAL_ARREST_KEYWORDS = [
    "cbi",
    "police",
    "arrest",
    "warrant",
    "case",
    "fir",
    "cyber crime",
]
ELECTRICITY_KEYWORDS = [
    "electricity",
    "power",
    "bill",
    "discom",
    "meter",
    "connection",
]
JOB_KEYWORDS = [
    "job",
    "hiring",
    "interview",
    "salary",
    "offer",
    "resume",
    "joining",
]


def score_scam_intent(text: str, intel: Dict[str, List[str]]) -> int:
    score = 0
    text_lower = text.lower()

    for kw in SCAM_SIGNAL_KEYWORDS:
        if kw in text_lower:
            score += 2

    if intel["upiIds"]:
        score += 4
    if intel["bankAccounts"]:
        score += 4
    if intel["phishingLinks"]:
        score += 4
    if intel["phoneNumbers"]:
        score += 2

    if "http" in text_lower:
        score += 2
    if "send" in text_lower or "transfer" in text_lower or "pay" in text_lower:
        score += 2

    logger.debug("Scam score computed=%s", score)
    return score


def scam_confirmed(score: int) -> bool:
    return score >= 6


def classify_scam_type(text: str) -> str:
    text_lower = text.lower()
    if any(kw in text_lower for kw in DIGITAL_ARREST_KEYWORDS):
        return "digital_arrest"
    if any(kw in text_lower for kw in ELECTRICITY_KEYWORDS):
        return "electricity"
    if any(kw in text_lower for kw in JOB_KEYWORDS):
        return "job"
    return "general"
