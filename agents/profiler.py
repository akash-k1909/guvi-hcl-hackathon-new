"""
🔍 Agent 1: The Profiler
Zero-trust validation and scam detection.
"""

from typing import Dict, Any

from models.state import HoneyPotState
from utils.logger import logger, log_security_event
from utils.forensics import ForensicsAnalyzer
from utils.extraction import IntelligenceExtractor
from config import settings


class ProfilerAgent:
    """
    The Profiler analyzes incoming messages for scam indicators.
    
    Responsibilities:
    - TRAI header validation
    - Domain age verification
    - URL safety analysis
    - Calculate scam probability score
    """
    
    def __init__(self):
        """Initialize Profiler agent."""
        self.forensics = ForensicsAnalyzer()
        self.extractor = IntelligenceExtractor()
    
    def analyze(self, state: HoneyPotState) -> HoneyPotState:
        """
        Run zero-trust analysis on the current message.
        
        Args:
            state: Current LangGraph state
            
        Returns:
            Updated state with profiler results
        """
        session_id = state.get("session_id", "unknown")
        sender_id = state.get("sender_id", "")
        message = state.get("current_message", "")
        
        log_security_event(
            logger,
            "PROFILER",
            "Starting zero-trust analysis",
            session_id=session_id,
        )
        
        # ===================================
        # TRAI Header Validation
        # ===================================
        trai_valid = False
        trai_reason = ""
        
        if settings.enable_trai_validation:
            trai_valid, trai_reason = self.forensics.validate_trai_header(sender_id)
            state["trai_valid"] = trai_valid
            log_security_event(
                logger,
                "PROFILER",
                f"TRAI validation: {trai_reason}",
                session_id=session_id,
                valid=trai_valid,
            )
        else:
            state["trai_valid"] = None
        
        # ===================================
        # Extract Intelligence
        # ===================================
        extracted = self.extractor.extract_all(message)
        
        urls = extracted["urls"]
        suspicious_urls = extracted["suspicious_urls"]
        keywords = extracted["keywords"]
        upi_ids = extracted["upi_ids"]
        bank_accounts = extracted["bank_accounts"]
        
        log_security_event(
            logger,
            "PROFILER",
            "Intelligence extracted",
            session_id=session_id,
            urls=len(urls),
            suspicious=len(suspicious_urls),
            keywords=len(keywords),
            upi=len(upi_ids),
        )
        
        # ===================================
        # Domain Age Check
        # ===================================
        domain_age_days = None
        
        if settings.enable_domain_age_check and urls:
            # Check first URL's domain
            domain = self.forensics.extract_domain_from_url(urls[0])
            if domain:
                age_days, age_status = self.forensics.check_domain_age(domain)
                if age_days is not None:
                    domain_age_days = age_days
                    state["domain_age_days"] = age_days
                    log_security_event(
                        logger,
                        "PROFILER",
                        f"Domain age: {age_days} days - {age_status}",
                        session_id=session_id,
                    )
        
        # ===================================
        # Calculate Risk Score
        # ===================================
        has_payment_info = len(upi_ids) > 0 or len(bank_accounts) > 0
        
        scam_score, risk_flags = self.forensics.calculate_risk_score(
            trai_valid=trai_valid,
            domain_age_days=domain_age_days,
            suspicious_url_count=len(suspicious_urls),
            keyword_count=len(keywords),
            has_payment_info=has_payment_info,
        )
        
        state["scam_probability"] = scam_score
        state["risk_flags"] = risk_flags
        state["profiler_complete"] = True
        
        log_security_event(
            logger,
            "PROFILER",
            f"🎯 Scam probability: {scam_score:.2%}",
            session_id=session_id,
            flags=", ".join(risk_flags) if risk_flags else "none",
        )
        
        # ===================================
        # Decision: Should we engage?
        # ===================================
        if scam_score >= settings.scam_threshold:
            state["should_continue"] = True
            log_security_event(
                logger,
                "PROFILER",
                f"✅ Score above threshold ({settings.scam_threshold:.2%}), engaging Actor",
                session_id=session_id,
            )
        else:
            state["should_continue"] = False
            log_security_event(
                logger,
                "PROFILER",
                f"❌ Score below threshold, sending generic response",
                session_id=session_id,
            )
        
        return state
