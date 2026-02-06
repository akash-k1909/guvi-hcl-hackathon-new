"""
🛡️ LangGraph State Definition
TypedDict-based state for the multi-agent state machine.
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class HoneyPotState(TypedDict, total=False):
    """
    State maintained throughout the LangGraph execution.
    
    This state is passed between agents and persisted in Redis.
    """
    
    # ===================================
    # Session Metadata
    # ===================================
    session_id: str
    turn_number: int
    start_time: datetime
    last_update_time: datetime
    
    # ===================================
    # Conversation History
    # ===================================
    messages: List[Dict[str, Any]]  # [{"role": "scammer/agent", "content": "...", "timestamp": ...}]
    sender_id: str
    current_message: str
    
    # ===================================
    # Profiler Agent Output
    # ===================================
    scam_probability: float  # 0.0 to 1.0
    risk_flags: List[str]  # ["suspicious_url", "urgency_keyword", "trai_violation"]
    domain_age_days: Optional[int]
    trai_valid: Optional[bool]
    profiler_complete: bool
    
    # ===================================
    # Actor Agent Output
    # ===================================
    actor_response: str  # Generated response to send back
    persona_used: str  # "confused_senior" or "eager_student"
    emotional_state: str  # "confused", "scared", "curious", "extracting"
    actor_complete: bool
    
    # ===================================
    # Auditor Agent Output (Silent)
    # ===================================
    extracted_upi_ids: List[str]
    extracted_bank_accounts: List[str]
    extracted_phone_numbers: List[str]
    extracted_urls: List[str]
    extracted_emails: List[str]
    extracted_keywords: List[str]
    forensic_ledger: List[Dict[str, Any]]  # Timestamped extraction events
    auditor_complete: bool
    
    # ===================================
    # State Machine Control
    # ===================================
    current_phase: str  # "START", "DETECT", "ENGAGE", "EXTRACT", "CALLBACK"
    should_continue: bool
    should_callback: bool
    engagement_duration: float  # Seconds
    
    # ===================================
    # Callback Status
    # ===================================
    callback_sent: bool
    callback_success: bool
    callback_attempts: int
    callback_error: Optional[str]
