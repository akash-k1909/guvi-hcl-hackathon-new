"""Intelligence extraction and merge utilities."""

import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

PATTERNS = {
    "upi": re.compile(r"[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}", re.IGNORECASE),
    "bank": re.compile(r"\b\d{9,18}\b"),
    "phone": re.compile(r"(?:\+91[\-\s]?)?[6789]\d{9}"),
    "url": re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", re.IGNORECASE),
}

SUSPICIOUS_KEYWORDS = [
    "block",
    "verify",
    "kyc",
    "suspend",
    "urgent",
    "police",
    "cbi",
    "expire",
    "warrant",
    "apk",
    "netbanking",
    "account",
    "fraud",
    "freeze",
    "penalty",
    "arrest",
    "confirm",
    "otp",
    "cvv",
    "pin",
    "refund",
    "chargeback",
    "loan",
    "reward",
    "gift",
    "lottery",
]


def extract_intelligence(text: str) -> Dict[str, List[str]]:
    text_lower = text.lower()
    result = {
        "bankAccounts": sorted(set(PATTERNS["bank"].findall(text))),
        "upiIds": sorted(set(PATTERNS["upi"].findall(text))),
        "phishingLinks": sorted(set(PATTERNS["url"].findall(text))),
        "phoneNumbers": sorted(set(PATTERNS["phone"].findall(text))),
        "suspiciousKeywords": [kw for kw in SUSPICIOUS_KEYWORDS if kw in text_lower],
    }
    logger.debug(
        "Intel counts bank=%s upi=%s url=%s phone=%s kw=%s",
        len(result["bankAccounts"]),
        len(result["upiIds"]),
        len(result["phishingLinks"]),
        len(result["phoneNumbers"]),
        len(result["suspiciousKeywords"]),
    )
    return result


def merge_intelligence(
    total: Dict[str, List[str]], new: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    merged = {}
    for key in total:
        merged[key] = sorted(set(total[key] + new[key]))
    return merged


def has_actionable_intel(intel: Dict[str, List[str]]) -> bool:
    return any(
        len(intel[key]) > 0
        for key in ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers"]
    )
