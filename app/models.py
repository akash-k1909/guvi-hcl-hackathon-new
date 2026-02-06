"""Pydantic schemas for request payloads."""

from typing import List
from pydantic import BaseModel, Field


class Message(BaseModel):
    sender: str
    text: str
    timestamp: int


class Metadata(BaseModel):
    channel: str = "SMS"
    language: str = "English"
    locale: str = "IN"


class InputData(BaseModel):
    session_id: str = Field(alias="sessionId")
    message: Message
    conversation_history: List[Message] = Field(
        default_factory=list, alias="conversationHistory"
    )
    metadata: Metadata = Field(default_factory=Metadata)

    class Config:
        populate_by_name = True
