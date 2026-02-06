"""
🛡️ Redis Session Manager
Handles state persistence and retrieval with automatic TTL management.
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime

import redis
from redis.exceptions import RedisError

from config import settings
from utils.logger import logger, log_security_event


class RedisClient:
    """
    Redis wrapper for session state management.
    """
    
    def __init__(self):
        """Initialize Redis connection pool."""
        try:
            self.client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            self.client.ping()
            log_security_event(
                logger,
                "SYSTEM",
                "Redis connection established",
                host=settings.redis_host,
                port=settings.redis_port,
            )
        except RedisError as e:
            logger.error(f"❌ Redis connection failed: {e}")
            logger.warning("⚠️ Falling back to in-memory state (not persistent)")
            self.client = None
            self._memory_store: Dict[str, str] = {}
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if self.client is None:
            return False
        try:
            self.client.ping()
            return True
        except RedisError:
            return False
    
    def _get_key(self, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"honeypot:session:{session_id}"
    
    def save_state(self, session_id: str, state: Dict[str, Any]) -> bool:
        """
        Save session state to Redis with TTL.
        
        Args:
            session_id: Session identifier
            state: State dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        key = self._get_key(session_id)
        
        try:
            # Add save timestamp
            state["_saved_at"] = datetime.utcnow().isoformat()
            
            # Serialize state
            serialized = json.dumps(state, default=str, ensure_ascii=False)
            
            if self.client:
                self.client.setex(
                    key,
                    settings.redis_ttl,
                    serialized
                )
                log_security_event(
                    logger,
                    "SYSTEM",
                    f"State saved to Redis",
                    session_id=session_id,
                    size_bytes=len(serialized),
                )
                return True
            else:
                # Fallback to in-memory
                self._memory_store[key] = serialized
                return True
                
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"❌ Failed to save state for {session_id}: {e}")
            return False
    
    def load_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session state from Redis.
        
        Args:
            session_id: Session identifier
            
        Returns:
            State dictionary if found, None otherwise
        """
        key = self._get_key(session_id)
        
        try:
            if self.client:
                serialized = self.client.get(key)
            else:
                serialized = self._memory_store.get(key)
            
            if serialized:
                state = json.loads(serialized)
                log_security_event(
                    logger,
                    "SYSTEM",
                    f"State loaded from Redis",
                    session_id=session_id,
                )
                return state
            else:
                log_security_event(
                    logger,
                    "SYSTEM",
                    f"No existing state found, creating new session",
                    session_id=session_id,
                )
                return None
                
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"❌ Failed to load state for {session_id}: {e}")
            return None
    
    def delete_state(self, session_id: str) -> bool:
        """
        Delete session state from Redis.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        key = self._get_key(session_id)
        
        try:
            if self.client:
                self.client.delete(key)
            else:
                self._memory_store.pop(key, None)
            
            log_security_event(
                logger,
                "SYSTEM",
                f"State deleted from Redis",
                session_id=session_id,
            )
            return True
            
        except RedisError as e:
            logger.error(f"❌ Failed to delete state for {session_id}: {e}")
            return False
    
    def extend_ttl(self, session_id: str) -> bool:
        """
        Extend the TTL of a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return True  # Memory store doesn't expire
        
        key = self._get_key(session_id)
        
        try:
            self.client.expire(key, settings.redis_ttl)
            return True
        except RedisError as e:
            logger.error(f"❌ Failed to extend TTL for {session_id}: {e}")
            return False
    
    def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            self.client.close()
            log_security_event(logger, "SYSTEM", "Redis connection closed")


# Global Redis client instance
redis_client = RedisClient()
