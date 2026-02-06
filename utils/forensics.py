"""
🛡️ Forensics & Domain Analysis
Zero-trust validation using TRAI headers and domain age verification.
"""

import re
from typing import Optional, Tuple, List
from datetime import datetime, timedelta
import socket

import tldextract
import whois

from utils.logger import logger


class ForensicsAnalyzer:
    """
    Domain and sender validation for zero-trust profiling.
    """
    
    # TRAI-compliant sender ID pattern (6 characters, alphanumeric)
    # Format: XX-NNNNNN where XX is telecom operator code
    TRAI_PATTERN = re.compile(r'^[A-Z]{2}-[A-Z0-9]{6}$', re.IGNORECASE)
    
    # Known legitimate banking sender IDs (whitelist)
    LEGITIMATE_SENDERS = {
        'HDFCBK', 'ICICIB', 'SBIIN', 'KOTAKB', 'AXISNB',
        'PNBSMS', 'BOISMS', 'CANBNK', 'UNIONSMS', 'IDBIBN',
    }
    
    @staticmethod
    def validate_trai_header(sender_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if sender ID follows TRAI format.
        
        Args:
            sender_id: Sender ID to validate
            
        Returns:
            (is_valid, reason) tuple
        """
        # Check if numeric (phone number)
        if sender_id.isdigit():
            if len(sender_id) == 10:
                return True, "Valid 10-digit phone number"
            elif len(sender_id) > 10:
                return True, "Valid international number"
            else:
                return False, "Invalid phone number length"
        
        # Check TRAI format
        if ForensicsAnalyzer.TRAI_PATTERN.match(sender_id):
            return True, "Valid TRAI format"
        
        # Check if in whitelist
        sender_upper = sender_id.upper()
        if any(legit in sender_upper for legit in ForensicsAnalyzer.LEGITIMATE_SENDERS):
            return True, "Whitelisted sender"
        
        # Generic alphanumeric (6 chars)
        if len(sender_id) == 6 and sender_id.isalnum():
            return True, "Valid 6-character alphanumeric"
        
        return False, f"Non-standard format: {sender_id}"
    
    @staticmethod
    def extract_domain_from_url(url: str) -> Optional[str]:
        """
        Extract domain from URL using tldextract.
        
        Args:
            url: URL to parse
            
        Returns:
            Domain string or None
        """
        try:
            extracted = tldextract.extract(url)
            if extracted.domain and extracted.suffix:
                return f"{extracted.domain}.{extracted.suffix}"
            return None
        except Exception as e:
            logger.warning(f"Failed to extract domain from {url}: {e}")
            return None
    
    @staticmethod
    def check_domain_age(domain: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Check domain registration age using WHOIS.
        
        Args:
            domain: Domain to check
            
        Returns:
            (age_in_days, status_message) tuple
        """
        try:
            w = whois.whois(domain)
            
            # Get creation date
            creation_date = w.creation_date
            
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if creation_date:
                age = (datetime.now() - creation_date).days
                
                if age < 30:
                    status = "⚠️ Very new domain (< 30 days)"
                elif age < 90:
                    status = "⚠️ Recent domain (< 90 days)"
                elif age < 365:
                    status = "Young domain (< 1 year)"
                else:
                    status = "✓ Established domain"
                
                return age, status
            else:
                return None, "⚠️ Creation date unavailable"
                
        except Exception as e:
            logger.warning(f"WHOIS error for {domain}: {e}")
            return None, f"⚠️ Error: {str(e)[:50]}"
    
    @staticmethod
    def calculate_risk_score(
        trai_valid: bool,
        domain_age_days: Optional[int],
        suspicious_url_count: int,
        keyword_count: int,
        has_payment_info: bool,
    ) -> Tuple[float, List[str]]:
        """
        Calculate aggregate risk score.
        
        Args:
            trai_valid: Whether sender ID is TRAI valid
            domain_age_days: Domain age in days (None if unknown)
            suspicious_url_count: Number of suspicious URLs
            keyword_count: Number of scam keywords
            has_payment_info: Whether message contains UPI/bank info
            
        Returns:
            (risk_score, risk_flags) tuple where score is 0.0 to 1.0
        """
        score = 0.0
        flags = []
        
        # TRAI validation (20 points)
        if not trai_valid:
            score += 0.2
            flags.append("trai_violation")
        
        # Domain age (30 points)
        if domain_age_days is not None:
            if domain_age_days < 30:
                score += 0.3
                flags.append("very_new_domain")
            elif domain_age_days < 90:
                score += 0.2
                flags.append("recent_domain")
            elif domain_age_days < 365:
                score += 0.1
                flags.append("young_domain")
        
        # Suspicious URLs (25 points)
        if suspicious_url_count > 0:
            score += min(0.25, suspicious_url_count * 0.15)
            flags.append(f"suspicious_urls_{suspicious_url_count}")
        
        # Scam keywords (15 points)
        if keyword_count > 0:
            score += min(0.15, keyword_count * 0.03)
            flags.append(f"scam_keywords_{keyword_count}")
        
        # Payment information (10 points)
        if has_payment_info:
            score += 0.1
            flags.append("payment_info_present")
        
        return min(score, 1.0), flags
    
    @staticmethod
    def is_ip_address(host: str) -> bool:
        """Check if host is an IP address instead of domain."""
        try:
            socket.inet_aton(host)
            return True
        except socket.error:
            return False
