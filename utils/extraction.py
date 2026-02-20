"""
🛡️ Intelligence Extraction Patterns
Regex-based patterns for extracting scam intelligence from messages.
"""

import re
from typing import List, Set, Dict, Any
from datetime import datetime

import phonenumbers
from phonenumbers import NumberParseException


class IntelligenceExtractor:
    """
    Hybrid regex + library-based extractor for scam intelligence.
    """
    
    # UPI ID pattern: username@provider
    UPI_PATTERN = re.compile(
        r'\b[\w\.\-]{3,}@(?:paytm|phonepe|googlepay|ybl|axl|okicici|okhdfcbank|oksbi|okaxis|upi)\b',
        re.IGNORECASE
    )
    
    # Bank account number (9-18 digits)
    BANK_ACCOUNT_PATTERN = re.compile(
        r'\b\d{9,18}\b'
    )
    
    # IFSC Code pattern
    IFSC_PATTERN = re.compile(
        r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
    )
    
    # Email pattern
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    
    # URL pattern
    URL_PATTERN = re.compile(
        r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
        re.IGNORECASE
    )
    
    # Suspicious URL patterns (common phishing TLDs)
    SUSPICIOUS_TLDS = {
        '.tk', '.ml', '.ga', '.cf', '.gq',  # Free domains
        '.xyz', '.top', '.win', '.bid', '.click',  # Cheap domains
    }
    
    # Scam keywords
    SCAM_KEYWORDS = {
        # Urgency
        'urgent', 'immediately', 'now', 'expire', 'suspended', 'blocked',
        'turant', 'abhi', 'jaldi',  # Hinglish
        
        # Verification
        'verify', 'confirm', 'update', 'validate', 'authenticate',
        'verification', 'otp', 'pin', 'password',
        
        # Rewards
        'congratulations', 'winner', 'prize', 'reward', 'cashback',
        'free', 'gift', 'bonus', 'lottery',
        'badhaai', 'inaam', 'muft',  # Hinglish
        
        # Banking
        'bank account', 'debit card', 'credit card', 'kyc',
        'account suspended', 'account locked', 'unauthorized',
        
        # Actions
        'click here', 'click link', 'download', 'install',
        'call us', 'reply', 'send', 'transfer',
        
        # Payment
        'payment', 'transfer', 'send money', 'processing fee',
        'charges', 'tax', 'refund',
    }
    
    @staticmethod
    def extract_upi_ids(text: str) -> List[str]:
        """Extract UPI IDs from text."""
        matches = IntelligenceExtractor.UPI_PATTERN.findall(text)
        return list(set(matches))  # Remove duplicates
    
    @staticmethod
    def extract_bank_accounts(text: str) -> List[str]:
        """Extract potential bank account numbers."""
        matches = IntelligenceExtractor.BANK_ACCOUNT_PATTERN.findall(text)
        # Filter out obviously wrong matches (like timestamps)
        filtered = [m for m in matches if 9 <= len(m) <= 18]
        return list(set(filtered))
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """
        Extract phone numbers using phonenumbers library.
        Focuses on Indian numbers but supports international.
        """
        phone_numbers_found: Set[str] = set()
        
        # Try parsing as Indian number first
        for match in phonenumbers.PhoneNumberMatcher(text, "IN"):
            formatted = phonenumbers.format_number(
                match.number,
                phonenumbers.PhoneNumberFormat.E164
            )
            phone_numbers_found.add(formatted)
        
        # Also try without region
        for match in phonenumbers.PhoneNumberMatcher(text, None):
            formatted = phonenumbers.format_number(
                match.number,
                phonenumbers.PhoneNumberFormat.E164
            )
            phone_numbers_found.add(formatted)
        
        return list(phone_numbers_found)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract all URLs from text."""
        matches = IntelligenceExtractor.URL_PATTERN.findall(text)
        return list(set(matches))
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract email addresses from text."""
        matches = IntelligenceExtractor.EMAIL_PATTERN.findall(text)
        return list(set(matches))
    
    @staticmethod
    def identify_suspicious_urls(urls: List[str]) -> List[str]:
        """Identify potentially malicious URLs based on TLD."""
        suspicious = []
        for url in urls:
            for tld in IntelligenceExtractor.SUSPICIOUS_TLDS:
                if tld in url.lower():
                    suspicious.append(url)
                    break
        return suspicious
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """Extract scam-related keywords from text."""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in IntelligenceExtractor.SCAM_KEYWORDS:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    @staticmethod
    def extract_all(text: str) -> Dict[str, Any]:
        """
        Extract all intelligence from text.
        
        Returns:
            Dictionary with all extracted data and timestamp
        """
        urls = IntelligenceExtractor.extract_urls(text)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "upi_ids": IntelligenceExtractor.extract_upi_ids(text),
            "bank_accounts": IntelligenceExtractor.extract_bank_accounts(text),
            "phone_numbers": IntelligenceExtractor.extract_phone_numbers(text),
            "urls": urls,
            "suspicious_urls": IntelligenceExtractor.identify_suspicious_urls(urls),
            "emails": IntelligenceExtractor.extract_emails(text),
            "keywords": IntelligenceExtractor.extract_keywords(text),
            "text_length": len(text),
        }
