"""
🛡️ National Security Grade Logger
Rich-formatted logging with visual excellence for demo purposes.
"""

import logging
import sys
from typing import Optional
from datetime import datetime

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
import structlog

from config import settings


# Custom theme for "National Security" aesthetics
SECURITY_THEME = Theme({
    "info": "cyan bold",
    "warning": "yellow bold",
    "error": "red bold",
    "critical": "white on red bold",
    "success": "green bold",
    "agent": "magenta bold",
    "intel": "blue bold",
})

console = Console(theme=SECURITY_THEME)


def setup_logging() -> logging.Logger:
    """
    Configure application logging with Rich or JSON formatting.
    
    Returns:
        Configured logger instance
    """
    
    # Clear existing handlers
    logging.root.handlers.clear()
    
    # Use simple console logging for Windows compatibility
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='[%(asctime)s] %(levelname)-8s %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stdout,
    )
    
    return logging.getLogger("honeypot")


def log_security_event(
    logger: logging.Logger,
    event_type: str,
    message: str,
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log a security event with visual formatting.
    
    Args:
        logger: Logger instance
        event_type: Type of event (PROFILER, ACTOR, AUDITOR, CALLBACK)
        message: Log message
        session_id: Optional session identifier
        **kwargs: Additional context data
    """
    
    prefix_map = {
        "PROFILER": "[PROF]",
        "ACTOR": "[ACTR]",
        "AUDITOR": "[AUDT]",
        "CALLBACK": "[CALL]",
        "SYSTEM": "[SYST]",
        "INTEL": "[INTL]",
    }
    
    prefix = prefix_map.get(event_type.upper(), "[INFO]")
    
    session_info = f"({session_id[:8]}...)" if session_id else ""
    log_msg = f"{prefix} {session_info} {message}"
    
    if kwargs:
        details = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        log_msg += f" | {details}"
    
    logger.info(log_msg)


# Initialize global logger
logger = setup_logging()
