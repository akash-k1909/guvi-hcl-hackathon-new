"""
🛡️ API Request/Response Schemas
Pydantic models for FastAPI endpoints following hackathon requirements.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class MessageContent(BaseModel):
    """Message object from GUVI format."""
    sender: str = Field(..., description="Sender: 'scammer' or 'user'")
    text: str = Field(..., description="Message text content")
    timestamp: int = Field(..., description="Epoch timestamp in milliseconds")


class Metadata(BaseModel):
    """Optional metadata from GUVI."""
    channel: Optional[str] = Field(default=None, description="SMS/WhatsApp/Email")
    language: Optional[str] = Field(default=None, description="Language used")
    locale: Optional[str] = Field(default=None, description="Country/region")
    
    class Config:
        extra = "allow"


class IncomingMessage(BaseModel):
    """
    Message from GUVI's Mock Scammer API - EXACT FORMAT.
    """
    sessionId: str = Field(..., description="Unique session identifier")
    message: MessageContent = Field(..., description="Current message")
    conversationHistory: List[MessageContent] = Field(
        default_factory=list,
        description="Previous messages in conversation"
    )
    metadata: Optional[Metadata] = Field(
        default=None,
        description="Optional metadata"
    )
    
    class Config:
        extra = "allow"


class HoneyPotResponse(BaseModel):
    """
    Response to GUVI's Mock Scammer API - EXACT FORMAT.
    """
    status: str = Field(default="success", description="Response status")
    reply: str = Field(..., description="Agent's reply to scammer")


class ExtractedIntelligence(BaseModel):
    """
    Intelligence extracted by the Auditor agent.
    """
    upi_ids: List[str] = Field(default_factory=list, description="Extracted UPI IDs")
    bank_accounts: List[str] = Field(
        default_factory=list,
        description="Bank account numbers"
    )
    phone_numbers: List[str] = Field(
        default_factory=list,
        description="Phone numbers"
    )
    urls: List[str] = Field(default_factory=list, description="Extracted URLs")
    emails: List[str] = Field(default_factory=list, description="Email addresses")
    payment_links: List[str] = Field(
        default_factory=list,
        description="Payment/phishing links"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Scam keywords identified"
    )
    raw_extractions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw extraction data with timestamps"
    )


class ExtractedIntelligenceCallback(BaseModel):
    """Intelligence for GUVI callback - EXACT FORMAT."""
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)


class CallbackPayload(BaseModel):
    """
    Final intelligence report for GUVI callback - EXACT FORMAT.
    """
    sessionId: str = Field(..., description="Session identifier")
    scamDetected: bool = Field(..., description="Whether scam was detected")
    totalMessagesExchanged: int = Field(..., description="Total messages in conversation")
    extractedIntelligence: ExtractedIntelligenceCallback = Field(
        ...,
        description="All extracted intelligence"
    )
    agentNotes: str = Field(..., description="Summary of scammer behavior")


class HealthCheckResponse(BaseModel):
    """
    Health check endpoint response.
    """
    status: str = Field(default="healthy", description="Service status")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )
    redis_connected: bool = Field(..., description="Redis connection status")
    version: str = Field(default="1.0.0", description="API version")
