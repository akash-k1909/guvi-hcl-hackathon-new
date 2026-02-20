"""
🛡️ End-to-End Workflow Tests
Tests the complete honey-pot workflow.
"""

import pytest
import asyncio
from datetime import datetime

from models.state import HoneyPotState
from agents.profiler import ProfilerAgent
from agents.actor import ActorAgent
from agents.auditor import AuditorAgent
from utils.extraction import IntelligenceExtractor
from utils.forensics import ForensicsAnalyzer


class TestIntelligenceExtraction:
    """Test intelligence extraction utilities."""
    
    def test_upi_extraction(self):
        """Test UPI ID extraction."""
        text = "Send money to scammer123@paytm or winner@phonepe"
        upi_ids = IntelligenceExtractor.extract_upi_ids(text)
        assert len(upi_ids) == 2
        assert "scammer123@paytm" in upi_ids
    
    def test_url_extraction(self):
        """Test URL extraction."""
        text = "Click here: https://malicious-site.tk/verify and http://phishing.com"
        urls = IntelligenceExtractor.extract_urls(text)
        assert len(urls) >= 2
    
    def test_phone_extraction(self):
        """Test phone number extraction."""
        text = "Call +91 9876543210 or 9123456789 immediately"
        phones = IntelligenceExtractor.extract_phone_numbers(text)
        assert len(phones) >= 1
    
    def test_keywords_extraction(self):
        """Test scam keyword extraction."""
        text = "URGENT! Your account is blocked. Verify OTP immediately!"
        keywords = IntelligenceExtractor.extract_keywords(text)
        assert "urgent" in keywords
        assert "blocked" in keywords
        assert "otp" in keywords


class TestForensics:
    """Test forensics analysis."""
    
    def test_trai_validation(self):
        """Test TRAI header validation."""
        # Valid formats
        valid, reason = ForensicsAnalyzer.validate_trai_header("9876543210")
        assert valid
        
        valid, reason = ForensicsAnalyzer.validate_trai_header("HDFCBK")
        assert valid
        
        # Invalid format
        valid, reason = ForensicsAnalyzer.validate_trai_header("SCAM")
        assert not valid or "non-standard" in reason.lower()
    
    def test_domain_extraction(self):
        """Test domain extraction from URL."""
        url = "https://malicious-site.tk/verify?user=123"
        domain = ForensicsAnalyzer.extract_domain_from_url(url)
        assert domain == "malicious-site.tk"
    
    def test_risk_score_calculation(self):
        """Test risk score calculation."""
        score, flags = ForensicsAnalyzer.calculate_risk_score(
            trai_valid=False,
            domain_age_days=15,  # Very new domain
            suspicious_url_count=2,
            keyword_count=5,
            has_payment_info=True,
        )
        
        # Should be high risk
        assert score >= 0.7
        assert "trai_violation" in flags
        assert "very_new_domain" in flags


class TestProfilerAgent:
    """Test Profiler agent."""
    
    @pytest.mark.asyncio
    async def test_profiler_analysis(self):
        """Test complete profiler analysis."""
        profiler = ProfilerAgent()
        
        state: HoneyPotState = {
            "session_id": "test-123",
            "sender_id": "SCAM99",
            "current_message": "Urgent! Your account blocked. Verify at https://fake-bank.tk. Send OTP.",
            "messages": [],
        }
        
        result = profiler.analyze(state)
        
        # Check profiler completed
        assert result["profiler_complete"] is True
        
        # Should detect as scam
        assert result["scam_probability"] > 0.5
        
        # Should have risk flags
        assert len(result["risk_flags"]) > 0


class TestActorAgent:
    """Test Actor agent."""
    
    @pytest.mark.asyncio
    async def test_actor_generates_response(self):
        """Test Actor generates persona response."""
        actor = ActorAgent()
        
        state: HoneyPotState = {
            "session_id": "test-123",
            "turn_number": 1,
            "persona_used": "confused_senior",
            "current_message": "Your bank account is locked",
            "messages": [],
        }
        
        result = actor.generate_response(state)
        
        # Check response generated
        assert result["actor_complete"] is True
        assert "actor_response" in result
        assert len(result["actor_response"]) > 0
        
        # Check emotional state set
        assert "emotional_state" in result


class TestAuditorAgent:
    """Test Auditor agent."""
    
    def test_auditor_extraction(self):
        """Test Auditor extracts intelligence."""
        auditor = AuditorAgent()
        
        state: HoneyPotState = {
            "session_id": "test-123",
            "turn_number": 1,
            "current_message": "Send ₹500 to scammer@paytm or call 9876543210",
            "extracted_upi_ids": [],
            "extracted_phone_numbers": [],
            "forensic_ledger": [],
        }
        
        result = auditor.extract_intelligence(state)
        
        # Check extraction completed
        assert result["auditor_complete"] is True
        
        # Check intelligence extracted
        assert len(result["extracted_upi_ids"]) > 0
        assert len(result["extracted_phone_numbers"]) > 0
        
        # Check forensic ledger updated
        assert len(result["forensic_ledger"]) > 0


class TestEndToEndWorkflow:
    """Test complete workflow."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete agent workflow."""
        profiler = ProfilerAgent()
        actor = ActorAgent()
        auditor = AuditorAgent()
        
        # Initial state
        state: HoneyPotState = {
            "session_id": "e2e-test-123",
            "sender_id": "9876543210",
            "current_message": "URGENT! Account blocked. Verify: https://fake.tk. Pay ₹500 to winner@paytm",
            "turn_number": 1,
            "messages": [],
            "persona_used": "confused_senior",
            "extracted_upi_ids": [],
            "extracted_phone_numbers": [],
            "extracted_urls": [],
            "forensic_ledger": [],
        }
        
        # Run through agents
        state = profiler.analyze(state)
        state = actor.generate_response(state)
        state = auditor.extract_intelligence(state)
        
        # Verify all agents completed
        assert state["profiler_complete"] is True
        assert state["actor_complete"] is True
        assert state["auditor_complete"] is True
        
        # Verify scam detected
        assert state["scam_probability"] > 0.5
        
        # Verify response generated
        assert len(state["actor_response"]) > 0
        
        # Verify intelligence extracted
        assert len(state["extracted_upi_ids"]) > 0
        assert len(state["extracted_urls"]) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
