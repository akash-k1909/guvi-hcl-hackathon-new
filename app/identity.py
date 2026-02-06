"""Persona generation."""

import logging
import random
from typing import Any, Dict

logger = logging.getLogger(__name__)

INDIAN_NAMES = [
    "Ramesh",
    "Suresh",
    "Priya",
    "Rajesh",
    "Anita",
    "Vijay",
    "Sunita",
    "Amit",
    "Rakesh",
    "Meena",
    "Sanjay",
    "Kavita",
    "Arun",
    "Deepak",
    "Pooja",
    "Ravi",
    "Neeta",
    "Mohan",
    "Seema",
    "Ashok",
]

INDIAN_CITIES = [
    "Mumbai",
    "Delhi",
    "Bangalore",
    "Chennai",
    "Kolkata",
    "Hyderabad",
    "Pune",
    "Ahmedabad",
    "Jaipur",
    "Lucknow",
    "Kanpur",
    "Nagpur",
    "Indore",
    "Bhopal",
    "Patna",
    "Vadodara",
    "Ludhiana",
    "Agra",
]

USED_NAMES = set()

PROFILE_CONFIG = {
    "digital_arrest": {
        "role": "scared businessman",
        "name_pool": ["Vikram", "Sanjay", "Rakesh", "Amit", "Arun"],
        "age_range": (30, 55),
    },
    "electricity": {
        "role": "confused pensioner",
        "name_pool": ["Ramesh", "Mohan", "Ashok", "Suresh", "Ravi"],
        "age_range": (58, 75),
    },
    "job": {
        "role": "desperate student",
        "name_pool": ["Rahul", "Karan", "Neha", "Priya", "Pooja"],
        "age_range": (18, 25),
    },
    "general": {
        "role": "confused citizen",
        "name_pool": INDIAN_NAMES,
        "age_range": (25, 65),
    },
}


def _get_unique_name(pool):
    available = [name for name in pool if name not in USED_NAMES]
    if not available:
        USED_NAMES.clear()
        available = pool[:]
    name = random.choice(available)
    USED_NAMES.add(name)
    return name


def create_identity(scam_type: str) -> Dict[str, Any]:
    profile = PROFILE_CONFIG.get(scam_type, PROFILE_CONFIG["general"])
    name = _get_unique_name(profile["name_pool"])
    age_min, age_max = profile["age_range"]
    identity = {
        "name": name,
        "age": random.randint(age_min, age_max),
        "city": random.choice(INDIAN_CITIES),
        "role": profile["role"],
        "scamType": scam_type,
    }
    logger.debug(
        "Identity created name=%s role=%s type=%s",
        identity["name"],
        identity["role"],
        scam_type,
    )
    return identity
