"""
🕵️ Agent 3: The Auditor
Silent intelligence extraction without alerting the scammer.
"""

from typing import Dict, Any
from datetime import datetime

from models.state import HoneyPotState
from utils.logger import logger, log_security_event
from utils.extraction import IntelligenceExtractor


class AuditorAgent:
    """
    The Auditor silently extracts and logs intelligence from all messages.
    
    This agent operates in the background without the scammer's knowledge.
    """
    
    def __init__(self):
        """Initialize Auditor agent."""
        self.extractor = IntelligenceExtractor()
    
    def extract_intelligence(self, state: HoneyPotState) -> HoneyPotState:
        """
        Silently extract all intelligence from the current message.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with extracted intelligence
        """
        session_id = state.get("session_id", "unknown")
        current_message = state.get("current_message", "")
        
        log_security_event(
            logger,
            "AUDITOR",
            "Silent extraction initiated",
            session_id=session_id,
        )
        
        # ===================================
        # Extract All Intelligence
        # ===================================
        extracted = self.extractor.extract_all(current_message)
        
        # Update state with NEW extractions (append to existing)
        state["extracted_upi_ids"] = list(set(
            state.get("extracted_upi_ids", []) + extracted["upi_ids"]
        ))
        
        state["extracted_bank_accounts"] = list(set(
            state.get("extracted_bank_accounts", []) + extracted["bank_accounts"]
        ))
        
        state["extracted_phone_numbers"] = list(set(
            state.get("extracted_phone_numbers", []) + extracted["phone_numbers"]
        ))
        
        state["extracted_urls"] = list(set(
            state.get("extracted_urls", []) + extracted["urls"]
        ))
        
        state["extracted_emails"] = list(set(
            state.get("extracted_emails", []) + extracted["emails"]
        ))
        
        state["extracted_keywords"] = list(set(
            state.get("extracted_keywords", []) + extracted["keywords"]
        ))
        
        # ===================================
        # Update Forensic Ledger
        # ===================================
        forensic_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "turn_number": state.get("turn_number", 0),
            "message_preview": current_message[:100],
            "extracted": extracted,
        }
        
        forensic_ledger = state.get("forensic_ledger", [])
        forensic_ledger.append(forensic_entry)
        state["forensic_ledger"] = forensic_ledger
        
        # ===================================
        # Log Findings
        # ===================================
        findings = []
        if extracted["upi_ids"]:
            findings.append(f"UPI={len(extracted['upi_ids'])}")
        if extracted["bank_accounts"]:
            findings.append(f"Accounts={len(extracted['bank_accounts'])}")
        if extracted["phone_numbers"]:
            findings.append(f"Phones={len(extracted['phone_numbers'])}")
        if extracted["urls"]:
            findings.append(f"URLs={len(extracted['urls'])}")
        if extracted["emails"]:
            findings.append(f"Emails={len(extracted['emails'])}")
        
        if findings:
            log_security_event(
                logger,
                "AUDITOR",
                f"Intelligence extracted: {', '.join(findings)}",
                session_id=session_id,
            )
        else:
            log_security_event(
                logger,
                "AUDITOR",
                "No new intelligence in this message",
                session_id=session_id,
            )
        
        # ===================================
        # Check for High-Value Intel
        # ===================================
        total_upi = len(state["extracted_upi_ids"])
        total_urls = len(state["extracted_urls"])
        total_phones = len(state["extracted_phone_numbers"])
        
        high_value_threshold = 3  # Trigger callback if we have 3+ pieces of intel
        total_intel = total_upi + total_urls + total_phones
        
        if total_intel >= high_value_threshold:
            log_security_event(
                logger,
                "AUDITOR",
                f"🎯 HIGH VALUE: {total_intel} pieces of intelligence collected",
                session_id=session_id,
            )
            # Could set a flag here to prioritize callback
        
        state["auditor_complete"] = True
        
        return state
    
    def generate_summary(self, state: HoneyPotState) -> str:
        """
        Generate a summary of all extracted intelligence.
        
        Args:
            state: Current state
            
        Returns:
            Human-readable summary
        """
        summary_parts = []
        
        turn_count = state.get("turn_number", 0)
        scam_prob = state.get("scam_probability", 0.0)
        
        summary_parts.append(
            f"Scam probability: {scam_prob:.1%}. "
            f"Engaged for {turn_count} turns."
        )
        
        upi_ids = state.get("extracted_upi_ids", [])
        if upi_ids:
            summary_parts.append(f"UPI IDs: {', '.join(upi_ids)}")
        
        banks = state.get("extracted_bank_accounts", [])
        if banks:
            summary_parts.append(f"Bank accounts: {', '.join(banks[:3])}")
        
        phones = state.get("extracted_phone_numbers", [])
        if phones:
            summary_parts.append(f"Phone numbers: {', '.join(phones)}")
        
        urls = state.get("extracted_urls", [])
        if urls:
            summary_parts.append(f"URLs detected: {len(urls)}")
        
        keywords = state.get("extracted_keywords", [])
        if keywords:
            top_keywords = keywords[:5]
            summary_parts.append(f"Keywords: {', '.join(top_keywords)}")
        
        if len(summary_parts) == 1:
            summary_parts.append("No actionable intelligence extracted yet.")
        
        return " | ".join(summary_parts)
