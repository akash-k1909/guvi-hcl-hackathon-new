"""
📡 GUVI Callback Service
Self-healing callback with exponential backoff retry.
"""

import asyncio
from typing import Optional, Dict, Any

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from models.schemas import CallbackPayload
from utils.logger import logger, log_security_event
from config import settings


class CallbackService:
    """
    Handles callbacks to the GUVI hackathon endpoint with automatic retries.
    """
    
    def __init__(self):
        """Initialize callback service."""
        self.callback_url = settings.guvi_callback_url
        self.api_key = settings.guvi_api_key
        self.timeout = 10.0  # seconds
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def _send_with_retry(
        self,
        session_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send callback with automatic retry.
        
        Args:
            session_id: Session identifier
            payload: Callback payload
            
        Returns:
            Response data
            
        Raises:
            httpx.HTTPError: If all retries fail
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Session-Id": session_id,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            log_security_event(
                logger,
                "CALLBACK",
                f"Sending callback to GUVI",
                session_id=session_id,
            )
            
            response = await client.post(
                self.callback_url,
                json=payload,
                headers=headers,
            )
            
            response.raise_for_status()
            
            log_security_event(
                logger,
                "CALLBACK",
                f"✅ Callback successful: {response.status_code}",
                session_id=session_id,
            )
            
            return response.json()
    
    async def send_callback(
        self,
        payload: CallbackPayload,
        session_id: str
    ) -> tuple[bool, Optional[str]]:
        """
        Send final intelligence report to GUVI endpoint.
        
        Args:
            payload: Callback payload
            session_id: Session identifier
            
        Returns:
            (success, error_message) tuple
        """
        try:
            # Convert Pydantic model to dict
            payload_dict = payload.model_dump(mode="json")
            
            # Send with retry
            result = await self._send_with_retry(session_id, payload_dict)
            
            log_security_event(
                logger,
                "CALLBACK",
                "🎯 Callback completed successfully",
                session_id=session_id,
                response=str(result)[:100],
            )
            
            return True, None
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            logger.error(f"❌ Callback failed after retries: {error_msg}")
            return False, error_msg
            
        except httpx.TimeoutException:
            error_msg = "Request timeout after all retries"
            logger.error(f"❌ Callback timeout: {error_msg}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)[:200]}"
            logger.error(f"❌ Callback error: {error_msg}")
            return False, error_msg
    
    async def send_callback_background(
        self,
        payload: CallbackPayload,
        session_id: str
    ) -> None:
        """
        Send callback in background with local fallback on failure.
        
        Args:
            payload: Callback payload
            session_id: Session identifier
        """
        success, error = await self.send_callback(payload, session_id)
        
        if not success:
            # Fallback: Save to local file
            fallback_path = f"failed_callbacks/{session_id}.json"
            try:
                import os
                import json
                
                os.makedirs("failed_callbacks", exist_ok=True)
                
                with open(fallback_path, "w") as f:
                    json.dump(
                        payload.model_dump(mode="json"),
                        f,
                        indent=2,
                        ensure_ascii=False
                    )
                
                logger.warning(
                    f"⚠️ Callback failed, saved to: {fallback_path}"
                )
                
            except Exception as e:
                logger.error(f"❌ Failed to save fallback file: {e}")


# Global callback service instance
callback_service = CallbackService()
